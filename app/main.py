"""FastAPI application entrypoint."""

import logging
import uuid

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.claude_service import ClaudeService
from app.confidence import calculate_confidence, determine_action
from app.constants import PROPERTY_CONTEXT
from app.schemas import ErrorResponse, InboundMessagePayload, WebhookResponse
from app.utils import normalize_payload, setup_logging

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Nistula Technical Assessment API",
    version="1.0.0",
    description="Hospitality messaging backend with normalization, intent detection, and AI reply drafting.",
)

claude_service = ClaudeService()


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Return consistent JSON payloads for handled HTTP exceptions."""

    payload = exc.detail
    request_id = uuid.uuid4()
    logger.warning(
        "HTTP exception | request_id=%s | path=%s | status_code=%s",
        request_id,
        request.url.path,
        exc.status_code,
    )

    if isinstance(payload, dict):
        body = {
            "error": payload.get("error", "http_error"),
            "detail": payload.get("detail", "Request failed"),
            "request_id": payload.get("request_id", str(request_id)),
        }
    else:
        body = {
            "error": "http_error",
            "detail": str(payload),
            "request_id": str(request_id),
        }

    return JSONResponse(status_code=exc.status_code, content=body)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Return structured validation errors for malformed payloads."""

    request_id = uuid.uuid4()
    logger.warning("Validation error | request_id=%s | path=%s", request_id, request.url.path)

    response = ErrorResponse(
        error="validation_error",
        detail=str(exc),
        request_id=request_id,
    )
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=response.model_dump(mode="json"))


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch unhandled errors and keep response format consistent."""

    request_id = uuid.uuid4()
    logger.exception(
        "Unhandled exception | request_id=%s | path=%s | error=%s",
        request_id,
        request.url.path,
        str(exc),
    )

    response = ErrorResponse(
        error="internal_server_error",
        detail="An unexpected error occurred.",
        request_id=request_id,
    )
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=response.model_dump(mode="json"))


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Liveness probe endpoint."""

    return {"status": "ok", "service": "nistula-technical-assessment"}


@app.post(
    "/webhook/message",
    response_model=WebhookResponse,
    responses={
        422: {"model": ErrorResponse},
        502: {"model": ErrorResponse},
        504: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    tags=["messages"],
    summary="Process inbound guest message",
)
async def handle_inbound_message(payload: InboundMessagePayload) -> WebhookResponse:
    """Normalize inbound message, draft response via Claude, and return routing decision."""

    normalized = normalize_payload(payload)

    try:
        drafted_reply = await claude_service.generate_reply(
            normalized_message=normalized,
            property_context=PROPERTY_CONTEXT,
        )
    except RuntimeError as exc:
        detail = str(exc)
        logger.error("Claude service failure | message_id=%s | detail=%s", normalized.message_id, detail)

        if "timeout" in detail.lower():
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail={
                    "error": "claude_timeout",
                    "detail": "AI generation timed out. Please retry or route to agent.",
                    "request_id": str(normalized.message_id),
                },
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "error": "claude_api_error",
                "detail": "AI provider is currently unavailable.",
                "request_id": str(normalized.message_id),
            },
        ) from exc

    confidence_score = calculate_confidence(normalized.query_type, normalized.message_text)
    action = determine_action(normalized.query_type, confidence_score)

    return WebhookResponse(
        message_id=normalized.message_id,
        query_type=normalized.query_type,
        drafted_reply=drafted_reply,
        confidence_score=confidence_score,
        action=action,
    )
