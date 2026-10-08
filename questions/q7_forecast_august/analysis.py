"""
Q7 -- Backtest and forecast August 2026 county activity.

Run from the repo root:
    python questions/q7_forecast_august/analysis.py

All forecasts and backtests use the processed panel only. The leakage check is
deliberately run before any target selection; no August 2026 data is permitted.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
import pandas as pd

import config as cfg
import qkit

BACKTEST_YEARS = (2023, 2024, 2025)
METHODS = (
    "seasonal_naive",
    "august_july_ratio",
    "seasonal_naive_drift",
    "pooled_august_july_ratio",
    "per_site_ratio",
)
POOL_PRIOR_YEARS = 2
METRICS = [*cfg.THREE_METRICS, *cfg.AGE_METRICS]


def _county_metadata() -> pd.DataFrame:
    """Use the processed county reference to retain counties with no activity."""
    counties = qkit.mmg(years=[2024])[["fips", "county_name"]].drop_duplicates()
    counties["fips"] = counties["fips"].astype("string").str.zfill(5)
    if counties["fips"].nunique() != 87:
        raise ValueError(
            "Expected 87 Minnesota counties in the processed 2024 county reference"
        )
    return counties.sort_values("fips").reset_index(drop=True)


def _historical_ratios(
    history: pd.DataFrame, metric: str, per_site: bool = False
) -> pd.DataFrame:
    """Return available county August/July ratios using only years before target."""
    rows = []
    for year in sorted(history["year"].unique()):
        july = history.loc[
            history["yearmonth"].eq(year * 100 + 7),
            ["fips", metric, "n_sites_reporting"],
        ].rename(columns={metric: "july", "n_sites_reporting": "july_sites"})
        august = history.loc[
            history["yearmonth"].eq(year * 100 + 8),
            ["fips", metric, "n_sites_reporting"],
        ].rename(columns={metric: "august", "n_sites_reporting": "august_sites"})
        paired = july.merge(august, on="fips", how="inner", validate="1:1")
        if per_site:
            denominator = paired["july"] / paired["july_sites"]
            numerator = paired["august"] / paired["august_sites"]
            paired["ratio"] = numerator / denominator.where(denominator.gt(0))
        else:
            paired["ratio"] = paired["august"] / paired["july"].where(
                paired["july"].gt(0)
            )
        paired["site_ratio"] = paired["august_sites"] / paired[
            "july_sites"
        ].where(paired["july_sites"].gt(0))
        paired["year"] = year
        rows.append(paired[["fips", "year", "ratio", "site_ratio"]])
    if not rows:
        return pd.DataFrame(columns=["fips", "year", "ratio", "site_ratio"])
    result = pd.concat(rows, ignore_index=True)
    return result.replace([np.inf, -np.inf], np.nan)


def _forecast_target(
    panel: pd.DataFrame, target_year: int, counties: pd.DataFrame
) -> pd.DataFrame:
    """Build candidate forecasts using observations strictly before August target."""
    target_ym = target_year * 100 + 8
    history = panel.loc[panel["yearmonth"].lt(target_ym)].copy()
    july = history.loc[
        history["yearmonth"].eq(target_year * 100 + 7),
        ["fips", "n_sites_reporting", *METRICS],
    ]
    prior_august = history.loc[
        history["yearmonth"].eq((target_year - 1) * 100 + 8),
        ["fips", *METRICS],
    ]
    prior_prior_august = history.loc[
        history["yearmonth"].eq((target_year - 2) * 100 + 8),
        ["fips", *METRICS],
    ]
    base = counties.merge(july, on="fips", how="left", validate="1:1")
    base = base.merge(
        prior_august, on="fips", how="left", suffixes=("", "_prior_august"),
        validate="1:1",
    )
    base = base.merge(
        prior_prior_august, on="fips", how="left",
        suffixes=("", "_prior_prior_august"), validate="1:1",
    )
    active_july = base["n_sites_reporting"].notna()

    records = []
    for metric in METRICS:
        ratios = _historical_ratios(
            history.loc[history["year"].lt(target_year)], metric
        )
        valid_ratios = ratios.loc[ratios["ratio"].notna()]
        state_ratio = valid_ratios["ratio"].median()
        if pd.isna(state_ratio):
            raise ValueError(f"No valid historical August/July ratios for {metric}")
        local = valid_ratios.groupby("fips")["ratio"].agg(["median", "count"])
        local_ratio = base["fips"].map(local["median"])
        ratio_count = base["fips"].map(local["count"]).fillna(0)
        local_ratio = local_ratio.fillna(state_ratio)
        pooled_ratio = (
            local_ratio * ratio_count + state_ratio * POOL_PRIOR_YEARS
        ) / (ratio_count + POOL_PRIOR_YEARS)

        site_ratios = _historical_ratios(
            history.loc[history["year"].lt(target_year)], metric, per_site=True
        )
        valid_metric_site_ratios = site_ratios.loc[
            site_ratios["ratio"].notna()
        ]
        valid_site_ratios = site_ratios.loc[site_ratios["site_ratio"].notna()]
        state_metric_site_ratio = valid_metric_site_ratios["ratio"].median()
        state_site_ratio = valid_site_ratios["site_ratio"].median()
        if pd.isna(state_metric_site_ratio) or pd.isna(state_site_ratio):
            raise ValueError(f"No valid per-site ratios for {metric}")
        county_metric_site_ratio = valid_metric_site_ratios.groupby("fips")[
            "ratio"
        ].median()
        county_site_ratio = valid_site_ratios.groupby("fips")[
            "site_ratio"
        ].median()
        metric_site_ratio = base["fips"].map(county_metric_site_ratio).fillna(
            state_metric_site_ratio
        )
        site_ratio = base["fips"].map(county_site_ratio).fillna(state_site_ratio)

        values = {
            "seasonal_naive": base[f"{metric}_prior_august"],
            "august_july_ratio": base[metric] * local_ratio,
            "pooled_august_july_ratio": base[metric] * pooled_ratio,
            "per_site_ratio": base[metric] * metric_site_ratio * site_ratio,
        }
        previous = base[f"{metric}_prior_august"]
        previous_previous = base[f"{metric}_prior_prior_august"]
        drift_factor = previous / previous_previous.where(
            previous_previous.gt(0)
        )
        values["seasonal_naive_drift"] = previous * drift_factor.where(
            drift_factor.notna(), 1
        )

        for method, prediction in values.items():
            frame = base[["fips", "county_name"]].copy()
            frame["target_year"] = target_year
            frame["metric"] = metric
            frame["method"] = method
            frame["prediction"] = prediction.clip(lower=0)
            frame["forecast_status"] = np.where(
                active_july, "forecasted", "no_reporting_history"
            )
            records.append(frame)
    return pd.concat(records, ignore_index=True)


def _smape(actual: pd.Series, prediction: pd.Series) -> pd.Series:
    denominator = actual.abs() + prediction.abs()
    return (200 * (actual - prediction).abs() / denominator).where(
        denominator.ne(0), 0
    )


def _score(predictions: pd.DataFrame) -> pd.DataFrame:
    usable = predictions.dropna(subset=["actual", "prediction"]).copy()
    usable["absolute_error"] = (usable["actual"] - usable["prediction"]).abs()
    usable["smape_pct"] = _smape(usable["actual"], usable["prediction"])
    rows = []
    grouped_keys = [
        (key, group)
        for key, group in usable.groupby(["target_year", "metric", "method"])
    ]
    for key, group in grouped_keys:
        rows.append(_score_row(key[0], key[1], key[2], group))
    for key, group in usable.groupby(["metric", "method"]):
        rows.append(_score_row("ALL", key[0], key[1], group))
    return pd.DataFrame(rows)


def _score_row(
    target_year: int | str, metric: str, method: str, group: pd.DataFrame
) -> dict:
    actual_sum = group["actual"].abs().sum()
    return {
        "target_year": target_year,
        "metric": metric,
        "method": method,
        "n_counties": group["fips"].nunique(),
        "macro_smape_pct": group["smape_pct"].mean(),
        "wape_pct": (
            100 * group["absolute_error"].sum() / actual_sum
            if actual_sum
            else np.nan
        ),
        "mae": group["absolute_error"].mean(),
    }


def _select_methods(scores: pd.DataFrame) -> tuple[dict[str, str], pd.DataFrame]:
    folds = scores.loc[scores["target_year"].ne("ALL")].copy()
    summary = (
        folds.groupby(["metric", "method"], as_index=False)
        .agg(
            mean_fold_smape_pct=("macro_smape_pct", "mean"),
            worst_fold_smape_pct=("macro_smape_pct", "max"),
            mean_fold_wape_pct=("wape_pct", "mean"),
            mean_fold_mae=("mae", "mean"),
            backtest_folds=("target_year", "nunique"),
        )
    )
    order = {method: index for index, method in enumerate(METHODS)}
    summary["_order"] = summary["method"].map(order).fillna(len(order))
    summary = summary.sort_values(
        ["metric", "mean_fold_smape_pct", "mean_fold_wape_pct", "_order"]
    ).drop(columns="_order")
    selected = (
        summary.drop_duplicates("metric").set_index("metric")["method"].to_dict()
    )
    return selected, summary


def _attach_actuals(
    candidates: pd.DataFrame, panel: pd.DataFrame, target_years: tuple[int, ...]
) -> pd.DataFrame:
    actual_frames = []
    for year in target_years:
        actual = panel.loc[
            panel["yearmonth"].eq(year * 100 + 8), ["fips", *METRICS]
        ].melt(id_vars="fips", var_name="metric", value_name="actual")
        actual["target_year"] = year
        actual_frames.append(actual)
    actuals = pd.concat(actual_frames, ignore_index=True)
    return candidates.merge(
        actuals, on=["target_year", "fips", "metric"], how="left", validate="m:1"
    )


def _add_age_sum_candidates(
    candidates: pd.DataFrame, age_methods: dict[str, str]
) -> pd.DataFrame:
    selected_ages = candidates.loc[
        candidates["metric"].isin(cfg.AGE_METRICS)
        & candidates.apply(
            lambda row: age_methods.get(row["metric"]) == row["method"], axis=1
        )
    ]
    age_sum = selected_ages.pivot(
        index=["target_year", "fips", "county_name"],
        columns="metric",
        values="prediction",
    ).reset_index()
    age_sum["metric"] = cfg.M_INDIVIDUALS
    age_sum["method"] = "age_group_sum"
    age_sum["prediction"] = age_sum[cfg.AGE_METRICS].sum(
        axis=1, min_count=len(cfg.AGE_METRICS)
    )
    age_sum["forecast_status"] = np.where(
        age_sum[cfg.AGE_METRICS].notna().all(axis=1),
        "forecasted",
        "no_reporting_history",
    )
    if "actual" in candidates.columns:
        actuals = (
            candidates.loc[
                candidates["metric"].eq(cfg.M_INDIVIDUALS),
                ["target_year", "fips", "actual"],
            ]
            .drop_duplicates(["target_year", "fips"])
        )
        age_sum = age_sum.merge(
            actuals, on=["target_year", "fips"], how="left", validate="1:1"
        )
    age_sum = age_sum.reindex(columns=candidates.columns)
    return pd.concat([candidates, age_sum], ignore_index=True)


def _add_intervals(
    forecasts: pd.DataFrame, backtest: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    errors = backtest.dropna(subset=["actual", "prediction"]).copy()
    errors["residual"] = errors["actual"] - errors["prediction"]
    errors["relative_residual_pct"] = np.where(
        errors["prediction"].gt(0),
        100 * errors["residual"] / errors["prediction"],
        np.nan,
    )
    summary = (
        errors.groupby("metric", as_index=False)
        .agg(
            n_backtest_rows=("residual", "size"),
            residual_q10=("residual", lambda values: values.quantile(0.10)),
            residual_q90=("residual", lambda values: values.quantile(0.90)),
            relative_error_q10_pct=(
                "relative_residual_pct", lambda values: values.quantile(0.10)
            ),
            relative_error_q90_pct=(
                "relative_residual_pct", lambda values: values.quantile(0.90)
            ),
        )
    )
    out = forecasts.merge(summary, on="metric", how="left", validate="m:1")
    lower_relative = out["prediction"] * (
        1 + out["relative_error_q10_pct"] / 100
    )
    upper_relative = out["prediction"] * (
        1 + out["relative_error_q90_pct"] / 100
    )
    lower_absolute = out["prediction"] + out["residual_q10"]
    upper_absolute = out["prediction"] + out["residual_q90"]
    out["lower_80"] = np.maximum(
        np.where(out["prediction"].gt(0), lower_relative, lower_absolute), 0
    )
    out["upper_80"] = np.maximum(
        np.where(out["prediction"].gt(0), upper_relative, upper_absolute), 0
    )
    out["upper_80"] = out[["upper_80", "lower_80"]].max(axis=1)
    return out, summary


def _add_age_share_checks(
    forecasts: pd.DataFrame, panel: pd.DataFrame
) -> pd.DataFrame:
    out = forecasts.copy()
    out["age_share_historical_min"] = np.nan
    out["age_share_historical_max"] = np.nan
    out["age_share_forecast"] = np.nan
    out["age_share_within_historical_range"] = pd.Series(
        pd.NA, index=out.index, dtype="boolean"
    )
    out["zero_after_positive_history"] = pd.Series(
        pd.NA, index=out.index, dtype="boolean"
    )
    individuals = out.loc[
        out["metric"].eq(cfg.M_INDIVIDUALS)
    ].set_index("fips")["prediction"]
    for metric in cfg.AGE_METRICS:
        historical_share = panel[metric] / panel[cfg.M_INDIVIDUALS].where(
            panel[cfg.M_INDIVIDUALS].gt(0)
        )
        bounds = historical_share.groupby(panel["fips"]).agg(["min", "max"])
        ever_positive = panel.groupby("fips")[metric].max().gt(0)
        mask = out["metric"].eq(metric)
        share = out.loc[mask, "prediction"] / out.loc[mask, "fips"].map(
            individuals
        )
        lower = out.loc[mask, "fips"].map(bounds["min"])
        upper = out.loc[mask, "fips"].map(bounds["max"])
        out.loc[mask, "age_share_forecast"] = share.to_numpy()
        out.loc[mask, "age_share_historical_min"] = lower.to_numpy()
        out.loc[mask, "age_share_historical_max"] = upper.to_numpy()
        has_history = lower.notna() & upper.notna() & share.notna()
        within_range = (share.ge(lower) & share.le(upper)).where(has_history)
        out.loc[mask, "age_share_within_historical_range"] = (
            within_range.astype("boolean").to_numpy()
        )
        positive_history = out.loc[mask, "fips"].map(ever_positive)
        zero_after_positive = (
            out.loc[mask, "prediction"].eq(0) & positive_history
        ).where(positive_history.notna())
        out.loc[mask, "zero_after_positive_history"] = (
            zero_after_positive.astype("boolean").to_numpy()
        )
    return out


def main() -> None:
    print("=" * 70)
    print("Q7 -- Backtest and forecast August 2026 activity")
    print("=" * 70)

    panel = qkit.county_month()
    qkit.leakage_check(panel)
    panel = panel.loc[panel["yearmonth"].le(cfg.TRAIN_CUTOFF_YM)].copy()
    if panel.empty or panel["yearmonth"].max() != cfg.TRAIN_CUTOFF_YM:
        raise ValueError("The county-month panel must end at the July 2026 cutoff")
    if panel[METRICS].isna().any().any():
        raise ValueError("Forecast metrics contain missing county-month values")
    if panel[METRICS].lt(0).any().any():
        raise ValueError("Forecast metrics contain negative values")
    age_sum = panel[cfg.AGE_METRICS].sum(axis=1)
    if not age_sum.equals(panel[cfg.M_INDIVIDUALS]):
        raise ValueError("Children, adults and seniors must sum to individuals")

    counties = _county_metadata()
    backtest_candidates = pd.concat(
        [
            _forecast_target(
                panel.loc[panel["yearmonth"].lt(year * 100 + 8)],
                year,
                counties,
            )
            for year in BACKTEST_YEARS
        ],
        ignore_index=True,
    )
    backtest_candidates = _attach_actuals(
        backtest_candidates, panel, BACKTEST_YEARS
    )
    independent_scores = _score(backtest_candidates)
    age_methods, _ = _select_methods(
        independent_scores.loc[
            independent_scores["metric"].isin(cfg.AGE_METRICS)
        ]
    )
    backtest_candidates = _add_age_sum_candidates(
        backtest_candidates, age_methods
    )
    scores = _score(backtest_candidates)
    selected_methods, selection_summary = _select_methods(scores)
    selected_methods[cfg.M_INDIVIDUALS] = "age_group_sum"
    selection_summary["selected_for_forecast"] = [
        selected_methods.get(metric) == method
        for metric, method in zip(
            selection_summary["metric"], selection_summary["method"]
        )
    ]

    selected_backtest = pd.concat(
        [
            backtest_candidates.loc[
                backtest_candidates["metric"].eq(metric)
                & backtest_candidates["method"].eq(method)
            ]
            for metric, method in selected_methods.items()
        ],
        ignore_index=True,
    )
    forecast_candidates = _forecast_target(
        panel, cfg.FORECAST_TARGET_YM // 100, counties
    )
    final_age_forecasts = pd.concat(
        [
            forecast_candidates.loc[
                forecast_candidates["metric"].eq(metric)
                & forecast_candidates["method"].eq(method)
            ]
            for metric, method in selected_methods.items()
            if metric in cfg.AGE_METRICS
        ],
        ignore_index=True,
    )
    forecast_candidates = _add_age_sum_candidates(
        forecast_candidates, age_methods
    )
    final_individuals = forecast_candidates.loc[
        forecast_candidates["metric"].eq(cfg.M_INDIVIDUALS)
        & forecast_candidates["method"].eq("age_group_sum")
    ]
    chosen_forecasts = pd.concat(
        [final_age_forecasts, final_individuals], ignore_index=True
    )
    for metric, method in selected_methods.items():
        if metric in cfg.AGE_METRICS:
            continue
        if metric == cfg.M_INDIVIDUALS:
            continue
        chosen_forecasts = pd.concat(
            [
                chosen_forecasts,
                forecast_candidates.loc[
                    forecast_candidates["metric"].eq(metric)
                    & forecast_candidates["method"].eq(method)
                ],
            ],
            ignore_index=True,
        )
    chosen_forecasts["selected_method"] = chosen_forecasts["method"]
    forecast_output, interval_summary = _add_intervals(
        chosen_forecasts, selected_backtest
    )
    forecast_output["forecast_as_of"] = cfg.TRAIN_CUTOFF_YM
    forecast_output["target_yearmonth"] = cfg.FORECAST_TARGET_YM
    forecast_output = _add_age_share_checks(forecast_output, panel)
    if len(forecast_output) != len(counties) * len(METRICS):
        raise ValueError("Expected one forecast row for every county and metric")
    if forecast_output.duplicated(["fips", "metric"]).any():
        raise ValueError("Forecast output contains duplicate county/metric rows")
    forecast_pivot = forecast_output.pivot(
        index="fips", columns="metric", values="prediction"
    )
    if not np.allclose(
        forecast_pivot[cfg.M_INDIVIDUALS].dropna(),
        forecast_pivot[cfg.AGE_METRICS].sum(axis=1, min_count=3).dropna(),
    ):
        raise ValueError("Individuals forecast must equal the sum of age forecasts")
    if forecast_output.loc[
        forecast_output["forecast_status"].eq("forecasted"), "prediction"
    ].isna().any():
        raise ValueError("Active counties must have a forecast for every metric")
    forecast_output = forecast_output[
        [
            "fips",
            "county_name",
            "metric",
            "prediction",
            "lower_80",
            "upper_80",
            "selected_method",
            "forecast_status",
            "forecast_as_of",
            "target_yearmonth",
            "n_backtest_rows",
            "relative_error_q10_pct",
            "relative_error_q90_pct",
            "age_share_forecast",
            "age_share_historical_min",
            "age_share_historical_max",
            "age_share_within_historical_range",
            "zero_after_positive_history",
        ]
    ].sort_values(["fips", "metric"])

    qkit.save(backtest_candidates, "q7_backtest_predictions")
    qkit.save(scores, "q7_backtest_scores")
    qkit.save(selection_summary, "q7_method_selection")
    qkit.save(forecast_output, "q7_forecasts")
    qkit.save(interval_summary, "q7_uncertainty_calibration")

    print("\nSelected forecast methods:")
    print(
        forecast_output[["metric", "selected_method"]]
        .drop_duplicates()
        .sort_values("metric")
        .to_string(index=False)
    )
    print("\nLowest mean-fold sMAPE candidate per metric; final Individuals uses age sum:")
    print(
        selection_summary.groupby("metric", as_index=False).first()[
            ["metric", "method", "mean_fold_smape_pct", "mean_fold_wape_pct"]
        ].to_string(index=False)
    )
    unavailable = forecast_output.loc[
        forecast_output["forecast_status"].eq("no_reporting_history"),
        ["fips", "county_name"],
    ].drop_duplicates()
    if not unavailable.empty:
        print("\nNo forecast is reported for counties without activity history:")
        print(unavailable.to_string(index=False))


if __name__ == "__main__":
    main()
