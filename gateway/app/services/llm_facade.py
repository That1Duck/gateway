# app/services/llm_facade.py
from .llm_port import LLMClient
from .gemini_adapter import GeminiAdapter
from .retry_decorator import RetryDecorator
from .llm_router import LLMRouter

# Якщо хочеш fallback, коли буде OpenAIAdapter:
# from .openai_adapter import OpenAIAdapter

class LLMFacade:
    def __init__(self, client: LLMClient | None = None):
        # 🔹 Базовий клієнт
        base_client = client or GeminiAdapter()

        # 🔹 Обгортка з ретраями
        retry_client = RetryDecorator(base_client, retries=2, delay=1.0)

        # 🔹 Якщо додамо fallback (напр. OpenAI)
        # fallback_client = OpenAIAdapter()
        # self.client = LLMRouter(retry_client, fallback_client)
        # Поки що просто retry
        self.client = retry_client

    def complete(self, messages, **kw) -> str:
        return next(self.client.chat_stream(messages, **kw))

    def complete_stream(self, messages, **kw):
        return self.client.chat_stream(messages, **kw)
