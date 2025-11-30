from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint
from ..db.base import Base

class LlmApiCredential(Base):
    __tablename__ = "llm_api_credentials"
    __table_args__ = (UniqueConstraint("user_id", "provider", name="uq_llm_cred_user_provider"))

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, index = True, nullable= False)

    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    encrypted_api_key: Mapped[str] = mapped_column(String(2048), nullable=False)