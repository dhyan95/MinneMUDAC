"""
Q8 -- Low-income, low-access areas and the reach of the network.

Run from the repo root:
    python questions/q8_lila_access/analysis.py

The script reads processed and external data only. Run clean_data.py and
build_lila.py first. Site locations are represented by tract internal points;
the location-error table quantifies the maximum possible displacement within
each assigned tract. This script is limited to reproducible Q8 metrics and
supporting outputs; notebook-only exploratory follow-ups, including the rural
county-adjacency and SNAP-grocery distance splits, do not belong here.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist

import config as cfg
import qkit

POPULATION_CENTERS = (
    cfg.EXTERNAL / "census" / "gazetteer" / "CenPop2020_Mean_TR27.txt"
)
SITE_TRACT_GAZETTEER = (
    cfg.EXTERNAL / "census" / "gazetteer" / "2026_Gaz_tracts_national.txt"
)
TRACT_BOUNDARIES = (
    cfg.EXTERNAL / "census" / "tract" / "tl_2020_27_tract"
    / "tl_2020_27_tract.shp"
)
LILA_CROSSWALK = cfg.PROCESSED / "lila_tracts_2020.parquet"
SITE_WINDOW_START = 202508
LILA_FLAG = "LILATracts_halfAnd10"
LILA_FLAGS = [
    "LILATracts_halfAnd10",
    "LILATracts_1And10",
    "LILATracts_1And20",
    "LILATracts_Vehicle",
]
GROCERY_FLAGS = ["LAhalfand10", "LA1and10"]
EXCLUDED_SITE_TYPES = {"Agency or Tribal Nation"}


def require_inputs() -> None:
    for path in (
        cfg.P_SITES,
        cfg.P_SITE_MONTH,
        POPULATION_CENTERS,
        SITE_TRACT_GAZETTEER,
        TRACT_BOUNDARIES,
        LILA_CROSSWALK,
    ):
        if not path.exists():
            raise FileNotFoundError(f"Required Q8 input not found: {path}")


def _mn_sites(sites: pd.DataFrame) -> pd.DataFrame:
    return sites[
        sites["state_fips"].astype("string").eq(cfg.STATE_FIPS_MN)
    ].copy()


def _load_centers() -> pd.DataFrame:
    centers = pd.read_csv(POPULATION_CENTERS, dtype=str, encoding="utf-8-sig")
    centers["tract_geoid"] = (
        centers["STATEFP"] + centers["COUNTYFP"] + centers["TRACTCE"]
    )
    for column in ("POPULATION", "LATITUDE", "LONGITUDE"):
        centers[column] = pd.to_numeric(centers[column], errors="coerce")
    return centers.rename(
        columns={
            "POPULATION": "population",
            "LATITUDE": "latitude",
            "LONGITUDE": "longitude",
        }
    )


def _load_site_tract_points(site_tracts: pd.DataFrame) -> pd.DataFrame:
    gazetteer = pd.read_csv(
        SITE_TRACT_GAZETTEER, sep="|", dtype=str, encoding="utf-8-sig"
    )
    gazetteer.columns = gazetteer.columns.str.strip()
    gazetteer = gazetteer[gazetteer["GEOID"].str.startswith(cfg.STATE_FIPS_MN)]
    gazetteer["latitude"] = pd.to_numeric(gazetteer["INTPTLAT"], errors="coerce")
    gazetteer["longitude"] = pd.to_numeric(gazetteer["INTPTLONG"], errors="coerce")
    points = site_tracts[["tract_geoid"]].drop_duplicates().merge(
        gazetteer[["GEOID", "latitude", "longitude"]],
        left_on="tract_geoid",
        right_on="GEOID",
        how="left",
        validate="one_to_one",
    )
    if points[["latitude", "longitude"]].isna().any(axis=None):
        raise ValueError("A food-shelf site tract has no Census Gazetteer point")
    return points


def _coverage_summary(group: pd.DataFrame) -> pd.Series:
    group = group[group["population"].gt(0) & group["nearest_site_miles"].notna()]
    if group.empty:
        return pd.Series(
            {
                "tracts": 0,
                "population": 0,
                "weighted_mean_nearest_miles": np.nan,
                **{
                    f"population_within_{miles}_mi_pct": np.nan
                    for miles in (1, 5, 10)
                },
                "tracts_with_site_pct": np.nan,
            }
        )

    weights = group["population"].to_numpy(dtype=float)
    miles = group["nearest_site_miles"].to_numpy(dtype=float)
    return pd.Series(
        {
            "tracts": len(group),
            "population": int(weights.sum()),
            "weighted_mean_nearest_miles": np.average(miles, weights=weights),
            **{
                f"population_within_{cutoff}_mi_pct": 100
                * weights[miles <= cutoff].sum()
                / weights.sum()
                for cutoff in (1, 5, 10)
            },
            "tracts_with_site_pct": 100 * group["site_count"].gt(0).mean(),
        }
    )


def _location_error_bounds(
    site_tracts: pd.DataFrame, boundaries: gpd.GeoDataFrame
) -> pd.DataFrame:
    """Bound displacement from tract internal point to any point in its tract."""
    projected = boundaries.to_crs("EPSG:26915").set_index("tract_geoid")
    site_points = _load_site_tract_points(site_tracts)
    point_geometry = gpd.GeoDataFrame(
        site_points,
        geometry=gpd.points_from_xy(
            site_points["longitude"], site_points["latitude"]
        ),
        crs="EPSG:4326",
    ).to_crs("EPSG:26915")

    rows = []
    for row in point_geometry.itertuples():
        polygon = projected.loc[row.tract_geoid, "geometry"]
        point = row.geometry
        parts = list(polygon.geoms) if polygon.geom_type == "MultiPolygon" else [polygon]
        max_distance_m = 0.0
        for part in parts:
            coordinates = np.asarray(part.exterior.coords)
            distances = np.hypot(
                coordinates[:, 0] - point.x, coordinates[:, 1] - point.y
            )
            max_distance_m = max(max_distance_m, float(distances.max()))
        rows.append(
            {
                "tract_geoid": row.tract_geoid,
                "max_point_to_tract_displacement_miles": max_distance_m / 1609.344,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    require_inputs()
    print("=" * 70)
    print("Q8 -- Low-income, low-access areas and the reach of the network")
    print("=" * 70)

    # Use the shared food-shelf and reporting definition, then define current
    # operation as at least one report in the latest 12 complete months.
    shared_reporting_sites = _mn_sites(
        qkit.sites(food_shelf_only=True, reporting_only=True)
    )
    recent_shared_reporting_sites = shared_reporting_sites[
        shared_reporting_sites["last_yearmonth"].between(
            SITE_WINDOW_START, cfg.TRAIN_CUTOFF_YM
        )
    ].copy()
    reporting_sites = recent_shared_reporting_sites[
        ~recent_shared_reporting_sites["agency_type_clean"].isin(EXCLUDED_SITE_TYPES)
    ].copy()
    placeable = reporting_sites[
        reporting_sites["has_geoid"].fillna(False)
        & ~reporting_sites["geoid_is_zip_centroid"].fillna(False)
    ].copy()
    if placeable["site_id"].duplicated().any():
        raise ValueError("Site master contains duplicate food-shelf site IDs")
    print(
        f"Sites reporting in {SITE_WINDOW_START}-{cfg.TRAIN_CUTOFF_YM}: "
        f"{placeable['site_id'].nunique():,} placeable Minnesota sites"
    )

    all_mn_shelf_sites = _mn_sites(qkit.sites(food_shelf_only=True))
    site_month = qkit.site_month(food_shelf_only=True)
    site_month = site_month[
        site_month["yearmonth"].between(SITE_WINDOW_START, cfg.TRAIN_CUTOFF_YM)
    ]
    mn_activity_ids = set(all_mn_shelf_sites["site_id"])
    site_month = site_month[site_month["site_id"].isin(mn_activity_ids)]
    placeable_ids = set(placeable["site_id"])
    denominator = site_month["households_adj"].sum()
    excluded_activity_share = (
        site_month.loc[~site_month["site_id"].isin(placeable_ids), "households_adj"].sum()
        / denominator
        if denominator
        else np.nan
    )
    site_audit = pd.DataFrame(
        [
            ("MN food-shelf-like sites", all_mn_shelf_sites["site_id"].nunique()),
            (
                "MN food-shelf-like sites ever reporting",
                len(shared_reporting_sites),
            ),
            (
                "Latest-12-month reports before Q8 type exclusion",
                len(recent_shared_reporting_sites),
            ),
            (
                "Latest-12-month Agency or Tribal Nation sites excluded",
                recent_shared_reporting_sites.loc[
                    recent_shared_reporting_sites["agency_type_clean"].isin(
                        EXCLUDED_SITE_TYPES
                    ),
                    "site_id",
                ].nunique(),
            ),
            (
                "Latest-12-month reporters after type exclusion",
                len(reporting_sites),
            ),
            (
                "Latest-12-month Q8 sites without tract geoid",
                int((~reporting_sites["has_geoid"].fillna(False)).sum()),
            ),
            (
                "Latest-12-month Q8 sites with ZIP-centroid geoid",
                int(reporting_sites["geoid_is_zip_centroid"].fillna(False).sum()),
            ),
            ("Placeable sites included in coverage", len(placeable)),
            (
                "Recent-period households from sites excluded from coverage (%)",
                100 * excluded_activity_share,
            ),
        ],
        columns=["measure", "value"],
    )
    qkit.save(site_audit, "q8_site_definition_audit")

    site_counts = (
        placeable.groupby("tract_geoid")["site_id"]
        .nunique()
        .rename("site_count")
        .reset_index()
    )
    centers = _load_centers()
    centers = centers[centers["tract_geoid"].str.startswith(cfg.STATE_FIPS_MN)]
    lila = pd.read_parquet(LILA_CROSSWALK)
    required_flags = [*LILA_FLAGS, *GROCERY_FLAGS, "Urban"]
    missing_flags = set(required_flags).difference(lila.columns)
    if missing_flags:
        raise ValueError(
            "Rebuild the LILA crosswalk; missing fields: "
            + ", ".join(sorted(missing_flags))
        )
    if lila["tract_geoid"].duplicated().any():
        raise ValueError("LILA crosswalk contains duplicate 2020 tract GEOIDs")

    boundaries = gpd.read_file(TRACT_BOUNDARIES)
    boundaries["tract_geoid"] = boundaries["GEOID"].astype(str).str.zfill(11)
    boundary_ids = set(boundaries["tract_geoid"])
    if set(centers["tract_geoid"]) != boundary_ids:
        raise ValueError("Population centers and tract boundaries do not match")

    tract_points = _load_site_tract_points(placeable)
    center_geometry = gpd.GeoDataFrame(
        centers,
        geometry=gpd.points_from_xy(centers["longitude"], centers["latitude"]),
        crs="EPSG:4326",
    ).to_crs("EPSG:26915")
    site_geometry = gpd.GeoDataFrame(
        tract_points,
        geometry=gpd.points_from_xy(
            tract_points["longitude"], tract_points["latitude"]
        ),
        crs="EPSG:4326",
    ).to_crs("EPSG:26915")
    center_xy = np.column_stack(
        [center_geometry.geometry.x, center_geometry.geometry.y]
    )
    site_xy = np.column_stack([site_geometry.geometry.x, site_geometry.geometry.y])
    nearest_site_miles = cdist(center_xy, site_xy).min(axis=1) / 1609.344

    distance_data = centers[["tract_geoid", "population"]].copy()
    distance_data["nearest_site_miles"] = nearest_site_miles
    distance_data = distance_data.merge(
        lila[["tract_geoid", *required_flags]],
        on="tract_geoid",
        how="left",
        validate="one_to_one",
    )
    distance_data = distance_data.merge(
        site_counts, on="tract_geoid", how="left", validate="one_to_one"
    )
    distance_data["site_count"] = distance_data["site_count"].fillna(0).astype(int)
    distance_data["lila_class"] = (
        distance_data[LILA_FLAG]
        .map({True: "LILA", False: "Non-LILA"})
        .fillna("Unavailable")
    )
    distance_data["urban_rural"] = (
        distance_data["Urban"].map({True: "Urban", False: "Rural"}).fillna("Unavailable")
    )
    qkit.save(distance_data, "q8_tract_coverage")

    eligible = distance_data[
        distance_data["population"].gt(0)
        & distance_data["lila_class"].ne("Unavailable")
        & distance_data["urban_rural"].ne("Unavailable")
    ]
    coverage = (
        eligible.groupby(["lila_class", "urban_rural"], observed=True)
        .apply(_coverage_summary, include_groups=False)
        .reset_index()
    )
    qkit.save(coverage, "q8_population_weighted_coverage")

    sensitivity_rows = []
    for flag in LILA_FLAGS:
        group = distance_data[
            distance_data[flag].notna() & distance_data["population"].gt(0)
        ].copy()
        group = group[group[flag].astype("boolean").fillna(False)]
        summary = _coverage_summary(group)
        sensitivity_rows.append(
            {
                "definition": flag,
                "lila_tracts": len(group),
                **summary.to_dict(),
            }
        )
    sensitivity = pd.DataFrame(sensitivity_rows)
    qkit.save(sensitivity, "q8_lila_definition_sensitivity")

    grocery_rows = []
    for flag in GROCERY_FLAGS:
        for (low_access, urban), group in distance_data.groupby(
            [flag, "Urban"], dropna=False, observed=True
        ):
            group = group[group["population"].gt(0)]
            if group.empty:
                continue
            grocery_rows.append(
                {
                    "grocery_definition": flag,
                    "grocery_access": (
                        "Unavailable"
                        if pd.isna(low_access)
                        else ("Low access" if bool(low_access) else "Not low access")
                    ),
                    "urban_rural": (
                        "Unavailable"
                        if pd.isna(urban)
                        else ("Urban" if bool(urban) else "Rural")
                    ),
                    **_coverage_summary(group).to_dict(),
                }
            )
    grocery = pd.DataFrame(grocery_rows)
    qkit.save(grocery, "q8_grocery_access_comparison")

    bounds = _location_error_bounds(placeable, boundaries)
    bounds = bounds.merge(site_counts, on="tract_geoid", how="left", validate="one_to_one")
    bounds["site_count"] = bounds["site_count"].fillna(0).astype(int)
    qkit.save(bounds, "q8_tract_location_error_bounds")
    bound_summary = (
        bounds["max_point_to_tract_displacement_miles"]
        .describe(percentiles=[0.5, 0.9, 0.95])
        .rename_axis("statistic")
        .reset_index(name="miles")
    )
    qkit.save(bound_summary, "q8_location_error_bound_summary")

    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 5))
    distance_grid = np.linspace(0, 20, 201)
    for (lila_class, urban_rural), group in eligible.groupby(
        ["lila_class", "urban_rural"], observed=True
    ):
        weights = group["population"].to_numpy(dtype=float)
        miles = group["nearest_site_miles"].to_numpy(dtype=float)
        cumulative = [
            100 * weights[miles <= cutoff].sum() / weights.sum()
            for cutoff in distance_grid
        ]
        ax.plot(distance_grid, cumulative, label=f"{lila_class} - {urban_rural}")
    ax.set(
        xlabel="Straight-line miles to nearest food-shelf site",
        ylabel="Cumulative share of tract population (%)",
        title="Population-weighted distance to nearest food-shelf site",
    )
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 100)
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    output = cfg.FIG / "08_q8_population_weighted_distance.png"
    fig.savefig(output, dpi=220, bbox_inches="tight")
    plt.close(fig)
    print(f"  -> {output.relative_to(ROOT)}")

    print("\nPopulation-weighted coverage:")
    print(coverage.to_string(index=False))
    print("\nTract-point location bound (maximum displacement within assigned tract):")
    print(bound_summary.to_string(index=False))


if __name__ == "__main__":
    main()
