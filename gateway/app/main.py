from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .core.cors import setup_cors
from .core.logging import setup_logging
from .core.config import settings
from .middlewares.request_id import RequestIDMiddleware
from .schemas.common import ErrorResponse, ErrorDetail
from .api.v1.routes import api_router

setup_logging()
app = FastAPI(title=settings.APP_NAME, version= settings.APP_VERSION)

# middleware
app.add_middleware(RequestIDMiddleware)
setup_cors(app)

# system root ping
@app.get("/health")
def root_health():
    return {"ok": True}

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    rid = getattr(request.state, "request_id", None)
    body = ErrorResponse(
        error=ErrorDetail(code = str(exc.status_code), message=exc.detail),
        request_id=rid
    )
    return  JSONResponse(status_code=exc.status_code, content= body.model_dump())

@app.exception_handler(RequestValidationError)
async  def validation_exceptiom_handler(request: Request, exc:  RequestValidationError):
    rid = getattr(request.state, "request_id", None)
    body = ErrorResponse(
        error=ErrorDetail(code="422", message="Validation error", ctx={"errors": exc.errors()}),
        request_id=rid,
    )
    return JSONResponse(status_code=422, content=body.model_dump())


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    rid = getattr(request.state, "request_id", None)
    # Логувати можна тут (loguru), але не шумимо у відповіді
    body = ErrorResponse(
        error=ErrorDetail(code="500", message="Internal Server Error"),
        request_id=rid,
    )
    return JSONResponse(status_code=500, content=body.model_dump())

# API v1
app.include_router(api_router, prefix="/api/v1")