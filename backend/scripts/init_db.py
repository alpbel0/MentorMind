"""
Database Initialization Script

Executes SQL schema files to create MentorMind database tables.

Usage:
    python scripts/init_db.py              # Create all tables
    python scripts/init_db.py --verify     # Verify tables exist
    python scripts/init_db.py --drop       # Drop all tables first (DESTRUCTIVE)
"""

import argparse
import logging
import sys
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from backend.config.settings import settings
from backend.models.database import engine

logger = logging.getLogger(__name__)

# =====================================================
# SQL Schema Files (in execution order)
# =====================================================

SCHEMA_FILES = [
    "00_enums.sql",
    "01_question_prompts.sql",
    "02_questions.sql",
    "03_model_responses.sql",
    "04_user_evaluations.sql",
    "05_judge_evaluations.sql",
    "06_triggers.sql",
]
"""SQL schema files to execute in order"""

SCHEMA_DIR = Path(__file__).parent.parent / "schemas"
"""Directory containing SQL schema files"""


# =====================================================
# Schema File Reading
# =====================================================

def read_schema_file(filename: str) -> str:
    """
    Read SQL schema file content.

    Args:
        filename: Name of the schema file (e.g., '01_question_prompts.sql')

    Returns:
        SQL content as string

    Raises:
        FileNotFoundError: If schema file doesn't exist
    """
    file_path = SCHEMA_DIR / filename
    if not file_path.exists():
        raise FileNotFoundError(f"Schema file not found: {file_path}")
    return file_path.read_text()


# =====================================================
# Schema Execution
# =====================================================

def execute_schema_file(filename: str) -> bool:
    """
    Execute a single schema file.

    Args:
        filename: Name of the schema file to execute

    Returns:
        True if successful, False otherwise
    """
    try:
        sql_content = read_schema_file(filename)
        with engine.begin() as conn:
            conn.execute(text(sql_content))
        logger.info(f"✓ Executed: {filename}")
        return True
    except SQLAlchemyError as e:
        logger.error(f"✗ Failed: {filename} - {e}")
        return False


def execute_all_schemas() -> bool:
    """
    Execute all schema files in order.

    Returns:
        True if all successful, False otherwise
    """
    success = True
    for filename in SCHEMA_FILES:
        if not execute_schema_file(filename):
            success = False
            break
    return success


# =====================================================
# Table Management
# =====================================================

def drop_all_tables() -> bool:
    """
    Drop all tables (DESTRUCTIVE).

    Drops tables in reverse order due to foreign key constraints.

    Returns:
        True if successful, False otherwise
    """
    try:
        with engine.begin() as conn:
            # Drop in reverse order due to foreign keys
            for filename in reversed(SCHEMA_FILES):
                table_name = filename.replace("0", "").replace("_", " ").replace(".sql", "").strip()
                # Handle the "1" -> "questionprompts" conversion
                table_name = filename.split("_", 1)[1].replace(".sql", "")
                conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
        logger.warning("⚠ All tables dropped")
        return True
    except SQLAlchemyError as e:
        logger.error(f"✗ Failed to drop tables: {e}")
        return False


# =====================================================
# Table Verification
# =====================================================

def verify_tables() -> bool:
    """
    Verify all expected database objects exist (tables, enums, triggers).

    Returns:
        True if all objects exist, False otherwise
    """
    expected_tables = {
        "question_prompts",
        "questions",
        "model_responses",
        "user_evaluations",
        "judge_evaluations",
    }

    expected_enums = {
        "metric_type",
        "difficulty_level",
    }

    expected_triggers = {
        "trigger_question_prompts_updated_at",
        "trigger_questions_updated_at",
        "trigger_user_evaluations_updated_at",
    }

    try:
        with engine.connect() as conn:
            # Verify tables
            result = conn.execute(text("""
                SELECT tablename FROM pg_tables
                WHERE schemaname = 'public'
            """))
            actual_tables = {row[0] for row in result}

            missing_tables = expected_tables - actual_tables
            if missing_tables:
                logger.error(f"✗ Missing tables: {missing_tables}")
                return False

            logger.info(f"✓ All {len(expected_tables)} tables verified")
            for table in sorted(expected_tables):
                logger.info(f"  - {table}")

            # Verify ENUM types
            result = conn.execute(text("""
                SELECT typname FROM pg_type
                WHERE typtype = 'e' AND typnamespace = (
                    SELECT oid FROM pg_namespace WHERE nspname = 'public'
                )
            """))
            actual_enums = {row[0] for row in result}

            missing_enums = expected_enums - actual_enums
            if missing_enums:
                logger.error(f"✗ Missing ENUM types: {missing_enums}")
                return False

            logger.info(f"✓ All {len(expected_enums)} ENUM types verified")
            for enum_type in sorted(expected_enums):
                logger.info(f"  - {enum_type}")

            # Verify triggers
            result = conn.execute(text("""
                SELECT tgname FROM pg_trigger
                JOIN pg_class ON pg_trigger.tgrelid = pg_class.oid
                JOIN pg_namespace ON pg_class.relnamespace = pg_namespace.oid
                WHERE pg_namespace.nspname = 'public'
                AND pg_trigger.tgname LIKE '%updated_at%'
            """))
            actual_triggers = {row[0] for row in result}

            missing_triggers = expected_triggers - actual_triggers
            if missing_triggers:
                logger.error(f"✗ Missing triggers: {missing_triggers}")
                return False

            logger.info(f"✓ All {len(expected_triggers)} auto-update triggers verified")
            for trigger in sorted(expected_triggers):
                logger.info(f"  - {trigger}")

        return True

    except SQLAlchemyError as e:
        logger.error(f"✗ Verification failed: {e}")
        return False


# =====================================================
# Main CLI
# =====================================================

def main() -> int:
    """
    Main entry point for CLI.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(
        description="Initialize MentorMind database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/init_db.py              # Create all tables
  python scripts/init_db.py --verify     # Verify tables exist
  python scripts/init_db.py --drop       # Drop all tables first (DESTRUCTIVE)
        """
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify tables exist (don't create new tables)"
    )
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop all tables first (DESTRUCTIVE)"
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s"
    )

    # Print header
    logger.info("=" * 50)
    logger.info("MentorMind Database Initialization")
    logger.info("=" * 50)
    logger.info(f"Database: {settings.postgres_db}")
    logger.info(f"Host: {settings.postgres_host}:{settings.postgres_port}")
    logger.info("-" * 50)

    # Verify only mode
    if args.verify:
        success = verify_tables()
        return 0 if success else 1

    # Drop mode (DESTRUCTIVE)
    if args.drop:
        logger.warning("⚠ DROP MODE ENABLED - ALL TABLES WILL BE DELETED")
        confirm = input("Type 'yes' to confirm: ")
        if confirm.lower() != "yes":
            logger.info("Aborted")
            return 1
        if not drop_all_tables():
            return 1

    # Create tables
    logger.info("Creating database tables...")
    if not execute_all_schemas():
        logger.error("Database initialization failed")
        return 1

    logger.info("-" * 50)
    logger.info("✓ Database initialization complete")
    logger.info("-" * 50)

    # Verify after creation
    if verify_tables():
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
