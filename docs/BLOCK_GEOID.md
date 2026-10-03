# How to use `block_geoid`

`block_geoid` is on the `Organization` table. It is the single most useful field in the
whole extract for Question 8, and the easiest one to break. This page explains what it
is, how to use it, and the three ways it goes wrong.

---

## 1. What it is

The Food Group did not give us site addresses — that would identify the sites. Instead
they geocoded each address and gave us the **2020 Census block** it falls in, as a
**15-digit GEOID**.

A GEOID is not an ID you look up. It is **built by concatenation**, so every larger
geography is literally a prefix of the string:

```
   2 7   0 5 3   0 2 6 8 0 7   7 0 0 9
   └─┬─┘ └──┬──┘ └────┬────┘ └──┬──┘
     │      │         │         │
     │      │         │         └── block          4 digits   ~ a city block
     │      │         └──────────── tract          6 digits   ~ 1,200-8,000 people
     │      └────────────────────── county         3 digits
     └───────────────────────────── state          2 digits   27 = Minnesota
```

So `270530268077009` is block 7009, in tract 026807, in county 053 (Hennepin), in state
27 (Minnesota).

**To get a larger geography, truncate the string. Never parse, never look up.**

| you want | take | example | length |
|---|---|---|---|
| state | first 2 | `27` | 2 |
| **county FIPS** | first 5 | `27053` | 5 |
| **census tract** | first 11 | `27053026807` | 11 |
| block group | first 12 | `270530268077` | 12 |
| block | all 15 | `270530268077009` | 15 |

This is already done for you. `src/geography.py::split_block_geoid()` returns
`state_fips`, `fips`, `tract_geoid` and `bg_geoid`, and those columns are already on
`data/processed/sites.parquet` and `data/processed/site_month.parquet`.

```python
import pandas as pd
sites = pd.read_parquet("data/processed/sites.parquet")
sites[["site_id", "block_geoid", "fips", "tract_geoid"]].head()
```

---

## 2. Why each level matters to us

- **County (5 digits)** — the join key for Map the Meal Gap, SNAP caseloads, Census
  county estimates, USDA rural codes. Every question except Q8 lives at this grain.
- **Tract (11 digits)** — the grain the **USDA Food Access Research Atlas** uses. LILA
  (low-income, low-access) status is a *tract* flag. This is the whole of Question 8:
  crosswalk the Atlas's 2010 tract flags to our 2020 `tract_geoid`s, then ask how many
  LILA tracts have a food-shelf site.
- **Block group (12 digits)** — the finest grain at which the ACS publishes income,
  vehicle access and population. Useful for Q6's need index if we want sub-county detail.
- **Block (15 digits)** — too fine for any published statistic. The block GEOID
  identifies the block, but this project does not have a block-level coordinate file.

---

## 3. Getting distance out of it

The Census 2020 Gazetteer directory does **not** contain the previously documented
`2020_Gaz_blocks_27.txt` file. The project has tract internal-point coordinates, not
site coordinates. Q8 therefore places sites at the Census internal point of their
assigned tract and computes the maximum distance from that point to the tract boundary
as a conservative within-tract displacement bound. This is not the observed site error;
the actual block point is unavailable in the downloaded sources.

The official tract Gazetteer entry is in `data/external/census/gazetteer/`. Minnesota
tract polygons in `data/external/census/tract/tl_2020_27_tract/` are used to calculate
the bound. The block GEOID still identifies the assigned tract, but does not itself
supply a latitude or longitude.

**Three warnings, all of which belong on the limitations slide:**

- A tract internal point is **not the site address**. The upper-bound displacement
  reported by `questions/q8_lila_access/analysis.py` may be large in rural Minnesota,
  and does not reveal where inside the tract the site actually lies.
- Great-circle distance is **not drive time**. Rural Minnesota has lakes. A site 8 miles
  away across Mille Lacs is not 8 miles away.
- Distance says nothing about **hours, capacity or eligibility**. A site open four hours
  a month is not equivalent to one open daily, and the data does not tell us which is
  which.

---

## 4. The three ways it breaks

### 4.1 It is not a number — read it as text

Excel and pandas will read `270530268077009` as a float. That gives you
`270530268077009.0`, and the `.0` silently poisons every string join. For states with a
FIPS below 10 (Alabama is `01`) the leading zero disappears entirely and the county code
shifts by one character — a bug that produces *plausible wrong answers* rather than an
error.

Always read it as string:

```python
pd.read_excel(path, dtype={"block_geoid": "string"})
```

`src/geography.py::clean_geoid()` handles the coercion, strips a trailing `.0`, rejects
anything non-numeric, and zero-pads to 15. Use it rather than writing your own.

### 4.2 12.5% of organizations have no geoid at all — 150 of 1,202

Blank means either no address was on file or the address could not be matched. Those
sites carry `has_geoid = False` and **cannot appear in any tract-level result**.

For Q8 the useful limitation is the share of recent household activity at sites excluded
from the distance analysis, not the percentage of all master rows. The
`q8_site_definition_audit.csv` output from `questions/q8_lila_access/analysis.py`
reports this directly for the selected 12-month window.

### 4.3 12 geoids are ZIP centroids, not addresses

`is_zip_centroid = TRUE` (carried through as `geoid_is_zip_centroid`) means the block is
real but it locates the **middle of the ZIP code**, not the site. The county is still
right. The tract is probably right in a city and probably wrong in a rural ZIP, which can
span several tracts.

**Rule:** keep them for county work, exclude them from distance work, and say so.

### 4.4 A related trap: the vintage mismatch

Our geoids are **2020** census geography. The USDA Food Access Research Atlas currently
published is built on **2019 data mapped to 2010 census tracts**. 2010 and 2020 tract
boundaries are not the same — Minnesota's tracts were split and merged in the 2020
redistricting.

You cannot join a 2020 tract GEOID to a 2010 tract flag and expect a correct answer. You
need the Census **2010→2020 tract relationship file**
(`https://www.census.gov/geographies/reference-files/time-series/geo/relationship-files.html`),
which gives the overlap between old and new tracts. Where one 2010 tract splits into two
2020 tracts, each inherits the parent's value. For a 2020 tract with multiple 2010
parents, this project computes an **area-weighted average** using the Census land-area
overlap and classifies a flag as true at a weighted share of at least 0.5. It is not
population-weighted; the relationship file supplies land overlap, not population by
overlap. See `questions/q8_lila_access/README.md` for the 5% significant-parent count
used to describe boundary changes.

This is the single biggest methodological risk in Question 8. Budget time for it.

---

## 5. Quick reference

```python
import sys; sys.path.insert(0, "src")
import geography as geo
import pandas as pd

sites = pd.read_parquet("data/processed/sites.parquet")

# county of each site (already a column, but this is how it is derived)
geo.split_block_geoid(sites["block_geoid"])["fips"]

# only sites we can safely use for distance work
usable = sites[sites["has_geoid"] & ~sites["geoid_is_zip_centroid"]]

# how many distinct tracts contain at least one site
sites.loc[sites["has_geoid"], "tract_geoid"].nunique()
```

As of the current extract: **1,052 of 1,202** organizations have a geoid, and the
1,051 geocoded Minnesota sites sit in just **512 distinct census tracts**, out of roughly
1,500 tracts in the state — and 325 of those 512 tracts hold more than one site (one holds
eight). Most of Minnesota's tracts contain no site at all — which is
the premise of Question 8, and worth putting on a slide as a single number.
