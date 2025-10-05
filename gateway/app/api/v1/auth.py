from fastapi import APIRouter, Response, Request, Depends, status
from sqlalchemy.orm import Session

from ...schemas.auth import (
    LoginRequest, LoginResponse, MeResponse, RefreshResponse, LogoutResponse, RegisterRequest, to_user_out
)
from ...services.auth_service import AuthService
from ...deps import current_user
from ...db.session import get_db
from ...core.config import settings

router = APIRouter(prefix='/auth', tags=["auth"])
svc = AuthService()

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    user = svc.register(db, email=body.email, password=body.password, full_name= body.full_name)
    return to_user_out(user)

@router.post("/login", response_model= LoginResponse)
def login(body: LoginRequest, response: Response, db: Session = Depends(get_db)):
    svc.login(db, body.email, body.password, response)
    return LoginResponse(ok = True)

@router.get("/me", response_model=MeResponse)
def me(user = Depends(current_user)):
    return MeResponse(**svc.me(user))

@router.post("/refresh", response_model=RefreshResponse)
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_cookie = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    svc.refresh(db, refresh_cookie, response)
    return RefreshResponse(ok = True)

@router.post("/logout", response_model=LogoutResponse)
def logout(response: Response):
    svc.logout(response)
    return LogoutResponse(ok = True)