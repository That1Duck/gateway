# app/services/llm_facade.py
from sqlalchemy.orm import Session
from .llm_port import LLMClient
from .gemini_adapter import GeminiAdapter
from .retry_decorator import RetryDecorator
from .llm_router import LLMRouter
from .llm_factory import make_llm

# Якщо хочеш fallback, коли буде OpenAIAdapter:
# from .openai_adapter import OpenAIAdapter

class LLMFacade:
    def __init__(self, db: Session, user_id: int, *,
                 client: LLMClient | None = None,
                 use_router: bool = False,
                 retries: int = 2,
                 delay: float = 1.0):

        base_client: LLMClient = client or make_llm(
            db = db,
            user_id= user_id,
            user_router= use_router
        )

        retry_client: LLMClient = RetryDecorator(
            base_client,
            retries=retries,
            delay=delay
        )

        self.client = retry_client

    def complete(self, messages, **kw) -> str:
        return next(self.client.chat_stream(messages, **kw))

    def complete_stream(self, messages, **kw):
        return self.client.chat_stream(messages, **kw)
