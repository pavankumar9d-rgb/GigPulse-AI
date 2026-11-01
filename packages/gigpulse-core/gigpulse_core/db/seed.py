"""Synthetic data seeding script for SQLite database.

Imports the validated 8-week synthetic baseline fixtures into SQLite.
"""

import sys
from pathlib import Path
from typing import Any, Dict
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from gigpulse_core.db.database import get_engine, get_session_factory, init_db
from gigpulse_core.db.importer import import_csv_file


def seed_synthetic_fixtures(engine: Engine, synthetic_dir: Path) -> Dict[str, Any]:
    """Initialize schema and import all synthetic fixtures into the database."""
    init_db(engine)
    session_factory = get_session_factory(engine)
    results = {}

    fixture_order = [
        ("work_sessions", "work_sessions.csv"),
        ("deliveries", "deliveries.csv"),
        ("expenses", "expenses.csv"),
        ("zone_demand", "zone_demand.csv"),
    ]

    with session_factory() as session:
        for template_type, filename in fixture_order:
            filepath = synthetic_dir / filename
            if not filepath.exists():
                raise FileNotFoundError(f"Missing fixture file: {filepath}")

            result = import_csv_file(session, filepath, template_type)
            results[template_type] = {
                "batch_id": result.batch_id,
                "status": result.status,
                "total_rows": result.total_rows,
                "accepted_rows": result.accepted_rows,
                "rejected_rows": result.rejected_rows,
                "duplicate_rows": result.duplicate_rows,
                "already_imported": result.already_imported,
            }

    return results


def main():
    db_path = sys.argv[1] if len(sys.argv) > 1 else "gigpulse.db"
    synth_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data/synthetic")

    print(f"Connecting to database: {db_path}")
    print(f"Reading synthetic fixtures from: {synth_dir}")

    engine = get_engine(db_path=db_path)
    results = seed_synthetic_fixtures(engine, synth_dir)

    print("\nDatabase Seeding Summary:")
    for k, v in results.items():
        print(f"  {k:15s}: {v['accepted_rows']} accepted, {v['rejected_rows']} rejected (Batch: {v['batch_id']})")
    print(f"\nDatabase initialized and seeded successfully at '{db_path}'.")


if __name__ == "__main__":
    main()

