
"""Filter chlorophyll trend map features by observation coverage."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAP_PATH = ROOT / "web/public/data/trend_map_chlorophyll.geojson"

MIN_YEARS = 15


def main():
    with MAP_PATH.open() as f:
        data = json.load(f)

    original_count = len(data["features"])

    data["features"] = [
        feature
        for feature in data["features"]
        if feature.get("properties", {}).get("n_years", 0) >= MIN_YEARS
    ]

    with MAP_PATH.open("w") as f:
        json.dump(data, f)

    print("Original features:", original_count)
    print("Filtered features:", len(data["features"]))
    print("Removed features:", original_count - len(data["features"]))


if __name__ == "__main__":
    main()
