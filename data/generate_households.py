"""
Generate the synthetic household and plot set for Mvula.

NO REAL HOUSEHOLD DATA IS USED OR PRODUCED HERE.

The schema mirrors a real Extension Planning Area field register, with every
personally identifying field removed: no household head name, no national ID,
no village headman. Households are referenced by an opaque Household_Ref.

Four defects characteristic of real paper registers are reproduced on purpose.
They are not noise to be cleaned up -- handling them is what the agent is for.

  1. Plot sizes paced or eyeballed rather than measured
  2. Tenure and plot location stale between seasons (rented plots move)
  3. Plots recorded as a sole crop that are in practice intercropped
  4. Records not revisited for one or more seasons

Deterministic: a fixed seed means the same set every run, so eval results
are comparable across days.
"""

import json
import random
import sqlite3
import hashlib
from pathlib import Path
from datetime import date, timedelta

SEED = 20261007
CURRENT_SEASON = "2026/27"
TODAY = date(2026, 10, 7)

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "mvula.db"
CSV_PATH = ROOT / "data" / "households_sample.csv"

# Four sections across two EPAs, two in each agroclimatic zone.
SECTIONS = [
    {"epa": "Chonde",    "section": "Chonde North", "zone": "lowland", "blocks": 6, "households": 620},
    {"epa": "Chonde",    "section": "Chonde South", "zone": "lowland", "blocks": 5, "households": 540},
    {"epa": "Thuchila",  "section": "Thuchila East", "zone": "upland", "blocks": 6, "households": 660},
    {"epa": "Thuchila",  "section": "Nessa",         "zone": "upland", "blocks": 5, "households": 580},
]

SOILS = {
    "lowland": ["sandy loam", "clay loam", "alluvial"],
    "upland": ["sandy loam", "loam", "shallow stony loam"],
}

SECONDARY_CROPS = ["pigeon peas", "beans", "groundnuts", "cassava", None]


def household_ref(epa: str, section: str, n: int) -> str:
    """Opaque, stable, carries no personal information."""
    raw = f"{epa}|{section}|{n}|{SEED}"
    return "H-" + hashlib.sha256(raw.encode()).hexdigest()[:10].upper()


def build(rng: random.Random):
    rows = []
    for sec in SECTIONS:
        for i in range(sec["households"]):
            zone = sec["zone"]

            # --- tenure ---------------------------------------------------
            tenure = rng.choices(
                ["customary", "rented", "borrowed"], weights=[62, 30, 8]
            )[0]

            # Rented and borrowed plots change between seasons. The register
            # often still holds last season's location.
            if tenure in ("rented", "borrowed"):
                seasons_old = rng.choices([0, 1, 2], weights=[40, 45, 15])[0]
            else:
                seasons_old = rng.choices([0, 1, 2, 3], weights=[55, 28, 12, 5])[0]

            tenure_season = {
                0: CURRENT_SEASON, 1: "2025/26", 2: "2024/25", 3: "2023/24"
            }[seasons_old]

            # A location record is stale if the plot can move and the record
            # predates this season.
            location_stale = seasons_old >= 1 and tenure in ("rented", "borrowed")

            # --- plot size ------------------------------------------------
            size_method = rng.choices(
                ["measured", "paced", "eyeballed"], weights=[14, 44, 42]
            )[0]
            true_size = round(rng.lognormvariate(-1.05, 0.52), 3)
            true_size = min(max(true_size, 0.08), 4.2)

            # Unmeasured sizes are recorded with error, and round numbers are
            # over-represented because people say "about half an acre".
            if size_method == "measured":
                recorded = round(true_size, 2)
            elif size_method == "paced":
                recorded = round(true_size * rng.uniform(0.80, 1.25), 2)
            else:
                recorded = round(true_size * rng.uniform(0.62, 1.55), 2)
                if rng.random() < 0.45:
                    recorded = rng.choice([0.2, 0.25, 0.4, 0.5, 0.75, 1.0, 1.5, 2.0])
            recorded = max(recorded, 0.05)

            # --- cropping -------------------------------------------------
            primary = "maize"
            # The register frequently records maize alone. That is a recording
            # habit, not a cropping pattern.
            secondary = rng.choices(
                SECONDARY_CROPS, weights=[14, 13, 8, 5, 60]
            )[0]

            # The register records a sole crop far more often than farmers
            # actually plant one. Where secondary is None the plot is still
            # frequently intercropped in practice -- the register just does
            # not say so.
            actually_intercropped = rng.random() < (0.55 if secondary is None else 0.93)
            intercrop_undeclared = actually_intercropped and secondary is None

            # --- inputs ---------------------------------------------------
            # Fertiliser requirement is derived from the recorded area, so an
            # eyeballed area propagates straight into the input figure.
            bags = round(recorded * 4.0)
            bags = max(1, min(bags, 14))

            aip = rng.random() < 0.38

            last_updated = TODAY - timedelta(days=rng.randint(20, 900))

            n = len(rows) + 1
            rows.append({
                "Household_Ref": household_ref(sec["epa"], sec["section"], n),
                "District": "Mulanje",
                "EPA_Name": sec["epa"],
                "Section_Name": sec["section"],
                "Block_Number": f"B{rng.randint(1, sec['blocks']):02d}",
                "Zone": zone,
                "Gender_HH": rng.choices(["F", "M"], weights=[41, 59])[0],
                "Total_Household_Members": rng.choices(
                    [2, 3, 4, 5, 6, 7, 8, 9], weights=[6, 12, 20, 22, 18, 12, 6, 4]
                )[0],
                "Plot_Location_Code": f"MLJ-{sec['epa'][:3].upper()}-{n:05d}",
                "Recorded_Plot_Size_Ha": recorded,
                "Plot_Size_Method": size_method,
                "Primary_Crop": primary,
                "Secondary_Crop": secondary,
                "Soil_Type_Topography": rng.choice(SOILS[zone]),
                "Tenure_Status": tenure,
                "Tenure_Recorded_Season": tenure_season,
                "Target_Fertilizer_Bags": bags,
                "AIP_Beneficiary": int(aip),
                "Record_Last_Updated": last_updated.isoformat(),

                # --- quality flags, carried with every row ----------------
                "flag_plot_size_unmeasured": int(size_method != "measured"),
                "flag_location_stale": int(location_stale),
                "flag_intercrop_undeclared": int(intercrop_undeclared),
                "flag_record_age_seasons": seasons_old,
            })
    return rows


SCHEMA = """
DROP TABLE IF EXISTS households;
CREATE TABLE households (
    Household_Ref              TEXT PRIMARY KEY,
    District                   TEXT NOT NULL,
    EPA_Name                   TEXT NOT NULL,
    Section_Name               TEXT NOT NULL,
    Block_Number               TEXT NOT NULL,
    Zone                       TEXT NOT NULL CHECK (Zone IN ('lowland','upland')),
    Gender_HH                  TEXT,
    Total_Household_Members    INTEGER,
    Plot_Location_Code         TEXT,
    Recorded_Plot_Size_Ha      REAL,
    Plot_Size_Method           TEXT CHECK (Plot_Size_Method IN ('measured','paced','eyeballed')),
    Primary_Crop               TEXT,
    Secondary_Crop             TEXT,
    Soil_Type_Topography       TEXT,
    Tenure_Status              TEXT,
    Tenure_Recorded_Season     TEXT,
    Target_Fertilizer_Bags     INTEGER,
    AIP_Beneficiary            INTEGER,
    Record_Last_Updated        TEXT,
    flag_plot_size_unmeasured  INTEGER NOT NULL,
    flag_location_stale        INTEGER NOT NULL,
    flag_intercrop_undeclared  INTEGER NOT NULL,
    flag_record_age_seasons    INTEGER NOT NULL
);
CREATE INDEX idx_section ON households (Section_Name);
CREATE INDEX idx_zone ON households (Zone);
"""


def main():
    rng = random.Random(SEED)
    rows = build(rng)

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA)
    cols = list(rows[0].keys())
    con.executemany(
        f"INSERT INTO households ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
        [tuple(r[c] for c in cols) for r in rows],
    )
    con.commit()

    # a readable sample for inspection
    import csv
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows[:40]:
            w.writerow(r)

    # --- report ------------------------------------------------------------
    n = len(rows)
    def pct(x): return f"{100 * x / n:5.1f}%"
    print(f"households generated: {n}")
    print(f"  written to {DB_PATH}")
    print()
    print("defect rates (deliberate):")
    print(f"  plot size unmeasured     {pct(sum(r['flag_plot_size_unmeasured'] for r in rows))}")
    print(f"  location record stale    {pct(sum(r['flag_location_stale'] for r in rows))}")
    print(f"  intercrop undeclared     {pct(sum(r['flag_intercrop_undeclared'] for r in rows))}")
    print(f"  record 1+ seasons old    {pct(sum(1 for r in rows if r['flag_record_age_seasons'] >= 1))}")
    clean = sum(1 for r in rows if not any(
        (r['flag_plot_size_unmeasured'], r['flag_location_stale'],
         r['flag_intercrop_undeclared'], r['flag_record_age_seasons'])))
    print(f"  no flags at all          {pct(clean)}")
    print()
    for sec in SECTIONS:
        c = sum(1 for r in rows if r["Section_Name"] == sec["section"])
        print(f"  {sec['section']:<16} {sec['zone']:<9} {c:>5} households")


if __name__ == "__main__":
    main()
