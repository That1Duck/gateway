from datetime import datetime
from sqlalchemy.orm import Session
from ..models.chat import Message, Chat


def handle_plain_text(
    db: Session,
    *,
    user_id: int,
    chat_id: int | None,
    text: str,
) -> str:
    """
    Processes plain text (NOT a command):
    1) Ensures chat_id is present
    2) Saves Message(role=‘user’)
    3) Calls LLM (PLACEHOLDER for now)
    4) Saves Message(role=‘assistant’)
    5) Returns the response
    """

    if chat_id is None:
        chat = Chat(user_id=user_id, title="Telegram chat")
        db.add(chat)
        db.commit()
        db.refresh(chat)
        chat_id = chat.id

    user_msg = Message(
        chat_id=chat_id,
        role="user",
        content=text,
        created_at=datetime.utcnow(),
    )
    db.add(user_msg)
    db.commit()

    # TODO: LLM pipeline
    reply = "LLM pipeline is not connected yet (TODO)."

    assistant_msg = Message(
        chat_id=chat_id,
        role="assistant",
        content=reply,
        created_at=datetime.utcnow(),
    )
    db.add(assistant_msg)
    db.commit()

    return reply