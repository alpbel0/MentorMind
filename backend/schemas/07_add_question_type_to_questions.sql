-- =====================================================
-- MentorMind - Question Type Denormalization
-- Task: Add question_type to questions table
-- Description: Migrate question_type from question_prompts to questions for query performance
-- =====================================================

-- Add question_type column (nullable for backward compatibility)
ALTER TABLE questions ADD COLUMN IF NOT EXISTS question_type TEXT;

-- Migrate existing data from question_prompts
UPDATE questions q
SET question_type = qp.question_type
FROM question_prompts qp
WHERE q.question_prompt_id = qp.id
  AND q.question_type IS NULL;

-- Add index for query performance
CREATE INDEX IF NOT EXISTS idx_questions_question_type
    ON questions (question_type);

-- Add comment
COMMENT ON COLUMN questions.question_type IS
    'Question type denormalized from question_prompts for query performance (e.g., hallucination_test, factual_accuracy)';
