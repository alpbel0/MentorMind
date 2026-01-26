-- =====================================================
-- MentorMind - User Evaluations Table
-- Task: 1.9
-- Description: User's evaluation of model responses
-- =====================================================

DROP TABLE IF EXISTS user_evaluations CASCADE;

CREATE TABLE user_evaluations (
    -- Primary Key (custom format)
    id TEXT PRIMARY KEY,
        -- Format: eval_YYYYMMDD_HHMMSS_randomhex

    -- Foreign key to model response
    response_id TEXT NOT NULL REFERENCES model_responses(id) ON DELETE CASCADE,

    -- Evaluation data (8 metrics)
    evaluations JSONB NOT NULL,
        -- Structure:
        -- {
        --   "Truthfulness": {"score": 3, "reasoning": "..."},
        --   "Helpfulness": {"score": null, "reasoning": "N/A"},
        --   ... (all 8 metrics)
        -- }

    -- Judge tracking
    judged BOOLEAN NOT NULL DEFAULT FALSE,
    judge_evaluation_id TEXT,
        -- Will reference judge_evaluations(id) after Task 1.10

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Performance indexes
CREATE INDEX idx_user_evaluations_response_id
    ON user_evaluations (response_id);

CREATE INDEX idx_user_evaluations_judged
    ON user_evaluations (judged);

-- Time-based index (newest first)
CREATE INDEX idx_user_evaluations_created_at_desc
    ON user_evaluations (created_at DESC);

COMMENT ON TABLE user_evaluations IS
    'User evaluations of model responses across 8 metrics. Judge evaluation runs asynchronously in background.';
