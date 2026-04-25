from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.taxonomy import BodyShape, Gender, LegRatio, ShoulderType, WaistType
from app.services.openai_service import detect_gender_from_image_with_llm
from app.services.persistence_service import save_body_analysis_record
from app.utils.file_utils import save_upload_file, to_public_upload_url

WAIST_SAMPLE_RATIO = 0.55
GRABCUT_ITERATIONS = 3
MASK_THRESHOLD = 127

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PixelPoint:
    x: float
    y: float


@dataclass(frozen=True)
class BodyMetrics:
    shoulder_width_px: float
    waist_width_px: float
    hip_width_px: float
    body_height_px: float
    leg_upper_ratio: float
    shoulder_to_height_ratio: float
    waist_to_avg_ratio: float
    shoulder_hip_ratio: float


def _safe_ratio(a: float, b: float) -> float:
    if b == 0:
        return 0.0
    return a / b


def _distance(p1: PixelPoint, p2: PixelPoint) -> float:
    return float(np.hypot(p1.x - p2.x, p1.y - p2.y))


def _midpoint(p1: PixelPoint, p2: PixelPoint) -> PixelPoint:
    return PixelPoint(x=(p1.x + p2.x) / 2, y=(p1.y + p2.y) / 2)


def _interpolate_point(start: PixelPoint, end: PixelPoint, ratio: float) -> PixelPoint:
    return PixelPoint(
        x=start.x + (end.x - start.x) * ratio,
        y=start.y + (end.y - start.y) * ratio,
    )


def _to_pixel_point(landmark, image_width: int, image_height: int) -> PixelPoint:
    return PixelPoint(
        x=float(np.clip(landmark.x * image_width, 0, image_width - 1)),
        y=float(np.clip(landmark.y * image_height, 0, image_height - 1)),
    )


def _build_pose_landmarker():
    vision = mp.tasks.vision
    base_options = mp.tasks.BaseOptions(model_asset_path=settings.pose_model_path)
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.IMAGE,
        num_poses=1,
    )
    return vision.PoseLandmarker.create_from_options(options)


def _read_image(image_path: str):
    # cv2.imread 在 Windows 下对中文路径兼容性较差，这里改为 fromfile + imdecode
    image_bytes = np.fromfile(image_path, dtype=np.uint8)
    if image_bytes.size == 0:
        return None
    return cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)


def _build_body_rect(
    image_width: int,
    image_height: int,
    nose: PixelPoint,
    shoulders: tuple[PixelPoint, PixelPoint],
    hips: tuple[PixelPoint, PixelPoint],
    ankles: tuple[PixelPoint, PixelPoint],
) -> tuple[int, int, int, int] | None:
    torso_width = max(_distance(*shoulders), _distance(*hips))
    all_points = [nose, *shoulders, *hips, *ankles]
    xs = [point.x for point in all_points]
    ys = [point.y for point in all_points]

    margin_x = max(24, torso_width * 0.9)
    margin_top = max(24, torso_width * 0.45)
    margin_bottom = max(24, torso_width * 0.35)

    left = max(0, int(min(xs) - margin_x))
    right = min(image_width - 1, int(max(xs) + margin_x))
    top = max(0, int(min(ys) - margin_top))
    bottom = min(image_height - 1, int(max(ys) + margin_bottom))

    width = right - left
    height = bottom - top
    if width < 40 or height < 80:
        return None

    return (left, top, width, height)


def _extract_body_mask(image: np.ndarray, rect: tuple[int, int, int, int] | None) -> np.ndarray | None:
    if rect is None:
        return None

    mask = np.zeros(image.shape[:2], np.uint8)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)

    try:
        cv2.grabCut(image, mask, rect, bgd_model, fgd_model, GRABCUT_ITERATIONS, cv2.GC_INIT_WITH_RECT)
    except cv2.error:
        return None

    foreground = np.where(
        (mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD),
        255,
        0,
    ).astype("uint8")

    kernel = np.ones((5, 5), np.uint8)
    foreground = cv2.morphologyEx(foreground, cv2.MORPH_OPEN, kernel)
    foreground = cv2.morphologyEx(foreground, cv2.MORPH_CLOSE, kernel)
    return foreground


def _segment_containing_center(indices: np.ndarray, center_x: int) -> np.ndarray | None:
    if indices.size == 0:
        return None

    split_points = np.where(np.diff(indices) > 1)[0] + 1
    segments = np.split(indices, split_points)

    containing_segments = [
        segment
        for segment in segments
        if segment.size > 0 and segment[0] <= center_x <= segment[-1]
    ]
    if containing_segments:
        return max(containing_segments, key=lambda segment: segment.size)

    return min(
        segments,
        key=lambda segment: min(abs(segment[0] - center_x), abs(segment[-1] - center_x)),
    )


def _measure_width_from_mask(mask: np.ndarray | None, y: float, center_x: float) -> float | None:
    if mask is None:
        return None

    height, width = mask.shape
    y_center = int(np.clip(round(y), 0, height - 1))
    x_center = int(np.clip(round(center_x), 0, width - 1))
    widths: list[float] = []

    for row in range(max(0, y_center - 2), min(height, y_center + 3)):
        indices = np.where(mask[row] > MASK_THRESHOLD)[0]
        segment = _segment_containing_center(indices, x_center)
        if segment is None or segment.size == 0:
            continue
        widths.append(float(segment[-1] - segment[0] + 1))

    if not widths:
        return None

    return float(np.median(widths))


def _estimate_waist_width_from_landmarks(
    left_shoulder: PixelPoint,
    right_shoulder: PixelPoint,
    left_hip: PixelPoint,
    right_hip: PixelPoint,
) -> float:
    left_waist = _interpolate_point(left_shoulder, left_hip, WAIST_SAMPLE_RATIO)
    right_waist = _interpolate_point(right_shoulder, right_hip, WAIST_SAMPLE_RATIO)
    return _distance(left_waist, right_waist)


def _classify_body_shape(shoulder_width_px: float, waist_width_px: float, hip_width_px: float) -> BodyShape:
    avg_frame_width = max((shoulder_width_px + hip_width_px) / 2, 1.0)
    waist_to_avg_ratio = waist_width_px / avg_frame_width
    shoulder_hip_ratio = _safe_ratio(shoulder_width_px, hip_width_px)
    shoulder_hip_diff_ratio = abs(shoulder_width_px - hip_width_px) / max(shoulder_width_px, hip_width_px, 1.0)

    if shoulder_hip_diff_ratio <= 0.1 and waist_to_avg_ratio <= 0.8:
        return BodyShape.X
    if waist_to_avg_ratio >= 0.94 and shoulder_hip_diff_ratio <= 0.12:
        return BodyShape.O
    if shoulder_hip_ratio <= 0.9:
        return BodyShape.A
    if shoulder_hip_ratio >= 1.1:
        return BodyShape.INVERTED_TRIANGLE
    if shoulder_hip_diff_ratio <= 0.15 and waist_to_avg_ratio <= 0.86:
        return BodyShape.X
    return BodyShape.H


def _classify_shoulder_type(shoulder_width_px: float, body_height_px: float) -> ShoulderType:
    ratio = _safe_ratio(shoulder_width_px, body_height_px)
    if ratio < 0.18:
        return ShoulderType.NARROW
    if ratio < 0.24:
        return ShoulderType.MEDIUM
    return ShoulderType.WIDE


def _classify_waist_type(waist_width_px: float, shoulder_width_px: float, hip_width_px: float) -> WaistType:
    avg_frame_width = max((shoulder_width_px + hip_width_px) / 2, 1.0)
    ratio = waist_width_px / avg_frame_width
    if ratio <= 0.78:
        return WaistType.DEFINED
    if ratio <= 0.92:
        return WaistType.NORMAL
    return WaistType.UNDEFINED


def _classify_leg_ratio(leg_upper_ratio: float) -> LegRatio:
    if leg_upper_ratio > 1.2:
        return LegRatio.LONG
    if leg_upper_ratio >= 0.9:
        return LegRatio.NORMAL
    return LegRatio.SHORT


def _measure_body_metrics(landmarks, image: np.ndarray) -> BodyMetrics:
    image_height, image_width = image.shape[:2]
    pixel_points = [_to_pixel_point(landmark, image_width, image_height) for landmark in landmarks]

    nose = pixel_points[0]
    left_shoulder = pixel_points[11]
    right_shoulder = pixel_points[12]
    left_hip = pixel_points[23]
    right_hip = pixel_points[24]
    left_ankle = pixel_points[27]
    right_ankle = pixel_points[28]

    shoulder_width_px = abs(right_shoulder.x - left_shoulder.x)
    hip_width_px = abs(right_hip.x - left_hip.x)
    body_center_x = np.mean([left_shoulder.x, right_shoulder.x, left_hip.x, right_hip.x])

    shoulder_mid = _midpoint(left_shoulder, right_shoulder)
    hip_mid = _midpoint(left_hip, right_hip)
    ankle_mid = _midpoint(left_ankle, right_ankle)
    waist_y = shoulder_mid.y + (hip_mid.y - shoulder_mid.y) * WAIST_SAMPLE_RATIO

    mask_rect = _build_body_rect(
        image_width=image_width,
        image_height=image_height,
        nose=nose,
        shoulders=(left_shoulder, right_shoulder),
        hips=(left_hip, right_hip),
        ankles=(left_ankle, right_ankle),
    )
    body_mask = _extract_body_mask(image, mask_rect)

    waist_width_px = _measure_width_from_mask(body_mask, waist_y, body_center_x)
    fallback_waist_width_px = _estimate_waist_width_from_landmarks(
        left_shoulder=left_shoulder,
        right_shoulder=right_shoulder,
        left_hip=left_hip,
        right_hip=right_hip,
    )

    if waist_width_px is None:
        waist_width_px = fallback_waist_width_px
    else:
        lower_bound = fallback_waist_width_px * 0.72
        upper_bound = max(shoulder_width_px, hip_width_px) * 1.02
        waist_width_px = float(np.clip(waist_width_px, lower_bound, upper_bound))

    leg_length_px = abs(ankle_mid.y - hip_mid.y)
    upper_length_px = abs(hip_mid.y - nose.y)
    body_height_px = max(ankle_mid.y - nose.y, 1.0)
    leg_upper_ratio = _safe_ratio(leg_length_px, upper_length_px)

    return BodyMetrics(
        shoulder_width_px=shoulder_width_px,
        waist_width_px=waist_width_px,
        hip_width_px=hip_width_px,
        body_height_px=body_height_px,
        leg_upper_ratio=leg_upper_ratio,
        shoulder_to_height_ratio=_safe_ratio(shoulder_width_px, body_height_px),
        waist_to_avg_ratio=_safe_ratio(waist_width_px, (shoulder_width_px + hip_width_px) / 2),
        shoulder_hip_ratio=_safe_ratio(shoulder_width_px, hip_width_px),
    )


def _analyze_landmarks(landmarks, image: np.ndarray) -> dict:
    metrics = _measure_body_metrics(landmarks, image)

    body_shape = _classify_body_shape(
        shoulder_width_px=metrics.shoulder_width_px,
        waist_width_px=metrics.waist_width_px,
        hip_width_px=metrics.hip_width_px,
    )
    shoulder_type = _classify_shoulder_type(
        shoulder_width_px=metrics.shoulder_width_px,
        body_height_px=metrics.body_height_px,
    )
    waist_type = _classify_waist_type(
        waist_width_px=metrics.waist_width_px,
        shoulder_width_px=metrics.shoulder_width_px,
        hip_width_px=metrics.hip_width_px,
    )
    leg_ratio = _classify_leg_ratio(metrics.leg_upper_ratio)

    analysis_summary = (
        f"基于肩宽、估计腰宽和臀宽的综合比例，检测到整体体型偏{body_shape.value}，"
        f"腰型为{waist_type.value}，肩部为{shoulder_type.value}，腿部比例{leg_ratio.value}。"
    )

    return {
        "body_shape": body_shape.value,
        "shoulder_type": shoulder_type.value,
        "waist_type": waist_type.value,
        "leg_ratio": leg_ratio.value,
        "analysis_summary": analysis_summary,
    }


def _detect_gender(image_path: str) -> str:
    try:
        return detect_gender_from_image_with_llm(image_path)
    except Exception as exc:
        logger.warning("Gender detect failed, fallback to 未知: %s", exc)
        return Gender.UNKNOWN.value


def analyze_body_from_image(upload_file, user_id: int | None = None) -> dict:
    saved_path = save_upload_file(upload_file, sub_dir="body")

    if not Path(settings.pose_model_path).exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"未找到 MediaPipe pose 模型文件: {settings.pose_model_path}",
        )

    image = _read_image(saved_path)
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="图片读取失败，请重新上传清晰的人像图片",
        )

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

    try:
        with _build_pose_landmarker() as landmarker:
            result = landmarker.detect(mp_image)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"MediaPipe 分析失败: {str(e)}",
        )

    if not result.pose_landmarks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="未检测到清晰人体，请上传正面、清晰、完整的人物图片",
        )

    analyzed = _analyze_landmarks(result.pose_landmarks[0], image)
    analyzed["gender"] = _detect_gender(saved_path)
    analyzed["analysis_summary"] = (
        f"{analyzed['analysis_summary']} 性别识别结果为{analyzed['gender']}。"
    )
    analyzed["image_path"] = saved_path
    analyzed["image_url"] = to_public_upload_url(saved_path)
    analyzed["record_id"] = save_body_analysis_record(user_id, analyzed)

    return analyzed
