# MinneMUDAC 2026 — The Food Group Student Data Challenge

**Graduate division.** Team of three: Valentino, Dhyan, Uddam.
**Deadline: 17 October 2026.** Live presentation with open Q&A.

---

## The problem in one paragraph

The Food Group runs a food bank, supports food shelves across Minnesota, operates a SNAP
helpline and supports farmers market access through Market Bucks. Every food shelf visit
is a unit of **demand**. Not every visit is **need** — some households use a shelf to
stretch a budget or because it is convenient. And not every need becomes a visit: stigma,
not knowing the program exists, no transport and other barriers keep households away.

The Food Group allocates resources by **visits**, which means it allocates by demand.
Where need is high and visits are low, the data gives no signal that the place exists.

**Our job: build a more complete picture of need and demand, show where they agree, show
where they diverge, and explain why.**

---

## Start here

**New to the project? Read these four, in order.** About forty minutes.

1. [`data/raw/reference/TFG_MinneMUDAC_Challenge_Brief.pdf`](data/raw/reference/TFG_MinneMUDAC_Challenge_Brief.pdf) — the brief itself. Non-negotiable.
2. [`docs/DATA_ERRORS.md`](docs/DATA_ERRORS.md) — what is wrong with the data and what we did about it. **Read before touching any number.**
3. [`docs/TEAM_PLAN.md`](docs/TEAM_PLAN.md) — who owns what, week by week.
4. The README in the question folder you own.

Then run the pipeline once so you have the same numbers as everyone else:

```bash
pip install -r requirements.txt
python src/clean_data.py     # data/raw -> data/processed   (~1 min)
python src/eda.py            # -> outputs/ + docs/EDA_FINDINGS.md
```

---

## Glossary

The organizers gave every team a glossary. It is in [`docs/GLOSSARY.md`](docs/GLOSSARY.md)
in full, with a table mapping each term to our columns. These are the words the judges
use, so they are the words we use. Six of them change how we write:

| term | what it means for us |
|---|---|
| **Need** vs **demand** | need is the Map the Meal Gap estimate; demand is what the food shelves recorded. Our Q1 charts say "observed demand", which is the glossary's own phrase |
| **Latent demand** vs **unmet demand** | need that never becomes a request, against a request the system cannot fill. Q6 targets the first; the second is mostly invisible in our data |
| **Visit** | one trip by one household. The brief labels visits as `HouseholdsReg`, which counts a household once per month, so our number is a floor |
| **Pounds distributed** | "a supply measure as much as a demand measure". Say this whenever pounds behaves differently from the people counts |
| **Food security** | "a household can be food secure and still use a food shelf". Activity above need does not mean need is overstated |
| **Food desert** | do not use it on a slide; say low-income, low-access (LILA) |

---

## The six questions (graduate division)

| Q | question | addendum | owner | folder |
|---|---|---|---|---|
| 1 | Need estimates against observed activity | — | Valentino | [`questions/q1_need_vs_activity/`](questions/q1_need_vs_activity/) |
| 4 | Food prices and food shelf activity | — | Dhyan | [`questions/q4_food_prices/`](questions/q4_food_prices/) |
| 5 | SNAP enrollment and food shelf use | — | Dhyan | [`questions/q5_snap/`](questions/q5_snap/) |
| 6 | A divergence measure for need and demand | **yes** | Valentino | [`questions/q6_divergence_measure/`](questions/q6_divergence_measure/) |
| 7 | Forecast August activity | **yes** | Uddam / Dhyan | [`questions/q7_forecast_august/`](questions/q7_forecast_august/) |
| 8 | Low-income, low-access areas and network reach | — | Uddam | [`questions/q8_lila_access/`](questions/q8_lila_access/) |

Questions 2 (calls) and 3 (farmers markets) are **novice-division only** and are not
scored for us. The brief explicitly allows carrying findings from them into a scored
question, and we do: calls feed Q5, Market Bucks feeds Q6. See
[`questions/_shared/`](questions/_shared/).

---

## ⚠ The two rules that can lose the competition

**1. No August 2026 data. Ever. From any source.** Q7 asks us to forecast August 2026 and
the brief disqualifies a team for using any August data. Truncate every external series at
**2026-07 before saving it to disk**. The `z12MoAverage_*` columns on the Organization
table were recomputed in August 2026 and are dropped in the pipeline for this reason.
`qkit.leakage_check()` raises on anything at or after 202608 — call it. **Uddam audits
the repo before submission**, and he is not the person who builds the Q7 model.

**2. Every public source needs four documented facts.** Publisher and exact series,
geographic grain, time grain, and why this source over an alternative. The brief requires
it. The registry is at the bottom of
[`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md), and a source with no row does not get used.

---

## Repository layout

```
MinneMUDAC/
├── data/
│   ├── raw/              read-only, never written to
│   │   ├── tfg/          The Food Group operational data (4 tables + bundle)
│   │   ├── feeding_america/  Map the Meal Gap, 2025 and 2026 editions
│   │   └── reference/    the brief and the data dictionary
│   ├── external/         public data we download (see docs/DATA_SOURCES.md)
│   ├── interim/          scratch, not committed
│   └── processed/        THE CANONICAL TABLES — everyone reads these
├── src/
│   ├── config.py         paths, metric names, cleaning thresholds, leakage cutoff
│   ├── geography.py      county label -> FIPS, block_geoid handling
│   ├── clean_data.py     data/raw -> data/processed
│   ├── eda.py            first look; writes outputs/ and docs/EDA_FINDINGS.md
│   └── qkit.py           the loaders every question script imports
├── questions/            one folder per question: README + analysis.py
├── docs/                 data errors, block_geoid, sources, team plan, EDA findings
├── outputs/              figures/ and tables/ — regenerable, never hand-edited
├── reports/              deck material and write-ups
└── notebooks/            exploration only; findings move to a script before they count
```

### The canonical tables

Nothing outside `src/clean_data.py` reads `data/raw/`. Everything else reads these:

| file | grain | rows |
|---|---|---|
| `site_month.parquet` | site × month, with a flag column per defect | 28,287 |
| `county_month.parquet` | county × month, keyed on 5-digit FIPS | 4,730 |
| `sites.parquet` | organization master with census geography | 1,202 |
| `mmg_county.parquet` | Map the Meal Gap, MN, 2019–2024 | 522 |
| `calls_clean.parquet` | call log with FIPS and a food-related flag | 49,727 |
| `marketbucks_clean.parquet` | market session with FIPS | 13,573 |
| `data_quality_log.csv` | every issue found, with the rule applied | 28 |

Load them through `qkit`, not by path:

```python
import sys; sys.path.insert(0, "src")
import qkit

cm   = qkit.county_month()                    # county x month panel
df   = qkit.county_year(years=[2023, 2024])   # activity + need, joined, ready
site = qkit.sites(distance_safe=True)         # geocoded, no ZIP centroids
qkit.leakage_check(cm)                        # raises on any Aug-2026 data
```

---

## What we already know

From `python src/eda.py` — enough to shape the story before any modelling.

**The brief's thesis is visible in The Food Group's own data.** Raw *counts* of activity
correlate almost perfectly with Feeding America's food-insecure population (Spearman
0.89–0.92), but that is mostly population — big counties have more of everything. In
*rates*, the correlation turns **negative**: counties with a higher food-insecurity rate
serve **fewer** households per food-insecure person (−0.26 to −0.29 in 2024).

**Wilkin County has no reporting food shelf in any of the 55 months.** Feeding America
estimates 810 food-insecure people there in 2024. Observed demand is zero. Zero demand is
not zero need — that is Question 6 in one county.

**Rural and metro diverge in two directions at once.** Metro counties serve 4.91
households per food-insecure person; rural counties serve 2.98. But rural counties carry
400 food-insecure people per site against metro's 637. Reach and load are different
problems and an index that averages them loses both.

**October is the busiest month** in all three metrics; January and February are the
quietest. Peak-to-trough spread is about 21%, so month-of-year effects are mandatory in
any Q4 or Q7 model.

**The three metrics are not interchangeable.** Over 2022–2025 households grew +63% and
individuals +66%, but pounds only +33%. Pounds per household fell from 62 to 50. The
network is spreading less food over more people — a finding in its own right, and a
warning against treating the three metrics as one.

**The August/July ratio is unstable and trending down:** 1.066 (2022), 1.152 (2023),
1.024 (2024), **0.937** (2025). Any Q7 model has to beat this, and its instability is the
honest uncertainty statement.

**Most of Minnesota has no site.** 1,051 geocoded sites sit in only **512 census tracts**
out of roughly 1,500 in the state, and 325 of those 512 tracts hold more than one site.

See [`docs/EDA_FINDINGS.md`](docs/EDA_FINDINGS.md) for the full generated list, and
`outputs/` for the tables and charts behind every number above.

---

## What is wrong with the data — the short version

Full detail in [`docs/DATA_ERRORS.md`](docs/DATA_ERRORS.md).

- **There is no visits field.** `UniqueVisits*` is 99.9% empty. We use **households
  served** as the stand-in and say so on every slide. It is a parameter in `config.py`.
- **The dictionary marks the populated columns deprecated.** The `*Total` family is
  flagged Deprecated; the components it supposedly sums are entirely empty. We verified
  `*Reg` and `*Total` are identical (0 disagreements) and read `*Reg`.
- **91 county labels for 87 counties.** Hennepin and Ramsey split into city/suburbs, St.
  Louis spelled two ways. Nothing joins to public data until they map to FIPS. Fixed in
  `geography.py`, with the canonical list read out of Map the Meal Gap rather than typed.
- **570 site-month rows (2.0%) fail a quality check** — impossible months, duplicates,
  273,385 households for 646 people, households pasted into the pounds column. All
  **flagged, never deleted**; aggregates use a `*_adj` column that falls back to the
  site's own median.
- **The panel is unbalanced.** 456–553 sites report in a given month, so a county total
  moves with who filed a report. `n_sites_reporting` sits next to every metric.
- **County is where the site is, not where the client lives.** A limitation on every
  county-level slide.
- **12.5% of sites have no `block_geoid`** and cannot be placed in a tract — but they are
  only 0.9% of households served.

---

## `block_geoid` in thirty seconds

The most useful field in the extract and the easiest to break. Full guide:
[`docs/BLOCK_GEOID.md`](docs/BLOCK_GEOID.md).

It is a 15-digit 2020 Census block GEOID, given instead of an address so sites are not
identifiable. It is built by **concatenation**, so every larger geography is a prefix:

```
27 | 053 | 026807 | 7009
state  county  tract   block
```

Take the first 5 characters for the **county FIPS** (joins to everything public), the
first 11 for the **census tract** (the grain USDA's LILA flags use — this is Q8).
**Read it as text, never as a number**, or the `.0` and the lost leading zeros will
poison every join. `geography.split_block_geoid()` already did this for you; the columns
are on `sites.parquet`.

---

## The plan in one paragraph

Week 1: foundations — everyone runs the pipeline, every external source is downloaded and
registered, the organizer email goes out, and the two riskiest unknowns (the MN DHS SNAP
series, the 2010→2020 tract crosswalk) are resolved or known to be dead ends. Week 2: one
rough chart and one sentence per question. Week 3: six answers become one story; findings
freeze Friday. Week 4: cross-briefing so each of us can defend questions we do not own,
leakage audit by someone who did not build the model, deck frozen Wednesday, two timed
rehearsals Thursday. Full detail, including the reasoning behind the split, in
[`docs/TEAM_PLAN.md`](docs/TEAM_PLAN.md).

---

## Standing rules

1. Raw data is read-only. All cleaning in `clean_data.py`. **No hand-edited Excel, ever.**
2. One canonical panel. Everyone reads `data/processed/` through `qkit`.
3. Nothing dated August 2026 or later enters the repo. Truncate at download.
4. Every public source gets a registry row before it is used.
5. Baselines before models. Complex must beat simple in a backtest.
6. Every number on a slide traces to a script we wrote and can explain live.
7. We state our own limitations, in minute three, before a judge does in minute twelve.
