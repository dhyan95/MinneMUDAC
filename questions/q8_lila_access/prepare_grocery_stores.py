"""Prepare local SNAP and OpenStreetMap grocery locations for Q8.

Keep the original downloads outside Git. Example:
    python questions/q8_lila_access/prepare_grocery_stores.py \
        --snap-csv "/path/to/Historical SNAP Retailer Locator Data 2005-2025.csv" \
        --osm-dir "/path/to/minnesota-261003-free"
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import config as cfg

SNAP_AS_OF = pd.Timestamp("2025-12-31")
MN_BOUNDS = (-97.5, 43.0, -89.0, 50.0)
OUTPUT = cfg.PROCESSED / "q8_grocery_store_points.parquet"

LARGE_GROCERY_TYPES = {
    "Supermarket",
    "Super Store",
    "Large Grocery Store",
}
ADDITIONAL_GROCERY_TYPES = {
    "Medium Grocery Store",
    "Small Grocery Store",
    "Combination Grocery/Other",
}


def _snap_locations(path: Path) -> pd.DataFrame:
    columns = [
        "Record ID",
        "Store Name",
        "Store Type",
        "State",
        "Latitude",
        "Longitude",
        "Authorization Date",
        "End Date",
    ]
    stores = pd.read_csv(path, usecols=columns, dtype=str, low_memory=False)
    stores = stores[stores["State"].str.strip().eq("MN")].copy()
    stores["authorization_date"] = pd.to_datetime(
        stores["Authorization Date"].str.strip(),
        format="%m/%d/%Y",
        errors="coerce",
    )
    stores["end_date"] = pd.to_datetime(
        stores["End Date"].str.strip(),
        format="%m/%d/%Y",
        errors="coerce",
    )
    stores = stores[
        stores["authorization_date"].le(SNAP_AS_OF)
        & (stores["end_date"].isna() | stores["end_date"].ge(SNAP_AS_OF))
    ].copy()
    stores["latitude"] = pd.to_numeric(stores["Latitude"], errors="coerce")
    stores["longitude"] = pd.to_numeric(stores["Longitude"], errors="coerce")
    min_lon, min_lat, max_lon, max_lat = MN_BOUNDS
    valid_coordinates = (
        stores["latitude"].between(min_lat, max_lat)
        & stores["longitude"].between(min_lon, max_lon)
    )
    if (~valid_coordinates).any():
        raise ValueError(
            f"{int((~valid_coordinates).sum())} active Minnesota SNAP retailers "
            "have missing or out-of-state coordinates"
        )
    if stores["Record ID"].isna().any() or stores["Record ID"].duplicated().any():
        raise ValueError("Active Minnesota SNAP retailer IDs must be present and unique")

    stores["store_name"] = stores["Store Name"].fillna("").str.strip()
    stores["store_type"] = stores["Store Type"].fillna("").str.strip()
    stores["store_id"] = "SNAP:" + stores["Record ID"].astype(str).str.strip()
    scopes = []
    for scope, store_types in (
        ("large_grocery", LARGE_GROCERY_TYPES),
        ("broad_grocery", LARGE_GROCERY_TYPES | ADDITIONAL_GROCERY_TYPES),
    ):
        selected = stores[stores["store_type"].isin(store_types)].copy()
        selected["source"] = "USDA SNAP Retailer Locator"
        selected["scope"] = scope
        selected["source_date"] = SNAP_AS_OF.date().isoformat()
        scopes.append(
            selected[
                [
                    "source",
                    "scope",
                    "store_id",
                    "store_name",
                    "store_type",
                    "latitude",
                    "longitude",
                    "source_date",
                ]
            ]
        )
    return pd.concat(scopes, ignore_index=True)


def _normalized_name(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.casefold().split())


def _osm_locations(directory: Path) -> pd.DataFrame:
    point_path = directory / "gis_osm_pois_free_1.shp"
    area_path = directory / "gis_osm_pois_a_free_1.shp"
    missing = [path for path in (point_path, area_path) if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "OSM point and area POI layers are both required: "
            + ", ".join(str(path) for path in missing)
        )

    points = gpd.read_file(
        point_path,
        columns=["osm_id", "fclass", "name"],
        engine="pyogrio",
    )
    points = points[points["fclass"].eq("supermarket")].copy()
    points["geometry_source"] = "point"

    areas = gpd.read_file(
        area_path,
        columns=["osm_id", "fclass", "name"],
        engine="pyogrio",
    )
    areas = areas[areas["fclass"].eq("supermarket")].copy()
    areas = areas.to_crs("EPSG:26915")
    areas["geometry"] = areas.geometry.representative_point()
    areas = areas.to_crs("EPSG:4326")
    areas["geometry_source"] = "area"

    stores = pd.concat([points, areas], ignore_index=True).reset_index(drop=True)
    stores = gpd.GeoDataFrame(stores, geometry="geometry", crs="EPSG:4326")
    if stores["osm_id"].isna().any() or stores["osm_id"].duplicated().any():
        raise ValueError("OSM supermarket feature IDs must be present and unique")

    stores["_normalized_name"] = stores["name"].map(_normalized_name)
    stores["_point_priority"] = stores["geometry_source"].map({"point": 0, "area": 1})
    projected = stores.to_crs("EPSG:26915")
    keep = np.ones(len(stores), dtype=bool)
    positions = pd.Series(np.arange(len(stores)), index=stores.index)
    for _, group in stores[stores["_normalized_name"].ne("")].groupby(
        "_normalized_name", sort=False
    ):
        ordered = group.sort_values(
            ["_point_priority", "osm_id"], kind="stable"
        ).index.tolist()
        accepted: list[int] = []
        for index in ordered:
            point = projected.loc[index, "geometry"]
            if any(point.distance(projected.loc[prior, "geometry"]) <= 100
                   for prior in accepted):
                keep[positions.loc[index]] = False
            else:
                accepted.append(index)
    stores = stores.iloc[np.flatnonzero(keep)].copy()
    stores["store_id"] = "OSM:" + stores["osm_id"].astype(str)
    stores["store_name"] = stores["name"].fillna("").str.strip()
    stores["store_type"] = "supermarket"
    stores["source"] = "OpenStreetMap via Geofabrik Minnesota extract"
    stores["scope"] = "osm_supermarket"
    readme_path = directory / "README"
    readme = readme_path.read_text(encoding="utf-8")
    date_match = re.search(r"as of (\d{4}-\d{2}-\d{2})T", readme)
    if not date_match:
        raise ValueError(f"Could not read OSM snapshot date from {readme_path}")
    stores["source_date"] = date_match.group(1)
    stores["longitude"] = stores.geometry.x
    stores["latitude"] = stores.geometry.y
    min_lon, min_lat, max_lon, max_lat = MN_BOUNDS
    in_state = (
        stores["latitude"].between(min_lat, max_lat)
        & stores["longitude"].between(min_lon, max_lon)
    )
    if not in_state.all():
        raise ValueError("OSM supermarket coordinates fall outside Minnesota bounds")
    return pd.DataFrame(
        stores[
            [
                "source",
                "scope",
                "store_id",
                "store_name",
                "store_type",
                "latitude",
                "longitude",
                "source_date",
            ]
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snap-csv", required=True, type=Path)
    parser.add_argument("--osm-dir", required=True, type=Path)
    args = parser.parse_args()
    for path in (args.snap_csv, args.osm_dir):
        if not path.exists():
            raise FileNotFoundError(f"Source path not found: {path}")

    snap = _snap_locations(args.snap_csv)
    osm = _osm_locations(args.osm_dir)
    stores = pd.concat([snap, osm], ignore_index=True)
    if stores[["latitude", "longitude"]].isna().any(axis=None):
        raise ValueError("Prepared grocery dataset contains missing coordinates")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    stores.to_parquet(OUTPUT, index=False)
    print(f"Prepared {len(stores):,} grocery locations -> {OUTPUT.relative_to(ROOT)}")
    print(
        stores.groupby(["source", "scope"], observed=True)
        .agg(stores=("store_id", "nunique"))
        .to_string()
    )
    print("Original CSV and shapefiles were read only; they were not modified.")


if __name__ == "__main__":
    main()
