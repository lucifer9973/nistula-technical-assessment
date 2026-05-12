"""Prompt builders for Anthropic Claude interactions."""

from app.constants import QueryType
from app.schemas import NormalizedMessage


def build_system_prompt() -> str:
    """Return the static instruction set for hospitality-safe replies."""

    return (
        "You are an operations assistant for a premium hospitality brand. "
        "Draft concise, professional guest replies using only the provided property context. "
        "Do not hallucinate facts, policies, availability, or prices beyond context. "
        "Never promise refunds. For complaint cases, acknowledge concern, apologize briefly, "
        "and indicate rapid human follow-up. Keep response under 120 words."
    )


def build_user_prompt(message: NormalizedMessage, property_context: str) -> str:
    """Create a grounded user prompt for Claude."""

    complaint_instruction = ""
    if message.query_type == QueryType.COMPLAINT:
        complaint_instruction = (
            "This is a complaint. Avoid commitments on compensation/refund. "
            "Escalate with urgency and empathy."
        )

    return (
        f"Guest Name: {message.guest_name}\n"
        f"Source: {message.source.value}\n"
        f"Booking Reference: {message.booking_ref}\n"
        f"Property ID: {message.property_id}\n"
        f"Detected Query Type: {message.query_type.value}\n"
        f"Guest Message: {message.message_text}\n\n"
        f"Property Context:\n{property_context}\n\n"
        f"Additional Instruction: {complaint_instruction or 'Respond accurately and politely.'}\n\n"
        "Draft the best possible reply now."
    )
