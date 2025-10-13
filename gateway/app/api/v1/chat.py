from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...models.chat import Project, Chat, Message
from ...schemas.chat import (
    ProjectIn, ProjectOut,
    ChatIn, ChatOut, ChatUpdate,
    MessageIn, MessageOut,
    CompletionIn, CompletionOut,
)
from ...services.llm_service import LLMService
from ...deps import current_user

llm = LLMService()

# ──────────────────────────────────────────────────────────────────────────────
# Вспомогательные проверки доступа
# ──────────────────────────────────────────────────────────────────────────────

def _get_user_project_or_404(db: Session, user, project_id: int) -> Project:
    p = (
        db.query(Project)
        .filter(Project.id == project_id, Project.user_id == user.id)
        .first()
    )
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return p

def _get_user_chat_or_404(db: Session, user, chat_id: int) -> Chat:
    """
    Разрешаем доступ, если:
      - чат в проекте, который принадлежит пользователю, ИЛИ
      - чат без проекта, но chat.user_id == user.id
    """
    chat = (
        db.query(Chat)
        .outerjoin(Project, Project.id == Chat.project_id)
        .filter(
            Chat.id == chat_id,
            (
                (Project.user_id == user.id)
                | ((Chat.project_id.is_(None)) & (Chat.user_id == user.id))
            ),
        )
        .first()
    )
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

# ──────────────────────────────────────────────────────────────────────────────
# Projects
# ──────────────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("", response_model=List[ProjectOut])
def list_projects(db: Session = Depends(get_db), user=Depends(current_user)):
    return (
        db.query(Project)
        .filter(Project.user_id == user.id)
        .order_by(Project.created_at.desc(), Project.id.desc())
        .all()
    )

@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(body: ProjectIn, db: Session = Depends(get_db), user=Depends(current_user)):
    p = Project(user_id=user.id, name=body.name.strip())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

@router.get("/{project_id}/chats", response_model=List[ChatOut])
def list_chats_in_project(
    project_id: int,
    include_deleted: bool = False,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    _get_user_project_or_404(db, user, project_id)
    q = db.query(Chat).filter(Chat.project_id == project_id)
    if not include_deleted:
        q = q.filter(Chat.deleted_at.is_(None))
    return q.order_by(Chat.created_at.desc(), Chat.id.desc()).all()

@router.post("/{project_id}/chats", response_model=ChatOut, status_code=status.HTTP_201_CREATED)
def create_chat_in_project(
    project_id: int,
    body: ChatIn,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    _get_user_project_or_404(db, user, project_id)
    c = Chat(
        project_id=project_id,
        user_id=None,  # владелец определяется проектом
        title=(body.title or "New chat").strip(),
        provider=body.provider or "gemini",
        model=body.model or "gemini-1.5-pro",
        settings_json=body.settings,
        created_at=datetime.utcnow(),
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    mode: str = Query(default="hard", pattern="^(hard|trash)$"),
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    """
    mode=hard  → жёсткое удаление проекта и всех его чатов (сообщения каскадом)
    mode=trash → пометить чаты deleted_at и удалить проект
    """
    _get_user_project_or_404(db, user, project_id)
    chats = db.query(Chat).filter(Chat.project_id == project_id).all()

    if mode == "trash":
        now = datetime.utcnow()
        for c in chats:
            if c.deleted_at is None:
                c.deleted_at = now
        # сам проект удаляем
        p = db.query(Project).filter(Project.id == project_id).first()
        db.delete(p)
        db.commit()
        return

    # hard
    for c in chats:
        db.delete(c)
    p = db.query(Project).filter(Project.id == project_id).first()
    db.delete(p)
    db.commit()
    return

# ──────────────────────────────────────────────────────────────────────────────
# Chats (глобальные)
# ──────────────────────────────────────────────────────────────────────────────

chats = APIRouter(prefix="/chats", tags=["chats"])

@chats.get("", response_model=List[ChatOut])
def list_chats(
    project_id: Optional[int] = Query(default=None),
    unassigned: bool = Query(default=False),
    include_deleted: bool = Query(default=False),
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    """
    GET /chats?unassigned=true                 → мои чаты без проекта
    GET /chats?project_id=123                  → чаты моего проекта 123
    GET /chats                                 → все мои чаты (и в проектах, и без), без удалённых
    """
    q = (
        db.query(Chat)
        .outerjoin(Project, Project.id == Chat.project_id)
        .filter(
            (Project.user_id == user.id) | ((Chat.project_id.is_(None)) & (Chat.user_id == user.id))
        )
    )

    if project_id is not None:
        # проверим, что проект мой
        _get_user_project_or_404(db, user, project_id)
        q = q.filter(Chat.project_id == project_id)

    if unassigned:
        q = q.filter(Chat.project_id.is_(None), Chat.user_id == user.id)

    if not include_deleted:
        q = q.filter(Chat.deleted_at.is_(None))

    return q.order_by(Chat.created_at.desc(), Chat.id.desc()).all()

@chats.post("", response_model=ChatOut, status_code=status.HTTP_201_CREATED)
def create_unassigned_chat(
    body: ChatIn,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    c = Chat(
        project_id=None,
        user_id=user.id,  # ВАЖНО: владелец unassigned-чата — текущий пользователь
        title=(body.title or "New chat").strip(),
        provider=body.provider or "gemini",
        model=body.model or "gemini-1.5-pro",
        settings_json=body.settings,
        created_at=datetime.utcnow(),
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

@chats.patch("/{chat_id}", response_model=ChatOut)
def update_chat(
    chat_id: int,
    body: ChatUpdate,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    chat = _get_user_chat_or_404(db, user, chat_id)

    # перенос между проектом и unassigned
    if body.project_id is not None:
        if body.project_id == 0 or body.project_id is None:
            # перенос в unassigned → чат становится личным
            chat.project_id = None
            chat.user_id = user.id
        else:
            # перенос в проект пользователя
            p = _get_user_project_or_404(db, user, body.project_id)
            chat.project_id = p.id
            chat.user_id = None  # в проекте владелец определяется проектом

    if body.title is not None:
        new_title = body.title.strip()
        if new_title:
            chat.title = new_title

    if body.settings is not None:
        chat.settings_json = body.settings

    db.commit()
    db.refresh(chat)
    return chat

@chats.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat_soft(
    chat_id: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    chat = _get_user_chat_or_404(db, user, chat_id)
    if chat.deleted_at is not None:
        return
    chat.deleted_at = datetime.utcnow()
    db.commit()
    return

@chats.delete("/{chat_id}/hard", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat_hard(
    chat_id: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    chat = _get_user_chat_or_404(db, user, chat_id)
    db.delete(chat)
    db.commit()
    return

@chats.get("/trash", response_model=List[ChatOut])
def list_deleted_chats(
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    q = (
        db.query(Chat)
        .outerjoin(Project, Project.id == Chat.project_id)
        .filter(
            Chat.deleted_at.is_not(None),
            (Project.user_id == user.id) | ((Chat.project_id.is_(None)) & (Chat.user_id == user.id)),
        )
    )
    return q.order_by(Chat.deleted_at.desc(), Chat.id.desc()).all()

@chats.post("/{chat_id}/restore", response_model=ChatOut)
def restore_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    chat = _get_user_chat_or_404(db, user, chat_id)
    chat.deleted_at = None
    db.commit()
    db.refresh(chat)
    return chat

# ──────────────────────────────────────────────────────────────────────────────
# Messages & Completion
# ──────────────────────────────────────────────────────────────────────────────

@chats.get("/{chat_id}/messages", response_model=List[MessageOut])
def list_messages(
    chat_id: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    _get_user_chat_or_404(db, user, chat_id)
    msgs = (
        db.query(Message)
        .filter(Message.chat_id == chat_id)
        .order_by(Message.created_at.asc(), Message.id.asc())
        .all()
    )
    return msgs

@chats.post("/{chat_id}/messages", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
def add_message(
    chat_id: int,
    body: MessageIn,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    _get_user_chat_or_404(db, user, chat_id)
    msg = Message(
        chat_id=chat_id,
        role=body.role,
        content=body.content,
        created_at=datetime.utcnow(),
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

@chats.post("/{chat_id}/completion", response_model=CompletionOut)
def completion(
    chat_id: int,
    body: CompletionIn,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    _get_user_chat_or_404(db, user, chat_id)

    # Заглушка: ответ строится на основе последнего user-сообщения
    text = llm.complete(
        [m.model_dump() for m in body.messages],
        model=body.model,
        settings=body.settings,
    )

    msg = Message(
        chat_id=chat_id,
        role="assistant",
        content=text,
        created_at=datetime.utcnow(),
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return {"message": msg}
