from sqlalchemy.orm import Session
from ..models.whatsapp_user import WhatsappUser

def get_or_create_whatsapp_user(db: Session, phone: str) -> WhatsappUser:
    """
    Search for user in WhatsApp by phone number.
    If user not found, create user and return him.
    :return: User from db
    """
    user = db.query(WhatsappUser).filter(WhatsappUser.phone == phone).first()
    if user:
        return user
    user = WhatsappUser(phone = phone, user_id = None)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user