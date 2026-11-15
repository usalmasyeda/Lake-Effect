import json
from pathlib import Path

lakes = [
    "lake_erie",
    "lake_ontario",
    "lake_huron",
    "lake_michigan",
    "lake_superior"
]

for lake in lakes:
    folder = (
        Path("web/public/data")
        if lake == "lake_erie"
        else Path("web/public/data/lakes") / lake
    )

    with (folder / "scanner.json").open() as f:
        data = json.load(f)

    print("\n" + "=" * 45)
    print(data["region"])

    for variable in data["variables"]:
        print("\nVariable:", variable["name"])

        for region, trend in variable["trend"].items():
            print(
                region,
                "| Direction:", trend["direction"],
                "| Slope:", trend["slope_per_decade"],
                "| P-value:", trend["p_value"],
                "| Significant:", trend["significant"]
            )

