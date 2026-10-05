# Status — end of week 2, plan for week 3

Updated 4 October 2026, for the advisor meeting on 5 October. Checked against `main` at
`b1affc2`, `uddam-branch` at `0ad5462` (Q7, not merged) and `dhyan_branch` at `547a141`
(Q4 and Q5, not merged).

**Deadline: Friday 17 October 2026.** 13 days left. Week 3 of 4 starts Monday.

---

## Where we are, in one table

| question | owner | analysis | `analysis.py` rebuilds the numbers | README has the answers | addendum | on `main` |
|---|---|---|---|---|---|---|
| Q1 need vs activity | Valentino | done | yes | yes | n/a | yes |
| Q4 food prices | Dhyan | done in the notebook | **no: 61-line skeleton, 5 TODOs** | **no: "not started"** | n/a | no |
| Q5 SNAP | Dhyan | done in the notebook | **no: 63-line skeleton, 5 TODOs** | **no: "not started"** | n/a | no |
| Q6 need measure | Valentino | done | yes | yes | written | yes |
| Q7 August forecast | Uddam (was Dhyan) | done: 5 baselines, 3 backtest years, forecasts, intervals | yes | yes | written | no |
| Q8 LILA access | Uddam | done | yes | yes | n/a | yes |

Every question has an answer. What is missing is uneven: Q4 and Q5 exist only as
notebooks, and rule 6 (every slide number comes from a script we can explain) is not met
for them. Q7 needs the leakage audit by someone other than its author. No deck exists
beyond six slide titles.

**How cooked are we:** not cooked. Analysis is ahead of the plan: the week-3 goal was
"six answers become one story", and the six answers exist. The risk has moved from
analysis to delivery, and delivery is concentrated on one person (Dhyan: two scripts, two
READMEs) plus the deck, which nobody owns yet.

---

## The findings, one paragraph each, for the advisor

**Q1.** Recorded food-shelf activity rises faster than need: a county with ten times the
food-insecure people records about sixteen times the activity (log-log slope 1.15 to 1.24,
every interval above 1, R² 0.84 to 0.88). Per 1,000 residents the relationship with the
food-insecurity rate is about zero. Pounds correlates most with the Feeding America
estimate, households least, by a small and consistent margin. Where it breaks down:
Wilkin (no reporting food shelf at all), Nicollet, Pope and Lac qui Parle record the least
relative to need; Steele, Washington and Rice the most. Four county characteristics
(distance to a site, rural class, no-vehicle households, SNAP households) explain 3% of
the mismatch and none shows a clear association; distance is the one to follow up. Three
spatial tests find no general border pattern. The residual partly measures the network:
counties with more sites record more per food-insecure person.

**Q4.** Prices explain little. Activity grew most during the 2022-23 food inflation, but
the largest single move was a 20% jump in March 2023 (all three metrics, one month), which
prices cannot cause. With SNAP and a trend in the model the price effect drops by a third.
Where a response shows, it is at about one month, in pounds and individuals, not
households. The firm finding is seasonality: October peak, January or February trough,
about a 20% swing, the same in all three metrics. *(Dhyan's draft now says this; the
follow-up notebook has the numbers.)*

**Q5.** An event study on 79 SNAP reporting units (unit and month fixed effects, clustered
errors, two exposure measures, metro and non-metro separately) finds **no evidence** that
counties more exposed to the March 2023 benefit cut saw a larger rise in food-shelf demand
(coefficients 0.013 and -0.009, p 0.42 and 0.33). Demand rose through 2023 everywhere. The
timeline is confirmed: last extra payment March 2023, regular benefit only from April.

**Q6.** Definition of need, written before any data: *a household is in need if, at any
point in the past year, it worried about running out of food, regardless of whether it
sought help* (the first item of the USDA food-security survey). The county measure is an
equal-weight index of seven public inputs that are neither demand nor Map the Meal Gap
inputs (SNAP households, no vehicle, senior poverty, housing-cost burden, no diploma, LILA
share, debt in collections). Wilkin was predicted at the 70th percentile of need before the
index existed and landed at the 71st. The index does not predict recorded activity per
resident (Spearman 0.07 to 0.14, all three metrics), agrees with MMG broadly (0.77) and
differs on five of the top ten. Need outranks activity most in Nobles, Grant, Wilkin,
Benton, Wadena; the reverse in Washington, Dodge, Cook, Houston. The top seven on need hold
under every alternative weighting. Two barriers explain the divergence: households without
internet (+0.41 per SD, p = 0.005) and distance to a site (+0.23, p = 0.025); 17% of the
divergence explained. Head to head, county size explains 85% of recorded activity and
neither MMG nor the index adds more than a point: activity follows population, whichever
way need is measured. MMG finds need where incomes are low; the index finds it where costs
and barriers are high.

**Q7.** Five transparent baselines backtested on August 2023, 2024 and 2025, every fold
using only earlier months. The pooled August/July ratio (county ratio shrunk toward the
statewide median) wins for every outcome: county-level sMAPE 16% (households) to 21%
(children). Individuals is the sum of the three age-group forecasts, as the 1 October brief
asks. August 2026 statewide households forecast 243,813 (August 2025 actual 237,148).
Intervals are the 10th and 90th percentiles of backtest residuals, roughly plus or minus
25%. Wilkin is left blank, not zero.

**Q8.** Within five straight-line miles of a food shelf: 98% of urban LILA population, 95%
of urban non-LILA, 55% of rural non-LILA, **37% of rural LILA**. In cities the network
reaches low-access areas as well as anywhere; in rural Minnesota it reaches them worse than
the rest. The network repeats the retail gap where the gap is biggest. 402 sites in the Q8
definition; limitations carry magnitudes (crosswalk: 23 of 1,505 tracts with multiple 2010
parents; within-tract displacement bound median 3.1 miles).

---

## Cross-question issues to settle this week

1. **Hennepin's reported households fell from about 87k (July 2025) to 63k (June 2026)
   and 69k (July 2026) with no matching fall in sites or SNAP.** Dhyan found it in Q5 and
   flagged it as a reporting problem. It matters most for Q7: the August 2026 Hennepin
   forecast (73k) is built on July 2026, so if the dip is late reporting the forecast of
   the largest county is biased low. Needs one decision: adjust, flag, or ask the
   organizers whether July is final. **Anoka has the same pattern** (August 2025 20,888
   households; July 2026 15,832, a quarter lower; forecast 17,636) and nobody has flagged
   it. Hennepin and Anoka are about 40% of the state's households. The audit this week
   lists every county whose last three months fell more than the state did against the
   same months a year earlier: dips clustered in the final months mean late reporting.
2. **Q4 and Q5 describe March 2023 differently.** Q4's follow-up: a 20% one-month jump in
   statewide totals. Q5: month fixed effects "rose smoothly, no step at March". Both are
   true of different objects (state totals vs. unit-level averages), but the deck can say
   only one thing about 2023. Proposed: Q5 claims what county exposure can explain
   (nothing); Q4 reports the jump as unexplained by prices or by exposure.
3. **One site definition, said once.** Q1 and Q6 count 462 food-shelf-like sites that ever
   reported; Q8 counts 402 (last 12 months, no "Agency or Tribal Nation"). Both are audited.
   Also: mobile outreach programs deliver 62% of Cook County's pounds and are not
   food-shelf-like by current type. Decide whether `AgencySubType = Mobile` joins the
   definition, before the deck, with Uddam.
4. **The through-line.** The plan's draft was *"visits measure demand; here is where need
   hides, and why."* The results support something sharper: *recorded activity follows
   population and little else; need, measured either way, does not move it; the counties
   where it is missing are far from a site and offline.* Settle the sentence Monday.
5. **Q7 organizer questions are still open**: scoring metric, Hennepin/Ramsey whole or
   split, Wilkin treatment, whether July 2026 is final, submission format and date. The
   forecasts are built on working assumptions for all five.

---

## Missing this week (6-12 October), by person

### Dhyan
| # | task | why it is first |
|---|---|---|
| 1 | `questions/q4_food_prices/analysis.py` and `q5_snap/analysis.py`: port the notebooks so every number on a Q4 or Q5 slide comes from a script | rule 6; both are skeletons today |
| 2 | Q4 and Q5 READMEs: status, the answers, caveats | both say "not started" |
| 3 | Merge `dhyan_branch` into `main` (4 behind, 7 ahead; the Q4 draft header is now fixed) | nothing of Q4 or Q5 is on main |
| 4 | Issue 2 above, with Uddam: one account of 2023 | the deck has one slide for it |

### Uddam
| # | task | why |
|---|---|---|
| 1 | Merge `uddam-branch` into `main` after deleting the stray `notebooks/q8_exploration-jvsc-...ipynb` | Q7 is not on main; 92 commits waiting |
| 2 | Q7: a decision on Hennepin and Anoka (issue 1), and send the five organizer questions if not sent | the largest counties' forecasts depend on it |
| 2b | Q7 intervals by county-size band: today every county gets the same ±39%, from one pooled error distribution, although small counties miss by more in the backtests | cheap, and the first thing a judge will ask about Lac qui Parle's interval |
| 3 | Deck at draft quality, end to end, from the six titles | the week-3 test is "a deck exists and can be read start to finish" |
| 4 | Decide the mobile-outreach question with Valentino (issue 3) | affects the 402 and the 462 |

### Valentino
| # | task | why |
|---|---|---|
| 1 | **Leakage audit of Q7**, as the person who did not build it: every input series ends at 2026-07, every backtest fold uses only earlier months, the `z12MoAverage_*` columns never enter | the one named penalty in the brief; the README requires a second person |
| 2 | Q1 and Q6 slides: two charts and one table each, plus the addendum slide | the material is in `outputs/`; this is choosing and writing |
| 3 | Check how many outreach sites statewide are mobile and how much activity they carry; bring the number to issue 3 | thirty minutes |
| 4 | Explain Q6 to a teammate without the notebook | everyone must be able to state the definition and the rejection criterion |

### All
- Monday: the through-line sentence (issue 4).
- **Findings freeze Friday 10 October.** After that, tightening only.
- Every slide number traces to a script. Q4 and Q5 are the only questions where that is
  not yet true.

---

## For the advisor on 5 October

What we would like a view on:

1. **Q7 method.** Five baselines, the pooled August/July ratio wins with sMAPE 16 to 21%.
   We have not fitted anything more complex. Is "ship the baseline and say so" the right
   call with 55 months of data, or is there one model worth the week?
2. **Hennepin's reporting dip** (issue 1): adjust the July base, flag it, or forecast from
   June? What would you do with a county that is a third of the state?
3. **Q6's definition and rejection criterion** (above). Is the survey-based rejection
   criterion the kind of falsifiability the graduate addendum is after?
4. **The 2023 story** (issue 2): one slide, two notebooks that describe it differently.
5. **The through-line** (issue 4).

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

### Five Q6 inputs added to the covariates panel (1 October)

`county_covariates.parquet` has five new columns; nothing already there changed. To get
them: `python questions/q8_lila_access/build_lila.py` once (it makes the Atlas extract the
LILA share is built from), then `python src/build_covariates.py`.

| column | source | why it is in Q6 |
|---|---|---|
| `pct_hh_housing_burden` | ACS B25070 + B25091 | rent is paid first; food is what is left |
| `pct_no_hs_diploma` | ACS B15003 | fewer ways out when trouble comes |
| `lila_share_1and10`, `lila_share_vehicle` | USDA Atlas via Q8 | no store within reach |
| `pct_debt_collections` | Urban Institute, Aug 2025 | financial strain that is not income |

All four sources are in the registry. None is an input to the Map the Meal Gap model.
Q6's definition of need, its inputs and the rejection and revision criteria are written
in `notebooks/q6_exploration.ipynb`, step 0, before any index exists.

### The organizers' glossary is in the repo (30 September)

`docs/GLOSSARY.md`, in full, with a table mapping each term to our columns. The root README
lists the six terms that change our wording. Three that touch open work:

- **Pounds is "a supply measure as much as a demand measure."** That is the organizers'
  own framing for Q4's "pounds grew less than the people counts" and Q1's site-count
  result. Quote it.
- **Latent demand vs unmet demand.** Q6 targets the first. Our data cannot see the second.
- **Visit = one trip.** `HouseholdsReg` counts a household once a month, so it is a floor.
  The brief's own label for the metric is "Visits [HouseholdsReg]", so the mapping is
  theirs; the floor caveat is ours.

### The site master now carries the shared food-shelf definition (30 September)

`sites.parquet` has seven new columns. Nothing already there changed, and every other
processed table is byte-for-byte the same as before. **Rerun `python src/clean_data.py`
after pulling** to get them.

| column | what it holds |
|---|---|
| `is_food_shelf_like` | true if the site's **current** type in the Organization master is a food shelf (Brick and Mortar, Food Shelf, Mobile, Tribal Program, Agency or Tribal Nation). Every site has it, reported or not |
| `agency_type_clean` | the master's type with the spelling variants collapsed, as in `site_month` |
| `ever_reported` | the site has at least one usable activity row |
| `first_yearmonth`, `last_yearmonth` | first and last month with activity, e.g. `202207`. A last month before `202607` means the site stopped reporting |
| `n_months_reported` | number of distinct months with activity |
| `share_months_food_shelf_like` | of its reported months, the share in which the activity file typed it as a food shelf |

Loader:

```python
qkit.sites(food_shelf_only=True, reporting_only=True)   # the 462 sites that are the network
qkit.sites(food_shelf_only=True)                        # 771, incl. 309 that never reported
```

The counts, out of 1,202 rows in the master:

| | never reported | reported |
|---|---|---|
| not food-shelf-like | 262 | 169 |
| food-shelf-like | 309 | **462** |

Three things to know:

- **This is the definition Q1, Q6 and Q8 share.** Q8's 723 sites and its 278 that never
  reported were counted from the master before the flag existed. Count from the 462.
- **56 sites changed type over time in the activity file.** For 52 of them the current
  type is "not a food shelf" although some earlier months were counted as one. The flag
  holds the current type; `share_months_food_shelf_like` keeps the history. County `_fs`
  totals in `county_month.parquet` still use the month-by-month type, which is why they
  did not change.
- **34 sites report activity but are not in the master.** They stay in `site_month` and
  cannot be placed on a map. Unchanged from before; the new step just logs them.

The full logic is `attach_site_activity()` in `src/clean_data.py`, and the three checks
it makes are in `data/processed/data_quality_log.csv`.

---

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

---

## Q6 — Valentino (2 October)

Done except slides: `questions/q6_divergence_measure/analysis.py` rebuilds every number,
`addendum.md` is filled in, the README carries the findings. The reasoning, with the
predictions written before each result, is `notebooks/q6_exploration.ipynb`.

**The definition:** a household is in need if, at any point in the past year, it worried
about running out of food, regardless of whether it sought help (the first item of the
USDA food-security survey). **The rejection criterion:** survey our highest-need
counties; if the worry is no more common there than elsewhere, we were wrong. Everyone
should be able to say both without notes.

**The index:** equal-weight mean of within-year z-scores of seven public inputs, none of
them demand or an MMG input (SNAP households, no vehicle, senior poverty, housing-cost
burden, no diploma, LILA share, debt in collections).

| finding | number |
|---|---|
| Wilkin, predicted before the index existed at about the 70th percentile of need | rank 26 of 87, the 71st percentile |
| the index against activity per 1,000 residents | Spearman 0.07 to 0.14, all three metrics: recorded demand does not rise with need |
| the index against MMG's rate | Spearman 0.77; five of the top ten differ |
| need outranks recorded activity most in | Nobles, Grant, Wilkin, Benton, Wadena, Chippewa, Todd |
| the reverse | Washington, Dodge, Cook, Houston |
| Mahnomen | first on need and above the Q1 line: a high-need county that is reached |
| stable top seven under every variant and in at least 71% of 500 random weightings | Mahnomen, Clearwater, Beltrami, Wadena, Ramsey, Pine, Nobles; places 8-10 rotate |
| what explains the divergence | households without internet (+0.41 per SD, p = 0.005) and distance to a site (+0.23, p = 0.025); rural absorbed by no-internet; 17% of the divergence explained, against 5% of Q1's residual with the same variables |
| no-internet is both | a driver of need (index higher where internet is scarce, p < 0.001) and a barrier (less activity for a given need, p = 0.049) |
| against MMG head to head | county size explains 85% of recorded activity; MMG adds 0.6 points, the index 0.4; the two residual rankings correlate 0.99. Activity follows population, whichever way need is measured |

Checks written in advance, none fired: index on poverty rate R² 0.60 (bar 0.9); first
principal component 41%. Three new ACS sources on 2 October (limited English, no
internet, non-citizens), registered; `build_covariates.py` loads them. Caveats: ranks counties, does not estimate a share; debt covers
only people with a credit file; 87 counties see only large effects.

**Q1 addition (2 October):** two direct tests of the border story next to Moran's I.
Join counts: red counties border blue ones no more than chance (10 vs 13.5 expected,
p = 0.88). Pooling counties with their neighbours tightens the residuals more than random
groups do, weakly (p = 0.07). The border pairs on the chart are examples, not evidence.

---

## Q4 — Dhyan (`dhyan_branch`, not merged)

Done in the notebook, header corrected to the one-month response. Not yet in `analysis.py`
or the README. The numbers below are from the follow-up notebook (28 September).

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

---

## Q8 — Uddam (on `main`; later commits on `uddam-branch`)

Done. `analysis.py` writes nine tables and two figures; the README carries the numbers,
the crosswalk rule and a limitations table with magnitudes. Headline: within five miles of
a site, 98% of urban LILA population, 37% of rural LILA population; rural LILA is reached
worse than rural non-LILA (55%). The network repeats the retail gap where it is biggest.
An interactive Leaflet map (`outputs/figures/08_q8_lila_site_presence_interactive.html`,
2.7 MB, needs internet) is for exploring and screenshots, not the deck.

## Q7 — Uddam (`uddam-branch`, not merged)

Done apart from the leakage audit and the organizer questions. Five baselines (seasonal
naive, August/July ratio, naive with drift, pooled ratio, per-site ratio) backtested on
August 2023 to 2025; the pooled August/July ratio is selected for every outcome
(`q7_method_selection.csv`). Forecasts, 80% empirical intervals and age-share sanity
flags are in `q7_forecasts.csv`. Open: Hennepin's July base (issue 1), whether Hennepin
and Ramsey are scored whole, Wilkin, the scoring metric, July completeness. The audit
is Valentino's this week.

## Q5 — Dhyan (`dhyan_branch`, not merged)

Done in the notebook: event study, 79 units, two exposure measures, metro split, no
exposure effect. Not yet in `analysis.py` or the README. Dhyan's Hennepin finding is
issue 1 above.


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
