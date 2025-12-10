from datetime import datetime
from types import SimpleNamespace

from sqlalchemy.orm import Session

from ..models.chat import Project, Chat, Message
from ..api.v1.chat import _get_user_chat_or_404, _get_user_project_or_404

def _ensure_linked_user(channel_user) -> SimpleNamespace:
    """
    We take the user_id field from channel_user and convert it into an object with .id,
    so that the existing code for Project/Chat can work with it.
    """
    if not channel_user.user_id:
        raise RuntimeError("Account is not linked to aplication user.")
    return SimpleNamespace(id = channel_user.user_id)

def _set_active_project(db: Session, channel_user, project_id: int | None) -> None:
    channel_user.active_project_id = project_id
    db.commit()
    db.refresh(channel_user)

def _set_active_chat(db: Session, channel_user, chat_id: int | None) -> None:
    channel_user.active_chat_id = chat_id
    db.commit()
    db.refresh(channel_user)

def router_user_message(chanel_user, text: str, db:Session) -> str:

    raw = (text or "").strip()
    if not raw:
        return "Empty message. Type 'help' to see available commands"
    norm = raw.lower()

    try:
        user = _ensure_linked_user(chanel_user)
    except RuntimeError:
        return (
            "Your account is not linked to any application user yet."
        )

    # --------------- HELP ---------------
    if norm in ("help", "/help"):
        return (
            "Available comands:\n"
            "- project new <name>\n"
            "- project delete <id>\n"
            "- project delete hard <id>\n"
            "- project list\n"
            "- chat new <project_id> <title>\n"
            "- chat move <chat_id> <project_id>\n"
            "- chat delete <chat_id>\n"
            "- chat delete hard <chat_id>\n"
            "- chat open <chat_id>\n"
            "- use project <project_id>\n"
            "- use chat <chat_id>\n"
        )