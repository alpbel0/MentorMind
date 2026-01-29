"""
Seed Data Script

Populates the question_prompts table with evaluation question templates.

Usage:
    python scripts/seed_data.py              # Seed question prompts (skeleton mode)
    python scripts/seed_data.py --verify     # Verify prompts exist
    python scripts/seed_data.py --reset      # Delete all prompts (DESTRUCTIVE)
    python scripts/seed_data.py --dry-run    # Show what will be seeded
"""

import argparse
import logging
import sys

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.models.database import SessionLocal
from backend.models.question_prompt import QuestionPrompt

logger = logging.getLogger(__name__)

# =====================================================
# Constants
# =====================================================

METRICS = [
    "Truthfulness",
    "Helpfulness",
    "Safety",
    "Bias",
    "Clarity",
    "Consistency",
    "Efficiency",
    "Robustness",
]
"""The 8 evaluation metrics for MentorMind"""

DIFFICULTIES = ["easy", "medium", "hard"]
"""Valid difficulty levels for question prompts"""

CATEGORIES = ["Math", "Coding", "Medical", "General"]
"""Valid categories for questions"""

# Expected counts after full implementation (Week 2)
EXPECTED_COUNT = len(METRICS) * len(DIFFICULTIES)  # 8 * 3 = 24
"""Total number of question prompts after Week 2 implementation"""


# =====================================================
# Seeding Functions
# =====================================================

def seed_question_prompts(db: Session) -> int:
    """
    Seed question prompts into database.

    SKELETON MODE: Returns message indicating Week 2 implementation.
    In Week 2, this function will insert 24 question prompt templates
    (8 metrics × 3 difficulty levels).

    Args:
        db: SQLAlchemy database session

    Returns:
        Number of prompts seeded (0 for skeleton mode)
    """
    logger.info("Seeding question prompts...")
    logger.info("")
    logger.info("  Week 2'de doldurulacak - 24 soru şablonu eklenecek")
    logger.info("  Her metrik için 3 şablon (easy, medium, hard)")
    logger.info("")
    logger.info(f"  Metrikler ({len(METRICS)}):")
    for metric in METRICS:
        logger.info(f"    - {metric}")
    logger.info("")
    logger.info(f"  Toplam: {EXPECTED_COUNT} şablon")

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

    # Count by difficulty
    difficulty_counts = {}
    for difficulty in DIFFICULTIES:
        count = db.query(QuestionPrompt).filter_by(difficulty=difficulty).count()
        difficulty_counts[difficulty] = count

    return {
        "count": total_count,
        "by_metric": metric_counts,
        "by_difficulty": difficulty_counts,
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
    """Display what will be seeded in Week 2."""
    logger.info("DRY RUN - No changes will be made")
    logger.info("")
    logger.info("Week 2'de eklenecek şablonlar:")
    logger.info(f"  - {len(METRICS)} metrik × {len(DIFFICULTIES)} zorluk seviyesi = {EXPECTED_COUNT} şablon")
    logger.info("")
    logger.info("Her metrik için:")
    for difficulty in DIFFICULTIES:
        logger.info(f"  - {difficulty} zorluk seviyesi")
    logger.info("")
    logger.info("Metrikler:")
    for metric in METRICS:
        logger.info(f"  - {metric}")
    logger.info("")
    logger.info("Kategoriler:")
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
  python scripts/seed_data.py              # Seed prompts (skeleton mode)
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
            logger.info("By Difficulty:")
            for difficulty in DIFFICULTIES:
                count = results['by_difficulty'][difficulty]
                expected = len(METRICS)
                status = "✓" if count == expected else "✗"
                logger.info(f"  {status} {difficulty}: {count}/{expected}")

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
