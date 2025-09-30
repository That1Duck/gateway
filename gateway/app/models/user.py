from dataclasses import dataclass
from typing import Optional
from ..core.security import hash_password

@dataclass
class User:
    id: int
    email: str
    password_hash: str
    full_name: Optional[str] = None
    role: str = "user"

DEMO_USER = User(
    id = 1,
    email= "demo@example.com",
    password_hash=hash_password("demo12345"),
    full_name="Demo User",
    role = "user"
)

def get_user_by_email(email: str) -> Optional[User]:
    if email.lower() == DEMO_USER.email.lower():
        return DEMO_USER
    return None

def get_user_by_id(uid: int) -> Optional[User]:
    if uid == DEMO_USER.id:
        return DEMO_USER
    return None