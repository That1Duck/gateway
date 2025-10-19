# app/services/llm_port.py — уніфікований інтерфейс
from abc import ABC, abstractmethod
from typing import Iterable, Dict, Any, List

class LLMClient(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kw) -> str: ...
    @abstractmethod
    def chat_stream(self, messages: List[Dict[str,str]], **kw) -> Iterable[str]: ...
