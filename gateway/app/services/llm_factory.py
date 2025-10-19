# app/services/llm_factory.py
from .gemini_adapter import GeminiAdapter
from .llm_router import LLMRouter

def make_llm(provider: str = "gemini", fallback: str | None = None):
    if provider == "openai":
        primary = GeminiAdapter()
    else:
        primary = GeminiAdapter()
    if fallback:
        fb = GeminiAdapter() if fallback == "openai" else GeminiAdapter()
        return LLMRouter(primary, fb)
    return primary
