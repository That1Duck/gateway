from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from ..models.telegram_account import TelegramAccount
from ..models.chat import Chat

def get_or_create_telegram_account(
        db: Session,
        *,
        telegram_id: int,
        user_id: int,
        user_name: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        language_code: Optional[str] = None,
) -> TelegramAccount:
    """
    Finds TelegramAccount by telegram_id.
    If not, creates a new one linked to user_id.
    Always updates basic information (user_name, first_name, etc.) and last_seen_at.
    """

    account: TelegramAccount | None = (
        db.query(TelegramAccount)
        .filter(TelegramAccount.telegram_id == telegram_id)
        .first()
    )

    now = datetime.now()
    if account is not None:
        if user_name is not None:
            account.user_name = user_name
        if first_name is not None:
            account.first_name = first_name
        if last_name is not None:
            account.last_name = last_name
        if language_code is not None:
            account.language_code = language_code

        account.last_seen_at = now
        db.add(account)
        db.commit()
        db.refresh(account)
        return account

    account = TelegramAccount(
        telegram_id = telegram_id,
        user_id = user_id,
        user_name = user_name,
        first_name = first_name,
        last_name = last_name,
        language_code = language_code,
        last_seen_at = now,
    )

    db.add(account)
    db.commit()
    db.refresh(account)
    return account

def ensure_active_chat(
        db: Session,
        *,
        account: TelegramAccount,
) -> TelegramAccount:
    """
    Ensures that TelegramAccount has active_chat.
    If active_chat_id is empty, create a new chat for this user.
    """
    if account.active_chat_id is not None:
        return account

    chat = Chat(
        user_id = account.user_id,
        title = f"Telegram chat ({account.telegram_id})",
    )

    db.add(chat)
    db.commit()
    db.refresh(chat)

    account.active_chat_id = chat.id
    account.active_chat = chat
    db.add(account)
    db.commit()
    db.refresh(account)

    return account