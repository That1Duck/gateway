import os
from .config import Settings
from cryptography.fernet import Fernet, InvalidToken

class EncryptionError(Exception):
    """Generic encryption/decryption error."""

def _get_fernet() -> Fernet:
    settings = Settings()
    key = settings.LLM_SETTINGS_SECRET_KEY
    if not key:
        raise EncryptionError("LLM_SETTINGS_SECRET_KEY is not set in environment.")
    try:
        return Fernet(key.encode() if isinstance(key, str) else key)
    except Exception as exc:
        raise EncryptionError("Invalid LLM_SETTINGS_SECRET_KEY format.") from exc

def encrypt_api_key(plain:str) -> str:
    """
    Encrypt API key (or any sensitive string) using Fernet.
    Returns base64-encoded ciphertext suitable for storing in DB.
    """
    if plain is None:
        raise EncryptionError("Cannot encrypt None as API key.")
    fernet = _get_fernet()
    token = fernet.encrypt(plain.encode("utf-8"))
    return token.decode("ascii")

def decrypt_api_key(ciphertext:str) -> str:
    """
    Decrypt previously encrypted API key.
    """
    if not ciphertext:
        raise EncryptionError("Empty ciphertext")
    f = _get_fernet()
    try:
        plain_bytes = f.decrypt(ciphertext.encode("ascii"))
    except InvalidToken as exc:
        raise EncryptionError("Invalid ciphertext or wrong secret key.") from exc
    return plain_bytes.decode("utf-8")