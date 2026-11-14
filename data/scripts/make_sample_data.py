"""
Makes SAMPLE (fake) data so the web app can be built before the real NASA data
is ready. Every output is marked "sample": true. Never use these numbers in the
story, slides or submission.

    python data/scripts/make_sample_data.py
    python data/scripts/trend_scanner.py series data/processed/sample/series --sample
    python data/scripts/trend_scanner.py grid data/processed/sample/chlorophyll_yearly.nc --variable chlorophyll --sample
"""

from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "processed" / "sample"
rng = np.random.default_rng(42)
years = np.arange(2003, 2026)
t = years - years[0]

# Basin-average series: (base, trend per year, noise) for lake / west / east
recipes = {
    "chlorophyll": {"west": (8, 0.25, 1.5), "east": (3, 0.0, 0.6)},
    "lake_temperature": {"west": (22.5, 0.04, 0.4), "east": (21.0, 0.03, 0.4)},
    "precipitation": {"west": (2.4, 0.0, 0.25), "east": (2.6, 0.0, 0.25)},
}
(OUT / "series").mkdir(parents=True, exist_ok=True)
for var, regs in recipes.items():
    df = pd.DataFrame({"year": years})
    for reg, (base, slope, noise) in regs.items():
        df[reg] = base + slope * t + rng.normal(0, noise, len(t))
    df["lake"] = (df["west"] + df["east"]) / 2
    df[["year", "lake", "west", "east"]].round(3).to_csv(OUT / "series" / f"{var}.csv", index=False)

# Gridded chlorophyll cube over a rough Lake Erie outline (0.1 degree cells)
lats = np.round(np.arange(41.4, 42.95, 0.1), 2)
lons = np.round(np.arange(-83.5, -78.85, 0.1), 2)
a = np.array([-83.3, 41.65])  # southwest end of the lake's centre line
b = np.array([-79.0, 42.75])  # northeast end
cube = np.full((len(years), len(lats), len(lons)), np.nan)
for i, la in enumerate(lats):
    for j, lo in enumerate(lons):
        p = np.array([lo, la])
        u = np.clip(np.dot(p - a, b - a) / np.dot(b - a, b - a), 0, 1)
        if np.linalg.norm(p - (a + u * (b - a))) > 0.28:
            continue  # outside the rough lake shape
        west_weight = max(0.0, 1 - u * 2.2)  # strong trend in the west, fading east
        cube[:, i, j] = 3 + 6 * west_weight + 0.3 * west_weight * t + rng.normal(0, 1.0, len(t))

xr.Dataset({"chlorophyll": (("year", "lat", "lon"), cube)},
           coords={"year": years, "lat": lats, "lon": lons},
           attrs={"note": "SAMPLE DATA - not real measurements"}
           ).to_netcdf(OUT / "chlorophyll_yearly.nc")
print(f"sample data written to {OUT.relative_to(ROOT)}")
