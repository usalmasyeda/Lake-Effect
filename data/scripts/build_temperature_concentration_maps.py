"""Generate pixel-level NOAA lake surface temperature maps."""

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
        "nc": PROCESSED / "series/temperature_yearly.nc",
        "output": WEB_DATA / "temperature_concentration.geojson",
    },
    "lake_ontario": {
        "name": "Lake Ontario",
        "nc": PROCESSED / "lakes/lake_ontario/temperature_yearly.nc",
        "output": WEB_DATA / "lakes/lake_ontario/temperature_concentration.geojson",
    },
    "lake_huron": {
        "name": "Lake Huron",
        "nc": PROCESSED / "lakes/lake_huron/temperature_yearly.nc",
        "output": WEB_DATA / "lakes/lake_huron/temperature_concentration.geojson",
    },
    "lake_michigan": {
        "name": "Lake Michigan",
        "nc": PROCESSED / "lakes/lake_michigan/temperature_yearly.nc",
        "output": WEB_DATA / "lakes/lake_michigan/temperature_concentration.geojson",
    },
    "lake_superior": {
        "name": "Lake Superior",
        "nc": PROCESSED / "lakes/lake_superior/temperature_yearly.nc",
        "output": WEB_DATA / "lakes/lake_superior/temperature_concentration.geojson",
    },
}


def grid_spacing(values):
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

        da = ds["temperature"]

        years = da["year"].values.astype(int)

        if len(years) == 0:
            print("No annual observations found.")
            return

        year = int(years.max())

        annual = da.sel(year=year).load()

        lats = annual["lat"].values
        lons = annual["lon"].values
        values = annual.values

    dlat = grid_spacing(lats)
    dlon = grid_spacing(lons)

    valid = np.isfinite(values)

    valid_values = values[valid]

    if len(valid_values) == 0:
        print("No valid temperature pixels.")
        return

    minimum = float(valid_values.min())
    maximum = float(valid_values.max())

    percentiles = {
        f"p{p}": round(float(np.percentile(valid_values, p)), 3)
        for p in [10, 25, 50, 75, 90]
    }

    features = []

    for i, lat in enumerate(lats):
        for j, lon in enumerate(lons):

            temperature = values[i, j]

            if not np.isfinite(temperature):
                continue

            lat = float(lat)
            lon = float(lon)

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
                    "temperature": round(float(temperature), 3),
                },
            })

    geojson = {
        "type": "FeatureCollection",
        "properties": {
            "lake_id": lake_id,
            "lake": config["name"],
            "variable": "temperature",
            "name": "Lake surface temperature",
            "units": "°C",
            "year": year,
            "season": "July–October seasonal average",
            "pixels": len(features),
            "minimum": round(minimum, 3),
            "maximum": round(maximum, 3),
            "percentiles": percentiles,
            "color_scale": [
                {"min": 0, "max": 5, "label": "Very cool"},
                {"min": 5, "max": 10, "label": "Cool"},
                {"min": 10, "max": 15, "label": "Moderate"},
                {"min": 15, "max": 20, "label": "Warm"},
                {"min": 20, "max": 25, "label": "Very warm"},
                {"min": 25, "max": None, "label": "Extremely warm"},
            ],
        },
        "features": features,
    }

    output = config["output"]
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w") as f:
        json.dump(geojson, f, allow_nan=False)

    print("Observation year:", year)
    print("Valid temperature pixels:", len(features))
    print("Minimum:", round(minimum, 3), "°C")
    print("Maximum:", round(maximum, 3), "°C")
    print("Median:", percentiles["p50"], "°C")
    print("Saved:", output.relative_to(ROOT))


def main():

    print("LAKE EFFECT — TEMPERATURE CONCENTRATION MAPS")
    print("============================================")

    for lake_id, config in LAKES.items():
        build_map(lake_id, config)

    print("\nTemperature map generation complete.")


if __name__ == "__main__":
    main()

