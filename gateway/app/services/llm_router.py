# app/services/llm_router.py
from .llm_port import LLMClient

class LLMRouter(LLMClient):
    """
    Primary → fallback router для кількох LLM.
    """
    def __init__(self, primary: LLMClient, fallback: LLMClient | None = None):
        self.primary = primary
        self.fallback = fallback

    def generate(self, prompt: str, **kw):
        try:
            return self.primary.generate(prompt, **kw)
        except Exception as e:
            print(f"[LLMRouter] Primary failed: {e}")
            if not self.fallback:
                raise
            print("[LLMRouter] Switching to fallback provider…")
            return self.fallback.generate(prompt, **kw)

    def chat_stream(self, messages, **kw):
        try:
            yield from self.primary.chat_stream(messages, **kw)
        except Exception as e:
            print(f"[LLMRouter] Primary failed: {e}")
            if not self.fallback:
                raise
            print("[LLMRouter] Switching to fallback provider…")
            yield from self.fallback.chat_stream(messages, **kw)
