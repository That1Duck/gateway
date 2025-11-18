# Shot instruction how to start without Docker

This short instruction describe operation of start from IDE

# Launching a project without Docker

Below are complete and clear instructions on how to run the backend + queue (Dramatiq) + Redis without Docker.
---

# 1. Setting dependencies

We create a virtual environment and install all libraries.

```bash
python -m venv .venv
# Windows PowerShell:
. .venv/Scripts/Activate.ps1

pip install --upgrade pip
pip install -r requirements.txt
```
---

# 2. Setting environment variables

`.env` file in the backend root:

```
DATABASE_URL=sqlite:///./dev.db
UPLOAD_DIR=./data/uploads

# Очередь
QUEUE_MODE=dramatiq
REDIS_URL=redis://localhost:6379/0
```

---

# 3. Installing and starting Redis (Windows)

You have two options:

## Option A — Redis in WSL (recommended)

```bash
wsl
sudo apt update
sudo apt install -y redis-server
sudo service redis-server start
redis-cli ping   # должно ответить PONG
```

Redis is now available on `localhost:6379` for Windows.

---

## Option B — Redis via Docker (if Docker Desktop is installed)

```bash
docker run -d --name redis -p 6379:6379 redis:7
```

Verification:

```bash
redis-cli -h localhost ping
```

---

# 4. Launching the backend API

From the directory where the `app/` package is located:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```
http://localhost:8000
```

OpenAPI documentation:

```
http://localhost:8000/docs
```

---

# 5. Launching the Dramatiq worker

In a separate terminal window, **in the same folder** where `app/` is located:

```bash
python -m dramatiq app.worker.tasks
```

Ensure that:

* there is a directory `app/worker/`
* there is a file `app/worker/tasks.py`
* RedisBroker is configured in it
* actor `parse_document_async` is declared inside it

The correct worker response looks like this:

```
Dramatiq '1.x.x' is booting up.
... Waiting for messages.
```


# 6. Process structure at startup

```
[ background process ]          [ queue ]             [ worker ]
uvicorn  ---------------->  Redis  <--------------  python -m dramatiq
(API accepts requests)      (stores tasks)        (parses documents)
```

---

# 7. Common errors and solutions

### ❗ `ModuleNotFoundError: No module named ‘app’`

You launched the worker **from the wrong directory**.
Go to the folder where `app/` is located:

```bash
cd backend
python -m dramatiq app.worker.tasks
```

### ❗ `redis.exceptions.ConnectionError`

Redis is not running → start Redis (WSL or Docker).
Check:

```bash
Test-NetConnection localhost -Port 6379
```

