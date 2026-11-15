# AI-assisted: written by Mehak with help from ChatGPT (an AI assistant) and reviewed by team Lake Effect.

"""Process NASA MODIS-Aqua monthly chlorophyll-a for Lake Erie."""

from pathlib import Path
import re

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from shapely import contains_xy

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
BOUNDARY = PROCESSED / "lake_erie_boundary.geojson"

MONTHS = { 7, 8, 9, 10}
SPLIT_LONGITUDE = -82.5

pattern = re.compile(
    r"AQUA_MODIS\.(\d{4})(\d{2})\d{2}_(\d{4})(\d{2})\d{2}"
    r"\.L3m\.MO\.CHL\.chlor_a\.4km\.nc$"
)

def main():
    geometry = gpd.read_file(BOUNDARY).geometry.iloc[0]
    files_by_year = {}

    for path in sorted(RAW.glob("*.nc")):
        match = pattern.fullmatch(path.name)
        if not match:
            continue
        year, month, end_year, end_month = map(int, match.groups())
        if year != end_year or month != end_month or month not in MONTHS:
            continue
        files_by_year.setdefault(year, {})[month] = path

    if not files_by_year:
        print("No matching June-October monthly 4 km files found.")
        return

    rows = []
    annual_grids = []


    for year, month_files in sorted(files_by_year.items()):
        if year < 2003 :
            continue

        print(f"\n{year}: found months {sorted(month_files)}")
        if set(month_files) != MONTHS:
            print("  Incomplete bloom season; skipping annual output.")
            continue

        monthly_grids = []

        for month in sorted(MONTHS):
            with xr.open_dataset(month_files[month]) as ds:
                grid = ds["chlor_a"].sel(
                    lat=slice(43.2, 41.3),
                    lon=slice(-83.6, -78.7)
                ).load()
                monthly_grids.append(grid)

        stack = xr.concat(monthly_grids, dim="month")
        stack = stack.assign_coords(month=sorted(MONTHS))

        lons, lats = np.meshgrid(stack.lon.values, stack.lat.values)
        inside = contains_xy(geometry, lons, lats)
        mask = xr.DataArray(
            inside,
            dims=("lat", "lon"),
            coords={"lat": stack.lat, "lon": stack.lon}
        )

        stack = stack.where(mask & (stack > 0))
        annual = stack.mean(dim="month", skipna=True)
        annual.name = "chlorophyll"

        west = annual.where(annual.lon < SPLIT_LONGITUDE)
        east = annual.where(annual.lon >= SPLIT_LONGITUDE)

        row = {
            "year": year,
            "lake": float(annual.mean(skipna=True)),
            "west": float(west.mean(skipna=True)),
            "east": float(east.mean(skipna=True)),
        }
        rows.append(row)
        annual_grids.append(annual.expand_dims(year=[year]))
        print("  Annual averages:", row)

    if not rows:
        print("\nNo complete June-October year yet.")
        print("Annual CSV and NetCDF were not created.")
        return

    series_dir = PROCESSED / "series"
    series_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=["year", "lake", "west", "east"]).to_csv(
        series_dir / "chlorophyll.csv", index=False
    )

    cube = xr.concat(annual_grids, dim="year")
    cube.to_dataset(name="chlorophyll").to_netcdf(
        PROCESSED / "chlorophyll_yearly.nc"
    )

    print("\nSaved annual chlorophyll CSV and NetCDF.")

if __name__ == "__main__":
    main()
