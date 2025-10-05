from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..core.config import settings

is_sqlite = settings.DB_URL.startswith("sqlite")

#
engine = create_engine(
    settings.DB_URL,
    connect_args={"check_same_thread": False} if is_sqlite else {},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit = False)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()