# Gateway (FastAPI)

Цей репозиторій містить **gateway-сервіс** на базі FastAPI, який виступає фасадом між фронтендом (Nuxt/Supastarter) та основним бізнес-сервісом.  
Основна ідея: **фронт спілкується лише з gateway через стабільний REST API**, а gateway всередині викликає адаптери до зовнішніх сервісів.

---

## Логіка роботи

1. **Фронт** надсилає HTTP-запит → наприклад `POST /api/v1/auth/login`.
2. **Gateway (FastAPI)** приймає запит, проходить через middleware:
   - додається `X-Request-ID` (унікальний ID запиту для логів і трасування),
   - перевіряються CORS (чи дозволено цей Origin).
3. Запит передається у **роутер** (`api/v1/...`), де:
   - перевіряється автентифікація (якщо треба),
   - дані валідовуються через Pydantic-схеми,
   - викликається **сервісний шар** (business logic).
4. Сервісний шар звертається до **адаптера**:
   - адаптер інкапсулює конкретний протокол до зовнішнього сервісу (HTTP, gRPC, CLI, DB),
   - зараз є тільки MOCK (OpenAI/echo).
5. Відповідь від адаптера приводиться до Pydantic-схеми й віддається назад клієнту.
6. Усі помилки повертаються в єдиному форматі:
   ```json
   {
     "error": {
       "code": "401",
       "message": "Missing access token",
       "ctx": null
     },
     "request_id": "uuid"
   }

## Структура проєкту

```
gateway/
├─ app/
│  ├─ main.py             # Точка входу, FastAPI app, middleware, handlers
│  ├─ core/               # Конфіг, безпека, cors, логування
│  │  ├─ config.py        # Завантаження .env, глобальні налаштування
│  │  ├─ security.py      # JWT, паролі, робота з куками
│  │  ├─ cors.py          # CORS (налаштування доступу з фронта)
│  │  └─ logging.py       # Налаштування логів через loguru
│  ├─ middlewares/
│  │  └─ request_id.py    # Додає X-Request-ID до кожного запиту/відповіді
│  ├─ schemas/            # Pydantic-схеми (контракти API)
│  │  ├─ common.py        # Health, помилки
│  │  └─ auth.py          # Схеми для аутентифікації
│  ├─ models/
│  │  └─ user.py          # In-memory користувач (мок)
│  ├─ services/
│  │  └─ auth_service.py  # Логіка auth (login, refresh, logout)
│  ├─ adapters/
│  │  └─ base.py          # Базовий інтерфейс адаптера (для майбутнього сервісу)
│  ├─ api/v1/
│  │  ├─ system.py        # /system/health, /system/version
│  │  ├─ auth.py          # /auth/login, /auth/me, /auth/refresh, /auth/logout
│  │  └─ routes.py        # Головний роутер API v1
│  └─ deps.py             # Depends (отримання request_id, current_user)
├─ requirements.txt       # Python-залежності
├─ .env.example           # Приклад конфігів для запуску
└─ README.md              # Цей файл

````

## Реалізовані ендпоінти

Системні:
- `GET /health` — перевірка, що застосунок живий.
- `GET /api/v1/system/health`
- `GET /api/v1/system/version`

Аутентифікація (JWT у httpOnly-куках):
- `POST /api/v1/auth/login` → встановлює `access_token` і `refresh_token` у куках.
- `GET /api/v1/auth/me` → повертає профіль користувача (потрібен `access_token`).
- `POST /api/v1/auth/refresh` → видає новий `access_token` (потрібен `refresh_token`).
- `POST /api/v1/auth/logout` → видаляє обидві куки.

## Використані інструменти
- FastAPI — веб-фреймворк для REST API.
- Uvicorn — ASGI-сервер для запуску.
- Pydantic v2 — валідація даних і робота з .env.
- python-jose — створення й перевірка JWT.
- passlib[argon2] — хешування паролів (argon2).
- loguru — зручні логи.

