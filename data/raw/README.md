# data/raw/ — READ ONLY

**Nothing writes to this folder. Ever.** These are the files exactly as The Food Group
and Feeding America supplied them. If a file here changes, every result in the project
silently changes with it and we lose the ability to reproduce anything.

Only `src/clean_data.py` reads from here. Everything else reads `data/processed/`.

```
tfg/                       The Food Group operational data
  org_FSStats.xlsx           site x month activity          28,287 rows
  Organization.xlsx          organization master             1,202 rows
  IncomingCall.xlsx          SNAP helpline call log         49,727 rows
  marketbucksUsage.xlsx      farmers market sessions        13,573 rows
  MinneMUDAC1_full_bundle.xlsx   all four of the above in one workbook,
                                 as originally supplied, with the dictionary tabs

feeding_america/
  MMG2025_2019-2023_Data_To_Share_v2.xlsx   Map the Meal Gap, 2019-2023
  MMG2026_2024_Data_To_Share.xlsx           Map the Meal Gap, 2024 only

reference/
  TFG_MinneMUDAC_Challenge_Brief.pdf        the brief
  Data_Dictionary.xlsx                      field-level dictionary for all four TFG tables

mde/                       Minnesota Department of Education, sent by the organizers 1 Oct 2026
  SNP Claim Data Sites PY24.xlsx   school meals claimed per site per month, Sep 2023 - Jun 2024
  SNP Claim Data Sites PY25.xlsx   same, Sep 2024 - Jun 2025
  SNP Claim Data Sites PY26.xlsx   same, Sep 2025 - Jun 2026
```

The `mde/` files are pivot tables: one sheet each for lunch (state-funded), breakfast
(federal) and after-school snacks, rows are school sites, columns are claim months. They
count meals served, not eligibility, and Minnesota has served free meals to all students
since 2023-24, so they are a child **demand** series, not a need signal. No county column:
mapping site IDs to counties needs MDE's school directory. Nothing reads them yet. A fourth
file, `SnpClaimSummary PY27.xlsx`, held July 2026 only for 60 sites, with a September 2026
run date; it was deleted on 1 October as not worth the date-rule risk.

The four `tfg/` tables are the same data as the bundle, split out. The bundle is kept
because it carries the dictionary and context tabs.

Read [../../docs/DATA_ERRORS.md](../../docs/DATA_ERRORS.md) before trusting any column
here — including the ones the dictionary tells you to trust.
