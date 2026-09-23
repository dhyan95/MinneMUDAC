# Q1 — Compare need estimates to observed activity

**Division:** all three answer this. It is the foundation for Q6 and Q8.
**Owner:** Valentino
**Status:** not started

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

**Years: 2023 and 2024.** The brief fixes this. Do not quietly widen it.

---

## Data

| what | where | note |
|---|---|---|
| activity | `data/processed/county_month.parquet` | filter `year in (2023, 2024)`, aggregate to county-year |
| need | `data/processed/mmg_county.parquet` | `fi_rate`, `fi_persons`, `child_fi_rate` |
| rural classification | `rucc_2023` — already inside the MMG table | free, no download |
| everything else | download it, then register it in [DATA_SOURCES.md](../../docs/DATA_SOURCES.md) | SAIPE poverty, PEP population, ACS vehicle access, distance |

`households` is our stand-in for **visits** — there is no visits field. See
[DATA_ERRORS.md §1.2](../../docs/DATA_ERRORS.md).

---

## Approach

1. **Build the county-year frame.** 87 counties × 2 years. Activity from the panel, need
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
  movement without reading the Read Me tab.

---

## Deliverables

- [ ] `analysis.py` that rebuilds every number from `data/processed/`
- [ ] One chart for the deck: need against activity, breakdown counties labelled
- [ ] A correlation table covering all three metrics, both years, counts and rates
- [ ] A ranked list of breakdown counties with the characteristics that explain them
- [ ] One sentence a judge remembers
- [ ] Limitations stated by us, before a judge states them
