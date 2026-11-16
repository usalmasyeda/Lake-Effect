# Submission drafts: every form field (edit freely)

usereeah checks every science claim before we submit. Field names match the 2026 Project Submission Guide.

## Project Name

Lake Effect

## High-Level Project Summary

Lake Effect is a web tool for NASA's "Be an Earth System Trend Detective" challenge. It answers four questions: what is changing, where, how much, and is the change significant? Pick a lake, and our Trend Scanner runs a Mann-Kendall trend test with Sen's slope on every available variable, ranks them by real change, and maps where change happens, pixel by pixel. A change only counts when the test says it is significant (p < 0.05), so the tool separates signal from year-to-year noise.

We start with Lake Erie, where harmful algal blooms return every summer, typically July to October (NOAA), and reach beaches in our own city, Windsor. Algae is rising: NASA MODIS-Aqua chlorophyll-a over Lake Erie (July to October, 2003–2025) increased about 1.55 mg/m³ per decade, a significant trend (p < 0.001), in both the western basin and the central and eastern basins. Bloom-season water temperature drifted up about 0.41 °C per decade (2007–2025), but that trend is not yet significant (p = 0.069): our tool says so instead of overclaiming.

The same tool already runs on all five Great Lakes: search for Erie, Ontario, Huron, Michigan or Superior to see each lake's ranked trends, maps and charts. Chlorophyll is rising significantly in Erie, Huron and Michigan; temperature is rising significantly in Ontario and Huron.

## Link to Project Demo

[Public YouTube or Google Drive link to the 30-second video, OR a public link to the 7-slide deck. Test it in a private browser window.]

## Link to Final Project

https://usalmasyeda.github.io/Lake-Effect/ (code: https://github.com/usalmasyeda/Lake-Effect)

## Detailed Project Description

**What it does.** Lake Effect helps anyone see which environmental changes in a lake are real. Instead of drawing a trend line and hoping, it tests every variable for statistical significance, ranks them from the strongest real change to none, and shows where in the lake the change is happening.

**How it works.**
1. We download satellite data for the five Great Lakes: NASA MODIS-Aqua chlorophyll-a (algae, about 4 km pixels) and NOAA GLSEA satellite lake surface temperature (about 1.4 km pixels). We mask the data to each lake's shoreline.
2. We average each variable over the bloom season (July to October, as defined by NOAA) for every year, for the whole lake, a western and an eastern part, and for every satellite pixel. For Lake Erie we split at 82.5° W (western basin vs central + eastern basins); for the other lakes, the western and eastern sections split each lake at its middle.
3. Our Trend Scanner (Python) runs the Mann-Kendall test on each series and pixel. A change counts as real only when p < 0.05. Sen's slope gives the size of the change per decade.
4. Results are saved as JSON and GeoJSON files and shown on a website: a lake search, a ranked list of variables, maps of this year's chlorophyll and temperature and of the long-term trend (coloured by significant increase or decrease), a time-series chart by region, and a short guided story for Lake Erie.

**Benefits.** It answers the challenge's hardest question, "is it significant?", clearly and honestly. For example, it shows that Lake Erie's summer water temperature has drifted upward but is not yet a significant trend, rather than overclaiming. It also maps where change happens: chlorophyll is rising significantly across 1,300 of 1,593 satellite pixels, in the western basin (+1.34 mg/m³ per decade) and the central and eastern basins (+1.39), with no pixel showing a significant decrease. The result holds up when we drop the two highest recent years and when we correct the test for autocorrelation.

**What we hope to achieve.** A simple, honest trend detector that residents, students and local decision-makers in Windsor-Essex can use to understand their lake, and that already covers all five Great Lakes.

**Tools.** Python (pandas, NumPy, xarray, pymannkendall), HTML/CSS/JavaScript with Leaflet and Chart.js, GitHub and GitHub Pages. We used Claude, ChatGPT and GitHub Copilot, AI assistants, to help write code and documents (see the README).

## Use of Super Intelligence (SI)

(Data collection only; judges don't see this answer, but they do see the AI labels in our project.)

Yes. The project idea came from our team: Salma lives in Windsor, where algal blooms affect local beaches, and wanted to tackle an environmental problem close to home. We used Claude (an AI assistant by Anthropic) to help refine the technical approach, plan the team's work, write most of the starter code (the data scripts and the website), and draft documents, slides and graphics. GitHub Copilot helped with the website's error handling and the map year slider. Our data lead used ChatGPT to help write the data download and processing scripts and the five-lakes maps. The team defined the science (bloom season, basin split) from cited sources, downloaded and processed the data, ran the analysis, and reviewed all results. AI-written code is marked at the top of each file and in the README; AI-generated images and video carry a visible "AI-generated" label.

## NASA Data

- **Aqua MODIS Level-3 Mapped Chlorophyll (CHL), version 2022.0, monthly, 4 km (`chlor_a`)** from the NASA Ocean Biology DAAC (https://www.earthdata.nasa.gov/centers/ob-daac), accessed through NASA Earthdata Search. July–October monthly files, 2003–2025, averaged per bloom season, masked to Lake Erie. This is the core of our project: it drives the ranked scanner, the trend map and the main finding.
- NASA Earthdata (https://www.earthdata.nasa.gov) for finding and downloading the data.

## Space Agency Partner Data and Other References

- NOAA GLERL GLSEA (ACSPO) gridded daily lake surface temperature for the five Great Lakes, 2007–2025, via GLERL ERDDAP `GLSEA_ACSPO_GCS` (https://coastwatch.glerl.noaa.gov/satellite-data-products/lake-surface-temperature)
- NOAA GLERL GLSEA lake-wide daily averages for Lake Erie (`glsea_avgtemps_3`), used to cross-check the temperature result (+0.44 °C per decade, p = 0.069, also not significant)
- NOAA NCCOS, Lake Erie Harmful Algal Bloom FAQs: bloom season definition (https://coastalscience.noaa.gov/science-areas/habs/hab-forecasts/lake-erie/faqs/)
- NOAA CoastWatch Great Lakes tutorial: GLSEA file format (https://coastwatch-training.github.io/tutorials/gl-timeseries-surface-temp/python/gl-timeseries-surface-temp.html)
- Canada–Ontario Lake Erie Action Plan (https://www.ontario.ca/page/canada-ontario-lake-erie-action-plan)
- Windsor-Essex County Health Unit: blue-green algae (https://www.wechu.org/your-environment/blue-green-algae-bloom) and beaches (https://www.wechu.org/your-environment/beaches)
- Essex Region Conservation Authority: watershed health (https://www.essexregionconservation.ca/programs-services/watershed-health)
- 2024 Canada–Ontario Lake Erie evaluation (https://www.canada.ca/en/canada-water-agency/freshwater-ecosystem-initiatives/great-lakes/great-lakes-protection/taking-action-protect/preventing-toxic-nuisance-algae/erie-evaluation-update-2024.html)
- Natural Earth 1:10m lakes: Great Lakes boundaries (public domain)
- OpenStreetMap: website background map (© OpenStreetMap contributors, ODbL)
- Python libraries for processing: geopandas, shapely (BSD-3-Clause)
- Code libraries: pymannkendall (MIT), pandas and NumPy (BSD-3-Clause), xarray (Apache-2.0), netCDF4 (MIT), Leaflet (BSD-2-Clause), Chart.js (MIT)
- Fonts: Space Grotesk, Inter, JetBrains Mono (Google Fonts, SIL Open Font License)
- Claude (Anthropic): AI assistant, see "Use of SI"
- GitHub Copilot: AI coding assistant, see "Use of SI"
- ChatGPT (OpenAI): AI assistant, see "Use of SI"
- Our code: MIT licence, https://github.com/usalmasyeda/Lake-Effect

## 30-second video script

Follows the 2026 guide's timing. About 75 spoken words. Add English subtitles. No images, voices or names of anyone under 18. Add a visible "AI-generated" label to any AI-made visuals.

| Time | On screen | Voiceover |
| --- | --- | --- |
| 0:00–0:02 | Cover slide | "Hi, we're team Lake Effect from Windsor." |
| 0:02–0:05 | A Lake Erie beach photo you took yourself, or slide 2 | "Every summer, algae blooms reach the beaches in our own city." |
| 0:05–0:10 | Slide 3: What? Where? How much? Significant? | "For NASA's Trend Detective challenge, we built Lake Effect: which changes in Lake Erie are real?" |
| 0:10–0:20 | Website: the ranked list, trend map, basin chart | "Our Trend Scanner tests NASA satellite data and keeps only real change. Algae in Lake Erie is rising across almost the whole lake." |
| 0:20–0:30 | Closing slide with the team names | "And it already works on all five Great Lakes, so communities everywhere can see what's really changing." |
