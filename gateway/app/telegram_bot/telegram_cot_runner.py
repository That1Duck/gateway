import os
import re
import asyncio
import httpx

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message

from ..core.config import settings

bot = Bot(settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

BACKEND_BASE_URL = os.environ.get("BACKEND_BASE_URL", "http://127.0.0.1:8000")
API_PREFIX = os.environ.get("API_PREFIX", "/api/v1")
LINK_RE = re.compile(r"^/link(?:@\w+)?\s+(\S+)\s*$", re.IGNORECASE)

def build_url(path: str) -> str:
    base = BACKEND_BASE_URL.rstrip("/")
    prefix = API_PREFIX.strip("/")
    p = path.lstrip("/")
    return f"{base}/{prefix}/{p}"

async def post_json(path: str, payload: dict) -> dict:
    url = build_url(path)
    print("POST:", url, "payload=", payload)

    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(url, json=payload)

        if r.status_code >= 400:
            raise RuntimeError(f"{r.status_code}: {r.text}")

        return r.json()

@dp.message(F.text.regexp(LINK_RE))
async def link_handler(message: Message):
    code = LINK_RE.match(message.text.strip()).group(1)
    tg = message.from_user

    try:
        data = await post_json(
            "integrations/telegram/link",
            {
                "telegram_id": tg.id,
                "code": code,
                "user_name": tg.username,
                "first_name": tg.first_name,
                "last_name": tg.last_name,
                "language_code": tg.language_code,
            },
        )
        await message.answer("Linked to user")
    except Exception as e:
        await message.answer(f"Link failed: {e}")

@dp.message(F.text)
async def text_handler(message: Message):
    tg = message.from_user
    text = message.text.strip()
    if text.lower().startswith("/link"):
        return

    try:
        data = await post_json(
            "integrations/telegram/message",
            {"telegram_id": tg.id, "text": text},
        )
        await message.answer(data["reply"])
    except Exception as e:
        await message.answer(f" Error: {e}")

async def main():
    print("Backend:", BACKEND_BASE_URL)
    print("API prefix:", API_PREFIX)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())