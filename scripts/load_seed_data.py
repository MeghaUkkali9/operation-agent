"""Loads data/seed/*.csv into the database configured by DATABASE_URL.

Creates tables if they don't exist and truncates before loading, so it is
safe to re-run (idempotent) against a dev or freshly-provisioned database.
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import delete

from app.database.base import Base
from app.database.models import Container, Vessel
from app.database.session import SessionLocal, engine

SEED_DIR = Path(__file__).resolve().parent.parent / "data" / "seed"


def load_vessels(session) -> None:
    with (SEED_DIR / "vessels.csv").open() as f:
        rows = list(csv.DictReader(f))

    session.execute(delete(Vessel))
    session.add_all(
        Vessel(
            id=int(row["id"]),
            vessel_name=row["vessel_name"],
            voyage_number=row["voyage_number"],
            arrival_date=row["arrival_date"],
            departure_date=row["departure_date"],
            status=row["status"],
            terminal=row["terminal"],
        )
        for row in rows
    )


def load_containers(session) -> None:
    with (SEED_DIR / "containers.csv").open() as f:
        rows = list(csv.DictReader(f))

    session.execute(delete(Container))
    session.add_all(
        Container(
            id=int(row["id"]),
            container_number=row["container_number"],
            vessel_id=int(row["vessel_id"]),
            container_type=row["container_type"],
            status=row["status"],
            destination=row["destination"],
            weight=float(row["weight"]),
            priority=row["priority"],
            terminal=row["terminal"],
            arrival_date=row["arrival_date"],
        )
        for row in rows
    )


def main() -> None:
    Base.metadata.create_all(engine)

    session = SessionLocal()
    try:
        load_vessels(session)
        session.flush()
        load_containers(session)
        session.commit()
    finally:
        session.close()

    print("Seed data loaded.")


if __name__ == "__main__":
    main()
