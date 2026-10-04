"""Compare nearest food-shelf and grocery retailer distances by tract.

Run analysis.py first, then prepare_grocery_stores.py. This is a descriptive
comparison of straight-line proximity, not a measure of store quality,
capacity, eligibility, or causation.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import config as cfg
from analysis import _load_centers

STORE_POINTS = cfg.PROCESSED / "q8_grocery_store_points.parquet"
TRACT_COVERAGE = cfg.TAB / "q8_tract_coverage.csv"
TRACT_DISTANCES_OUT = cfg.PROCESSED / "q8_tract_retail_distances.parquet"
SUMMARY_OUT = cfg.TAB / "q8_retail_pattern_comparison.csv"


def _weighted_correlation(x: np.ndarray, y: np.ndarray, weights: np.ndarray) -> float:
    mean_x = np.average(x, weights=weights)
    mean_y = np.average(y, weights=weights)
    covariance = np.average((x - mean_x) * (y - mean_y), weights=weights)
    variance_x = np.average((x - mean_x) ** 2, weights=weights)
    variance_y = np.average((y - mean_y) ** 2, weights=weights)
    if variance_x <= 0 or variance_y <= 0:
        return float("nan")
    return float(covariance / np.sqrt(variance_x * variance_y))


def main() -> None:
    for path in (STORE_POINTS, TRACT_COVERAGE):
        if not path.exists():
            raise FileNotFoundError(
                f"Required input not found: {path}. Prepare store points and run "
                "`python questions/q8_lila_access/analysis.py` first."
            )

    stores = pd.read_parquet(STORE_POINTS)
    coverage = pd.read_csv(TRACT_COVERAGE, dtype={"tract_geoid": str})
    centers = _load_centers()
    centers = centers[centers["tract_geoid"].isin(coverage["tract_geoid"])].copy()
    coverage = coverage.merge(
        centers[["tract_geoid", "latitude", "longitude"]],
        on="tract_geoid",
        how="left",
        validate="one_to_one",
    )
    if coverage[["latitude", "longitude"]].isna().any(axis=None):
        raise ValueError("A covered tract is missing its Census population-center point")

    center_lon = coverage["longitude"].to_numpy(dtype=float)
    center_lat = coverage["latitude"].to_numpy(dtype=float)
    center_x, center_y = _project_coordinates(center_lon, center_lat)
    center_points = np.column_stack([center_x, center_y])
    scope_keys = (
        stores[["source", "scope"]]
        .drop_duplicates()
        .sort_values(["source", "scope"])
        .itertuples(index=False, name=None)
    )
    distance_frames = []
    for source, scope in scope_keys:
        selected = stores[
            stores["source"].eq(source) & stores["scope"].eq(scope)
        ]
        if selected.empty:
            raise ValueError(f"No store points found for {source} / {scope}")
        retailer_x, retailer_y = _project_coordinates(
            selected["longitude"].to_numpy(dtype=float),
            selected["latitude"].to_numpy(dtype=float),
        )
        retailer_xy = np.column_stack([retailer_x, retailer_y])
        nearest_miles = cdist(center_points, retailer_xy).min(axis=1) / 1609.344
        distance_frames.append(
            pd.DataFrame(
                {
                    "tract_geoid": coverage["tract_geoid"].to_numpy(),
                    "source": source,
                    "scope": scope,
                    "nearest_grocery_miles": nearest_miles,
                }
            )
        )

    distances = pd.concat(distance_frames, ignore_index=True).merge(
        coverage[
            [
                "tract_geoid",
                "population",
                "nearest_site_miles",
                "lila_class",
                "urban_rural",
            ]
        ],
        on="tract_geoid",
        how="left",
        validate="many_to_one",
    )
    if distances[["nearest_grocery_miles", "nearest_site_miles"]].isna().any(axis=None):
        raise ValueError("Retail distance comparison contains missing distances")
    distances.to_parquet(TRACT_DISTANCES_OUT, index=False)

    rows = []
    eligible = distances[
        distances["population"].gt(0)
        & distances["lila_class"].ne("Unavailable")
        & distances["urban_rural"].ne("Unavailable")
    ]
    for (source, scope, lila_class, urban_rural), group in eligible.groupby(
        ["source", "scope", "lila_class", "urban_rural"], observed=True
    ):
        source_stores = stores[
            stores["source"].eq(source) & stores["scope"].eq(scope)
        ]
        weights = group["population"].to_numpy(dtype=float)
        shelf_miles = group["nearest_site_miles"].to_numpy(dtype=float)
        grocery_miles = group["nearest_grocery_miles"].to_numpy(dtype=float)
        rows.append(
            {
                "source": source,
                "scope": scope,
                "source_date": source_stores["source_date"].iloc[0],
                "retailer_count": source_stores["store_id"].nunique(),
                "lila_class": lila_class,
                "urban_rural": urban_rural,
                "tracts": len(group),
                "population": int(weights.sum()),
                "weighted_mean_nearest_grocery_miles": np.average(
                    grocery_miles, weights=weights
                ),
                "weighted_mean_nearest_food_shelf_miles": np.average(
                    shelf_miles, weights=weights
                ),
                "weighted_mean_shelf_minus_grocery_miles": np.average(
                    shelf_miles - grocery_miles, weights=weights
                ),
                "population_within_5_mi_grocery_pct": (
                    100 * weights[grocery_miles <= 5].sum() / weights.sum()
                ),
                "population_within_5_mi_food_shelf_pct": (
                    100 * weights[shelf_miles <= 5].sum() / weights.sum()
                ),
                "weighted_distance_correlation": _weighted_correlation(
                    grocery_miles, shelf_miles, weights
                ),
            }
        )
    summary = pd.DataFrame(rows)
    SUMMARY_OUT.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(SUMMARY_OUT, index=False)
    print(f"  -> {SUMMARY_OUT.relative_to(ROOT)} ({len(summary)} rows)")
    print(summary.to_string(index=False))


def _project_coordinates(
    longitude: np.ndarray, latitude: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    from pyproj import Transformer

    transformer = Transformer.from_crs("EPSG:4326", "EPSG:26915", always_xy=True)
    x, y = transformer.transform(longitude, latitude)
    return np.asarray(x), np.asarray(y)


if __name__ == "__main__":
    main()
