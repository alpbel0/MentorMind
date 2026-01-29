"""
MentorMind - Request Logging Middleware

This module provides middleware for logging HTTP requests and responses.
It tracks request duration, status codes, and other relevant information.
"""

import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


logger = logging.getLogger(__name__)


# =====================================================
# Request Logging Middleware
# =====================================================

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests and responses.

    Features:
    - Generates unique request IDs for tracking
    - Logs request method, path, and client IP
    - Tracks request duration
    - Logs response status code

    Log format:
        [REQ] {request_id} {method} {path} from {client}
        [RES] {request_id} {status_code} - {duration:.2f}ms
    """

    def __init__(self, app: ASGIApp):
        """
        Initialize the middleware.

        Args:
            app: The ASGI application to wrap
        """
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """
        Process each request and log its details.

        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler in the chain

        Returns:
            The HTTP response from the route handler
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())[:8]

        # Get client IP (handle proxy scenarios)
        client_ip = self._get_client_ip(request)

        # Get request details
        method = request.method
        path = request.url.path

        # Log incoming request
        logger.info(f"[REQ] {request_id} {method} {path} from {client_ip}")

        # Process request and measure duration
        start_time = time.time()
        try:
            response = await call_next(request)
            duration = (time.time() - start_time) * 1000  # Convert to ms

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            # Log response
            logger.info(
                f"[RES] {request_id} {response.status_code} - {duration:.2f}ms"
            )

            return response

        except Exception as e:
            duration = (time.time() - start_time) * 1000

            # Log error response
            logger.error(
                f"[ERR] {request_id} Exception after {duration:.2f}ms: {e}"
            )
            raise

    def _get_client_ip(self, request: Request) -> str:
        """
        Get the client IP address, handling proxy scenarios.

        Args:
            request: The incoming HTTP request

        Returns:
            Client IP address as string
        """
        # Check for forwarded headers (proxy/load balancer)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # X-Forwarded-For can contain multiple IPs, use the first one
            return forwarded.split(",")[0].strip()

        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to direct connection IP
        if request.client:
            return request.client.host

        return "unknown"
