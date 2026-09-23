# data/external/

Public data we download ourselves. Nothing here is committed to git without a reason,
and nothing here gets used without a row in the registry at the bottom of
[../../docs/DATA_SOURCES.md](../../docs/DATA_SOURCES.md).

```
census/    SAIPE poverty, PEP population, ACS tables, 2020 Gazetteer, tract relationship files
bls/       CPI food-at-home series, LAUS county unemployment
usda/      Food Access Research Atlas, Rural-Urban Continuum Codes, FNS SNAP tables
mn_dhs/    Minnesota SNAP county caseloads
```

## Three rules

1. **Keep the file exactly as downloaded.** Do not open it in Excel and save it. That is
   how leading zeros die. All reshaping happens in a script.
2. **Truncate every monthly series at 2026-07 before saving.** Not at analysis time — at
   download time. The brief disqualifies a team for using August 2026 data from any
   source.
3. **Register it.** Publisher, exact series, geographic grain, time grain, vintage, who
   downloaded it, when, and why this source over an alternative. The brief requires the
   four facts; the other three are for us.
