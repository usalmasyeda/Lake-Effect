# Submission drafts: every form field (edit freely)

Lines in [brackets] wait for Mehak's chlorophyll results. usereeah checks every science claim before we submit. Field names match the 2026 Project Submission Guide.

## Project Name

Lake Effect

## High-Level Project Summary

Lake Effect is a web tool for NASA's "Be an Earth System Trend Detective" challenge. It answers four questions: what is changing, where, how much, and is the change significant? Pick a lake, and our Trend Scanner runs a Mann-Kendall trend test with Sen's slope on every available variable, ranks them by real change, and maps where change happens, pixel by pixel. A change only counts when the test says it is significant (p < 0.05), so the tool separates signal from year-to-year noise.

We start with Lake Erie, where harmful algal blooms return every summer, typically July to October (NOAA), and reach beaches in our own city, Windsor. So far, bloom-season surface temperature rose about 0.44 °C per decade from 2007 to 2025, but the trend is not yet significant (p = 0.069). [Chlorophyll result: which basin, how much, significant or not.]

The same tool works for any lake and any gridded Earth science variable.

## Link to Project Demo

[Public YouTube or Google Drive link to the 30-second video, OR a public link to the 7-slide deck. Test it in a private browser window.]

## Link to Final Project

https://usalmasyeda.github.io/Lake-Effect/ (code: https://github.com/usalmasyeda/Lake-Effect)

## Detailed Project Description

**What it does.** Lake Effect helps anyone see which environmental changes in a lake are real. Instead of drawing a trend line and hoping, it tests every variable for statistical significance, ranks them from the strongest real change to none, and shows where in the lake the change is happening.

**How it works.**
1. We download satellite and model data for Lake Erie: NASA MODIS-Aqua chlorophyll-a (algae), NOAA GLSEA lake surface temperature [and NASA MERRA-2 precipitation].
2. We average each variable over the bloom season (July to October, as defined by NOAA) for every year, for the whole lake, the western basin (west of 82.5° W) and the central + eastern basins, and for every satellite pixel.
3. Our Trend Scanner (Python) runs the Mann-Kendall test on each series and pixel. A change counts as real only when p < 0.05. Sen's slope gives the size of the change per decade.
4. Results are saved as JSON and GeoJSON files and shown on a website: a ranked list of variables, a trend map coloured by significant increase or decrease, a time-series chart by basin, and a short guided story.

**Benefits.** It answers the challenge's hardest question, "is it significant?", clearly and honestly. For example, it shows that Lake Erie's summer water temperature has drifted upward but is not yet a significant trend, rather than overclaiming. It also shows that one variable can change differently in different parts of the same lake. [Chlorophyll west-vs-east example.]

**What we hope to achieve.** A simple, honest trend detector that residents, students and local decision-makers in Windsor-Essex can use to understand their lake, and that works for any other lake.

**Tools.** Python (pandas, NumPy, xarray, pymannkendall), HTML/CSS/JavaScript with Leaflet and Chart.js, GitHub and GitHub Pages. We used Claude, an AI assistant, to help write code and documents (see the README).

## Use of Super Intelligence (SI)

(Data collection only; judges don't see this answer, but they do see the AI labels in our project.)

Yes. The project idea came from our team: Salma lives in Windsor, where algal blooms affect local beaches, and wanted to tackle an environmental problem close to home. We used Claude (an AI assistant by Anthropic) to help refine the technical approach, plan the team's work, write most of the starter code (the data scripts and the website), and draft documents, slides and graphics. The team defined the science (bloom season, basin split) from cited sources, downloaded and processed the data, ran the analysis, and reviewed all results. AI-written code is marked at the top of each file and in the README; AI-generated images and video carry a visible "AI-generated" label.

## NASA Data

- **MODIS-Aqua chlorophyll-a** from the NASA Ocean Biology DAAC (https://www.earthdata.nasa.gov/centers/ob-daac): [Mehak: exact product name, resolution, date range]. Used to measure algae trends over Lake Erie, by basin and by pixel, for the bloom season (July to October).
- [**MERRA-2 M2TMNXFLX** precipitation from NASA GES DISC, if added.]
- NASA Earthdata (https://www.earthdata.nasa.gov) for finding and downloading the data.

## Space Agency Partner Data and Other References

- NOAA GLERL GLSEA lake surface temperature, lake-wide daily averages, 2007–2025 (https://coastwatch.glerl.noaa.gov/satellite-data-products/lake-surface-temperature)
- NOAA NCCOS, Lake Erie Harmful Algal Bloom FAQs: bloom season definition (https://coastalscience.noaa.gov/science-areas/habs/hab-forecasts/lake-erie/faqs/)
- NOAA CoastWatch Great Lakes tutorial: GLSEA file format (https://coastwatch-training.github.io/tutorials/gl-timeseries-surface-temp/python/gl-timeseries-surface-temp.html)
- [usereeah's sources for the basin split and "why it matters"]
- Code libraries: pymannkendall (MIT), pandas and NumPy (BSD-3-Clause), xarray (Apache-2.0), netCDF4 (MIT), Leaflet (BSD-2-Clause), Chart.js (MIT)
- Map tiles: CARTO basemaps, map data © OpenStreetMap contributors (ODbL)
- Fonts: Space Grotesk, Inter, JetBrains Mono (Google Fonts, SIL Open Font License)
- Claude (Anthropic): AI assistant, see "Use of SI"
- Our code: MIT licence, https://github.com/usalmasyeda/Lake-Effect

## 30-second video script

Follows the 2026 guide's timing. About 75 spoken words. Add English subtitles. No images, voices or names of anyone under 18. Add a visible "AI-generated" label to any AI-made visuals.

| Time | On screen | Voiceover |
| --- | --- | --- |
| 0:00–0:02 | Cover slide | "Hi, we're team Lake Effect from Windsor." |
| 0:02–0:05 | A Lake Erie beach photo you took yourself, or slide 2 | "Every summer, algae blooms reach the beaches in our own city." |
| 0:05–0:10 | Slide 3: What? Where? How much? Significant? | "For NASA's Trend Detective challenge, we built Lake Effect: which changes in Lake Erie are real?" |
| 0:10–0:20 | Website: the ranked list, trend map, basin chart | "Our Trend Scanner tests NASA satellite data, keeps only statistically significant change, and maps where it's happening. [Chlorophyll result in one line.]" |
| 0:20–0:30 | Closing slide with the team names | "The same tool works for any lake, so communities everywhere can see what's really changing." |
