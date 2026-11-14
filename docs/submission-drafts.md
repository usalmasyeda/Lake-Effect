# Submission drafts (edit freely)

Lines in [brackets] wait for Mehak's chlorophyll results. Check every claim with usereeah before submitting.

## 30-second pitch video

About 75 spoken words. Screen recordings of the website work best; never show the faces, names or voices of anyone under 18.

| Time | On screen | Voiceover |
| --- | --- | --- |
| 0–5 s | Cover slide: LAKE EFFECT and the satellite lens | "Every summer, harmful algae blooms return to Lake Erie, right in Windsor's backyard." |
| 5–12 s | Slide 3: What? Where? How much? Significant? | "NASA satellites have watched the lake for over twenty years. But with so many variables, which changes are real?" |
| 12–20 s | Website: click through the ranked Trend Scanner list | "Our Trend Scanner tests every variable, and only calls a change real when the statistics say so." |
| 20–26 s | Website: the trend map, then the basin chart | "[Chlorophyll result, e.g. In the western basin, algae rose __ per decade, a significant trend.]" |
| 26–30 s | Closing slide with the team names | "Lake Effect. Detecting real change, from space." |

## Project summary (about 150 words)

Lake Effect is a web tool for NASA's "Be an Earth System Trend Detective" challenge. It answers four questions: what is changing, where, how much, and is the change significant? Pick a lake, and our Trend Scanner runs a Mann-Kendall trend test with Sen's slope on every available variable, ranks them by real change, and maps where change happens, pixel by pixel. A change only counts when the test says it is significant (p < 0.05), so the tool separates signal from year-to-year noise.

We start with Lake Erie, where harmful algal blooms return every summer, typically July to October (NOAA). So far, bloom-season surface temperature rose about 0.44 °C per decade from 2007 to 2025, but the trend is not yet significant (p = 0.069). [Chlorophyll result: which basin, how much, significant or not.]

The same tool works for any lake and any gridded Earth science variable.

## How we used NASA and other data

- **Chlorophyll-a:** NASA MODIS-Aqua, via the NASA Ocean Biology DAAC (https://www.earthdata.nasa.gov/centers/ob-daac) [Mehak: confirm the exact product and route used]
- **Lake surface temperature:** NOAA GLERL GLSEA lake-wide daily averages, 2007–2025 (https://coastwatch.glerl.noaa.gov/satellite-data-products/lake-surface-temperature)
- **Precipitation (model):** NASA MERRA-2, M2TMNXFLX [only if added]
- **Bloom season definition:** NOAA NCCOS Lake Erie HAB FAQs (https://coastalscience.noaa.gov/science-areas/habs/hab-forecasts/lake-erie/faqs/)

## Links

- Website: https://usalmasyeda.github.io/Lake-Effect/
- Code: https://github.com/usalmasyeda/Lake-Effect
