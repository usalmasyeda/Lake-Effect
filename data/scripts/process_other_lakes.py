
"""Process NASA MODIS-Aqua chlorophyll-a for four additional Great Lakes.

Calculates:
- Whole-lake annual chlorophyll averages
- Western-section annual averages
- Eastern-section annual averages
- Annual satellite pixel grids for concentration and trend maps

Western/eastern sections are analytical longitude-based divisions.
"""

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
BOUNDARIES = PROCESSED / "boundaries"
OUTPUT = PROCESSED / "lakes"

MONTHS = {7, 8, 9, 10}

LAKES = [
    "lake_ontario",
    "lake_huron",
    "lake_michigan",
    "lake_superior",
]

PATTERN = re.compile(
    r"AQUA_MODIS\.(\d{4})(\d{2})\d{2}_(\d{4})(\d{2})\d{2}"
    r"\.L3m\.MO\.CHL\.chlor_a\.4km\.nc$"
)


def find_complete_years():
    """Find years containing all four July–October monthly files."""
    files_by_year = {}

    for path in sorted(RAW.glob("*.nc")):
        match = PATTERN.fullmatch(path.name)

        if not match:
            continue

        year, month, end_year, end_month = map(int, match.groups())

        if year < 2003 or year != end_year:
            continue

        if month != end_month or month not in MONTHS:
            continue

        files_by_year.setdefault(year, {})[month] = path

    return {
        year: files
        for year, files in sorted(files_by_year.items())
        if set(files) == MONTHS
    }


def safe_mean(grid):
    """Return a numeric mean or NaN when no valid pixels exist."""
    values = grid.values
    valid = values[np.isfinite(values)]

    if len(valid) == 0:
        return np.nan

    return float(np.mean(valid))


def valid_pixel_count(grid):
    """Count valid chlorophyll pixels."""
    return int(np.isfinite(grid.values).sum())


def process_lake(lake, files_by_year):
    boundary_path = BOUNDARIES / f"{lake}.geojson"

    if not boundary_path.exists():
        print(f"Boundary missing: {boundary_path}")
        return

    geometry = gpd.read_file(boundary_path).geometry.iloc[0]

    min_lon, min_lat, max_lon, max_lat = geometry.bounds

    margin = 0.1

    # Divide the lake into analytical western/eastern sections.
    split_longitude = (min_lon + max_lon) / 2

    rows = []
    annual_grids = []

    print(f"\nProcessing {lake.replace('_', ' ').title()}")
    print(f"Western/eastern split: {split_longitude:.4f}° longitude")

    for year, month_files in files_by_year.items():

        monthly_grids = []

        for month in sorted(MONTHS):
            with xr.open_dataset(month_files[month]) as ds:

                grid = ds["chlor_a"].sel(
                    lat=slice(
                        max_lat + margin,
                        min_lat - margin
                    ),
                    lon=slice(
                        min_lon - margin,
                        max_lon + margin
                    )
                ).load()

                monthly_grids.append(grid)

        # Combine the four monthly observations.
        stack = xr.concat(
            monthly_grids,
            dim="month"
        ).assign_coords(
            month=sorted(MONTHS)
        )

        lons, lats = np.meshgrid(
            stack.lon.values,
            stack.lat.values
        )

        # Keep pixels whose centers fall inside the lake boundary.
        inside = contains_xy(
            geometry,
            lons,
            lats
        )

        mask = xr.DataArray(
            inside,
            dims=("lat", "lon"),
            coords={
                "lat": stack.lat,
                "lon": stack.lon
            }
        )

        # Remove land and invalid chlorophyll values.
        stack = stack.where(mask & np.isfinite(stack) & (stack > 0))

        # Calculate July–October annual average per pixel.
        annual = stack.mean(
            dim="month",
            skipna=True
        )

        annual.name = "chlorophyll"

        # Divide annual grid into three analytical regions.
        west = annual.where(
            annual.lon < split_longitude
        )

        east = annual.where(
            annual.lon >= split_longitude
        )

        # Calculate annual regional averages.
        lake_mean = safe_mean(annual)
        west_mean = safe_mean(west)
        east_mean = safe_mean(east)

        pixels = valid_pixel_count(annual)
        west_pixels = valid_pixel_count(west)
        east_pixels = valid_pixel_count(east)

        rows.append({
            "year": year,
            "lake": lake_mean,
            "west": west_mean,
            "east": east_mean,
            "valid_pixels": pixels
        })

        # Preserve full annual satellite pixel grid.
        annual_grids.append(
            annual.expand_dims(year=[year])
        )

        print(
            f"  {year}: "
            f"Lake={lake_mean:.3f}, "
            f"West={west_mean:.3f}, "
            f"East={east_mean:.3f}, "
            f"Pixels={pixels}"
        )

    if not rows:
        print("No complete years found.")
        return

    lake_output = OUTPUT / lake
    lake_output.mkdir(parents=True, exist_ok=True)

    # Save whole-lake and regional annual averages.
    df = pd.DataFrame(rows)

    df.to_csv(
        lake_output / "chlorophyll.csv",
        index=False
    )

    # Save complete annual pixel grids.
    cube = xr.concat(
        annual_grids,
        dim="year"
    )

    cube.to_dataset(
        name="chlorophyll"
    ).to_netcdf(
        lake_output / "chlorophyll_yearly.nc"
    )

    print(f"\nSaved: {lake_output / 'chlorophyll.csv'}")
    print(f"Saved: {lake_output / 'chlorophyll_yearly.nc'}")
    print(f"Years processed: {len(rows)}")


def main():
    files_by_year = find_complete_years()

    print(
        f"Found {len(files_by_year)} "
        "complete July–October years."
    )

    if not files_by_year:
        print("No complete historical years available.")
        return

    for lake in LAKES:
        process_lake(lake, files_by_year)

    print("\nAll four additional lakes processed.")


if __name__ == "__main__":
    main()
