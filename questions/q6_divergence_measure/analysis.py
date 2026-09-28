"""
Q6 -- A divergence measure for need and demand

Owner: Valentino
Read questions/q6_divergence_measure/README.md before editing this file.

Run from the repo root:   python questions/q6_divergence_measure/analysis.py

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

import config as cfg
import qkit

OUT_PREFIX = "q6"


def main() -> None:
    print("=" * 70)
    print("Q6 -- A divergence measure for need and demand")
    print("=" * 70)

    df = qkit.county_year(years=[2024])
    sites = qkit.sites(distance_safe=True)

    # The county with a need estimate and no activity at all is the purest
    # case the question describes. Any measure we build must produce a
    # sensible need value here.
    blank = df[df["households"].isna()][["fips", "county_name", "fi_persons"]]
    print("Counties with a need estimate and zero reported activity:")
    print(blank.to_string(index=False))

    # TODO Step 1. Write the falsifiable definition of need FIRST.
    #   See questions/q6_divergence_measure/addendum.md. A rejection criterion
    #   invented after you know the answer is not a criterion.

    # TODO Step 2. Assemble need signals that are (a) independent of visits and
    #   (b) NOT already inside the Map the Meal Gap model:
    #     - distance to nearest site (block_geoid + Census Gazetteer)
    #     - no-vehicle households (ACS B08201)
    #     - SNAP participation gap (DHS caseload / MMG income-eligible FI)
    #     - senior share (ACS S0101)
    #     - school meal eligibility (MN Dept of Education)

    # TODO Step 3. Build the index. Normalise, weight, state every weight.

    # TODO Step 4. Divergence = need rank - activity rank, for EACH of the
    #   three metrics separately.

    # TODO Step 5. Explain the divergence with county characteristics, as in Q1.

    # TODO Step 6. Stability: re-rank under alternative weights. If the top ten
    #   counties change, the ranking is not a finding.


if __name__ == "__main__":
    main()
