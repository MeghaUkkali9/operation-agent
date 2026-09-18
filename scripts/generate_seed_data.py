"""Generates synthetic vessels.csv and containers.csv into data/seed/.

Deterministic (fixed random seed) so the generated data is reproducible and
diffable in git. This script has no database or app dependency — it only
produces CSVs; scripts/load_seed_data.py loads them into Postgres.
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 42
NUM_VESSELS = 120
NUM_CONTAINERS = 1400

SEED_DIR = Path(__file__).resolve().parent.parent / "data" / "seed"

TERMINALS = ["Terminal A", "Terminal B", "Terminal C"]

VESSEL_ADJECTIVES = [
    "Northern", "Pacific", "Atlantic", "Golden", "Silver", "Royal", "Grand",
    "Blue", "Southern", "Eastern", "Western", "Crimson", "Emerald", "Coral",
    "Arctic",
]
VESSEL_NOUNS = [
    "Star", "Horizon", "Voyager", "Pioneer", "Navigator", "Mariner",
    "Trader", "Express", "Legacy", "Odyssey", "Endeavor", "Pathfinder",
    "Enterprise", "Discovery", "Frontier",
]

DESTINATIONS = [
    "Rotterdam", "Singapore", "Shanghai", "Los Angeles", "Hamburg",
    "Jebel Ali", "Santos", "Busan", "Antwerp", "Ningbo", "Long Beach",
    "Colombo", "Piraeus", "Tanjung Pelepas", "Felixstowe", "Valencia",
    "Algeciras", "Nhava Sheva", "Durban", "Vancouver",
]

# Fictitious container-line prefixes — deliberately not real ISO carrier codes.
CONTAINER_PREFIXES = ["ZTCU", "OPXU", "QRSU", "VNKU", "WLMU", "JHDU", "BFPU"]

CONTAINER_TYPES = ["standard", "reefer", "dangerous_goods", "open_top", "flat_rack"]
CONTAINER_TYPE_WEIGHTS = [0.55, 0.2, 0.1, 0.08, 0.07]

CONTAINER_STATUSES = ["in_yard", "loaded", "dispatched", "delayed", "damaged"]
CONTAINER_STATUS_WEIGHTS = [0.35, 0.25, 0.25, 0.1, 0.05]

PRIORITIES = ["low", "normal", "high", "urgent"]
PRIORITY_WEIGHTS = [0.2, 0.55, 0.18, 0.07]

VESSEL_STATUSES = ["scheduled", "arrived", "departed", "delayed"]
VESSEL_STATUS_WEIGHTS = [0.15, 0.4, 0.35, 0.1]

START_DATE = date(2026, 1, 1)
DATE_RANGE_DAYS = 240


def random_date(rng: random.Random, start: date, days: int) -> date:
    return start + timedelta(days=rng.randint(0, days))


def generate_vessels(rng: random.Random) -> list[dict]:
    used_names: set[str] = set()
    vessels = []

    for i in range(1, NUM_VESSELS + 1):
        while True:
            name = f"MV {rng.choice(VESSEL_ADJECTIVES)} {rng.choice(VESSEL_NOUNS)}"
            if name not in used_names:
                used_names.add(name)
                break

        arrival = random_date(rng, START_DATE, DATE_RANGE_DAYS)
        departure = arrival + timedelta(days=rng.randint(1, 5))
        status = rng.choices(VESSEL_STATUSES, weights=VESSEL_STATUS_WEIGHTS)[0]

        vessels.append(
            {
                "id": i,
                "vessel_name": name,
                "voyage_number": f"V2026-{i:04d}",
                "arrival_date": arrival.isoformat(),
                "departure_date": departure.isoformat(),
                "status": status,
                "terminal": rng.choice(TERMINALS),
            }
        )

    return vessels


def generate_containers(rng: random.Random, vessels: list[dict]) -> list[dict]:
    containers = []
    used_numbers: set[str] = set()

    for i in range(1, NUM_CONTAINERS + 1):
        vessel = rng.choice(vessels)
        vessel_arrival = date.fromisoformat(vessel["arrival_date"])

        while True:
            number = f"{rng.choice(CONTAINER_PREFIXES)}{rng.randint(1000000, 9999999)}"
            if number not in used_numbers:
                used_numbers.add(number)
                break

        containers.append(
            {
                "id": i,
                "container_number": number,
                "vessel_id": vessel["id"],
                "container_type": rng.choices(
                    CONTAINER_TYPES, weights=CONTAINER_TYPE_WEIGHTS
                )[0],
                "status": rng.choices(
                    CONTAINER_STATUSES, weights=CONTAINER_STATUS_WEIGHTS
                )[0],
                "destination": rng.choice(DESTINATIONS),
                "weight": round(rng.uniform(2000, 28000), 2),
                "priority": rng.choices(PRIORITIES, weights=PRIORITY_WEIGHTS)[0],
                "terminal": vessel["terminal"],
                "arrival_date": (vessel_arrival + timedelta(days=rng.randint(0, 1))).isoformat(),
            }
        )

    return containers


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rng = random.Random(SEED)
    SEED_DIR.mkdir(parents=True, exist_ok=True)

    vessels = generate_vessels(rng)
    containers = generate_containers(rng, vessels)

    write_csv(SEED_DIR / "vessels.csv", vessels)
    write_csv(SEED_DIR / "containers.csv", containers)

    print(f"Generated {len(vessels)} vessels and {len(containers)} containers into {SEED_DIR}")


if __name__ == "__main__":
    main()
