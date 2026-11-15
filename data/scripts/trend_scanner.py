# AI-assisted: written with Claude (an AI assistant) and reviewed by team Lake Effect.
"""
LAKE EFFECT — MULTI-LAKE TREND SCANNER

Analyzes:
- Chlorophyll-a
- Lake surface temperature
- Precipitation (when processed data is available)

For all five Great Lakes:
- Whole lake
- Western region
- Eastern region

Statistical methods:
- Original Mann-Kendall test
- Sen's slope
- Significance threshold: p < 0.05

Outputs:
web/public/data/
web/public/data/lakes/<lake>/
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pymannkendall as mk


# ============================================================
# CONFIGURATION
# ============================================================

ALPHA = 0.05

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "web" / "public" / "data"

LAKES = {
    "lake_erie": "Lake Erie",
    "lake_ontario": "Lake Ontario",
    "lake_huron": "Lake Huron",
    "lake_michigan": "Lake Michigan",
    "lake_superior": "Lake Superior",
}

VARIABLES = {
    "chlorophyll": {
        "name": "Chlorophyll-a (algae)",
        "units": "mg/m³",
        "source": "NASA MODIS-Aqua",
    },
    "temperature": {
        "name": "Lake surface temperature",
        "units": "°C",
        "source": "NOAA GLSEA ACSPO",
    },
    "precipitation": {
        "name": "Precipitation",
        "units": "mm/day",
        "source": "NASA MERRA-2",
    },
}


# ============================================================
# STATISTICAL ANALYSIS
# ============================================================

def test_series(values):

    values = pd.to_numeric(
        pd.Series(values),
        errors="coerce"
    ).to_numpy(dtype=float)

    values = values[np.isfinite(values)]

    n = len(values)

    if n < 8:
        return {
            "direction": "insufficient data",
            "p_value": None,
            "significant": False,
            "slope_per_decade": None,
            "n_years": n,
        }

    result = mk.original_test(
        values,
        alpha=ALPHA
    )

    significant = bool(result.h)

    return {
        "direction": (
            result.trend
            if significant
            else "no significant trend"
        ),
        "observed_direction": (
            "increasing"
            if result.slope > 0
            else "decreasing"
            if result.slope < 0
            else "stable"
        ),
        "p_value": round(float(result.p), 8),
        "significant": significant,
        "slope_per_decade": round(
            float(result.slope) * 10,
            4
        ),
        "n_years": n,
    }


# ============================================================
# TIME SERIES SCANNER
# ============================================================

def scan_series(folder: Path, sample=False):

    results = []

    if not folder.exists():
        raise FileNotFoundError(
            f"Data folder does not exist: {folder}"
        )

    csv_files = sorted(folder.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in {folder}"
        )

    for csv in csv_files:

        var_id = csv.stem

        if var_id not in VARIABLES:
            print(f"Skipping unsupported file: {csv.name}")
            continue

        df = pd.read_csv(csv)

        if "year" not in df.columns:
            print(f"Skipping {csv.name}: missing year column")
            continue

        df["year"] = pd.to_numeric(
            df["year"],
            errors="coerce"
        )

        df = (
            df.dropna(subset=["year"])
            .sort_values("year")
            .reset_index(drop=True)
        )

        # Only analyze actual lake regions.
        regions = [
            column
            for column in ("lake", "west", "east")
            if column in df.columns
        ]

        if not regions:
            print(
                f"Skipping {csv.name}: "
                "no lake, west or east columns"
            )
            continue

        meta = VARIABLES[var_id]

        trends = {}

        for region in regions:

            trends[region] = test_series(
                df[region].tolist()
            )

        lake_trend = trends.get("lake")

        if lake_trend is None:
            lake_trend = next(iter(trends.values()))

        series = {}

        for region in regions:

            series[region] = [
                None if pd.isna(value)
                else round(float(value), 4)
                for value in df[region]
            ]

        results.append({
            "id": var_id,
            **meta,
            "years": df["year"].astype(int).tolist(),
            "series": series,
            "trend": trends,
            "_rank": (
                0 if lake_trend["significant"] else 1,
                lake_trend["p_value"]
                if lake_trend["p_value"] is not None
                else 1,
            ),
        })

    results.sort(key=lambda item: item["_rank"])

    for result in results:
        result.pop("_rank")

    return {
        "generated": datetime.now(
            timezone.utc
        ).isoformat(timespec="seconds"),
        "sample": sample,
        "alpha": ALPHA,
        "ranking": [
            result["id"]
            for result in results
        ],
        "variables": results,
    }


# ============================================================
# PIXEL-LEVEL TREND MAP
# ============================================================

def trend_grid(
    nc_path: Path,
    var_id: str,
    name: str,
    units: str,
    sample=False,
):

    import xarray as xr

    if not nc_path.exists():
        raise FileNotFoundError(
            f"NetCDF file not found: {nc_path}"
        )

    features = []

    with xr.open_dataset(nc_path) as ds:

        if var_id not in ds:
            raise ValueError(
                f"{var_id} not found in {nc_path}"
            )

        da = ds[var_id]

        if not {"lat", "lon", "year"}.issubset(
            da.dims
        ):
            raise ValueError(
                f"Unexpected dimensions: {da.dims}"
            )

        lats = da["lat"].values
        lons = da["lon"].values

        dlat = (
            abs(float(lats[1] - lats[0]))
            if len(lats) > 1 else 0.1
        )

        dlon = (
            abs(float(lons[1] - lons[0]))
            if len(lons) > 1 else 0.1
        )

        for i, lat in enumerate(lats):

            for j, lon in enumerate(lons):

                values = da.isel(
                    lat=i,
                    lon=j
                ).values

                trend = test_series(values)

                if trend["p_value"] is None:
                    continue

                latitude = float(lat)
                longitude = float(lon)

                features.append({
                    "type": "Feature",

                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [
                                longitude - dlon / 2,
                                latitude - dlat / 2
                            ],
                            [
                                longitude + dlon / 2,
                                latitude - dlat / 2
                            ],
                            [
                                longitude + dlon / 2,
                                latitude + dlat / 2
                            ],
                            [
                                longitude - dlon / 2,
                                latitude + dlat / 2
                            ],
                            [
                                longitude - dlon / 2,
                                latitude - dlat / 2
                            ],
                        ]]
                    },

                    "properties": {
                        "lat": round(latitude, 4),
                        "lon": round(longitude, 4),
                        **trend,
                    }
                })

    significant = sum(
        feature["properties"]["significant"]
        for feature in features
    )

    return {
        "type": "FeatureCollection",

        "properties": {
            "variable": var_id,
            "name": name,
            "units": units,
            "alpha": ALPHA,
            "sample": sample,
            "total_pixels": len(features),
            "significant_pixels": significant,
            "non_significant_pixels": (
                len(features) - significant
            ),
            "generated": datetime.now(
                timezone.utc
            ).isoformat(timespec="seconds"),
        },

        "features": features,
    }


# ============================================================
# JSON OUTPUT
# ============================================================

def clean_json(value):

    if isinstance(value, float) and math.isnan(value):
        return None

    raise TypeError(
        f"Cannot serialize {type(value)}"
    )


def write_json(data, path):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    path.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            allow_nan=False,
            default=clean_json,
            indent=2,
        )
    )

    print(f"Saved: {path.relative_to(ROOT)}")


# ============================================================
# MAIN
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description="Lake Effect Multi-Lake Trend Scanner"
    )

    parser.add_argument(
        "--lake",
        choices=list(LAKES.keys()),
        default="lake_erie",
        help="Select the Great Lake"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    series_parser = subparsers.add_parser(
        "series",
        help="Analyze yearly CSV data"
    )

    series_parser.add_argument(
        "folder",
        type=Path
    )

    series_parser.add_argument(
        "--sample",
        action="store_true"
    )

    grid_parser = subparsers.add_parser(
        "grid",
        help="Generate pixel-level trend maps"
    )

    grid_parser.add_argument(
        "nc",
        type=Path
    )

    grid_parser.add_argument(
        "--variable",
        required=True
    )

    grid_parser.add_argument(
        "--name",
        default=None
    )

    grid_parser.add_argument(
        "--units",
        default=""
    )

    grid_parser.add_argument(
        "--sample",
        action="store_true"
    )

    args = parser.parse_args()

    lake_name = LAKES[args.lake]

    output = (
        OUT_DIR
        if args.lake == "lake_erie"
        else OUT_DIR / "lakes" / args.lake
    )

    print("\n" + "=" * 55)
    print("LAKE EFFECT — TREND SCANNER")
    print("=" * 55)
    print("Lake:", lake_name)

    if args.command == "series":

        result = scan_series(
            args.folder,
            args.sample
        )

        result["region"] = lake_name

        write_json(
            result,
            output / "scanner.json"
        )

        print("\nVARIABLE SUMMARY")

        for variable in result["variables"]:

            print("\n", variable["name"])

            for region, trend in variable["trend"].items():

                print(
                    f"  {region}: "
                    f"{trend['direction']} | "
                    f"Slope: {trend['slope_per_decade']} | "
                    f"P-value: {trend['p_value']} | "
                    f"Significant: {trend['significant']}"
                )

    elif args.command == "grid":

        meta = VARIABLES.get(
            args.variable,
            {}
        )

        result = trend_grid(
            args.nc,
            args.variable,
            args.name or meta.get(
                "name",
                args.variable
            ),
            args.units or meta.get("units", ""),
            args.sample
        )

        write_json(
            result,
            output / f"trend_map_{args.variable}.geojson"
        )

        print(
            "Total pixels:",
            result["properties"]["total_pixels"]
        )

        print(
            "Significant pixels:",
            result["properties"]["significant_pixels"]
        )

        print(
            "Non-significant pixels:",
            result["properties"]["non_significant_pixels"]
        )


if __name__ == "__main__":
    main()
