from pydantic import BaseModel, Field

class TelegramMessageRequest(BaseModel):
    telegram_id: int = Field(..., example=123456789)
    text: str = Field(..., min_length=1)

class TelegramMessageResponse(BaseModel):
    reply: str