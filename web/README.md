# Web app

The interactive Lake Effect tool: one page, plain HTML, CSS and JavaScript. No build step.

- `index.html`: page layout
- `style.css`: Lake Effect colours and fonts
- `app.js`: loads the data and draws the scanner list, map (Leaflet), chart (Chart.js) and story
- `public/data/`: the only files the page reads (shapes in [../docs/data-format.md](../docs/data-format.md))
  - `scanner.json`: ranked variables, series and trend numbers
  - `trend_map_<variable>.geojson`: per-pixel trend cells for the map
  - `story.json`: the story steps (edit the text here)

## Run it locally

```bash
cd web
python -m http.server 8000
```

Then open http://localhost:8000. Opening `index.html` directly from the folder won't load the data; use the server.

## Publish

Every push to `main` publishes `web/` to GitHub Pages via `.github/workflows/pages.yml`.
One-time setup: repo **Settings > Pages > Source: GitHub Actions**.

Public link: https://usalmasyeda.github.io/Lake-Effect/

## A map for another variable

The map works for any variable that has a `trend_map_<id>.geojson`. Variables without one still show in the list and chart.
