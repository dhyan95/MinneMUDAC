"""
Q1 -- Need estimates against observed activity

Owner: Valentino
Read questions/q1_need_vs_activity/README.md before editing this file.

Run from the repo root:   python questions/q1_need_vs_activity/analysis.py

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

OUT_PREFIX = "q1"


def main() -> None:
    print("=" * 70)
    print("Q1 -- Need estimates against observed activity")
    print("=" * 70)

    # Step 1. County-year frame: activity + Map the Meal Gap, 2022-2024.
    df = qkit.county_year(years=cfg.Q1_YEARS)
    print(f"{len(df)} county-years, {df['fips'].nunique()} counties")

    # Step 2. Public covariates (build with: python src/build_covariates.py).
    cov = qkit.covariates(years=cfg.Q1_YEARS).drop(columns="county_name")
    df = df.merge(cov, on=["fips", "year"], how="left", validate="1:1")
    for m in cfg.THREE_METRICS:
        df[f"{m}_per_1k"] = 1000 * df[m] / df["population"]

    # Step 3. Correlations: each metric against need, counts AND rates, per year.
    rows = []
    for year in cfg.Q1_YEARS:
        sub = df[df["year"] == year].dropna(subset=["fi_persons"])
        for m in cfg.THREE_METRICS:
            s = sub.dropna(subset=[m])
            rows.append({
                "year": year, "metric": m, "n_counties": len(s),
                "pearson_counts": s[m].corr(s["fi_persons"]),
                "spearman_counts": s[m].corr(s["fi_persons"], method="spearman"),
                "spearman_rate": s[f"{m}_per_fi"].corr(s["fi_rate"], method="spearman"),
            })
    corr = pd.DataFrame(rows).round(3)
    print(corr.to_string(index=False))
    qkit.save(corr, f"{OUT_PREFIX}_correlations")

    # TODO Step 4. Residuals from log activity on log food-insecure persons.
    #   Rank them. The tails are the breakdown counties the brief asks for.

    # TODO Step 5. Regress the residuals on county characteristics.
    #   Keep it small: 87 counties will not support a large model.
    #   Prefer covariates that are NOT inputs to the Map the Meal Gap model.


if __name__ == "__main__":
    main()
