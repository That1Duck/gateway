from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import jwt
from passlib.context import CryptContext
from fastapi import Response

from .config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto") # bcrypt_sha256 | argon2

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)

def _create_token(sub:str, ttl: timedelta, token_type: str) -> str:
    now = datetime.now(timezone.utc)
    payload: Dict[str, Any] = {
        "sub": sub,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + ttl).timestamp())
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm= settings.JWT_ALG)

def create_access_token(sub:str) -> str:
    return _create_token(sub, timedelta(minutes = settings.ACCESS_TOKEN_TTL_MIN), "access")

def create_refresh_token(sub:str) -> str:
    return _create_token(sub, timedelta(days = settings.REFRESH_TOKEN_TTL_DAYS), "refresh")

def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])

# Cookies helpers
def set_auth_cookies(response: Response, access:str, refresh: Optional[str] = None) -> None:
    def _set(cookie_name:str, value:str, max_age:int):
        kwargs = dict(
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=max_age,
            path="/"
        )
        if settings.COOKIE_DOMAIN:
            kwargs["domain"] = settings.COOKIE_DOMAIN
        response.set_cookie(key = cookie_name, value=value, **kwargs)

        print("DEBUG Set-Cookie header now:",
              response.headers.get("set-cookie"))

    _set(settings.ACCESS_COOKIE_NAME, access, settings.ACCESS_TOKEN_TTL_MIN * 60)
    if refresh:
        _set(settings.REFRESH_COOKIE_NAME, refresh, settings.REFRESH_TOKEN_TTL_DAYS * 24 *3600)

def clear_auth_cookies(response: Response) -> None:
    kwargs = dict(path = "/")
    if settings.COOKIE_DOMAIN:
        kwargs["domain"] = settings.COOKIE_DOMAIN
    response.delete_cookie(key = settings.ACCESS_COOKIE_NAME, **kwargs)
    response.delete_cookie(key = settings.REFRESH_COOKIE_NAME, **kwargs)


"""
def set_auth_cookies(response: Response, access:str, refresh: Optional[str] = None) -> None:
    response.set_cookie(
        key = settings.ACCESS_COOKIE_NAME,
        value= access,
        httponly= True,
        secure= settings.COOKIE_SECURE,
        samesite= settings.COOKIE_SAMESITE,
        domain= settings.COOKIE_DOMAIN,
        max_age= settings.ACCESS_TOKEN_TTL_MIN * 60,
        path= "/"
    )
    if refresh:
        response.set_cookie(
            key=settings.REFRESH_COOKIE_NAME,
            value=refresh,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            domain=settings.COOKIE_DOMAIN,
            max_age=settings.REFRESH_TOKEN_TTL_DAYS * 24 * 3600,
            path="/"
        )

def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(
        key = settings.ACCESS_COOKIE_NAME,
        domain = settings.COOKIE_DOMAIN,
        path = "/"
    )
"""