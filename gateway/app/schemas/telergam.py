from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field

class TelegramSyncUserRequest(BaseModel):
    telegram_id: int = Field(..., example = 1234567)
    user_id: int = Field(..., description= "ID of user in db")

    user_name: Optional[str] = Field(None, example="User_name")
    first_name: Optional[str] = Field(None, example="Name")
    last_name: Optional[str] = Field(None, example="Last_Name")
    language_code: Optional[str] = Field(None, example="en")

class TelegramSyncResponse(BaseModel):
    telegram_account_id: int
    user_id: int
    telegram_id: int
    active_chat_id: int