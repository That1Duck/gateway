import google.generativeai as genai
from typing import List, Dict, Optional
from ..core.config import settings

class LLMService:
    def __init__(self):
        api_key = settings.GOOGLE_API_KEY
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY is not set")
        genai.configure(api_key=api_key)

    def complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        settings_dict: Optional[dict] = None,
    ) -> str:
        # ---- побудова історії
        history = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if not content:
                continue
            if role == "assistant":
                history.append({"role": "model", "parts": [content]})
            else:
                history.append({"role": "user", "parts": [content]})

        # ---- конфіг генерації
        generation_config = {
            "temperature": (settings_dict or {}).get("temperature", 0.7),
            "top_p": (settings_dict or {}).get("top_p", 0.95),
            "max_output_tokens": (settings_dict or {}).get("max_tokens", 1024),
        }

        # ---- список моделей для спроб (основна → запасні)
        candidates = [model or "gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite"]

        for name in candidates:
            try:
                print(f"[LLMService] trying model: {name}")
                llm = genai.GenerativeModel(name, generation_config=generation_config)
                chat = llm.start_chat(history=history)
                resp = chat.send_message(" ")  # тригер відповіді
                text = (resp.text or "").strip()
                if text:
                    print(f"[LLMService] success with model: {name}")
                    return text
            except Exception as e:
                print(f"[LLMService] model {name} failed → {e}")

        # ---- якщо всі спроби не вдалися
        return "⚠️ Gemini не доступний зараз, спробуйте пізніше."
