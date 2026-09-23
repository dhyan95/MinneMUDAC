"""
qkit.py -- the small toolkit every question script imports.

The point is that all six questions load the same tables the same way, so two
people cannot quietly answer two questions off two different versions of the
numbers.

Typical opening of a question script:

    import sys; sys.path.insert(0, "src")
    import qkit

    cm = qkit.county_month()                 # county x month panel
    need = qkit.mmg(years=[2023, 2024])      # Map the Meal Gap
    df = qkit.county_year(years=[2023, 2024])  # activity + need, joined, ready
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C


# ------------------------------------------------------------------ loaders
def site_month(clean_only: bool = False, food_shelf_only: bool = False) -> pd.DataFrame:
    """
    Site x month activity.

    clean_only       drop rows failing a quality check (default: keep them, use *_adj)
    food_shelf_only  keep only brick-and-mortar / food-shelf-like site types
    """
    d = pd.read_parquet(C.P_SITE_MONTH)
    d = d[~d["bad_period"] & ~d["is_duplicate_superseded"]]
    if clean_only:
        d = d[d["is_clean"]]
    if food_shelf_only:
        d = d[d["is_food_shelf_like"]]
    return d


def county_month(food_shelf_only: bool = False) -> pd.DataFrame:
    """
    County x month panel, keyed on 5-digit FIPS.

    With food_shelf_only=True the three metrics are swapped for the
    food-shelf-only versions, so downstream code does not change.
    """
    d = pd.read_parquet(C.P_COUNTY_MONTH)
    if food_shelf_only:
        for m in C.THREE_METRICS:
            d[m] = d[f"{m}_fs"]
    return d


def sites(geocoded_only: bool = False, distance_safe: bool = False) -> pd.DataFrame:
    """
    Site master.

    distance_safe  also drops the 12 sites whose geoid is a ZIP centroid, which
                   locates the middle of the ZIP rather than the site.
    """
    d = pd.read_parquet(C.P_SITES)
    if geocoded_only or distance_safe:
        d = d[d["has_geoid"]]
    if distance_safe:
        d = d[~d["geoid_is_zip_centroid"]]
    return d


def mmg(years: list[int] | None = None) -> pd.DataFrame:
    """Map the Meal Gap, MN counties. 2023 and earlier come from the 2025
    edition, 2024 from the 2026 edition. Do not average the two editions."""
    d = pd.read_parquet(C.P_MMG)
    if years:
        d = d[d["year"].isin(years)]
    return d


def calls(food_only: bool = False, exclude_snap_rx: bool = False,
          geocoded_only: bool = False) -> pd.DataFrame:
    """
    Call log.

    exclude_snap_rx  drops clinic-pushed referrals (31% of calls). Their volume
                     tracks clinic enrolment, not household demand, so they
                     should almost always be excluded from a demand signal.
    """
    d = pd.read_parquet(C.P_CALLS)
    d = d[~d["sparse_period"]]
    if food_only:
        d = d[d["is_food_related"]]
    if exclude_snap_rx:
        d = d[~d["is_snap_rx"]]
    if geocoded_only:
        d = d[d["fips"].notna()]
    return d


def marketbucks() -> pd.DataFrame:
    return pd.read_parquet(C.P_MARKETBUCKS)


# --------------------------------------------------------------- derived frames
def county_year(years: list[int] | None = None, food_shelf_only: bool = False) -> pd.DataFrame:
    """
    Activity aggregated to county-year, joined to Map the Meal Gap.

    This is the frame Q1 and Q6 both want. It is an OUTER join on purpose: a
    county with a need estimate and no activity at all (Wilkin) has to survive
    the join, because that county is the whole point of Question 6.
    """
    cm = county_month(food_shelf_only=food_shelf_only)
    if years:
        cm = cm[cm["year"].isin(years)]
    act = (cm.groupby(["fips", "county_name", "year"])[C.THREE_METRICS]
             .sum().reset_index())
    act["months_observed"] = (cm.groupby(["fips", "county_name", "year"])["yearmonth"]
                                .nunique().values)
    need = mmg(years)
    out = act.merge(need, on=["fips", "year"], how="outer", suffixes=("", "_mmg"))
    # Wilkin has a need estimate and no activity at all, so its name only exists
    # on the need side of the join. Coalesce rather than lose the row's label.
    out["county_name"] = out["county_name"].fillna(out["county_name_mmg"])
    out = out.drop(columns=["county_name_mmg"])
    for m in C.THREE_METRICS:
        out[f"{m}_per_fi"] = out[m] / out["fi_persons"]
    return out


def leakage_check(df: pd.DataFrame, date_col: str = "yearmonth") -> None:
    """
    Raise if a frame contains anything at or after the forecast target month.

    Call this in every Q7 script, and in any script that loads an external
    monthly series. The brief disqualifies a team for using August 2026 data
    from any source, so this is cheap insurance.
    """
    if date_col not in df.columns:
        raise KeyError(f"leakage_check: no column {date_col!r} to check")
    bad = df[df[date_col] >= C.FORECAST_TARGET_YM]
    if len(bad):
        raise ValueError(
            f"LEAKAGE: {len(bad)} rows at or after {C.FORECAST_TARGET_YM}. "
            f"The brief disqualifies a team for using August 2026 data from any source. "
            f"Truncate the source at {C.TRAIN_CUTOFF_YM} before saving it.")
    print(f"leakage_check passed: nothing at or after {C.FORECAST_TARGET_YM}")


def save(df: pd.DataFrame, name: str) -> None:
    """Write a result table to outputs/tables/ under a question-prefixed name."""
    path = C.TAB / f"{name}.csv"
    df.to_csv(path, index=False)
    print(f"  -> outputs/tables/{name}.csv  ({len(df)} rows)")
