from typing import Any, Optional
from pydantic import BaseModel

"""
Pydantic schemas for standard answers
- HealthResponse -> health-check
- ErrorDetail and ErrorResponse -> uniform error format
"""

class HealthResponse(BaseModel):
    ok: bool
    name: str
    version: str

class ErrorDetail(BaseModel):
    code: str
    message: str
    ctx: Optional[dict[str, Any]] = None

class ErrorResponse(BaseModel):
    error: ErrorDetail
    request_id: Optional[str] = None