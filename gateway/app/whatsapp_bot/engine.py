from sqlalchemy.orm import Session
from ..db.session import SessionLocal
from .client import WhatsAppClient
from ..services.whatsapp_user import get_or_create_whatsapp_user

from ..models.chat import  Project, Chat, Message
from ..api.v1.chat import _get_user_chat_or_404, _get_user_project_or_404

from types import SimpleNamespace
import datetime

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

def _ensure_linked_user(wa_user) -> SimpleNamespace:
    """
    Formating WhatsappUser into simple object with .id
    """
    if not wa_user.user_id:
        raise RuntimeError("WhatsApp user is not linked to an application user.")
    return SimpleNamespace(id = wa_user.user_id)

def _set_active_project(db: Session, wa_user, project_id: int | None) -> None:
    wa_user.active_project_id = project_id
    db.commit()
    db.refresh(wa_user)


def _set_active_chat(db: Session, wa_user, chat_id: int | None) -> None:
    wa_user.active_chat_id = chat_id
    db.commit()
    db.refresh(wa_user)


def router_user_message(wa_user, text: str, db: Session) -> str:
    """
    Base route. Just framework for now.
    Proces menu for user.
    """
    norm = text.strip().lower()

    try:
        user = _ensure_linked_user(wa_user)
    except RuntimeError:
        return (
            "Your WhatsApp number is not linked to any application user yet. "
            "Please link your account in the web interface."
        )

    # 1) Help
    if norm in ("help","/help"):
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

    # ------------------------------------------------------------------
    # PROJECTS
    # ------------------------------------------------------------------

    # 1) Create project
    if norm.startswith("project new "):
        name = text[len("project new "):].strip()
        if not name:
            return "Please provide project name, e.g. 'new project My Docs'."
        p = Project(user_id = user, name = name)
        db.add(p)
        db.commit()
        db.refresh(p)
        return f"Project {name} created with id={p.id}."

    # 2) Delete project
    if norm.startswith("project delete "):
        name = text[len("project delete "):].strip()
        if not name:
            return "Please provide project id"

        # TODO: call service
        return f"Project {name}"

    # 4) List
    if norm == "project list":
        projects = (
            db.query(Project)
            .filter(Project.user_id == user.id)
            .order_by(Project.created_at.desc(), Project.id.desc())
            .all()
        )
        if not projects:
            return "You have no projects yet."
        lines = ["Your projects:"]
        for p in projects:
            lines.append(f"- [{p.id}] {p.name}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # CHATS
    # ------------------------------------------------------------------

    # 5) Create chat in project <project_id> <title>
    if norm.startswith("chat new "):

        # TODO call service
        return f"Create chat"

    # 6) Move chat <chat_id> <project_id>
    if norm.startswith("chat move "):
        parts = norm.split()
        if len(parts) != 4:
            return "Usage: chat move <chat_id> < project_id>"
        _, _, chat_id_str, project_id_str = parts
        if not chat_id_str.isdigit() or not project_id_str.isdigit():
            return "chat_if and project_if must be numbers."
        chat_id = int(chat_id_str)
        project_id = int(project_id_str)

        chat = _get_user_chat_or_404(db, user, chat_id)
        project = _get_user_project_or_404(db, user, project_id)

        chat.project_id = project_id
        db.commit()
        db.refresh(chat)

        if wa_user.active_chat_id == chat_id:
            _set_active_project(db, wa_user, project.id)

        return f"Chat {chat.id} moved to project {project.id}."


    # 7) Delete chat: chat delete <chat_id>
    if norm.startswith("chat delete "):
        name = text[len("chat open "):].strip()
        if not name.isdigit():
            return "Please provide numeric chat id, e.g. 'chat delete 1'."
        cid = int(name)
        chat = _get_user_chat_or_404(db, user, cid)
        if chat.deleted_at is not None:
            return f"Chat {cid} is already in trash."
        chat.deleted_at = datetime.utcnow()
        db.commit()
        return f"Chat {cid} moved to trash."

    # 8) Chat open: chat open <chat_id>
    if norm.startswith("chat open "):
        name = text[len("chat open "):].strip()
        if not name.isdigit():
            return "Please provide numeric chat id, e.g. 'chat open 1'."
        cid = int(name)
        chat = _get_user_chat_or_404(db, user, cid)

        msgs = (
            db.query(Message)
            .filter(Message.chat_id == cid)
            .order_by(Message.created_at.desc(), Message.id.desc())
            .all()
        )
        msgs = list(reversed(msgs))
        lines = [f"Chat [{chat.id}] '{chat.title}':"]
        if not msgs:
            lines.append("(no messages yet)")
        else:
            for m in msgs:
                ts = m.created_at.strftime("%Y-%m-%d %H:%M")
                lines.append(f"[{ts}] {m.role}: {m.content}")
        return "\n".join(lines)

    # 9) Use project: use project <id>
    if norm.startswith("use project "):
        name = text[len("use project "):].strip()
        # TODO call service
        return f"Use project"

    # 10) Use chat: use chat <id>
    if norm.startswith("use chat "):
        name = text[len("use chat "):].strip()
        if not name.isdigit():
            return "Please provide numeric chat id, e.g. 'use chat 1'."
        cid = int(name)
        _get_user_chat_or_404(db, user, cid)
        _set_active_chat(db,wa_user, cid)
        return f"Active chat set to {cid}."

    return (
        "Unknown command. Type 'help' to see available commands.\n\n"
        f"You said: {text}"
    )