-- =====================================================
-- MentorMind - Auto-Update Triggers
-- Task: SQL Schema Correction
-- Description: PostgreSQL triggers to auto-update updated_at timestamp
-- =====================================================

-- Generic trigger function to auto-update updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_updated_at_column() IS
    'Generic trigger function to auto-update updated_at timestamp on UPDATE operations';

-- =====================================================
-- Triggers for each table with updated_at column
-- =====================================================

-- Trigger for question_prompts table
DROP TRIGGER IF EXISTS trigger_question_prompts_updated_at
    ON question_prompts;

CREATE TRIGGER trigger_question_prompts_updated_at
    BEFORE UPDATE ON question_prompts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for questions table
DROP TRIGGER IF EXISTS trigger_questions_updated_at
    ON questions;

CREATE TRIGGER trigger_questions_updated_at
    BEFORE UPDATE ON questions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for user_evaluations table
DROP TRIGGER IF EXISTS trigger_user_evaluations_updated_at
    ON user_evaluations;

CREATE TRIGGER trigger_user_evaluations_updated_at
    BEFORE UPDATE ON user_evaluations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
