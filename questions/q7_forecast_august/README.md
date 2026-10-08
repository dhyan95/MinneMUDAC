# Q7 — Forecast August activity

**Division:** undergraduate and graduate. **Graduate addendum required** — see
[addendum.md](addendum.md).
**Ownership:** Dhyan — county forecasts; Uddam — graduate age-group addendum
**Status:** county baselines, backtests, August 2026 forecasts, and age-group analysis
implemented. Independent leakage audit and organizer clarifications remain outstanding.

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

Predict **August 2026** for each Minnesota county: visits (`HouseholdsReg`), pounds
distributed (`PoundsReg`), and individuals served (`IndividualsReg`).

The graduate addendum requires separate predictions for **children** (`ChildrenReg`),
**seniors** (`SeniorsReg`), and **adults** (`AdultsReg`). The brief says a separate
Individuals prediction is no longer required for the age-group addendum because it is
the sum of those three predictions. This does not remove Individuals from the main Q7
ask; derive or reconcile it from the age predictions rather than treating it as an
additional independent age-group forecast.

---

## Data

Everything you need is in `data/processed/county_month.parquet`: 86 counties × 55 months,
2022-01 to 2026-07, with `n_sites_reporting` alongside every metric.

Age splits (`children`, `adults`, `seniors`) are in the same table and sum to
`individuals` in complete rows. The addendum now asks for forecasts of the three age
groups themselves; the prior suggestion to forecast Individuals first and allocate it
by age shares is not required. Age-share and seasonal analysis can still inform the
forecasts, but evaluate the age predictions directly.

---

## Approach

`analysis.py` backtests six transparent candidates on August 2023, 2024 and 2025.
Every fold uses only rows strictly before its August target:

1. **Seasonal naive:** repeat the previous August.
2. **August/July ratio:** July times the county's median earlier August/July ratio.
3. **Seasonal naive with drift:** previous August times the latest available
   year-over-year August growth; when two August observations are not available, it
   falls back to seasonal naive.
4. **Pooled August/July ratio:** shrink the county ratio toward the statewide median
   ratio using two prior-year observations as the statewide prior. This stabilizes
   counties with short or noisy histories.
5. **Pooled trailing-quarter ratio:** average the county's May, June and July activity,
   then scale that recent level by a historical August/(May–July average) ratio. The
   county ratio is shrunk toward the statewide ratio using the same two-year prior.
   This tests whether a three-month recent level is more stable than July alone.
6. **Per-site ratio:** forecast activity per reporting site and multiply by the
   historical August/July reporting-site ratio.

Counties with no activity history cannot use these county-specific baselines. For
those counties, `analysis.py` reports a separately labeled rural-peer imputation:
the mean 2023–2025 August activity per food-insecure person among nonmetro Minnesota
counties (RUCC 4–9), multiplied by the target county's latest available food-insecure
population estimate. For 2025, the 2024 need estimate is used because it is the latest
available. Individuals are derived from the three imputed age-group estimates. These
rows have no county-specific prediction interval and must not be presented as normal
model forecasts.

The same candidates are evaluated separately for households, pounds, individuals,
children, adults and seniors. Method selection now minimizes average fold-level
county RMSE, matching the prediction metric in the draft graduate rubric. sMAPE, WAPE
and MAE remain reported as complementary diagnostics. Individuals is reported as the
sum of the three selected age-group forecasts, as required by the graduate addendum;
its independently forecast candidates remain in the backtest for comparison.

The forecast interval uses the 10th and 90th percentiles of the selected method's
backtest residuals, pooled across counties and folds. It is a rough empirical
uncertainty range, not a calibrated guarantee: only three August backtest folds are
available. The script does not fit a more complex model unless a later change first
defines and validates it against these same leakage-safe baselines.

Run from the repository root:

```bash
python questions/q7_forecast_august/analysis.py
```

For an interactive walkthrough of the data checks, backtests, forecasts and diagnostics,
open and run [the Q7 notebook](../../notebooks/q7_forecast_august.ipynb) from top to
bottom. It includes rubric-aligned county RMSE charts and statewide plots comparing each
candidate's fold RMSE with the selected pooled May–July method highlighted for the five
rubric-scored outcomes, plus statewide plots comparing candidates with historical actuals
and the final August 2026 forecasts. The all-method RMSE comparison is also saved as
`outputs/figures/q7_method_rmse_comparison.png`. Statewide aggregation is for
visualization only; it can hide county-level errors. The notebook calls the same analysis
script; it does not implement a separate forecasting pipeline.

It writes:

- `outputs/tables/q7_backtest_predictions.csv` — county-level actuals and candidate
  predictions for the three backtest Augusts.
- `outputs/tables/q7_backtest_scores.csv` — fold and combined RMSE, MSE, sMAPE, WAPE
  and MAE.
- `outputs/tables/q7_method_selection.csv` — average and worst-fold scores used to
  choose each outcome's forecast method, with `selected_for_forecast` marking the
  final choice (including the required age-sum Individuals forecast).
- `outputs/tables/q7_forecasts.csv` — August 2026 county predictions, empirical
  intervals, selected methods and county age-share sanity-check flags.
- `outputs/tables/q7_uncertainty_calibration.csv` — residual quantiles used for the
  intervals.

The county reference contains all 87 counties, but Wilkin has no activity history in
the panel. Its predictions are therefore rural-peer imputations marked
`imputed_rural_peer_rate`, not county-specific model forecasts; their prediction
intervals are blank. The processed county-month panel also rolls Hennepin and Ramsey up
to whole counties and does not retain the split labels. The output therefore covers
whole counties only.

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
- **Are Hennepin and Ramsey scored whole or split?** The processed county-month panel
  rolls them up and does not retain split-level activity. Ask the organizers; if split
  forecasts are required, rebuild the panel with split labels before forecasting.

---

## Deliverables

- [x] `analysis.py` producing August 2026 predictions for the three main metrics and
      the three graduate age groups; derive Individuals from age groups where applicable
- [x] Backtest results for 2023, 2024 and 2025 against every baseline
- [x] A stated uncertainty range, not just a point estimate
- [x] [addendum.md](addendum.md) completed — children, seniors, adults, separately
- [ ] **Leakage audit signed off by someone other than the model's author**
- [ ] Submission in whatever format the organizers specify (ask early)
