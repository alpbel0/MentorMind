-- =====================================================
-- MentorMind - Evaluation Snapshots Table
-- Task: 11.2
-- Description: Immutable snapshots of completed evaluations for Coach Chat & Evidence
-- Reference: AD-3 (New Snapshot Table), AD-13 (Retention Policy)
-- =====================================================

DROP TABLE IF EXISTS evaluation_snapshots CASCADE;

CREATE TABLE evaluation_snapshots (
    -- Primary Key (custom format)
    id TEXT PRIMARY KEY,
        -- Format: snap_YYYYMMDD_HHMMSS_randomhex

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Question snapshot (immutable copy)
    question_id TEXT NOT NULL,
        -- Reference to original question (not FK, allows question deletion)
    question TEXT NOT NULL,
        -- Snapshot of question text
    model_answer TEXT NOT NULL,
        -- Snapshot of model's response
    model_name TEXT NOT NULL,
        -- Model that provided the answer

    -- Judge metadata
    judge_model TEXT NOT NULL DEFAULT 'gpt-4o',

    -- Metric information (using SLUG format per Task 11.1)
    primary_metric TEXT NOT NULL,
        -- Values: 'truthfulness', 'helpfulness', 'safety', 'bias',
        --         'clarity', 'consistency', 'efficiency', 'robustness'
    bonus_metrics JSONB NOT NULL DEFAULT '[]'::jsonb,
        -- Array of metric slugs, e.g., ['clarity', 'helpfulness']
    category TEXT,
        -- Math, Coding, Medical, General, etc.

    -- Scores (nested by metric slug per user decision)
    user_scores_json JSONB NOT NULL,
        -- Structure: {
        --   "truthfulness": {"score": 4, "reasoning": "Good accuracy"},
        --   "helpfulness": {"score": 3, "reasoning": "Somewhat helpful"},
        --   ...
        -- }
    judge_scores_json JSONB NOT NULL,
        -- Structure: {
        --   "truthfulness": {"score": 5, "rationale": "Excellent catch"},
        --   "helpfulness": {"score": 3, "rationale": "Adequate guidance"},
        --   ...
        -- }

    -- Evidence (for Coach Chat - AD-3, AD-7)
    evidence_json JSONB,
        -- Per-metric evidence items
        -- Structure: {
        --   "truthfulness": [
        --     {
        --       "start": 42,
        --       "end": 87,
        --       "quote": "...",
        --       "why": "Hallucination detected",
        --       "better": "Correct answer is...",
        --       "verified": true,
        --       "highlight_available": true
        --     }
        --   ],
        --   "clarity": [...]
        -- }

    -- Judge summary
    judge_meta_score INTEGER NOT NULL CHECK (judge_meta_score BETWEEN 1 AND 5),
    weighted_gap REAL NOT NULL,
    overall_feedback TEXT,

    -- Source references (not FKs - allow source deletion)
    user_evaluation_id TEXT,
        -- Reference to user_evaluations table
    judge_evaluation_id TEXT,
        -- Reference to judge_evaluations table

    -- Chat metadata (AD-9: Turn Limit)
    chat_turn_count INTEGER NOT NULL DEFAULT 0,
    max_chat_turns INTEGER NOT NULL DEFAULT 15,
        -- Coach conversation limits

    -- Status and soft delete
    status snapshot_status NOT NULL DEFAULT 'active',
    deleted_at TIMESTAMP,
        -- NULL = not deleted, set = soft deleted
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- =====================================================
-- Indexes
-- =====================================================

-- Status filter (primary query pattern)
CREATE INDEX idx_snapshots_status
    ON evaluation_snapshots (status);

-- Primary metric filter
CREATE INDEX idx_snapshots_primary_metric
    ON evaluation_snapshots (primary_metric);

-- Time-based queries (newest first - AD-13: Retention)
CREATE INDEX idx_snapshots_created_at
    ON evaluation_snapshots (created_at DESC);

-- Soft delete queries (per user requirement)
CREATE INDEX idx_snapshots_deleted_at
    ON evaluation_snapshots (deleted_at)
    WHERE deleted_at IS NOT NULL;

-- Composite: active snapshots by primary metric (common UI query)
CREATE INDEX idx_snapshots_active_metric
    ON evaluation_snapshots (primary_metric, created_at DESC)
    WHERE status = 'active' AND deleted_at IS NULL;

-- =====================================================
-- Comments
-- =====================================================

COMMENT ON TABLE evaluation_snapshots IS
    'Immutable snapshots of completed evaluations for Coach Chat & Evidence. Isolated from live tables - source deletions don''t affect chat history. Supports soft delete and retention policies (AD-13).';

COMMENT ON COLUMN evaluation_snapshots.id IS
    'Primary key: snap_YYYYMMDD_HHMMSS_randomhex format';

COMMENT ON COLUMN evaluation_snapshots.question_id IS
    'Reference to original question (not FK - question can be deleted without affecting snapshot)';

COMMENT ON COLUMN evaluation_snapshots.primary_metric IS
    'Primary metric being evaluated (slug format: truthfulness, helpfulness, etc.)';

COMMENT ON COLUMN evaluation_snapshots.user_scores_json IS
    'User scores nested by metric slug: {"truthfulness": {"score": 4, "reasoning": "..."}}';

COMMENT ON COLUMN evaluation_snapshots.judge_scores_json IS
    'Judge scores nested by metric slug: {"truthfulness": {"score": 5, "rationale": "..."}}';

COMMENT ON COLUMN evaluation_snapshots.evidence_json IS
    'Per-metric evidence items for Coach Chat highlighting';

COMMENT ON COLUMN evaluation_snapshots.status IS
    'Snapshot status: active (chat available), completed (chat finished), archived (retention policy)';

COMMENT ON COLUMN evaluation_snapshots.deleted_at IS
    'Soft delete timestamp - NULL if not deleted, set when user deletes chat';

-- =====================================================
-- Trigger: Auto-update updated_at
-- =====================================================

DROP TRIGGER IF EXISTS trigger_evaluation_snapshots_updated_at
    ON evaluation_snapshots;

CREATE TRIGGER trigger_evaluation_snapshots_updated_at
    BEFORE UPDATE ON evaluation_snapshots
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
