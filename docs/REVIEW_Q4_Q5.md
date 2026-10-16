# Review of Q4 and Q5 — `dhyan_branch` at `547a141`

Reviewed 6 October 2026 at Dhyan's request. Every number below was recomputed from the
processed data on `main` plus the CPI file on `dhyan_branch`; the scratch scripts are not
in the repo, but each check is one regression and is described well enough to repeat.

Short version: **both analyses are sound in design and both conclusions need changing.**
Q5's "demand rose smoothly, no jump at March 2023" is an artefact of how the month effects
were plotted; the model itself shows a 19% step. Q4's final single-lag regression is the
result the follow-up notebook refuted on 28 September, and it depends entirely on 2023.
Fixing both removes the contradiction between the two questions: they then agree that
March 2023 was a step, that prices cannot explain a step, and that SNAP exposure does not
explain it either.

---

## Q5 — the event study

### What is right

The design is the right one and it is carefully done: 79 reporting units at the source's
own grain, unit and month fixed effects, errors clustered on unit, two independent
exposure measures, the metro split, zeros dropped before logs rather than fudged. Finding
the Hennepin reporting drop is the most useful data observation anyone has made for Q7.
Nothing below changes the headline that **exposure to the cut does not predict a larger
rise in demand**.

### 1. "No jump at March 2023" is a plotting artefact — the model shows a 19% step (high)

The month effects in Steps 7a and the saved figure come from a model that also contains
`exposure_x_post`. In that model a month effect is the level for a unit with **zero
exposure**. No unit has zero exposure; the mean is 7.5. The exposure term carries
0.012 × 7.5 = 0.09 of every post-month's level, and that is exactly the size of the step
that went missing from the plot.

| Feb → Mar 2023, log households | step |
|---|---|
| month effects as plotted (zero-exposure unit) | +0.08 |
| same model, evaluated at mean exposure | **+0.17** |
| unit + month effects only, no exposure term | **+0.17** (= +19%) |

At unit level the step is general, not a few big counties: **91% of units rose from
February to March 2023, median +18%**. It is the largest single-month step in the
series apart from January to February 2022.

What to change:

- Step 7a and the figure `q5_month_effects_event_study.png`: plot month effects from a
  model without the exposure term, or add `b × mean exposure` to the post months. The
  title "rose steadily through 2023 — no sharp jump at the SNAP cut" has to go.
- Step 9's "demand rose smoothly across 2023, not in a step" and "this shape favors a
  price-driven story" both go. Prices fell smoothly through 2023 and cannot produce a step;
  your own last cell makes the same point (correlation 0.06 between month-to-month demand
  change and lagged inflation).
- The honest sentence: *demand stepped up about 19% in March 2023 in nearly every unit,
  and the size of that step did not depend on how many of the unit's people were on SNAP.*

This also removes the disagreement with Q4, which found the same 20% step in the state
totals. Both questions now say the same thing about 2023.

### 2. Report the interval, not only the p-value (medium)

The null is real but it is not tight. From your specification:

| | coefficient | 95% interval |
|---|---|---|
| per percentage point of exposure | 0.012 | −0.018 to +0.042 |
| per one standard deviation of exposure (2.4 points), post period | +2.9% | **−4% to +10%** |

So the data rule out a large concentration of the rise in high-SNAP units; they do not
rule out a moderate one. "No evidence that high-exposure counties rose more" is right.
"The strain was felt broadly, not concentrated" (the deck sentence) says more than the
interval allows; say "we found no sign that it was concentrated".

Two checks that strengthen the null and should go in as cells:

- **Short windows.** Exposure × (March–August 2023), on top of exposure × post:
  −0.017, p = 0.20. Exposure × (March 2023–February 2024): −0.015, p = 0.25. The null is
  not an artefact of averaging over 41 post months.
- **Pre-trend.** Exposure × linear month over January 2022–February 2023: −0.001,
  p = 0.29. High-exposure units were not already on a different path.

### 3. A claim the code does not make (medium)

The markdown after Step 4d says Hennepin's final months "are excluded from / flagged in
the regression as a robustness consideration". No cell does this. I checked: dropping
Hennepin from February 2026 onward leaves the coefficient at 0.012, p = 0.42. Either add
that cell or delete the sentence; a judge who reads the notebook will look for it.

### 4. Small things (low)

- `pre_event_snap_participation_percent` as a main effect alongside `C(snap_unit)` is
  collinear with the unit effects and is absorbed. Harmless, but remove it from the
  formula so the output does not show a meaningless coefficient.
- `n_sites_reporting` is merged into the panel and never used. Adding log sites as a
  control: exposure coefficient 0.012, p = 0.40, sites coefficient 0.30. Worth one line.
- Tribal nations are excluded from the SNAP counts, so exposure is understated for
  Beltrami, Mahnomen and Clearwater. State it in the limitations.
- The six unit-months with zero households are dropped before the log. State it.
- Deck sentence: "high-need areas" should be "areas with more people on SNAP". Need is
  Q6's word and means something else there.
- The notebook's cells are out of order (Step 2 before Step 1). Harmless, confusing.

---

## Q4 — prices

### What is right

The exploration is honest about its own weak spots: Step 7 shows the correlation
disappears after 2024, Step 8 shows the lag scan is an artefact, Step 15 discards an
invalid number, and the cost-group comparison now carries the county-size correction.
The seasonal finding (October peak, January/February trough, about a 20% swing) is the
firm result and should lead the slide.

### 1. The final single-lag regression is the spurious result, and it rests on 2023 (high)

Step 19 regresses individuals YoY on CPI YoY at lag 1, plain OLS, no controls, and reports
coefficient 4.1, p = 0.0000, R² = 0.40, then converts it to "26,264 more individuals per
percentage point of inflation". Recomputed, with what is behind it:

| | coefficient | p | R² |
|---|---|---|---|
| as in the notebook (n = 42) | 4.11 | 0.0000 | 0.40 |
| **excluding 2023** (n = 30, which is the same as 2024 on) | **1.40** | **0.60** | **0.01** |
| same regression at lag 0, 1, 2, 3, 4, 5, 6 | 4.3, 4.1, 3.8, 3.8, 3.7, 3.6, 3.5 | | |

Three things follow:

- **The relationship exists only in 2023.** Mean YoY growth was +40% in 2023 and +2% in
  every other year; mean lagged inflation was 6.3% in 2023 and 1.6% otherwise. One year
  of high growth coinciding with one year of high inflation is one observation, not 42.
  Without it, nothing is left.
- **The p-value is not a p-value.** Durbin–Watson is 0.35 and the lag-1 residual
  autocorrelation is 0.82. YoY series of overlapping 12-month changes are smooth by
  construction, and the follow-up showed on 28 September that neither HC1 nor a 12-month
  Newey-West window fixes this, because the 42 months are one episode. "p = 0.0000" on a
  slide invites the one question that sinks it.
- **"Lag 1" is not identified.** The coefficient is 3.5 to 4.3 at every lag from 0 to 6,
  because CPI YoY barely changes from one month to the next. The one-month response the
  follow-up found came from a different design: month-over-month changes with month
  dummies and all lags in one model (pounds +7.0 at lag 1, p < 0.001; individuals +7.7;
  households not significant; lag 2 negative; six-month total indistinguishable from
  zero). That is the evidence for "about one month"; Step 19 is not.

Also: the Step 19 markdown says lag 5 "chosen from earlier exploration" while the code
uses lag 1. One of them is wrong.

What to change:

- Replace Step 19 with the month-over-month distributed-lag result from the follow-up
  notebook, stated with its caveats (46 months, 19 parameters, households does not show
  it). That is simple enough for the advisor's request and it is the result that survives.
- Drop the "26,264 individuals per percentage point" translation, or keep it only with
  "if the 2023 relationship were causal and repeated, which we cannot show".
- The header's "consistent with a population with little to no savings buffer" is a story
  the data does not test. A judge who asks "how do you know it is savings?" gets no answer.
  State what was found and stop.

### 2. The notebook argues with itself (medium)

Step 7 says the correlation is "mostly shared trend plus reporting growth" and is negative
after 2024. Step 8 says the lag pattern is an artefact. Steps 10a, 10b and 12 are marked
superseded. Then Step 19 asserts a strong price effect from a weaker version of the same
regression. Reading top to bottom, the notebook's own evidence contradicts its conclusion.
Either move the superseded steps to an appendix or delete them, and make the conclusion
follow from what remains.

### 3. Small things (low)

- Step numbers run 1, 3, 4, 5, 6, 2, 7, 8, 9, 10a, 10b, 11, 12, 14, 5, 15, 6, 19. Renumber
  before anyone else reads it.
- Step 4 calls the BLS API inside the notebook and writes the file; the registry row now
  exists, so the "TODO if not done" can go. Keep the October 2025 gap as NaN, as you do.
- The cost-group section is now correct and well caveated. It is a limitation slide, not a
  finding, and the text says so.

---

## The 2023 paragraph both questions can share

For the deck, so the two slides do not disagree:

> Food-shelf demand stepped up about 19% in March 2023 and stayed there. The step appears
> in nearly every county (91% of SNAP reporting units rose that month, median +18%). It is
> not a price effect: food inflation fell smoothly through 2023 and cannot produce a step,
> and once 2023 is set aside there is no relationship between inflation and demand. It is
> not explained by SNAP exposure either: counties with more people on SNAP did not rise
> more than counties with fewer (95% interval for one standard deviation of exposure, −4%
> to +10%). March 2023 was the month Minnesota paid the last emergency allotment, so the
> timing fits the announcement of the cut, but a statewide step cannot be attributed to it
> with county data alone.

---

## Delivery, which is the larger gap

Both `analysis.py` files are 60-line skeletons with TODOs and no outputs; both READMEs say
"not started"; nothing of Q4 or Q5 is on `main`. Rule 6 (every slide number comes from a
script) is not met for a third of the deck. Once the two conclusions above are fixed, the
port is mechanical: the Q5 panel and three regressions, the seasonal index, the
distributed-lag model, the cost-group table. A day, maybe two.

Order I would do it in: fix the Q5 plot and conclusion (an hour), replace Q4 Step 19 (an
hour), port both to `analysis.py`, write the READMEs, merge.

---

## Follow-up, 16 October: the lag model and the March step, recomputed

Done by Valentino's side of the table after the slide text drifted away from the notebook.
Both models were rerun from scratch from `data/processed` and the CPI file, not read off
the notebook. The notebook's numbers reproduce to the decimal.

### Q4, monthly distributed-lag model (lags 0 to 6 in one model, month effects, HAC errors, 46 months)

| lag | households | pounds | individuals |
|---|---|---|---|
| 1 | +3.7, p = 0.040 | +7.0, p < 0.001 | +7.7, p < 0.001 |
| 2 | −6.9, p = 0.012 | −2.3, p = 0.287 | −4.0, p = 0.020 |
| 4 | +7.3, p = 0.085 | +0.3, p = 0.885 | +0.3, p = 0.897 |
| sum of lags 0 to 6 | p = 0.18 | p = 0.06 | p = 0.16 |

What the slides may say: one month after a price rise all three metrics go up, households
by less; two months after, households and individuals drop back; over six months the net
effect is not different from zero, so a price rise moves visits earlier rather than adding
them. **What they may not say:** a month-four response in households. Its p-value is 0.085
and its interval includes zero. The notebook's own conclusion cell already states the
lag-1 and lag-2 story; the slide text was the thing that drifted.

Two things to keep off every slide and out of every answer:

- The notebook prints "+367% per 1% price change" and "+767%". That multiplies by 100
  twice. The coefficients are already in percent (3.7% and 7.7%); the chart is right.
- The month-four bar. If a judge asks, the answer is "not significant, p = 0.085".

### Q5, the March 2023 step, three ways

| check | result |
|---|---|
| unit and month fixed effects, February to March 2023 | +0.176 log = +19.3% |
| unit level, February to March 2023 | median +18.9%, 90% of 78 units up |
| state total, February to March 2023 | +20.3% |
| February to March in 2022, 2024, 2025, 2026 (seasonal control) | −4.2%, −1.2%, +3.6%, +8.6% |
| March 2023 excess over those | +17.4% |
| year-over-year households: Feb 2023, Mar 2023, Apr 2023, Jun 2023 | −0.4%, +34.5%, +30.2%, +38.0% |

The step is real, it is not the spring rise, and it lands in the month the extra SNAP
payments ended. One wording to soften: June 2022 is a step of the same size (+0.179) and
December 2023 is close (−0.162), so "the largest single move" should be "one of the
largest, and the only one that lines up with a dated policy change".

### CPI note

October 2025 CPI was never published (federal shutdown), so that month and its lags drop
out of the lag model. That is why n = 46, not 47. Say so if asked, not before.
