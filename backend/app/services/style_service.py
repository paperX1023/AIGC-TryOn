from app.services.openai_service import parse_style_text_with_llm


def parse_style_text_rule(text: str) -> dict:
    styles = []
    scene = "日常"
    goals = []

    if "韩系" in text:
        styles.append("韩系")
    if "简约" in text:
        styles.append("简约")
    if "通勤" in text:
        styles.append("通勤")
    if "甜美" in text:
        styles.append("甜美")
    if "休闲" in text:
        styles.append("休闲")
    if "中国风" in text:
        styles.append("中国风")

    if not styles:
        styles.append("基础风格")

    if "上课" in text:
        scene = "上课"
    elif "面试" in text:
        scene = "面试"
    elif "约会" in text:
        scene = "约会"
    elif "出去玩" in text or "出游" in text:
        scene = "出游"

    if "显瘦" in text:
        goals.append("显瘦")
    if "显高" in text:
        goals.append("显高")
    if "舒适" in text:
        goals.append("舒适")

    if not goals:
        goals.append("舒适")

    return {
        "styles": styles,
        "scene": scene,
        "goals": goals
    }


def parse_style_text(text: str, use_llm: bool = False) -> dict:
    if use_llm:
        try:
            return parse_style_text_with_llm(text)
        except Exception as e:
            print("LLM parse failed, fallback to rule parse:", e)
            return parse_style_text_rule(text)

    return parse_style_text_rule(text)