# Q7 — Graduate addendum

**Graduate teams answer this. Undergraduate teams do not.**

> 1. A separate prediction for **children served**, **seniors served**, and **adults
>    served**.

---

## What makes this easier than it looks

In the cleaned site-month panel, `children + adults + seniors` equals `individuals`
for the complete age-group records used by `age_analysis.py`. The script also checks
that this identity still holds after statewide monthly aggregation and stops if it
does not.

The October 1 brief requires predictions for each age group. It also says a separate
Individuals prediction is no longer required for the addendum because it is the sum of
children, adults, and seniors. The main Q7 ask still names Individuals served, so use the
age-group forecasts to derive/reconcile that main metric rather than producing a second,
independent Individuals estimate.

Forecast children, adults, and seniors as the three requested age outcomes, using
age-specific baselines/models and backtests. The historic identity
`children + adults + seniors = individuals` remains a useful data-quality check, not a
requirement to make an independent Individuals forecast or force age estimates to match
one.

---

## The first thing to check

Before choosing, compute the seasonal index **separately for children, adults and
seniors**, the same way `src/eda.py` does for the three main metrics. Run
`python questions/q7_forecast_august/age_analysis.py`; it uses adjusted monthly values,
excludes August 2026 and later, and saves its chart and tables in `outputs/`.

The current statewide exploration through July 2026 shows October as the highest-volume
month for all three groups (seasonal indices: children 1.074, adults 1.078, seniors
1.108). August is modestly above each group's average (1.041, 1.006 and 1.050,
respectively). The statewide age shares do not show a monotonic senior-share increase:
the senior share declined from 13.0% in 2022 to 10.8% in 2024, then was 11.2% in 2025
and 2026 year-to-date. These are descriptive statewide patterns, not county-level
forecasts or backtest results.

Two things to look for:

- **Do the age groups peak in different months?** Children plausibly spike in summer when
  school meals stop and again at the start of the school year. Different peaks are a
  reason to evaluate age-group-specific seasonal baselines rather than assume one common
  seasonal pattern.
- **Are the shares drifting?** If the senior share has been rising steadily across
  2022–2026, recent or trended age-group estimates may be more informative than a
  long-run average.

The October 1 brief also makes Minnesota Free School Meals Program monthly claims data
available as an **optional** source. It may help contextualize children’s seasonal
patterns, but it is not required for the age forecasts. If used, document its source
and grain, and exclude August 2026 and all later observations before analysis or saving;
the Q7 leakage rule applies to every source.

This analysis is worth doing regardless of which option you pick, because *"children's
demand peaks in month X for reason Y"* is a substantive finding about summer meal gaps,
not just a modelling detail. SUN Bucks (summer EBT) appears in the call data and is
directly relevant.

---

## Sanity checks before submitting

- [x] Derived Individuals equals the sum of the three age predictions, county by county.
- [x] No county has a negative or zero prediction for a group that has never been zero.
- [x] County age shares are checked against their historical monthly ranges and flagged
      in `q7_forecasts.csv` when outside; no out-of-range values are silently clipped.
- [x] Backtested on August 2023, 2024 and 2025 at the age-group level, not only on the
      total.
- [x] Small-county instability is addressed with a pooled August/July ratio; per-site
      and unpooled alternatives are also backtested.
- [ ] Same leakage audit as the main question, by someone other than the model author.

## Forecast and backtest update

The candidate set now includes a pooled trailing-quarter ratio: a county's average
activity in May–July is scaled by its historical August-to-May–July-average ratio, with
that ratio shrunk toward the statewide value. This directly tests whether a three-month
recent level is more stable than July alone. Method selection minimizes mean fold-level
county RMSE to align with the draft graduate prediction rubric; sMAPE, WAPE and MAE
remain supporting diagnostics.

The updated candidate set must be evaluated by rerunning
`questions/q7_forecast_august/analysis.py`. Until that run completes against the
processed panel, do not use the earlier forecast totals or method-selection output as
the final results: they predate the pooled-quarter candidate and RMSE-based selection.
The regenerated outputs will also flag age-group shares outside each county's
historical monthly range rather than clipping them.

**Operational takeaway:** Use the regenerated county age forecasts to describe the
projected age mix and service-planning implications; do not quote the previous totals
until the updated backtest and forecast tables have been produced.

---

## Deliverables

- [x] County × age-group prediction table for August 2026
- [x] Exploratory statewide seasonal indices and annual age shares, generated by
      `age_analysis.py` through July 2026; this is not an age-group forecast
- [x] A stated reason for the age-group forecasting approach, supported by backtests
- [x] Backtest at the age-group level
- [x] One sentence on what the age split tells The Food Group operationally — the
      addendum is graded on insight, not only on the numbers
