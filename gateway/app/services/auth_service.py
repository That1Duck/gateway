from fastapi import HTTPException, status, Response
from ..core.security import (
    verify_password, create_access_token, create_refresh_token,
    set_auth_cookies, clear_auth_cookies, decode_token
)
from ..models.user import get_user_by_email, get_user_by_id

class AuthService:
    def login(self, email:str, password: str, response: Response) -> None:
        user = get_user_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid credentials")
        access = create_access_token(str(user.id))
        refresh = create_refresh_token(str(user.id))
        set_auth_cookies(response, access = access, refresh=refresh)


    def me(self, user) -> dict:
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }

    def logout(self, response: Response) -> None:
        clear_auth_cookies(response)

    def refresh(self, refresh_cookie: str | None, response: Response) -> None:
        if not refresh_cookie:
            raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,
                                detail="Missing refresh token")
        try:
            payload = decode_token(refresh_cookie)
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail="Invalid token type")
            user = get_user_by_id(int(payload.get("sub")))
            if not user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail="User not found")
            new_access = create_access_token(str(user.id))
            set_auth_cookies(response, access=new_access)
        except Exception:
            raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid or expired refresh")