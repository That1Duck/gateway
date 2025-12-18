from datetime import datetime, timedelta
import secrets
import string
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...models.user import User
from ...models.chat import Chat
from ...models.telegram_account import TelegramAccount

from ...db.session import get_db
from ...deps import current_user

from ...schemas.telegram_link import (
    TelegramLinkRequest,
    TelegramLinkResponse,
    TelegramLinkCodeResponse,
)

router = APIRouter(tags=["telegram-link"])

def _gen_code(n: int = 8) -> str:
    """Generating secret code for link"""
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(n))

@router.post("/users/me/telegram/link-code", response_model=TelegramLinkCodeResponse)
def create_telegram_link_code(
        db: Session = Depends(get_db),
        user: User = Depends(current_user)
):
    code = _gen_code(8)
    expires = datetime.utcnow() + timedelta(minutes=10)

    user.telegram_link_code = code
    user.telegram_link_expires_at = expires

    db.add(user)
    db.commit()
    db.refresh(user)

    return TelegramLinkCodeResponse(
        code = code,
        expires_at=expires,
    )

@router.post("/integrations/telegram/link", response_model=TelegramLinkResponse)
def link_telegram_account(
        payload: TelegramLinkRequest,
        db: Session = Depends(get_db)
):
    user: User | None = (
        db.query(User)
        .filter(User.telegram_link_code == payload.code)
        .first()
    )
    if not user:
        raise HTTPException(status_code=400, detail="Invalid link code")

    if not user.telegram_link_expires_at or user.telegram_link_expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Link code expired")

    account: TelegramAccount | None = (
        db.query(TelegramAccount)
        .filter(TelegramAccount.telegram_id == payload.telegram_id)
        .first()
    )
    if not account:
        account = TelegramAccount(
            telegram_id=payload.telegram_id,
            user_id = user.id,
            user_name=payload.user_name,
            first_name=payload.first_name,
            last_name=payload.last_name,
            language_code=payload.language_code,
            is_active=True,
            last_seen_at=datetime.utcnow(),
        )
        db.add(account)
        db.commit()
        db.refresh(account)
    else:
        account.user_name = payload.user_name or account.user_name
        account.first_name = payload.first_name or account.first_name
        account.last_name = payload.last_name or account.last_name
        account.language_code = payload.language_code or account.language_code
        account.last_seen_at = datetime.utcnow()
        account.user_id = user.id

    account.user_id = user.id
    if not account.active_chat_id:
        chat = Chat(
            user_id = user.id,
            title = f"Telegram chat ({payload.telegram_id})"
        )
        db.add(chat)
        db.commit()
        db.refresh(chat)
        account.active_chat_id = chat.id

    user.telegram_link_code = None
    user.telegram_link_expires_at = None

    db.add_all([user, account])
    db.commit()
    db.refresh(account)

    return  TelegramLinkResponse(
        linked= True,
        user_id= user.id,
        active_chat_id= account.active_chat_id,
    )