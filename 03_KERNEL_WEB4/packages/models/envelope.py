"""
Standard API response envelope.

Every response follows:
{
  "success": true/false,
  "request_id": "...",
  "trace_id": "...",
  "timestamp": "...",
  "data": { ... }        # on success
  "error": { ... }       # on failure
}
"""

from __future__ import annotations

import time
from typing import Any, Optional

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str
    status: int
    message: str
    request_id: Optional[str] = None
    trace_id: Optional[str] = None


class Envelope(BaseModel):
    success: bool = True
    request_id: Optional[str] = None
    trace_id: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)
    data: Optional[Any] = None
    error: Optional[ErrorDetail] = None

    @classmethod
    def ok(
        cls, data: Any, request_id: str | None = None, trace_id: str | None = None
    ) -> "Envelope":
        return cls(success=True, data=data, request_id=request_id, trace_id=trace_id)

    @classmethod
    def fail(
        cls,
        code: str,
        status: int,
        message: str,
        request_id: str | None = None,
        trace_id: str | None = None,
    ) -> "Envelope":
        return cls(
            success=False,
            error=ErrorDetail(
                code=code,
                status=status,
                message=message,
                request_id=request_id,
                trace_id=trace_id,
            ),
            request_id=request_id,
            trace_id=trace_id,
        )


ERROR_MAP = {
    400: "INVALID_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    409: "CONFLICT",
    422: "VALIDATION_FAILED",
    429: "RATE_LIMITED",
    500: "INTERNAL_ERROR",
}
