from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...models.telegram_account import TelegramAccount
from ...schemas.telegram_bot import TelegramMessageRequest, TelegramMessageResponse

from ...services.chat_cli_router import router_user_message
from ...services.chat_text_pipeline import handle_plain_text

router = APIRouter(prefix="/integrations/telegram", tags=["telegram-bot"])


@router.post("/message", response_model=TelegramMessageResponse)
def telegram_message(payload: TelegramMessageRequest, db: Session = Depends(get_db)):
    acc = (
        db.query(TelegramAccount)
        .filter(TelegramAccount.telegram_id == payload.telegram_id)
        .first()
    )
    if not acc:
        #raise HTTPException(status_code=404, detail="Telegram account not found. Use /link first.")
        return TelegramMessageResponse(
            reply="Telegram account not found. Please link first: /link <code> (get code on website)."
        )


    if not acc.user_id:
        return TelegramMessageResponse(
            reply="Your Telegram is not linked yet. Please use /link <code> (get code on website)."
        )

    cmd_reply = router_user_message(acc, payload.text, db)
    if cmd_reply is not None:
        return TelegramMessageResponse(reply=cmd_reply)

    reply = handle_plain_text(
        db,
        user_id=acc.user_id,
        chat_id=getattr(acc, "active_chat_id", None),
        text=payload.text,
    )
    return TelegramMessageResponse(reply=reply)