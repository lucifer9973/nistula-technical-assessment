"""Confidence scoring and routing action logic."""

from app.constants import MessageAction, QueryType


BASE_SCORES: dict[QueryType, float] = {
    QueryType.PRE_SALES_AVAILABILITY: 0.91,
    QueryType.PRE_SALES_PRICING: 0.88,
    QueryType.POST_SALES_CHECKIN: 0.87,
    QueryType.SPECIAL_REQUEST: 0.74,
    QueryType.COMPLAINT: 0.38,
    QueryType.GENERAL_ENQUIRY: 0.70,
}


def calculate_confidence(query_type: QueryType, message_text: str) -> float:
    """Calculate a normalized confidence score in the range [0, 1]."""

    score = BASE_SCORES.get(query_type, 0.65)
    lowered = message_text.lower()

    if any(token in lowered for token in ("urgent", "asap", "immediately")):
        score -= 0.08

    if len(lowered) < 25:
        score += 0.03

    if "?" in lowered and query_type in {
        QueryType.PRE_SALES_AVAILABILITY,
        QueryType.PRE_SALES_PRICING,
        QueryType.POST_SALES_CHECKIN,
    }:
        score += 0.02

    return max(0.0, min(1.0, round(score, 2)))


def determine_action(query_type: QueryType, confidence_score: float) -> MessageAction:
    """Map confidence score and intent into an operational action."""

    if query_type == QueryType.COMPLAINT or confidence_score < 0.60:
        return MessageAction.ESCALATE
    if confidence_score > 0.85:
        return MessageAction.AUTO_SEND
    return MessageAction.AGENT_REVIEW
