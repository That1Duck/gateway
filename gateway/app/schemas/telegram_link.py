from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class TelegramLinkCodeResponse(BaseModel):
    code: str
    expires_at: datetime

class TelegramLinkRequest(BaseModel):
    telegram_id: int = Field(..., example= 12345678)
    code: str = Field(..., min_length= 4)

    user_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: Optional[str] = None

class TelegramLinkResponse(BaseModel):
    linked: bool
    user_id: int
    active_chat_id: int