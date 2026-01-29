-- =====================================================
-- MentorMind - Questions Table
-- Task: 1.7
-- Description: Generated questions with metadata
-- =====================================================

DROP TABLE IF EXISTS questions CASCADE;

CREATE TABLE questions (
    -- Primary Key (custom format)
    id TEXT PRIMARY KEY,
        -- Format: q_YYYYMMDD_HHMMSS_randomhex
        -- Example: q_20250126_143052_a1b2c3d4

    -- Core fields
    question TEXT NOT NULL,
    category TEXT NOT NULL,
    difficulty difficulty_level NOT NULL,
    reference_answer TEXT,
    expected_behavior TEXT,

    rubric_breakdown JSONB NOT NULL,
        -- Object mapping scores 1-5 to descriptions
        -- {"1": "description", "2": "description", ...}

    -- Denormalized fields (from question_prompts)
    primary_metric metric_type NOT NULL,
    bonus_metrics JSONB NOT NULL DEFAULT '[]'::jsonb,

    -- Foreign key to source prompt (nullable)
    question_prompt_id INTEGER REFERENCES question_prompts(id) ON DELETE SET NULL,

    -- Usage tracking (for pool management)
    times_used INTEGER NOT NULL DEFAULT 0,
    first_used_at TIMESTAMP,
    last_used_at TIMESTAMP,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Performance indexes
CREATE INDEX idx_questions_primary_metric
    ON questions (primary_metric);

CREATE INDEX idx_questions_category
    ON questions (category);

CREATE INDEX idx_questions_difficulty
    ON questions (difficulty);

CREATE INDEX idx_questions_times_used
    ON questions (times_used);

-- Composite index for pool selection (lowest times_used first)
CREATE INDEX idx_questions_pool_selection
    ON questions (primary_metric, difficulty, times_used ASC);

COMMENT ON TABLE questions IS
    'Generated questions from Claude. Denormalized primary_metric and bonus_metrics for query performance.';
