# data/external/

Public data we download ourselves. Nothing here is committed to git without a reason,
and nothing here gets used without a row in the registry at the bottom of
[../../docs/DATA_SOURCES.md](../../docs/DATA_SOURCES.md).

```
census/saipe/      SAIPE county poverty and median income (est22all.xls ...)
census/acs/        ACS tables, named acs5_<endyear>_<table>.csv (renamed from the
                   data.census.gov export name; contents untouched)
census/gazetteer/  Gazetteer tracts, CenPop2020 tract centres of population
census/adjacency/  County Adjacency File 2023 (which counties border which)
urban/             Urban Institute, Debt in America 2025, county overall-debt file
bls/laus/          LAUS county unemployment, annual averages
bls/               CPI food-at-home series
mn_sdc/            MN State Demographic Center population and household estimates
usda/      Food Access Research Atlas, Rural-Urban Continuum Codes, FNS SNAP tables
osm/       OpenStreetMap geographic extracts, kept locally and filtered by analysis scripts
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
