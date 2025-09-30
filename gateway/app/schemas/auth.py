from pydantic import BaseModel, EmailStr

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