# Q1 — Compare need estimates to observed activity

**Division:** all three answer this. It is the foundation for Q6 and Q8.
**Owner:** Valentino
**Status:** in progress — covariates built, residual analysis next

---

## The ask, in our words

Feeding America estimates how many food-insecure people live in each Minnesota county.
The Food Group counts what actually happens at food shelves. Four things have to come
out of this question:

1. Do the two tell the same story, for each of the **three metrics** (visits, pounds,
   individuals)?
2. **Which metric correlates most and least** with the Feeding America estimates?
3. **Which counties** are where the relationship breaks down?
4. Using public data, **what county characteristics explain the mismatch** — poverty
   rate, rural share, distance to nearest food shelf, SNAP enrollment, and anything else
   we can defend?

**Years: 2022, 2023 and 2024.** The brief originally said 2023–2024; the organizers
widened it to 2022–2024 in a later update (Sept 2026). The window is `C.Q1_YEARS` in
`src/config.py`. 2022 and 2023 need come from the same MMG edition (2025); 2024 comes
from the 2026 edition.

---

## Data

| what | where | note |
|---|---|---|
| activity | `data/processed/county_month.parquet` | `qkit.county_year(C.Q1_YEARS)` aggregates to county-year |
| need | `data/processed/mmg_county.parquet` | `fi_rate`, `fi_persons`, `child_fi_rate`, `rucc_2023` (rural class, free) |
| covariates | `data/processed/county_covariates.parquet` | `qkit.covariates()`, built by `python src/build_covariates.py` |

Every covariate, its source, and whether it is inside the MMG model (circularity risk).
Full source facts are in the [registry](../../docs/DATA_SOURCES.md#source-registry--fill-in-one-row-per-file-actually-downloaded).

| column | meaning | source | in MMG model? | status |
|---|---|---|---|---|
| `population`, `households_census` | residents, households (April 1) | MN State Demographic Center | no (denominator) | ✅ 2022–24 |
| `poverty_rate`, `child_poverty_rate` | % in poverty, all ages / 0–17 | Census SAIPE | **yes** | ✅ 2022–24 |
| `median_hh_income` | median household income | Census SAIPE | **yes** | ✅ 2022–24 |
| `unemployment_rate` | annual average | BLS LAUS | **yes** | ✅ 2022–24 |
| `pct_no_vehicle` | % households with no vehicle | ACS 5-yr B08201 | no | ✅ 2022–24 |
| `pct_senior`, `senior_poverty_rate` | % aged 65+, % of 65+ in poverty | ACS 5-yr B17001 | partly | ✅ 2022–24 |
| `pct_hh_snap` | % households receiving SNAP | ACS 5-yr B22003 | no | ✅ 2022–24 |
| `n_sites_reporting`, `sites_per_10k` | food-shelf-like sites with activity that year | derived, `site_month` | no | ✅ 2022–24 |
| `mean_km_to_site` | pop-weighted km from tract to nearest reporting site | derived, Gazetteer + CenPop2020 | no | ✅ 2022–24 |
| `rucc_2023` | rural-urban continuum code, 1–9 | USDA ERS, via MMG file | no | ✅ |

ACS 5-year tables are assigned to their **end year** (2019–2023 → 2023).

`households` is our stand-in for **visits** — there is no visits field. See
[DATA_ERRORS.md §1.2](../../docs/DATA_ERRORS.md).

---

## Approach

1. **Build the county-year frame.** 87 counties × 3 years. Activity from the panel, need
   from MMG, covariates joined on `fips`.
2. **Rates, not counts.** Report both, lead with rates. Denominators: per 1,000 residents
   (PEP) for general use, and **per food-insecure person** for this question specifically,
   since that is what makes "activity against need" a meaningful ratio.
3. **Correlations.** Pearson and Spearman, each metric against `fi_persons` (counts) and
   `fi_rate` (rates), each year separately. Report Spearman as the headline — 87 counties
   with a few very large ones is exactly the case Pearson handles badly.
4. **Find the breakdown counties.** Fit a simple relationship (log activity on log
   food-insecure persons), take the residuals, and rank. The tails are the answer to
   question 3.
5. **Explain the residuals.** Regress residuals on county characteristics. Keep the model
   small — 87 observations does not support a large one.

The EDA script already does a rough version of steps 1–4; start from
`outputs/tables/04_*.csv` rather than from scratch.

---

## What the preview already shows

From `python src/eda.py`:

| year | metric | Pearson (counts) | Spearman (counts) | Spearman (rate vs FI rate) |
|---|---|---|---|---|
| 2022 | households | 0.969 | 0.893 | **−0.149** |
| 2022 | pounds | 0.980 | 0.916 | **−0.129** |
| 2022 | individuals | 0.964 | 0.893 | **−0.180** |
| 2023 | households | 0.952 | 0.889 | **−0.146** |
| 2023 | pounds | 0.976 | 0.907 | **−0.203** |
| 2023 | individuals | 0.937 | 0.891 | **−0.156** |
| 2024 | households | 0.946 | 0.901 | **−0.294** |
| 2024 | pounds | 0.969 | 0.918 | **−0.285** |
| 2024 | individuals | 0.932 | 0.905 | **−0.262** |

Read that carefully, because it is the whole question in one table. In **counts** the two
sources agree almost perfectly — and that agreement is mostly population. In **rates** the
correlation is *negative*: counties with a higher food-insecurity rate serve **fewer**
households per food-insecure person. That is the brief's thesis, visible in our own data
before any modelling.

Counties with the least activity relative to their food-insecure population in 2024:
**Scott, Nicollet, Pope, Norman, Lac qui Parle, Nobles, Douglas, Stevens**.
Most: **Steele, Rice, Washington, Renville, Houston, Kittson, Olmsted, Cook**.
And **Wilkin County has no reporting food shelf at all**, in any month of the data.

Those lists are a starting point, not a finding — they use our current cleaning rules and
the household proxy. Re-derive them properly.

---

## Traps

- **Counts versus counts mostly measures population.** A scatter of county activity
  against county food-insecure persons will look excellent and mean almost nothing. Lead
  with rates.
- **Map the Meal Gap is modelled from poverty and unemployment.** Explaining its
  residuals with poverty is partly circular. Covariates *outside* the MMG model —
  distance, vehicle access, site density, rurality — are worth far more.
- **87 counties. Do not over-model.** Four or five covariates, stated clearly, beats a
  gradient boosting model nobody can explain in Q&A.
- **County means where the site is, not where the client lives.** Counties with a
  regional shelf absorb their neighbours' demand. This is a limitation on every slide.
- **Two MMG editions.** 2023 comes from the 2025 edition, 2024 from the 2026 edition, and
  the methodology changed between them. Do not present a 2023→2024 change as a real
  movement without reading the Read Me tab. 2022→2023 is within one edition and is
  comparable.

---

## Deliverables

- [ ] `analysis.py` that rebuilds every number from `data/processed/`
- [ ] One chart for the deck: need against activity, breakdown counties labelled
- [x] A correlation table covering all three metrics, all three years, counts and rates (`outputs/tables/q1_correlations.csv`)
- [ ] A ranked list of breakdown counties with the characteristics that explain them
- [ ] One sentence a judge remembers
- [ ] Limitations stated by us, before a judge states them
