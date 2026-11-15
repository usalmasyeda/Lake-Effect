
"""Generate pixel-level chlorophyll concentration maps for all five Great Lakes.

Uses the latest available annual July-October NASA MODIS-Aqua
chlorophyll-a grid for each lake.

Outputs GeoJSON files for the interactive web map.
"""

from pathlib import Path
import json

import numpy as np
import xarray as xr

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed"
WEB_DATA = ROOT / "web" / "public" / "data"

LAKES = {
    "lake_erie": {
        "name": "Lake Erie",
        "nc": PROCESSED / "chlorophyll_yearly.nc",
        "output": WEB_DATA / "chlorophyll_concentration.geojson",
    },
    "lake_ontario": {
        "name": "Lake Ontario",
        "nc": PROCESSED / "lakes/lake_ontario/chlorophyll_yearly.nc",
        "output": WEB_DATA / "lakes/lake_ontario/chlorophyll_concentration.geojson",
    },
    "lake_huron": {
        "name": "Lake Huron",
        "nc": PROCESSED / "lakes/lake_huron/chlorophyll_yearly.nc",
        "output": WEB_DATA / "lakes/lake_huron/chlorophyll_concentration.geojson",
    },
    "lake_michigan": {
        "name": "Lake Michigan",
        "nc": PROCESSED / "lakes/lake_michigan/chlorophyll_yearly.nc",
        "output": WEB_DATA / "lakes/lake_michigan/chlorophyll_concentration.geojson",
    },
    "lake_superior": {
        "name": "Lake Superior",
        "nc": PROCESSED / "lakes/lake_superior/chlorophyll_yearly.nc",
        "output": WEB_DATA / "lakes/lake_superior/chlorophyll_concentration.geojson",
    },
}


def grid_spacing(values):
    """Calculate grid-cell spacing from coordinate values."""
    if len(values) < 2:
        raise ValueError("Grid needs at least two coordinates.")

    return float(np.median(np.abs(np.diff(values))))


def build_map(lake_id, config):
    nc_path = config["nc"]

    if not nc_path.exists():
        print(f"Missing NetCDF file: {nc_path}")
        return

    print(f"\nProcessing {config['name']}")

    with xr.open_dataset(nc_path) as ds:
        da = ds["chlorophyll"]

        available_years = da["year"].values.astype(int)

        if len(available_years) == 0:
            print("No annual observations found.")
            return

        # Use the latest year available in the dataset.
        year = int(available_years.max())

        annual = da.sel(year=year).load()

        lats = annual["lat"].values
        lons = annual["lon"].values

        values = annual.values

    dlat = grid_spacing(lats)
    dlon = grid_spacing(lons)

    valid = np.isfinite(values) & (values > 0)

    valid_values = values[valid]

    if len(valid_values) == 0:
        print("No valid chlorophyll pixels.")
        return

    minimum = float(valid_values.min())
    maximum = float(valid_values.max())

    # Robust color-scale reference values.
    p10 = float(np.percentile(valid_values, 10))
    p50 = float(np.percentile(valid_values, 50))
    p90 = float(np.percentile(valid_values, 90))

    features = []

    for i, lat in enumerate(lats):
        for j, lon in enumerate(lons):

            concentration = values[i, j]

            if not np.isfinite(concentration) or concentration <= 0:
                continue

            lat = float(lat)
            lon = float(lon)

            # Build one polygon for each satellite pixel.
            coordinates = [[
                [lon - dlon / 2, lat - dlat / 2],
                [lon + dlon / 2, lat - dlat / 2],
                [lon + dlon / 2, lat + dlat / 2],
                [lon - dlon / 2, lat + dlat / 2],
                [lon - dlon / 2, lat - dlat / 2],
            ]]

            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": coordinates,
                },
                "properties": {
                    "lat": round(lat, 5),
                    "lon": round(lon, 5),
                    "concentration": round(float(concentration), 4),
                },
            })

    geojson = {
        "type": "FeatureCollection",
        "properties": {
            "lake_id": lake_id,
            "lake": config["name"],
            "variable": "chlorophyll",
            "name": "Chlorophyll-a concentration",
            "units": "mg/m³",
            "year": year,
            "season": "July–October average",
            "pixels": len(features),
            "minimum": round(minimum, 4),
            "maximum": round(maximum, 4),
            "percentiles": {
                "p10": round(p10, 4),
                "p50": round(p50, 4),
                "p90": round(p90, 4),
            },
        },
        "features": features,
    }

    output = config["output"]
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w") as f:
        json.dump(geojson, f, allow_nan=False)

    print("Observation year:", year)
    print("Valid satellite pixels:", len(features))
    print("Minimum concentration:", round(minimum, 4), "mg/m³")
    print("Maximum concentration:", round(maximum, 4), "mg/m³")
    print("Saved:", output.relative_to(ROOT))


def main():
    print("LAKE EFFECT — CHLOROPHYLL CONCENTRATION MAPS")
    print("============================================")

    for lake_id, config in LAKES.items():
        build_map(lake_id, config)

    print("\nConcentration map generation complete.")


if __name__ == "__main__":
    main()
