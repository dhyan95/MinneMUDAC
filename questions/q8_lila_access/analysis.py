"""
Q8 -- Low-income, low-access areas and the reach of the network

Owner: Uddam
Read questions/q8_lila_access/README.md before editing this file.

Run from the repo root:   python questions/q8_lila_access/analysis.py

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

OUT_PREFIX = "q8"


def main() -> None:
    print("=" * 70)
    print("Q8 -- Low-income, low-access areas and the reach of the network")
    print("=" * 70)

    # Only sites we can actually place. ZIP-centroid geoids locate the middle
    # of a ZIP, not the site, so they are excluded from anything spatial.
    sites = qkit.sites(distance_safe=True)
    mn = sites[sites["state_fips"] == C.STATE_FIPS_MN]
    print(f"{len(mn)} placeable MN sites in {mn['tract_geoid'].nunique()} tracts")

    clustering = mn.groupby("tract_geoid").size().value_counts().sort_index()
    print("sites per tract:")
    print(clustering.to_string())

    # How much activity do the UNPLACEABLE sites represent? This is the honest
    # version of the "12.5% missing" limitation, and a judge will ask for it.
    sm = qkit.site_month()
    placeable = set(mn["site_id"])
    share = (sm.loc[~sm["site_id"].isin(placeable), "households_adj"].sum()
             / sm["households_adj"].sum())
    print(f"unplaceable sites account for {share:.1%} of all households served")

    # TODO Step 1. Load the USDA Food Access Research Atlas (tract-level LILA
    #   flags, 2019 data on 2010 tract boundaries).

    # TODO Step 2. Crosswalk 2010 -> 2020 tracts. THIS IS THE BIGGEST RISK IN
    #   THE QUESTION. Our geoids are 2020. Write the split/merge rule down.

    # TODO Step 3. Population-weighted coverage: what share of the people living
    #   in LILA tracts have a site within 1 / 5 / 10 miles? Weight by people,
    #   never by tract count.

    # TODO Step 4. THE REAL QUESTION: does the network repeat the retail
    #   pattern? Compare site density against grocery store density.

    # TODO Step 5. Split urban and rural LILA tracts. Half a mile and ten
    #   miles are not the same kind of "low access".

    # TODO Step 6. Limitations WITH MAGNITUDES. See the README.


if __name__ == "__main__":
    main()
