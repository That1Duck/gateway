# app/services/gemini_adapter.py
from typing import Iterable, Dict, List, Any
from .llm_port import LLMClient
from .llm_service import LLMService  # ваш реальный сервис работы с Gemini

class GeminiAdapter(LLMClient):
    def __init__(self, model: str = "gemini-2.5-flash"):
        self.inner = LLMService()
        self.model = model

    def generate(self, prompt: str, **kw) -> str:
        # оборачиваем prompt в формат history из одной user-реплики
        messages = [{"role": "user", "content": prompt}]
        return self.inner.complete(messages, model=self.model, settings=kw.get("settings"))

    def chat_stream(self, messages: List[Dict[str, str]], **kw) -> Iterable[str]:
        # у нас пока нет реального стриминга — возвращаем одним чанком
        text = self.inner.complete(
            messages,
            model=self.model,
            settings_dict=kw.get("settings") or kw.get("settings_dict")
        )
        yield text
