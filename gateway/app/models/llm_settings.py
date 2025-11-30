from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, Float, ForeignKey, UniqueConstraint
from ..db.base import Base

class LlmSettings(Base):
    __tablename__ = "llm_settings"
    __table_args__ = (UniqueConstraint("user_id", name = "uq_llm_settings_user"))

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)

    default_provider: Mapped[str] = mapped_column(String(32), default="gemeni")
    default_model: Mapped[str] = mapped_column(String(128), default="")
    temperature: Mapped[float] = mapped_column(Float, default=0)
    max_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)

    use_streaming: Mapped[bool] = mapped_column(Boolean, default=True)
    use_rag_by_default: Mapped[bool] = mapped_column(Boolean, default=False)
    log_prompts: Mapped[bool] = mapped_column(Boolean, default=False)

    timeout_seconds: Mapped[int] = mapped_column(Integer, default=30)