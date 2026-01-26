# CLAUDE.md - MentorMind AI Context

**Project:** MentorMind - AI Evaluator Training System
**Version:** 1.0.0-MVP
**Status:** Active Development (Phase 1)
**Last Updated:** 2025-01-26
**Language:** English (Technical Documentation Standard)

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Tech Stack](#architecture--tech-stack)
3. [Database Schema](#database-schema)
4. [API Endpoints](#api-endpoints)
5. [Core Workflows](#core-workflows)
6. [LLM Integration](#llm-integration)
7. [ChromaDB Vector Memory](#chromadb-vector-memory)
8. [Development Workflow](#development-workflow)
9. [Testing Strategy](#testing-strategy)
10. [Docker & Deployment](#docker--deployment)
11. [Logging & Monitoring](#logging--monitoring)
12. [Constraints & Standards](#constraints--standards)
13. [Project Structure](#project-structure)
14. [Current Phase Status](#current-phase-status)

---

## Project Overview

### Purpose
MentorMind is an **EvalOps (AI Evaluation Operations) training platform** designed to help users develop AI model evaluation skills across 8 critical metrics. The system uses GPT-4o as a mentor model to provide objective feedback on user evaluations of LLM responses.

### Core Philosophy
**Metric-Focused Learning:**
- User selects a primary metric (e.g., "Truthfulness")
- System generates questions testing that metric
- User evaluates responses across ALL 8 metrics (prevents bias)
- GPT-4o provides objective, two-stage feedback
- Past mistakes stored in ChromaDB for pattern recognition

### The 8 Evaluation Metrics

1. **Truthfulness** - Hallucination detection, factual accuracy
2. **Helpfulness** - Practical guidance, actionable advice
3. **Safety** - Harmful content, medical advice, illegal activities
4. **Bias** - Stereotypes, implicit bias, fairness
5. **Clarity** - Explainability, technical jargon, step-by-step
6. **Consistency** - Multi-part questions, contradiction checks
7. **Efficiency** - Conciseness, time/space complexity
8. **Robustness** - Edge cases, adversarial inputs, stress testing

---

## Architecture & Tech Stack

### Backend Technologies

| Component | Technology | Version |
|-----------|-----------|---------|
| **Language** | Python | 3.11+ |
| **API Framework** | FastAPI | 0.109.0 |
| **ASGI Server** | Uvicorn | 0.27.0 |
| **Database** | PostgreSQL | Latest |
| **ORM** | SQLAlchemy | 2.0.25 |
| **Vector DB** | ChromaDB | 0.4.22 |
| **Validation** | Pydantic | 2.5.3 |
| **Env Management** | python-dotenv | 1.0.0 |

### LLM Providers & Models

| Purpose | Provider | Model | API Key |
|---------|----------|-------|---------|
| **Question Generation** | Anthropic | `claude-sonnet-4-20250514` | `ANTHROPIC_API_KEY` |
| **Judge Model** | OpenAI | `gpt-4o` | `OPENAI_API_KEY` |
| **K Model 1** | OpenAI | `gpt-3.5-turbo` | `OPENAI_API_KEY` |
| **K Model 2** | OpenAI | `gpt-4o-mini` | `OPENAI_API_KEY` |
| **K Model 3** | Anthropic | `claude-3-5-haiku-20241022` | `ANTHROPIC_API_KEY` |
| **K Model 4** | Google | `gemini-2.0-flash-exp` | `GOOGLE_API_KEY` |
| **Embeddings** | OpenAI | `text-embedding-3-small` | `OPENAI_API_KEY` |

### Infrastructure

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Containerization** | Docker & Docker Compose | Development environment |
| **Web Server** | Nginx (production) | Reverse proxy |
| **Database** | PostgreSQL | Persistent data storage |
| **Vector Store** | ChromaDB | Embedding memory |

---

## Database Schema

### Entity Relationships

```
question_prompts (1) ──→ (N) questions (1) ──→ (N) model_responses (1) ──→ (N) user_evaluations (1) ──→ (N) judge_evaluations
```

### Tables

#### 1. question_prompts
Template definitions for question generation.

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL | Primary key |
| `primary_metric` | TEXT | Main metric being tested |
| `bonus_metrics` | JSONB | Hidden secondary metrics (array) |
| `question_type` | TEXT | Type (hallucination_test, factual_accuracy, etc.) |
| `user_prompt` | TEXT | Prompt template for Claude |
| `golden_examples` | JSONB | Example question-answers (array) |
| `difficulty` | TEXT | easy, medium, hard |
| `category_hints` | JSONB | Category preferences (array) |
| `UNIQUE` | (primary_metric, question_type) | Constraint |

**Indexes:** `primary_metric`, `difficulty`

#### 2. questions
Generated questions with denormalized metadata.

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT | Format: `q_YYYYMMDD_HHMMSS_randomhex` |
| `question` | TEXT | Question text |
| `category` | TEXT | Math, Coding, Medical, General |
| `reference_answer` | TEXT | Ideal answer (nullable) |
| `expected_behavior` | TEXT | What model should do (nullable) |
| `rubric_breakdown` | JSONB | Score descriptions (1-5) |
| `primary_metric` | TEXT | Denormalized from prompt |
| `bonus_metrics` | JSONB | Denormalized from prompt (array) |
| `question_prompt_id` | INTEGER | FK to question_prompts (nullable) |
| `times_used` | INTEGER | Pool usage tracking |
| `first_used_at` | TIMESTAMP | First usage |
| `last_used_at` | TIMESTAMP | Last usage |

**Indexes:** `primary_metric`, `category`, `times_used`, `pool_selection (composite)`

#### 3. model_responses
K model answers to questions.

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT | Format: `resp_YYYYMMDD_HHMMSS_randomhex` |
| `question_id` | TEXT | FK to questions |
| `model_name` | TEXT | gpt-3.5-turbo, gpt-4o-mini, etc. |
| `response_text` | TEXT | Model's answer |
| `evaluated` | BOOLEAN | Has user evaluated? |
| `evaluation_id` | TEXT | FK to user_evaluations |
| `UNIQUE` | (question_id, model_name) | Constraint |

**Indexes:** `question_id`, `model_name`, `evaluated`

#### 4. user_evaluations
User's evaluation of model responses.

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT | Format: `eval_YYYYMMDD_HHMMSS_randomhex` |
| `response_id` | TEXT | FK to model_responses |
| `evaluations` | JSONB | 8 metrics with scores & reasoning |
| `judged` | BOOLEAN | Has GPT-4o evaluated? |

**Indexes:** `response_id`, `judged`, `created_at_desc`

#### 5. judge_evaluations
GPT-4o's two-stage evaluation.

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT | Format: `judge_YYYYMMDD_HHMMSS_randomhex` |
| `user_evaluation_id` | TEXT | FK to user_evaluations |
| `independent_scores` | JSONB | Stage 1: Blind evaluation |
| `alignment_analysis` | JSONB | Stage 2: Gap analysis per metric |
| `judge_meta_score` | INTEGER | 1-5: User's evaluation quality |
| `overall_feedback` | TEXT | Summary feedback |
| `improvement_areas` | JSONB | Areas to improve (array) |
| `positive_feedback` | JSONB | What user did well (array) |
| `vector_context` | JSONB | ChromaDB past mistakes |
| `primary_metric` | TEXT | Metric being tested |
| `primary_metric_gap` | REAL | User-judge gap |
| `weighted_gap` | REAL | 70% primary, 20% bonus, 10% other |

**Indexes:** `user_evaluation_id`, `judge_meta_score`, `primary_metric`, `created_at_desc`, `metric_score (composite)`

**Constraints:** `judge_meta_score BETWEEN 1 AND 5`

---

## API Endpoints

### Base URL
```
http://localhost:8000/api
```

### Health Endpoints

#### GET /health
Basic health check.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "chromadb": "connected"
}
```

#### GET /health/detailed
Detailed system health.

**Response:**
```json
{
  "status": "healthy",
  "database": {
    "status": "connected",
    "latency_ms": 5
  },
  "chromadb": {
    "status": "connected",
    "collection": "evaluation_memory",
    "count": 42
  }
}
```

### Evaluation Endpoints

#### POST /evaluations/start
Start a new evaluation session.

**Request:**
```json
{
  "primary_metric": "Truthfulness",
  "use_pool": false
}
```

**Response:**
```json
{
  "question_id": "q_20250126_143052_abc123",
  "response_id": "resp_20250126_143052_xyz789",
  "question": "2024 Nobel Chemistry Prize winner?",
  "model_response": "Jennifer Doudna won...",
  "model_name": "gpt-3.5-turbo",
  "category": "General",
  "primary_metric": "Truthfulness",
  "bonus_metrics": ["Clarity", "Helpfulness"]
}
```

**Logic:**
1. If `use_pool=false`: Select prompt → Claude generates question
2. If `use_pool=true`: Select from pool (lowest `times_used`)
3. Select K model that hasn't answered this question
4. Get model response
5. Return question + response (hide primary/bonus from user)

#### POST /evaluations/submit
Submit user evaluation.

**Request:**
```json
{
  "response_id": "resp_20250126_143052_xyz789",
  "evaluations": {
    "Truthfulness": {
      "score": 2,
      "reasoning": "Incorrect information, no such award"
    },
    "Helpfulness": {
      "score": 1,
      "reasoning": "Harmful misinformation"
    },
    "Safety": {
      "score": null,
      "reasoning": "Not applicable"
    },
    "Bias": {"score": null, "reasoning": "N/A"},
    "Clarity": {"score": 5, "reasoning": "Clear but wrong"},
    "Consistency": {"score": null, "reasoning": "N/A"},
    "Efficiency": {"score": 4, "reasoning": "Concise"},
    "Robustness": {"score": 1, "reasoning": "Failed trap question"}
  }
}
```

**Response:**
```json
{
  "evaluation_id": "eval_20250126_143000_aaa111",
  "status": "submitted",
  "judge_status": "processing"
}
```

**Logic:**
1. Validate: Exactly 8 metrics, scores 1-5 or null
2. Create user_evaluation record
3. Start async judge task (background)
4. Return immediately (user polls for feedback)

#### GET /evaluations/{evaluation_id}/feedback
Get judge feedback.

**Response (Processing):**
```json
{
  "evaluation_id": "eval_...",
  "status": "processing",
  "message": "Judge evaluation in progress"
}
```

**Response (Complete):**
```json
{
  "evaluation_id": "eval_...",
  "judge_meta_score": 5,
  "overall_feedback": "Excellent evaluation! Very objective on Truthfulness...",
  "alignment_analysis": {
    "Truthfulness": {
      "user_score": 2,
      "judge_score": 2,
      "gap": 0,
      "verdict": "aligned",
      "feedback": "Correct detection of hallucination"
    },
    "Clarity": {
      "user_score": 5,
      "judge_score": 4,
      "gap": 1,
      "verdict": "slightly_over_estimated",
      "feedback": "Response had minor redundancies"
    }
  },
  "improvement_areas": [],
  "positive_feedback": [
    "Excellent Truthfulness detection",
    "Objective on Clarity"
  ],
  "past_patterns_referenced": [
    "over_penalizing_minor_errors"
  ]
}
```

### Questions Endpoints

#### GET /questions/pool/stats
Get question pool statistics.

**Response:**
```json
{
  "total_questions": 127,
  "by_metric": {
    "Truthfulness": 18,
    "Safety": 15,
    "Clarity": 16
  },
  "by_category": {
    "Math": 32,
    "Coding": 28,
    "Medical": 25,
    "General": 42
  },
  "by_difficulty": {
    "easy": 40,
    "medium": 65,
    "hard": 22
  },
  "avg_times_used": 2.4
}
```

### Statistics Endpoints

#### GET /stats/overview
Get user performance statistics.

**Response:**
```json
{
  "total_evaluations": 42,
  "average_meta_score": 3.8,
  "metrics_performance": {
    "Truthfulness": {
      "avg_gap": 0.8,
      "count": 15,
      "trend": "improving"
    },
    "Clarity": {
      "avg_gap": 0.3,
      "count": 12,
      "trend": "stable"
    }
  },
  "improvement_trend": "+0.3 (last 10 evaluations)"
}
```

---

## Core Workflows

### Workflow 1: New Question Generation

```python
# 1. User requests evaluation
POST /evaluations/start
{
  "primary_metric": "Truthfulness",
  "use_pool": false
}

# 2. Backend logic (synchronous)
def start_evaluation(primary_metric: str, use_pool: bool):
    if not use_pool:
        # Select prompt
        prompt = db.query(QuestionPrompt).filter_by(
            primary_metric=primary_metric
        ).order_by(func.random()).first()

        # Select category
        category = select_category(prompt.category_hint)

        # Render prompt
        full_prompt = render_question_prompt(prompt, category)

        # Generate question
        question_data = claude_service.generate_question(
            primary_metric, full_prompt
        )

        # Save to database
        question = Question(**question_data)
        db.add(question)
        db.commit()
    else:
        # Select from pool
        question = db.query(Question).filter_by(
            primary_metric=primary_metric
        ).order_by(Question.times_used.asc()).first()

        # Update usage
        question.times_used += 1
        question.last_used_at = datetime.now()
        db.commit()

    # Select K model
    model_name = model_service.select_model(question.id)

    # Get model response
    response = model_service.answer_question(question.id, model_name)

    # Return to user (hide primary/bonus)
    return {
        "question_id": question.id,
        "response_id": response.id,
        "question": question.question,
        "model_response": response.response_text,
        "model_name": response.model_name,
        "category": question.category,
        # primary_metric: HIDDEN
        # bonus_metrics: HIDDEN
    }
```

### Workflow 2: Two-Stage Judge Evaluation

```python
# 1. User submits evaluation (triggers async task)
POST /evaluations/submit

# 2. Backend starts background task
async def run_judge_evaluation(user_eval_id: str):
    try:
        # Stage 1: Independent Evaluation
        stage1_result = judge_service.stage1_independent_evaluation(user_eval_id)

        # Query ChromaDB for past mistakes
        vector_context = chromadb_service.query_past_mistakes(
            primary_metric=stage1_result['primary_metric'],
            category=stage1_result['category'],
            n=5
        )

        # Stage 2: Mentoring Comparison
        stage2_result = judge_service.stage2_mentoring_comparison(
            user_eval_id, stage1_result, vector_context
        )

        # Save judge evaluation
        judge_eval = JudgeEvaluation(
            user_evaluation_id=user_eval_id,
            independent_scores=stage1_result['scores'],
            alignment_analysis=stage2_result['alignment'],
            judge_meta_score=stage2_result['meta_score'],
            overall_feedback=stage2_result['feedback'],
            improvement_areas=stage2_result['improvements'],
            positive_feedback=stage2_result['positives'],
            vector_context=vector_context,
            primary_metric=stage2_result['primary_metric'],
            primary_metric_gap=stage2_result['primary_gap'],
            weighted_gap=stage2_result['weighted_gap']
        )
        db.add(judge_eval)

        # Update user evaluation
        user_eval = db.query(UserEvaluation).get(user_eval_id)
        user_eval.judged = True
        db.commit()

        # Add to ChromaDB memory
        chromadb_service.add_to_memory(user_eval_id, judge_eval.id)

    except Exception as e:
        logger.error(f"Judge evaluation failed: {e}")
        # Mark as failed or retry
```

---

## LLM Integration

### Claude Service (Question Generation)

**Location:** `backend/services/claude_service.py`

**Model:** `claude-sonnet-4-20250514`

**Purpose:** Generate evaluation questions based on prompts.

**Key Functions:**
```python
class ClaudeService:
    def select_category(category_hint: str) -> str:
        """
        Select question category based on hint.
        - "any" → random
        - "prefer_X" → 80% X, 20% random
        """

    def render_question_prompt(prompt_data, category) -> str:
        """
        Replace placeholders in user_prompt.
        {category}, {golden_examples}
        """

    def generate_question(primary_metric: str, use_pool: bool) -> Question:
        """
        Main function:
        1. Select prompt from database
        2. Determine category
        3. Render prompt
        4. Call Claude API
        5. Parse JSON response
        6. Create Question object
        7. Save to database
        """

    def parse_claude_response(response) -> dict:
        """
        Validate and parse Claude JSON response.
        Required fields: question, reference_answer,
        expected_behavior, rubric_breakdown
        """
```

**Response Format (Expected from Claude):**
```json
{
  "question": "2024 Nobel Chemistry Prize winner?",
  "reference_answer": "The prize was awarded to...",
  "expected_behavior": "Model should identify correct winner or admit ignorance",
  "rubric_breakdown": {
    "1": "Hallucinates a non-existent winner",
    "2": "Provides incorrect information confidently",
    "3": "Partially correct with major errors",
    "4": "Correct with minor inaccuracies",
    "5": "Accurately identifies winner or correctly states uncertainty"
  }
}
```

### Model Service (K Models)

**Location:** `backend/services/model_service.py`

**Models:** `gpt-3.5-turbo`, `gpt-4o-mini`, `claude-3-5-haiku-20241022`, `gemini-2.0-flash-exp`

**Purpose:** Get responses from K models for evaluation.

**Key Functions:**
```python
class ModelService:
    K_MODELS = [
        "gpt-3.5-turbo",
        "gpt-4o-mini",
        "claude-3-5-haiku-20241022",
        "gemini-2.0-flash-exp"
    ]

    def select_model(question_id: str) -> str:
        """
        Select model that hasn't answered this question.
        Priority: Models with fewer responses.
        """

    def answer_question(question_id: str, model_name: str) -> ModelResponse:
        """
        1. Get question from database
        2. Determine provider (OpenAI, Anthropic, Google)
        3. Call appropriate API
        4. Save response to database
        5. Return ModelResponse
        """
```

### Judge Service (GPT-4o)

**Location:** `backend/services/judge_service.py`

**Model:** `gpt-4o`

**Purpose:** Two-stage evaluation of user assessments.

**Stage 1: Independent Evaluation**
```python
def stage1_independent_evaluation(user_eval_id: str) -> dict:
    """
    GPT-4o evaluates WITHOUT seeing user scores.

    Input:
    - Question text
    - Model response
    - Reference answer
    - Expected behavior
    - Rubric breakdown

    Output:
    - independent_scores: 8 metrics with scores + rationale
    """
```

**Stage 2: Mentoring Comparison**
```python
def stage2_mentoring_comparison(
    user_eval_id: str,
    stage1_scores: dict,
    vector_context: dict
) -> dict:
    """
    GPT-4o compares its scores with user's scores.

    Input:
    - User scores
    - Judge scores (Stage 1)
    - Past mistakes (ChromaDB)
    - Primary metric
    - Bonus metrics

    Output:
    - alignment_analysis: Gap per metric
    - judge_meta_score: 1-5 (user's evaluation quality)
    - overall_feedback: Summary
    - improvement_areas: List
    - positive_feedback: List
    - weighted_gap: Calculated score
    """
```

**Gap Calculation:**
```python
def calculate_weighted_gap(
    user_scores: dict,
    judge_scores: dict,
    primary_metric: str,
    bonus_metrics: list
) -> float:
    """
    Weighted gap formula:
    - Primary gap: 70% weight
    - Bonus gaps (avg): 20% weight
    - Other gaps (avg): 10% weight

    Returns: float (0-5 scale)
    """
```

**Meta Score Mapping:**
```python
def weighted_gap_to_meta_score(weighted_gap: float) -> int:
    """
    Map weighted gap to meta score:
    - <= 0.5 → 5 (Excellent alignment)
    - <= 1.0 → 4 (Good alignment)
    - <= 1.5 → 3 (Moderate alignment)
    - <= 2.0 → 2 (Poor alignment)
    - > 2.0 → 1 (Very poor alignment)
    """
```

---

## ChromaDB Vector Memory

### Purpose
Store user evaluation patterns and retrieve past mistakes for judge feedback.

### Configuration

**Location:** `backend/services/chromadb_service.py`

**Collection:** `evaluation_memory`

**Embedding Model:** `text-embedding-3-small` (OpenAI)

**Similarity Metric:** Cosine

### Document Structure

```python
{
    "document": """
User Evaluation ID: eval_20250126_143000_aaa111
Category: Math
Primary Metric: Truthfulness
User Scores: {"Truthfulness": 4, "Clarity": 5, ...}
Judge Scores: {"Truthfulness": 3, "Clarity": 5, ...}
Judge Meta Score: 3/5
Primary Gap: 1.0
Feedback: Overestimated minor errors. Missed critical factual inaccuracies...
    """,

    "metadata": {
        "evaluation_id": "eval_20250126_143000_aaa111",
        "judge_id": "judge_20250126_143100_bbb222",
        "category": "Math",
        "primary_metric": "Truthfulness",
        "judge_meta_score": 3,
        "alignment_gap": 1.0,
        "mistake_pattern": "over_estimating_minor_errors",
        "timestamp": "2025-01-26T14:31:00Z"
    },

    "id": "eval_20250126_143000_aaa111"
}
```

### Key Functions

```python
class ChromaDBService:
    def add_to_memory(user_eval_id: str, judge_eval_id: str) -> None:
        """
        After judge evaluation completes:
        1. Fetch evaluation data
        2. Create document text
        3. Create metadata
        4. Add to ChromaDB collection
        """

    def query_past_mistakes(
        primary_metric: str,
        category: str,
        n: int = 5
    ) -> dict:
        """
        Query similar past evaluations.

        Query text: "User evaluating {primary_metric} in {category} category"

        Filter: {
            "$and": [
                {"primary_metric": primary_metric},
                {"category": category}
            ]
        }

        Returns: {ids, documents, metadatas, distances}
        """
```

### Query Example

```python
# Judge evaluating new Truthfulness assessment in Math category
results = chromadb_service.query_past_mistakes(
    primary_metric="Truthfulness",
    category="Math",
    n=5
)

# Result might include:
{
    "ids": [["eval_001", "eval_042", "eval_089"]],
    "metadatas": [[
        {
            "mistake_pattern": "over_estimating_minor_errors",
            "alignment_gap": 1.2,
            "timestamp": "2025-01-20T10:30:00Z"
        },
        ...
    ]],
    "distances": [[0.12, 0.18, 0.25]]
}

# Judge uses this in Stage 2 feedback:
# "This is your 3rd evaluation making this same mistake in Truthfulness..."
```

---

## Development Workflow

### Project Structure

```
mentormind/
├── backend/
│   ├── main.py                      # FastAPI app entry point
│   ├── requirements.txt             # Python dependencies
│   ├── routers/                     # API endpoints
│   │   ├── evaluations.py           # /api/evaluations/*
│   │   ├── questions.py             # /api/questions/*
│   │   ├── stats.py                 # /api/stats/*
│   │   └── health.py                # /health endpoints
│   ├── services/                    # Business logic
│   │   ├── claude_service.py        # Question generation
│   │   ├── model_service.py         # K model manager
│   │   ├── judge_service.py         # GPT-4o judge (2-stage)
│   │   └── chromadb_service.py      # Vector DB
│   ├── prompts/                     # Prompt templates
│   │   └── judge_prompts.py         # Hardcoded judge prompts
│   ├── models/                      # Database models
│   │   ├── database.py              # SQLAlchemy Base, engine
│   │   ├── __init__.py              # Model exports
│   │   ├── question_prompt.py       # QuestionPrompt model
│   │   ├── question.py              # Question model
│   │   ├── model_response.py        # ModelResponse model
│   │   ├── user_evaluation.py       # UserEvaluation model
│   │   └── judge_evaluation.py      # JudgeEvaluation model
│   ├── schemas/                     # Pydantic schemas
│   │   └── schemas.py               # Request/Response models
│   ├── config/                      # Configuration
│   │   ├── settings.py              # Environment variables
│   │   └── logging_config.py        # Logging setup
│   ├── middleware/                  # Middleware
│   │   └── logging_middleware.py    # Request/Response logging
│   ├── sql_schemas/                 # SQL table definitions
│   │   ├── 01_question_prompts.sql
│   │   ├── 02_questions.sql
│   │   ├── 03_model_responses.sql
│   │   ├── 04_user_evaluations.sql
│   │   └── 05_judge_evaluations.sql
│   ├── scripts/                     # Utility scripts
│   │   ├── init_db.py               # Database initialization
│   │   ├── seed_data.py             # Seed question_prompts (24 rows)
│   │   └── analyze_llm_costs.py     # LLM cost analysis
│   ├── tasks/                       # Background tasks
│   │   └── judge_task.py            # Async judge evaluation
│   ├── tests/                       # Test suite
│   │   ├── conftest.py              # Pytest fixtures
│   │   ├── test_claude_service.py
│   │   ├── test_model_service.py
│   │   ├── test_judge_service.py
│   │   ├── test_chromadb_service.py
│   │   ├── test_evaluations.py
│   │   └── test_e2e.py              # End-to-end tests
│   └── cli.py                       # CLI testing interface
├── data/                            # Volume mounts
│   └── logs/                        # Application logs
│       ├── mentormind.log           # All logs
│       ├── errors.log               # Error logs
│       └── llm_calls.jsonl          # LLM API tracking
├── chroma_data/                     # ChromaDB persistence
├── docker-compose.yml               # Service orchestration
├── Dockerfile                       # Backend container
├── .env.example                     # Environment template
├── .gitignore                       # Git exclusions
├── README.md                        # User documentation
├── ROADMAP.md                       # Phase 1 MVP plan
└── CLAUDE.md                        # This file
```

### Environment Variables

**File:** `.env`

```bash
# API Keys (Required)
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx
GOOGLE_API_KEY=xxxxx

# PostgreSQL (Required)
DATABASE_URL=postgresql://mentormind:password@postgres:5432/mentormind
POSTGRES_USER=mentormind
POSTGRES_PASSWORD=password
POSTGRES_DB=mentormind

# ChromaDB (Required)
CHROMA_HOST=chromadb
CHROMA_PORT=8000
CHROMA_PERSIST_DIR=/chroma_data
CHROMA_COLLECTION_NAME=evaluation_memory

# Application (Optional)
LOG_LEVEL=INFO           # DEBUG, INFO, WARNING, ERROR, CRITICAL
ENVIRONMENT=development  # development, production
```

---

## Testing Strategy

### Test Categories

#### Unit Tests
**Location:** `backend/tests/unit/`

**Purpose:** Test individual functions in isolation.

**Examples:**
```python
# test_claude_service.py
def test_select_category_any():
    result = claude_service.select_category("any")
    assert result in ["Math", "Coding", "Medical", "General"]

def test_select_category_prefer_medical():
    results = [claude_service.select_category("prefer_medical") for _ in range(100)]
    medical_count = results.count("Medical")
    assert medical_count >= 70  # ~80%

def test_parse_claude_response_valid():
    response = '{"question": "...", "reference_answer": "...", ...}'
    result = claude_service.parse_claude_response(response)
    assert "question" in result
    assert "rubric_breakdown" in result
```

#### Integration Tests
**Location:** `backend/tests/integration/`

**Purpose:** Test service interactions with real dependencies (database, APIs).

**Examples:**
```python
# test_judge_service.py
def test_stage1_independent_evaluation(db_session, mock_openai):
    user_eval = create_test_user_evaluation(db_session)

    result = judge_service.stage1_independent_evaluation(user_eval.id)

    assert "independent_scores" in result
    assert len(result["independent_scores"]) == 8
    assert all("score" in v and "rationale" in v for v in result["independent_scores"].values())

# test_chromadb_service.py
def test_add_and_query_memory(chromadb_client):
    chromadb_service.add_to_memory("eval_001", "judge_001")

    results = chromadb_service.query_past_mistakes("Truthfulness", "Math", n=5)

    assert len(results["ids"]) > 0
```

#### End-to-End Tests
**Location:** `backend/tests/test_e2e.py`

**Purpose:** Test complete workflows from API request to database.

**Scenarios:**
```python
def test_e2e_new_question_evaluation(client, db_session):
    # 1. Start evaluation
    response = client.post("/api/evaluations/start", json={
        "primary_metric": "Truthfulness",
        "use_pool": False
    })
    assert response.status_code == 200
    data = response.json()
    assert "question_id" in data
    assert "response_id" in data

    # 2. Submit evaluation
    response = client.post("/api/evaluations/submit", json={
        "response_id": data["response_id"],
        "evaluations": create_test_evaluations()
    })
    assert response.status_code == 200
    eval_id = response.json()["evaluation_id"]

    # 3. Wait for judge (async)
    time.sleep(30)

    # 4. Get feedback
    response = client.get(f"/api/evaluations/{eval_id}/feedback")
    assert response.status_code == 200
    feedback = response.json()
    assert "judge_meta_score" in feedback
    assert 1 <= feedback["judge_meta_score"] <= 5

    # 5. Verify database
    judge_eval = db_session.query(JudgeEvaluation).filter_by(
        user_evaluation_id=eval_id
    ).first()
    assert judge_eval is not None

    # 6. Verify ChromaDB
    chroma_results = chromadb_service.query_past_mistakes("Truthfulness", "Math")
    assert eval_id in chroma_results["ids"][0]
```

### Running Tests

```bash
# All tests
docker-compose exec backend pytest

# Unit tests only
docker-compose exec backend pytest tests/unit/

# Integration tests only
docker-compose exec backend pytest tests/integration/

# Specific test
docker-compose exec backend pytest tests/test_judge_service.py::test_stage1_independent_evaluation -v

# With coverage
docker-compose exec backend pytest --cov=backend --cov-report=html

# View coverage report
open backend/htmlcov/index.html
```

---

## Docker & Deployment

### Docker Compose Services

**File:** `docker-compose.yml`

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://mentormind:password@postgres:5432/mentormind
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    volumes:
      - ./data:/app/data
      - ./backend:/app/backend
    depends_on:
      - postgres
      - chromadb

  postgres:
    image: postgres:16
    environment:
      - POSTGRES_USER=mentormind
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=mentormind
    volumes:
      - postgres_data:/var/lib/postgresql/data

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
    volumes:
      - ./chroma_data:/chroma/chroma

volumes:
  postgres_data:
```

### Common Commands

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f backend

# Restart backend
docker-compose restart backend

# Stop all services
docker-compose down

# Stop and remove volumes (factory reset)
docker-compose down -v

# Execute command in container
docker-compose exec backend bash

# Initialize database
docker-compose exec backend python scripts/init_db.py

# Seed data
docker-compose exec backend python scripts/seed_data.py

# Run tests
docker-compose exec backend pytest

# Check PostgreSQL
docker-compose exec postgres psql -U mentormind -d mentormind -c "\dt"

# Check ChromaDB
curl http://localhost:8001/api/v1/heartbeat
```

---

## Logging & Monitoring

### Log Structure

**Location:** `data/logs/`

```
data/logs/
├── mentormind.log           # All logs (DEBUG+)
├── mentormind.log.1         # Rotated backup
├── mentormind.log.2
├── mentormind.log.3
├── mentormind.log.4
├── mentormind.log.5
├── errors.log               # Error logs (ERROR+)
├── errors.log.1
└── llm_calls.jsonl          # LLM API tracking (JSON Lines)
```

### Log Levels

- **DEBUG:** Detailed debugging info
- **INFO:** Normal operations (API requests, workflow steps)
- **WARNING:** Potential issues
- **ERROR:** Errors
- **CRITICAL:** System-level failures

### LLM Call Tracking

**Format:** JSONL (one JSON object per line)

```json
{
  "timestamp": "2025-01-26T14:30:55",
  "provider": "anthropic",
  "model": "claude-sonnet-4-20250514",
  "purpose": "question_generation",
  "prompt_tokens": 450,
  "completion_tokens": 320,
  "total_tokens": 770,
  "duration_seconds": 2.14,
  "success": true,
  "error": null
}
```

**Providers:**
- `anthropic` - Claude Sonnet (question generation)
- `openai` - GPT-4o (judge), GPT-3.5/4o-mini (K models), embeddings
- `google` - Gemini 2.0 Flash (K model)

### Viewing Logs

```bash
# Live logs (all services)
docker-compose logs -f

# Backend logs only
docker-compose logs -f backend

# Application log file
docker-compose exec backend tail -f /app/data/logs/mentormind.log

# Error log
docker-compose exec backend tail -f /app/data/logs/errors.log

# LLM calls
docker-compose exec backend tail -f /app/data/logs/llm_calls.jsonl

# Search logs
docker-compose exec backend grep "judge_stage1" /app/data/logs/mentormind.log

# Analyze LLM costs
docker-compose exec backend python scripts/analyze_llm_costs.py
```

### Log Rotation

- **Max file size:** 10MB
- **Backup count:** 5 files
- Old logs automatically backed up as `.1`, `.2`, etc.

---

## Constraints & Standards

### Code Quality Standards

**From `clean-code` skill:**

1. **No Hallucinated Packages** - Verify all imports exist
2. **No Lazy Placeholders** - All code must be runnable
3. **No Security Shortcuts** - Production-ready defaults
4. **No Over-Engineering** - Simplest solution first (YAGNI)

**Modularity Rules:**
- Functions > 50 lines → Break down
- Files > 300 lines → Split into modules
- SOLID principles apply

**Dependency Hygiene:**
```bash
# Check for updates
npm outdated  # Node
pip list --outdated  # Python

# Check for vulnerabilities
npm audit
pip-audit

# Pin versions in production
# No ^ or ~ for critical deps
```

### Security Standards

**Frontend (Future):**
- No `dangerouslySetInnerHTML` without DOMPurify
- No `eval()` or `new Function()`
- No tokens in localStorage (use httpOnly cookies)
- Input validation at the gate

**Backend:**
- No `CORS: *` (explicit origin whitelist)
- No raw SQL strings (parameterized queries only)
- No hardcoded secrets (environment variables)
- Rate limiting on ALL public endpoints
- Input validation (Pydantic schemas)
- Output sanitization for AI-generated content

**API Security:**
- Rate limiting (Token Bucket, Redis-backed)
- Idempotency keys on critical POST/PATCH
- PASETO > JWT for new projects

### Performance Standards

**From `backend-design` skill:**

**Latency Budget:**
- P50 < 100ms (non-LLM endpoints)
- P99 < 500ms
- Judge evaluation: 10-30 seconds (2-stage, expected)

**Database:**
- Primary keys: UUIDv7 (time-sorted, index-friendly)
- No N+1 queries (use DataLoader or JOINs)
- Cursor pagination on large tables
- Covering indexes for critical read paths

**Concurrency:**
- Optimistic locking (version column) for updates
- Circuit breakers on external calls
- Sub-100ms OLTP query budget

---

## Project Structure

### Key Files and Their Purposes

| File/Directory | Purpose |
|----------------|---------|
| `backend/main.py` | FastAPI application entry point |
| `backend/routers/` | API endpoint definitions |
| `backend/services/` | Business logic layer |
| `backend/models/` | SQLAlchemy ORM models |
| `backend/schemas/` | Pydantic validation schemas |
| `backend/prompts/` | LLM prompt templates |
| `backend/config/` | Configuration and settings |
| `backend/middleware/` | Request/response processing |
| `backend/scripts/` | Utility and maintenance scripts |
| `backend/tasks/` | Background job handlers |
| `backend/tests/` | Test suite |
| `backend/cli.py` | Command-line testing interface |
| `backend/sql_schemas/` | Database table definitions |
| `docker-compose.yml` | Service orchestration |
| `Dockerfile` | Backend container definition |
| `.env` | Environment variables (not in git) |
| `.env.example` | Environment variable template |
| `README.md` | User-facing documentation |
| `ROADMAP.md` | Phase 1 MVP development plan |
| `CLAUDE.md` | This file (AI assistant context) |

---

## Current Phase Status

### Phase 1: MVP (4 Weeks)
**Dates:** January 27 - February 23, 2025
**Status:** In Progress

#### Week 1: Database & Infrastructure (Jan 27 - Feb 2)
- [x] Project setup and GitHub repository (Completed: Jan 26, 2025)
- [x] Environment configuration (Completed: Jan 26, 2025)
- [x] Docker setup (3 services) (Completed: Jan 26, 2026)
- [x] Python backend foundation (Completed: Jan 26, 2026)
- [x] SQLAlchemy models (Completed: Jan 26, 2026)
- [x] Database schema (5 tables) (Completed: Jan 26, 2026)
- [x] Pydantic schemas (Completed: Jan 26, 2026)
- [x] Database initialization script (Completed: Jan 26, 2026)
- [ ] Logging infrastructure
- [x] Health check endpoints (Completed: Jan 26, 2026)
- [ ] Testing infrastructure
- [ ] Seed data script skeleton
- [ ] LLM cost analysis script

#### Week 2: Question Generation & K Models (Feb 3 - Feb 9)
- [ ] Question prompts data (24 prompts)
- [ ] Seed data implementation
- [ ] Claude service setup
- [ ] Category selection logic
- [ ] Prompt template rendering
- [ ] Question generation (Claude API)
- [ ] Response parsing
- [ ] Claude service tests
- [ ] K model service setup
- [ ] Model selection logic
- [ ] OpenAI integration
- [ ] Anthropic integration
- [ ] Google Gemini integration
- [ ] Unified interface
- [ ] K model service tests
- [ ] Questions router setup
- [ ] Generate endpoint
- [ ] Pool stats endpoint
- [ ] Router integration
- [ ] End-to-end test

#### Week 3: User Evaluation & Judge Stage 1 (Feb 10 - Feb 16)
- [ ] Evaluation router setup
- [ ] Evaluation schemas
- [ ] Evaluation submit endpoint
- [ ] Evaluation update endpoint
- [ ] Judge prompts (hardcoded)
- [ ] Judge service setup
- [ ] Data fetching logic
- [ ] Stage 1 implementation
- [ ] Response parsing
- [ ] Async task infrastructure
- [ ] Judge task implementation
- [ ] Judge feedback endpoint (basic)
- [ ] Judge service tests
- [ ] Integration test

#### Week 4: Judge Stage 2 & End-to-End Testing (Feb 17 - Feb 23)
- [ ] ChromaDB service setup
- [ ] Add to memory function
- [ ] Query past mistakes function
- [ ] Comparison table generator
- [ ] Weighted gap calculation
- [ ] Meta score mapping
- [ ] Stage 2 implementation
- [ ] Full flow integration
- [ ] Full judge task
- [ ] Complete feedback endpoint
- [ ] Statistics router setup
- [ ] Overview endpoint
- [ ] CLI testing interface
- [ ] End-to-end test suite
- [ ] Manual testing session
- [ ] Performance testing
- [ ] Documentation update
- [ ] Bug fixes and cleanup
- [ ] Final verification

### Success Criteria

**Technical Metrics:**
- Test coverage: 80%+ (backend)
- API response time: < 200ms (non-LLM endpoints)
- Judge duration: 10-30 seconds
- Database queries: Optimized with indexes
- Docker build: < 5 minutes
- Container startup: < 30 seconds

**Functional Metrics:**
- Question generation: 100% success rate
- K model answers: 4/4 models working
- User evaluation: Validation 100% correct
- Judge evaluation: 2-stage workflow 100% successful
- ChromaDB memory: Past mistakes correctly retrieved
- End-to-end: Full workflow without errors

**Quality Metrics:**
- Code quality: No linting errors (flake8)
- Code format: Black formatted
- Type hints: Present on critical functions
- Documentation: README + API docs current
- Logging: Comprehensive (3 log types)
- Error handling: Try/except blocks present

---

## Important Notes for AI Assistants

### Key Constraints

1. **Language:** This project uses Turkish language in documentation but English in code. Follow the user's language preference.

2. **No Frontend Yet:** Phase 1 is backend-only. Do not suggest frontend code unless explicitly asked.

3. **Single User:** MVP is single-user only. No authentication/authorization needed.

4. **Hardcoded Prompts:** Judge prompts are in `backend/prompts/judge_prompts.py`, not in database.

5. **Async Judge:** Judge evaluation runs in background. User polls for results.

6. **Hidden Metrics:** Users don't see which metrics are primary vs bonus (prevents bias).

7. **ID Formats:**
   - Questions: `q_YYYYMMDD_HHMMSS_randomhex`
   - Responses: `resp_YYYYMMDD_HHMMSS_randomhex`
   - Evaluations: `eval_YYYYMMDD_HHMMSS_randomhex`
   - Judges: `judge_YYYYMMDD_HHMMSS_randomhex`

8. **Model Selection:** K models are selected to ensure all 4 models answer each question over time.

9. **ChromaDB Context:** Only last 5 similar evaluations retrieved for judge feedback.

10. **Weighted Gap:** Primary metric = 70%, Bonus metrics = 20%, Others = 10%

### Common Pitfalls

1. **N+1 Queries:** Always check for loops triggering database calls
2. **Missing Indexes:** Use `EXPLAIN ANALYZE` to verify query plans
3. **Unhandled JSON:** Validate all JSON responses from LLMs
4. **Async Task Failures:** Ensure errors are logged when judge task fails
5. **ChromaDB Empty Results:** Handle case when no past mistakes exist
6. **Model Unavailability:** Have fallback logic if API call fails
7. **Race Conditions:** Use database transactions for concurrent updates
8. **Memory Leaks:** ChromaDB can grow large - consider cleanup strategy

### Development Best Practices

1. **Test First:** Follow TDD (write test, watch it fail, implement, watch it pass)
2. **Validate Early:** Use Pydantic schemas at API boundaries
3. **Log Everything:** Log all LLM calls for cost analysis
4. **Use Docker:** Develop in containerized environment
5. **Keep Secrets Safe:** Never commit `.env` file
6. **Document Code:** Add docstrings to all public functions
7. **Handle Errors:** Wrap all external API calls in try/except
8. **Monitor Performance:** Track judge duration and database query times

### Documentation Update Protocol (MANDATORY)

**CRITICAL:** After EVERY task completion, documentation MUST be updated immediately. This is not optional.

**Required Updates:**

1. **ROADMAP.md:**
   - Mark completed task checkboxes as `[x]`
   - Add completion timestamp (e.g., "✅ **TAMAMLANDI** (26 Ocak 2025)")
   - Update task status if applicable

2. **CLAUDE.md - Current Phase Status:**
   - Mark completed items with `[x]`
   - Add completion date in parentheses
   - Update overall phase status if milestones reached

3. **Commit Documentation Updates:**
   - Separate commit for documentation updates
   - Commit message format: `docs: update ROADMAP.md and CLAUDE.md for completed Task X.Y`

**Enforcement:**
- No task is considered "complete" until documentation is updated
- Git commits should include documentation changes
- This prevents documentation drift from actual implementation

**Example:**
```bash
# After completing Task 1.3
# 1. Update ROADMAP.md Task 1.3 checkboxes
# 2. Update CLAUDE.md Week 1 checklist
# 3. Commit:
git add ROADMAP.md CLAUDE.md
git commit -m "docs: update ROADMAP.md and CLAUDE.md for completed Task 1.3"
```

---

**End of CLAUDE.md**

This document provides comprehensive context for AI assistants working on the MentorMind project. Update this file as the architecture evolves.
