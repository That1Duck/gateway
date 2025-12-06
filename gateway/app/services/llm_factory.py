# app/services/llm_factory.py
from sqlalchemy.orm import Session
from .gemini_adapter import GeminiAdapter
from .llm_router import LLMRouter
from .llm_port import LLMClient
from .llm_settings import get_or_create_settings

def make_llm(db: Session, user_id:int, *, user_router: bool = False) -> LLMClient:
    """
    Фабрика LLM-клієнта для конкретного користувача.

    - Читає llm_settings.user_id → default_provider
    - Створює відповідний адаптер (з db + user_id всередині)
    - Опційно обгортає primary + fallback у LLMRouter.
    """
    settings = get_or_create_settings(db, user_id)
    provider = settings.default_provider or "gemini"
    default_model = settings.default_model or "gemini-2.5-flash"

    if provider == "gemini":
        primary: LLMClient = GeminiAdapter(db, user_id = user_id, model=default_model)
    else:
        primary = GeminiAdapter(db, user_id = user_id, model=default_model)
    if user_router:
        fb = GeminiAdapter(db, user_id, "gemini-2.5-flash")
        return LLMRouter(primary, fb)
    return primary
