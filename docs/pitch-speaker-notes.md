# Lake Effect pitch: speaker notes

Script for the 7-slide deck (the 2026 limit is 7 slides including the title). The 30-second video script is in `submission-drafts.md`. Lines in [brackets] are still to be filled in.

| # | Slide | What to say |
| --- | --- | --- |
| 1 | **Cover: Lake Effect** | Hi, we're Lake Effect. We built a tool that scans NASA satellite data for real environmental change, starting with Lake Erie, right here in Windsor's backyard. |
| 2 | **The problem** | Every summer, toxic algae blooms return to Lake Erie. NOAA says the typical season runs July to October, the blooms need warm water, and the Maumee River is their main nutrient source. And here in Windsor-Essex, the Health Unit warns blooms can affect our drinking water and health. |
| 3 | **The challenge** | The challenge asks four questions. The hardest is the last one: is a change real, or just year-to-year noise? Most tools stop at drawing a line. Ours tests it. |
| 4 | **Our solution** | Pick a lake, and the scanner runs a standard trend test on every variable at once. It only calls something a trend when the test says it's significant, then ranks the results and maps where the change is happening. |
| 5 | **The website** | This is the live site. The scanner ranks every variable. Click one and the map shows where it changed, and the chart shows how it changed over time in each basin. |
| 6 | **Finding 1: algae (chlorophyll)** | NASA's MODIS-Aqua satellite has measured chlorophyll, a sign of algae, over Lake Erie for more than twenty years. Our scanner finds it rising about 1.55 mg/m³ per decade, significant in the western basin and in the central and eastern basins. Over 80% of the lake's pixels show a significant increase, and none a decrease. It stays significant even without the two highest recent years. |
| 7 | **Finding 2: temperature** | Lake Erie's bloom-season water temperature drifted up about 0.44 °C per decade, but the test says it isn't significant yet: the swings from one year to the next are bigger than the trend. We checked three month windows and got the same answer. Our scanner marks this as "no significant trend", which is exactly what it's built to do: tell signal from noise. |
| | **Close (end of slide 7)** | Lake Effect doesn't just draw lines on a chart. It tells you which changes are real, ranks them, and shows where they happen. We started with Lake Erie, and the same tool works for any lake. Thank you! |

## Facts used on the slides and their sources

- Typical bloom season July to October; blooms need water of at least 65 °F; the Maumee River is the main nutrient source: [NOAA NCCOS, Lake Erie HAB FAQs](https://coastalscience.noaa.gov/science-areas/habs/hab-forecasts/lake-erie/faqs/)
- Temperature result: [docs/findings/lake-temperature-finding.pdf](findings/lake-temperature-finding.pdf)
