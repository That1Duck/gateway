from typing import Optional
from pydantic import BaseModel, Field

class LlmSettingsOut(BaseModel):
    default_provider: str
    default_model: str
    temperature: float
    max_tokens: Optional[int]
    use_streaming: bool
    use_rag_by_default: bool
    log_prompts: bool
    timeout_seconds: int

    has_openai_key: bool = False
    has_gemini_key: bool = False
    has_grok_key: bool = False

    class Config:
        from_attributes = True

class LlmSettingsUpdate(BaseModel):
    default_provider: Optional[str] = Field(None, description="openai|gemini|grok|...")
    default_model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    use_streaming: Optional[bool] = None
    use_rag_by_default: Optional[bool] = None
    log_prompts: Optional[bool] = None
    timeout_seconds: Optional[int] = None

class LlmCredentialUpdate(BaseModel):
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    grok_api_key: Optional[str] = None