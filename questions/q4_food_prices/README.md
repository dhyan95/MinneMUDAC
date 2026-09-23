# Q4 — Food prices and food shelf activity

**Division:** undergraduate and graduate.
**Owner:** Dhyan
**Status:** not started

---

## The ask, in our words

1. Do more people arrive at food shelves when grocery prices rise?
2. Does the response happen **at once, or after a delay**?
3. Does it show up in **all three metrics**, or only some?
4. What **other cyclical patterns** do prices *not* explain?

The purpose stated in the brief is operational: The Food Group wants to tell food
shelves what demand to expect, and tell donors what need to expect. Timing is the
deliverable, not just a correlation.

---

## Data

| what | where | grain |
|---|---|---|
| activity | `data/processed/county_month.parquet` | county × month, 2022-01 to 2026-07 |
| prices | **BLS CPI `CUUR0200SAF11`** — Food at home, Midwest region | region × **month** |
| robustness | BLS CPI `CUUSA211SAF11` — Minneapolis-St. Paul | metro × **bimonthly** |
| county price variation | `cost_per_meal` in `mmg_county.parquet` | county × **year** |

Download CPI from the BLS public API or the series page, truncate at **2026-07**, save to
`data/external/bls/`, and register it in [DATA_SOURCES.md](../../docs/DATA_SOURCES.md).

---

## Approach

1. **Statewide monthly series first.** Aggregate the county panel to statewide monthly
   totals for all three metrics. Plot alongside CPI food-at-home.
2. **Work in year-over-year change, not levels.** Both series trend upward across
   2022–2026, so a level correlation is spurious by construction.
3. **Distributed lag.** Regress YoY activity change on YoY CPI change at lags 0 through
   6, with month-of-year fixed effects. Report the lag profile — that is the answer to
   "at once or delayed".
4. **Do it separately for each metric.** They do not move together: over 2022–2025,
   households grew +63%, individuals +66%, pounds only +33%. Pounds is supply-constrained
   in a way the people counts are not, and that difference is a finding.
5. **Then the residual seasonality.** Once price is in the model, what cycle is left?
   Compare against the seasonal index in `outputs/tables/02_seasonal_index.csv`.
6. **County heterogeneity, carefully.** The Midwest CPI is one series for all 87
   counties, so it cannot identify a cross-county price effect. If you want one, use
   `cost_per_meal` (county, annual) as a cross-sectional interaction and state the grain
   limitation plainly.

---

## What the preview already shows

Seasonality is real and it is **not subtle** (`outputs/figures/02_seasonality.png`):

| metric | busiest | quietest | peak-to-trough |
|---|---|---|---|
| households | **October** (1.100) | January (0.906) | 21.4% |
| pounds | **October** (1.082) | February (0.900) | 20.3% |
| individuals | **October** (1.102) | January (0.908) | 21.3% |

October is the busiest month in all three metrics and the January/February trough is
just as consistent. Whatever price effect exists has to be separated from a 20%
month-of-year swing, so month-of-year effects are not optional in this model.

Pounds per household is **falling** year on year: 62 (2022), 57 (2023), 55 (2024),
50 (2025), 51 (2026 partial). The network is spreading less food over more households.
That is a Q4 story in itself, and it is also a warning: pounds does not respond to
demand the way the people counts do.

---

## Traps

- **Spurious trend.** Levels correlate because both trend up. YoY changes, always.
- **One CPI series for 87 counties.** Identification is purely over time. There is no
  cross-county variation in the driver, so do not present a county-level "price effect"
  from the Midwest series.
- **Reporting composition.** A jump in a county total can be three new sites reporting.
  Carry `n_sites_reporting` in every regression, or work per reporting site.
- **Prices are not the only thing moving.** SNAP benefit changes (Q5) hit the same series
  in the same window. Coordinate with Dhyan's Q5 work so the two questions do not claim
  the same variation.
- **CPI release gaps.** Check the series for missing months in the window before
  modelling, and note the publication lag.

---

## Deliverables

- [ ] `analysis.py` that rebuilds every number from `data/processed/` + `data/external/`
- [ ] One chart: lag profile of activity response to price, all three metrics
- [ ] A stated answer in months: "demand responds after N months"
- [ ] The residual seasonal pattern that price does not explain
- [ ] A line for the operations slide: what The Food Group should tell shelves and donors
