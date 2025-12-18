from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...schemas.llm_settings import (
    LlmSettingsOut,
    LlmSettingsUpdate,
    LlmCredentialUpdate
)
from ...services.llm_settings import (
    get_or_create_settings,
    update_settings,
    set_api_key,
    has_api_key
)
from ...deps import current_user
from ...models.user import User
from ...core.redis_cache import cache_get_json, cache_set_json, cache_delete

def _settings_cache_key(user_id: int) -> str:
    return f"user:{user_id}:llm_settings_view"

router = APIRouter(prefix="/settings/llm", tags=["llm-settings"])

@router.get("", response_model=LlmSettingsOut)
@router.get("/", response_model=LlmSettingsOut)
def get_llm_settings(
        db: Session = Depends(get_db),
        user: User = Depends(current_user)
):
    """
    Get LLM settings for the current user +
    information about which API keys are configured (without the keys themselves).
    """
    # checking if cache is in redis
    cache_key = _settings_cache_key(user.id)
    cached = cache_get_json(cache_key)
    if cached is not None:
        return cached

    settings = get_or_create_settings(db, user.id)

    has_openai = has_api_key(db, user.id, "openai")
    has_gemini = has_api_key(db, user.id, "gemini")
    has_grok = has_api_key(db, user.id, "grok")

    result = LlmSettingsOut(
        default_provider=settings.default_provider,
        default_model=settings.default_model,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
        use_streaming=settings.use_streaming,
        use_rag_by_default=settings.use_rag_by_default,
        log_prompts=settings.log_prompts,
        timeout_seconds=settings.timeout_seconds,
        has_openai_key=has_openai,
        has_gemini_key=has_gemini,
        has_grok_key=has_grok,
    )

    # throw to cache
    cache_set_json(cache_key, result.model_dump(), ttl_seconds=300)
    return result

@router.put("", response_model=LlmSettingsOut)
@router.put("/", response_model=LlmSettingsOut)
def update_llm_settings(
        payload: LlmSettingsUpdate,
        db: Session = Depends(get_db),
        user: User = Depends(current_user)
):
    """
    Update the user's regular (non-secret) LLM settings.
    """
    settings = update_settings(
        db,
        user.id,
        default_provider=payload.default_provider,
        default_model=payload.default_model,
        temperature=payload.temperature,
        max_tokens=payload.max_tokens,
        use_streaming=payload.use_streaming,
        use_rag_by_default=payload.use_rag_by_default,
        log_prompts=payload.log_prompts,
        timeout_seconds=payload.timeout_seconds,
    )

    has_openai = has_api_key(db, user.id, "openai")
    has_gemini = has_api_key(db, user.id, "gemini")
    has_grok = has_api_key(db, user.id, "grok")

    result = LlmSettingsOut(
        default_provider=settings.default_provider,
        default_model=settings.default_model,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
        use_streaming=settings.use_streaming,
        use_rag_by_default=settings.use_rag_by_default,
        log_prompts=settings.log_prompts,
        timeout_seconds=settings.timeout_seconds,
        has_openai_key=has_openai,
        has_gemini_key=has_gemini,
        has_grok_key=has_grok,
    )

    cache_key = _settings_cache_key(user.id)
    cache_set_json(cache_key, result.model_dump(), ttl_seconds=300)
    return result

@router.put("/credentials")
def update_llm_credentials(
        payload: LlmCredentialUpdate,
        db: Session = Depends(get_db),
        user: User = Depends(current_user)
):
    """
    Update provider API keys for the current user.
    Each key is optional — we only update those that have arrived.
    Response without the keys themselves (status only).
    """

    if payload.openai_api_key:
        set_api_key(db, user.id, "openai", payload.openai_api_key)
    if payload.gemini_api_key:
        set_api_key(db, user.id, "gemini", payload.gemini_api_key)
    if payload.grok_api_key:
        set_api_key(db, user.id, "grok", payload.grok_api_key)

    has_openai = has_api_key(db, user.id, "openai")
    has_gemini = has_api_key(db, user.id, "gemini")
    has_grok = has_api_key(db, user.id, "grok")

    settings = get_or_create_settings(db, user.id)
    result = LlmSettingsOut(
        default_provider=settings.default_provider,
        default_model=settings.default_model,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
        use_streaming=settings.use_streaming,
        use_rag_by_default=settings.use_rag_by_default,
        log_prompts=settings.log_prompts,
        timeout_seconds=settings.timeout_seconds,
        has_openai_key=has_openai,
        has_gemini_key=has_gemini,
        has_grok_key=has_grok,
    )

    cache_key = _settings_cache_key(user.id)
    cache_set_json(cache_key, result.model_dump(), ttl_seconds=300)

    return {
        "status": "ok",
        "has_openai_key": has_openai,
        "has_gemini_key": has_gemini,
        "has_grok_key": has_grok,
    }