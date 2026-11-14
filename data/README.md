# Data

## Folders

- `raw/`: downloaded NASA and NOAA files. Ignored by Git because they're too large. Write down where each one came from below.
- `processed/series/`: one CSV per variable, columns `year,lake,west,east`, one row per year.
- `processed/*_yearly.nc`: NetCDF cubes with dims `(year, lat, lon)` for the trend map.
- `processed/sample/`: fake data from `make_sample_data.py`. For building only.

## Steps to reproduce (data lead: fill in as you go)

1. Chlorophyll-a: _source, product name, date range, how downloaded_
2. Lake surface temperature: _..._
3. Precipitation (MERRA-2): _..._
4. Averaging: _bloom season months used, basin split longitude_
5. Run the scanner:

```bash
python data/scripts/trend_scanner.py series data/processed/series
python data/scripts/trend_scanner.py grid data/processed/chlorophyll_yearly.nc --variable chlorophyll
```
