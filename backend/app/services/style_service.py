import logging

from app.services.openai_service import parse_style_text_with_llm
from app.services.style_normalizer import extract_style_result_from_text, normalize_style_result

logger = logging.getLogger(__name__)


def parse_style_text_rule(text: str) -> dict:
    return extract_style_result_from_text(text).model_dump(mode="json")


def parse_style_text(text: str, use_llm: bool = False) -> dict:
    if use_llm:
        try:
            return normalize_style_result(parse_style_text_with_llm(text)).model_dump(mode="json")
        except Exception as exc:
            logger.warning("LLM parse failed, fallback to rule parse: %s", exc)
            return parse_style_text_rule(text)

    return parse_style_text_rule(text)
