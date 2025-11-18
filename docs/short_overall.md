# 📁 Structure Overview
## Backend (FastAPI)
```gateway/
├─ app/
│  ├─ main.py               → app entry, mounts routers
│  ├─ api/
│  │  ├─ chat.py            → chat endpoints (CRUD, trash, completion)
│  │  ├─ project.py         → project endpoints (CRUD)
│  │  ├─ auth.py            → register/login/logout/me
│  │  └─ system.py          → health/version check
│  ├─ models/
│  │  ├─ user.py, project.py, chat.py, message.py
│  │  └─ __init__.py
│  ├─ db/
│  │  ├─ base.py            → Base = declarative_base()
│  │  ├─ session.py         → engine + SessionLocal
│  │  └─ init_pragma.py     → enable PRAGMA foreign_keys=ON (SQLite)
│  └─ services/             → gemini_adapter, auth_service, etc.
└─ ...
```

## Frontend (Nuxt 4 / Vue 3)
```frontend/
└─ app/
   ├─ components/
   │  ├─ AppSidebar.vue
   │  ├─ AppProjectTree.vue
   │  ├─ AppChat.vue
   │  ├─ AppComposer.vue
   │  └─ ui/                → shadcn-vue components
   ├─ pages/
   │  ├─ login.vue, register.vue
   │  └─ p/[pid]/c/[cid].vue → single chat view
   ├─ lib/
   │  ├─ api.ts             → generic API client (ofetch)
   │  ├─ chatApi.ts         → REST endpoints for chats/projects/messages
   │  └─ useAuth.ts         → auth composable
   └─ layouts/
      ├─ default.vue        → main layout (sidebar + chat)
      └─ auth.vue           → layout for login/register
```
# 🚀 Backend — API Reference
## 🔐 Auth Method	Path	Description
```
POST	/auth/register	Register user
POST	/auth/login	Login, set cookies
POST	/auth/logout	Logout
GET	/auth/me	Current user info
POST	/auth/refresh	Refresh tokens
```
## 📂 Projects
Method	Path	Description
```
GET	/projects	List all projects
POST	/projects	Create new project
DELETE	/projects/{id}/hard	Hard delete project (and all chats)
```
## 💬 Chats
Method	Path	Description
```
GET	/chats	List all chats (optionally filter by project/user)
POST	/chats	Create unassigned chat
GET	/projects/{pid}/chats	List chats in project
POST	/projects/{pid}/chats	Create chat under project
DELETE	/chats/{id}	Soft delete (move to trash)
DELETE	/chats/{id}/hard	Hard delete chat (remove messages)
POST	/chats/trash	Empty trash (remove all deleted chats & messages)
```
## 💭 Messages & Completion
```
Method	Path	Description
GET	/chats/{id}/messages	List messages for chat
POST	/chats/{id}/messages	Add user message
POST	/chats/{id}/completion	Generate assistant reply (Gemini/OpenAI)
```
## 🧠 Data Model
```
class User(Base):
    id, email, password_hash, full_name

class Project(Base):
    id, user_id (FK), name, created_at
    chats = relationship("Chat", cascade="all, delete-orphan")

class Chat(Base):
    __tablename__ = "chats"
    __table_args__ = {"sqlite_autoincrement": True}
    id, user_id (FK), project_id (FK), title, deleted_at
    messages = relationship("Message", cascade="all, delete-orphan", passive_deletes=True)

class Message(Base):
    id, chat_id (FK), role ('user'|'assistant'), content, created_at
```

🗑️ Soft delete: Chat.deleted_at != None

💥 Hard delete: physically remove record + cascade messages.

## 🎨 Frontend — UI Logic
Layout

- Sidebar → AppSidebar.vue:
contains AppProjectTree (projects/chats/trash)

- Main area → AppChat.vue:
displays conversation (scrollable)

- Composer → AppComposer.vue:
textarea, send button, suggestion prompts (optional popover)

## Component Responsibilities
Component	Responsibility

`AppProjectTree.vue`	Project list, chat list, trash; create/delete/hard delete

`AppChat.vue`	Render messages (user/assistant), auto-scroll

`AppComposer.vue`	Handle input, send user message, show suggestions

`pages/p/[pid]/c/[cid].vue`	Single chat page; loads messages for current chat id; watches cid changes

`lib/chatApi.ts`	Typed wrappers for backend API

`lib/api.ts`	Creates ofetch instance with auth cookies & runtimeConfig

## 🧩 Frontend → Backend Integration

All API calls go through ofetch client (createApi()).

Cookies are sent via credentials: "include".

Auth state stored in cookies (access, refresh).

On login, app redirects to /.

AppProjectTree calls loadAll() to reload:

projects

chats (nested)

trash (deleted chats)

## 🧾 Example Message Flow

- User sends message → POST /chats/{id}/messages

- Front pushes message to UI

- Then POST /chats/{id}/completion

- backend calls Gemini/OpenAI adapter

- generates assistant message

- saves to DB (Message(role='assistant', content=...))

- Chat updates in UI, scrolls to bottom

## 🧰 Developer Notes

- Hot reload: npm run dev (frontend), uvicorn app.main:app --reload (backend)

- CORS: enabled in FastAPI (setup_cors(app))

- DB migrations: Alembic or recreate for SQLite dev

- Hard delete safety: use /hard endpoints only when really needed

- Foreign keys: ensure PRAGMA foreign_keys=ON for SQLite in base/session.py