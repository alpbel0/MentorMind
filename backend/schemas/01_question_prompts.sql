-- =====================================================
-- MentorMind - Question Prompts Table
-- Task: 1.6
-- Description: Template definitions for question generation
-- =====================================================

-- Drop table if exists (for clean re-runs)
DROP TABLE IF EXISTS question_prompts CASCADE;

-- Create table
CREATE TABLE question_prompts (
    -- Primary Key
    id SERIAL PRIMARY KEY,

    -- Core fields
    primary_metric TEXT NOT NULL,
        -- Values: 'Truthfulness', 'Helpfulness', 'Safety', 'Bias',
        --         'Clarity', 'Consistency', 'Efficiency', 'Robustness'

    bonus_metrics JSONB NOT NULL DEFAULT '[]'::jsonb,
        -- Array of secondary metric names

    question_type TEXT NOT NULL,
        -- Examples: 'hallucination_test', 'factual_accuracy',
        --           'explain_like_5', 'harmful_content', etc.

    user_prompt TEXT NOT NULL,
        -- Prompt template for Claude (contains {category}, {golden_examples} placeholders)

    golden_examples JSONB NOT NULL DEFAULT '[]'::jsonb,
        -- Array of example question-answer pairs

    difficulty TEXT NOT NULL CHECK (difficulty IN ('easy', 'medium', 'hard')),

    category_hints JSONB NOT NULL DEFAULT '[]'::jsonb,
        -- Array of category preferences (e.g., ["Math", "Coding"] or ["any"])

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Unique constraint
CREATE UNIQUE INDEX idx_question_prompts_unique_metric_type
    ON question_prompts (primary_metric, question_type);

-- Performance indexes
CREATE INDEX idx_question_prompts_primary_metric
    ON question_prompts (primary_metric);

CREATE INDEX idx_question_prompts_difficulty
    ON question_prompts (difficulty);

-- Comment
COMMENT ON TABLE question_prompts IS
    'Template definitions for Claude-based question generation. Each row defines how to generate questions for a specific metric and question type.';
