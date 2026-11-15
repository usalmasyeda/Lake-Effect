# Lake Effect

**Pick a lake, scan every variable for real change, and see what is changing, where, how much, and whether it's significant.**

Lake Effect is our project for the **NASA Space Apps Challenge 2026** (Windsor local event), answering the challenge **Be an Earth System Trend Detective**. We start with Lake Erie, where harmful algal blooms affect drinking water, fishing and summers on the lake for Windsor-Essex and beyond.

> 📘 **New here? Read the [team game plan](docs/Lake-Effect-Game-Plan.pdf) first:** what we're building, who does what, and how it all connects. Your tasks are in the **Issues** tab.
>
> 🌐 **Live site:** https://usalmasyeda.github.io/Lake-Effect/

## How it works

1. **NASA satellite and model data**: chlorophyll-a (algae), lake surface temperature, precipitation
2. **Clean and average**: cut to Lake Erie, one value per year (and per pixel)
3. **Trend Scanner**: every variable gets a Mann-Kendall test (is the change real?) and Sen's slope (how much per decade?)
4. **Ranked list + trend map**: biggest real changes first; the map shows where, pixel by pixel
5. **Interactive tool**: pick a variable, area and years; see the map, chart and numbers
6. **Lake Erie story**: a guided tour of what we found, west basin vs east basin

A change counts as **significant** when its Mann-Kendall p-value is below **0.05**.

## Repo layout

```
lake-effect/
├── data/
│   ├── scripts/
│   │   ├── trend_scanner.py      # the Trend Scanner (series + per-pixel map)
│   │   └── make_sample_data.py   # fake data so the web app can be built early
│   ├── raw/                      # downloaded NASA files (not committed, too big)
│   └── processed/                # yearly CSVs and NetCDF cubes we build
├── web/
│   └── public/data/              # JSON + GeoJSON the web app reads
├── docs/
│   ├── data-format.md            # the contract between data and web
│   ├── story.md                  # the Lake Erie story outline
│   └── handoffs.md               # end-of-session notes
├── TASKS.md                      # who does what
└── CONTRIBUTING.md               # how to work in this repo
```

## Quick start (data)

```bash
pip install -r requirements.txt
python data/scripts/make_sample_data.py
python data/scripts/trend_scanner.py series data/processed/sample/series --sample
python data/scripts/trend_scanner.py grid data/processed/sample/chlorophyll_yearly.nc --variable chlorophyll --sample
```

This writes `web/public/data/scanner.json` and `web/public/data/trend_map_chlorophyll.geojson`. Sample files are marked `"sample": true`; **never use sample numbers in the story or submission.** When the real data is ready, run the same commands on it without `--sample`.

## Data sources

| Variable | Source |
| --- | --- |
| Chlorophyll-a | NASA MODIS-Aqua, [Ocean Biology DAAC](https://www.earthdata.nasa.gov/centers/ob-daac) |
| Chlorophyll (recent) | NASA PACE OCI, [chlorophyll data tools](https://www.earthdata.nasa.gov/topics/biosphere/chlorophyll/data-access-tools) |
| Lake surface temperature | NOAA GLERL [GLSEA](https://coastwatch.glerl.noaa.gov/satellite-data-products/lake-surface-temperature) |
| Precipitation (model) | NASA [MERRA-2 M2TMNXFLX](https://www.earthdata.nasa.gov/fr/data/catalog/ges-disc-m2tmnxflx-5.12.4) |
| Trend test | [pymannkendall](https://pypi.org/project/pymannkendall) |

## Key times (Windsor, ET)

- **Sunday 1:00 PM**: feature freeze, must-haves only after this
- **Sunday 8:00 PM**: our target to submit
- **Sunday 11:59 PM**: official deadline

## Team

| Name | Role |
| --- | --- |
| Salma | Captain: design, story, pitch, data support |
| Mehak | Data lead, design support |
| usereeah | Science lead |
| Faria | Web developer |
| Yumna | Testing and design support |

## Use of AI (Super Intelligence) tools

We used **Claude** (an AI assistant by Anthropic) as a tool during the hackathon, as allowed by the Space Apps rules:

- **Code:** AI wrote most of the starter code: `data/scripts/trend_scanner.py`, `data/scripts/make_sample_data.py`, `data/scripts/get_glsea_temperature.py` and the website in `web/`. Each AI-assisted file says so at the top. Team members ran, tested and adapted the code.
- **Documents and graphics:** AI drafted planning documents, the slide deck, the video script and our graphics. AI-generated images and video carry a visible "AI-generated" label.
- **Not AI:** the project idea comes from our team (Salma lives in Windsor, where algal blooms affect local beaches). The team defined the science (bloom season, basin split) from cited sources, downloaded and processed the data, ran the analysis and reviewed every result.

## References

### Data

| Data | Provider | Use |
| --- | --- | --- |
| MODIS-Aqua chlorophyll-a | NASA Ocean Biology DAAC: https://www.earthdata.nasa.gov/centers/ob-daac | Algae trend (main NASA dataset) |
| GLSEA lake surface temperature (lake-wide daily averages, `glsea_avgtemps_3`) | NOAA GLERL: https://coastwatch.glerl.noaa.gov/satellite-data-products/lake-surface-temperature | Temperature trend |
| Lake Erie bloom season (July to October) | NOAA NCCOS Lake Erie HAB FAQs: https://coastalscience.noaa.gov/science-areas/habs/hab-forecasts/lake-erie/faqs/ | Analysis definition |
| GLSEA file format and access | NOAA CoastWatch Great Lakes tutorial: https://coastwatch-training.github.io/tutorials/gl-timeseries-surface-temp/python/gl-timeseries-surface-temp.html | Download method |

### Code, libraries and design resources

| Resource | Use | Licence |
| --- | --- | --- |
| pymannkendall | Mann-Kendall test, Sen's slope | MIT |
| pandas, NumPy | Data handling | BSD-3-Clause |
| xarray, netCDF4 | Gridded satellite files | Apache-2.0, MIT |
| Leaflet | Web map | BSD-2-Clause |
| Chart.js | Web charts | MIT |
| CARTO basemap tiles, OpenStreetMap data | Map background | Attribution required; OSM data under ODbL |
| Google Fonts: Space Grotesk, Inter, JetBrains Mono | Typography | SIL Open Font License |
| GitHub Pages | Hosting | GitHub terms |
| Claude (Anthropic) | AI assistant, see above | Anthropic terms |

## License

MIT, see [LICENSE](LICENSE).
