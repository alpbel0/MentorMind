"""
Database Connection Test Script

Usage: docker-compose exec backend python scripts/test_db_connection.py
"""

import sys
import time
from sqlalchemy import text
from backend.models.database import engine, test_database_connection
from backend.config.settings import settings


def main():
    print("=" * 60)
    print("MentorMind - Database Connection Test")
    print("=" * 60)
    print(f"Host: {settings.postgres_host}:{settings.postgres_port}")
    print(f"Database: {settings.postgres_db}")
    print(f"User: {settings.postgres_user}")
    print("-" * 60)

    # Test connection latency
    start_time = time.time()
    if test_database_connection():
        db_latency = (time.time() - start_time) * 1000

        print(f"\nSUCCESS: Database is reachable")
        print(f"   Latency: {db_latency:.2f}ms")

        # Pool info
        pool = engine.pool
        print(f"\nConnection Pool:")
        print(f"  Pool Size: {pool.size()}")
        print(f"  Max Overflow: {pool._max_overflow}")
        print(f"  Checked Out: {pool.checkedout()}")

        # List tables
        try:
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT tablename FROM pg_tables
                    WHERE schemaname = 'public'
                """))
                tables = [row[0] for row in result]
                print(f"\nExisting Tables: {len(tables)}")
                if tables:
                    for table in tables:
                        print(f"  - {table}")
                else:
                    print("  (No tables yet)")
        except Exception as e:
            print(f"\nWARNING: Could not list tables: {e}")

        return 0
    else:
        print("\nFAILURE: Database is not reachable")
        print("\nTroubleshooting:")
        print("  1. docker-compose ps postgres")
        print("  2. docker-compose logs postgres")
        print("  3. Check DATABASE_URL in .env")
        return 1


if __name__ == "__main__":
    sys.exit(main())
