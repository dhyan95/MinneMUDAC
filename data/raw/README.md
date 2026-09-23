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
```

The four `tfg/` tables are the same data as the bundle, split out. The bundle is kept
because it carries the dictionary and context tabs.

Read [../../docs/DATA_ERRORS.md](../../docs/DATA_ERRORS.md) before trusting any column
here — including the ones the dictionary tells you to trust.
