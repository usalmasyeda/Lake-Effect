# Lake Effect

**Pick a lake, scan every variable for real change, and see what is changing, where, how much, and whether it's significant.**

Lake Effect is our project for the **NASA Space Apps Challenge 2026** (Windsor local event), answering the challenge **Be an Earth System Trend Detective**. We start with Lake Erie, where harmful algal blooms affect drinking water, fishing and summers on the lake for Windsor-Essex and beyond.

> 🌐 **Live site:** https://usalmasyeda.github.io/Lake-Effect/

## What we found (Lake Erie, July–October bloom season)

| Variable | Whole lake | Western basin | Central + eastern basins |
| --- | --- | --- | --- |
| Chlorophyll-a (algae), NASA MODIS-Aqua, 2003–2025 | **+1.55 mg/m³ per decade**, p < 0.001, significant | +1.34, p = 0.004, significant | +1.39, p < 0.001, significant |
| Lake surface temperature, NOAA GLSEA, 2007–2025 | +0.41 °C per decade, p = 0.069, **not significant yet** | +0.46, p = 0.11, not significant | +0.45, p = 0.059, not significant |

1,300 of 1,593 satellite pixels show a significant increase in algae, and none a decrease. The algae trend stays significant without the two highest recent years (2024–25) and with an autocorrelation-corrected test (Hamed-Rao). The same tool runs on all five Great Lakes.

## How it works

1. **Satellite data** for all five Great Lakes: NASA MODIS-Aqua chlorophyll-a (algae) and NOAA GLSEA lake surface temperature (precipitation from NASA MERRA-2 is a next step)
2. **Clean and average**: cut to each lake's shoreline, one July–October value per year (and per pixel)
3. **Trend Scanner**: every variable gets a Mann-Kendall test (is the change real?) and Sen's slope (how much per decade?)
4. **Ranked list + trend map**: biggest real changes first; the map shows where, pixel by pixel
5. **Interactive tool**: pick a lake from the menu, pick a variable; slide through the years on the map (algae 2003–2025, temperature 2007–2025), switch to the long-term trend map, and see a chart for each part of the lake and the numbers
6. **Lake Erie story**: a guided tour of what we found, west basin vs east basin

Regions: for Lake Erie, the western basin is west of 82.5° W. For the other four lakes, the "western" and "eastern" sections split each lake at its middle (not at its basins).

Temperature: the website uses NOAA's gridded GLSEA (ACSPO) temperature, so it can map every lake (Lake Erie: +0.41 °C per decade, p = 0.069). Our first analysis used NOAA's lake-wide GLSEA averages (`glsea_avgtemps_3`, +0.44 °C per decade, p = 0.069, see `docs/findings/`). Both say the same thing: an upward drift that is not significant yet.

Map size: temperature maps are shown at about 4 km (one real 1.4 km pixel per 3 x 3 block, no averaging) so the site loads fast; see `data/scripts/compact_web_maps.py`.

A change counts as **significant** when its Mann-Kendall p-value is below **0.05**.

## Repo layout

```
lake-effect/
├── data/
│   ├── README.md                 # how to reproduce the data, step by step
│   ├── scripts/
│   │   ├── download_nasa_*.sh/.py           # MODIS-Aqua chlorophyll downloads (Earthdata Login)
│   │   ├── get_glsea_temperature.py         # NOAA GLSEA lake-wide averages
│   │   ├── process_chlorophyll.py           # Lake Erie: mask, Jul–Oct average, basins
│   │   ├── process_temperature.py           # Lake Erie temperature from gridded GLSEA
│   │   ├── process_other_lakes.py           # the other four Great Lakes
│   │   ├── trend_scanner.py                 # Mann-Kendall + Sen's slope (series and per pixel)
│   │   ├── filter_trend_map.py              # keep pixels with at least 15 years
│   │   ├── build_*_maps.py, compact_web_maps.py  # map files for the website
│   │   └── make_sample_data.py              # fake data used only while building
│   ├── raw/                      # downloaded files (not committed, too big)
│   └── processed/                # yearly CSVs and NetCDF cubes, lake boundaries
├── web/                          # the website (index.html, app.js, style.css)
│   └── public/data/              # JSON + GeoJSON the website reads
├── docs/                         # story, data format, findings, submission notes
└── tools/record_demo.js          # records the demo video from the live site
```

## Reproduce the results

```bash
pip install -r requirements.txt
# 1. Download and process the data: see data/README.md (needs a free NASA Earthdata Login)
# 2. Run the Trend Scanner on the yearly series and the per-pixel cube
python data/scripts/trend_scanner.py series data/processed/series
python data/scripts/trend_scanner.py grid data/processed/chlorophyll_yearly.nc --variable chlorophyll
# 3. Build the website's map files
python data/scripts/build_yearly_maps.py
python data/scripts/compact_web_maps.py
```

The website in `web/` is static: open `web/index.html` through any local web server (for example `python -m http.server` in `web/`).

## Data sources

| Variable | Source |
| --- | --- |
| Chlorophyll-a | NASA MODIS-Aqua, [Ocean Biology DAAC](https://www.earthdata.nasa.gov/centers/ob-daac) |
| Lake surface temperature | NOAA GLERL [GLSEA](https://coastwatch.glerl.noaa.gov/satellite-data-products/lake-surface-temperature) (gridded ACSPO, and lake-wide averages) |
| Precipitation (next step, not in the results yet) | NASA [MERRA-2 M2TMNXFLX](https://www.earthdata.nasa.gov/fr/data/catalog/ges-disc-m2tmnxflx-5.12.4) |
| Trend test | [pymannkendall](https://pypi.org/project/pymannkendall) |

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
| GLSEA product page and ERDDAP dataset `GLSEA_ACSPO_GCS` | NOAA GLERL: https://coastwatch.glerl.noaa.gov/satellite-data-products/great-lakes-surface-environmental-analysis-glsea/ and https://apps.glerl.noaa.gov/erddap/griddap/GLSEA_ACSPO_GCS.html | Temperature download |
| Ocean Color Level-3 data and direct data access | NASA OB.DAAC: https://oceandata.sci.gsfc.nasa.gov/l3/ and https://oceandata.sci.gsfc.nasa.gov/directdataaccess/ | Chlorophyll download |
| Earthdata Login and Earthdata Search | NASA: https://urs.earthdata.nasa.gov/ and https://search.earthdata.nasa.gov/ | Data access |
| NASA Earth science data and information policy | NASA: https://www.earthdata.nasa.gov/engage/open-data-services-and-software/data-and-information-policy | Data use terms |
| Climate Change Indicators: Great Lakes Water Levels and Temperatures (archived Jan 2025) | US EPA: https://19january2025snapshot.epa.gov/climate-indicators/great-lakes | Context: slight warming since 1995 |
| State of the Great Lakes 2025 | US EPA and Canada Water Agency, binational.net: https://binational.net/2026/01/20/state-of-the-great-lakes-2025 | Background on long-term Great Lakes change |

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
