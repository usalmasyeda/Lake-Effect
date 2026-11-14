# Data format: the contract between data and web

The data side writes these files into `web/public/data/`. The web app only reads them. If you need to change a shape, agree it in #data and #web first.

## `scanner.json`: the ranked Trend Scanner

```json
{
  "region": "Lake Erie",
  "generated": "2026-11-14T18:46:00+00:00",
  "sample": false,
  "alpha": 0.05,
  "ranking": ["chlorophyll", "lake_temperature", "precipitation"],
  "variables": [
    {
      "id": "chlorophyll",
      "name": "Chlorophyll-a (algae)",
      "units": "mg/m³",
      "source": "NASA MODIS-Aqua, Ocean Biology DAAC",
      "years": [2003, 2004, "..."],
      "series": { "lake": [5.1, "..."], "west": [8.2, "..."], "east": [3.0, "..."] },
      "trend": {
        "lake": { "direction": "increasing", "p_value": 0.0004, "significant": true,
                  "slope_per_decade": 1.44, "n_years": 23 },
        "west": { "...": "same fields" },
        "east": { "...": "same fields" }
      }
    }
  ]
}
```

- `ranking`: variable ids, strongest significant change first. Show them in this order.
- `direction`: `"increasing"`, `"decreasing"`, `"no significant trend"` or `"insufficient data"`.
- `slope_per_decade`: Sen's slope × 10, in the variable's `units` per decade.
- `series` values can be `null` for missing years.
- Regions (Issue #5): `west` = longitude < -82.5° (western basin); `east` = longitude >= -82.5° (central **and** eastern basins together). Label `east` as "Central + eastern basins".
- Bloom season (Issue #5): June 1 to October 31.
- A variable may only have `lake` (e.g. lake temperature from GLSEA lake-wide averages).

## `trend_map_<variable>.geojson`: where it's changing

A GeoJSON `FeatureCollection` of square grid cells. Each feature's `properties`:

```json
{ "lat": 41.7, "lon": -83.1, "direction": "increasing", "p_value": 0.001,
  "significant": true, "slope_per_decade": 2.6, "n_years": 23 }
```

Top-level `properties` carries `variable`, `name`, `units`, `alpha`, `sample`, `generated`.

## Map colouring (shared with design)

| Cell | Colour |
| --- | --- |
| Significant increase | lime `#A8D65C` (stronger = larger slope) |
| Significant decrease | teal `#4FC3C9` |
| Not significant | grey, 25% opacity |

## Sample vs real

Every file has `"sample": true | false`. While `sample` is `true`, the web app should show a small **"Sample data"** badge.
