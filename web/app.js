// AI-assisted: written with Claude (an AI assistant) and reviewed by team Lake Effect.
// Lake Effect web app. Reads only the files in public/data/ (see docs/data-format.md).
const DATA = 'public/data/';
const COLORS = { up: '#A8D65C', down: '#4FC3C9', none: '#6B7F8C', lake: '#EAF4F4', west: '#A8D65C', east: '#9FD8D4' };
const REGION_LABEL = { lake: 'Whole lake', west: 'Western basin', east: 'Central + eastern basins' };

const state = { scanner: null, selected: null, chart: null, map: null, layer: null, story: [], step: 0 };

const fmt = (v, d = 2) => (v === null || v === undefined ? 'n/a' : Number(v).toFixed(d));
const signed = (v, d = 2) => (v === null || v === undefined ? 'n/a' : (v > 0 ? '+' : '') + Number(v).toFixed(d));
const pval = p => (p === null || p === undefined ? 'n/a' : p < 0.001 ? '< 0.001' : p.toFixed(3));
const kind = t => (!t || !t.significant ? 'none' : t.direction === 'decreasing' ? 'down' : 'up');
const verdictText = t => (!t ? 'No data' : !t.significant ? 'No real change' : t.direction === 'decreasing' ? 'Falling' : 'Rising');

async function getJSON(name) {
  const res = await fetch(DATA + name, { cache: 'no-store' });
  if (!res.ok) throw new Error(`${name}: ${res.status}`);
  return res.json();
}

// ---------- Trend Scanner list ----------
function renderScanner() {
  const s = state.scanner;
  document.getElementById('alpha').textContent = s.alpha;
  document.getElementById('sample-badge').hidden = !s.sample;
  const list = document.getElementById('scanner-list');
  list.innerHTML = '';
  s.ranking.forEach((id, i) => {
    const v = s.variables.find(x => x.id === id);
    const t = v.trend.lake || Object.values(v.trend)[0];
    const li = document.createElement('li');
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'var-btn';
    btn.dataset.id = id;
    btn.setAttribute('aria-pressed', 'false');
    btn.innerHTML = `
      <span class="rank">${String(i + 1).padStart(2, '0')}</span>
      <span class="var-name"></span>
      <span class="verdict ${kind(t)}">${verdictText(t)}</span>
      <span class="var-num">${signed(t.slope_per_decade)} ${v.units} per decade · p ${pval(t.p_value)}</span>
      <span class="var-src"></span>`;
    btn.querySelector('.var-name').textContent = v.name;
    btn.querySelector('.var-src').textContent = v.source;
    btn.addEventListener('click', () => select(id));
    li.appendChild(btn);
    list.appendChild(li);
  });
}

// ---------- Map ----------
function initMap() {
  state.map = L.map('map', { scrollWheelZoom: false, attributionControl: true })
    .fitBounds([[41.35, -83.6], [42.95, -78.8]]);
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap contributors &copy; CARTO', subdomains: 'abcd', maxZoom: 12,
  }).addTo(state.map);
}

async function renderMap(v) {
  if (state.layer) { state.map.removeLayer(state.layer); state.layer = null; }
  const hint = document.getElementById('map-hint');
  let geo;
  try { geo = await getJSON(`trend_map_${v.id}.geojson`); }
  catch { hint.textContent = `No map yet for ${v.name}. The list and chart still work.`; return; }
  hint.textContent = `${geo.properties.name}: change per decade, pixel by pixel.`;
  const maxAbs = Math.max(...geo.features.filter(f => f.properties.significant)
    .map(f => Math.abs(f.properties.slope_per_decade || 0)), 1e-9);
  state.layer = L.geoJSON(geo, {
    style: f => {
      const p = f.properties, k = kind(p);
      const strength = k === 'none' ? 0 : Math.min(1, Math.abs(p.slope_per_decade) / maxAbs);
      return { stroke: false, fillColor: COLORS[k], fillOpacity: k === 'none' ? 0.25 : 0.35 + 0.55 * strength };
    },
    onEachFeature: (f, layer) => {
      const p = f.properties;
      layer.bindPopup(`<strong>${verdictText(p)}</strong><br>${signed(p.slope_per_decade)} ${geo.properties.units} per decade<br>p = ${pval(p.p_value)}<br>${p.lat}°N, ${Math.abs(p.lon)}°W`);
    },
  }).addTo(state.map);
}

// ---------- Chart ----------
function renderChart(v) {
  const regions = ['lake', 'west', 'east'].filter(r => v.series[r]);
  const datasets = regions.map(r => ({
    label: REGION_LABEL[r], data: v.series[r], borderColor: COLORS[r], backgroundColor: COLORS[r],
    borderWidth: r === 'lake' ? 3 : 2, pointRadius: 0, tension: 0.25, spanGaps: true,
  }));
  document.getElementById('chart-hint').textContent = `${v.name}, ${v.units}, yearly`;
  if (state.chart) state.chart.destroy();
  state.chart = new Chart(document.getElementById('chart'), {
    type: 'line',
    data: { labels: v.years, datasets },
    options: {
      responsive: true, maintainAspectRatio: false, interaction: { mode: 'index', intersect: false },
      plugins: { legend: { labels: { color: '#C9DDE0', boxWidth: 12 } } },
      scales: {
        x: { ticks: { color: '#C9DDE0', maxTicksLimit: 8 }, grid: { color: 'rgba(159,216,212,0.08)' } },
        y: { ticks: { color: '#C9DDE0' }, grid: { color: 'rgba(159,216,212,0.08)' },
             title: { display: true, text: v.units, color: '#C9DDE0' } },
      },
    },
  });
  const stats = document.getElementById('basin-stats');
  stats.innerHTML = '';
  regions.forEach(r => {
    const t = v.trend[r];
    const div = document.createElement('div');
    div.className = 'stat';
    div.style.borderTopColor = COLORS[kind(t)];
    div.innerHTML = `<div class="lbl">${REGION_LABEL[r].toUpperCase()}</div>
      <div class="val">${verdictText(t)}</div>
      <div class="sub">${signed(t.slope_per_decade)} ${v.units}/decade · p ${pval(t.p_value)}</div>`;
    stats.appendChild(div);
  });
}

function select(id) {
  const v = state.scanner.variables.find(x => x.id === id);
  if (!v) return;
  state.selected = id;
  document.querySelectorAll('.var-btn').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.id === id)));
  renderChart(v);
  renderMap(v);
}

// ---------- Story ----------
function renderStory() {
  const s = state.story[state.step];
  if (!s) return;
  document.getElementById('story-count').textContent = `${state.step + 1} / ${state.story.length}`;
  const body = document.getElementById('story-body');
  body.innerHTML = '<h3></h3><p></p>';
  body.querySelector('h3').textContent = s.title;
  body.querySelector('p').textContent = s.text;
  document.getElementById('story-prev').disabled = state.step === 0;
  document.getElementById('story-next').disabled = state.step === state.story.length - 1;
  if (s.variable && s.variable !== state.selected) select(s.variable);
}

async function init() {
  initMap();
  try {
    state.scanner = await getJSON('scanner.json');
  } catch (e) {
    document.getElementById('scanner-list').innerHTML = '<li class="hint">Could not load scanner.json. Run the Trend Scanner first.</li>';
    return;
  }
  renderScanner();
  select(state.scanner.ranking[0]);
  try {
    state.story = (await getJSON('story.json')).steps || [];
  } catch { state.story = []; }
  if (state.story.length) {
    document.getElementById('story-prev').addEventListener('click', () => { state.step--; renderStory(); });
    document.getElementById('story-next').addEventListener('click', () => { state.step++; renderStory(); });
    renderStory();
  } else {
    document.querySelector('.story').hidden = true;
  }
}

init();
