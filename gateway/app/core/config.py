from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Centralized settings via .env
    - Name of the app
    - Version
    - CORS origins
    - Header for request_id
    """
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENV: str = "dev"
    APP_NAME: str = "Gateway"
    APP_VERSION: str = "0.1.0"

    # список origin-ів у .env задається через кому
    CORS_ORIGINS: str = "http://localhost:3000"
    REQUEST_ID_HEADER: str = "X-Request-ID"

    # JWT / Cookies
    JWT_SECRET: str = "change_me_please"
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_TTL_MIN: int = 15
    REFRESH_TOKEN_TTL_DAYS: int = 14

    COOKIE_DOMAIN: str = "localhost"
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"  # "lax" | "strict" | "none"
    ACCESS_COOKIE_NAME: str = "access_token"
    REFRESH_COOKIE_NAME: str = "refresh_token"

    DB_URL: str =  "sqlite:///./data/app.db"

    GOOGLE_API_KEY: Optional[str] = None

    @property
    def cors_origins_list(self) -> List[str]:
        """Return list of origins from the list .env"""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

settings = Settings()