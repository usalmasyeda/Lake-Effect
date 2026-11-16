# Lake Effect

**Pick a lake, scan every variable for real change, and see what is changing, where, how much, and whether it's significant.**

Lake Effect is our project for the **NASA Space Apps Challenge 2026** (Windsor local event), answering the challenge **Be an Earth System Trend Detective**. We start with Lake Erie, where harmful algal blooms affect drinking water, fishing and summers on the lake for Windsor-Essex and beyond.

> 📘 **New here? Read the [team game plan](docs/Lake-Effect-Game-Plan.pdf) first:** what we're building, who does what, and how it all connects. Your tasks are in the **Issues** tab.
>
> 🌐 **Live site:** https://usalmasyeda.github.io/Lake-Effect/

## How it works

1. **Satellite data** for all five Great Lakes: NASA MODIS-Aqua chlorophyll-a (algae) and NOAA GLSEA lake surface temperature (precipitation from NASA MERRA-2 is a next step)
2. **Clean and average**: cut to Lake Erie, one value per year (and per pixel)
3. **Trend Scanner**: every variable gets a Mann-Kendall test (is the change real?) and Sen's slope (how much per decade?)
4. **Ranked list + trend map**: biggest real changes first; the map shows where, pixel by pixel
5. **Interactive tool**: search for a lake, pick a variable; slide through the years on the map (2007–2025), switch to the long-term trend map, and see a chart for each part of the lake and the numbers
6. **Lake Erie story**: a guided tour of what we found, west basin vs east basin

Regions: for Lake Erie, the western basin is west of 82.5° W. For the other four lakes, the "western" and "eastern" sections split each lake at its middle (not at its basins).

Temperature: the website uses NOAA's gridded GLSEA (ACSPO) temperature, so it can map every lake (Lake Erie: +0.41 °C per decade, p = 0.069). Our first analysis used NOAA's lake-wide GLSEA averages (`glsea_avgtemps_3`, +0.44 °C per decade, p = 0.069, see `docs/findings/`). Both say the same thing: an upward drift that is not significant yet.

Map size: temperature maps are shown at about 4 km (one real 1.4 km pixel per 3 x 3 block, no averaging) so the site loads fast; see `data/scripts/compact_web_maps.py`.

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
| Lake surface temperature | NOAA GLERL [GLSEA](https://coastwatch.glerl.noaa.gov/satellite-data-products/lake-surface-temperature) (gridded ACSPO, and lake-wide averages) |
| Precipitation (next step, not in the results yet) | NASA [MERRA-2 M2TMNXFLX](https://www.earthdata.nasa.gov/fr/data/catalog/ges-disc-m2tmnxflx-5.12.4) |
| Trend test | [pymannkendall](https://pypi.org/project/pymannkendall) |

## Key times (Windsor, ET)

- **Sunday 6:00 PM**: feature freeze, fixes only after this
- **Sunday 8:00 PM**: our target to submit
- **Sunday 11:59 PM**: official deadline

## Team

| Name | Role |
| --- | --- |
| Salma | Captain: design, story, pitch, data support |
| Mehak | Data lead, design support |
| Yusriyah (usereeah) | Science lead |
| Faria | Web developer |
| Yumna | Testing and design support |

## Use of AI (Super Intelligence) tools

We used **Claude** (an AI assistant by Anthropic), **ChatGPT** (OpenAI) and **GitHub Copilot** as tools during the hackathon, as allowed by the Space Apps rules:

- **Code:** AI wrote most of the starter code: `data/scripts/trend_scanner.py`, `data/scripts/make_sample_data.py`, `data/scripts/get_glsea_temperature.py` and the website in `web/`. GitHub Copilot helped with the website's error handling and the map year slider (pull requests #19 and #20). Mehak used ChatGPT to help write the data download and processing scripts, the five-lakes maps and the five-lakes version of the website. Each AI-assisted file says so at the top. Team members ran, tested and adapted the code.
- **Documents and graphics:** AI drafted planning documents, the slide deck, the video script and our graphics. AI-generated images and video carry a visible "AI-generated" label.
- **Not AI:** the project idea comes from our team (Salma lives in Windsor, where algal blooms affect local beaches). The team defined the science (bloom season, basin split) from cited sources, downloaded and processed the data, ran the analysis and reviewed every result.

## References

### Data

| Data | Provider | Use |
| --- | --- | --- |
| MODIS-Aqua chlorophyll-a | NASA Ocean Biology DAAC: https://www.earthdata.nasa.gov/centers/ob-daac | Algae trend (main NASA dataset) |
| GLSEA (ACSPO) gridded lake surface temperature, `GLSEA_ACSPO_GCS` on GLERL ERDDAP | NOAA GLERL: https://coastwatch.glerl.noaa.gov/satellite-data-products/lake-surface-temperature | Temperature maps and trends, all five lakes |
| GLSEA lake surface temperature (lake-wide daily averages, `glsea_avgtemps_3`) | NOAA GLERL (same page) | Lake Erie temperature cross-check |
| Lake Erie bloom season (July to October) | NOAA NCCOS Lake Erie HAB FAQs: https://coastalscience.noaa.gov/science-areas/habs/hab-forecasts/lake-erie/faqs/ | Analysis definition |
| GLSEA file format and access | NOAA CoastWatch Great Lakes tutorial: https://coastwatch-training.github.io/tutorials/gl-timeseries-surface-temp/python/gl-timeseries-surface-temp.html | Download method |

### Code, libraries and design resources

| Resource | Use | Licence |
| --- | --- | --- |
| pymannkendall | Mann-Kendall test, Sen's slope | MIT |
| pandas, NumPy | Data handling | BSD-3-Clause |
| xarray, netCDF4 | Gridded satellite files | Apache-2.0, MIT |
| geopandas, shapely | Lake boundary masks | BSD-3-Clause |
| Leaflet | Web map | BSD-2-Clause |
| Chart.js | Web charts | MIT |
| Natural Earth 1:10m lakes (Great Lakes shorelines) | Lake boundaries | Public domain |
| OpenStreetMap | Website background map | © OpenStreetMap contributors, ODbL |
| Google Fonts: Space Grotesk, Inter, JetBrains Mono | Typography | SIL Open Font License |
| GitHub Pages | Hosting | GitHub terms |
| Claude (Anthropic) | AI assistant, see above | Anthropic terms |
| GitHub Copilot | AI coding assistant, see above | GitHub terms |
| ChatGPT (OpenAI) | AI assistant, see above | OpenAI terms |

## License

MIT, see [LICENSE](LICENSE).
