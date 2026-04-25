from enum import Enum


class StrValueEnum(str, Enum):
    @classmethod
    def values(cls) -> list[str]:
        return [item.value for item in cls]


class Gender(StrValueEnum):
    MALE = "男"
    FEMALE = "女"
    UNKNOWN = "未知"
    NEUTRAL = "中性"


class BodyShape(StrValueEnum):
    X = "X型"
    H = "H型"
    O = "O型"
    A = "A型"
    INVERTED_TRIANGLE = "倒三角型"


class ShoulderType(StrValueEnum):
    NARROW = "窄"
    MEDIUM = "中等"
    WIDE = "宽"


class WaistType(StrValueEnum):
    DEFINED = "明显"
    UNDEFINED = "不明显"
    NORMAL = "一般"


class LegRatio(StrValueEnum):
    SHORT = "偏短"
    NORMAL = "普通"
    LONG = "偏长"


class StyleTag(StrValueEnum):
    KOREAN = "韩系"
    MINIMAL = "简约"
    COMMUTE = "通勤"
    SWEET = "甜美"
    CASUAL = "休闲"
    CHINESE = "中国风"


class SceneTag(StrValueEnum):
    DAILY = "日常"
    CLASS = "上课"
    INTERVIEW = "面试"
    DATE = "约会"
    TRAVEL = "出游"


class GoalTag(StrValueEnum):
    SLIM = "显瘦"
    TALL = "显高"
    COMFORT = "舒适"
