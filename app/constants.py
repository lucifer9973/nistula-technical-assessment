"""Application-wide constants and enumerations."""

from enum import Enum


class MessageSource(str, Enum):
    """Supported inbound message channels."""

    WHATSAPP = "whatsapp"
    BOOKING_COM = "booking_com"
    AIRBNB = "airbnb"
    INSTAGRAM = "instagram"
    DIRECT = "direct"


class QueryType(str, Enum):
    """Unified categories for guest intents."""

    PRE_SALES_AVAILABILITY = "pre_sales_availability"
    PRE_SALES_PRICING = "pre_sales_pricing"
    POST_SALES_CHECKIN = "post_sales_checkin"
    SPECIAL_REQUEST = "special_request"
    COMPLAINT = "complaint"
    GENERAL_ENQUIRY = "general_enquiry"


class MessageAction(str, Enum):
    """Action recommended by confidence scoring."""

    AUTO_SEND = "auto_send"
    AGENT_REVIEW = "agent_review"
    ESCALATE = "escalate"


SUPPORTED_SOURCES = {source.value for source in MessageSource}

PROPERTY_CONTEXT = """Property: Villa B1, Assagao, North Goa
Bedrooms: 3 | Max guests: 6 | Private pool: Yes
Check-in: 2pm | Check-out: 11am
Base rate: INR 18,000 per night (up to 4 guests)
Extra guest: INR 2,000 per night per person
WiFi password: Nistula@2024
Caretaker: Available 8am to 10pm
Chef on call: Yes, pre-booking required
Availability April 20-24: Available
Cancellation: Free up to 7 days before check-in"""

CLASSIFIER_KEYWORDS: dict[QueryType, tuple[str, ...]] = {
    QueryType.COMPLAINT: (
        "angry",
        "frustrated",
        "not working",
        "refund",
        "unacceptable",
        "terrible",
        "worst",
        "bad service",
        "disappointed",
        "issue",
        "problem",
        "no hot water",
        "broken",
    ),
    QueryType.SPECIAL_REQUEST: (
        "airport transfer",
        "early check-in",
        "late check-out",
        "decorations",
        "surprise",
        "chef",
        "birthday setup",
        "pickup",
        "drop",
        "special arrangement",
        "extra bed",
    ),
    QueryType.POST_SALES_CHECKIN: (
        "wifi",
        "wi-fi",
        "check-in",
        "check in",
        "check-out",
        "check out",
        "caretaker",
        "password",
        "house rules",
        "location",
        "directions",
    ),
    QueryType.PRE_SALES_AVAILABILITY: (
        "available",
        "availability",
        "is it free",
        "date",
        "dates",
        "from",
        "to",
        "nights",
        "calendar",
        "vacant",
    ),
    QueryType.PRE_SALES_PRICING: (
        "rate",
        "rates",
        "price",
        "pricing",
        "cost",
        "tariff",
        "charges",
        "discount",
        "inr",
        "quote",
        "how much",
    ),
}

QUERY_PRIORITY: tuple[QueryType, ...] = (
    QueryType.COMPLAINT,
    QueryType.SPECIAL_REQUEST,
    QueryType.POST_SALES_CHECKIN,
    QueryType.PRE_SALES_AVAILABILITY,
    QueryType.PRE_SALES_PRICING,
    QueryType.GENERAL_ENQUIRY,
)
