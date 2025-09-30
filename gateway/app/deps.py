from fastapi import Request, HTTPException, status, Depends
from jose import JWTError

from .core.config import settings
from .core.security import decode_token
from .models.user import get_user_by_id

def get_request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)

def current_user(request: Request):
    token = request.cookies.get(settings.ACCESS_COOKIE_NAME)

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail= "Missing access token")
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail= "Invalid token type")
        sub = payload.get("sub")
        user = get_user_by_id(int(sub))
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid or expired token")