# Data

## Folders

- `raw/`: downloaded NASA and NOAA files. Ignored by Git because they're too large. Write down where each one came from below.
- `processed/series/`: one CSV per variable, columns `year,lake,west,east`, one row per year.
- `processed/*_yearly.nc`: NetCDF cubes with dims `(year, lat, lon)` for the trend map.
- `processed/sample/`: fake data from `make_sample_data.py`. For building only.

## Steps to reproduce (data lead: fill in as you go)


1. Chlorophyll-a:
   - Source: NASA Ocean Biology Distributed Active Archive Center (OB.DAAC), accessed through NASA Earthdata Search.
   - Product: Aqua MODIS Level-3 Global Mapped Chlorophyll (CHL), version 2022.0, monthly, 4 km resolution (`chlor_a`).
   - Historical download range: 2002–2026, June–October, subject to product availability. The official analysis targets 2003 onward and uses July–October.
   - Access: https://search.earthdata.nasa.gov/
   - NASA Earthdata Login is required for authenticated downloads.
   - Download script: `data/scripts/download_nasa_all_years.sh`
   - Run from the repository root: `bash data/scripts/download_nasa_all_years.sh`
   - Raw files are stored in `data/raw/` and excluded from Git.
   - The download script skips existing nonempty files. Downloaded NetCDF files must be validated before processing.
   - Processing script: `data/scripts/process_chlorophyll.py`
   - Processing uses the Lake Erie polygon stored at `data/processed/lake_erie_boundary.geojson` to mask pixels outside the lake.
   - Annual chlorophyll values are calculated from the July–October monthly observations.
   - Outputs: `data/processed/series/chlorophyll.csv` and `data/processed/chlorophyll_yearly.nc`.
   - Limitations: Satellite-derived chlorophyll-a is an estimate, not a direct measure of algal toxicity. Missing months or pixels may affect annual coverage.
2. Lake surface temperature:
   - Source: NOAA GLERL GLSEA lake-wide daily average surface temperatures (`glsea_avgtemps_3`), from the GLERL ERDDAP server.
   - Script: `python data/scripts/get_glsea_temperature.py --allow-expired-cert` (NOAA's HTTPS certificate was expired on Nov 14, 2026; the flag accepts it for that server only).
   - Lake Erie's July–October mean for each year, 2007–2025. One whole-lake value per year (no basin split for this product).
   - Output: `data/processed/series/lake_temperature.csv`
3. Precipitation (MERRA-2): not added (stretch goal).

4. Averaging:
   - Bloom season: July 1–October 31, following NOAA's typical Lake Erie bloom season.
   - Each year's seasonal chlorophyll-a average is calculated using July, August, September, and October.
   - Only years with all four monthly files are processed.
   - Lake boundary: Natural Earth 1:10m lakes dataset, using the Lake Erie polygon.
   - Western basin: Lake Erie pixels west of -82.5° longitude.
   - Central and eastern basins: Lake Erie pixels at or east of -82.5° longitude.
   - The -82.5° boundary is a provisional project convention pending source confirmation.
   - `lake` represents the whole-lake average, `west` the western region, and `east` the combined central and eastern region.
   - Chlorophyll-a concentrations are reported in mg/m³.
   - The processed annual CSV contains `year,lake,west,east`.
   - The annual NetCDF contains dimensions `(year, lat, lon)`.

   - Spatial trend quality filter: Only map features with at least 15 years of valid observations are included in the published GeoJSON.
   - The 15-year threshold is a project-specific quality rule.
   - The original trend map contained 1,600 features. Seven features with fewer than 15 years were excluded, leaving 1,593 features.
   - The published map contains 1,300 statistically significant increasing trends (Mann-Kendall p < 0.05).
   - Important: The current filter was applied after running the trend scanner. It must be incorporated into the processing workflow before future regeneration.


5. Run the scanner:

```bash
python data/scripts/trend_scanner.py series data/processed/series
python data/scripts/trend_scanner.py grid data/processed/chlorophyll_yearly.nc --variable chlorophyll
python data/scripts/filter_trend_map.py
```
