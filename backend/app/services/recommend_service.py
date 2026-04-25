from __future__ import annotations

import math
import logging
from dataclasses import dataclass
from enum import Enum

from app.schemas.taxonomy import (
    BodyShape,
    Gender,
    GoalTag,
    LegRatio,
    SceneTag,
    ShoulderType,
    StyleTag,
    WaistType,
)
from app.services.openai_service import generate_recommend_reason_with_llm
from app.services.recommend_catalog import CATALOG_ITEMS, CatalogItem

FEATURE_WEIGHTS = {
    "style": 1.0,
    "scene": 1.15,
    "goal": 1.05,
    "body": 1.2,
    "shoulder": 0.75,
    "waist": 0.7,
    "leg": 0.75,
}

logger = logging.getLogger(__name__)

BODY_SHAPE_SOFT_MATCH = {
    BodyShape.X: ((BodyShape.X, 1.0), (BodyShape.H, 0.8), (BodyShape.A, 0.65)),
    BodyShape.H: ((BodyShape.H, 1.0), (BodyShape.X, 0.72), (BodyShape.O, 0.58)),
    BodyShape.O: ((BodyShape.O, 1.0), (BodyShape.H, 0.78)),
    BodyShape.A: ((BodyShape.A, 1.0), (BodyShape.X, 0.6)),
    BodyShape.INVERTED_TRIANGLE: ((BodyShape.INVERTED_TRIANGLE, 1.0), (BodyShape.H, 0.5)),
}

WAIST_TYPE_SOFT_MATCH = {
    WaistType.DEFINED: ((WaistType.DEFINED, 1.0), (WaistType.NORMAL, 0.76)),
    WaistType.NORMAL: ((WaistType.NORMAL, 1.0), (WaistType.DEFINED, 0.72), (WaistType.UNDEFINED, 0.58)),
    WaistType.UNDEFINED: ((WaistType.UNDEFINED, 1.0), (WaistType.NORMAL, 0.66)),
}

CATEGORY_LIMITS = {
    "上装": 2,
    "下装": 2,
    "外套": 1,
    "鞋履": 1,
    "裙装": 1,
    "套装": 1,
}

BODY_REASON_MAP = {
    BodyShape.X: "X 型身材腰线更明显，适合突出曲线并保持上下比例平衡的搭配。",
    BodyShape.H: "H 型身材更适合用短上装、高腰或利落剪裁来强化比例感。",
    BodyShape.O: "O 型身材更适合纵向线条更强、领口更开阔且重心更稳定的搭配。",
    BodyShape.A: "A 型身材更适合把视觉重点放在上半身，并用垂感下装平衡轮廓。",
    BodyShape.INVERTED_TRIANGLE: "倒三角型更适合通过开领、垂感和更稳定的下装廓形来均衡重心。",
}

SCENE_REASON_MAP = {
    SceneTag.CLASS: "上课场景会提高舒适、耐穿和活动便利相关单品的排序权重。",
    SceneTag.INTERVIEW: "面试场景会优先保留更利落、干净和通勤感更强的候选单品。",
    SceneTag.DATE: "约会场景会更偏向柔和、精致且有氛围感的搭配方向。",
    SceneTag.TRAVEL: "出游场景会优先选择轻便、耐走和层次感更好的搭配。",
    SceneTag.DAILY: "日常场景会平衡舒适度、百搭性和搭配稳定性。",
}

GOAL_REASON_MAP = {
    GoalTag.SLIM: "显瘦目标会提高深色、纵向线条更明显单品的得分。",
    GoalTag.TALL: "显高目标会提高高腰、短外套和纵向延伸感更强单品的得分。",
    GoalTag.COMFORT: "舒适目标会提高柔软面料、宽松版型和通勤友好单品的权重。",
}


@dataclass(frozen=True)
class RankedCatalogItem:
    item: CatalogItem
    score: float
    cosine_similarity: float
    style_overlap: float
    scene_match: float
    goal_overlap: float
    fit_overlap: float


@dataclass(frozen=True)
class NormalizedRecommendInput:
    gender: Gender
    body_shape: BodyShape
    shoulder_type: ShoulderType
    waist_type: WaistType
    leg_ratio: LegRatio
    styles: list[StyleTag]
    scene: SceneTag
    goals: list[GoalTag]


def _make_item(name: str, category: str, target_gender: Gender) -> dict:
    return {
        "name": name,
        "category": category,
        "target_gender": target_gender,
    }


def _format_list(values: list[str]) -> str:
    return "、".join(values)


def _coerce_enum(enum_cls, value, default_value):
    if isinstance(value, enum_cls):
        return value

    try:
        return enum_cls(value)
    except ValueError:
        return default_value


def _coerce_enum_list(enum_cls, values, default_values):
    if not values:
        return list(default_values)

    normalized_values = []
    for value in values:
        enum_value = _coerce_enum(enum_cls, value, None)
        if enum_value and enum_value not in normalized_values:
            normalized_values.append(enum_value)

    return normalized_values or list(default_values)


def _normalize_recommend_input(data) -> NormalizedRecommendInput:
    return NormalizedRecommendInput(
        gender=_coerce_enum(Gender, getattr(data, "gender", Gender.UNKNOWN), Gender.UNKNOWN),
        body_shape=_coerce_enum(BodyShape, getattr(data, "body_shape", BodyShape.H), BodyShape.H),
        shoulder_type=_coerce_enum(ShoulderType, getattr(data, "shoulder_type", ShoulderType.MEDIUM), ShoulderType.MEDIUM),
        waist_type=_coerce_enum(WaistType, getattr(data, "waist_type", WaistType.NORMAL), WaistType.NORMAL),
        leg_ratio=_coerce_enum(LegRatio, getattr(data, "leg_ratio", LegRatio.NORMAL), LegRatio.NORMAL),
        styles=_coerce_enum_list(StyleTag, getattr(data, "styles", []), [StyleTag.MINIMAL]),
        scene=_coerce_enum(SceneTag, getattr(data, "scene", SceneTag.DAILY), SceneTag.DAILY),
        goals=_coerce_enum_list(GoalTag, getattr(data, "goals", []), [GoalTag.COMFORT]),
    )


def _resolve_style_direction(styles: list[StyleTag], gender: Gender) -> str:
    style_set = set(styles)

    if {StyleTag.KOREAN, StyleTag.MINIMAL}.issubset(style_set):
        return "韩系简约男生风" if gender == Gender.MALE else "韩系简约风"
    if StyleTag.KOREAN in style_set:
        return "韩系日常男装风" if gender == Gender.MALE else "韩系日常风"
    if {StyleTag.CHINESE, StyleTag.COMMUTE}.issubset(style_set):
        return "新中式通勤风"
    if StyleTag.CHINESE in style_set:
        return "新中式男装风" if gender == Gender.MALE else "新中式风格"
    if StyleTag.SWEET in style_set:
        return "甜美温柔风"
    if StyleTag.COMMUTE in style_set:
        return "简约通勤男装风" if gender == Gender.MALE else "简约通勤风"
    if StyleTag.CASUAL in style_set:
        return "轻松休闲风"
    return "基础日常风"


def _feature_key(prefix: str, value: Enum) -> str:
    return f"{prefix}:{value.value}"


def _build_user_vector(data) -> dict[str, float]:
    vector: dict[str, float] = {}

    for style in data.styles:
        vector[_feature_key("style", style)] = FEATURE_WEIGHTS["style"]

    vector[_feature_key("scene", data.scene)] = FEATURE_WEIGHTS["scene"]

    for goal in data.goals:
        vector[_feature_key("goal", goal)] = FEATURE_WEIGHTS["goal"]

    for body_shape, factor in BODY_SHAPE_SOFT_MATCH.get(data.body_shape, ((data.body_shape, 1.0),)):
        vector[_feature_key("body", body_shape)] = FEATURE_WEIGHTS["body"] * factor
    vector[_feature_key("shoulder", data.shoulder_type)] = FEATURE_WEIGHTS["shoulder"]
    for waist_type, factor in WAIST_TYPE_SOFT_MATCH.get(data.waist_type, ((data.waist_type, 1.0),)):
        vector[_feature_key("waist", waist_type)] = FEATURE_WEIGHTS["waist"] * factor
    vector[_feature_key("leg", data.leg_ratio)] = FEATURE_WEIGHTS["leg"]

    return vector


def _build_item_vector(item: CatalogItem) -> dict[str, float]:
    vector: dict[str, float] = {}

    for style in item.style_tags:
        vector[_feature_key("style", style)] = FEATURE_WEIGHTS["style"]
    for scene in item.scene_tags:
        vector[_feature_key("scene", scene)] = FEATURE_WEIGHTS["scene"]
    for goal in item.goal_tags:
        vector[_feature_key("goal", goal)] = FEATURE_WEIGHTS["goal"]
    for body_shape in item.body_shapes:
        vector[_feature_key("body", body_shape)] = FEATURE_WEIGHTS["body"]
    for shoulder_type in item.shoulder_types:
        vector[_feature_key("shoulder", shoulder_type)] = FEATURE_WEIGHTS["shoulder"]
    for waist_type in item.waist_types:
        vector[_feature_key("waist", waist_type)] = FEATURE_WEIGHTS["waist"]
    for leg_ratio in item.leg_ratios:
        vector[_feature_key("leg", leg_ratio)] = FEATURE_WEIGHTS["leg"]

    return vector


def _cosine_similarity(left: dict[str, float], right: dict[str, float]) -> float:
    shared_keys = set(left) & set(right)
    numerator = sum(left[key] * right[key] for key in shared_keys)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))

    if left_norm == 0 or right_norm == 0:
        return 0.0

    return numerator / (left_norm * right_norm)


def _normalized_overlap(user_values, item_values) -> float:
    if not user_values:
        return 0.0

    user_set = set(user_values)
    item_set = set(item_values)
    if not item_set:
        return 0.0

    return len(user_set & item_set) / len(user_set)


def _fit_overlap(item: CatalogItem, data) -> float:
    body_shape_match = any(
        compatible_shape in item.body_shapes
        for compatible_shape, _ in BODY_SHAPE_SOFT_MATCH.get(data.body_shape, ((data.body_shape, 1.0),))
    )
    waist_type_match = any(
        compatible_waist in item.waist_types
        for compatible_waist, _ in WAIST_TYPE_SOFT_MATCH.get(data.waist_type, ((data.waist_type, 1.0),))
    )
    checks = [
        body_shape_match,
        data.shoulder_type in item.shoulder_types,
        waist_type_match,
        data.leg_ratio in item.leg_ratios,
    ]
    return sum(1 for check in checks if check) / len(checks)


def _is_gender_compatible(item: CatalogItem, gender: Gender) -> bool:
    if gender == Gender.UNKNOWN:
        return True
    return item.target_gender in {Gender.NEUTRAL, gender}


def _score_item(item: CatalogItem, data, user_vector: dict[str, float]) -> RankedCatalogItem:
    item_vector = _build_item_vector(item)
    cosine_similarity = _cosine_similarity(user_vector, item_vector)
    style_overlap = _normalized_overlap(data.styles, item.style_tags)
    scene_match = 1.0 if data.scene in item.scene_tags else 0.0
    goal_overlap = _normalized_overlap(data.goals, item.goal_tags)
    fit_overlap = _fit_overlap(item, data)
    popularity_bonus = item.popularity / 100
    gender_bonus = 1.0 if item.target_gender == data.gender else 0.82 if item.target_gender == Gender.NEUTRAL else 0.0

    score = (
        cosine_similarity * 0.42
        + style_overlap * 0.18
        + scene_match * 0.14
        + goal_overlap * 0.10
        + fit_overlap * 0.10
        + popularity_bonus * 0.06
    ) * gender_bonus

    return RankedCatalogItem(
        item=item,
        score=score,
        cosine_similarity=cosine_similarity,
        style_overlap=style_overlap,
        scene_match=scene_match,
        goal_overlap=goal_overlap,
        fit_overlap=fit_overlap,
    )


def _fallback_hot_items(data) -> list[RankedCatalogItem]:
    compatible_items = [item for item in CATALOG_ITEMS if _is_gender_compatible(item, data.gender)]
    compatible_items.sort(
        key=lambda item: (
            data.scene in item.scene_tags,
            item.target_gender == data.gender,
            item.popularity,
        ),
        reverse=True,
    )

    user_vector = _build_user_vector(data)
    return [_score_item(item, data, user_vector) for item in compatible_items[:8]]


def _select_diverse_items(ranked_items: list[RankedCatalogItem], limit: int = 6) -> list[RankedCatalogItem]:
    selected: list[RankedCatalogItem] = []
    category_counts: dict[str, int] = {}

    for ranked_item in ranked_items:
        category = ranked_item.item.category
        if category_counts.get(category, 0) >= CATEGORY_LIMITS.get(category, 1):
            continue

        selected.append(ranked_item)
        category_counts[category] = category_counts.get(category, 0) + 1

        if len(selected) >= limit:
            break

    return selected


def _rank_candidates(data) -> tuple[list[RankedCatalogItem], bool]:
    user_vector = _build_user_vector(data)
    ranked_items = [
        _score_item(item, data, user_vector)
        for item in CATALOG_ITEMS
        if _is_gender_compatible(item, data.gender)
    ]
    ranked_items.sort(key=lambda item: (item.score, item.item.popularity), reverse=True)

    should_fallback = not ranked_items or ranked_items[0].score < 0.45
    if should_fallback:
        ranked_items = _fallback_hot_items(data)
        ranked_items.sort(key=lambda item: (item.score, item.item.popularity), reverse=True)

    return _select_diverse_items(ranked_items), should_fallback


def _build_rule_reason(data, ranked_items: list[RankedCatalogItem], used_fallback: bool) -> str:
    style_text = _format_list([style.value for style in data.styles])
    goal_text = _format_list([goal.value for goal in data.goals])

    parts = [
        f"本轮推荐先按{style_text}等风格标签做候选召回，再结合{data.scene.value}场景、{goal_text}目标和体型特征进行排序。",
        BODY_REASON_MAP.get(data.body_shape, "推荐时已综合考虑你的整体身材比例。"),
        SCENE_REASON_MAP.get(data.scene, "场景标签会参与本轮候选排序。"),
    ]

    for goal in data.goals:
        reason = GOAL_REASON_MAP.get(goal)
        if reason:
            parts.append(reason)

    if ranked_items:
        top_item_names = _format_list([ranked_item.item.name for ranked_item in ranked_items[:3]])
        parts.append(f"综合得分更高的候选主要集中在{top_item_names}这些单品。")

    if used_fallback:
        parts.append("当候选分数接近时，系统会使用基础热度补齐推荐结果，保证冷启动场景下也能返回稳定搭配。")

    return " ".join(dict.fromkeys(parts))


def generate_recommendation_rule(data) -> dict:
    normalized_data = _normalize_recommend_input(data)
    ranked_items, used_fallback = _rank_candidates(normalized_data)

    if not ranked_items:
        ranked_items = _fallback_hot_items(normalized_data)[:4]
        used_fallback = True

    categorized_items = [
        _make_item(
            name=ranked_item.item.name,
            category=ranked_item.item.category,
            target_gender=ranked_item.item.target_gender,
        )
        for ranked_item in ranked_items
    ]
    recommended_items = [item["name"] for item in categorized_items]

    return {
        "recommended_items": recommended_items,
        "categorized_items": categorized_items,
        "recommended_style_direction": _resolve_style_direction(normalized_data.styles, normalized_data.gender),
        "reason": _build_rule_reason(normalized_data, ranked_items, used_fallback),
    }


def generate_recommendation(data, use_llm_reason: bool = True) -> dict:
    normalized_data = _normalize_recommend_input(data)
    result = generate_recommendation_rule(normalized_data)

    if use_llm_reason:
        try:
            input_summary = {
                "gender": normalized_data.gender,
                "body_shape": normalized_data.body_shape,
                "shoulder_type": normalized_data.shoulder_type,
                "waist_type": normalized_data.waist_type,
                "leg_ratio": normalized_data.leg_ratio,
                "styles": normalized_data.styles,
                "scene": normalized_data.scene,
                "goals": normalized_data.goals,
            }

            llm_reason = generate_recommend_reason_with_llm(input_summary, result)
            result["reason"] = llm_reason
        except Exception as exc:
            logger.warning("LLM recommend reason failed, fallback to rule reason: %s", exc)

    return result
