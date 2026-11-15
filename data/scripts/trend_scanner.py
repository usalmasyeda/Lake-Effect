# AI-assisted: written with Claude (an AI assistant) and reviewed by team Lake Effect.
"""
Lake Effect Trend Scanner.

Takes yearly values for one or more Earth science variables over Lake Erie and
answers the four questions from the challenge:

    what is changing   -> every variable is tested and ranked
    where              -> per-pixel trend map (GeoJSON) for gridded data
    how much           -> Sen's slope, reported per decade
    is it significant  -> Mann-Kendall test, p < 0.05

Outputs land in web/public/data/ so the web app can read them directly.
See docs/data-format.md for the exact file shapes.

Usage
-----
    # Scan basin-average series (one CSV per variable, columns: year,lake,west,east)
    python data/scripts/trend_scanner.py series data/processed/series

    # Trend map for one gridded variable (NetCDF with dims year, lat, lon)
    python data/scripts/trend_scanner.py grid data/processed/chlorophyll_yearly.nc \
        --variable chlorophyll --name Chlorophyll-a --units "mg/m3"
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

ALPHA = 0.05  # significance threshold
REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "web" / "public" / "data"

# Metadata for the variables we scan. Add a row here to add a variable.
VARIABLES = {
    "chlorophyll": {"name": "Chlorophyll-a (algae)", "units": "mg/m³",
                    "source": "NASA MODIS-Aqua, Ocean Biology DAAC"},
    "lake_temperature": {"name": "Lake surface temperature", "units": "°C",
                         "source": "NOAA GLERL GLSEA"},
    "precipitation": {"name": "Precipitation (model)", "units": "mm/day",
                      "source": "NASA MERRA-2 (M2TMNXFLX)"},
}


def test_series(values: list[float]) -> dict:
    """Mann-Kendall + Sen's slope on one yearly series. NaNs are dropped."""
    x = np.asarray(values, dtype=float)
    x = x[~np.isnan(x)]
    if len(x) < 8:  # too short to say anything honest
        return {"direction": "insufficient data", "p_value": None,
                "significant": False, "slope_per_decade": None, "n_years": int(len(x))}
    r = mk.original_test(x, alpha=ALPHA)
    significant = bool(r.h)
    direction = r.trend if significant else "no significant trend"
    return {
        "direction": direction,                       # increasing / decreasing / no significant trend
        "p_value": round(float(r.p), 8),
        "significant": significant,
        "slope_per_decade": round(float(r.slope) * 10, 4),  # Sen's slope is per year
        "n_years": int(len(x)),
    }


def scan_series(folder: Path, sample: bool = False) -> dict:
    """Scan every <variable>.csv in folder and rank variables by strength of change."""
    results = []
    for csv in sorted(folder.glob("*.csv")):
        var_id = csv.stem
        df = pd.read_csv(csv).sort_values("year")
        regions = [c for c in df.columns if c != "year"]
        meta = VARIABLES.get(var_id, {"name": var_id, "units": "", "source": ""})
        trends = {reg: test_series(df[reg].tolist()) for reg in regions}
        lake = trends.get("lake") or next(iter(trends.values()))
        results.append({
            "id": var_id,
            **meta,
            "years": df["year"].astype(int).tolist(),
            "series": {reg: [None if pd.isna(v) else round(float(v), 4) for v in df[reg]]
                       for reg in regions},
            "trend": trends,
            # rank key: significant first, then smallest p-value
            "_rank": (0 if lake["significant"] else 1, lake["p_value"] if lake["p_value"] is not None else 1),
        })
    results.sort(key=lambda r: r["_rank"])
    for r in results:
        r.pop("_rank")
    return {
        "region": "Lake Erie",
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sample": sample,
        "alpha": ALPHA,
        "ranking": [r["id"] for r in results],
        "variables": results,
    }


def trend_grid(nc_path: Path, var_id: str, name: str, units: str, sample: bool = False) -> dict:
    """Per-pixel Mann-Kendall on a NetCDF cube (year, lat, lon) -> GeoJSON grid cells."""
    import xarray as xr

    ds = xr.open_dataset(nc_path)
    da = ds[var_id] if var_id in ds else ds[list(ds.data_vars)[0]]
    lats, lons = da["lat"].values, da["lon"].values
    dlat = float(abs(lats[1] - lats[0])) if len(lats) > 1 else 0.1
    dlon = float(abs(lons[1] - lons[0])) if len(lons) > 1 else 0.1
    features = []
    for i, lat in enumerate(lats):
        for j, lon in enumerate(lons):
            series = da.isel(lat=i, lon=j).values
            if np.all(np.isnan(series)):
                continue  # land or no data
            t = test_series(series.tolist())
            if t["p_value"] is None:
                continue
            la, lo = float(lat), float(lon)
            features.append({
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [[
                    [lo - dlon / 2, la - dlat / 2], [lo + dlon / 2, la - dlat / 2],
                    [lo + dlon / 2, la + dlat / 2], [lo - dlon / 2, la + dlat / 2],
                    [lo - dlon / 2, la - dlat / 2]]]},
                "properties": {"lat": round(la, 4), "lon": round(lo, 4), **t},
            })
    return {
        "type": "FeatureCollection",
        "properties": {"variable": var_id, "name": name, "units": units, "alpha": ALPHA,
                       "sample": sample,
                       "generated": datetime.now(timezone.utc).isoformat(timespec="seconds")},
        "features": features,
    }


def _write(obj: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, allow_nan=False, default=_clean))
    print(f"wrote {path.relative_to(REPO_ROOT)}")


def _clean(o):
    if isinstance(o, float) and math.isnan(o):
        return None
    raise TypeError(type(o))


def main() -> None:
    p = argparse.ArgumentParser(description="Lake Effect Trend Scanner")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("series", help="scan basin-average CSVs")
    s.add_argument("folder", type=Path)
    s.add_argument("--sample", action="store_true", help="mark output as sample data")
    g = sub.add_parser("grid", help="per-pixel trend map from a NetCDF cube")
    g.add_argument("nc", type=Path)
    g.add_argument("--variable", required=True)
    g.add_argument("--name", default=None)
    g.add_argument("--units", default="")
    g.add_argument("--sample", action="store_true")
    a = p.parse_args()

    if a.cmd == "series":
        _write(scan_series(a.folder, a.sample), OUT_DIR / "scanner.json")
    else:
        meta = VARIABLES.get(a.variable, {})
        _write(trend_grid(a.nc, a.variable, a.name or meta.get("name", a.variable),
                          a.units or meta.get("units", ""), a.sample),
               OUT_DIR / f"trend_map_{a.variable}.geojson")


if __name__ == "__main__":
    main()
