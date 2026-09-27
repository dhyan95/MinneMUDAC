"""
Map USDA LILA tracts and food-shelf-type site presence by 2020 census tract.

Run from the repository root:
    python questions/q8_lila_access/map.py

The map shows tract-level site presence, not exact site addresses or service
areas. ZIP-centroid locations are excluded.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import pandas as pd
from shapely.geometry import box

import config as C

BOUNDARIES = (
    C.EXTERNAL / "census" / "tract" / "tl_2020_27_tract"
    / "tl_2020_27_tract.shp"
)
LILA_DATA = C.PROCESSED / "lila_tracts_2020.parquet"
OUTPUT = C.FIG / "08_q8_lila_site_presence.png"
TWIN_CITIES_OUTPUT = C.FIG / "08_q8_lila_site_presence_twin_cities.png"
LILA_FLAG = "LILATracts_halfAnd10"
TWIN_CITIES_BOUNDS = (-94.15, 44.45, -92.45, 45.45)

COLORS = {
    "LILA tract with site": "#238b8e",
    "LILA tract without site": "#e76f51",
    "Non-LILA tract with site": "#82a876",
    "Non-LILA tract without site": "#edf0f2",
    "LILA status unavailable": "#b8b8b8",
}


def draw_map(
    map_data: gpd.GeoDataFrame,
    output: Path,
    title: str,
    extent: tuple[float, float, float, float] | None = None,
) -> None:
    fig, ax = plt.subplots(figsize=(10, 9) if extent else (10, 10))
    for category, color in COLORS.items():
        subset = map_data[map_data["map_category"].eq(category)]
        if not subset.empty:
            subset.plot(
                ax=ax,
                color=color,
                linewidth=0.25 if extent else 0.12,
                edgecolor="white",
            )

    if extent:
        geographic_extent = gpd.GeoSeries(
            [box(extent[0], extent[1], extent[2], extent[3])], crs="EPSG:4326"
        ).to_crs(map_data.crs)
        xmin, ymin, xmax, ymax = geographic_extent.total_bounds
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)

    fig.suptitle(title, x=0.5, y=0.97, fontsize=15, fontweight="bold")
    fig.text(
        0.5,
        0.935,
        "2020 tract boundaries | USDA 2019 half-mile/10-mile LILA definition",
        ha="center",
        fontsize=10,
        color="#444444",
    )
    fig.legend(
        handles=[Patch(facecolor=color, edgecolor="white", label=category)
                 for category, color in COLORS.items()],
        title="Tract classification",
        loc="lower center",
        bbox_to_anchor=(0.5, 0.015),
        ncol=2,
        frameon=True,
        framealpha=0.95,
    )
    fig.text(
        0.5,
        0.105,
        "Site presence is assigned to the site's tract, not an exact address or service radius.",
        ha="center",
        fontsize=8,
        color="#444444",
    )
    ax.set_axis_off()
    fig.subplots_adjust(top=0.91, bottom=0.15)
    fig.savefig(output, dpi=220)
    plt.close(fig)


def main() -> None:
    for path in (BOUNDARIES, LILA_DATA, C.P_SITES):
        if not path.exists():
            raise FileNotFoundError(f"Required Q8 map input not found: {path}")

    tracts = gpd.read_file(BOUNDARIES)
    if "GEOID" not in tracts.columns:
        raise ValueError("TIGER/Line shapefile is missing its GEOID tract key")
    tracts["tract_geoid"] = tracts["GEOID"].astype(str).str.zfill(11)

    lila = pd.read_parquet(LILA_DATA)
    if LILA_FLAG not in lila.columns:
        raise ValueError(f"Crosswalk is missing required flag: {LILA_FLAG}")
    lila = lila[["tract_geoid", LILA_FLAG]]
    if lila["tract_geoid"].duplicated().any():
        raise ValueError("Crosswalk contains duplicate 2020 tract GEOIDs")

    sites = pd.read_parquet(C.P_SITES)
    placeable = sites[
        sites["state_fips"].astype(str).eq(C.STATE_FIPS_MN)
        & sites["has_geoid"].fillna(False).astype(bool)
        & ~sites["geoid_is_zip_centroid"].fillna(False).astype(bool)
        & sites["AgencyType"].isin(C.FOOD_SHELF_TYPES)
    ]
    site_counts = (
        placeable.groupby("tract_geoid")["site_id"]
        .nunique()
        .rename("site_count")
        .reset_index()
    )

    map_data = tracts.merge(lila, on="tract_geoid", how="left", validate="one_to_one")
    map_data = map_data.merge(
        site_counts, on="tract_geoid", how="left", validate="one_to_one"
    )
    map_data["site_count"] = map_data["site_count"].fillna(0).astype(int)
    has_site = map_data["site_count"].gt(0)
    known_lila = map_data[LILA_FLAG].notna()

    map_data["map_category"] = "LILA status unavailable"
    map_data.loc[known_lila & map_data[LILA_FLAG].astype("boolean").fillna(False) & has_site,
                 "map_category"] = "LILA tract with site"
    map_data.loc[known_lila & map_data[LILA_FLAG].astype("boolean").fillna(False) & ~has_site,
                 "map_category"] = "LILA tract without site"
    map_data.loc[known_lila & ~map_data[LILA_FLAG].astype("boolean").fillna(False) & has_site,
                 "map_category"] = "Non-LILA tract with site"
    map_data.loc[known_lila & ~map_data[LILA_FLAG].astype("boolean").fillna(False) & ~has_site,
                 "map_category"] = "Non-LILA tract without site"

    if map_data.crs is None:
        raise ValueError("TIGER/Line tract file has no coordinate reference system")
    map_data = map_data.to_crs("EPSG:26915")

    draw_map(
        map_data,
        OUTPUT,
        "Minnesota food shelves and low-income, low-access tracts",
    )
    draw_map(
        map_data,
        TWIN_CITIES_OUTPUT,
        "Twin Cities food shelves and low-income, low-access tracts",
        extent=TWIN_CITIES_BOUNDS,
    )

    print(f"Saved {OUTPUT.relative_to(C.ROOT)}")
    print(f"Saved {TWIN_CITIES_OUTPUT.relative_to(C.ROOT)}")
    print(f"Tracts: {len(map_data)}; tracts with a placeable food-shelf-type site: "
          f"{int(has_site.sum())}; LILA status unavailable: {int((~known_lila).sum())}")


if __name__ == "__main__":
    main()
