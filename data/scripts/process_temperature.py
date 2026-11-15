# AI-assisted: written by Mehak with help from ChatGPT (an AI assistant) and reviewed by team Lake Effect.

"""
LAKE EFFECT — NOAA GLSEA Surface Temperature Processor

Processes daily NOAA GLSEA ACSPO satellite-derived surface
temperature for all five Great Lakes.

Output:
    temperature.csv
    temperature_yearly.nc

Season:
    July–October

Years:
    2007–2025

Minimum valid daily observations per pixel:
    10
"""

from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr

from shapely import contains_xy


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]

BOUNDARIES = ROOT / "data" / "processed" / "boundaries"
OUTPUT = ROOT / "data" / "processed"

NOAA_URL = (
    "https://apps.glerl.noaa.gov/erddap/griddap/"
    "GLSEA_ACSPO_GCS"
)

YEARS = range(2007, 2026)

MONTHS = {7, 8, 9, 10}

MIN_OBSERVATIONS = 10

MARGIN = 0.05

LAKES = [
    "lake_erie",
    "lake_ontario",
    "lake_huron",
    "lake_michigan",
    "lake_superior",
]


# --------------------------------------------------
# OUTPUT FOLDER
# --------------------------------------------------

def output_folder(lake):

    if lake == "lake_erie":
        return OUTPUT / "series"

    return OUTPUT / "lakes" / lake


# --------------------------------------------------
# PROCESS ONE LAKE
# --------------------------------------------------

def process_lake(remote, lake):

    print("\n" + "=" * 55)
    print(f"PROCESSING {lake.replace('_', ' ').upper()}")
    print("=" * 55)

    boundary_path = BOUNDARIES / f"{lake}.geojson"

    if not boundary_path.exists():
        print(f"Missing boundary: {boundary_path}")
        return

    boundaries = gpd.read_file(boundary_path)

    if boundaries.crs is not None:
        boundaries = boundaries.to_crs("EPSG:4326")

    geometry = boundaries.geometry.iloc[0]

    min_lon, min_lat, max_lon, max_lat = geometry.bounds

    # Use the lake's geographic centroid to define
    # consistent western and eastern sections.
    split_longitude = geometry.centroid.x

    print(
        f"Western/eastern split: "
        f"{split_longitude:.4f}° longitude"
    )

    # Extract only the lake's geographic bounding box.
    # This allows NOAA to serve a smaller spatial subset.
    lake_data = remote.sel(
        latitude=slice(
            min_lat - MARGIN,
            max_lat + MARGIN
        ),
        longitude=slice(
            min_lon - MARGIN,
            max_lon + MARGIN
        )
    )

    lons, lats = np.meshgrid(
        lake_data.longitude.values,
        lake_data.latitude.values
    )

    # Keep only pixels inside the actual lake boundary.
    inside = contains_xy(geometry, lons, lats)

    mask = xr.DataArray(
        inside,
        dims=("latitude", "longitude"),
        coords={
            "latitude": lake_data.latitude,
            "longitude": lake_data.longitude
        }
    )

    rows = []
    annual_grids = []

    # --------------------------------------------------
    # PROCESS EACH YEAR
    # --------------------------------------------------

    for year in YEARS:

        print(f"\n{year}:")

        # Fetch only July–October for this year.
        daily = lake_data.sel(
            time=slice(
                f"{year}-07-01",
                f"{year}-10-31"
            )
        ).load()

        if daily.sizes.get("time", 0) == 0:
            print("  No observations. Skipping.")
            continue

        # Apply quality filters and lake boundary.
        valid = daily.where(
            np.isfinite(daily)
            & (daily >= -2)
            & (daily <= 40)
            & mask
        )

        # Count valid daily measurements per pixel.
        observation_count = valid.count(dim="time")

        # Seasonal mean at every pixel.
        annual = valid.mean(
            dim="time",
            skipna=True
        )

        # Exclude pixels with insufficient observations.
        annual = annual.where(
            observation_count >= MIN_OBSERVATIONS
        )

        annual.name = "temperature"

        # Whole-lake mean.
        lake_mean = float(
            annual.mean(skipna=True).values
        )

        # Western and eastern sections.
        west = annual.where(
            annual.longitude < split_longitude
        )

        east = annual.where(
            annual.longitude >= split_longitude
        )

        west_mean = float(
            west.mean(skipna=True).values
        )

        east_mean = float(
            east.mean(skipna=True).values
        )

        valid_pixels = int(
            np.isfinite(annual.values).sum()
        )

        valid_days = int(
            daily.sizes["time"]
        )

        rows.append({
            "year": year,
            "lake": lake_mean,
            "west": west_mean,
            "east": east_mean,
            "valid_pixels": valid_pixels,
            "available_days": valid_days
        })

        # Rename dimensions to match Trend Scanner.
        annual = annual.rename({
            "latitude": "lat",
            "longitude": "lon"
        })

        annual_grids.append(
            annual.expand_dims(year=[year])
        )

        print(f"  Seasonal mean: {lake_mean:.2f} °C")
        print(f"  Western mean:  {west_mean:.2f} °C")
        print(f"  Eastern mean:  {east_mean:.2f} °C")
        print(f"  Valid pixels:  {valid_pixels}")
        print(f"  Daily observations: {valid_days}")

        

    # --------------------------------------------------
    # SAVE OUTPUTS
    # --------------------------------------------------

    if not rows:
        print("\nNo usable temperature observations.")
        return

    folder = output_folder(lake)
    folder.mkdir(parents=True, exist_ok=True)

    # Save yearly regional averages.
    csv_path = folder / "temperature.csv"

    pd.DataFrame(rows).to_csv(
        csv_path,
        index=False
    )

    print(f"\nSaved CSV: {csv_path}")

    # Save annual pixel-level temperature cube.
    cube = xr.concat(
        annual_grids,
        dim="year"
    )

    nc_path = folder / "temperature_yearly.nc"

    cube.to_dataset(
        name="temperature"
    ).to_netcdf(
        nc_path,
        encoding={
            "temperature": {
                "zlib": True,
                "complevel": 4
            }
        }
    )

    print(f"Saved NetCDF: {nc_path}")

    print(f"Years processed: {len(rows)}")
    print(
        f"Year range: "
        f"{rows[0]['year']}–{rows[-1]['year']}"
    )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    print("\nLAKE EFFECT — NOAA TEMPERATURE PROCESSING")
    print("=" * 55)

    print("Source: NOAA GLSEA ACSPO")
    print("Variable: sst")
    print("Units: °C")
    print("Season: July–October")
    print("Years: 2007–2025")

    print("\nConnecting to NOAA...")

    remote_ds = xr.open_dataset(
        NOAA_URL,
        engine="netcdf4"
    )

    try:

        if "sst" not in remote_ds:
            raise ValueError(
                "NOAA dataset does not contain the sst variable."
            )

        print("NOAA connection successful.")

        remote = remote_ds["sst"]

        print(
            "Available observations:",
            remote.sizes["time"]
        )

        for lake in LAKES:
            process_lake(remote, lake)

        print("\n" + "=" * 55)
        print("TEMPERATURE PROCESSING COMPLETE")
        print("=" * 55)

    finally:
        remote_ds.close()


if __name__ == "__main__":
    main()
