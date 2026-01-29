# MentorMind - SQL Schema Corrections Summary

**Date:** 29 January 2026
**Status:** COMPLETED
**Task:** Comprehensive SQL schema correction to align with DB_SCHEMA.md

---

## Summary of Changes

This document summarizes the comprehensive corrections made to the MentorMind SQL schema to ensure alignment with the documented architecture in DB_SCHEMA.md.

### New Files Created

1. **`backend/schemas/00_enums.sql`** - ENUM type definitions
   - `metric_type`: 8 evaluation metrics (Truthfulness, Helpfulness, Safety, Bias, Clarity, Consistency, Efficiency, Robustness)
   - `difficulty_level`: 3 difficulty levels (easy, medium, hard)

2. **`backend/schemas/06_triggers.sql`** - Auto-update triggers
   - `update_updated_at_column()` function
   - Triggers on: question_prompts, questions, user_evaluations

### Modified Files

1. **`backend/schemas/01_question_prompts.sql`**
   - Added `is_active BOOLEAN NOT NULL DEFAULT TRUE`
   - Converted `primary_metric` from TEXT to `metric_type` ENUM
   - Converted `difficulty` from TEXT to `difficulty_level` ENUM
   - Added index on `is_active`

2. **`backend/schemas/02_questions.sql`**
   - Added `difficulty difficulty_level NOT NULL`
   - Converted `primary_metric` from TEXT to `metric_type` ENUM
   - Added index on `difficulty`
   - Updated composite index to include difficulty

3. **`backend/schemas/03_model_responses.sql`**
   - Removed `evaluation_id` field (eliminated circular dependency)

4. **`backend/schemas/04_user_evaluations.sql`**
   - Added `updated_at TIMESTAMP NOT NULL DEFAULT NOW()`

5. **`backend/schemas/05_judge_evaluations.sql`**
   - Converted `primary_metric` from TEXT to `metric_type` ENUM

### ORM Model Updates

1. **`backend/models/question_prompt.py`**
   - Added `is_active: Mapped[bool]` field
   - Removed relationship to avoid circular dependency

2. **`backend/models/question.py`**
   - Added `difficulty: Mapped[str]` field with SQLAlchemy Enum
   - Removed relationship to avoid circular dependency
   - Removed ForeignKey constraint (enforced at DB level)

3. **`backend/models/user_evaluation.py`**
   - Added `updated_at: Mapped[datetime]` field
   - Removed relationships to avoid circular dependency
   - Removed ForeignKey constraint (enforced at DB level)

4. **`backend/models/model_response.py`**
   - Removed ForeignKey constraint (enforced at DB level)
   - Removed relationships to avoid circular dependency

5. **`backend/models/judge_evaluation.py`**
   - Removed ForeignKey constraint (enforced at DB level)
   - Removed relationships to avoid circular dependency

### Pydantic Schema Updates

**`backend/models/schemas.py`**
- Added `is_active: bool` to `QuestionPromptBase`
- Added `difficulty: str` to `QuestionBase`
- Added `updated_at: datetime` to `UserEvaluationResponse`

---

## Technical Decisions

### 1. ENUM Types vs CHECK Constraints
**Decision:** Use PostgreSQL ENUM types
**Rationale:** 
- Type safety at database level
- Better performance (integer storage vs string comparison)
- Clearer intent in schema definition

### 2. Auto-update Triggers
**Decision:** Use PostgreSQL triggers for `updated_at`
**Rationale:**
- Automatic enforcement at database level
- Cannot be bypassed by application code
- Consistent behavior across all access methods

### 3. ORM Relationships Removed
**Decision:** Remove SQLAlchemy relationships to avoid circular dependency
**Rationale:**
- Circular dependencies between models caused import errors
- Foreign key constraints still enforced at database level
- Manual joins can be used when needed

### 4. evaluation_id Field Removed
**Decision:** Remove `evaluation_id` from model_responses table
**Rationale:**
- Created circular dependency (model_responses ↔ user_evaluations)
- Navigation should go: user_evaluations → model_responses (via response_id)
- Database integrity maintained by foreign key constraints

---

## Verification Results

All verification tests passed:

✅ ENUM types created with correct values
✅ New columns added (is_active, difficulty, updated_at)
✅ evaluation_id removed from model_responses
✅ Auto-update triggers working correctly
✅ ORM models functional with new fields
✅ Pydantic schemas validated successfully

---

## Migration Notes

For future deployments:
1. Run schema files in order: 00_enums.sql → 01-05 tables → 06_triggers.sql
2. No data migration needed (blank database)
3. ORM models updated to work without bi-directional relationships

---

## Files Modified

- `backend/schemas/00_enums.sql` (NEW)
- `backend/schemas/01_question_prompts.sql` (MODIFIED)
- `backend/schemas/02_questions.sql` (MODIFIED)
- `backend/schemas/03_model_responses.sql` (MODIFIED)
- `backend/schemas/04_user_evaluations.sql` (MODIFIED)
- `backend/schemas/05_judge_evaluations.sql` (MODIFIED)
- `backend/schemas/06_triggers.sql` (NEW)
- `backend/models/question_prompt.py` (MODIFIED)
- `backend/models/question.py` (MODIFIED)
- `backend/models/user_evaluation.py` (MODIFIED)
- `backend/models/model_response.py` (MODIFIED)
- `backend/models/judge_evaluation.py` (MODIFIED)
- `backend/models/schemas.py` (MODIFIED)

---

**Implementation completed:** 29 January 2026
**All tests passed:** ✅
