from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint
from ..db.base import Base

class WhatsappUser(Base):
    __tablename__ = "whatsapp_user"
    __table_args__ = (
        UniqueConstraint("phone", name = "uq_whatsapp_user_phone")
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement= True)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable= True, index=True)
    phone: Mapped[str] = mapped_column(String(32), nullable= False, index=True)