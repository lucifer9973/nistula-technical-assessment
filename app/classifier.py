"""Rule-based classification for guest intent detection."""

from app.constants import CLASSIFIER_KEYWORDS, QUERY_PRIORITY, QueryType


def classify_query(message_text: str) -> QueryType:
    """Classify a message into one of the supported query types.

    Complaints are given strict priority to enforce safe escalation.
    """

    lowered = message_text.lower().strip()
    if not lowered:
        return QueryType.GENERAL_ENQUIRY

    matched_types: set[QueryType] = set()

    for query_type, keywords in CLASSIFIER_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            matched_types.add(query_type)

    for query_type in QUERY_PRIORITY:
        if query_type in matched_types:
            return query_type

    return QueryType.GENERAL_ENQUIRY
