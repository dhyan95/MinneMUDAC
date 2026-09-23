# Q7 — Graduate addendum

**Graduate teams answer this. Undergraduate teams do not.**

> 1. A separate prediction for **children served**, **seniors served**, and **adults
>    served**.

---

## What makes this easier than it looks

In `data/processed/county_month.parquet`, `children + adults + seniors` equals
`individuals` in **every single row** — 0 mismatches across 26,024 rows with all four
fields present. The age split is an exact decomposition, not an approximation.

That means you do **not** have to build three independent forecasts. You have a choice,
and it is worth stating the choice explicitly in the deck:

**Option A — forecast the total, then split by share.**
Forecast `individuals` with your main Q7 model, then apply a forecast of each county's
age shares. Guarantees the three components sum to the total, which is a property a judge
will check. The share forecast can be simple: the county's trailing 12-month share, or
its August share from previous years.

**Option B — forecast each age group directly.**
Three models. More flexible if the age groups have genuinely different seasonality, but
the three will not sum to your `individuals` forecast unless you reconcile them
afterward.

**Recommendation: start with A.** Move to B only if the backtest shows the age groups
have meaningfully different seasonal patterns — which is the first thing to check.

---

## The first thing to check

Before choosing, compute the seasonal index **separately for children, adults and
seniors**, the same way `src/eda.py` does for the three main metrics.

Two things to look for:

- **Do the age groups peak in different months?** Children plausibly spike in summer when
  school meals stop and again at the start of the school year. If children peak in a
  different month than adults, Option A's fixed-share assumption is wrong for August
  specifically — and August is the month we are forecasting.
- **Are the shares drifting?** If the senior share has been rising steadily across
  2022–2026, a trailing-average share will underestimate it. Use a trended share.

This analysis is worth doing regardless of which option you pick, because *"children's
demand peaks in month X for reason Y"* is a substantive finding about summer meal gaps,
not just a modelling detail. SUN Bucks (summer EBT) appears in the call data and is
directly relevant.

---

## Sanity checks before submitting

- [ ] The three age predictions **sum to** the individuals prediction, county by county.
- [ ] No county has a negative or zero prediction for a group that has never been zero.
- [ ] Age shares are within the historical range for that county — a county whose senior
      share has been 20–25% for four years should not be predicted at 45%.
- [ ] Backtested on August 2023, 2024 and 2025 at the age-group level, not only on the
      total.
- [ ] Counties where an age group is small enough to be noise are pooled or flagged.
- [ ] Same leakage audit as the main question, by someone other than the author.

---

## Deliverables

- [ ] County × age-group prediction table for August 2026
- [ ] The seasonal index by age group (chart)
- [ ] A stated reason for choosing Option A or Option B
- [ ] Backtest at the age-group level
- [ ] One sentence on what the age split tells The Food Group operationally — the
      addendum is graded on insight, not only on the numbers
