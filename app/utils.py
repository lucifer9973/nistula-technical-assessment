"""General utility helpers for the API."""

import logging
import uuid
from datetime import UTC, datetime

from app.classifier import classify_query
from app.schemas import InboundMessagePayload, NormalizedMessage


def setup_logging() -> None:
    """Configure a concise structured logging format."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def generate_message_id() -> uuid.UUID:
    """Generate a UUID4 for message-level traceability."""

    return uuid.uuid4()


def utc_now() -> datetime:
    """Return timezone-aware UTC timestamp."""

    return datetime.now(UTC)


def normalize_payload(payload: InboundMessagePayload) -> NormalizedMessage:
    """Transform inbound payload into the normalized internal schema."""

    query_type = classify_query(payload.message)

    return NormalizedMessage(
        message_id=generate_message_id(),
        source=payload.source,
        guest_name=payload.guest_name,
        message_text=payload.message,
        timestamp=payload.timestamp,
        booking_ref=payload.booking_ref,
        property_id=payload.property_id,
        query_type=query_type,
    )
