"""
Q4 -- Food prices and food shelf activity

Owner: Dhyan
Read questions/q4_food_prices/README.md before editing this file.

Run from the repo root:   python questions/q4_food_prices/analysis.py

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

OUT_PREFIX = "q4"


def main() -> None:
    print("=" * 70)
    print("Q4 -- Food prices and food shelf activity")
    print("=" * 70)

    cm = qkit.county_month()
    qkit.leakage_check(cm)

    # Step 1. Statewide monthly series, all three metrics.
    state = cm.groupby("yearmonth")[cfg.THREE_METRICS].sum().reset_index()
    state["n_sites"] = cm.groupby("yearmonth")["n_sites_reporting"].sum().values
    print(state.tail(6).to_string(index=False))

    # TODO Step 2. Load BLS CPI food-at-home, Midwest (CUUR0200SAF11).
    #   Truncate at 2026-07 BEFORE saving into data/external/bls/.
    #   cpi = pd.read_csv(cfg.EXTERNAL / "bls" / "cpi_food_at_home_midwest.csv")
    #   qkit.leakage_check(cpi)

    # TODO Step 3. Year-over-year changes, not levels. Both series trend up,
    #   so a correlation in levels is spurious by construction.

    # TODO Step 4. Distributed lag: activity YoY on CPI YoY at lags 0..6,
    #   with month-of-year effects. Report the lag profile for each metric.

    # TODO Step 5. Residual seasonality once price is in the model.
    #   Compare against outputs/tables/02_seasonal_index.csv.

    # TODO Step 6. County heterogeneity via cost_per_meal (county, annual).
    #   One Midwest CPI series cannot identify a cross-county price effect.


if __name__ == "__main__":
    main()
