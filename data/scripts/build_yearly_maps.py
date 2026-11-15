# AI-assisted: written with Claude (an AI assistant) and reviewed by team Lake Effect.
"""Build small per-year map files for the website's year slider.

For each lake and variable, writes web/public/data/[lakes/<lake>/]yearly_<variable>.json:

{
  "variable": "chlorophyll", "units": "mg/m³", "years": [2003, ..., 2025],
  "cell": [dlon, dlat],            # size of one square in degrees
  "pixels": [[lat, lon, [v2003, v2004, ...]], ...]   # null = no data that year
}

Values are the July–October average for each year, from the yearly NetCDF files the
processing scripts already made. Temperature (1.4 km) is thinned to about 4 km the same
way as compact_web_maps.py: one real pixel per 3 x 3 block, nearest the block centre,
never averaged.

Run from the repo root:  python data/scripts/build_yearly_maps.py
"""
import json
import math
from pathlib import Path

import numpy as np
import xarray as xr

P = Path("data/processed")
WEB = Path("web/public/data")
UNITS = {"chlorophyll": "mg/m³", "temperature": "°C"}
SOURCES = {
    "lake_erie": {"chlorophyll": P / "chlorophyll_yearly.nc", "temperature": P / "series/temperature_yearly.nc"},
    **{lake: {v: P / f"lakes/{lake}/{v}_yearly.nc" for v in UNITS}
       for lake in ["lake_ontario", "lake_huron", "lake_michigan", "lake_superior"]},
}
BLOCK = 3


def coord(ds, *names):
    for n in names:
        if n in ds.coords:
            return n
    raise KeyError(names)


def build(lake, var, path):
    ds = xr.open_dataset(path)
    la, lo = coord(ds, "lat", "latitude"), coord(ds, "lon", "longitude")
    da = ds[var].transpose("year", la, lo)
    years = [int(y) for y in ds["year"].values]
    lats, lons = ds[la].values.astype(float), ds[lo].values.astype(float)
    vals = da.values
    dlat, dlon = abs(float(np.median(np.diff(lats)))), abs(float(np.median(np.diff(lons))))
    has = np.isfinite(vals).any(axis=0)
    rows, cols = np.nonzero(has)
    picks = list(zip(rows, cols))
    cell = [dlon, dlat]
    if var == "temperature":
        blocks = {}
        for r, c in picks:
            key = (r // BLOCK, c // BLOCK)
            d = math.hypot(r - (key[0] * BLOCK + 1), c - (key[1] * BLOCK + 1))
            if key not in blocks or d < blocks[key][0]:
                blocks[key] = (d, r, c)
        picks = [(r, c) for _, r, c in blocks.values()]
        cell = [dlon * BLOCK, dlat * BLOCK]
    pixels = []
    for r, c in picks:
        series = [None if not np.isfinite(v) else round(float(v), 2) for v in vals[:, r, c]]
        pixels.append([round(float(lats[r]), 4), round(float(lons[c]), 4), series])
    out = {"lake": lake, "variable": var, "units": UNITS[var], "years": years,
           "season": "July–October average", "cell": [round(cell[0], 5), round(cell[1], 5)],
           "pixels": pixels}
    if var == "temperature":
        out["thinned_to_km"] = 4
    folder = WEB if lake == "lake_erie" else WEB / "lakes" / lake
    dest = folder / f"yearly_{var}.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
    print(f"{dest}: {len(pixels)} squares x {len(years)} years, {dest.stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    for lake, vars_ in SOURCES.items():
        for var, path in vars_.items():
            build(lake, var, path)
