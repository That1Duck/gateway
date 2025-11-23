from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import PlainTextResponse
import logging

from .config import META_WHATSAPP_VERIFY_TOKEN
from .engine import handle_incoming_text

log = logging.getLogger(__name__)
router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])

@router.get("/webhook")
async def verify_webhook(
        hub_mode: str | None = None,
        hub_verify_token: str | None = None,
        hub_challenge: str | None = None,
):
    """
    Verification endpoint for Meta WhatsApp Webhook.
    Meta sends GET with hub.mode, hub.verify_token, hub.challenge.
    """
    if hub_mode == "subscribe" and hub_verify_token == META_WHATSAPP_VERIFY_TOKEN:
        return PlainTextResponse(content=hub_challenge or "")
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/webhook")
async def receive_webhook(request: Request):
    """
    Main webhook endpoint for incoming WhatsApp messages
    """
    body = await request.json()

    entry_list = body.get("entry",[])
    for entry in entry_list:
        changes = entry.get("changes", [])
        for change in changes:
            value = change.get("value", [])
            messages = value.get("messages", [])
            for message in messages:
                msg_type = message.get("type")
                from_number = message.get("from")
                if msg_type == "text":
                    text = message.get("text",{}).get("body", {})
                    if text and from_number:
                        handle_incoming_text(from_number, text)
                    else:
                        log.info("Ignoring non-text message type: %s", msg_type)

    return {}