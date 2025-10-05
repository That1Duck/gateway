from pydantic import BaseModel, EmailStr, field_validator

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None
    role: str

class LoginResponse(BaseModel):
    ok: bool

class MeResponse(UserOut):
    pass

class RefreshResponse(BaseModel):
    ok: bool

class LogoutResponse(BaseModel):
    ok: bool

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None

    @field_validator("password")
    @classmethod
    def password_len(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

def to_user_out(u) -> "UserOut":
    return UserOut(id=u.id, email=u.email, full_name=u.full_name, role = u.role)