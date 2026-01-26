-- =====================================================
-- MentorMind - Judge Evaluations Table
-- Task: 1.10
-- Description: GPT-4o's two-stage evaluation
-- =====================================================

DROP TABLE IF EXISTS judge_evaluations CASCADE;

CREATE TABLE judge_evaluations (
    -- Primary Key (custom format)
    id TEXT PRIMARY KEY,
        -- Format: judge_YYYYMMDD_HHMMSS_randomhex

    -- Foreign key to user evaluation
    user_evaluation_id TEXT NOT NULL REFERENCES user_evaluations(id) ON DELETE CASCADE,

    -- Stage 1: Independent Evaluation (GPT-4o blind scoring)
    independent_scores JSONB NOT NULL,
        -- Same structure as user_evaluations.evaluations

    -- Stage 2: Mentoring Comparison (gap analysis)
    alignment_analysis JSONB NOT NULL,
        -- Per-metric gap analysis
        -- {
        --   "Truthfulness": {
        --     "user_score": 3,
        --     "judge_score": 2,
        --     "gap": 1,
        --     "verdict": "over_estimated",
        --     "feedback": "..."
        --   },
        --   ... (all 8 metrics)
        -- }

    -- Meta evaluation
    judge_meta_score INTEGER NOT NULL CHECK (judge_meta_score BETWEEN 1 AND 5),
        -- 1: Very poor alignment
        -- 2: Poor alignment
        -- 3: Moderate alignment
        -- 4: Good alignment
        -- 5: Excellent alignment

    overall_feedback TEXT NOT NULL,

    improvement_areas JSONB NOT NULL DEFAULT '[]'::jsonb,
    positive_feedback JSONB NOT NULL DEFAULT '[]'::jsonb,

    -- ChromaDB context
    vector_context JSONB,
        -- Past mistakes retrieved from ChromaDB

    -- Gap metrics (for statistics)
    primary_metric TEXT NOT NULL,
    primary_metric_gap REAL NOT NULL,
    weighted_gap REAL NOT NULL,
        -- Formula: primary*0.7 + bonus_avg*0.2 + other_avg*0.1

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Performance indexes
CREATE INDEX idx_judge_evaluations_user_evaluation_id
    ON judge_evaluations (user_evaluation_id);

CREATE INDEX idx_judge_evaluations_meta_score
    ON judge_evaluations (judge_meta_score);

CREATE INDEX idx_judge_evaluations_primary_metric
    ON judge_evaluations (primary_metric);

-- Time-based index (newest first)
CREATE INDEX idx_judge_evaluations_created_at_desc
    ON judge_evaluations (created_at DESC);

-- Composite index for statistics queries
CREATE INDEX idx_judge_evaluations_metric_score
    ON judge_evaluations (primary_metric, judge_meta_score);

COMMENT ON TABLE judge_evaluations IS
    'GPT-4o two-stage evaluation: (1) Independent blind scoring, (2) Mentoring comparison with user scores. Includes ChromaDB-retrieved past mistakes.';
