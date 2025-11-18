# Gateway Backend Architecture Overview

This document provides a concise technical overview of the **Gateway backend**. It is intended for backend developers who need to understand, maintain, or extend the system. The goal is to present the core responsibilities of the gateway layer, describe how major components interact, and outline recommended extension patterns.

---

# 1. Technology Stack

The backend gateway is implemented using the following technologies:

* **FastAPI** – primary web framework, routing, validation, request handling.
* **Uvicorn** – ASGI server for hosting FastAPI.
* **SQLAlchemy ORM** – relational database access layer.
* **Alembic** – migrations and schema evolution.
* **Redis + Dramatiq** – distributed task queue for background document processing.
* **Pydantic** – input/output data validation and response models.
* **pdfplumber / python-docx / pypdf** – document parsing utilities.

The gateway exposes REST APIs used by the frontend and manages communication with the background worker.

---

# 2. Project Structure

The backend is organized into a modular layout for clarity and scalability:

```
gateway/
│
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── documents.py      # File upload, document retrieval
│   │
│   ├── db/
│   │   ├── base.py               # SQLAlchemy Base
│   │   ├── session.py            # Engine + SessionLocal
│   │   └── migrations/           # Alembic
│   │
│   ├── models/
│   │   └── document.py           # Document + DocumentChunk ORM models
│   │
│   ├── schemas/
│   │   └── document.py           # Pydantic response models
│   │
│   ├── services/
│   │   ├── pipeline.py           # Processing pipeline logic
│   │   ├── parsers.py            # Unified parser entry point
│   │   ├── parsers_pdf.py        # PDF extraction
│   │   └── parsers_docx.py       # DOCX extraction
│   │
│   ├── worker/
│   │   └── tasks.py              # Dramatiq tasks and Redis broker setup
│   │
│   └── main.py                   # FastAPI initialization + routing
│
└── .env / config files
```

This structure isolates API handling, business logic, data persistence, and background processing.

---

# 3. Core Components and Responsibilities

## 3.1 FastAPI Application (`main.py`)

* Instantiates the FastAPI application.
* Registers routers, middleware, and global configurations.
* Provides the `/health` endpoint.

## 3.2 API Layer (`api/routes/documents.py`)

Responsible for handling document-related operations:

* `POST /files/upload` – accepts file uploads, stores metadata, enqueues document processing.
* `GET /files/{id}` – retrieves document state, metadata, and processed text chunks.

The upload endpoint does not process files itself. Instead, it stores the file, records the document in the database, and sends a background task to Dramatiq.

---

# 4. Database Layer

## 4.1 SQLAlchemy Models (`models/document.py`)

Two primary entities:

### Document

Represents a user-uploaded document and holds:

* Original/stored names
* MIME type and file path
* SHA-256 hash (for deduplication)
* Metadata (title, author, page count, language)
* Processing status: `queued`, `processing`, `ready`, `failed`
* Progress percentage
* Error details

### DocumentChunk

Represents segmented text extracted from the document:

* Sequential chunk index
* Extracted text content
* Page range (page_from / page_to)

A `Document` has a one-to-many relationship with its chunks.

## 4.2 Alembic

Used for maintaining schema compatibility across development stages.

---

# 5. Background Processing

## 5.1 Dramatiq Tasks (`worker/tasks.py`)

Defines background tasks executed outside the API process.

Key elements:

* Configuration of **RedisBroker** for task queueing.
* Actor `parse_document_async(document_id)` with retries.
* Import and execution of the processing pipeline.

The worker is started with:

```
python -m dramatiq app.worker.tasks
```

## 5.2 Redis

Serves as the message broker for Dramatiq, storing queued document processing jobs.

---

# 6. Document Processing Pipeline (`services/pipeline.py`)

The pipeline is the core unit of document processing. It:

* Validates task idempotency
* Updates document status to `processing`
* Parses documents using a format-specific parser
* Extracts metadata
* Splits extracted text into chunks and persists them
* Updates `progress_percent` through defined stages
* Handles exceptions by marking the document as `failed`

This module contains no dependency on FastAPI or Dramatiq, promoting clean separation and reusability.

---

# 7. Parsing Layer (`services/parsers*.py`)

### parsers.py

Dispatches to specific parser implementations based on file extension or MIME type.

### parsers_pdf.py

Extracts:

* Page count
* Metadata (title, author)
* Per-page text

### parsers_docx.py

Extracts:

* Core DOCX metadata
* Full document text, optionally split into logical chunks

The parsing layer can be extended to support additional formats by implementing a new module and dispatch rule.

---

# 8. Gateway Responsibilities and Data Flow

The gateway backend coordinates the complete ingestion flow:

```
Client → FastAPI Gateway → Database → Redis Queue → Dramatiq Worker → Pipeline → Database → Client
```

Flow summary:

1. The client uploads a file.
2. Gateway stores the file and records metadata.
3. Gateway enqueues a processing task.
4. Worker processes the document and updates the database.
5. Client polls document status until completion.

---

# 9. Extending the Backend

### Adding New API Endpoints

* Create a new route file under `api/routes/`.
* Define associated models and schemas if necessary.
* Register the router in `main.py`.

### Adding New Task Types

* Add a new actor in `worker/tasks.py`.
* Implement task logic in a separate service module.

### Adding New Document Formats

* Implement a new parser module under `services/`.
* Add dispatch rules in `parsers.py`.

### Extending Document Metadata

* Modify the ORM model and corresponding Pydantic schema.
* Add a migration via Alembic.
* Update the pipeline to populate new fields.

---

# 10. Summary

The gateway backend is a modular FastAPI-based system designed for scalable document ingestion and background processing. Its architecture separates concerns across routing, services, persistence, and asynchronous workers. This structure simplifies maintenance and allows the project to grow by extending individual modules without redesigning the entire system.
