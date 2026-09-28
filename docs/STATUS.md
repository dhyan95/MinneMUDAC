# Status — end of week 1, plan for week 2

Written 27 September 2026 for the team meeting. Checked against `main` at `1a52fdf`,
`uddam-branch` at `54043ed` and `dhyan_branch` at `634abcc`.

---

## Where we are

| question | owner | state | lives in |
|---|---|---|---|
| Q1 need vs activity | Valentino | sub-questions 1–3 answered, 4 fitted and not yet interpreted | `notebooks/q1_exploration.ipynb` |
| Q4 food prices | Dhyan | full exploratory draft with a headline | `notebooks/q4_exploration.ipynb` on `dhyan_branch` |
| Q5 SNAP | Dhyan | not started; source not found yet | |
| Q6 divergence measure | Valentino | not started (week 2 item) | |
| Q7 forecast | Dhyan, Uddam | not started | |
| Q8 LILA access | Uddam | crosswalk built, coverage and retail comparison drafted | `notebooks/q8_exploration.ipynb` on `uddam-branch` |

No question has its numbers in `analysis.py` yet. Everything is in notebooks.

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
| Dhyan | Find the MN DHS county-monthly SNAP series | **not in any branch — ask at the meeting** |
| all | Re-run pipeline, confirm same numbers | Uddam's re-run matches to 14 decimal places |
| all | Organizer email sent | not visible in the repo |
| all | Section-2 decisions agreed and recorded | not visible in the repo |

**End-of-week-1 test** (every source on disk, truncated, registered): passes for
everything except the SNAP series. The plan calls that the highest-risk unknown in the
project. If it does not exist, Q5 needs a different design.

### Two things to settle at the meeting

1. **The weekdays in `TEAM_PLAN.md` are one day off.** The deadline is **Saturday
   17 October 2026**; the plan calls it a Friday. Week 4 as written (cross-briefing
   Monday 13, leakage audit Tuesday 14, deck frozen Wednesday 15, rehearsals Thursday 16)
   needs its weekday labels corrected, and the findings freeze at the end of week 3 needs
   a date: Friday 9 October or Monday 12 October.
2. **Merge order.** Both branches are up to date with `main` and touch different files,
   so they merge cleanly in any order.

---

## Announcement: the config alias is now `cfg`

`import config as C` is now `import config as cfg` in every `.py` file on `main`, the Q1
notebook, and two markdown files. 133 uses in 14 files.

- **Why:** `C(...)` is also the statsmodels formula shortcut for a categorical variable.
  With `C` taken by the config module, any formula using it fails.
- **Checked:** every file compiles and imports, Q1 `analysis.py` and the Q1 notebook run,
  and no output file changed.
- **Not changed:** `questions/q8_lila_access/map.py` (deleted on `uddam-branch`) and the
  two notebooks on the open branches. Those keep working as they are, because the alias
  is local to each file. Their owners can switch when convenient.

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

### For the whole team

`TEAM_PLAN.md` names the Spearman of −0.26 to −0.29 as the "strongest single fact". That
is the number with the built-in tilt. The opening line of the deck should be rewritten
around the log-log slope once it is reported.

---

## Q4 — Dhyan (`dhyan_branch`, not merged)

A careful, well-documented draft. Every step states its question, what was done, the
finding and the warning, and one invalid step is marked as such instead of deleted.

**Headline in the notebook:** demand rises 4–6 months after prices rise. Seasonality is
separate: October peak, January or February trough, a swing of about 20%.

### To discuss

1. **The headline is stronger than the notebook's own body.** The evidence is 42 months
   and one price episode. Food inflation fell from 12% to 1% during 2023 and has stayed
   between 0.4% and 2.7% since. Activity growth fell over the same stretch. Two series
   with one shared step will correlate at whatever lag lines the steps up. The notebook
   says this itself ("treat as exploratory drift"); the summary at the top does not.
2. **The size of the effect points to something else moving.** A coefficient of 4.7
   means one point of food inflation goes with 4.7 points of activity growth. The end of
   the pandemic SNAP emergency allotments falls in the same window and is Q5's event.
   The plan already says Q4 and Q5 must agree on which one claims the 2023 variation.
3. **The standard errors are still too small.** Year-over-year changes overlap for
   11 months, so the residuals stay correlated far beyond the 3-month HAC window.
   A window of 12 is the defensible choice.
4. **Step 2 is wrong as stated.** It finds the base and `_fs` columns identical and
   concludes either can be used. They are identical only because
   `county_month(food_shelf_only=True)` overwrites the base columns with the `_fs` ones.
   Without the flag they differ by about 7% of pounds. No result changes.
5. **The county cost comparison uses households per food-insecure person**, which is the
   measure with Q1's caveat 1. Higher-cost counties are also the metro counties, so the
   gap may be county size.
6. **February 2022 is unexplained**: 157,600 households against 115,500 in January, with
   the site count flat. This is a panel question, so it goes to Valentino.

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
7. The xlsx is still tracked, so the `.gitignore` line has no effect. Untracking it
   deletes it from everyone's working copy on their next pull; agree on that first.
8. Registry typo: "Minneosta".

---

## Week 2 (29 September – 5 October)

**Goal from the plan: one rough chart and one sentence per question.** Anything with no
number by the end of the week is what gets descoped, decided as a team.

### Valentino

| # | task | note |
|---|---|---|
| 1 | Interpret the sub-question 4 output | which signs match the hypotheses; what R² = 0.03 means; whether the three metrics agree |
| 2 | Report the log-log fit as the Q1 headline | slope, interval and R² per metric and year; it forms no ratio |
| 3 | Moran's I on the residuals | needs the Census county adjacency file and a registry row; write the predicted sign first |
| 4 | Port Q1 into `analysis.py` | it stops at Step 3 today |
| 5 | Update the Q1 README | status line and deliverables |
| 6 | **Q6: design the need index** | write the falsifiable definition before any result exists |
| 7 | Panel: add `is_food_shelf_like` and last active month to `sites.parquet` | gives Q8 the shared site definition |
| 8 | Panel: look into February 2022 | for Q4 |
| 9 | Record the panel v1 sign-off | |

### Dhyan

| # | task | note |
|---|---|---|
| 1 | **Q7 baselines backtested on August 2023, 2024 and 2025** | the plan's most important week 2 deliverable |
| 2 | Say whether the SNAP series exists | decides the Q5 design |
| 3 | Q5: design the event study around verified benefit-change dates | |
| 4 | Q4: settle the headline wording and widen the HAC window | items 1–3 above |
| 5 | Q4: agree with Q5 on who claims 2023 | |
| 6 | Fill in the CPI registry date, merge the branch | |
| 7 | Move the Q4 numbers into `analysis.py` | |

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

- Correct the weekday labels in `TEAM_PLAN.md` and fix the date of the findings freeze.
- Send the organizer email if it has not gone out.
- Record the Section-2 decisions in our own words.
