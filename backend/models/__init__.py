"""
MentorMind - Database Models Package

SQLAlchemy ORM models for MentorMind database.
"""

from backend.models.database import Base, engine, SessionLocal, get_db, test_database_connection
from backend.models.question_prompt import QuestionPrompt
from backend.models.question import Question
from backend.models.model_response import ModelResponse, K_MODELS
from backend.models.user_evaluation import UserEvaluation
from backend.models.judge_evaluation import JudgeEvaluation
from backend.models.evaluation_snapshot import EvaluationSnapshot
from backend.models.chat_message import ChatMessage

__all__ = [
    # Database
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    "test_database_connection",
    # Models
    "QuestionPrompt",
    "Question",
    "ModelResponse",
    "K_MODELS",
    "UserEvaluation",
    "JudgeEvaluation",
    # Coach Chat Models (Task 11.4)
    "EvaluationSnapshot",
    "ChatMessage",
]
