import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

logging.basicConfig(level=logging.INFO)

class LogRequestBodyMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.url.path == "/api/system/exchanges" and request.method == "POST":
            body = await request.body()
            logging.info(f"Intercepted request body for {request.method} {request.url.path}: {body.decode()}")
            # Re-populate the stream so that the endpoint can read it
            async def receive():
                return {"type": "http.request", "body": body}
            request = Request(request.scope, receive)
        
        response = await call_next(request)
        return response