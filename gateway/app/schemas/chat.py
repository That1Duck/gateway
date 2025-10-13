from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal, Optional

Role = Literal["user", "assistant", "system"]

class ProjectIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)

class ProjectOut(BaseModel):
    id: int
    name: str
    created_at: datetime
    class Config: from_attributes = True

class ChatIn(BaseModel):
    title: str = "New chat"
    provider: str = "gemini"
    model: str = "gemini-1.5-pro"
    settings: Optional[dict] = None

class ChatOut(BaseModel):
    id: int
    project_id: Optional[int] = None
    title: str
    provider: str
    model: str
    settings_json: Optional[dict] = None
    created_at: datetime
    deleted_at: Optional[datetime] = None
    class Config: from_attributes = True

class ChatUpdate(BaseModel):
    title: Optional[str] = None
    # None → переместить в «без проекта»
    project_id: Optional[int | None] = None
    settings: Optional[dict] = None

class MessageIn(BaseModel):
    role: Role
    content: str

class MessageOut(BaseModel):
    id: int
    chat_id: int
    role: Role
    content: str
    meta_json: Optional[dict] = None
    created_at: datetime
    class Config: from_attributes = True

class CompletionIn(BaseModel):
    messages: list[MessageIn]
    model: Optional[str] = None
    settings: Optional[dict] = None

class CompletionOut(BaseModel):
    message: MessageOut
