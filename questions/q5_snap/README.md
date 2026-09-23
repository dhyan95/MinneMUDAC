# Q5 — SNAP enrollment and food shelf use

**Division:** undergraduate and graduate.
**Owner:** Dhyan
**Status:** not started

---

## The ask, in our words

SNAP gives a household money to buy food. A food shelf gives a household food directly.

1. Do the two **move together**, or does one **replace** the other?
2. When **SNAP benefits change**, what happens to food shelf activity?
3. Does the relationship **differ across locations**?

The stated purpose is advocacy: The Food Group wants to show lawmakers what SNAP does.
That means the deliverable is a defensible causal claim about benefit changes, not a
correlation between two caseload series.

---

## Data

| what | where | grain | note |
|---|---|---|---|
| activity | `data/processed/county_month.parquet` | county × month | |
| SNAP caseloads | **MN DHS** public assistance caseload statistics | county × **month** | **verify the exact report, URL and publication lag first** |
| benefit levels | USDA FNS SNAP COLA / maximum allotment schedules | national | annual, October adjustments — these are the *events* |
| state totals | USDA FNS SNAP participation & issuance | state × month | cross-check on DHS |
| eligibility context | `snap_threshold`, `pct_fi_below_snap_threshold` in `mmg_county.parquet` | county × year | free, already loaded |

The brief requires the **source, the grain, and the publication lag** stated explicitly
for the SNAP source. Put all three in
[DATA_SOURCES.md](../../docs/DATA_SOURCES.md) before you build on it.

Truncate every series at **2026-07**. See the leakage rule.

---

## Approach

1. **Find and validate the DHS county-monthly series.** This is the first task and it may
   take a day. Everything below depends on it. If county-monthly does not exist, fall
   back to state-monthly and say so — but look hard first.
2. **Describe before inferring.** Plot SNAP caseload and food shelf households for the
   same county over time. Do they rise together?
3. **Identification comes from benefit changes, not from levels.** Levels co-move because
   both respond to hardship, and that tells you nothing about substitution. Build an
   event study around dated benefit changes:
   - the end of pandemic **emergency allotments** in early 2023 (a large, dated, national
     cut — the cleanest event in the window),
   - the annual **October COLA** adjustments,
   - any other disruption in the window (**verify dates from a primary source before
     building around them**).
4. **Exposure, not just before/after.** Counties differ in how much of their population
   was on SNAP, so a national benefit cut is a bigger shock in some counties than others.
   Interact the event with pre-period SNAP intensity. That is what turns a time-series
   coincidence into evidence.
5. **Heterogeneity.** Metro against rural, high against low participation gap. The brief
   asks for it directly.

---

## What the preview already shows

The call centre is a SNAP helpline, and it is a second, independent read on SNAP
activity that we get for free:

- Call volume runs **731 to 1,684 calls a month** since 2023.
- **31% of all calls are SNAP Rx** — clinic-pushed referrals, not household-pulled
  demand. Their volume tracks which clinics are enrolled. **Separate them before using
  calls as any kind of demand signal.**
- **34% of calls carry no usable county**, so any geographic use must state that share.

Q2 (calls as a signal) is not scored for us, but the brief explicitly permits carrying
findings from an unscored question into a scored one. A SNAP-eligibility call spike that
precedes a caseload change is supporting evidence for Q5, and it costs us nothing.

---

## Traps

- **Co-movement is not substitution.** Both series rise in a recession. Only a benefit
  change separates the two hypotheses.
- **Publication lag.** DHS caseloads arrive one to two months late. Do not let a lagged
  series create a phantom lead-lag relationship.
- **Enrollment versus benefit level.** "SNAP enrollment" and "SNAP benefits" are
  different variables. The brief asks about both. Keep them separate in the writing.
- **Q4 and Q5 compete for the same variation.** A benefit cut and a price spike in the
  same quarter cannot both own the resulting demand jump. Agree with Q4 on who claims
  what, and say so in the deck rather than letting a judge find it.
- **Shared with Q4:** reporting composition. Carry `n_sites_reporting`.

---

## Deliverables

- [ ] `analysis.py` that rebuilds every number from `data/processed/` + `data/external/`
- [ ] SNAP source fully documented: publisher, series, grain, lag, why this one
- [ ] One chart: food shelf activity around a dated benefit change
- [ ] A stated direction and magnitude: "when benefits fell by X, activity rose by Y"
- [ ] Heterogeneity: which counties respond most, and what they have in common
- [ ] One sentence a lawmaker could repeat
