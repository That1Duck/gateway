from fastapi import HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..core.security import (
    verify_password, create_access_token, create_refresh_token,
    set_auth_cookies, clear_auth_cookies, decode_token, hash_password
)
from ..models.user import User

class AuthService:
    def register(self, db: Session, email:str, password:str, full_name: str | None) -> User:
        existing = db.scalar(select(User).where(User.email == email.lower()))
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="Email already registered")

        user = User(
            email = email.lower(),
            password_hash=hash_password(password),
            full_name=full_name,
            role = "user",
            is_active = True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def login(self, db: Session, email:str, password: str, response: Response) -> None:
        user = db.scalar(select(User).where(User.email == email.lower()))
        if not user or not verify_password(password, user.password_hash) or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid credentials")
        access = create_access_token(str(user.id))
        refresh = create_refresh_token(str(user.id))
        set_auth_cookies(response, access = access, refresh=refresh)


    def me(self, user: User) -> dict:
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }

    def logout(self, response: Response) -> None:
        clear_auth_cookies(response)

    def refresh(self, db:Session ,refresh_cookie: str | None, response: Response) -> None:
        if not refresh_cookie:
            raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,
                                detail="Missing refresh token")
        try:
            payload = decode_token(refresh_cookie)
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail="Invalid token type")
            user_id = int(payload.get("sub"))
            user = db.get(User, user_id)
            if not user or not user.is_active:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail="User not found")
            new_access = create_access_token(str(user.id))
            set_auth_cookies(response, access=new_access)
        except Exception:
            raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid or expired refresh")