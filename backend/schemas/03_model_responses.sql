-- =====================================================
-- MentorMind - Model Responses Table
-- Task: 1.8
-- Description: K model answers to questions
-- =====================================================

DROP TABLE IF EXISTS model_responses CASCADE;

CREATE TABLE model_responses (
    -- Primary Key (custom format)
    id TEXT PRIMARY KEY,
        -- Format: resp_YYYYMMDD_HHMMSS_randomhex

    -- Foreign key to question
    question_id TEXT NOT NULL REFERENCES questions(id) ON DELETE CASCADE,

    -- Model info
    model_name TEXT NOT NULL CHECK (model_name IN (
        'gpt-3.5-turbo',
        'gpt-4o-mini',
        'claude-3-5-haiku-20241022',
        'gemini-2.0-flash-exp'
    )),

    -- Response
    response_text TEXT NOT NULL,

    -- Evaluation tracking
    evaluated BOOLEAN NOT NULL DEFAULT FALSE,
    evaluation_id TEXT,
        -- Will reference user_evaluations(id) after Task 1.9

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Unique constraint: each model answers each question once
CREATE UNIQUE INDEX idx_model_responses_unique_question_model
    ON model_responses (question_id, model_name);

-- Performance indexes
CREATE INDEX idx_model_responses_question_id
    ON model_responses (question_id);

CREATE INDEX idx_model_responses_model_name
    ON model_responses (model_name);

CREATE INDEX idx_model_responses_evaluated
    ON model_responses (evaluated);

-- Index for finding un-evaluated responses
CREATE INDEX idx_model_responses_pending_evaluations
    ON model_responses (evaluated) WHERE evaluated = FALSE;

COMMENT ON TABLE model_responses IS
    'Responses from K models (GPT-3.5, GPT-4o-mini, Claude Haiku, Gemini). Each model answers each question exactly once.';
