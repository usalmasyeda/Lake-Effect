# Tasks

Each task is also a GitHub Issue with an owner. Must-haves are done by **Sunday 1:00 PM** (feature freeze). Stretch goals only after that.

| Person | Role |
| --- | --- |
| Salma | Captain: design, story, pitch, plus lake temperature data |
| Mehak | Data lead (chlorophyll + Trend Scanner), plus design support |
| usereeah | Science lead: research and fact-checking |
| Faria | Web developer |
| Yumna | Testing and design support |

## Salma: captain, design, story, data support

- [ ] Post the design details (colours, fonts) in #design
- [ ] Sketch the web app layout for Faria: scanner list, map, chart, story panel
- [ ] Download lake surface temperature (NOAA GLSEA) and build `data/processed/series/lake_temperature.csv`
- [ ] Write the Lake Erie story in `docs/story.md` with usereeah (3 to 4 short steps)
- [ ] Build the slides (about 7) with Yumna
- [ ] Script and record the 30-second pitch video
- [ ] Write the project summary and submit on the Space Apps Project tab

## Mehak: data lead

- [ ] Get a NASA Earthdata login and download MODIS-Aqua chlorophyll for Lake Erie, 2003 to now
- [ ] Build `data/processed/series/chlorophyll.csv` (columns: year, lake, west, east) and `data/processed/chlorophyll_yearly.nc` (year, lat, lon)
- [ ] Run `trend_scanner.py` on the real data and push the outputs to `web/public/data/`
- [ ] Stretch: add MERRA-2 precipitation the same way
- [ ] Write the download and processing steps in `data/README.md`
- [ ] Help Salma with map colours and the data visuals in the slides

## usereeah: science lead

- [ ] Confirm the west/east basin split (suggested: west of 82.5° W is the western basin) and which months count as bloom season
- [ ] Collect 3 to 5 trusted sources on Lake Erie algal blooms
- [ ] Write the "why it matters" text: drinking water, fishing, Windsor-Essex
- [ ] Check the real results make scientific sense and flag anything odd
- [ ] Review every claim in the story, slides and summary before submission

## Faria: web developer

- [ ] Set up the web app in `web/` (React + Leaflet, or plain HTML + Leaflet if faster) and deploy a public link on GitHub Pages
- [ ] Trend Scanner panel: ranked list from `scanner.json`, with direction, slope per decade and p-value
- [ ] Trend map: draw `trend_map_chlorophyll.geojson` on a Leaflet map, coloured as in `docs/data-format.md`
- [ ] Time-series chart: lake, west and east series for the selected variable
- [ ] "Sample data" badge while files are marked `sample: true`
- [ ] Story panel that steps through `docs/story.md`
- [ ] Stretch: variable switcher for the map, year slider

## Yumna: testing and design support

- [ ] Test the public link on phone and laptop as soon as it's up; report bugs as GitHub Issues
- [ ] Help Salma build the slides
- [ ] Take screenshots and a backup screen recording of the demo
- [ ] Keep `README.md` current: what it is, how to run it, data sources, team
- [ ] Remind everyone to post hand-off notes in `docs/handoffs.md` and Discord
