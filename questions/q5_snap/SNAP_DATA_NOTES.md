# SNAP data notes — Minnesota county-monthly caseloads

Checked 27 September 2026. Read this after the Q5 README. The county-monthly series the
README asks for in step 1 exists, and it is in the repo.

## What is in the repo

| file | what it is |
|---|---|
| `data/external/mn_dhs/snap_dashboard_county_month_2016-01_2026-07.csv` | the download, cut at July 2026 |
| `src/build_snap.py` | reshapes it; run once from the repo root |
| `data/processed/snap_unit_month.parquet` | one row per reporting unit and month |
| `data/processed/snap_unit_crosswalk.csv` | which of our 87 counties is in which unit |

```python
import qkit
snap = qkit.snap()                        # 79 county units x 127 months
units = qkit.snap_units()                 # county -> unit, with the reason
activity = qkit.activity_by_snap_unit()   # food shelf activity on the same units
both = snap.merge(activity, on=["snap_unit", "yearmonth"], how="left")
```

`qkit.snap()` runs the leakage check every time it is called.

## The source

- 2016-01 to 2026-07, 127 months, none missing. No duplicate rows, no blank cells.
- One row per county or tribal nation per month.
- The download held 2026-08 as well. Those 87 rows were removed before the file entered
  the repo. Nothing else was changed. The original is kept outside the repo.
- **Publication lag: about one month.** The download on 27 September already held August.
  The page does not state an update schedule, so the lag is observed, not published.
- **Publisher:** Minnesota Department of Children, Youth, and Families, page "SNAP Food
  Assistance in Minnesota", https://dcyf.mn.gov/snap-food-assistance-minnesota. File
  downloaded: `snap-dashboard-data-through-august-2026.xlsx`.
- The same page offers `snap-dashboard-statewide-totals-through-august-2026.xlsx`. It is
  not in the repo. It would serve as the state-level cross-check the README asks for, and
  it must be cut at 2026-07 in the same way before it is saved.
- The page defines a case as "any group of people individually enrolled in food
  assistance, live together, and purchase and prepare food together". It does not define
  MFAP; the meaning given below is ours and should be confirmed.

### Columns

| column | meaning |
|---|---|
| `case_count`, `person_count` | households and people receiving food benefits that month |
| `snap_federal_food_issued` | federal SNAP dollars issued. **This is the SNAP benefit series.** |
| `mfap_state_food_issued` | Minnesota Food Assistance Program, state-funded |
| `snap_mfip_fed_food_issued`, `mfip_state_food_issued` | the food portion of family cash assistance (MFIP) |
| `..._cancelled`, `..._net` | cancelled benefits, and issued minus cancelled |
| `total_net` | the four net columns added together |

## Why "units" and not counties

The source does not report every county on its own. Eleven of our 87 counties are
affected.

| unit | counties | what the source does |
|---|---|---|
| MNPrairie | Dodge, Steele, Waseca | one row for the three; they never appear separately |
| Pope-Grant | Pope, Grant | Grant has no row after 2021-12. In 2022-01 Pope rises from 732 to 1,148 persons, which is Grant's 412 |
| Southwest | Lincoln, Lyon, Murray, Pipestone, Redwood, Rock | six rows, but cases move between them |

The evidence for Southwest: from December 2025 to July 2026 Redwood goes
613 → 1,012 → 695 and Lincoln 100 → 214 → 91, while the six together go 5,542 → 5,444.
The median month-to-month change is 0.7% for the total and up to 3.9% for a single
county. The typical Minnesota county is 1.3%.

Each unit is added up the same way in every month, so the series has one definition from
2016 to 2026. That leaves 79 county units: 76 single counties and 3 combined.

To change a grouping, edit `COMBINED` at the top of `src/build_snap.py` and run it again.

### Tribal nations

Red Lake Nation, White Earth Band and Mille Lacs Band are reported separately: 3,174,
2,211 and 82 persons in July 2026, about 2.7% of the state. Their members live in
counties whose own rows are therefore too low, mainly Beltrami and Clearwater (Red Lake)
and Mahnomen, Becker and Clearwater (White Earth). They are not added to any county.
`qkit.snap(counties_only=False)` returns them.

## What the data already shows

| | |
|---|---|
| Emergency allotments end | federal dollars per case: **$453 in March 2023, $267 in April 2023** |
| First month of lower benefits in Minnesota | **April 2023** |
| Size of the cut, per case | 47% at the median unit, from 37% to 54% |
| Persons on SNAP, share of population, March 2023 | 7.7% at the median unit, from 2.8% (Carver) to 14.7% (Cass) |

The last row is the exposure measure from step 4 of the README. It varies fivefold
across units, which is what the event study needs.

## Decisions for the Q5 owner

1. **Accept the three combined units, or split them.** Splitting needs another source,
   such as ACS SNAP households by county, and adds an assumption.
2. **Tribal nations:** leave them out and state it, or allocate them to counties.
3. **Which series is "SNAP benefits":** federal SNAP only, or federal SNAP plus the MFIP
   food portion.
4. **The event month is April 2023.** Q4's price effect sits in the same window, so the
   two questions need one agreed account of 2023.

## Limitations to state

- 11 of 87 counties cannot be analysed one by one.
- Steele and Pope are inside combined units. Steele has the most food shelf activity
  above what need predicts in Q1, and Pope is among the most below.
- Counties with tribal members have SNAP counts that are too low.
- A case is counted where it is administered, which is not always where the household
  lives.
