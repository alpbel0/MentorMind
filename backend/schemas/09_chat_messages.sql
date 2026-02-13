-- =====================================================
-- MentorMind - Chat Messages Table
-- Task: 11.3
-- Description: Chat history for Coach conversations
-- Reference: AD-3 (New Snapshot Table), AD-4 (SSE + DB Chat)
-- =====================================================

DROP TABLE IF EXISTS chat_messages CASCADE;

CREATE TABLE chat_messages (
    -- Primary Key (custom format)
    id TEXT PRIMARY KEY,
        -- Format: msg_YYYYMMDD_HHMMSS_randomhex

    -- Shared Turn ID (for idempotency - AD-4)
    client_message_id TEXT NOT NULL,
        -- Client-generated UUID (v4)
        -- Both user and assistant messages in same turn share this ID

    -- Completion flag (for SSE reconnect - AD-4)
    is_complete BOOLEAN NOT NULL DEFAULT TRUE,
        -- true: Message fully delivered
        -- false: Streaming in progress (allows Update-In-Place on reconnect)

    -- Foreign key to snapshot
    snapshot_id TEXT NOT NULL REFERENCES evaluation_snapshots(id) ON DELETE CASCADE,

    -- Message role
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),

    -- Content
    content TEXT NOT NULL DEFAULT '',

    -- Selected metrics (for user messages only)
    selected_metrics JSONB,
        -- Array of metric slugs, e.g., ['truthfulness', 'clarity']
        -- Null for assistant messages (derived from conversation context)

    -- Token count (for analytics)
    token_count INTEGER NOT NULL DEFAULT 0,

    -- Timestamp
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- =====================================================
-- Constraints
-- =====================================================

-- Idempotency constraint (AD-4)
-- Prevents duplicate messages - same snapshot, same turn, same role = unique
CREATE UNIQUE INDEX idx_chat_messages_idempotency
    ON chat_messages (snapshot_id, client_message_id, role);

-- =====================================================
-- Indexes
-- =====================================================

-- Chat history queries (ordered by time)
CREATE INDEX idx_chat_messages_snapshot_created
    ON chat_messages (snapshot_id, created_at DESC);

-- Dedup lookup (fast idempotency check)
CREATE INDEX idx_chat_messages_client_message
    ON chat_messages (snapshot_id, client_message_id);

-- =====================================================
-- Comments
-- =====================================================

COMMENT ON TABLE chat_messages IS
    'Chat history for Coach conversations. Uses Shared Turn ID (client_message_id) for idempotency. is_complete enables SSE reconnection with Update-In-Place.';

COMMENT ON COLUMN chat_messages.id IS
    'Primary key: msg_YYYYMMDD_HHMMSS_randomhex format';

COMMENT ON COLUMN chat_messages.client_message_id IS
    'Client-generated UUID (Shared Turn ID). Both user and assistant messages in same turn share this ID. Enables idempotency and deduplication.';

COMMENT ON COLUMN chat_messages.is_complete IS
    'True = message fully delivered, False = streaming in progress. Enables Update-In-Place pattern for SSE reconnection.';

COMMENT ON COLUMN chat_messages.role IS
    'Message role: user or assistant';

COMMENT ON COLUMN chat_messages.selected_metrics IS
    'Array of metric slugs selected for this conversation turn (user messages only). Examples: ["truthfulness", "clarity"]';

COMMENT ON COLUMN chat_messages.token_count IS
    'Token count for the message (used for analytics and cost tracking)';

-- =====================================================
-- Trigger: Auto-update updated_at
-- =====================================================

-- Add updated_at column first (missing in original schema)
ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP NOT NULL DEFAULT NOW();

DROP TRIGGER IF EXISTS trigger_chat_messages_updated_at
    ON chat_messages;

CREATE TRIGGER trigger_chat_messages_updated_at
    BEFORE UPDATE ON chat_messages
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
