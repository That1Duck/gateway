# Gateway
Detailed documentation is [here](docs/).

# Overall
## Gateway
### Backend
Fast API
- Main web API framework.
- Handles file uploads, routers, validation, responses, and status endpoints.

Uvicorn
- ASGI server used to run FastAPI

### Database Layer
SQLAlchemy
- ORM for defining models and handling database operation

SQLite
- Storage for documents, metadata, chunked text, processing status, etc.

### Document Processing
pdfplumber / pypdf
- Extract text and metadata from PDF files.

python-docx
- Extract text and metadata from DOCX documents.

### Background Processing
Dramatiq 
- Task queue library used to execute heavy work outside the API process.

Redis
- Message broker for Dramatiq.
- Stores tasks such as parse_document_async(document_id).

Worker process
- Separate Python process that reads tasks from Redis and runs the document pipeline.

## Frontend
Nuxt + Vue
- UI for uploading files, viewing document history, and tracking processing status.

TailwindCSS
- Styling

Polling / API calls
- Frontend checks document status (queued → processing → ready).