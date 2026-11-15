# AI-assisted: written by Mehak with help from ChatGPT (an AI assistant) and reviewed by team Lake Effect.

"""Incrementally update Lake Erie annual chlorophyll data from NASA files."""

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
NETCDF = PROCESSED / "chlorophyll_yearly.nc"
CSV = PROCESSED / "series" / "chlorophyll.csv"
BOUNDARY = PROCESSED / "lake_erie_boundary.geojson"

MONTHS = {7, 8, 9, 10}
SPLIT_LONGITUDE = -82.5

PATTERN = re.compile(
    r"AQUA_MODIS\.(\d{4})(\d{2})\d{2}_(\d{4})(\d{2})\d{2}"
    r"\.L3m\.MO\.CHL\.chlor_a\.4km\.nc$"
)


def main():
    if not NETCDF.exists() or not CSV.exists():
        raise FileNotFoundError("Historical NetCDF or CSV is missing.")

    with xr.open_dataset(NETCDF) as ds:
        historical = ds.load()

    existing = set(map(int, historical.year.values))
    print("Existing years:", min(existing), "to", max(existing))

    files_by_year = {}

    for path in RAW.glob("*.nc"):
        match = PATTERN.fullmatch(path.name)
        if not match:
            continue

        year, month, end_year, end_month = map(int, match.groups())

        if year != end_year or month != end_month:
            continue
        if year < 2003 or year in existing or month not in MONTHS:
            continue

        files_by_year.setdefault(year, {})[month] = path

    geometry = gpd.read_file(BOUNDARY).geometry.iloc[0]
    new_grids = []

    for year, month_files in sorted(files_by_year.items()):
        if set(month_files) != MONTHS:
            print(f"Skipping {year}: incomplete July–October season")
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

        # Prevent combining incompatible satellite grids.
        if (
            not np.array_equal(annual.lat.values, historical.lat.values)
            or not np.array_equal(annual.lon.values, historical.lon.values)
        ):
            raise ValueError(f"{year}: grid coordinates differ from historical data")

        new_grids.append(annual.expand_dims(year=[year]))
        print(f"Processed new year: {year}")

    if not new_grids:
        print("No new complete season available. Historical data unchanged.")
        return

    combined = xr.concat(
        [historical["chlorophyll"], *new_grids], dim="year"
    ).sortby("year")

    rows = []
    for year in combined.year.values:
        annual = combined.sel(year=year)
        rows.append({
            "year": int(year),
            "lake": float(annual.mean(skipna=True)),
            "west": float(
                annual.where(annual.lon < SPLIT_LONGITUDE).mean(skipna=True)
            ),
            "east": float(
                annual.where(annual.lon >= SPLIT_LONGITUDE).mean(skipna=True)
            ),
        })

    # Prepare both outputs before replacing existing files.
    tmp_nc = NETCDF.with_name("chlorophyll_yearly.tmp.nc")
    tmp_csv = CSV.with_name("chlorophyll.tmp.csv")

    try:
        combined.to_dataset(name="chlorophyll").to_netcdf(tmp_nc)
        pd.DataFrame(
            rows, columns=["year", "lake", "west", "east"]
        ).to_csv(tmp_csv, index=False)

                # Save the master dataset first.
        tmp_nc.replace(NETCDF)

        # The CSV is derived from the master NetCDF.
        # If this step fails, it can be regenerated from the NetCDF.
        tmp_csv.replace(CSV)
    finally:
        tmp_nc.unlink(missing_ok=True)
        tmp_csv.unlink(missing_ok=True)

    print("Updated annual NetCDF and CSV successfully.")


if __name__ == "__main__":
    main()
