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

    # check if string starts with comand from list
    if not (
        norm in ("help", "/help")
        or norm.startswith("project ")
        or norm.startswith("chat ")
        or norm.startswith("use ")
    ):
        return None

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
    # ----------------- Project -----------------
    # project new <name>
    if norm.startswith("project new "):
        name = raw[len("project new "):].strip()
        if not name:
            return "Usage: project new <name>"

        p = Project(user_id = user.id, name = name)
        db.add(p)
        db.commit()
        db.refresh(p)

        _set_active_project(db, chanel_user, p.id)
        return f"Project {name} created with id = {p.id}"

    # project delete <id>
    if norm.startswith("project delete "):
        rest = norm[len("project delete "):].strip()
        if not rest.isdigit():
            return "Usage: project delete <id>"

        pid = int(rest)
        p = _get_user_project_or_404(db, user, pid)

        now = datetime.utcnow()
        chats = db.query(Chat).filter(Chat.project_id == pid).all()
        for c in chats:
            if getattr(c, "deleted_at", None) is None:
                c.deleted_at = now

        db.delete(p)
        db.commit()

        if getattr(chanel_user, "active_project_id", None) == pid:
            _set_active_project(db, chanel_user, None)

        return f"Project {pid} deleted (its chats moved to trash)"

    # project delete hard <id>
    if norm.startswith("project delete hard "):
        rest = norm[len("project delete hard "):].strip()
        if not rest.isdigit():
            return "Usage: project delete hard <id>"

        pid = int(rest)
        p = _get_user_project_or_404(db, user, pid)

        chats = db.query(Chat).filter(Chat.project_id == pid).all()
        for c in chats:
            db.delete(c)
        db.delete(p)
        db.commit()

        if getattr(chanel_user, "active_project_id", None) == pid:
            _set_active_project(db, chanel_user, None)

        return f"Project {pid} and all its chats were HARD-deleted"

    # project list
    if norm == ("project list"):
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

    # ----------------- Chat -----------------
    # chat new <project_id> <title>
    if norm.startswith("chat new "):
        parts = raw.split(maxsplit=3)
        if len(parts) != 4:
            return "Usage: chat new <project_id> <title>"

        _,_, pid, title = parts
        if not pid.isdigit():
            return "Project id must be a number."
        pid = int(pid)

        _get_user_project_or_404(db, user, pid)
        c = Chat(
            project_id=pid,
            user_id=chanel_user.user_id,
            title=(title or "New chat").strip(),
            settings_json=None,
            created_at=datetime.utcnow(),
        )
        db.add(c)
        db.commit()
        db.refresh(c)

        _set_active_project(db, chanel_user, pid)
        _set_active_chat(db, chanel_user, c.id)

        return f"Chat '{c.title}' created in project [{pid}] with id={c.id}"

    # chat move <chat_id> <project_id>
    if norm.startswith("chat move "):
        parts = norm.split()
        if len(parts) != 4:
            return "Usage: chat move <chat_id> <project_id>"
        _,_, cid_str, pid_str = parts
        if not cid_str.isdigit() or not pid_str.isdigit():
            return "chat_id and project_id must be numbers."

        cid = int(cid_str)
        pid = int(pid_str)

        chat = _get_user_chat_or_404(db, user, cid)
        project = _get_user_project_or_404(db, user, pid)

        chat.project_id = project.id
        db.commit()
        db.refresh(chat)

        # if getattr(chanel_user, "active_chat_id", None) == cid:
        #     _set_active_chat(db,chanel_user,project.id)

        return f"Chat {chat.id} moved to project {project.id}"

    # chat delete <chat_id>
    if norm.startswith("chat delete "):
        rest = norm[len("chat delete "):].strip()
        if not rest.isdigit():
            return "Usage: chat open <chat_id>"

        cid = int(rest)
        chat = _get_user_chat_or_404(db, user, cid)

        if getattr(chat, "deleted_at", None) is not None:
            return f"Chat {cid} is already in trash"

        chat.deleted_at = datetime.utcnow()
        db.commit()
        return f"Chat {cid} moved to trash."

    # chat delete hard <chat_id>
    if norm.startswith("chat delete hard "):
        rest = norm[len("chat delete hard "):].strip()
        if not rest.isdigit():
            return "Usage: chat delete hard <chat_id>"

        cid = int(rest)
        chat = _get_user_chat_or_404(db, user, cid)
        db.delete(chat)
        db.commit()

        if getattr(chanel_user, "active_chat_id", None) == cid:
            _set_active_chat(db, chanel_user, None)

        return f"Chat {cid} HARD-deleted."

    # chat open <chat_id>
    if norm.startswith("chat open "):
        rest = norm[len("chat open "):].strip()
        if not rest.isdigit():
            return "Usage: chat open <chat_id>"
        cid = int(rest)
        chat = _get_user_chat_or_404(db, user, cid)

        msgs = (
            db.query(Message)
            .filter(Message.chat_id == cid)
            .order_by(Message.created_at.asc(), Message.id.asc())
            .all()
        )
        _set_active_chat(db, chanel_user, cid)
        lines = [f"chat [{chat.id}] '{chat.title}':"]
        if not msgs:
            lines.append("(no messages yet)")
        else:
            for m in msgs:
                ts = m.created_at.strftime("%Y-%m-%d %H:%M")
                lines.append(f"[{ts}] {m.role}: {m.content}")
        return "\n".join(lines)

    # ----------------- Use -----------------
    # use project <project_id>
    if norm.startswith("use project "):
        rest = norm[len("use project "):].strip()
        if not rest.isdigit():
            return "Usage: use project <project_id>"

        pid = int(rest)
        _get_user_project_or_404(db, user, pid)
        _set_active_project(db, chanel_user, pid)
        _set_active_chat(db, chanel_user, None)
        return f"Active project set to {pid}"

    # use chat <chat_id>
    if norm.startswith("use chat "):
        rest = norm[len("use chat "):].strip()
        if not rest.isdigit():
            return "Usage: use chat <chat_id>"
        cid = int(rest)
        chat = _get_user_chat_or_404(db, user, cid)
        _set_active_chat(db, chanel_user, cid)
        if chat.project_id is not None:
            _set_active_project(db, chanel_user, chat.project_id)
        return f"Active chat set to {cid}"