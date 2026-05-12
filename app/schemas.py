"""Pydantic schemas for request/response contracts."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.constants import MessageAction, MessageSource, QueryType


class InboundMessagePayload(BaseModel):
    """Raw message payload from an external messaging channel."""

    source: MessageSource = Field(..., description="Inbound source channel")
    guest_name: str = Field(..., min_length=1, max_length=120)
    message: str = Field(..., min_length=1, max_length=4000)
    timestamp: datetime
    booking_ref: str = Field(..., min_length=3, max_length=64)
    property_id: str = Field(..., min_length=2, max_length=64)

    model_config = ConfigDict(str_strip_whitespace=True)


class NormalizedMessage(BaseModel):
    """Unified schema after inbound normalization and classification."""

    message_id: UUID
    source: MessageSource
    guest_name: str
    message_text: str
    timestamp: datetime
    booking_ref: str
    property_id: str
    query_type: QueryType


class WebhookResponse(BaseModel):
    """Drafted response and operational routing decision."""

    message_id: UUID
    query_type: QueryType
    drafted_reply: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    action: MessageAction


class ErrorResponse(BaseModel):
    """Standardized API error response body."""

    error: str
    detail: str
    request_id: UUID | None = None
