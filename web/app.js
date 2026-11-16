// AI-assisted: written with help from AI assistants (Claude, ChatGPT, GitHub Copilot) and reviewed by team Lake Effect.
/*
 * LAKE EFFECT — Multi-Lake Environmental Explorer
 *
 * Five Great Lakes:
 * Erie, Ontario, Huron, Michigan and Superior.
 *
 * Features:
 * - Lake search
 * - NASA chlorophyll concentration maps
 * - NOAA lake surface temperature maps
 * - Long-term statistical trend maps
 * - Interactive satellite pixels
 * - Whole-lake, western and eastern comparisons
 * - Plain-language scientific explanations
 * - Historical yearly charts
 * - Lake stories
 */

const DATA = 'public/data/';
const SCANNER_DISPLAY_ORDER = ['chlorophyll', 'temperature'];

const LAKES = {
  lake_erie: {
    name: 'Lake Erie',
    aliases: ['erie'],
    folder: '',
    splitType: 'basin'
  },
  lake_ontario: {
    name: 'Lake Ontario',
    aliases: ['ontario'],
    folder: 'lakes/lake_ontario/',
    splitType: 'section'
  },
  lake_huron: {
    name: 'Lake Huron',
    aliases: ['huron'],
    folder: 'lakes/lake_huron/',
    splitType: 'section'
  },
  lake_michigan: {
    name: 'Lake Michigan',
    aliases: ['michigan'],
    folder: 'lakes/lake_michigan/',
    splitType: 'section'
  },
  lake_superior: {
    name: 'Lake Superior',
    aliases: ['superior'],
    folder: 'lakes/lake_superior/',
    splitType: 'section'
  }
};

const COLORS = {
  up: '#A8D65C',
  down: '#4FC3C9',
  none: '#8295A1',
  lake: '#EAF4F4',
  west: '#A8D65C',
  east: '#9FD8D4'
};

const CONCENTRATION_SCALE = [
  { min: 0, max: 1, color: '#eff8e8', label: 'Very low' },
  { min: 1, max: 2, color: '#d8edc5', label: 'Low' },
  { min: 2, max: 5, color: '#a8d879', label: 'Moderate' },
  { min: 5, max: 10, color: '#70bd48', label: 'Elevated' },
  { min: 10, max: 20, color: '#35852c', label: 'High' },
  { min: 20, max: Infinity, color: '#14551b', label: 'Very high' }
];

const TEMPERATURE_SCALE = [
  { min: -Infinity, max: 5, color: '#244C9A', label: 'Very cold' },
  { min: 5, max: 10, color: '#3988C9', label: 'Cold' },
  { min: 10, max: 15, color: '#79C8D5', label: 'Cool' },
  { min: 15, max: 20, color: '#F5D76E', label: 'Warm' },
  { min: 20, max: 25, color: '#EF913F', label: 'Very warm' },
  { min: 25, max: Infinity, color: '#C83D35', label: 'Hot' }
];

const REGION_LABEL = {
  lake: 'Whole lake',
  west: 'Western section',
  east: 'Eastern section'
};

const state = {
  lake: 'lake_erie',
  dataBase: DATA,
  scanner: null,
  selected: null,
  chart: null,
  map: null,
  layer: null,
  mapMode: 'concentration',
  mapYears: {
    chlorophyll: 2025,
    temperature: 2025
  },
  yearlyMapCache: new Map(),
  story: [],
  step: 0,
  loadId: 0,
  mapLoadId: 0
};

// ---------- Formatting helpers ----------

const fmt = (value, decimals = 2) =>
  value === null || value === undefined || !Number.isFinite(Number(value))
    ? 'Not available'
    : Number(value).toFixed(decimals);

const signed = (value, decimals = 2) =>
  value === null || value === undefined || !Number.isFinite(Number(value))
    ? 'Not available'
    : (value > 0 ? '+' : '') + Number(value).toFixed(decimals);

const pval = p =>
  p === null || p === undefined
    ? 'Not available'
    : p < 0.001
      ? '< 0.001'
      : Number(p).toFixed(3);

const kind = trend =>
  !trend || !trend.significant
    ? 'none'
    : trend.direction === 'decreasing'
      ? 'down'
      : 'up';

const verdictText = trend =>
  !trend
    ? 'No data available'
    : !trend.significant
      ? 'No clear long-term trend detected'
      : trend.direction === 'decreasing'
        ? 'Decreasing'
        : 'Increasing';

function getRegionLabel(region) {
  if (region === 'lake') return 'Whole lake';

  const type = LAKES[state.lake].splitType;

  if (region === 'west') {
    return type === 'basin' ? 'Western basin' : 'Western section';
  }

  if (region === 'east') {
    return type === 'basin' ? 'Eastern basin' : 'Eastern section';
  }

  return region;
}

// ---------- Data loading ----------

async function getJSON(filename, base = state.dataBase) {
  const response = await fetch(base + filename, {
    cache: 'no-store'
  });

  if (!response.ok) {
    throw new Error(`${filename}: HTTP ${response.status}`);
  }

  return response.json();
}

// ---------- Lake search ----------

function normalizeLakeName(value) {
  return value.trim().toLowerCase().replace(/\s+/g, ' ');
}

function findLake(query) {
  const normalized = normalizeLakeName(query);

  for (const [id, lake] of Object.entries(LAKES)) {
    const shortName = id.replace('lake_', '');

    const acceptedNames = [
      lake.name.toLowerCase(),
      shortName,
      ...lake.aliases
    ];

    if (acceptedNames.includes(normalized)) {
      return id;
    }
  }

  return null;
}

// ---------- Map initialization ----------


function initMap() {
  state.map = L.map('map', {
    scrollWheelZoom: false,
    attributionControl: true
  }).setView([44.5, -82.5], 5);

  // Use OpenStreetMap tiles instead of CARTO.
  // No API key required.
  const baseMap = L.tileLayer(
    'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    {
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 18,
      subdomains: ['a', 'b', 'c']
    }
  );

  baseMap.addTo(state.map);

  setupMapLegend();
  setupMapModeToggle();
  setupMapYearSliders();
}


// ---------- Map legend ----------

function setupMapLegend() {
  const legend = document.querySelector('.map-panel .legend');

  if (legend) {
    legend.id = 'dynamic-map-legend';
    legend.removeAttribute('aria-hidden');
  }
}

function setupMapModeToggle() {
  const toggle = document.getElementById('trend-map-toggle');

  toggle.addEventListener('click', () => {
    const variable = state.scanner?.variables.find(
      item => item.id === state.selected
    );
    const observationMode = variable
      ? getObservationMapMode(variable)
      : 'concentration';

    setMapMode(state.mapMode === 'trends' ? observationMode : 'trends');
  });

  updateMapModeToggle();
}

function setupMapYearSliders() {
  for (const mapType of ['chlorophyll', 'temperature']) {
    const slider = document.getElementById(`${mapType}-year-slider`);
    const output = document.getElementById(`${mapType}-year-output`);

    slider.addEventListener('input', () => {
      state.mapYears[mapType] = Number(slider.value);
      output.value = String(state.mapYears[mapType]);
      output.textContent = String(state.mapYears[mapType]);

      if (state.mapMode === 'trends') return;

      const variable = state.scanner?.variables.find(
        item => item.id === state.selected
      );

      if (variable && getYearlyMapType(variable) === mapType) {
        renderMap(variable);
      }
    });
  }
}

function syncYearSlider(mapType, years) {
  if (!Array.isArray(years) || !years.length) return;
  const slider = document.getElementById(`${mapType}-year-slider`);
  const output = document.getElementById(`${mapType}-year-output`);
  const limits = document.querySelectorAll(
    `#${mapType}-year-control .map-year-limits span`
  );
  const min = Math.min(...years);
  const max = Math.max(...years);

  slider.min = String(min);
  slider.max = String(max);
  state.mapYears[mapType] = Math.min(
    max,
    Math.max(min, state.mapYears[mapType])
  );
  slider.value = String(state.mapYears[mapType]);
  output.value = String(state.mapYears[mapType]);
  output.textContent = String(state.mapYears[mapType]);
  if (limits.length === 2) {
    limits[0].textContent = String(min);
    limits[1].textContent = String(max);
  }
}

function updateMapModeToggle() {
  const toggle = document.getElementById('trend-map-toggle');
  const yearControls = document.getElementById('map-year-controls');

  if (toggle) {
    toggle.setAttribute('aria-checked', String(state.mapMode === 'trends'));
  }

  if (yearControls) {
    yearControls.hidden = state.mapMode === 'trends';
  }

  const variable = state.scanner?.variables.find(
    item => item.id === state.selected
  );
  const selectedMapType = variable
    ? getYearlyMapType(variable)
    : 'chlorophyll';
  document.getElementById('chlorophyll-year-control').hidden =
    selectedMapType !== 'chlorophyll';
  document.getElementById('temperature-year-control').hidden =
    selectedMapType !== 'temperature';
}

function getObservationMapMode(variable) {
  return variable.id.toLowerCase().includes('temperature')
    ? 'temperature'
    : 'concentration';
}

function getYearlyMapType(variable) {
  return getObservationMapMode(variable) === 'temperature'
    ? 'temperature'
    : 'chlorophyll';
}

function setMapMode(mode) {
  if (!['concentration', 'temperature', 'trends'].includes(mode)) {
    return;
  }

  state.mapMode = mode;
  updateMapModeToggle();

  if (!state.scanner || !state.selected) return;

  const variable = state.scanner.variables.find(
    item => item.id === state.selected
  );

  if (variable) {
    renderMap(variable);
  }
}

// ---------- Map legends ----------

function renderConcentrationLegend() {
  const legend = document.getElementById('dynamic-map-legend');

  if (!legend) return;

  legend.innerHTML = '';

  legend.style.cssText = `
    display: block;
    margin-top: 14px;
    color: #C9DDE0;
  `;

  legend.innerHTML = `
    <div style="font-size:12px;margin-bottom:8px">
      <strong>CHLOROPHYLL CONCENTRATION</strong>
      <span style="opacity:0.7">(mg/m³)</span>
    </div>

    <div style="
      height:14px;
      border-radius:4px;
      background:linear-gradient(
        to right,
        #F1F8E9,
        #DCEFC4,
        #B5DE83,
        #78C65A,
        #369B45,
        #176B35
      );
    "></div>

    <div style="
      display:flex;
      justify-content:space-between;
      font-size:11px;
      margin-top:6px;
    ">
      <span>0</span>
      <span>1</span>
      <span>2</span>
      <span>5</span>
      <span>10</span>
      <span>20+</span>
    </div>

    <div style="font-size:11px;margin-top:7px;opacity:0.8">
      Lighter green = lower concentration · Darker green = higher concentration
    </div>
  `;
}

function renderTrendLegend() {
  const legend = document.getElementById('dynamic-map-legend');

  if (!legend) return;

  legend.innerHTML = '';

  const items = [
    {
      color: COLORS.up,
      label: 'Increasing'
    },
    {
      color: COLORS.down,
      label: 'Decreasing'
    },
    {
      color: COLORS.none,
      label: 'No statistically significant trend'
    }
  ];

  items.forEach(item => {
    const entry = document.createElement('span');

    entry.style.cssText = `
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      color: #C9DDE0;
    `;

    const swatch = document.createElement('i');

    swatch.style.cssText = `
      width: 13px;
      height: 13px;
      background: ${item.color};
      display: inline-block;
    `;

    entry.append(swatch, document.createTextNode(item.label));
    legend.appendChild(entry);
  });
}

// ---------- Map helpers ----------

function removeCurrentLayer() {
  if (state.layer && state.map) {
    state.map.removeLayer(state.layer);
    state.layer = null;
  }
}

function zoomToLayer(layer) {
  const bounds = layer.getBounds();

  if (bounds.isValid()) {
    state.map.fitBounds(bounds, {
      padding: [20, 20],
      maxZoom: 9
    });
  }
}

function showMapMessage(message) {
  const hint = document.getElementById('map-hint');

  if (hint) hint.textContent = message;
}

function getCoordinates(lat, lon) {
  const latitude =
    `${Math.abs(lat).toFixed(4)}°${lat >= 0 ? 'N' : 'S'}`;

  const longitude =
    `${Math.abs(lon).toFixed(4)}°${lon >= 0 ? 'E' : 'W'}`;

  return `${latitude}, ${longitude}`;
}

// ---------- Smooth chlorophyll color interpolation ----------

function interpolateColor(value, stops) {
  if (!Number.isFinite(value)) return '#8295A1';

  if (value <= stops[0].value) {
    return stops[0].color;
  }

  if (value >= stops[stops.length - 1].value) {
    return stops[stops.length - 1].color;
  }

  for (let i = 0; i < stops.length - 1; i++) {
    const lower = stops[i];
    const upper = stops[i + 1];

    if (value >= lower.value && value <= upper.value) {
      const ratio =
        (value - lower.value) /
        (upper.value - lower.value);

      const hex = color => [
        parseInt(color.slice(1, 3), 16),
        parseInt(color.slice(3, 5), 16),
        parseInt(color.slice(5, 7), 16)
      ];

      const a = hex(lower.color);
      const b = hex(upper.color);

      const result = a.map((channel, index) =>
        Math.round(channel + (b[index] - channel) * ratio)
      );

      return '#' + result
        .map(channel => channel.toString(16).padStart(2, '0'))
        .join('');
    }
  }

  return stops[stops.length - 1].color;
}

const CHLOROPHYLL_COLOR_STOPS = [
  { value: 0, color: '#F1F8E9' },
  { value: 1, color: '#DCEFC4' },
  { value: 2, color: '#B5DE83' },
  { value: 5, color: '#78C65A' },
  { value: 10, color: '#369B45' },
  { value: 20, color: '#176B35' }
];

function getConcentrationColor(value) {
  return interpolateColor(
    value,
    CHLOROPHYLL_COLOR_STOPS
  );
}

function getConcentrationDescription(value) {
  if (value < 1) return 'Very low concentration';
  if (value < 2) return 'Low concentration';
  if (value < 5) return 'Moderate concentration';
  if (value < 10) return 'Elevated concentration';
  if (value < 20) return 'High concentration';

  return 'Very high concentration';
}

// ---------- Temperature map helpers ----------

const TEMPERATURE_COLOR_STOPS = [
  { value: 5, color: '#2455A4' },
  { value: 10, color: '#398FC5' },
  { value: 15, color: '#78C9D5' },
  { value: 20, color: '#F4D66D' },
  { value: 25, color: '#EE9144' },
  { value: 30, color: '#C83D35' }
];

function getTemperatureColor(value) {
  return interpolateColor(
    value,
    TEMPERATURE_COLOR_STOPS
  );
}

function getTemperatureDescription(value) {
  if (value < 5) return 'Very cold water';
  if (value < 10) return 'Cold water';
  if (value < 15) return 'Cool water';
  if (value < 20) return 'Warm water';
  if (value < 25) return 'Very warm water';

  return 'Hot water';
}

// ---------- Temperature legend ----------

function renderTemperatureLegend() {
  const legend = document.getElementById('dynamic-map-legend');

  if (!legend) return;

  legend.innerHTML = '';

  legend.style.cssText = `
    display: block;
    margin-top: 14px;
    color: #C9DDE0;
  `;

  legend.innerHTML = `
    <div style="font-size:12px;margin-bottom:8px">
      <strong>LAKE SURFACE TEMPERATURE</strong>
      <span style="opacity:0.7">(°C)</span>
    </div>

    <div style="
      height:14px;
      border-radius:4px;
      background:linear-gradient(
        to right,
        #2455A4,
        #398FC5,
        #78C9D5,
        #F4D66D,
        #EE9144,
        #C83D35
      );
    "></div>

    <div style="
      display:flex;
      justify-content:space-between;
      font-size:11px;
      margin-top:6px;
    ">
      <span>5°C</span>
      <span>10°C</span>
      <span>15°C</span>
      <span>20°C</span>
      <span>25°C</span>
      <span>30°C</span>
    </div>

    <div style="font-size:11px;margin-top:7px;opacity:0.8">
      Blue = colder water · Yellow = warmer water · Red = hottest water
    </div>
  `;
}
// ---------- Year-by-year observation map ----------

async function getYearlyMapData(variableId) {
  const filename = `yearly_${variableId}.json`;
  const base = state.dataBase;
  const cacheKey = base + filename;

  if (!state.yearlyMapCache.has(cacheKey)) {
    state.yearlyMapCache.set(cacheKey, getJSON(filename, base));
  }

  try {
    return await state.yearlyMapCache.get(cacheKey);
  } catch (error) {
    state.yearlyMapCache.delete(cacheKey);
    throw error;
  }
}

async function renderYearlyObservationMap(variable) {
  const currentMapLoad = ++state.mapLoadId;
  const mapType = getYearlyMapType(variable);
  const isTemperature = mapType === 'temperature';

  removeCurrentLayer();
  showMapMessage(`Loading ${variable.name} for ${state.mapYears[mapType]}...`);

  try {
    const data = await getYearlyMapData(variable.id);

    if (currentMapLoad !== state.mapLoadId) return;

    syncYearSlider(mapType, data.years);
    const mapYear = state.mapYears[mapType];
    const yearIndex = data.years.indexOf(mapYear);

    if (yearIndex < 0) {
      showMapMessage(`${variable.name} data is not available for ${mapYear}.`);
      return;
    }

    const [cellWidth, cellHeight] = data.cell;
    const layer = L.featureGroup();
    let pixelCount = 0;

    data.pixels.forEach(([lat, lon, values]) => {
      const value = values[yearIndex];

      if (value === null || !Number.isFinite(value)) return;

      const color = isTemperature
        ? getTemperatureColor(value)
        : getConcentrationColor(value);
      const rectangle = L.rectangle(
        [
          [lat - cellHeight / 2, lon - cellWidth / 2],
          [lat + cellHeight / 2, lon + cellWidth / 2]
        ],
        {
          stroke: false,
          fillColor: color,
          fillOpacity: 0.96
        }
      );
      const description = isTemperature
        ? getTemperatureDescription(value)
        : getConcentrationDescription(value);
      const decimals = isTemperature ? 2 : 3;
      const source = isTemperature
        ? 'NOAA GLSEA observation'
        : 'NASA MODIS-Aqua observation';

      rectangle.bindPopup(`
        <div style="min-width:180px">
          <strong>${variable.name}</strong>
          <h3 style="margin:8px 0">${fmt(value, decimals)} ${data.units}</h3>
          <p>${description}</p>
          <hr>
          <small>${source}: ${mapYear}</small>
          <br>
          <small>${data.season}</small>
          <br>
          <small>Location: ${getCoordinates(lat, lon)}</small>
        </div>
      `);

      layer.addLayer(rectangle);
      pixelCount++;
    });

    if (!pixelCount) {
      showMapMessage(`No ${variable.name.toLowerCase()} pixels are available for ${mapYear}.`);
      return;
    }

    state.layer = layer.addTo(state.map);
    zoomToLayer(state.layer);

    if (isTemperature) {
      renderTemperatureLegend();
    } else {
      renderConcentrationLegend();
    }

    const thinnedMessage = data.thinned_to_km
      ? ` (thinned to ~${data.thinned_to_km} km grid spacing)`
      : '';
    showMapMessage(
      `${LAKES[state.lake].name}: ${mapYear} seasonal ` +
      `${isTemperature ? 'water temperatures' : 'chlorophyll measurements'}. ` +
      `${pixelCount.toLocaleString()} pixels shown${thinnedMessage}. ` +
      'Click a square to see its measurement.'
    );
  } catch (error) {
    if (currentMapLoad !== state.mapLoadId) return;

    console.error('Yearly observation map error:', error);
    showMapMessage(
      `Could not load ${variable.name} data for ${state.mapYears[mapType]}. Check its yearly map file.`
    );
  }
}

// ---------- Statistical trend map ----------

async function renderTrendMap(variable) {
  const currentMapLoad = ++state.mapLoadId;

  removeCurrentLayer();

  showMapMessage('Loading long-term environmental trends...');

  try {
    const geo = await getJSON(
      `trend_map_${variable.id}.geojson`
    );

    if (currentMapLoad !== state.mapLoadId) return;

    if (!geo.features || !geo.features.length) {
      showMapMessage('No trend pixels are available.');
      return;
    }

    const significantSlopes = geo.features
      .filter(feature => feature.properties.significant)
      .map(feature =>
        Math.abs(feature.properties.slope_per_decade || 0)
      );

    const maxAbs = Math.max(...significantSlopes, 1e-9);

    state.layer = L.geoJSON(geo, {
      style: feature => {
        const properties = feature.properties;
        const colorKind = kind(properties);

        const strength = colorKind === 'none'
          ? 0
          : Math.min(
              1,
              Math.abs(properties.slope_per_decade) / maxAbs
            );

        return {
          stroke: false,
          fillColor: COLORS[colorKind],
          fillOpacity: colorKind === 'none'
            ? 0.35
            : 0.45 + 0.45 * strength
        };
      },

      onEachFeature: (feature, layer) => {
        const p = feature.properties;

        const explanation = !p.significant
          ? 'The data does not show a statistically significant long-term change at this pixel.'
          : p.direction === 'decreasing'
            ? `${variable.name} has decreased over the observation period.`
            : `${variable.name} has increased over the observation period.`;

        const coordinates = getCoordinates(p.lat, p.lon);

        layer.bindPopup(`
          <div style="min-width:190px">
            <strong>${verdictText(p)}</strong>

            <p>${explanation}</p>

            <hr>

            <strong>Estimated change per decade</strong>

            <h3 style="margin:6px 0">
              ${signed(p.slope_per_decade, 3)}
              ${geo.properties.units}
            </h3>

            <small>Statistical p-value: ${pval(p.p_value)}</small>
            <br>

            <small>Location: ${coordinates}</small>
          </div>
        `);
      }
    }).addTo(state.map);

    zoomToLayer(state.layer);

    renderTrendLegend();

    const significantCount = geo.features.filter(
      feature => feature.properties.significant
    ).length;

    showMapMessage(
      `${geo.properties.name}: ${geo.features.length.toLocaleString()} ` +
      `pixels shown. ${significantCount.toLocaleString()} show a ` +
      'statistically significant trend' +
      (geo.properties.thinned_to_km ? ` (one 1.4 km pixel per ~${geo.properties.thinned_to_km} km square)` : '') +
      '. Click a square to explore.'
    );

  } catch (error) {
    if (currentMapLoad !== state.mapLoadId) return;

    console.error('Trend map error:', error);

    showMapMessage(
      'Trend map is not available for this variable or lake yet.'
    );
  }
}

// ---------- Map dispatcher ----------

async function renderMap(variable) {
  updateMapModeToggle();

  if (state.mapMode === 'trends') {
    await renderTrendMap(variable);
  } else {
    await renderYearlyObservationMap(variable);
  }
}

// ---------- Trend Scanner ----------

function getScannerDisplayVariables(scanner) {
  const orderedIds = [
    ...SCANNER_DISPLAY_ORDER.filter(id =>
      scanner.ranking.includes(id)
    ),
    ...scanner.ranking.filter(id =>
      !SCANNER_DISPLAY_ORDER.includes(id)
    )
  ];

  return orderedIds
    .map(id => scanner.variables.find(item => item.id === id))
    .filter(Boolean);
}

function renderScanner() {
  const scanner = state.scanner;

  document.getElementById('alpha').textContent =
    scanner.alpha;

  document.getElementById('sample-badge').hidden =
    !scanner.sample;

  const list = document.getElementById('scanner-list');

  list.innerHTML = '';

  if (!scanner.variables.length) {
    list.innerHTML =
      '<li class="hint">No variables available for this lake.</li>';
    return;
  }

  getScannerDisplayVariables(scanner).forEach((variable, index) => {
    const { id } = variable;

    const trend =
      variable.trend.lake ||
      Object.values(variable.trend)[0];

    const item = document.createElement('li');
    const button = document.createElement('button');

    button.type = 'button';
    button.className = 'var-btn';
    button.dataset.id = id;
    button.setAttribute('aria-pressed', 'false');

    button.innerHTML = `
      <span class="rank">
        ${String(index + 1).padStart(2, '0')}
      </span>

      <span class="var-name"></span>

      <span class="verdict ${kind(trend)}">
        ${verdictText(trend)}
      </span>

      <span class="var-num"></span>

      <span class="var-src"></span>
    `;

    button.querySelector('.var-name').textContent =
      variable.name;

    button.querySelector('.var-num').textContent =
      `${signed(trend.slope_per_decade)} ${variable.units} per decade`;

    button.querySelector('.var-src').textContent =
      variable.source;

    button.addEventListener('click', () => {
      select(id);
    });

    item.appendChild(button);
    list.appendChild(item);
  });
}

// ---------- Yearly trend chart ----------

function renderChart(variable) {
  const selectedRegion =
    document.getElementById('region-select')?.value || 'all';

  const regions = ['lake', 'west', 'east'].filter(region =>
    variable.series[region] &&
    (selectedRegion === 'all' || selectedRegion === region)
  );

  const datasets = regions.map(region => ({
    label: getRegionLabel(region),
    data: variable.series[region],
    borderColor: COLORS[region],
    backgroundColor: COLORS[region],
    borderWidth: region === 'lake' ? 3 : 2,
    pointRadius: 2,
    pointHoverRadius: 5,
    tension: 0,
    spanGaps: true
  }));

  document.getElementById('chart-hint').textContent =
    `${variable.name}: yearly July–October average, 2003–2025.`;

  if (state.chart) {
    state.chart.destroy();
  }

  state.chart = new Chart(
    document.getElementById('chart'),
    {
      type: 'line',

      data: {
        labels: variable.years,
        datasets
      },

      options: {
        responsive: true,
        maintainAspectRatio: false,

        interaction: {
          mode: 'index',
          intersect: false
        },

        plugins: {
          legend: {
            display: true,
            labels: {
              color: '#C9DDE0',
              boxWidth: 12,
              padding: 15
            }
          },

          tooltip: {
            callbacks: {
              label: context =>
                `${context.dataset.label}: ${fmt(context.parsed.y, 3)} ${variable.units}`
            }
          }
        },

        scales: {
          x: {
            title: {
              display: true,
              text: 'Year',
              color: '#C9DDE0'
            },

            ticks: {
              color: '#C9DDE0',
              maxTicksLimit: 8
            },

            grid: {
              color: 'rgba(159,216,212,0.08)'
            }
          },

          y: {
            title: {
              display: true,
              text: variable.units,
              color: '#C9DDE0'
            },

            ticks: {
              color: '#C9DDE0'
            },

            grid: {
              color: 'rgba(159,216,212,0.08)'
            }
          }
        }
      }
    }
  );

  renderRegionalStats(variable, regions);
}
// ---------- Regional statistics ----------

function renderRegionalStats(variable, regions) {
  const stats = document.getElementById('basin-stats');

  stats.innerHTML = '';

  regions.forEach(region => {
    const trend = variable.trend[region];

    if (!trend) return;

    const div = document.createElement('div');

    div.className = 'stat';
    div.style.borderTopColor = COLORS[kind(trend)];

    const description = !trend.significant
      ? 'No statistically significant trend was detected.'
      : trend.direction === 'decreasing'
        ? `${variable.name} has decreased over the observation period.`
        : `${variable.name} has increased over the observation period.`;

    div.innerHTML = `
      <div class="lbl">
        ${getRegionLabel(region).toUpperCase()}
      </div>

      <div class="val">
        ${verdictText(trend)}
      </div>

      <div class="sub">
        Estimated change: ${signed(trend.slope_per_decade, 3)}
        ${variable.units}/decade
      </div>

      <div class="sub">
        p-value: ${pval(trend.p_value)}
      </div>

      <div class="sub">
        ${trend.n_years} years analyzed
      </div>
    `;

    const explanation = document.createElement('p');

    explanation.className = 'hint';
    explanation.style.marginTop = '8px';
    explanation.style.fontSize = '12px';
    explanation.textContent = description;

    div.appendChild(explanation);
    stats.appendChild(div);
  });
}

// ---------- Select a variable ----------

function select(id) {
  if (!state.scanner) return;

  const variable = state.scanner.variables.find(
    item => item.id === id
  );

  if (!variable) return;

  state.selected = id;

  if (state.mapMode !== 'trends') {
    state.mapMode = getObservationMapMode(variable);
  }
  updateMapModeToggle();

  document.querySelectorAll('.var-btn').forEach(button => {
    button.setAttribute(
      'aria-pressed',
      String(button.dataset.id === id)
    );
  });

  renderChart(variable);
  renderMap(variable);
}

// ---------- Story navigation ----------

function renderStory() {
  const story = state.story[state.step];

  if (!story) return;

  document.getElementById('story-count').textContent =
    `${state.step + 1} / ${state.story.length}`;

  const body = document.getElementById('story-body');

  body.innerHTML = '<h3></h3><p></p>';

  body.querySelector('h3').textContent = story.title;
  body.querySelector('p').textContent = story.text;

  document.getElementById('story-prev').disabled =
    state.step === 0;

  document.getElementById('story-next').disabled =
    state.step === state.story.length - 1;

  if (story.variable && story.variable !== state.selected) {
    select(story.variable);
  }
}

function setupStoryNavigation() {
  document.getElementById('story-prev')
    .addEventListener('click', () => {
      if (state.step > 0) {
        state.step--;
        renderStory();
      }
    });

  document.getElementById('story-next')
    .addEventListener('click', () => {
      if (state.step < state.story.length - 1) {
        state.step++;
        renderStory();
      }
    });
}

// ---------- Load selected lake ----------

async function loadLake(lakeId) {
  const lake = LAKES[lakeId];

  if (!lake) return;

  const loadId = ++state.loadId;

  state.lake = lakeId;
  state.dataBase = DATA + lake.folder;

  state.scanner = null;
  state.selected = null;
  state.story = [];
  state.step = 0;

  state.mapLoadId++;

  document.querySelector('.region').textContent =
    lake.name;

  const input = document.getElementById('lake-search-input');

  input.value = lake.name;

  const message = document.getElementById('lake-search-message');

  message.textContent =
    `Loading NASA observations for ${lake.name}...`;

  document.getElementById('scanner-list').innerHTML =
    '<li class="hint">Loading lake data...</li>';

  showMapMessage('Loading satellite data...');

  document.getElementById('chart-hint').textContent =
    'Loading yearly observations...';

  document.getElementById('basin-stats').innerHTML = '';

  if (state.chart) {
    state.chart.destroy();
    state.chart = null;
  }

  removeCurrentLayer();

  document.querySelector('.story').hidden = true;

  try {
    const scanner = await getJSON('scanner.json');

    if (loadId !== state.loadId) return;

    state.scanner = scanner;

    renderScanner();

    const [firstVariable] = getScannerDisplayVariables(scanner);

    if (firstVariable) {
      select(firstVariable.id);
    } else {
      document.getElementById('scanner-list').innerHTML =
        '<li class="hint">No variables available.</li>';
    }

    try {
      const storyData = await getJSON('story.json');

      if (loadId !== state.loadId) return;

      state.story = storyData.steps || [];

      if (state.story.length) {
        document.querySelector('.story').hidden = false;
        renderStory();
      }

    } catch {
      state.story = [];
      document.querySelector('.story').hidden = true;
    }

    message.textContent =
      `Showing ${lake.name}: NASA MODIS-Aqua observations, 2003–2025.`;

    setTimeout(() => {
      if (loadId === state.loadId && state.map) {
        state.map.invalidateSize();
      }
    }, 100);

  } catch (error) {
    if (loadId !== state.loadId) return;

    console.error('Lake loading error:', error);

    message.textContent =
      `Unable to load ${lake.name}. Please check its data files.`;

    document.getElementById('scanner-list').innerHTML =
      '<li class="hint">Could not load this lake\'s scanner data.</li>';

    showMapMessage('Lake data could not be loaded.');
  }
}

// ---------- Lake search ----------

function setupLakeSearch() {
  const input = document.getElementById('lake-search-input');
  const button = document.getElementById('lake-search-button');
  const message = document.getElementById('lake-search-message');

  function searchLake() {
    const query = input.value.trim();

    if (!query) {
      message.textContent = 'Please enter a lake name.';
      return;
    }

    const lakeId = findLake(query);

    if (!lakeId) {
      message.textContent =
        'Lake not found. Available lakes: Erie, Ontario, Huron, Michigan and Superior.';
      return;
    }

    loadLake(lakeId);
  }

  button.addEventListener('click', searchLake);

  input.addEventListener('keydown', event => {
    if (event.key === 'Enter') {
      event.preventDefault();
      searchLake();
    }
  });
}

// ---------- Region filter ----------

function setupRegionFilter() {
  document.getElementById('region-select')
    ?.addEventListener('change', () => {
      if (!state.scanner || !state.selected) return;

      const variable = state.scanner.variables.find(
        item => item.id === state.selected
      );

      if (variable) {
        renderChart(variable);
      }
    });
}

// ---------- Initialize application ----------

async function init() {
  initMap();

  setupLakeSearch();
  setupStoryNavigation();
  setupRegionFilter();

  await loadLake('lake_erie');
}

init();