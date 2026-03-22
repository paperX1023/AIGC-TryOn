import base64
import json
from pathlib import Path

from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None


def _ensure_client() -> OpenAI:
    if client is None:
        raise RuntimeError("OPENAI_API_KEY 未配置")
    return client


def _image_path_to_data_url(image_path: str) -> str:
    suffix = Path(image_path).suffix.lower()
    media_type = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }.get(suffix, "image/jpeg")

    encoded = base64.b64encode(Path(image_path).read_bytes()).decode("utf-8")
    return f"data:{media_type};base64,{encoded}"


def parse_style_text_with_llm(text: str) -> dict:
    response = _ensure_client().responses.create(
        model=settings.openai_model,
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "你是一个穿搭需求解析助手。"
                            "请把用户输入解析成结构化结果。"
                            "你必须返回 JSON，并严格符合给定 schema。"
                        )
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": text}
                ]
            }
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "style_parse_result",
                "schema": {
                    "type": "object",
                    "properties": {
                        "styles": {"type": "array", "items": {"type": "string"}},
                        "scene": {"type": "string"},
                        "goals": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["styles", "scene", "goals"],
                    "additionalProperties": False
                }
            }
        }
    )

    return json.loads(response.output_text)


def generate_recommend_reason_with_llm(input_summary: dict, recommend_result: dict) -> str:
    response = _ensure_client().responses.create(
        model=settings.openai_model,
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "你是一个穿搭推荐文案助手。"
                            "你的任务是根据用户身材特征、风格需求、场景和推荐单品，"
                            "生成一段自然、简洁、适合直接展示给用户的中文推荐理由。"
                            "不要输出标题，不要分点，不要使用 markdown。"
                            "长度控制在 60 到 120 字。"
                        )
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            f"用户信息：{json.dumps(input_summary, ensure_ascii=False)}\n"
                            f"推荐结果：{json.dumps(recommend_result, ensure_ascii=False)}"
                        )
                    }
                ]
            }
        ]
    )

    return response.output_text.strip()


def detect_gender_from_image_with_llm(image_path: str) -> str:
    response = _ensure_client().responses.create(
        model=settings.openai_vision_model or settings.openai_model,
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "你是服装系统的人像属性识别助手。"
                            "请根据人物照片判断外观呈现更接近男性、女性或无法判断。"
                            "你必须返回 JSON，并严格符合给定 schema。"
                        ),
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "请仅返回 gender 字段，枚举值为：男、女、未知。"},
                    {"type": "input_image", "image_url": _image_path_to_data_url(image_path)},
                ],
            },
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "gender_detect_result",
                "schema": {
                    "type": "object",
                    "properties": {
                        "gender": {"type": "string", "enum": ["男", "女", "未知"]},
                    },
                    "required": ["gender"],
                    "additionalProperties": False,
                },
            }
        },
    )

    return json.loads(response.output_text)["gender"]
