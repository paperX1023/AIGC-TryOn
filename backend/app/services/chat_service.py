from dataclasses import dataclass
from time import sleep
from uuid import uuid4

from app.services.persistence_service import save_chat_exchange
from app.services.recommend_service import generate_recommendation
from app.services.style_service import parse_style_text


@dataclass
class _RecommendInput:
    gender: str
    body_shape: str
    shoulder_type: str
    waist_type: str
    leg_ratio: str
    styles: list[str]
    scene: str
    goals: list[str]


def _format_list(values: list[str]) -> str:
    return "、".join(values)


def _build_reply_without_body(parsed_result: dict) -> str:
    style_text = _format_list(parsed_result["styles"])
    goal_text = _format_list(parsed_result["goals"])
    scene = parsed_result["scene"]

    return (
        f"我先帮你解析了需求：你更偏向{style_text}，场景是{scene}，目标是{goal_text}。"
        "如果先完成体型分析，我可以进一步结合你的身材给出更精准的单品推荐。"
    )


def _build_reply_with_recommendation(body_context, parsed_result: dict, recommend_result: dict) -> str:
    style_direction = recommend_result["recommended_style_direction"]
    items = _format_list(recommend_result["recommended_items"])
    reason = recommend_result["reason"]

    return (
        f"结合你的{body_context.gender}性别特征、{body_context.body_shape}体型、"
        f"{body_context.shoulder_type}肩以及{_format_list(parsed_result['styles'])}需求，"
        f"我更建议你尝试{style_direction}。"
        f"可以优先从{items}这些单品入手。{reason}"
    )


def _split_reply(reply: str, chunk_size: int = 8):
    for index in range(0, len(reply), chunk_size):
        yield reply[index:index + chunk_size]


def _build_response_from_parsed(data, parsed_result: dict, session_id: str) -> dict:
    if not data.body_context:
        response = {
            "reply": _build_reply_without_body(parsed_result),
            "session_id": session_id,
            "parsed_result": parsed_result,
            "recommend_result": None,
        }
        save_chat_exchange(
            user_id=data.user_id,
            session_code=session_id,
            user_text=data.text,
            assistant_reply=response["reply"],
            parsed_result=parsed_result,
            recommend_result=None,
        )
        return response

    recommend_input = _RecommendInput(
        gender=data.body_context.gender,
        body_shape=data.body_context.body_shape,
        shoulder_type=data.body_context.shoulder_type,
        waist_type=data.body_context.waist_type,
        leg_ratio=data.body_context.leg_ratio,
        styles=parsed_result["styles"],
        scene=parsed_result["scene"],
        goals=parsed_result["goals"],
    )

    recommend_result = generate_recommendation(recommend_input, use_llm_reason=True)

    response = {
        "reply": _build_reply_with_recommendation(data.body_context, parsed_result, recommend_result),
        "session_id": session_id,
        "parsed_result": parsed_result,
        "recommend_result": recommend_result,
    }
    save_chat_exchange(
        user_id=data.user_id,
        session_code=session_id,
        user_text=data.text,
        assistant_reply=response["reply"],
        parsed_result=parsed_result,
        recommend_result=recommend_result,
    )
    return response


def _build_response(data) -> dict:
    parsed_result = parse_style_text(data.text, use_llm=True)
    session_id = data.session_id or uuid4().hex
    return _build_response_from_parsed(data, parsed_result, session_id)


def generate_chat_recommendation(data) -> dict:
    return _build_response(data)


def stream_chat_recommendation(data):
    session_id = data.session_id or uuid4().hex
    yield {
        "event": "session",
        "data": {"session_id": session_id},
    }

    parsed_result = parse_style_text(data.text, use_llm=True)
    yield {
        "event": "meta",
        "data": {
            "session_id": session_id,
            "parsed_result": parsed_result,
            "recommend_result": None,
        },
    }

    response = _build_response_from_parsed(data, parsed_result, session_id)
    if response["recommend_result"] is not None:
        yield {
            "event": "meta",
            "data": {
                "session_id": response["session_id"],
                "parsed_result": response["parsed_result"],
                "recommend_result": response["recommend_result"],
            },
        }

    for chunk in _split_reply(response["reply"]):
        yield {
            "event": "chunk",
            "data": {"content": chunk},
        }
        sleep(0.02)

    yield {
        "event": "done",
        "data": response,
    }
