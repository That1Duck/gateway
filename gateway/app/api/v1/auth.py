from fastapi import APIRouter, Response, Request, Depends
from fastapi import status
from ...schemas.auth import (
    LoginRequest, LoginResponse, MeResponse, RefreshResponse, LogoutResponse
)
from ...services.auth_service import AuthService
from ...deps import current_user
from ...core.config import settings

router = APIRouter(prefix='/auth', tags=["auth"])
svc = AuthService()

@router.post("/login", response_model= LoginResponse)
def login(body: LoginRequest, response: Response):
    svc.login(body.email, body.password, response)
    return LoginResponse(ok = True)

@router.get("/me", response_model=MeResponse)
def me(user = Depends(current_user)):
    return MeResponse(**svc.me(user))

@router.post("/refresh", response_model=RefreshResponse)
def refresh(request: Request, response: Response):
    refresh_cookie = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    svc.refresh(refresh_cookie, response)
    return RefreshResponse(ok = True)

@router.post("/logout", response_model=LogoutResponse)
def logout(response: Response):
    svc.logout(response)
    return LogoutResponse(ok = True)