
"""Rebuild Lake Erie chlorophyll CSV from the master NetCDF."""

from pathlib import Path
import os
import tempfile

import pandas as pd
import xarray as xr

ROOT = Path(__file__).resolve().parents[2]
NETCDF = ROOT / "data/processed/chlorophyll_yearly.nc"
CSV = ROOT / "data/processed/series/chlorophyll.csv"

SPLIT_LONGITUDE = -82.5


def main():
    if not NETCDF.exists():
        raise FileNotFoundError(f"Missing master dataset: {NETCDF}")

    with xr.open_dataset(NETCDF) as ds:
        years = [int(y) for y in ds.year.values]

        if not years or len(years) != len(set(years)):
            raise ValueError("Missing or duplicate years in NetCDF")

        rows = []

        for year in sorted(years):
            annual = ds["chlorophyll"].sel(year=year)

            rows.append({
                "year": year,
                "lake": float(annual.mean(skipna=True)),
                "west": float(
                    annual.where(annual.lon < SPLIT_LONGITUDE)
                    .mean(skipna=True)
                ),
                "east": float(
                    annual.where(annual.lon >= SPLIT_LONGITUDE)
                    .mean(skipna=True)
                ),
            })

    CSV.parent.mkdir(parents=True, exist_ok=True)

    # Write a complete temporary CSV before replacing the existing file.
    fd, temp_path = tempfile.mkstemp(
        prefix="chlorophyll_",
        suffix=".tmp.csv",
        dir=CSV.parent,
    )

    try:
        with os.fdopen(fd, "w") as file:
            pd.DataFrame(
                rows, columns=["year", "lake", "west", "east"]
            ).to_csv(file, index=False)

        os.replace(temp_path, CSV)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    print(f"CSV rebuilt successfully: {len(rows)} years")
    print(f"Coverage: {min(years)}–{max(years)}")


if __name__ == "__main__":
    main()
