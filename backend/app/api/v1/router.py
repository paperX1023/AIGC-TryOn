from fastapi import APIRouter
from app.api.v1.endpoints import body, chat, health, recommend, style, tryon

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router, tags=["health"])
api_router.include_router(style.router, prefix="/style", tags=["style"])
api_router.include_router(body.router, prefix="/body", tags=["body"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(recommend.router, tags=["recommend"])
api_router.include_router(tryon.router, tags=["tryon"])
