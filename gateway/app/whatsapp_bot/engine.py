from sqlalchemy.orm import Session

from ..core.config import settings
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
    raw = (text or "").strip()
    if not raw:
        return "Empty message. Type 'help' to see available commands."

    norm = raw.lower()

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

    # 1) Create project: project new <name>
    if norm.startswith("project new "):
        name = raw[len("project new "):].strip()
        if not name:
            return "Please provide project name, e.g. 'new project My Docs'."
        p = Project(user_id = user, name = name)
        db.add(p)
        db.commit()
        db.refresh(p)
        _set_active_project(db, wa_user, p.id)
        return f"Project {name} created with id={p.id}."

    # 2) Delete project: project delete <id>
    if norm.startswith("project delete "):
        name_id = norm[len("project delete "):].strip()
        if not name_id.isdigit():
            return "Please provide numeric project id, e.g. 'project delete 1'."

        pid = int(name_id)
        p = _get_user_project_or_404(db, user, pid)
        now = datetime.utcnow()

        chats = db.query(Chat).filter(Chat.project_id == pid).all()
        for c in chats:
            if c.deleted_at is None:
                c.deleted_at = now
        db.delete(p)
        db.commit()

        if wa_user.active_project_id == pid:
            _set_active_project(db, wa_user, None)

        return f"Project {pid} deleted (its chats moved to trash)."

    # 3) Delete project hard: project delete hard <id>
    if norm.startswith("project delete hard "):
        name_id = norm[len("project delete hard "):].strip()
        if not name_id.isdigit():
            return "Please provide numeric project id, e.g. 'project delete hard 1'."

        pid = int(name_id)
        p = _get_user_project_or_404(db, user, pid)

        chats = db.query(Chat).filter(Chat.project_id == pid).all()
        for c in chats:
            db.delete(c)
        db.delete(p)
        db.commit()

        if wa_user.active_project_id == pid:
            _set_active_project(db, wa_user, None)

        return f"Project {pid} and all its chats were HARD-deleted."

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

    # 5) Create chat in project: chat new <project_id> <title>
    if norm.startswith("chat new "):
        parts = raw.split(maxsplit=3)
        if len(parts):
            return "Usage: chat new <project_id> <title>"
        _, _, project_id_str, title = parts
        if not project_id_str.isdigit():
            return "Project id must be a number."
        pid = int(project_id_str)

        _get_user_project_or_404(db, user, pid)

        c = Chat(
            project_id = pid,
            user_id = None,
            title=(title or "New chat").strip(),
            provider = "gemini",
            model = "gemini-1.5",
            settings_json = None,
            created_at = datetime.utcnow()
        )
        db.add(c)
        db.commit()
        db.refresh(c)

        _set_active_chat(db, wa_user, pid)
        _set_active_chat(db, wa_user, c.id)

        return f"Create {c.title} created in project {pid}"

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
        name = norm[len("chat open "):].strip()
        if not name.isdigit():
            return "Please provide numeric chat id, e.g. 'chat delete 1'."
        cid = int(name)
        chat = _get_user_chat_or_404(db, user, cid)
        if chat.deleted_at is not None:
            return f"Chat {cid} is already in trash."
        chat.deleted_at = datetime.utcnow()
        db.commit()
        return f"Chat {cid} moved to trash."

    # 8) Delete chat hard: chat delete hard <chat_id>
    if norm.startswith("chat delete hard "):
        rest = norm[len("chat delete hard "):].strip()
        if not rest.isdigit():
            return "Please provide numeric chat id, e.g. 'chat delete hard 1'."
        cid = int(rest)
        chat = _get_user_chat_or_404(db, user, cid)
        db.delete(chat)
        db.commit()

        if wa_user.active_chat_id == cid:
            _set_active_chat(db, wa_user, None)

        return f"Chat {cid} HARD-deleted."

    # 9) Chat open: chat open <chat_id>
    if norm.startswith("chat open "):
        name = norm[len("chat open "):].strip()
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
        _set_active_chat(db, wa_user, cid)
        lines = [f"Chat [{chat.id}] '{chat.title}':"]
        if not msgs:
            lines.append("(no messages yet)")
        else:
            for m in msgs:
                ts = m.created_at.strftime("%Y-%m-%d %H:%M")
                lines.append(f"[{ts}] {m.role}: {m.content}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # USE OF CHAT AND PROJECT
    # ------------------------------------------------------------------

    # 10) Use project: use project <id>
    if norm.startswith("use project "):
        name_id = norm[len("use project "):].strip()
        if not name_id.isdigit():
            return "Please provide numeric project id, e.g. 'use project 1'."
        pid = int(name_id)
        _get_user_project_or_404(db,user,pid)
        _set_active_project(db,wa_user, pid)
        return f"Active project set to {pid}."

    # 11) Use chat: use chat <id>
    if norm.startswith("use chat "):
        name = norm[len("use chat "):].strip()
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