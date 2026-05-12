-- nistula-technical-assessment PostgreSQL schema
-- Purpose: Unified hospitality messaging data model across channels.

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- guests
-- Stores a canonical guest profile and channel identifiers used to reconcile
-- the same person across WhatsApp, Booking.com, Airbnb, Instagram, and direct channels.
CREATE TABLE IF NOT EXISTS guests (
    guest_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(120) NOT NULL,
    primary_email VARCHAR(255),
    primary_phone VARCHAR(32),
    external_profiles JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_guest_email_format CHECK (
        primary_email IS NULL OR primary_email ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'
    )
);

COMMENT ON TABLE guests IS 'Canonical guest record shared across all inbound sources.';
COMMENT ON COLUMN guests.external_profiles IS 'Channel-specific IDs keyed by source, e.g. {"whatsapp":"+91...","airbnb":"ab_123"}.';

-- reservations
-- Booking-level data used to link inquiry and post-sales support context.
CREATE TABLE IF NOT EXISTS reservations (
    reservation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_ref VARCHAR(64) NOT NULL UNIQUE,
    property_id VARCHAR(64) NOT NULL,
    guest_id UUID NOT NULL REFERENCES guests(guest_id) ON DELETE RESTRICT,
    source_channel VARCHAR(32) NOT NULL,
    checkin_date DATE,
    checkout_date DATE,
    guest_count SMALLINT,
    status VARCHAR(32) NOT NULL DEFAULT 'unknown',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_guest_count_positive CHECK (guest_count IS NULL OR guest_count > 0)
);

COMMENT ON TABLE reservations IS 'Reservation metadata tied to a canonical guest and channel booking reference.';

-- conversations
-- A conversation groups related messages for a guest, optionally linked to a reservation.
CREATE TABLE IF NOT EXISTS conversations (
    conversation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    guest_id UUID NOT NULL REFERENCES guests(guest_id) ON DELETE CASCADE,
    reservation_id UUID REFERENCES reservations(reservation_id) ON DELETE SET NULL,
    source_channel VARCHAR(32) NOT NULL,
    subject VARCHAR(150),
    status VARCHAR(32) NOT NULL DEFAULT 'open',
    opened_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_closed_after_opened CHECK (closed_at IS NULL OR closed_at >= opened_at)
);

COMMENT ON TABLE conversations IS 'Thread-level object for routing, SLA tracking, and escalation history.';

-- messages
-- Stores both inbound guest messages and drafted/sent outbound responses.
CREATE TABLE IF NOT EXISTS messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(conversation_id) ON DELETE CASCADE,
    reservation_id UUID REFERENCES reservations(reservation_id) ON DELETE SET NULL,
    source_channel VARCHAR(32) NOT NULL,
    direction VARCHAR(16) NOT NULL,
    guest_name VARCHAR(120),
    message_text TEXT NOT NULL,
    query_type VARCHAR(64) NOT NULL,
    confidence_score NUMERIC(4, 3),
    action VARCHAR(32),
    ai_drafted_reply TEXT,
    agent_edited_reply TEXT,
    ai_model VARCHAR(80),
    normalized_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    source_message_timestamp TIMESTAMPTZ,
    source_message_id VARCHAR(128),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_message_direction CHECK (direction IN ('inbound', 'outbound')),
    CONSTRAINT chk_confidence_range CHECK (confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1))
);

COMMENT ON TABLE messages IS 'Message ledger with AI draft, human edit, confidence score, and classification.';
COMMENT ON COLUMN messages.normalized_payload IS 'Snapshot of normalized webhook payload to support reproducibility and audits.';

-- Useful indexes for read-heavy operations and escalation workflows.
CREATE INDEX IF NOT EXISTS idx_guests_phone ON guests(primary_phone);
CREATE INDEX IF NOT EXISTS idx_reservations_guest_id ON reservations(guest_id);
CREATE INDEX IF NOT EXISTS idx_reservations_property_id ON reservations(property_id);
CREATE INDEX IF NOT EXISTS idx_conversations_guest_status ON conversations(guest_id, status);
CREATE INDEX IF NOT EXISTS idx_conversations_reservation_id ON conversations(reservation_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_created ON messages(conversation_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_query_type ON messages(query_type);
CREATE INDEX IF NOT EXISTS idx_messages_action ON messages(action);
CREATE INDEX IF NOT EXISTS idx_messages_low_confidence ON messages(confidence_score) WHERE confidence_score < 0.60;
CREATE INDEX IF NOT EXISTS idx_messages_complaints ON messages(query_type, created_at DESC) WHERE query_type = 'complaint';

-- Optional trigger helper for updated_at maintenance.
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_guests_set_updated_at ON guests;
CREATE TRIGGER trg_guests_set_updated_at
BEFORE UPDATE ON guests
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_reservations_set_updated_at ON reservations;
CREATE TRIGGER trg_reservations_set_updated_at
BEFORE UPDATE ON reservations
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_conversations_set_updated_at ON conversations;
CREATE TRIGGER trg_conversations_set_updated_at
BEFORE UPDATE ON conversations
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_messages_set_updated_at ON messages;
CREATE TRIGGER trg_messages_set_updated_at
BEFORE UPDATE ON messages
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Hardest Design Decision
-- Cross-platform guest identity handling:
-- The hardest issue is reconciling one real-world guest across fragmented channel identifiers.
-- A strict unique key per channel creates duplicates; a soft identity model risks false merges.
-- This schema keeps a canonical guests row and stores channel handles in external_profiles JSONB,
-- allowing progressive identity stitching without destructive merges.
--
-- Conversation linkage challenges:
-- Not all messages map cleanly to a reservation at ingest time.
-- conversations.reservation_id is nullable so early pre-sales messages can still be threaded,
-- then linked later once booking_ref is known.
--
-- Scalability considerations:
-- messages is the highest-volume table, so indexes target common filters: conversation timeline,
-- complaints, action queues, and low-confidence cases.
-- Normalized payload snapshots in JSONB preserve replay/debug capability without forcing frequent
-- schema migrations for source-specific fields.
