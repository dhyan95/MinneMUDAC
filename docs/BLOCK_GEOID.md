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
  join our sites' `tract_geoid` to the Atlas's tract flag and ask how many LILA tracts
  have a site.
- **Block group (12 digits)** — the finest grain at which the ACS publishes income,
  vehicle access and population. Useful for Q6's need index if we want sub-county detail.
- **Block (15 digits)** — too fine for any published statistic, but it is the level that
  has a **published latitude and longitude centroid**, which is how we get distance.

---

## 3. Getting distance out of it

We have no coordinates. We can get them, and this is the single most valuable external
file to download.

1. Download the **2020 Census Block Assignment / Gazetteer** file for Minnesota:
   `https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2020_Gazetteer/` →
   `2020_Gaz_blocks_27.txt` (tab-separated, includes `INTPTLAT` and `INTPTLONG`, the
   internal point of every block in Minnesota).
2. Save it to `data/external/census/` and record it in [DATA_SOURCES.md](DATA_SOURCES.md).
3. Join on the 15-digit `GEOID` to get a lat/long per site.
4. Do the same for every **tract** centroid (`2020_Gaz_tracts_27.txt`), then compute
   great-circle distance from each tract centroid to the nearest site.

That gives you "distance to nearest food shelf" per tract, which Question 1 asks for
explicitly as a county characteristic, and which Question 8 needs as its access measure.

**Three warnings, all of which belong on the limitations slide:**

- A block centroid is a **point inside a polygon**, not a door. In rural Minnesota a
  block can be several square miles, so the error is meaningful exactly where the
  distances are largest.
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

For Q8 this is a real limitation, and the honest way to state it is not "12.5% missing"
but: *how much activity do the missing sites represent, and are they systematically
rural?* We already know the first half — `questions/q8_lila_access/analysis.py` computes
it, and the unplaceable sites account for only **0.9% of all households served**. That is
a much better answer than a percentage of rows, and it makes the limitation small rather
than vague. Still check whether they are disproportionately rural, because that would
bias the coverage estimate in a specific direction.

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
2020 tracts, both children inherit the parent's flag; where several merge, you have to
decide (population-weighted majority is the defensible choice) and write the decision
down.

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
