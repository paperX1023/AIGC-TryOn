from app.services.openai_service import generate_recommend_reason_with_llm


def _make_item(name: str, category: str, target_gender: str) -> dict:
    return {
        "name": name,
        "category": category,
        "target_gender": target_gender,
    }


def _append_item(categorized_items: list[dict], name: str, category: str, target_gender: str):
    if not any(item["name"] == name for item in categorized_items):
        categorized_items.append(_make_item(name, category, target_gender))


def _resolve_style_direction(styles: list[str], gender: str) -> str:
    if "韩系" in styles and "简约" in styles:
        return "韩系简约男生风" if gender == "男" else "韩系简约风"
    if "韩系" in styles:
        return "韩系日常男装风" if gender == "男" else "韩系日常风"
    if "中国风" in styles:
        return "新中式男装风" if gender == "男" else "新中式风格"
    if "甜美" in styles:
        return "甜美温柔风"
    if "通勤" in styles:
        return "简约通勤男装风" if gender == "男" else "简约通勤风"
    return "基础日常风"


def generate_recommendation_rule(data) -> dict:
    categorized_items = []
    target_gender = data.gender if data.gender in ["男", "女"] else "中性"
    style_direction = _resolve_style_direction(data.styles, data.gender)
    reasons = []

    if data.gender == "男":
        if data.body_shape == "H型" and data.waist_type == "不明显":
            _append_item(categorized_items, "合身短夹克", "外套", target_gender)
            _append_item(categorized_items, "直筒休闲裤", "下装", target_gender)
            reasons.append("你的腰线不明显，更适合通过利落短外套和直筒裤强化上短下长的比例。")
        elif data.body_shape == "A型":
            _append_item(categorized_items, "深色直筒裤", "下装", target_gender)
            _append_item(categorized_items, "基础圆领T恤", "上装", target_gender)
            reasons.append("下半身量感更明显时，适合用简洁上装和深色直筒裤平衡整体视觉重心。")
        elif data.body_shape == "倒三角型":
            _append_item(categorized_items, "垂感长裤", "下装", target_gender)
            _append_item(categorized_items, "开领衬衫", "上装", target_gender)
            reasons.append("肩部存在感较强时，开领和垂感下装能弱化肩部并拉开下半身比例。")
    elif data.gender == "女":
        if data.body_shape == "H型" and data.waist_type == "不明显":
            _append_item(categorized_items, "高腰直筒裤", "下装", target_gender)
            _append_item(categorized_items, "短款上衣", "上装", target_gender)
            reasons.append("你的腰线不够明显，适合通过高腰和短款单品增强比例感。")
        elif data.body_shape == "A型":
            _append_item(categorized_items, "A字裙", "裙装", target_gender)
            _append_item(categorized_items, "简洁上装", "上装", target_gender)
            reasons.append("下半身量感更明显时，适合用简洁上装和A字版型优化整体平衡。")
        elif data.body_shape == "倒三角型":
            _append_item(categorized_items, "垂感阔腿裤", "下装", target_gender)
            _append_item(categorized_items, "弱化肩部设计上衣", "上装", target_gender)
            reasons.append("肩部存在感较强时，适合选择能平衡上下身视觉重心的搭配。")
    else:
        if data.body_shape == "H型":
            _append_item(categorized_items, "直筒长裤", "下装", target_gender)
            _append_item(categorized_items, "利落短上装", "上装", target_gender)
            reasons.append("H 型体型更适合强调腰线和纵向比例的搭配。")
        elif data.body_shape == "A型":
            _append_item(categorized_items, "基础上装", "上装", target_gender)
            _append_item(categorized_items, "垂感直筒裤", "下装", target_gender)
            reasons.append("A 型体型更适合用简洁上装搭配垂感下装来平衡轮廓。")
        else:
            _append_item(categorized_items, "开领上装", "上装", target_gender)
            _append_item(categorized_items, "宽松长裤", "下装", target_gender)
            reasons.append("肩部存在感较强时，更适合用开领设计和宽松长裤分散视觉重心。")

    if data.shoulder_type == "宽":
        _append_item(categorized_items, "V领上衣" if data.gender != "男" else "V领针织", "上装", target_gender)
        reasons.append("肩部较宽时，V 领和开阔领口的设计会更显轻盈。")
    elif data.shoulder_type == "窄":
        _append_item(categorized_items, "有层次感的上装", "上装", target_gender)
        reasons.append("肩部较窄时，可以增加上半身层次感来提升整体协调度。")

    if data.leg_ratio == "偏短":
        _append_item(categorized_items, "同色系下装", "下装", target_gender)
        _append_item(categorized_items, "提高腰线单品", "搭配策略", "中性")
        reasons.append("腿部比例偏短时，高腰和同色系搭配有助于拉长视觉比例。")
    elif data.leg_ratio == "偏长":
        _append_item(categorized_items, "短款外套", "外套", target_gender)
        reasons.append("腿部比例较好时，可以更轻松地尝试短款和利落版型。")

    if "显瘦" in data.goals:
        _append_item(categorized_items, "深色下装", "下装", "中性")
        reasons.append("显瘦需求下，更适合选择深色、纵向线条更明显的单品。")

    if "显高" in data.goals:
        _append_item(categorized_items, "提高腰线单品", "搭配策略", "中性")
        reasons.append("显高需求下，应优先突出腰线并减少上下身分割感。")

    if "舒适" in data.goals:
        _append_item(categorized_items, "宽松针织单品", "上装", "中性")
        reasons.append("舒适需求下，柔软面料和适度宽松的版型更合适。")

    if data.scene == "上课":
        _append_item(categorized_items, "休闲帆布鞋" if data.gender != "男" else "休闲运动鞋", "鞋履", "中性")
        reasons.append("上课场景更适合轻松、耐穿、活动方便的搭配。")
    elif data.scene == "面试":
        _append_item(categorized_items, "简洁西装外套", "外套", "中性")
        reasons.append("面试场景建议整体更利落、克制、干净。")
    elif data.scene == "约会":
        _append_item(categorized_items, "柔和配色单品" if data.gender != "男" else "干净针织上装", "上装", target_gender)
        reasons.append("约会场景更适合增加柔和感和精致感。")
    elif data.scene == "出游":
        _append_item(categorized_items, "轻便休闲套装" if data.gender != "男" else "轻便工装套装", "套装", target_gender)
        reasons.append("出游场景更适合舒适、方便活动的穿搭。")

    if not categorized_items:
        _append_item(categorized_items, "基础T恤", "上装", "中性")
        _append_item(categorized_items, "休闲长裤", "下装", "中性")
        reasons.append("当前未命中特殊规则，返回基础日常推荐。")

    recommended_items = [item["name"] for item in categorized_items]
    reason = " ".join(dict.fromkeys(reasons))

    return {
        "recommended_items": recommended_items,
        "categorized_items": categorized_items,
        "recommended_style_direction": style_direction,
        "reason": reason,
    }


def generate_recommendation(data, use_llm_reason: bool = True) -> dict:
    result = generate_recommendation_rule(data)

    if use_llm_reason:
        try:
            input_summary = {
                "gender": data.gender,
                "body_shape": data.body_shape,
                "shoulder_type": data.shoulder_type,
                "waist_type": data.waist_type,
                "leg_ratio": data.leg_ratio,
                "styles": data.styles,
                "scene": data.scene,
                "goals": data.goals
            }

            llm_reason = generate_recommend_reason_with_llm(input_summary, result)
            result["reason"] = llm_reason
        except Exception as e:
            print("LLM recommend reason failed, fallback to rule reason:", e)

    return result
