import google.generativeai as genai
from typing import List, Dict, Optional
from .llm_settings import get_or_create_settings, get_api_key
from sqlalchemy.orm import Session

class LLMService:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        self.llm_settings = get_or_create_settings(db, user_id)
        api_key = get_api_key(db, user_id, "gemini")
        if not api_key:
            raise RuntimeError("Gemini API key is not configured for this user.")
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

        base_temp = self.llm_settings.temperature or 0.7
        base_max_tokens = self.llm_settings.max_tokens or 1024

        # ---- конфіг генерації
        generation_config = {
            "temperature": (settings_dict or {}).get("temperature", base_temp),
            "top_p": (settings_dict or {}).get("top_p", 0.95),
            "max_output_tokens": (settings_dict or {}).get("max_tokens", base_max_tokens),
        }

        default_model = self.llm_settings.default_model or "gemini-2.5-pro"
        main_model = model or default_model

        # ---- список моделей для спроб (основна → запасні)
        candidates = [main_model or "gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite"]

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
