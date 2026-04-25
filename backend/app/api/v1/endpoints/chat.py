import json

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse

from app.api.deps import get_optional_current_user, resolve_request_user_id
from app.schemas.chat import ChatRecommendRequest, ChatRecommendResponse
from app.schemas.user import UserResponse
from app.services.chat_service import generate_chat_recommendation, stream_chat_recommendation

router = APIRouter()


def _format_sse(event: str, data) -> str:
    payload = json.dumps(jsonable_encoder(data), ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n"


@router.post("/recommend", response_model=ChatRecommendResponse)
def recommend_chat(
    data: ChatRecommendRequest,
    current_user: UserResponse | None = Depends(get_optional_current_user),
):
    data.user_id = resolve_request_user_id(data.user_id, current_user)
    result = generate_chat_recommendation(data)
    return ChatRecommendResponse(**result)


@router.post("/recommend/stream")
def recommend_chat_stream(
    data: ChatRecommendRequest,
    current_user: UserResponse | None = Depends(get_optional_current_user),
):
    data.user_id = resolve_request_user_id(data.user_id, current_user)

    def event_stream():
        try:
            for item in stream_chat_recommendation(data):
                yield _format_sse(item["event"], item["data"])
        except Exception as exc:
            yield _format_sse("error", {"message": str(exc) or "生成推荐失败"})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
