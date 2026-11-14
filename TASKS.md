# Tasks

Each task is also a GitHub Issue with an owner. Must-haves are done by **Sunday 1:00 PM** (feature freeze). Stretch goals only after that.

## Captain: design, story, pitch (Salma)

- [ ] Post the design details (colours, fonts) in #design and in `docs/data-format.md`
- [ ] Write the Lake Erie story in `docs/story.md` with the science lead (3 to 4 short steps)
- [ ] Design the web app layout: scanner list, map, chart, story panel (share a mockup with web)
- [ ] Build the slides (about 7)
- [ ] Script and record the 30-second pitch video
- [ ] Write the project summary and submit on the Space Apps Project tab

## Web developer (Nishant)

- [ ] Set up the web app in `web/` and deploy a public link (GitHub Pages or Vercel)
- [ ] Trend Scanner panel: ranked list from `scanner.json`, with direction, slope per decade and p-value
- [ ] Trend map: draw `trend_map_chlorophyll.geojson` on a Leaflet map, coloured as in `docs/data-format.md`
- [ ] Time-series chart: lake, west and east series for the selected variable
- [ ] "Sample data" badge while files are marked `sample: true`
- [ ] Story panel that steps through `docs/story.md`
- [ ] Stretch: variable switcher for the map, year slider, draw-a-box trend

## Data lead

- [ ] Get a NASA Earthdata login and download MODIS-Aqua chlorophyll for Lake Erie (yearly or monthly, 2003 to now)
- [ ] Build `data/processed/series/chlorophyll.csv` (columns: year, lake, west, east) and `chlorophyll_yearly.nc` (year, lat, lon)
- [ ] Run `trend_scanner.py` on the real chlorophyll data and push the outputs
- [ ] Add lake surface temperature (GLSEA) the same way
- [ ] Add MERRA-2 precipitation the same way
- [ ] Write the download and processing steps in `data/README.md` so judges can reproduce them

## Science lead

- [ ] Confirm the west/east basin split (suggested: west of 82.5° W is the western basin) and the bloom season months to average
- [ ] Check the real results make scientific sense; flag anything odd
- [ ] Write the "why it matters" text: drinking water, fishing, Windsor-Essex
- [ ] Collect 3 to 5 trusted sources on Lake Erie blooms for the story and README
- [ ] Review every claim in the story, slides and summary before submission

## Fifth role: QA, docs and demo support

- [ ] Help the data lead with downloads (temperature or precipitation)
- [ ] Keep `README.md` current: what it is, how to run it, data sources, team
- [ ] Test the public link on phone and laptop; report bugs as Issues
- [ ] Take screenshots and a backup screen recording of the demo
- [ ] Keep `docs/handoffs.md` tidy and remind people to post hand-offs
