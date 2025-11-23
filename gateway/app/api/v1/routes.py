from fastapi import APIRouter
from .system import router as system_router
from .auth import router as auth_router
from .chat import router as projects_router
from .chat import chats as chats_router
from .document import router as doc_router
from ...whatsapp_bot.webhook import router as whatsapp_router

"""
Main router for v1 API
Connect systems module 
Connect auth module
Connect chat router
"""

api_router = APIRouter()
api_router.include_router(system_router)
api_router.include_router(auth_router)
api_router.include_router(projects_router)
api_router.include_router(chats_router)
api_router.include_router(doc_router)
api_router.include_router(whatsapp_router)

