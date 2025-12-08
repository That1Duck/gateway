from typing import Optional

from sqlalchemy.orm import Session

from ..models.llm_settings import LlmSettings
from ..models.llm_credentials import LlmApiCredential
from ..core.encryption import encrypt_api_key, decrypt_api_key

# --------- Settings ---------
def get_or_create_settings(db: Session, user_id: int) -> LlmSettings:
    settings = (
        db.query(LlmSettings)
        .filter(LlmSettings.user_id == user_id)
        .first()
    )
    if settings:
        return settings

    settings = LlmSettings(user_id = user_id)
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings

def update_settings(
        db: Session,
        user_id: int,
        *,
        default_provider: Optional[str] = None,
        default_model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        use_streaming: Optional[bool] = None,
        use_rag_by_default: Optional[bool] = None,
        log_prompts: Optional[bool] = None,
        timeout_seconds: Optional[int] = None
) -> LlmSettings:
    settings = get_or_create_settings(db, user_id)

    if default_provider is not None:
        settings.default_provider = default_provider
    if default_model is not None:
        settings.default_model = default_model
    if temperature is not None:
        settings.temperature = float(temperature)
    if max_tokens is not None:
        settings.max_tokens = max_tokens
    if use_streaming is not None:
        settings.use_streaming = use_streaming
    if use_rag_by_default is not None:
        settings.use_rag_by_default = use_rag_by_default
    if log_prompts is not None:
        settings.log_prompts = log_prompts
    if timeout_seconds is not None:
        settings.timeout_seconds = timeout_seconds

    db.commit()
    db.refresh(settings)
    return settings


# --------- Credentials ---------

def set_api_key(db: Session, user_id: int, provider:str, api_key: str) -> LlmApiCredential:
    """
    Encrypt and save/update the API key for a specific provider
    """
    encrypt = encrypt_api_key(api_key)

    cred = (
        db.query(LlmApiCredential)
        .filter(
            LlmApiCredential.user_id == user_id,
            LlmApiCredential.provider == provider,
        )
        .first()
    )

    if cred is None:
        cred = LlmApiCredential(
            user_id = user_id,
            provider = provider,
            encrypted_api_key=encrypt,
        )
        db.add(cred)
    else:
        cred.encrypted_api_key = encrypt

    db.commit()
    db.refresh(cred)
    return cred

def get_api_key(db: Session, user_id: int, provider: str) -> Optional[str]:
    """
    Return the decrypted API key( or None if not configured).
    Call ONLY when you really need to knock on LLM.
    """

    cred = (
        db.query(LlmApiCredential)
        .filter(
            LlmApiCredential.user_id == user_id,
            LlmApiCredential.provider == provider
        )
        .first()
    )
    if cred is None:
        return None
    return decrypt_api_key(cred.encrypted_api_key)

def has_api_key(db: Session, user_id: int, provider: str) -> bool:
    """
    Only kkey presence check (for UI: "key set: yes/no"), without decryption
    """
    return (
        db.query(LlmApiCredential)
        .filter(
            LlmApiCredential.user_id == user_id,
            LlmApiCredential.provider == provider
        )
        .count()
        > 0
    )