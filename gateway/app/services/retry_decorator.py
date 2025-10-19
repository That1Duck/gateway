# app/services/retry_decorator.py
from time import sleep
from .llm_port import LLMClient

class RetryDecorator(LLMClient):
    """
    Обгортка над будь-яким LLMClient, що повторює запит при помилці.
    """
    def __init__(self, client: LLMClient, retries: int = 2, delay: float = 0.5):
        self.client = client
        self.retries = retries
        self.delay = delay

    def generate(self, prompt: str, **kw):
        for attempt in range(self.retries + 1):
            try:
                return self.client.generate(prompt, **kw)
            except Exception as e:
                if attempt == self.retries:
                    raise
                print(f"[RetryDecorator] Error: {e} → retrying {attempt+1}/{self.retries}")
                sleep(self.delay)

    def chat_stream(self, messages, **kw):
        for attempt in range(self.retries + 1):
            try:
                yield from self.client.chat_stream(messages, **kw)
                break
            except Exception as e:
                if attempt == self.retries:
                    raise
                print(f"[RetryDecorator] Error: {e} → retrying {attempt+1}/{self.retries}")
                sleep(self.delay)
