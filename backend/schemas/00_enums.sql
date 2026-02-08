-- =====================================================
-- MentorMind - Custom ENUM Types
-- Task: SQL Schema Correction
-- Description: PostgreSQL ENUM types for metrics and difficulty
-- =====================================================

-- Drop existing types if they exist (for clean re-runs)
DROP TYPE IF EXISTS metric_type CASCADE;
DROP TYPE IF EXISTS difficulty_level CASCADE;

-- Create metric_type ENUM
CREATE TYPE metric_type AS ENUM (
    'Truthfulness',
    'Helpfulness',
    'Safety',
    'Bias',
    'Clarity',
    'Consistency',
    'Efficiency',
    'Robustness'
);

COMMENT ON TYPE metric_type IS
    'The 8 evaluation metrics used in MentorMind for AI model assessment';

-- Create difficulty_level ENUM
CREATE TYPE difficulty_level AS ENUM (
    'easy',
    'medium',
    'hard'
);

COMMENT ON TYPE difficulty_level IS
    'Difficulty levels for questions: easy, medium, hard';

-- =====================================================
-- Snapshot Status ENUM (Task 11.2)
-- =====================================================

DROP TYPE IF EXISTS snapshot_status CASCADE;

CREATE TYPE snapshot_status AS ENUM (
    'active',
    'completed',
    'archived'
);

COMMENT ON TYPE snapshot_status IS
    'Evaluation snapshot status for Coach Chat lifecycle:
    - active: Chat available for conversation
    - completed: Chat finished by user
    - archived: Retention policy applied';
