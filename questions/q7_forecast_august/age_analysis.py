"""
Q7 graduate addendum: explore age-group seasonality and share drift.

Run from the repo root:
    python questions/q7_forecast_august/age_analysis.py

This is exploratory only. It does not forecast age groups or modify the Q7
model. All inputs stop at the last permitted training month, July 2026.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import matplotlib.pyplot as plt
import pandas as pd

import config as cfg
import qkit

AGE_METRICS = cfg.AGE_METRICS
AGE_COLUMNS = [f"{metric}_adj" for metric in AGE_METRICS]
INDIVIDUALS_COLUMN = "individuals_adj"


def main() -> None:
    activity = qkit.site_month()
    qkit.leakage_check(activity)
    activity = activity[activity["yearmonth"].le(cfg.TRAIN_CUTOFF_YM)]
    complete = activity[AGE_COLUMNS + [INDIVIDUALS_COLUMN]].notna().all(axis=1)
    activity = activity[complete].copy()
    if activity.empty:
        raise ValueError("No complete age-group activity rows remain")

    monthly = (
        activity.groupby(["yearmonth", "year", "month"], as_index=False)[
            AGE_COLUMNS + [INDIVIDUALS_COLUMN]
        ]
        .sum()
        .sort_values("yearmonth")
    )
    age_sum = monthly[AGE_COLUMNS].sum(axis=1)
    if not age_sum.equals(monthly[INDIVIDUALS_COLUMN]):
        mismatch_count = int(age_sum.ne(monthly[INDIVIDUALS_COLUMN]).sum())
        raise ValueError(
            f"Age-group totals do not match individuals in {mismatch_count} months"
        )

    monthly["year"] = monthly["yearmonth"] // 100
    monthly["month"] = monthly["yearmonth"] % 100
    month_means = monthly.groupby("month")[AGE_COLUMNS].mean()
    overall_means = monthly[AGE_COLUMNS].mean()
    seasonal = month_means.divide(overall_means, axis="columns")
    seasonal.index.name = "calendar_month"
    seasonal = seasonal.reset_index().melt(
        id_vars="calendar_month", var_name="age_group", value_name="seasonal_index"
    )
    seasonal["age_group"] = seasonal["age_group"].str.removesuffix("_adj")
    seasonal["first_yearmonth"] = monthly["yearmonth"].min()
    seasonal["last_yearmonth"] = monthly["yearmonth"].max()
    seasonal.to_csv(cfg.TAB / "q7_age_seasonal_index.csv", index=False)
    print(f"  -> outputs/tables/q7_age_seasonal_index.csv ({len(seasonal)} rows)")

    annual = (
        monthly.groupby("year", as_index=False)[AGE_COLUMNS + [INDIVIDUALS_COLUMN]]
        .sum()
    )
    for metric, column in zip(AGE_METRICS, AGE_COLUMNS):
        annual[f"{metric}_share"] = annual[column] / annual[INDIVIDUALS_COLUMN]
    annual["period"] = annual["year"].astype(str)
    annual.loc[annual["year"].eq(2026), "period"] = "2026 Jan-Jul"
    annual.to_csv(cfg.TAB / "q7_age_annual_shares.csv", index=False)
    print(f"  -> outputs/tables/q7_age_annual_shares.csv ({len(annual)} rows)")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for metric in AGE_METRICS:
        group = seasonal[seasonal["age_group"].eq(metric)]
        axes[0].plot(
            group["calendar_month"],
            group["seasonal_index"],
            marker="o",
            label=metric.title(),
        )
        axes[1].plot(
            annual["period"],
            annual[f"{metric}_share"] * 100,
            marker="o",
            label=metric.title(),
        )
    axes[0].axhline(1, color="#666666", linewidth=1, linestyle="--")
    axes[0].set(
        title="Monthly seasonality by age group",
        xlabel="Calendar month",
        ylabel="Seasonal index (1 = average month)",
        xticks=range(1, 13),
    )
    axes[1].set(
        title="Age-group share of individuals served",
        xlabel="Year",
        ylabel="Share of individuals (%)",
    )
    axes[1].tick_params(axis="x", rotation=25)
    for ax in axes:
        ax.grid(alpha=0.25)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3,
               bbox_to_anchor=(0.5, 0.01))
    fig.suptitle("Q7 addendum: age-group patterns through July 2026")
    fig.tight_layout(rect=(0, 0.08, 1, 0.94))
    output = cfg.FIG / "07_q7_age_group_patterns.png"
    fig.savefig(output, dpi=220, bbox_inches="tight")
    plt.close(fig)
    print(f"  -> {output.relative_to(ROOT)}")
    print("\nSeasonal index:")
    print(seasonal.pivot(index="calendar_month", columns="age_group",
                         values="seasonal_index").round(3).to_string())
    print("\nAnnual shares (2026 is year-to-date through July):")
    print(annual[["period", *[f"{metric}_share" for metric in AGE_METRICS]]]
                 .set_index("period").mul(100).round(1).to_string())


if __name__ == "__main__":
    main()
