import math
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from fastapi import HTTPException, status

from app.core.config import settings
from app.services.openai_service import detect_gender_from_image_with_llm
from app.utils.file_utils import save_upload_file, to_public_upload_url


def _distance(p1, p2) -> float:
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)


def _safe_ratio(a: float, b: float) -> float:
    if b == 0:
        return 0.0
    return a / b


def _build_pose_landmarker():
    vision = mp.tasks.vision
    base_options = mp.tasks.BaseOptions(model_asset_path=settings.pose_model_path)
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.IMAGE,
        num_poses=1
    )
    return vision.PoseLandmarker.create_from_options(options)


def _read_image(image_path: str):
    # cv2.imread 在 Windows 下对中文路径兼容性较差，这里改为 fromfile + imdecode
    image_bytes = np.fromfile(image_path, dtype=np.uint8)
    if image_bytes.size == 0:
        return None
    return cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)


def _analyze_landmarks(landmarks) -> dict:
    # 关键点索引：官方 Pose Landmarker 输出 33 个姿态关键点
    # 这里先用最常用的几个点做简单规则
    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]
    left_hip = landmarks[23]
    right_hip = landmarks[24]
    left_ankle = landmarks[27]
    right_ankle = landmarks[28]
    nose = landmarks[0]

    shoulder_width = _distance(left_shoulder, right_shoulder)
    hip_width = _distance(left_hip, right_hip)

    shoulder_hip_ratio = _safe_ratio(shoulder_width, hip_width)

    # 粗略腿长：臀部中点到脚踝中点
    hip_mid_y = (left_hip.y + right_hip.y) / 2
    ankle_mid_y = (left_ankle.y + right_ankle.y) / 2
    leg_length = abs(ankle_mid_y - hip_mid_y)

    # 粗略上半身长度：鼻子到臀部中点
    upper_length = abs(hip_mid_y - nose.y)
    leg_upper_ratio = _safe_ratio(leg_length, upper_length)

    if 0.9 <= shoulder_hip_ratio <= 1.1:
        body_shape = "H型"
    elif shoulder_hip_ratio < 0.9:
        body_shape = "A型"
    else:
        body_shape = "倒三角型"

    if shoulder_width < 0.12:
        shoulder_type = "窄"
    elif shoulder_width < 0.18:
        shoulder_type = "中等"
    else:
        shoulder_type = "宽"

    # 第一版先不给复杂腰线识别，先按体型做粗略推断
    if body_shape == "H型":
        waist_type = "不明显"
    else:
        waist_type = "一般"

    if leg_upper_ratio > 1.2:
        leg_ratio = "偏长"
    elif leg_upper_ratio >= 0.9:
        leg_ratio = "普通"
    else:
        leg_ratio = "偏短"

    analysis_summary = (
        f"检测到整体体型偏{body_shape}，肩部为{shoulder_type}，"
        f"腿部比例{leg_ratio}。"
        # f"腿部比例{leg_ratio}，当前分析结果为基础规则版。"
    )

    return {
        "body_shape": body_shape,
        "shoulder_type": shoulder_type,
        "waist_type": waist_type,
        "leg_ratio": leg_ratio,
        "analysis_summary": analysis_summary,
    }


def _detect_gender(image_path: str) -> str:
    try:
        return detect_gender_from_image_with_llm(image_path)
    except Exception as e:
        print("Gender detect failed, fallback to 未知:", e)
        return "未知"


def analyze_body_from_image(upload_file) -> dict:
    saved_path = save_upload_file(upload_file, sub_dir="body")

    if not Path(settings.pose_model_path).exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"未找到 MediaPipe pose 模型文件: {settings.pose_model_path}"
        )

    image = _read_image(saved_path)
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="图片读取失败，请重新上传清晰的人像图片"
        )

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

    try:
        with _build_pose_landmarker() as landmarker:
            result = landmarker.detect(mp_image)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"MediaPipe 分析失败: {str(e)}"
        )

    if not result.pose_landmarks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="未检测到清晰人体，请上传正面、清晰、完整的人物图片"
        )

    analyzed = _analyze_landmarks(result.pose_landmarks[0])
    analyzed["gender"] = _detect_gender(saved_path)
    analyzed["analysis_summary"] = (
        f"检测到整体体型偏{analyzed['body_shape']}，肩部为{analyzed['shoulder_type']}，"
        f"腿部比例{analyzed['leg_ratio']}，性别识别结果为{analyzed['gender']}。"
    )
    analyzed["image_path"] = saved_path
    analyzed["image_url"] = to_public_upload_url(saved_path)

    return analyzed
