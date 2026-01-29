"""
Seed Data Script

Populates the question_prompts table with evaluation question templates.

Usage:
    python scripts/seed_data.py              # Seed question prompts
    python scripts/seed_data.py --verify     # Verify prompts exist
    python scripts/seed_data.py --reset      # Delete all prompts (DESTRUCTIVE)
    python scripts/seed_data.py --dry-run    # Show what will be seeded
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.models.database import SessionLocal
from backend.models.question_prompt import QuestionPrompt
from backend.prompts.master_prompts import (
    METRICS,
    QUESTION_TYPES,
    MASTER_PROMPTS,
    BONUS_METRIC_MAPPINGS,
    get_golden_example,
)

logger = logging.getLogger(__name__)

# =====================================================
# Constants
# =====================================================

CATEGORIES = ["Math", "Coding", "Medical", "General"]
"""Valid categories for questions"""

# Expected count: 8 metrics × 3 question_types = 24 prompts
EXPECTED_COUNT = sum(len(qt_list) for qt_list in QUESTION_TYPES.values())
"""Total number of question prompts after Task 2.1 implementation"""


# =====================================================
# Seeding Functions
# =====================================================

def seed_question_prompts(db: Session) -> int:
    """
    Seed question prompts into database.

    Creates 24 question prompt templates:
    - 8 metrics × 3 question_types each
    - All with difficulty='medium' (as per Task 2.1 spec)
    - Each question_type has 1 golden example

    Args:
        db: SQLAlchemy database session

    Returns:
        Number of prompts seeded
    """
    logger.info("Seeding question prompts...")
    logger.info("")
    logger.info(f"  Creating {EXPECTED_COUNT} prompt templates:")
    logger.info(f"    - {len(METRICS)} metrics")
    logger.info(f"    - 3 question_types per metric")
    logger.info(f"    - All with difficulty='medium'")
    logger.info("")

    count = 0

    for metric in METRICS:
        question_types = QUESTION_TYPES.get(metric, [])
        logger.info(f"  Processing {metric}... ({len(question_types)} types)")

        for question_type in question_types:
            # Get golden example for this metric-type combination
            golden_example = get_golden_example(metric, question_type)

            if not golden_example:
                logger.warning(f"    Warning: No golden example for {metric}:{question_type}")

            # Create QuestionPrompt record
            prompt = QuestionPrompt(
                primary_metric=metric,
                bonus_metrics=BONUS_METRIC_MAPPINGS.get(metric, []),
                question_type=question_type,
                user_prompt=MASTER_PROMPTS[metric]["user_prompt_template"],
                golden_examples=[golden_example] if golden_example else [],
                difficulty="medium",  # Fixed to medium for all prompts
                category_hints=["any"],  # Default: any category
                is_active=True
            )
            db.add(prompt)
            count += 1

    try:
        db.commit()
        logger.info("")
        logger.info(f"✓ Seeded {count} question prompts")

        # Log breakdown by metric
        logger.info("")
        logger.info("  Prompts by metric:")
        for metric in METRICS:
            qt_count = len(QUESTION_TYPES.get(metric, []))
            logger.info(f"    - {metric}: {qt_count}")

        return count
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to seed prompts: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 0


# =====================================================
# Verification Functions
# =====================================================

def verify_prompts(db: Session) -> dict:
    """
    Verify question prompts exist in database.

    Args:
        db: SQLAlchemy database session

    Returns:
        Dictionary with verification results:
        - count: Total number of prompts
        - by_metric: Dict of metric -> count
        - by_difficulty: Dict of difficulty -> count
        - is_complete: True if all 24 prompts exist
    """
    total_count = db.query(QuestionPrompt).count()

    # Count by primary metric
    metric_counts = {}
    for metric in METRICS:
        count = db.query(QuestionPrompt).filter_by(primary_metric=metric).count()
        metric_counts[metric] = count

    # Count by question type
    type_counts = {}
    for metric in METRICS:
        for qt in QUESTION_TYPES.get(metric, []):
            key = f"{metric}:{qt}"
            count = db.query(QuestionPrompt).filter_by(
                primary_metric=metric,
                question_type=qt
            ).count()
            type_counts[key] = count

    return {
        "count": total_count,
        "by_metric": metric_counts,
        "by_question_type": type_counts,
        "is_complete": total_count == EXPECTED_COUNT,
        "expected_count": EXPECTED_COUNT,
    }


# =====================================================
# Reset Functions
# =====================================================

def reset_prompts(db: Session) -> bool:
    """
    Delete all question prompts from database.

    DESTRUCTIVE OPERATION: This will delete all question prompts.

    Args:
        db: SQLAlchemy database session

    Returns:
        True if successful, False otherwise
    """
    try:
        deleted = db.query(QuestionPrompt).delete()
        db.commit()
        logger.warning(f"Deleted {deleted} question prompts")
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Failed to reset prompts: {e}")
        return False


# =====================================================
# Dry-Run Display
# =====================================================

def show_dry_run() -> None:
    """Display what will be seeded."""
    logger.info("DRY RUN - No changes will be made")
    logger.info("")
    logger.info(f"Will create {EXPECTED_COUNT} prompt templates:")
    logger.info(f"  - {len(METRICS)} metrics")
    logger.info(f"  - 3 question_types per metric")
    logger.info(f"  - All with difficulty='medium'")
    logger.info("")
    logger.info("Prompts to be created:")
    for metric in METRICS:
        qts = QUESTION_TYPES.get(metric, [])
        logger.info(f"  {metric}:")
        for qt in qts:
            logger.info(f"    - {qt}")
    logger.info("")
    logger.info("Categories:")
    for category in CATEGORIES:
        logger.info(f"  - {category}")


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
        description="Seed MentorMind question prompts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/seed_data.py              # Seed prompts
  python scripts/seed_data.py --verify     # Verify prompts exist
  python scripts/seed_data.py --reset      # Delete all prompts (DESTRUCTIVE)
  python scripts/seed_data.py --dry-run    # Show what will be seeded
        """
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify prompts exist (don't seed new prompts)"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete all prompts (DESTRUCTIVE)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what will be seeded (don't make changes)"
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s"
    )
    # Suppress SQLAlchemy engine logs
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    # Print header
    logger.info("=" * 50)
    logger.info("MentorMind Seed Data Script")
    logger.info("=" * 50)
    logger.info("-" * 50)

    # Create database session
    db = SessionLocal()

    try:
        # Verify mode
        if args.verify:
            logger.info("Verifying question prompts...")
            logger.info("")

            results = verify_prompts(db)

            logger.info(f"Total prompts: {results['count']}")
            logger.info(f"Expected: {results['expected_count']}")
            logger.info(f"Status: {'✓ Complete' if results['is_complete'] else '✗ Incomplete'}")
            logger.info("")
            logger.info("By Metric:")
            for metric in METRICS:
                count = results['by_metric'][metric]
                status = "✓" if count == len(DIFFICULTIES) else "✗"
                logger.info(f"  {status} {metric}: {count}")
            logger.info("")
            logger.info("By Question Type:")
            for metric in METRICS:
                for qt in QUESTION_TYPES.get(metric, []):
                    key = f"{metric}:{qt}"
                    count = results['by_question_type'].get(key, 0)
                    status = "✓" if count == 1 else "✗"
                    logger.info(f"  {status} {key}: {count}")

            logger.info("-" * 50)
            return 0 if results['is_complete'] else 1

        # Reset mode (DESTRUCTIVE)
        if args.reset:
            logger.warning("⚠ RESET MODE - ALL PROMPTS WILL BE DELETED")
            confirm = input("Type 'yes' to confirm: ")
            if confirm.lower() != "yes":
                logger.info("Aborted")
                return 1
            logger.info("")
            if not reset_prompts(db):
                return 1
            logger.info("-" * 50)
            logger.info("✓ Reset complete")
            logger.info("-" * 50)
            return 0

        # Dry-run mode
        if args.dry_run:
            show_dry_run()
            logger.info("-" * 50)
            return 0

        # Normal seed mode (skeleton)
        logger.info("Seeding question prompts...")
        logger.info("")

        count = seed_question_prompts(db)

        logger.info("")
        logger.info("-" * 50)
        logger.info(f"✓ Seeding complete: {count} prompts added")
        logger.info("-" * 50)
        return 0

    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        return 1

    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
