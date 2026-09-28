# Q8 — Low-income, low-access areas and the reach of the network

**Division: graduate only.** No other division answers this. It is the clearest chance to
show work the other divisions cannot.
**Owner:** Uddam
**Status:** foundation in progress — Atlas extract and tract crosswalk built

---

## The ask, in our words

Some areas have many low-income households and poor access to a grocery store. USDA calls
these **LILA** tracts (low-income, low-access); older sources say *food desert*.

1. Does the food shelf network **sufficiently reach** these areas?
2. Does the network **fill the retail gap**, or does it **repeat the same pattern as the
   retail market**?
3. Like Q1, investigate **differences across locations**.
4. **Discuss the limitations** of your outcomes — the brief asks for this explicitly, so
   it is graded, not optional.

Question 2 is the interesting one. If food shelves sit where grocery stores already are,
then the charitable network mirrors the retail market and leaves the same gaps. If they
sit where stores are not, the network is doing something the market does not.

---

## Data

| what | where | grain | vintage |
|---|---|---|---|
| site locations | `data/processed/sites.parquet` → `tract_geoid` | **2020** census tract | current |
| LILA flags | USDA ERS **Food Access Research Atlas** | census tract | **2019 data on 2010 tracts** |
| tract↔tract crosswalk | Census **2010→2020 tract relationship file** | tract | **required** |
| tract centroids | Census **2020 Gazetteer** `2020_Gaz_tracts_27.txt` | tract | current |
| tract population / poverty | ACS 5-year | tract | rolling 5-year |

Read [BLOCK_GEOID.md](../../docs/BLOCK_GEOID.md) before writing a line of code. The whole
question runs on that field.

---

## Approach

1. **Get the crosswalk right first.** Our geoids are 2020, the Atlas is 2010. This is the
   single biggest methodological risk in the question and it must be solved before
   anything else. Where a 2010 tract splits, both children inherit the flag; where tracts
   merge, take the population-weighted majority — and **write the rule down**.
2. **Place the sites.** `tract_geoid` is already on `sites.parquet`. Exclude the 12 ZIP
   centroid geoids from any distance work. The 150 sites without a geoid cannot enter
   this analysis at all.
3. **The simple coverage number, first.** What share of Minnesota's LILA tracts contain a
   site? What share have a site within 1, 5, 10 miles? Weight by **population**, not by
   tract count — a tract is not a person.
4. **The retail-pattern comparison — this is the real question.** Compare the
   distribution of food shelves against the distribution of grocery stores. If both are
   concentrated in the same tracts, the network repeats the retail pattern. Quantify it:
   correlation of site density with store density, or a like-for-like coverage rate for
   LILA and non-LILA tracts.
5. **Differences across locations.** Urban LILA tracts (low access means half a mile)
   behave nothing like rural LILA tracts (ten miles). Split them and report separately —
   USDA's own flags come in both distance definitions (`LILATracts_halfAnd10`,
   `LILATracts_1And10`, `LILATracts_Vehicle`), and which one you pick changes the answer.
6. **Limitations, written as analysis, not as an apology.** See below.

---

## What the preview already shows

From `python src/eda.py`:

- **1,051 geocoded Minnesota sites sit in only 512 distinct census tracts**, out of
  roughly 1,500 tracts in the state. Most of Minnesota's tracts contain no site at all.
- Sites **cluster**: 325 of those 512 tracts hold more than one site, and one tract holds
  **eight**. A county with many sites is not necessarily a county with spread-out sites,
  and that distinction is the heart of this question.
- **12.5% of organizations have no `block_geoid`** and cannot be placed — but they
  account for only **0.9% of all households served**, so the limitation is small. Check
  whether they are disproportionately rural.
- Counties carrying the most households per site over the last 12 months: **Washington,
  Steele, Anoka, Isanti, Olmsted, Renville**.

The clustering number is a good opening slide for this question: *512 tracts out of
~1,500, and two thirds of those hold more than one site.*

---

## Limitations — graded, so write them properly

The brief asks for these directly. Each one should come with a **magnitude**, not just an
acknowledgement.

| limitation | how to quantify it |
|---|---|
| Atlas is 2019 data on 2010 tracts; our geoids are 2020 | how many MN tracts changed between 2010 and 2020? |
| Straight-line distance, not drive time | pick a few rural cases and compare against a routing estimate |
| No site hours, capacity or eligibility data | state it; presence is not access |
| 12.5% of sites unplaceable | **0.9% of households served** (already computed in `analysis.py`) — now check whether they are disproportionately rural |
| 12 ZIP-centroid geoids | excluded from distance; say how many and where |
| Tract is where the **site** is, not where clients live | same limitation as everywhere else in this project |

The pattern to follow is in that fourth row. "12.5% of rows are missing" is a weak
answer; "the unplaceable sites are 0.9% of households served, and they are/are not
disproportionately rural" is a strong one. Do the same for every other row in the table.

---

## Deliverables

- [ ] `analysis.py` rebuilding every number from `data/processed/` + `data/external/`
- [x] The crosswalk rule, written down and defensible
- [ ] Population-weighted LILA coverage, by distance band and by urban/rural
- [ ] The retail-pattern comparison — the answer to "does the network fill the gap"
- [x] One map for the deck
- [ ] A limitations section with **magnitudes**

### Map

Run the cells in `notebooks/q8_exploration.ipynb` to explore tract-level site
presence, crosswalk sensitivity, nearest-site distance, population-weighted
coverage, and the USDA grocery-access comparison; it also creates statewide and
Twin Cities zoom versions:
`outputs/figures/08_q8_lila_site_presence.png` and
`outputs/figures/08_q8_lila_site_presence_twin_cities.png`. They shade 2020
tracts by the USDA half-mile/10-mile LILA flag and food-shelf-type site presence.
Presence is assigned at tract level, not shown as an exact address or service radius.
Notebook results are exploratory. Reproduce any reported findings in `analysis.py`
before treating them as final results.

### Rebuilding the Atlas crosswalk

Run `python questions/q8_lila_access/build_lila.py` for the initial build. The
Minnesota Atlas extract and 2020 crosswalk are cached as Parquet files in
`data/processed/`; later runs reuse them unless an available source file is newer.
Use `--force` to explicitly rebuild the caches. `analysis.py` uses the same cache.
