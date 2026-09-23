"""
Q5 -- SNAP enrollment and food shelf use

Owner: Dhyan
Read questions/q5_snap/README.md before editing this file.

Run from the repo root:   python questions/q5_snap/analysis.py

Rules for this file:
  * It reads from data/processed/ and data/external/ only, never data/raw/.
  * Every number that ends up on a slide is produced here, by this script.
  * If you cannot explain a line of it live, it does not belong here.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
import pandas as pd

import config as C
import qkit

OUT_PREFIX = "q5"


def main() -> None:
    print("=" * 70)
    print("Q5 -- SNAP enrollment and food shelf use")
    print("=" * 70)

    cm = qkit.county_month()
    qkit.leakage_check(cm)

    # The call centre is a SNAP helpline: a second, free read on SNAP activity.
    # Clinic-pushed SNAP Rx referrals are excluded because their volume tracks
    # which clinics are enrolled, not household demand.
    calls = qkit.calls(exclude_snap_rx=True, geocoded_only=True)
    by_county_month = (calls.groupby(["fips", "yearmonth"])
                            .size().rename("calls").reset_index())
    print(f"{len(by_county_month)} county-months of non-SNAP-Rx calls")

    # TODO Step 1. Find and validate the MN DHS county-monthly SNAP caseload
    #   series. Record publisher, series, grain and publication lag in
    #   docs/DATA_SOURCES.md. Everything below depends on this.

    # TODO Step 2. Plot caseload against food shelf households, same county.

    # TODO Step 3. Event study around dated benefit changes. Levels co-move
    #   because both respond to hardship; only a benefit change separates
    #   "they move together" from "one replaces the other".
    #   Verify every event date against a primary source before using it.

    # TODO Step 4. Exposure interaction: a national benefit cut is a bigger
    #   shock in a county where more people were on SNAP to begin with.

    # TODO Step 5. Heterogeneity by metro/rural and by participation gap.


if __name__ == "__main__":
    main()
