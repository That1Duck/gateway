from typing import Optional

class LLMService:
    """
    Пока — заглушка. Вернём короткий эхо-ответ.
    Позже сюда подключим Google Gemini SDK.
    """
    def complete(
        self,
        messages: list[dict],
        model: str = "gemini-1.5-pro",
        settings: Optional[dict] = None,
    ) -> str:
        last_user = next((m for m in reversed(messages) if m.get("role") == "user"), None)
        text = last_user["content"] if last_user else ""
        return f"🤖 (demo) I received: {text[:400]}"