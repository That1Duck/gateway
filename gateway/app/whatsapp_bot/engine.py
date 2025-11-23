from .client import WhatsAppClient

client = WhatsAppClient()

def handle_incoming_text(from_number: str, text: str) -> None:
    """
    The framework of the function so far
    :param from_number:
    :param text:
    """
    reply = f"You said: {text}"
    client.send_text(to=from_number, body= reply)