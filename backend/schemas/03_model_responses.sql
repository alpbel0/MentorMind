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

    -- Model info (6 models via OpenRouter)
    model_name TEXT NOT NULL CHECK (model_name IN (
        'mistralai/mistral-nemo',
        'qwen/qwen-2.5-7b-instruct',
        'deepseek/deepseek-chat',
        'google/gemini-2.0-flash-001',
        'openai/gpt-4o-mini',
        'openai/gpt-3.5-turbo'
    )),

    -- Response
    response_text TEXT NOT NULL,

    -- Evaluation tracking
    evaluated BOOLEAN NOT NULL DEFAULT FALSE,

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
    'Responses from K models via OpenRouter (Mistral Nemo, Qwen 2.5, DeepSeek, Gemini Flash, GPT-4o-mini, GPT-3.5-turbo). Each model answers each question exactly once.';
