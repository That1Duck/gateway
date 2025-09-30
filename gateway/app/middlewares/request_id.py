import uuid
from http.client import responses

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from ..core.config import settings


class RequestIDMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, header_name: str | None = None):
        super().__init__(app)
        self.header_name = header_name or settings.REQUEST_ID_HEADER

    async def dispatch(self, request: Request, call_next):
        """
        Checks for header {X-Request_ID}
        if no header -> generate new header via UUID

        Attached header to response and return it
        """
        req_id = request.headers.get(self.header_name) or str(uuid.uuid4())

        request.state.request_id = req_id
        response: Response = await call_next(request)
        return  response