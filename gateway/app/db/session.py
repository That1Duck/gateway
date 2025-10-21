from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from ..core.config import settings

is_sqlite = settings.DB_URL.startswith("sqlite")

#
engine = create_engine(
    settings.DB_URL,
    connect_args={"check_same_thread": False} if is_sqlite else {},
)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    # включаем FK только для SQLite; для Postgres/MySQL этот PRAGMA игнорируется
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    except Exception:
        pass

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit = False)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()