from fastapi import APIRouter
from src.app.log_route import LogRoute
from src.chat.handlers.api.v1.router import router as chat_router
from src.chat_participant.handlers.api.v1.router import router as chat_participant_router
from src.message.handlers.api.v1.router import router as message_router
from src.message_read.handlers.api.v1.router import router as message_read_router
from src.user.handlers.api.v1.router import router as user_router

router = APIRouter(route_class=LogRoute)

router.include_router(user_router, prefix="/user", tags=["user"])
router.include_router(chat_router, prefix="/chat", tags=["chat"])
router.include_router(message_router, prefix="/message", tags=["message"])
router.include_router(chat_participant_router, prefix="/chat_participant", tags=["chat_participant"])
router.include_router(message_read_router, prefix="/message-read", tags=["message_read"])
