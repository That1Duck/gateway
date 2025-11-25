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

    # 1) Help
    if norm in ("help","/help"):
        return (
            "Available comands:\n"
            "- project new <name>\n"
            "- project delete <id>\n"
            "- project list\n"
            "- chat new <project_id> <title>\n"
            "- chat move <chat_id> <project_id>\n"
            "- chat delete <chat_id>\n"
            "- chat open <chat_id>\n"
            "- use project <project_id>\n"
            "- use chat <chat_id>\n"
        )

    # 2) Create project
    if norm.startswith("project new "):
        name = text[len("project new "):].strip()
        if not name:
            return "Please provide project name, e.g. 'new project My Docs'."

        # TODO: call service
        return f"Project {name}"

    # 3) Delete project
    if norm.startswith("project delete "):
        name = text[len("project delete "):].strip()
        if not name:
            return "Please provide project id"

        # TODO: call service
        return f"Project {name}"

    # 4) List
    if norm == "project list":
        # TODO call service
        return "Here will be a list of your projects"

    # 5) Create chat in project <project_id> <title>
    if norm.startswith("chat new "):

        # TODO call service
        return f"Create chat"

    # 6) Move chat
    if norm.startswith("chat move "):
        # TODO call service
        return f"Move chat"

    # 7) Delete chat: chat delete <chat_id>
    if norm.startswith("chat delete "):
        name = text[len("chat open "):].strip()
        # TODO call service
        return f"Delete chat"

    # 8) Chat open: chat open <chat_id>
    if norm.startswith("chat open "):
        name = text[len("chat open "):].strip()
        # TODO call service
        return f"Chat open"

    # 9) Use project: use project <id>
    if norm.startswith("use project "):
        name = text[len("use project "):].strip()
        # TODO call service
        return f"Use project"

    # 10) Use chat: use chat <id>
    if norm.startswith("use chat "):
        name = text[len("use chat "):].strip()
        # TODO call service
        return f"Use chat"

    return "Try again"