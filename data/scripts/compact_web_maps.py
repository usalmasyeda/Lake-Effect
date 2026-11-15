# AI-assisted: written with Claude (an AI assistant) and reviewed by team Lake Effect.
"""Make the website's map files small enough to load quickly.

1. Keeps only the properties the website reads, rounds coordinates to 4 decimals
   (about 10 m) and writes compact JSON.
2. Temperature maps (NOAA GLSEA, about 1.4 km pixels) are thinned to about 4 km:
   the lake is cut into 3 x 3 blocks of pixels, and each block is drawn as one square
   using the real pixel closest to the block's centre. No values are averaged or
   invented; every square shows one real pixel's own measurement or trend test.
   About 4 km also matches the MODIS chlorophyll pixels.

Run from the repo root after rebuilding the maps:
    python data/scripts/compact_web_maps.py
"""
import json
import math
from pathlib import Path

WEB_DATA = Path("web/public/data")
KEEP = {"lat", "lon", "direction", "p_value", "significant", "slope_per_decade",
        "concentration", "temperature", "n_years"}
BLOCK = 3  # thin temperature maps to 3 x 3 pixel blocks


def square(lon0, lat0, lon1, lat1):
    r = lambda v: round(v, 4)
    return {"type": "Polygon", "coordinates": [[[r(lon0), r(lat0)], [r(lon1), r(lat0)],
            [r(lon1), r(lat1)], [r(lon0), r(lat1)], [r(lon0), r(lat0)]]]}


def cell_size(feature):
    ring = feature["geometry"]["coordinates"][0]
    xs = [p[0] for p in ring]
    ys = [p[1] for p in ring]
    return max(xs) - min(xs), max(ys) - min(ys)


def thin(features):
    dx, dy = cell_size(features[0])
    lon_min = min(f["properties"]["lon"] for f in features)
    lat_min = min(f["properties"]["lat"] for f in features)
    blocks = {}
    for f in features:
        p = f["properties"]
        col = round((p["lon"] - lon_min) / dx)
        row = round((p["lat"] - lat_min) / dy)
        key = (col // BLOCK, row // BLOCK)
        # centre of this block, in pixel units
        cx, cy = key[0] * BLOCK + (BLOCK - 1) / 2, key[1] * BLOCK + (BLOCK - 1) / 2
        dist = math.hypot(col - cx, row - cy)
        if key not in blocks or dist < blocks[key][0]:
            blocks[key] = (dist, f)
    out = []
    for (bx, by), (_, f) in blocks.items():
        lon0 = lon_min + (bx * BLOCK - 0.5) * dx
        lat0 = lat_min + (by * BLOCK - 0.5) * dy
        out.append({"type": "Feature", "properties": f["properties"],
                    "geometry": square(lon0, lat0, lon0 + BLOCK * dx, lat0 + BLOCK * dy)})
    return out


def compact(path: Path):
    geo = json.loads(path.read_text())
    before = path.stat().st_size
    features = []
    for f in geo["features"]:
        props = {k: v for k, v in f["properties"].items() if k in KEEP}
        if f["geometry"]["type"] == "Polygon":
            ring = f["geometry"]["coordinates"][0]
            xs = [p[0] for p in ring]
            ys = [p[1] for p in ring]
            geom = square(min(xs), min(ys), max(xs), max(ys))
        else:
            geom = f["geometry"]
        features.append({"type": "Feature", "properties": props, "geometry": geom})
    meta = dict(geo.get("properties", {}))
    if "temperature" in path.name and len(features) and meta.get("thinned_to_km") is None:
        meta["original_pixels"] = len(features)
        features = thin(features)
        meta["thinned_to_km"] = 4
        meta["thinning"] = ("Shown at about 4 km: one real 1.4 km NOAA GLSEA pixel per 3 x 3 block, "
                            "nearest the block centre. Values are not averaged.")
        meta["shown_pixels"] = len(features)
        if "significant_pixels" in meta:
            meta["significant_pixels_shown"] = sum(1 for f in features if f["properties"].get("significant"))
    geo["properties"] = meta
    geo["features"] = features
    path.write_text(json.dumps(geo, ensure_ascii=False, separators=(",", ":")))
    print(f"{path}: {before/1e6:.1f} MB -> {path.stat().st_size/1e6:.2f} MB ({len(features)} squares)")


if __name__ == "__main__":
    for p in sorted(WEB_DATA.rglob("*.geojson")):
        if p.name == "lake_erie_boundary.geojson":
            continue
        compact(p)
