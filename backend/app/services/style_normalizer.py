from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from app.schemas.style import StyleParsedResult
from app.schemas.taxonomy import GoalTag, SceneTag, StyleTag

STYLE_ALIASES: dict[StyleTag, tuple[str, ...]] = {
    StyleTag.KOREAN: ("韩系", "韩风", "韩式", "korean"),
    StyleTag.MINIMAL: ("简约", "极简", "简洁", "基础风格", "基础款"),
    StyleTag.COMMUTE: ("通勤", "上班", "职场", "通勤风", "商务休闲"),
    StyleTag.SWEET: ("甜美", "甜妹", "少女", "温柔"),
    StyleTag.CASUAL: ("休闲", "日常", "松弛", "随性", "轻松"),
    StyleTag.CHINESE: ("中国风", "新中式", "国风", "中式"),
}

SCENE_ALIASES: dict[SceneTag, tuple[str, ...]] = {
    SceneTag.CLASS: ("上课", "校园", "通学", "学生"),
    SceneTag.INTERVIEW: ("面试", "求职", "见工"),
    SceneTag.DATE: ("约会", "见面", "聚会"),
    SceneTag.TRAVEL: ("出游", "出去玩", "旅行", "逛街"),
    SceneTag.DAILY: ("日常", "平时", "每天"),
}

GOAL_ALIASES: dict[GoalTag, tuple[str, ...]] = {
    GoalTag.SLIM: ("显瘦", "瘦一点", "遮肉", "修饰身材"),
    GoalTag.TALL: ("显高", "增高感", "拉长比例", "提高腰线"),
    GoalTag.COMFORT: ("舒适", "舒服", "轻松", "好活动"),
}


def _ensure_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, Iterable):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)]


def _match_enum(raw_value: str, alias_map: dict, default_value):
    normalized = raw_value.strip().lower()
    if not normalized:
        return default_value

    for enum_value in alias_map:
        if normalized == enum_value.value.lower():
            return enum_value

    for enum_value, aliases in alias_map.items():
        lowered_aliases = [alias.lower() for alias in aliases]
        if normalized in lowered_aliases:
            return enum_value

    for enum_value, aliases in alias_map.items():
        lowered_aliases = [alias.lower() for alias in aliases]
        if any(alias in normalized or normalized in alias for alias in lowered_aliases):
            return enum_value

    return default_value


def _dedupe_preserve_order(values: list) -> list:
    deduped = []
    seen = set()
    for item in values:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped


def normalize_style_result(raw_result: Any) -> StyleParsedResult:
    if isinstance(raw_result, StyleParsedResult):
        return raw_result

    if not isinstance(raw_result, dict):
        raw_result = {}

    normalized_styles = _dedupe_preserve_order(
        [
            _match_enum(style, STYLE_ALIASES, StyleTag.MINIMAL)
            for style in _ensure_list(raw_result.get("styles"))
        ]
    ) or [StyleTag.MINIMAL]

    normalized_goals = _dedupe_preserve_order(
        [
            _match_enum(goal, GOAL_ALIASES, GoalTag.COMFORT)
            for goal in _ensure_list(raw_result.get("goals"))
        ]
    ) or [GoalTag.COMFORT]

    normalized_scene = _match_enum(
        str(raw_result.get("scene", "")),
        SCENE_ALIASES,
        SceneTag.DAILY,
    )

    return StyleParsedResult(
        styles=normalized_styles,
        scene=normalized_scene,
        goals=normalized_goals,
    )


def extract_style_result_from_text(text: str) -> StyleParsedResult:
    normalized_text = text.strip().lower()

    matched_styles = [
        style
        for style, aliases in STYLE_ALIASES.items()
        if style.value.lower() in normalized_text
        or any(alias.lower() in normalized_text for alias in aliases)
    ]

    matched_goals = [
        goal
        for goal, aliases in GOAL_ALIASES.items()
        if goal.value.lower() in normalized_text
        or any(alias.lower() in normalized_text for alias in aliases)
    ]

    matched_scene = next(
        (
            scene
            for scene, aliases in SCENE_ALIASES.items()
            if scene.value.lower() in normalized_text
            or any(alias.lower() in normalized_text for alias in aliases)
        ),
        SceneTag.DAILY,
    )

    return StyleParsedResult(
        styles=_dedupe_preserve_order(matched_styles) or [StyleTag.MINIMAL],
        scene=matched_scene,
        goals=_dedupe_preserve_order(matched_goals) or [GoalTag.COMFORT],
    )
