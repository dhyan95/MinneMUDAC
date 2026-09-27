"""
Build the USDA Food Access Research Atlas extract and crosswalk it to 2020 tracts.

Run from the repository root:
    python questions/q8_lila_access/build_lila.py

The Atlas contains 2019-era measures on 2010 tract boundaries. The site panel
uses 2020 tract GEOIDs, so each 2020 tract receives an area-weighted average of
its 2010 parents. A flag is true when that average is at least 0.5. This makes
splits inherit the parent flag and makes merges an explicit majority rule.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import config as C

ATLAS = C.EXTERNAL / "usda" / "FoodAccessResearchAtlasData2019.xlsx"
RELATIONSHIP = C.EXTERNAL / "census" / "relationship" / "tab20_tract20_tract10_st27.txt"
ATLAS_OUT = C.PROCESSED / "lila_tracts_2010.parquet"
LOOKUP_OUT = C.PROCESSED / "lila_variable_lookup.csv"
CROSSWALK_OUT = C.PROCESSED / "lila_tracts_2020.parquet"

LILA_FLAGS = [
    "LILATracts_halfAnd10",
    "LILATracts_1And10",
    "LILATracts_1And20",
    "LILATracts_Vehicle",
]


def load_atlas() -> pd.DataFrame:
    """Read the Atlas once, retain Minnesota, and save its dictionary."""
    if not ATLAS.exists():
        raise FileNotFoundError(f"USDA Atlas not found: {ATLAS}")

    atlas = pd.read_excel(
        ATLAS, sheet_name="Food Access Research Atlas", dtype={"CensusTract": str}
    )
    atlas = atlas[atlas["State"].eq("Minnesota")].copy()
    atlas["tract_geoid_2010"] = atlas["CensusTract"].str.zfill(11)
    atlas["fips"] = atlas["tract_geoid_2010"].str[:5]
    atlas = atlas.drop(columns=["CensusTract", "State"])

    if len(atlas) != 1334:
        raise ValueError(f"Expected 1,334 Minnesota Atlas rows, got {len(atlas)}")
    if not atlas["tract_geoid_2010"].is_unique:
        raise ValueError("Atlas 2010 tract GEOIDs are not unique")
    if not atlas["tract_geoid_2010"].str.startswith(C.STATE_FIPS_MN).all():
        raise ValueError("Atlas extract contains a non-Minnesota tract")

    lookup = pd.read_excel(ATLAS, sheet_name="Variable Lookup")
    lookup.to_csv(LOOKUP_OUT, index=False)
    atlas.to_parquet(ATLAS_OUT, index=False)
    return atlas


def crosswalk(atlas: pd.DataFrame) -> pd.DataFrame:
    """Apply the documented area-weighted 2010-parent majority rule."""
    if not RELATIONSHIP.exists():
        raise FileNotFoundError(f"Tract relationship file not found: {RELATIONSHIP}")

    rel = pd.read_csv(RELATIONSHIP, sep="|", dtype=str)
    rel = rel.rename(
        columns={
            "GEOID_TRACT_20": "tract_geoid",
            "GEOID_TRACT_10": "tract_geoid_2010",
        }
    )
    rel["area_weight"] = pd.to_numeric(rel["AREALAND_PART"], errors="coerce")
    rel = rel[["tract_geoid", "tract_geoid_2010", "area_weight"]]
    rel = rel.merge(
        atlas[["tract_geoid_2010", *LILA_FLAGS]],
        on="tract_geoid_2010",
        how="left",
        validate="many_to_one",
    )
    if rel[LILA_FLAGS].isna().all(axis=None):
        raise ValueError("No relationship rows matched the Minnesota Atlas")

    rel["area_weight"] = rel["area_weight"].fillna(0)
    grouped = rel.groupby("tract_geoid", sort=False)
    out = grouped["area_weight"].agg(
        parent_area_weight="sum", parent_count="nunique"
    ).reset_index()
    for flag in LILA_FLAGS:
        values = pd.to_numeric(rel[flag], errors="coerce")
        weighted = (rel.assign(_value=values * rel["area_weight"])
                    .groupby("tract_geoid")["_value"].sum())
        parent_weight = out.set_index("tract_geoid")["parent_area_weight"]
        share = weighted.reindex(parent_weight.index) / parent_weight
        out[f"{flag}_share"] = share.to_numpy()
        out[flag] = pd.array(
            share.ge(0.5).where(parent_weight.gt(0)), dtype="boolean"
        )

    if out["tract_geoid"].nunique() != len(out):
        raise ValueError("Crosswalk produced duplicate 2020 tract GEOIDs")
    out.to_parquet(CROSSWALK_OUT, index=False)
    return out


def main() -> None:
    atlas = load_atlas()
    out = crosswalk(atlas)
    print(f"  -> {ATLAS_OUT.relative_to(C.ROOT)} ({len(atlas)} rows)")
    print(f"  -> {LOOKUP_OUT.relative_to(C.ROOT)} ({len(pd.read_csv(LOOKUP_OUT))} rows)")
    print(f"  -> {CROSSWALK_OUT.relative_to(C.ROOT)} ({len(out)} 2020 tracts)")
    print("2020 tracts by number of 2010 parents:")
    print(out["parent_count"].value_counts().sort_index().to_string())


if __name__ == "__main__":
    main()
