# Q8 — Low-income, low-access areas and the reach of the network

**Division: graduate only.** No other division answers this. It is the clearest chance to
show work the other divisions cannot.
**Owner:** Uddam
**Status:** coverage analysis runs reproducibly from `analysis.py`; validate its
generated outputs before quoting them in the deck.

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
| site locations | `data/processed/sites.parquet` → `tract_geoid` | **2020** census tract | current; represented by tract internal points |
| LILA and grocery-access flags | USDA ERS **Food Access Research Atlas** | census tract | **2019 data on 2010 tracts** |
| tract↔tract crosswalk | Census **2010→2020 tract relationship file** | tract | **required** |
| site tract internal points | Census `2026_Gaz_tracts_national.txt` | 2020-definition tract | 2026 release |
| tract population weights | Census `CenPop2020_Mean_TR27.txt` | tract | 2020 Decennial Census |

Read [BLOCK_GEOID.md](../../docs/BLOCK_GEOID.md) for the location precision limitation.

---

## Approach

1. **Get the crosswalk right first.** Atlas flags are on 2010 tracts and site geoids are
   2020. Each 2020 tract receives an area-weighted average of its 2010 parents using
   Census land-area overlap; a flag is true when at least half of the known overlap
   area is flagged. This is an **area-weighted**, not population-weighted, transfer
   because the relationship file supplies land overlap, not population by overlap.
   `parent_count` counts parents contributing at least 5% of the new tract's land area;
   all-parent counts are retained separately for audit.
2. **Place the sites.** Start from the shared food-shelf-like and ever-reported
   definition, but exclude the current type `Agency or Tribal Nation`: it is too broad
   for a food-shelf location measure. Keep sites with a usable activity record in the
   latest 12 complete months (August 2025–July 2026), a Minnesota tract geoid, and no
   ZIP-centroid geocode. This is narrower than the shared Q1/Q6 type filter.
   `analysis.py` writes the inclusion audit and counts recent-period household activity
   omitted from the spatial analysis.
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
6. **Limitations, written as analysis, not as an apology.** The 2020 Census Gazetteer
   does not publish a block-centroid file at the URL previously listed in
   `BLOCK_GEOID.md`. Until block coordinates are available, sites use the internal point
   of their assigned tract. `analysis.py` measures the maximum distance from that point
   to any boundary vertex for each site tract; this is a conservative upper bound on
   within-tract displacement, not the observed site-location error.

---

## Reproducible outputs

Run `python questions/q8_lila_access/analysis.py` after the shared cleaning pipeline
and crosswalk build. It selects sites using `state_fips == "27"`, the shared
food-shelf-like and ever-reported flags, a latest report during August 2025–July 2026,
and a tract geocode that is not a ZIP centroid. It additionally excludes the broad
current `Agency or Tribal Nation` category. The generated
`q8_site_definition_audit.csv` records the counts and recent household activity left
out by this rule.

The same run creates population-weighted distance bands by LILA and urban/rural status,
alternative LILA definitions, the urban/rural grocery-access comparison, and the
within-tract location-displacement bound. These outputs—not the earlier notebook
preview or the all-master-row EDA—are the source for final numbers.

In the current run, **402 sites** meet the Q8 definition: 415 shared-type reporters
had a report in the latest 12 months, then 13 broad `Agency or Tribal Nation` entries
were excluded. None of the remaining sites lack a tract geoid or use a ZIP centroid;
sites excluded from coverage account for **0.004%** of recent-period households in the
food-shelf-like activity panel. Within five straight-line miles are **37.0% of rural
LILA population**, **98.1% of urban LILA population**, **55.3% of rural non-LILA
population**, and **95.2% of urban non-LILA population**. These are proximity
estimates, not evidence of capacity, client usage, or service eligibility.

The corrected crosswalk has **1,479 2020 tracts with one significant 2010 parent,
23 with multiple significant parents, and three with no parent covering 5% of tract
land area**. Four zero-population tracts are omitted from population-weighted results
and maps. Among the 358 distinct site tracts, the maximum within-tract displacement
bound has a median of **3.1 miles**, a 90th percentile of **14.4 miles**, and a maximum
of **56.4 miles**. This is a conservative projected-distance bound, not an estimate of
actual site-coordinate error.

---

## Limitations — graded, so write them properly

The brief asks for these directly. Each one should come with a **magnitude**, not just an
acknowledgement.

| limitation | how to quantify it |
|---|---|
| Atlas is 2019 data on 2010 tracts; our geoids are 2020 | 23 tracts have multiple significant 2010 parents; 1,479 have one and 3 have no parent contributing at least 5% of land area |
| Straight-line distance, not drive time | the current analysis reports straight-line distance only |
| No site hours, capacity or eligibility data | state it; presence is not access |
| Sites excluded from the spatial definition | 13 broad type entries are excluded; the remaining excluded sites account for 0.004% of recent-period households |
| ZIP-centroid locations | 0 among the latest-12-month Q8 site set; verified in `q8_site_definition_audit.csv` |
| Tract point represents the **site** | report the maximum within-tract displacement bound from `analysis.py`; it is not the actual site error |

Use activity share and the displacement bound from the generated tables to give these
limitations magnitudes; the all-master-row missing-geoid percentage is not a substitute.

---

## Deliverables

- [x] `analysis.py` rebuilding coverage, sensitivity, and limitation numbers from `data/processed/` + `data/external/`
- [x] The crosswalk rule, written down and defensible
- [x] Population-weighted LILA coverage, by distance band and by urban/rural
- [x] The retail-pattern comparison — grocery-access coverage by urban/rural group
- [x] One map for the deck
- [x] A limitations section with **magnitudes**

### Map

Run the cells in `notebooks/q8_exploration.ipynb` to explore tract-level site
presence, crosswalk sensitivity, nearest-site distance, population-weighted
coverage, and the USDA grocery-access comparison; it also creates statewide and
Twin Cities zoom versions:
`outputs/figures/08_q8_lila_site_presence.png` and
`outputs/figures/08_q8_lila_site_presence_twin_cities.png`. The distance
coverage cell saves `outputs/figures/08_q8_population_weighted_distance.png`.
The notebook also creates `outputs/figures/08_q8_lila_site_presence_interactive.html`,
a zoomable map that shows recent site counts by county at statewide scale and
switches to tract categories as the user zooms in. The color key updates with
the map scale, and the layer control toggles tract categories; hover/click gives
feature-level details. Open the HTML file in a browser with internet access to
zoom in and capture local screenshots; internet is used for Leaflet assets and
basemap tiles. County boundaries are dissolved from the same TIGER tract polygons.
The maps shade 2020 tracts by the USDA half-mile/10-mile LILA flag and
recent reporting food-shelf site presence. Presence is assigned at tract level, not
shown as an exact address or service radius. The notebook excludes zero-population
tracts and uses the same latest-12-month site definition as `analysis.py`.
Notebook results are exploratory. Reproduce any reported findings in `analysis.py`
before treating them as final results.

### Rebuilding the Atlas crosswalk

Run `python questions/q8_lila_access/build_lila.py` for the initial build. The
Minnesota Atlas extract and 2020 crosswalk are cached as Parquet files in
`data/processed/`; later runs reuse them unless an available source file is newer.
Use `--force` to explicitly rebuild the caches. `analysis.py` uses the same cache.
The analysis script writes reproducible tables to `outputs/tables/` and the
population-weighted distance figure to
`outputs/figures/08_q8_population_weighted_distance.png`.
