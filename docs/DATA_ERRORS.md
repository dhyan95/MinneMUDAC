# What is wrong with the data, and what we did about it

Every number below was produced by `python src/clean_data.py` against the files in
`data/raw/`. The machine-readable version of this list is
`data/processed/data_quality_log.csv`; the individual suspect rows are in
`outputs/tables/flagged_rows.csv`.

**The rule we follow: flag, never delete.** Every suspect row keeps its raw value and
gains a boolean column saying what is wrong with it. Aggregations then decide which
flags to exclude, and that decision is visible in code. A judge who asks "why is this
number what it is" gets an answer from the repo, not from memory.

---

## 1. The problem the data dictionary itself creates

### 1.1 The dictionary marks the populated columns as deprecated

`org_FSStats` has two families of metric columns:

| family | example | dictionary says | actually populated |
|---|---|---|---|
| `*Reg` (regular distributions) | `HouseholdsReg` | no usage note | 92.1% |
| `*Total` (all distribution types) | `HouseholdsTotal` | **Deprecated** | 92.1% |
| `*Extra`, `*Produce`, `*Holiday` | `HouseholdsExtra` | Deprecated | **0.0%** |

Read literally, the dictionary tells you to avoid `HouseholdsTotal` and use the
components — but the components are entirely empty, so `Total` has nowhere to come
from except `Reg`.

**We checked, and it does.** Wherever both columns are present, `*Reg` and `*Total` are
identical for all six metrics: 0 disagreements, maximum absolute difference 0. The two
families are the same data under two names.

**Decision:** read the `*Reg` columns, because they carry no deprecation warning, and
re-run the equality check on every pipeline run so we find out immediately if a future
extract breaks the equality. The check is logged as `Reg vs Total column families
disagree`.

### 1.2 There is no usable visits field

The brief names three metrics, and the first is **visits**. `org_FSStats` has
`UniqueVisitsReg` / `UniqueVisitsTotal`, and both are **99.9% empty** (0.1% populated).
There is no other field that counts trips.

**Decision:** use **households served** (`HouseholdsReg`) as the stand-in for visits,
and say so on every slide that uses it. A household served in a month is not a trip: a
household that visits four times in a month is counted once, so our "visits" number is
a floor, and any county where households visit more often is understated relative to
its true trip count.

The field is a parameter, not a hard-coded name — `M_VISITS` in [src/config.py](../src/config.py).
If the organizers tell us they mean something else, it is a one-line change and nothing
downstream breaks.

> **Ask the organizers.** This is question one on the list in [TEAM_PLAN.md](TEAM_PLAN.md).
> Q7 is *scored* on visits, so being wrong about which field that is costs us the
> prediction component.

---

## 2. Errors in `org_FSStats` (food shelf activity, 28,287 rows)

### 2.1 Month codes that are not months — 26 rows

25 rows are coded `202300` (month 0) and 1 row `202315` (month 15). These cannot be
placed on a calendar.

*Why it matters:* a naive `groupby(year)` silently folds them into 2023 totals; a
`groupby(yearmonth)` creates phantom periods.

*What we did:* flagged `bad_period = True` and excluded them from every time series.
They stay in `site_month.parquet` so we can ask The Food Group what they were meant to be.

### 2.2 Duplicate site-months — 87 rows across 43 site-months

The grain is supposed to be one row per site per month. 43 site-months have two or more
rows.

*Why it matters:* summing the raw table double counts them.

*What we did:* sorted by `zzModificationTS` and kept the most recently modified record.
The older rows are flagged `is_duplicate_superseded = True` rather than dropped. The
reasoning: where duplicates carry different numbers, a later edit is a correction, not a
second event.

### 2.3 Impossible values — 250 rows

| check | rows | example |
|---|---|---|
| negative counts or pounds | 5 | negative `PoundsReg` |
| individuals per household below 1 or above 8 | 243 | Waseca site, 2023-07: **273,385 households for 646 individuals** |
| households exactly equal to pounds (and > 1,000) | 2 | Ramsey-Suburbs site, 2025-03: households = pounds = 83,909 |

The Waseca row alone is larger than the entire statewide household total for that month.
The Ramsey row is a field pasted into the wrong column — households and pounds agreeing
to the unit at that magnitude is not a coincidence.

*What we did:* flagged `negative_value`, `implausible_ratio`, `households_equals_pounds`.
The thresholds (1 and 8 individuals per household) are in `config.py` and are deliberately
wide: Minnesota's average household is about 2.4 people, and the observed median here is
2.73, so 8 is generous rather than aggressive.

### 2.4 Values far above a site's own history — 290 rows

A value more than **5× the median of that same site** (for sites with at least 6 months
of history) is flagged `spike_flag = True`.

*Why compare against the site's own median:* an absolute cutoff would penalise a large
site for being large. A site-relative cutoff asks the right question, which is "is this
month unlike this site".

*Caveat we must state out loud:* a real surge — a new mobile distribution, a disaster
response — looks exactly like a keying error under this rule. That is why we flag rather
than delete, and why 570 flagged rows (2.0% of the table) are listed in
`outputs/tables/flagged_rows.csv` for a human to skim before the deck is frozen.

### 2.5 The correction: `*_adj` columns

Every metric exists twice in `site_month.parquet`:

- `households`, `pounds`, `individuals` — **the raw value, untouched**
- `households_adj`, `pounds_adj`, `individuals_adj` — raw where `is_clean`, the **site's own
  median** where it is not

County aggregates are built from the `_adj` columns, so one keying error cannot move a
county total. Any result can be re-run on the raw columns to show the correction did not
create the finding.

---

## 3. Geography: 91 labels for 87 counties

`org_FSStats.County` is free text and uses 91 distinct labels:

| problem | labels | rows |
|---|---|---|
| Hennepin split into city and suburbs | `Hennepin-Minneapolis`, `Hennepin-Suburbs`, `Hennepin` | 5,474 |
| Ramsey split into city and suburbs | `Ramsey-Saint Paul`, `Ramsey-Suburbs` | 2,421 |
| St. Louis spelled two ways | `St. Louis`, `Saint Louis` | 1,082 |
| no county at all | blank | 132 |

*Why it matters:* **nothing joins to anything until this is fixed.** Map the Meal Gap,
Census, USDA, BLS and DHS are all keyed on the 5-digit county FIPS code, and none of them
has ever heard of "Hennepin-Suburbs".

*What we did:* [src/geography.py](../src/geography.py) builds a crosswalk from label to
FIPS. The 87 canonical counties and their codes are **read out of the Map the Meal Gap
file rather than typed by hand**, so the list cannot drift. Sub-county labels are rolled
up to the whole county, and the original label is preserved in `county_split_label` in
case Q7 turns out to be scored on the split. Result: **87 matched, 4 rolled up, 1 missing**
— full coverage.

The call centre's `County` field is worse, because call takers type it live:
`Hennipen`, `hennHennepin`, `Sterns`, `Ramesy`, `rasmey`, `AAnoka`, `dakotaDakota`,
`rRoseau`, `FilmoreFillmore`, `h`, `USA`, `Cottonwood/Brown`. Unambiguous typos are
corrected by a lookup in `geography.py`; `Cottonwood/Brown` names two counties and is
deliberately left unmatched rather than guessed.

### 3.1 County means where the *site* is, not where the *client* lives

This is not a data error, it is a property of the data, and it limits every county-level
result in the project. A household that drives from Isanti to a larger shelf in Anoka is
counted in Anoka. Cross-county use inflates counties with regional shelves and deflates
their neighbours.

**Every county-level slide carries this as a stated limitation.** Better from us than
from a judge.

### 3.2 Wilkin County reports nothing, ever

Of Minnesota's 87 counties, **86 appear in the panel**. Wilkin County (FIPS 27167) has no
reporting food shelf in any of the 55 months.

*This is a finding, not a bug.* Feeding America estimates food-insecure people in Wilkin;
The Food Group observes zero activity there. Zero observed demand is not zero need — it is
Question 6 in its purest form, and it is a good candidate for the opening slide.

---

## 4. Errors in `Organization` (1,202 rows)

| issue | rows | what we did |
|---|---|---|
| `block_geoid` missing | 150 (12.5%) | flagged `has_geoid = False`; these sites cannot enter Q8 |
| `block_geoid` derived from a ZIP centroid | 12 | flagged `geoid_is_zip_centroid = True`; the block is real but it is the middle of the ZIP, **not the site**, so it must not be used for distance |
| geocoded county disagrees with the typed `County` | 37 | `block_geoid` wins, disagreement flagged `fips_disagrees` |
| `State` holds a ZIP code (`55313`, `55056`, `55318`) or a stray newline (`MN\n`) | 4 | flagged `state_dirty`; trust `block_geoid` and `County` instead |
| primary key is not always an integer | 13 orgs, 571 stat rows | see below |

### 4.1 The `.1` primary keys

13 organization IDs end in `.1` — `13462.1`, `14696.1`, `14711.1`. For **five** of them the
plain integer version also exists as a separate organization, so `14696` and `14696.1` are
two different sites.

*Why it matters:* `astype(int)` silently merges them and `astype(float)` invites
floating-point drift. Either way you lose or double-count a site.

*What we did:* the site key is carried as **text** everywhere in this project
(`to_site_id()` in `clean_data.py`).

### 4.2 The `z12MoAverage_*` columns are a leakage hazard

The eleven rolling-12-month-average columns on `Organization` were recomputed in
**August 2026**. Q7 requires us to predict August 2026, and the brief says using any
August data from any source **disqualifies the team**.

*What we did:* these columns are dropped in `build_sites()` and never reach
`data/processed/`. They are not "cleaned", they are removed, so nobody can reach for them
by accident.

### 4.3 The join key between the two tables

`Organization.__ID` = `org_FSStats._id_site`. (`_id_Agency` looks like it should be the
key — the dictionary says it links to "the agency-level identifier used in distribution
and statistics tables" — but it matches only **3.9%** of the sites in `org_FSStats`, so it
is not.) On the correct key, **94.9%** of reporting sites have an organization record and
**91%** have a `block_geoid`.

---

## 5. Errors in `Incoming Call` (49,727 rows)

| issue | share | what we did |
|---|---|---|
| no usable county | 34% | flagged; any geographic use must state this share up front |
| records before 2023 | 41 rows | flagged `sparse_period`; logging was not in routine use, so do not read a trend across the 2022/2023 boundary |
| SNAP Rx clinic referrals | 31% | flagged `is_snap_rx` |

**SNAP Rx deserves its own warning.** These are referrals *pushed* by enrolled healthcare
clinics, not calls *pulled* by households in need. Their volume tracks which clinics are
enrolled in the program, not local demand. Mixing them into a "call volume" series makes
the series measure The Food Group's partnership pipeline and then calls it food
insecurity. They must be separated before calls are used as a demand signal anywhere.

We also had to **define** what a food-related call is, since the brief does not. Our
definition is in `build_calls()` in `clean_data.py`, split into a narrow set
(`is_food_direct`: Food Shelf, Meal Program, Farmers market, SUN Bucks, Affordable
Groceries) and a SNAP set (`is_snap_related`). It is written down so it can be argued
with, and so the result can be re-run under a different definition in one edit.

---

## 6. Errors in `marketbucksUsage` (13,573 rows)

| issue | rows | what we did |
|---|---|---|
| redeemed exceeds distributed | 3,515 | flagged `redeemed_over_distributed`, **value kept** |
| site record carries no county | 753 | flagged, excluded from county results |
| late entries | 215 | flagged `is_late_entry` |

The first one looks like an error and is not: customers carry tokens between market
visits, so a session can redeem more than it distributed. It is flagged specifically so
that nobody "fixes" it later in the project. Netting these to zero would erase real
redemption.

---

## 7. Map the Meal Gap: two editions, one FIPS format

- `MMG2025_2019-2023_Data_To_Share_v2.xlsx` covers **2019–2023** (435 MN county-years).
- `MMG2026_2024_Data_To_Share.xlsx` covers **2024 only** (87 MN counties).
- The 2026 edition adds an `Imputed Market Basket Data` column and drops
  `Ratio (1 in X) Overall`.
- The 2025 edition's Read Me records a **methodology change** for local meal cost, food
  budget shortfall and meal gap. Read it before comparing 2023 to 2024.
- FIPS is an integer in these files and text in most public sources. We cast it to a
  **5-character zero-padded string** on load. Minnesota is `27xxx`, so the leading-zero bug
  stays invisible until someone adds Alabama (`01xxx`) — which is exactly the kind of bug
  that surfaces the night before a deadline.

The two editions are concatenated with a `source_edition` column. **Do not average them.**

---

## 8. The structural problem: the panel is unbalanced

Between **456 and 553** sites report in a given month. The median site reports all 55
months, but a quarter of sites report **33 months or fewer** — so the tail of the network
turns over constantly.

This means a county total moves with **who filed a report**, not only with demand. The
county panel therefore carries `n_sites_reporting` next to every metric, and any
month-over-month claim has to look at both columns.

The final month in the data (2026-07) has 489 reporting sites, **2.8% below** the trailing
12-month average. July is the base for the August forecast, so if it is still receiving
late entries the forecast is biased downward. This is question four on the organizer list.

A county-month with no row at all is a **reporting gap, not a zero**. We leave it absent
rather than filling with zero, because filling would invent a collapse in demand.

---

## Summary

| table | rows | rows flagged | headline problem |
|---|---|---|---|
| `org_FSStats` | 28,287 | 570 (2.0%) | no visits field; 91 county labels |
| `Organization` | 1,202 | 150 without geoid | 12.5% cannot be placed in a tract |
| `Incoming Call` | 49,727 | 16,977 without county | 34% ungeocodable, 31% clinic-pushed |
| `marketbucksUsage` | 13,573 | 753 without county | seasonal, narrow coverage |
| Map the Meal Gap | 522 MN county-years | — | two editions, methodology change |
