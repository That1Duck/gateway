from sqlalchemy.orm import Session
from ..db.session import SessionLocal
from .client import WhatsAppClient
from ..services.whatsapp_user import get_or_create_whatsapp_user

client = WhatsAppClient()

def handle_incoming_text(from_number: str, text: str) -> None:
    """
    Function open db session, search for user by phone number.
    Calls router for menu messages.
    Sends text to user.
    Close db session.
    """
    db: Session = SessionLocal()
    try:
        wa_user = get_or_create_whatsapp_user(db, phone=from_number)
        reply = router_user_message(wa_user, text, db)
        if reply:
            client.send_text(to=from_number, body=reply)
    finally:
        db.close()

def router_user_message(wa_user, text: str, db: Session) -> str:
    """
    Base route. Just framework for now.
    Proces menu for user:
    - create new project <name>
    - show list project

    # TODO create more menu options and
    """
    norm = text.strip().lower()

    if norm in ("help","/help"):
        return (
            "Available comands:\n"
            "- new project <name>\n"
            "- list project\n"
            "- new chat <title>\n"
            "- ..."
        )

    if norm.startswith("new project "):
        name = text[len("new project "):].strip()
        if not name:
            return "Please provide project name, e.g. 'new project My Docs'."

        # TODO: call service
        return f"Project {name}"

    if norm == "list projects":
        # TODO call service
        return "Here will be a list of your projects"

    return "Try again"