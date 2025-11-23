import logging
import httpx

from .config import (
    META_WHATSAPP_ACCESS_TOKEN,
    META_WHATSAPP_PHONE_NUMBER_ID,
    META_WHATSAPP_BASE_URL,
)

log = logging.getLogger(__name__)

class WhatsAppClient:
    def __init__(self):
        self.base_url = META_WHATSAPP_BASE_URL
        self.phone_number_id = META_WHATSAPP_PHONE_NUMBER_ID
        self.access_token = META_WHATSAPP_ACCESS_TOKEN

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearner {self.access_token}",
            "Content-Type": "application/json"
        }

    def send_text(self, to: str, body: str) -> None:
        """
        Send text message to a WhatsApp user.

        :param to: WhatsApp phone number
        :param body: Text message body
        """
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        payload = {
            "messaging_product":"whatsapp",
            "to":to,
            "type":"text",
            "text": {"body": body},
        }
        #log.info("Send message to %s: %s", to, body)
        resp = httpx.post(url,
                          headers=self._headers(),
                          json=payload,
                          timeout=10.0)
        if resp.status_code >= 400:
            #log.error("WhatsApp send_text failed: %s %s", resp.status_code, resp.text)
            resp.raise_for_status()