# Q7 — Forecast August activity

**Division:** undergraduate and graduate. **Graduate addendum required** — see
[addendum.md](addendum.md).
**Owner:** Uddam
**Status:** not started

---

## ⚠ The disqualification rule, first

> August has already happened. You do not have its data, and you must not go looking for
> it. **Use of any August data from any source will disqualify your team.**

This is the only rule in the brief with a stated penalty. Treat it as a hard constraint
on the whole repository, not just on this folder.

**What that means in practice:**

- The food shelf panel ends **2026-07**. Never extend it.
- Any external series (CPI, SNAP, unemployment) must be **truncated at 2026-07 before it
  is saved to disk**. Not filtered at analysis time — truncated at download.
- The `z12MoAverage_*` columns on `Organization` were recomputed in **August 2026** and
  may contain August activity. They are **dropped in `clean_data.py`** and never reach
  `data/processed/`. Do not go back to the raw file for them.
- **One named person audits this before submission.** Not the person who built the model.
  See the team plan.

---

## The ask, in our words

Predict **August 2026** for **each Minnesota county**, for each of the three metrics:
visits, pounds distributed, individuals served.

The graduate addendum adds separate predictions for **children, seniors and adults**.

---

## Data

Everything you need is in `data/processed/county_month.parquet`: 86 counties × 55 months,
2022-01 to 2026-07, with `n_sites_reporting` alongside every metric.

Age splits (`children`, `adults`, `seniors`) are in the same table, and they sum exactly
to `individuals` in every row — we checked, there are **zero** mismatches. That makes the
addendum a share problem rather than three separate forecasts.

---

## Approach

**Baselines first, and they are strong.** Anything more complex has to beat them in a
backtest or it does not go in.

1. **Seasonal naive:** August 2026 = August 2025, per county.
2. **August/July ratio:** July 2026 × the county's historical August/July ratio.
3. **Seasonal naive with drift:** August 2025 × the county's year-over-year growth.

Then:

4. **Backtest on August 2023, 2024 and 2025.** Train only on data before each target.
   Report the error metric you expect to be scored on and at least one alternative.
5. **Pool the small counties.** A county serving 200 households a month is noise under a
   percentage-error metric, and percentage errors are dominated by exactly those
   counties.
6. **Handle reporting composition.** Forecast **per reporting site** and multiply by an
   expected site count, or model the total and carry the risk explicitly. The site count
   is part of what you are forecasting whether you acknowledge it or not.
7. **Only then** try something fitted — county fixed effects with month dummies, or a
   gradient model with lags. It must beat the baseline in the backtest.

---

## What the preview already shows

The August/July ratio, statewide, by year
(`outputs/tables/02_august_over_july_ratio.csv`):

| year | households | pounds | individuals |
|---|---|---|---|
| 2022 | 1.066 | 1.105 | 1.069 |
| 2023 | 1.152 | 1.156 | 1.156 |
| 2024 | 1.024 | 0.993 | 1.016 |
| 2025 | **0.937** | 1.007 | **0.950** |

**The ratio is not stable, and it is trending down.** A naive "August is 6% above July"
would have been wrong in 2025 in the wrong direction. Whatever you do, this table is the
thing to beat, and its instability is the honest uncertainty statement for the slide.

Seasonally, August is **not** the peak — October is, in all three metrics. August sits
mid-range. The peak-to-trough spread across the year is about 21%.

**July 2026 has 489 reporting sites, 2.8% below the trailing 12-month average.** If July
is still receiving late entries, every July-based forecast is biased **downward**. This
is on the organizer question list, and if they confirm July is incomplete, the ratio
method needs an adjustment for it.

---

## Traps

- **Leakage means disqualification.** Everything above.
- **Reporting composition changes the target.** You are forecasting "what gets reported",
  not "what happens".
- **Noisy small counties dominate percentage errors.** Check which metric is scored.
- **Three metrics, three different processes.** Pounds grew +33% over 2022–2025 while
  households grew +63%. Do not reuse one model's parameters across metrics.
- **Overfitting 55 months.** With a short panel and 86 counties, a complex model will
  find structure that is not there. The backtest is the only referee.
- **Are Hennepin and Ramsey scored whole or split?** Our panel rolls them up, and
  `county_split_label` preserves the split. Ask the organizers, and make sure the code
  can produce both.

---

## Deliverables

- [ ] `analysis.py` producing a county × metric prediction table for August 2026
- [ ] Backtest results for 2023, 2024 and 2025 against every baseline
- [ ] A stated uncertainty range, not just a point estimate
- [ ] [addendum.md](addendum.md) completed — children, seniors, adults, separately
- [ ] **Leakage audit signed off by someone other than the model's author**
- [ ] Submission in whatever format the organizers specify (ask early)
