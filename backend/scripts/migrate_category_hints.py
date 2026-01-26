"""
Migration script to update category_hints from []/NULL to ["any"]

This script fixes the validator conflict that occurs when category_hints
contains empty arrays [] or NULL values. The Pydantic validator requires
non-empty arrays, and the new default is ["any"].

Problem:
- SQL default changed from [] to ["any"]
- Existing records may have [] or NULL values
- Validator rejects empty lists with ValueError

Solution:
- Update all [] values to ["any"]
- Update all NULL values to ["any"]
- Report migration statistics

Author: Ralph Wiggum (Surgical Debugging)
Date: 2025-01-26
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from backend.models.database import engine
from sqlalchemy.exc import SQLAlchemyError


def migrate_category_hints(dry_run: bool = True) -> dict:
    """
    Migrate category_hints from []/NULL to ["any"].

    Args:
        dry_run: If True, show changes without applying them

    Returns:
        dict: Migration statistics
    """
    stats = {
        "total_records": 0,
        "empty_arrays": 0,
        "null_values": 0,
        "already_valid": 0,
        "updated": 0
    }

    try:
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()

            try:
                # Count total records
                result = conn.execute(text(
                    "SELECT COUNT(*) FROM question_prompts"
                ))
                stats["total_records"] = result.scalar()

                print(f"📊 Toplam kayıt: {stats['total_records']}")
                print("-" * 50)

                # Check empty arrays []
                result = conn.execute(text(
                    "SELECT COUNT(*) FROM question_prompts WHERE category_hints = '[]'::jsonb"
                ))
                stats["empty_arrays"] = result.scalar()
                print(f"🔍 Boş dizi ([]): {stats['empty_arrays']}")

                # Check NULL values
                result = conn.execute(text(
                    "SELECT COUNT(*) FROM question_prompts WHERE category_hints IS NULL"
                ))
                stats["null_values"] = result.scalar()
                print(f"🔍 NULL değerler: {stats['null_values']}")

                # Count valid records
                result = conn.execute(text(
                    "SELECT COUNT(*) FROM question_prompts "
                    "WHERE category_hints != '[]'::jsonb AND category_hints IS NOT NULL"
                ))
                stats["already_valid"] = result.scalar()
                print(f"✅ Zaten geçerli: {stats['already_valid']}")

                # Calculate total updates needed
                stats["updated"] = stats["empty_arrays"] + stats["null_values"]

                if stats["updated"] == 0:
                    print("\n✅ Migration gerekli değil! Tüm kayıtlar zaten geçerli.")
                    return stats

                print(f"\n🔧 Güncellenecek kayıt: {stats['updated']}")
                print("-" * 50)

                if dry_run:
                    print("⚠️  DRY RUN MODU - Değişiklikler uygulanmayacak")
                    print("\nÖrnek güncellenecek kayıtlar:")

                    # Show sample records that would be updated
                    result = conn.execute(text("""
                        SELECT id, primary_metric, category_hints
                        FROM question_prompts
                        WHERE category_hints = '[]'::jsonb OR category_hints IS NULL
                        LIMIT 3
                    """))

                    for row in result:
                        print(f"  - ID: {row[0]}, Metric: {row[1]}, Hints: {row[2]}")

                    # Rollback since it's dry run
                    trans.rollback()
                    print("\n✅ Dry run tamamlandı. Gerçek migration için --apply kullanın.")

                else:
                    print("🚀 Migration başlıyor...")

                    # Update empty arrays to ["any"]
                    if stats["empty_arrays"] > 0:
                        result = conn.execute(text("""
                            UPDATE question_prompts
                            SET category_hints = '["any"]'::jsonb
                            WHERE category_hints = '[]'::jsonb
                        """))
                        print(f"  ✅ {stats['empty_arrays']} boş dizi güncellendi")

                    # Update NULL values to ["any"]
                    if stats["null_values"] > 0:
                        result = conn.execute(text("""
                            UPDATE question_prompts
                            SET category_hints = '["any"]'::jsonb
                            WHERE category_hints IS NULL
                        """))
                        print(f"  ✅ {stats['null_values']} NULL değer güncellendi")

                    # Commit transaction
                    trans.commit()
                    print("\n✅ Migration başarıyla tamamlandı!")

                    # Verify all records now have valid category_hints
                    result = conn.execute(text("""
                        SELECT COUNT(*) FROM question_prompts
                        WHERE category_hints = '[]'::jsonb OR category_hints IS NULL
                    """))
                    invalid_count = result.scalar()

                    if invalid_count == 0:
                        print("✅ Doğrulama başarılı! Tüm kayıtlar geçerli.")
                    else:
                        print(f"⚠️  Uyarı: {invalid_count} geçersiz kayıt hala mevcut!")

            except Exception as e:
                # Rollback on error
                trans.rollback()
                print(f"❌ Hata: {e}")
                raise

    except SQLAlchemyError as e:
        print(f"❌ Veritabanı hatası: {e}")
        raise
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")
        raise

    return stats


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Migration script for category_hints compatibility"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Migration'i uygula (varsayılan: dry-run)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Onaysız migration uygulama (dikkatli kullanın)"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("🔧 Category Hints Migration Script")
    print("=" * 60)
    print()

    if not args.apply:
        print("⚠️  DRY RUN MODU - Değişiklikler uygulanmayacak")
        print("Gerçek migration için --apply bayrağını kullanın")
        print()

    # Check if database is accessible
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Veritabanı bağlantısı başarılı")
        print()
    except Exception as e:
        print(f"❌ Veritabanı bağlantı hatası: {e}")
        sys.exit(1)

    # Run migration
    try:
        stats = migrate_category_hints(dry_run=not args.apply)

        print()
        print("=" * 60)
        print("📊 Migration Özeti")
        print("=" * 60)
        print(f"Toplam kayıt:      {stats['total_records']}")
        print(f"Boş dizi ([]):     {stats['empty_arrays']}")
        print(f"NULL değerler:     {stats['null_values']}")
        print(f"Zaten geçerli:     {stats['already_valid']}")
        print(f"Güncellendi:       {stats['updated']}")
        print("=" * 60)

        if not args.apply and stats['updated'] > 0:
            print()
            print("💡 Migration'i uygulamak için:")
            print("   python backend/scripts/migrate_category_hints.py --apply")

    except Exception as e:
        print()
        print(f"❌ Migration başarısız: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
