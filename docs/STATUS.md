# Status — end of week 1, plan for week 2

Updated 28 September 2026, after the meeting with the advisor. Checked against `main` at
`943c68e`, `uddam-branch` at `54043ed` and `dhyan_branch` at `e123861`.

**Deadline: Saturday 17 October 2026.** 19 days left. Day 7 of 26.

---

## What changed on 28 September

The advisor raised four points about Q4. All four are answered in a new notebook,
`notebooks/q4_advisor_followup.ipynb`, on `dhyan_branch`.

| The advisor asked | Answer |
|---|---|
| Run HAC with a 12-month window | Done. It changes the standard errors by less than 10% and none of the conclusions. The window was never the problem. |
| Is a 4 to 6 month delay too late? | Yes. The data does not support it. |
| Could something else be interacting? | Yes. Activity jumped 20% in one month, March 2023. That was the month of the last extra SNAP payment in Minnesota; benefits fell in April. |
| Redo the county split by metro | Done. Cost and metro are largely the same split, and neither matters once county size is removed. |

**The Q4 headline changes.** "Demand rises 4 to 6 months after prices rise" is withdrawn.
The details are in the Q4 section below.

**The order of work changes.** Q5 should be done before Q4 is finished. The reason is in
the Q5 section.

---

## Open decisions

Carried over from the agenda for 28 September. Strike out the ones the meeting settled.

| # | decision | who it affects | note |
|---|---|---|---|
| 1 | **Date of the findings freeze** | all | The plan's weekday labels are one day off; it calls the 17th a Friday. Pick Friday 9 or Monday 12 October, then correct week 4 |
| 2 | **Q7: who starts the baselines, and when** | Dhyan, Uddam | The only scored prediction, and nothing exists yet. The plan calls the backtests the most important deliverable of week 2 |
| 3 | **Dhyan's load** | all | He owns Q4, Q5 and the Q7 model. One is drafted. Decide whether anything moves |
| 4 | **SNAP reporting units** | Dhyan | The SNAP series is found. 11 counties are not reported one by one. Accept 79 units, or split them |
| 5 | **Who claims 2023: Q4 or Q5** | Dhyan | Proposed answer: Q5 claims what county exposure to the SNAP cut can explain, and Q4 gets the rest. Q5 can remove prices completely with month dummies. Q4 cannot remove SNAP |
| 6 | **One definition of a food shelf site** | Uddam, Valentino | Q8 counts 723 sites; 278 never reported activity. Valentino can add the shared flag to `sites.parquet` |
| 7 | **The opening line of the deck** | Uddam | The plan's "strongest single fact" is a correlation with a built-in tilt. Replace it with the log-log slope |
| 8 | **When notebook numbers move into `analysis.py`** | all | Nothing is in a script yet, and rule 6 says every slide number comes from one |
| 9 | **Untrack the 85 MB Atlas file** | all | Doing it deletes the file from everyone's working copy on their next pull |

### One sentence per drafted question

| question | chart | one sentence |
|---|---|---|
| Q1 | log-log fit, notebook cells 7–8 | activity follows county size, not need intensity |
| Q4 | the four series over time, follow-up notebook section B | activity grew fastest in 2023, and prices cannot be separated from the SNAP cut in statewide data |
| Q8 | population-weighted distance curve | 40% of rural LILA residents are within 5 miles of a site, against 99% urban |

### Housekeeping

- `dhyan_branch` now includes `main`, so it has the SNAP loaders and the `cfg` alias.
- `uddam-branch` is 6 commits behind `main`. It touches none of the same files, so it
  merges cleanly.
- Record the panel v1 sign-off and the Section-2 decisions.

---

## Where we are

| question | owner | state | lives in |
|---|---|---|---|
| Q1 need vs activity | Valentino | sub-questions 1–3 answered, 4 fitted and not yet interpreted | `notebooks/q1_exploration.ipynb` |
| Q4 food prices | Dhyan | exploratory draft, plus a follow-up that revises its headline | `notebooks/q4_exploration.ipynb` and `q4_advisor_followup.ipynb` on `dhyan_branch` |
| Q5 SNAP | Dhyan | **data found and loaded**; analysis not started | `src/build_snap.py`, `questions/q5_snap/SNAP_DATA_NOTES.md` |
| Q6 divergence measure | Valentino | not started (week 2 item) | |
| Q7 forecast | Dhyan, Uddam | not started | |
| Q8 LILA access | Uddam | crosswalk built, coverage and retail comparison drafted | `notebooks/q8_exploration.ipynb` on `uddam-branch` |

### Progress against the README checklists

| question | deliverables | drafted | final |
|---|---|---|---|
| Q1 | 6 | 4 | 1 |
| Q4 | 5 | 3 | 0 |
| Q8 | 6 | 4 | 2 |
| Q5 | 6 | 1 | 0 |
| Q6 | 6 | 0 | 0 |
| Q7 | 6 | 0 | 0 |
| **Total** | **35** | **12** | **3** |

"Drafted" means it exists in a notebook. 23% of the time is used and about a third of the
deliverables are drafted. Against the plan the team is on pace: week 1 asked only for
foundations, and three questions already have draft answers.

### Week 1 scorecard

| who | goal | status |
|---|---|---|
| Valentino | Q1 county frame built | done |
| Valentino | Public covariates downloaded and registered | done, 8 sources |
| Valentino | Panel v1 signed off | built; sign-off not recorded |
| Uddam | Atlas downloaded | done |
| Uddam | 2010→2020 tract crosswalk working | done, one counting bug |
| Uddam | Source registry started | done; relationship file row missing |
| Dhyan | BLS CPI downloaded, truncated at 2026-07 | done on his branch; registry date still blank |
| Dhyan | Find the MN county-monthly SNAP series | **found**, in the repo, cut at 2026-07 |
| all | Re-run pipeline, confirm same numbers | Uddam's re-run matches to 14 decimal places |
| all | Organizer email sent | not visible in the repo |
| all | Section-2 decisions agreed and recorded | not visible in the repo |

**End-of-week-1 test** (every source on disk, truncated, registered): passes.

---

## Announcements

### The config alias is now `cfg`

`import config as C` is now `import config as cfg` in every `.py` file on `main` and in
the Q1 notebook.

- **Why:** `C(...)` is also the statsmodels formula shortcut for a categorical variable.
  With `C` taken by the config module, any formula using it fails.
- **Not changed:** the two notebooks on the open branches. They keep working as they are,
  because the alias is local to each file.

### New loaders for SNAP

```python
qkit.snap()                   # SNAP caseloads, unit x month, leakage-checked
qkit.snap_units()             # county -> unit
qkit.activity_by_snap_unit()  # food shelf activity on the same units
```

Run `python src/build_snap.py` once after pulling.

---

## Q1 — Valentino

### Findings

- In counts, need and activity agree almost perfectly (Pearson about 0.95). That is
  mostly county size.
- Activity does not rise with need intensity. Per food-insecure person, Spearman with
  `fi_rate` is −0.15 to −0.29. Per 1,000 residents it is about 0.
- The log-log fit of activity on food-insecure persons has a slope of about 1.2: bigger
  counties get more activity per person in need.
- Most activity below what need predicts: Nicollet, Pope, Lac qui Parle, Benton, Norman,
  Roseau. Most above: Steele, Washington, Rice, Renville, Cook, Mahnomen.
- Several "below" counties border "above" ones (Nicollet / Blue Earth, Roseau / Kittson,
  Benton / Sherburne). Consistent with people crossing county lines. Observed, not shown.
- Wilkin has a need estimate and no reporting food shelf at all.
- The ranking holds when only food-shelf-like sites are counted (Spearman 0.94 between
  the two rankings). Cook is the exception: two outreach programs roughly triple its
  count.

### Sub-question 4

Hypotheses were written down before any result was looked at (notebook cell 12). Model:
county-year residual on distance to nearest site, `rucc` in three groups, share of
households with no vehicle, share on SNAP, and year dummies, with standard errors
clustered on county. n = 258 county-years, 86 counties.

**Nothing is statistically significant. R² = 0.03.** Distance has the predicted sign
(−0.10 per standard deviation, p = 0.16). Adding poverty changes nothing.

A county's own characteristics do not explain the mismatch. That is what the
cross-county story would predict.

### Caveats for the slides

1. The per-food-insecure-person correlation has a built-in negative tilt: `fi_persons` is
   in the denominator of one axis and the numerator of the other.
2. The per-1,000-residents version has a ratio problem too. Dividing by population only
   removes county size if activity is exactly proportional to size, and the slope of 1.2
   says it is not. Use that chart as an illustration, not as the evidence.
3. 2024 uses a different MMG edition from 2022–23. The stronger 2024 numbers are not a
   trend.
4. County is where the site is, not where the client lives.
5. Households stand in for visits. A household is counted once per month.

---

## Q4 — Dhyan (`dhyan_branch`, not merged)

Two notebooks. `q4_exploration.ipynb` is Dhyan's draft. `q4_advisor_followup.ipynb` answers
the advisor's questions and revises the draft's headline. The follow-up runs on its own
and does not change the draft.

### Supported answers to the four Q4 questions

| Q4 asks | Answer |
|---|---|
| Do more people arrive when prices rise? | Activity grew fastest during and just after the 2022 to 2023 inflation. The largest move is a 20% jump in March 2023, which is a step and points to an event. The SNAP cut and a rise in reporting sites fall in the same months, and statewide data cannot separate the three. |
| At once, or after a delay? | Not after 4 to 6 months. Where a response shows, it is at about one month. |
| In all three metrics? | In pounds and individuals. Not clearly in households. |
| What cycles do prices not explain? | The seasonal pattern stands: an October peak, a January or February low, a swing of about 20%. |

### Findings, with the numbers

**1. A 12-month HAC window changes nothing.** For households at lag 5 the coefficient is
4.71 and the standard error is 0.83, 0.90 or 0.88 under the three methods. The reason the
p-values cannot be trusted is different: lagged food inflation has a correlation of 0.99
with its own previous month. It is one smooth decline, so the 42 months are one episode
and nowhere near 42 independent observations.

**2. The 4 to 6 month lag came from the method.** Three pieces of evidence:

- The correlation between prices and activity rises steadily from a 6-month lead to a
  10-month lag. It never peaks at 4 to 6. It is already 0.34 to 0.50 when prices move one
  month *after* activity, which cannot be a response.
- The sites control has a correlation of 0.93 with lagged prices. The model had two
  explanatory variables that were nearly the same series.
- With SNAP and a time trend added, the price coefficient is flat across lags 0 to 10.

**3. Activity jumped 20% in March 2023 and stayed there.**

| February to March 2023 | households | pounds | individuals |
|---|---|---|---|
| Change in one month | +19.9% | +21.9% | +22.3% |

The number of reporting sites did not change. In 2024, 2025 and 2026 the same month's
change was between minus 2% and plus 6%. In year-over-year data a one-time jump looks
like 12 months of high growth, and growth did fall from 30% to 6% in March 2024.

**4. Adding SNAP takes a third or more off the price effect.**

| | households | pounds | individuals |
|---|---|---|---|
| R², prices and sites only | 0.49 | 0.63 | 0.67 |
| R², with SNAP added | 0.75 | 0.72 | 0.81 |
| Price coefficient, before | 4.71 | 3.52 | 5.32 |
| Price coefficient, with SNAP and trend | 2.93 | 2.30 | 2.89 |

**5. In month-to-month changes, the one lag that stands out is one month.** A model with
lags 0 to 6 together gives +7.0 for pounds and +7.7 for individuals at lag 1. Both pass a
correction for 21 tests. Households does not (p = 0.12). Lag 2 is negative in all three,
and the total over six months cannot be told apart from zero.

**6. The county cost gap was county size.** 22 of the 27 metro counties are in the
higher-cost group. The gap in the draft was in the means (3.19 against 2.14) and came
from three counties: Steele, Washington and Olmsted. On medians it is not significant
(p = 0.16). With county size removed, neither cost (p = 0.70) nor metro status (p = 0.60)
makes a difference. This matches the null result in Q1.

**7. "Households per food-insecure person" carries one of Q1's two caveats.** The built-in
tilt does not apply, because Q4 sets the ratio against cost and not against the
food-insecurity rate. The county-size caveat does apply: a county with 10 times the
food-insecure people records 1.34 times the ratio. Use the Q1 residual for any comparison
across counties.

### What to be careful about

- **The jump came before the cut.** Activity jumped in March 2023. Minnesota paid the
  last extra SNAP benefit that month, and benefits fell in April. Both dates are
  confirmed (see the Q5 section). So households and food shelves either acted on the
  announcement, or the jump has another cause. Statewide data cannot say which.
- **Growth was already 41% in January 2023**, before the jump. The jump is part of the
  story, not all of it.
- **The one-month response is weak evidence.** 46 months, 19 parameters, and the metric
  that stands in for visits does not show it.
- **Every p-value in the year-over-year models is unreliable**, for the reason in
  finding 1. That includes the one on SNAP.

### Corrections to make in `q4_exploration.ipynb`

| Where | Change |
|---|---|
| Top cell | Replace the 4 to 6 month claim |
| Step 2 | The base and `_fs` columns are identical only because `food_shelf_only=True` overwrites one with the other. Without the flag they differ by about 7% of pounds. No result changes. |
| Step 10b | Mark as superseded, the way Step 10a is |
| Step 12 | "CPI adds 19% to 28% to R²" is from the model without SNAP |
| County cost comparison | Replace the comparison of means |

### Still open

- **February 2022 is unexplained**: 157,600 households against 115,500 in January, with
  the site count flat. This is a panel question, so it goes to Valentino.
- The follow-up was run on Python 3.12. Dhyan's machine has Python 3.9. The code avoids
  anything newer, but it has not been run there.

---

## Q5 — Dhyan

The county-monthly SNAP series exists. Full notes are in
`questions/q5_snap/SNAP_DATA_NOTES.md`.

| | |
|---|---|
| Span | 2016-01 to 2026-07, 127 months, none missing |
| Grain | 79 county units and 3 tribal nations |
| Publication lag | about one month |
| Emergency allotments end | federal dollars per case: $453 in March 2023, $267 in April 2023 |
| Size of the cut | 47% at the median unit, from 37% to 54% |
| Exposure before the cut | 7.7% of residents on SNAP at the median unit, from 2.8% to 14.7% |

### What to know

1. **The download held August 2026.** Those 87 rows were removed before the file entered
   the repo. The original is kept outside the repo folder.
2. **11 counties are not reported one by one**, so they are grouped: Dodge, Steele and
   Waseca; Pope and Grant; and six southwest counties whose rows trade cases from month
   to month while their total stays flat.
3. **Tribal nations are reported apart** from the counties their members live in, about
   2.7% of the state. Beltrami and Mahnomen are the counties most affected.
4. **This touches Q1.** Steele and Pope are both inside combined units.

### How Q5 relates to Q4

SNAP can be used in Q4 as a control. That does not answer Q5.

| | Q4 | Q5 |
|---|---|---|
| Role of SNAP | A control: something else that moved | The subject |
| Data | One statewide series | 79 county units |
| Where the evidence comes from | Change over time | Differences between counties in how exposed they were to the cut |

**Q5 should come first.** Every county faces the same price index in a given month, so
month dummies in a county model remove prices completely. A statewide series has no
counties to compare, so Q4 cannot remove SNAP. Estimate the SNAP effect in Q5, then return
to Q4 and see what prices explain in what is left.

### The timeline of the cut, confirmed

| when | what happened |
|---|---|
| 29 December 2022 | The law ending emergency allotments is signed |
| January and February 2023 | Minnesota counties notify households |
| February 2023 | Last month of eligibility |
| **March 2023** | **Last extra payment in Minnesota. Food shelf activity jumps 20%.** |
| **April 2023** | **First month with the regular benefit only** |

Minnesota paid the extra benefit the month after eligibility, which is why the dashboard
shows the fall in April while national sources say March. Sources are listed in
`questions/q5_snap/SNAP_DATA_NOTES.md`.

**Q5 has to choose which month is the event.** An event study dated to April puts the
March jump in the "before" period and misses it.

---

## Q8 — Uddam (`uddam-branch`, not merged)

The map code moved from `map.py` into a notebook, and the notebook now drafts README
steps 3 to 5: population-weighted coverage by distance band, urban and rural split, all
four LILA definitions, and a comparison with USDA grocery access.

**Draft headline:** about 40% of the rural LILA population is within 5 miles of a site,
against 99% of the urban LILA population and 58% of the rural non-LILA population.

### To fix, most important first

1. **The site list includes sites that are not operating, and it now drives the distance
   numbers too.** The notebook counts 723 sites. 278 never appear in the activity data,
   and 415 were active in the last 12 months. `FOOD_SHELF_TYPES` was written for the
   activity table; applied to the site master it lets in 285 "Agency or Tribal Nation"
   entries, a type with 16 reporting sites and about 0% of pounds. Coverage is overstated
   until this is fixed.
2. **Sites are placed at the centre of their tract, not at their block.** In a large
   rural tract that can be off by miles, and the rural 5-mile figure is the one most
   exposed. The 15-digit `block_geoid` is available. Either use block locations or state
   the size of the error.
3. **`parent_count` is still inflated about 35×.** The notebook table shows 693 tracts
   with one parent; counting only parents that cover at least 5% of the tract gives
   1,479. The new retail crosswalk in the notebook uses the correct denominator;
   `build_lila.py` does not yet. Run `build_lila.py --force` after fixing.
4. **The grocery comparison needs the urban and rural split before it is read.**
   Low-grocery-access tracts are less likely to contain a site (23% against 35%), but
   their residents are more often within 5 miles of one (91% against 70%). The half-mile
   definition is mostly urban tracts, so the two groups differ in more than grocery
   access.
5. The map footnote is hidden behind the legend, and three all-water tracts in Lake
   Superior show as "LILA status unavailable".
6. The relationship file has no row in the registry of downloaded files.
7. Registry typo: "Minneosta".

---

## Week 2 (29 September – 5 October)

**Goal from the plan: one rough chart and one sentence per question.** Anything with no
number by the end of the week is what gets descoped, decided as a team.

### Valentino

| # | task | note |
|---|---|---|
| 1 | Interpret the sub-question 4 output | which signs match the hypotheses; what R² = 0.03 means; whether the three metrics agree |
| 2 | Report the log-log fit as the Q1 headline | chart and table are in the notebook (cells 7–8); read them and write the sentence |
| 3 | Moran's I on the residuals | needs the Census county adjacency file and a registry row; write the predicted sign first |
| 4 | Port Q1 into `analysis.py` | it stops at Step 3 today |
| 5 | Update the Q1 README | status line and deliverables |
| 6 | **Q6: design the need index** | write the falsifiable definition before any result exists |
| 7 | Panel: add `is_food_shelf_like` and last active month to `sites.parquet` | gives Q8 the shared site definition |
| 8 | Panel: look into February 2022 | for Q4 |

### Dhyan

| # | task | note |
|---|---|---|
| 1 | **Q7 baselines backtested on August 2023, 2024 and 2025** | the plan's most important week 2 deliverable |
| 2 | Q5: decide which month is the event, and say why | the announcement, the last extra payment (March 2023) or the first reduced payment (April 2023) |
| 3 | Q5: decide the units, tribal nations and benefit series | the four decisions in `SNAP_DATA_NOTES.md` |
| 4 | Q5: event study with county exposure and month dummies | the data and loaders are ready; do this before finishing Q4 |
| 5 | Q4: make the five corrections to `q4_exploration.ipynb` | listed in the Q4 section |
| 6 | Q4: run `q4_advisor_followup.ipynb` on his own machine | it has only been run on Python 3.12 |
| 7 | Q4: Minneapolis-St. Paul CPI as a robustness check | the README asks for it |
| 8 | Fill in the CPI registry date, merge the branch | |
| 9 | Move the Q4 numbers into `analysis.py` | |

### Uddam

| # | task | note |
|---|---|---|
| 1 | Q8: fix the site definition and re-run coverage | depends on Valentino's task 7, or filter on `site_month` directly |
| 2 | Q8: fix `parent_count` in `build_lila.py` | |
| 3 | Q8: block-level site locations, or the size of the error | |
| 4 | Q8: move the coverage numbers into `analysis.py` | |
| 5 | Q7 age-share analysis | children, adults, seniors |
| 6 | Deck skeleton | one slide per question, titles only |
| 7 | Registry: relationship file row, typo | |
| 8 | Merge the branch | |

### All

- Correct the weekday labels in `TEAM_PLAN.md`.
- Send the organizer email if it has not gone out.
- Record the Section-2 decisions in our own words.
