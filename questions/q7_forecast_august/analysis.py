"""
Q7 -- Forecast August 2026 activity

Owner: Uddam
Read questions/q7_forecast_august/README.md before editing this file.

Run from the repo root:   python questions/q7_forecast_august/analysis.py

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

OUT_PREFIX = "q7"


def main() -> None:
    print("=" * 70)
    print("Q7 -- Forecast August 2026 activity")
    print("=" * 70)

    cm = qkit.county_month()

    # Non-negotiable. The brief disqualifies a team for using August 2026 data
    # from any source. This raises rather than warns.
    qkit.leakage_check(cm)

    # Baseline 1: seasonal naive. August 2026 = August 2025, per county.
    aug25 = cm[cm["yearmonth"] == 202508].set_index("fips")[cfg.THREE_METRICS]
    jul26 = cm[cm["yearmonth"] == cfg.TRAIN_CUTOFF_YM].set_index("fips")[cfg.THREE_METRICS]

    # Baseline 2: July 2026 times the county's historical August/July ratio.
    ratios = []
    for year in (2022, 2023, 2024, 2025):
        jul = cm[cm["yearmonth"] == year * 100 + 7].set_index("fips")[cfg.THREE_METRICS]
        aug = cm[cm["yearmonth"] == year * 100 + 8].set_index("fips")[cfg.THREE_METRICS]
        ratios.append((aug / jul).replace([np.inf, -np.inf], np.nan))
    ratio = pd.concat(ratios).groupby(level=0).median()

    baseline = pd.DataFrame(index=jul26.index)
    for m in cfg.THREE_METRICS:
        baseline[f"{m}_seasonal_naive"] = aug25[m]
        baseline[f"{m}_ratio"] = jul26[m] * ratio[m]
    baseline = baseline.reset_index()
    print(baseline.head().to_string(index=False))
    qkit.save(baseline, f"{OUT_PREFIX}_baselines")

    # TODO Step 1. Backtest on August 2023, 2024 and 2025. Train only on data
    #   strictly before each target month.

    # TODO Step 2. Pool small counties. Percentage-error metrics are dominated
    #   by counties serving a few hundred households.

    # TODO Step 3. Handle reporting composition. Forecast per reporting site
    #   and multiply by an expected site count, or carry the risk explicitly.
    #   July 2026 has 489 reporting sites, 2.8% below the trailing average.

    # TODO Step 4. Only then try a fitted model. It has to beat these baselines
    #   in the backtest or it does not go in.

    # TODO Step 5. Graduate addendum: children, seniors, adults separately.
    #   See addendum.md. The age columns sum exactly to individuals, so a
    #   share-based split is the natural first approach.


if __name__ == "__main__":
    main()
