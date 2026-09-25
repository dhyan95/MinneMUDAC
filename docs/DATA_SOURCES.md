# Public data sources

The brief requires four facts for **every** public source we use:

1. the publisher and the **exact** series,
2. the **geographic grain** (county, tract, region),
3. the **time grain** (monthly, bimonthly, annual),
4. **why this source and not an alternative.**

This page is where that record lives. It has two parts: a candidate list per question,
with the four facts filled in as far as we can before downloading, and a registry table
that must be completed for every file we actually put in `data/external/`.

> **Rule:** nothing goes into `data/external/` without a row in the registry at the
> bottom of this file. An undocumented source is worth zero points and is a gift to a
> judge looking for a weakness.

> **Leakage rule:** nothing dated **August 2026 or later** enters this repo. Not a CPI
> release, not a SNAP caseload table, not a refreshed Map the Meal Gap. Q7 asks us to
> predict August 2026 and the brief says using August data from any source disqualifies
> the team. When you download a monthly series, **truncate it to 2026-07 before saving**.

---

## Already in the repo

| source | file | grain | time grain | used by |
|---|---|---|---|---|
| Feeding America, Map the Meal Gap 2025 edition | `data/raw/feeding_america/MMG2025_2019-2023_Data_To_Share_v2.xlsx` | county | annual, 2019–2023 | Q1, Q6 |
| Feeding America, Map the Meal Gap 2026 edition | `data/raw/feeding_america/MMG2026_2024_Data_To_Share.xlsx` | county | annual, 2024 only | Q1, Q6 |

Both are mandated by the brief for Questions 1 and 6. Read the **Read Me** tab of the
2025 file before comparing 2023 to 2024: it records a methodology change for local meal
cost, food budget shortfall and meal gap. It also carries the Rural-Urban Continuum Code
(2013 and 2023 vintages), which gives us a free rural/urban classifier with no extra
download.

---

## Q1 — county characteristics that might explain the mismatch

The brief names four examples: poverty rate, rural share, distance to nearest food shelf,
SNAP enrollment. Take those as a floor, not a ceiling.

| # | source | exact series | geographic grain | time grain | why this one |
|---|---|---|---|---|---|
| 1 | Census Bureau, **SAIPE** | Small Area Income and Poverty Estimates, "All ages in poverty, percent" | county | annual, ~1 year lag | The standard county poverty number. ACS 5-year is also county-level but is a 5-year average, which blurs exactly the year-to-year movement Q1 asks about. |
| 2 | Census Bureau, **Population Estimates (PEP)** | `CO-EST` annual county resident population | county | annual | Every rate in this project needs a denominator. PEP is the annual series; the decennial count is only every ten years. |
| 3 | USDA ERS, **Rural-Urban Continuum Codes 2023** | already inside the Map the Meal Gap file | county | decennial-ish vintage | Free — no download needed. Prefer it to "metro/non-metro" because it is a 9-point scale, so "how rural" becomes a continuous covariate. |
| 4 | Census Bureau, **ACS 5-year** | `B08201` (household vehicle availability), `B17001` (poverty by age), `S1701` | county **and tract** | 5-year rolling | Vehicle access is the barrier the brief names indirectly ("no transport"). Tract-level availability also makes it reusable in Q6 and Q8. |
| 5 | Census, **2020 Gazetteer** | `2020_Gaz_tracts_27.txt`, `2020_Gaz_blocks_27.txt` | tract / block centroids | static | The only way to turn `block_geoid` into a distance. See [BLOCK_GEOID.md](BLOCK_GEOID.md). |
| 6 | BLS, **LAUS** | Local Area Unemployment Statistics, county unemployment rate | county | **monthly** | The one labour-market series published monthly at county level. Q1 uses the annual average; Q4 and Q7 can use the monthly. |

**The trap to write on the slide:** Map the Meal Gap is itself *modelled* from poverty
and unemployment. "Poverty explains the mismatch" is therefore partly mechanical — you
are partly regressing a variable on its own inputs. Covariates that are **not** in the
MMG model (distance, vehicle access, site density, rurality) carry much more information
and should lead the Q1 story.

---

## Q4 — food prices and food shelf activity

| # | source | exact series | geographic grain | time grain | why this one |
|---|---|---|---|---|---|
| 1 | BLS, **CPI** | `CUUR0200SAF11` — Food at home, **Midwest region**, all urban consumers | Midwest census region | **monthly** | The finest *monthly* food-price series that covers all of Minnesota. National CPI would ignore regional price movement; Minneapolis-St. Paul CPI is bimonthly and covers only the metro. |
| 2 | BLS, **CPI** | `CUUSA211SAF11` — Food at home, **Minneapolis-St. Paul-Bloomington** | metro area | **bimonthly** | Use as a robustness check on the metro counties only. State plainly that it is bimonthly and metro-only. |
| 3 | USDA ERS, **Food Price Outlook** | annual/forecast food-at-home price change | national | annual | Context for the deck, not for identification. |
| 4 | Feeding America | `Cost Per Meal`, already in Map the Meal Gap | **county** | annual | The only *county-level* price signal we have. Annual grain means it cannot carry the lag analysis, but it can carry cross-sectional heterogeneity: do high-cost-per-meal counties respond more? |

**The trap:** prices and activity both trend upward over 2022–2026, so a correlation in
*levels* is spurious. Work in **year-over-year percentage change**, include
month-of-year effects, and test lags 0–6 months. With one CPI series for all counties,
identification is purely over time — there is no cross-county variation in the driver,
so do not present a county-level "price effect" from the Midwest series.

---

## Q5 — SNAP enrollment and food shelf use

| # | source | exact series | geographic grain | time grain | why this one |
|---|---|---|---|---|---|
| 1 | **Minnesota DHS** | SNAP/Food Support monthly county caseload reports (DHS publishes "Minnesota Public Assistance Caseload Statistics") | **county** | **monthly**, publication lag of roughly 1–2 months | The only county-monthly SNAP series that exists for Minnesota. Everything else is state or annual. **Verify the exact report name, the URL and the lag before relying on it.** |
| 2 | USDA FNS | **SNAP State Activity Report** / national and state participation & issuance | state | monthly (state), annual (state activity report) | Use for benefit-level changes and as a cross-check on the DHS totals. Cannot support county heterogeneity. |
| 3 | USDA FNS | **SNAP COLA / maximum allotment** schedules | national | annual (October adjustments) | This is the *event* series. Benefit levels change on a published schedule, which gives a clean date for an event study. |
| 4 | Feeding America | `SNAP Threshold`, `% FI ≤ SNAP Threshold`, already in Map the Meal Gap | county | annual | Free measure of how much of a county's food-insecure population is even income-eligible for SNAP. Feeds the Q6 "participation gap" directly. |

**The trap:** SNAP caseloads and food shelf activity both rise when times are hard, so
their levels co-move for reasons that say nothing about substitution. Identification has
to come from **benefit changes** — the end of pandemic emergency allotments in early
2023 is the obvious one, and any later benefit disruption in the window is another
(**verify the dates before building the event study around them**). Compare counties by
how exposed they were, not just before and after.

---

## Q6 — a divergence measure for need and demand

The brief is explicit: the measure must consider **more than demand**, and will likely
need public data. The design constraint that matters is that the inputs must be
**independent of food shelf visits** and **not already inside the Map the Meal Gap model**,
or you have rebuilt MMG under a new name.

| # | source | exact series | grain | time grain | why |
|---|---|---|---|---|---|
| 1 | Census ACS 5-year | `B08201` no-vehicle households | county, tract | 5-year | Transport is one of the four barriers the brief names. Not in the MMG model. |
| 2 | MN Dept of Education | Free and reduced-price lunch eligibility by district | school district | annual | Child need signal independent of both visits and MMG. District→county needs a crosswalk. |
| 3 | Census ACS | `S0101` age structure, senior share | county | 5-year | Seniors are a known under-claiming group; a high senior share with low activity is a real divergence candidate. |
| 4 | Derived, this repo | distance to nearest site (from `block_geoid` + Gazetteer) | tract | static | Ours, not published anywhere. Directly measures a barrier. |
| 5 | Derived, this repo | SNAP participation gap = DHS caseload ÷ MMG income-eligible food-insecure | county | monthly ÷ annual | A county where few eligible people claim SNAP is a county where few eligible people use a food shelf, for the same reasons. |

**The trap:** arbitrary weights. Whatever index you build, show the **county ranking is
stable** under reasonable alternative weightings. A rank that flips when you change a
weight from 0.2 to 0.3 is not a finding.

---

## Q7 — forecasting August activity

**Use no external data unless you are certain of its vintage.** The safest Q7 model uses
only the food shelf panel itself. If you bring in a driver from Q4 or Q5, it must be
truncated at **2026-07** and someone other than the model's author must verify it.

Candidate internal features: month-of-year, county, site count reporting, the county's
own July value, the historical August/July ratio, trailing 3- and 12-month levels.

---

## Q8 — low-income, low-access areas

| # | source | exact series | grain | time grain | why this one |
|---|---|---|---|---|---|
| 1 | USDA ERS, **Food Access Research Atlas** | `LILATracts_1And10`, `LILATracts_Vehicle`, `LILATracts_halfAnd10` | **census tract** | 2019 data on **2010** tract boundaries | The source the brief points at ("USDA shortens this to LILA"). State the vintage explicitly: it is the whole limitation. |
| 2 | Census Bureau | **2010 → 2020 tract relationship file** | tract | static | **Required.** Our geoids are 2020, the Atlas is 2010. Without this the join is wrong in a way that still produces numbers. |
| 3 | Census, **2020 Gazetteer** | `2020_Gaz_tracts_27.txt` | tract centroid | static | Distance from tract centroid to nearest site. |
| 4 | Census ACS 5-year | tract population, poverty, vehicle access | tract | 5-year | Weights the coverage measure by people rather than by tracts. A tract is not a person. |

**The traps, all of which belong on the Q8 limitations slide:**
- Atlas vintage (2019 data, 2010 tracts) against our 2020 geoids.
- Straight-line distance, not drive time.
- No data on site **hours, capacity or eligibility** — presence is not access.
- 12.5% of sites have no geoid and cannot be placed at all.

---

## Where to put the files

```
data/external/
├── census/         SAIPE, PEP, ACS, Gazetteer, relationship files
├── bls/            CPI series, LAUS
├── usda/           Food Access Research Atlas, RUCC, FNS SNAP
└── mn_dhs/         SNAP county caseloads
```

Keep the file **exactly as downloaded**. Do not open it in Excel and save it — that is
how leading zeros die. All reshaping happens in a script.

---

## Source registry — fill in one row per file actually downloaded

| file path | publisher | exact series / table id | geo grain | time grain | vintage / last obs | downloaded by | date | why this over the alternative |
|---|---|---|---|---|---|---|---|---|
| data/external/bls/CUUR0200SAF11.csv | U.S. Bureau of Labor Statistics | CUUR0200SAF11 (CPI-U, not seasonally adjusted, Midwest region, Food at home) | Midwest Census region | monthly | 2021-01 through 2026-07 (2025-10 missing; retrieved via BLS public API, no vintage/revision date returned) | Dhyan | *(fill in actual run date)* | Chosen over the Minneapolis–St. Paul metro series (CUUSA211SAF11) because it's monthly rather than bimonthly, giving full lag resolution at 1-month steps; the metro series is reserved as a robustness check per the brief |
| | | | | | | | | |
| | | | | | | | | |
| | | | | | | | | |
| | | | | | | | | |

*(Every one of the four required facts is a column here. If a row cannot be completed,
the source does not get used.)*
