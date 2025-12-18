from datetime import datetime
from sqlalchemy.orm import Session
from ..models.chat import Message, Chat
from ..schemas.chat import CompletionIn, MessageIn
from ..services.llm_facade import LLMFacade

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
    3) Calls histoty of messages
    4) Calls LLM (PLACEHOLDER for now)
    5) Returns the response
    """

    if chat_id is None:
        return (
            "No active chat.\n"
            "Use:\n"
            "- chat new <project_id> <title>\n"
            "- use chat <chat_id>"
        )

    user_msg = Message(
        chat_id=chat_id,
        role="user",
        content=text,
        created_at=datetime.utcnow(),
    )
    db.add(user_msg)
    db.commit()

    messages = (
        db.query(Message)
        .filter(Message.chat_id == chat_id)
        .order_by(Message.created_at.asc(), Message.id.asc())
        .all()
    )

    messages_for_llm = [{"role": m.role, "content": m.content} for m in messages]

    facade = LLMFacade(
        db=db,
        user_id=user_id,
    )
    reply = facade.complete(chat_id=chat_id, messages=messages_for_llm)

    return reply