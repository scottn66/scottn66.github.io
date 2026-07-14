/* The Shape of People to Come — page runtime.
   Everything renders from demographics/data/*.json (built by
   scripts/build_demographics_data.py); Figure 1 is baked so the first
   screen needs no fetch. Plotly + KaTeX are self-hosted in vendor/. */
'use strict';

/* ---------------------------------------------------------------- tokens */
// Validated categorical palette; color follows the country in every figure.
const CC = {
  USA: '#1F4E9E', CHN: '#B83A2E', DEU: '#A8861D', NGA: '#2F7A4A',
  JPN: '#6A4FA3', KOR: '#0782AF', IND: '#C2632F',
};
const INK = '#1E1E1E', MUTED = '#555', RULE = '#E5E5EA', PAPER = '#FFFFFF';
const GOOD_SOFT = '#DEEFE0', WARN_SOFT = '#F4DCDA';
const ACCENT = '#1F4E9E', WARN = '#B83A2E', ORANGE = '#D97036';
const FONT = {
  family: '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Helvetica,Arial,sans-serif',
  color: INK, size: 12.5,
};
const BASE = {
  paper_bgcolor: PAPER, plot_bgcolor: PAPER, font: FONT,
  margin: { l: 46, r: 18, t: 28, b: 38 },
  hoverlabel: { bgcolor: '#1b2330', font: { color: '#fff', size: 12 }, bordercolor: '#1b2330' },
};
const NOPAD = { displayModeBar: false, responsive: true };

// Plotly's `responsive` flag only reacts to window `resize` events; pane
// drags and CSS reflows change a figure's box without firing one. Watch each
// figure's own container and resize the plot to match. Figures that carry a
// data-hratio keep height proportional to width (clamped to hmin/hmax) so
// they never flatten on wide screens.
function plotWidth(el) {
  const cs = getComputedStyle(el);
  return el.clientWidth - (parseFloat(cs.paddingLeft) || 0) - (parseFloat(cs.paddingRight) || 0);
}
const RESIZER = new ResizeObserver(entries => {
  for (const e of entries) {
    const el = e.target;
    if (!el.classList.contains('js-plotly-plot') || !el.offsetWidth) continue;
    const ratio = parseFloat(el.dataset.hratio);
    if (ratio) {
      const w = plotWidth(el);
      const target = Math.round(Math.min(Math.max(w * ratio, +el.dataset.hmin || 0), +el.dataset.hmax || 1e4));
      const cur = el._fullLayout || {};
      if (Math.abs((cur.width || 0) - w) > 2 || Math.abs((cur.height || 0) - target) > 2)
        Plotly.relayout(el, { width: w, height: target });
    } else {
      Plotly.Plots.resize(el);
    }
  }
});

// Declare a figure's proportions: height = clamp(width * ratio, hmin, hmax).
// Returns the height for the initial draw; RESIZER maintains it afterwards.
function sized(el, ratio, hmin, hmax) {
  el.dataset.hratio = ratio; el.dataset.hmin = hmin; el.dataset.hmax = hmax;
  return Math.round(Math.min(Math.max(plotWidth(el) * ratio, hmin), hmax));
}
const AGE_LABELS = ['0-4','5-9','10-14','15-19','20-24','25-29','30-34','35-39','40-44','45-49',
  '50-54','55-59','60-64','65-69','70-74','75-79','80-84','85-89','90-94','95-99','100+'];

const grid = (ax) => Object.assign({ gridcolor: RULE, zerolinecolor: RULE, linecolor: RULE, tickcolor: RULE }, ax);

// Plotly.newPlot leaves pre-existing children (our "loading…" placeholders) in
// place; clear the container first so figures sit alone in their card.
function mount(id) {
  const el = document.getElementById(id);
  el.innerHTML = '';
  RESIZER.observe(el);
  return el;
}

/* ------------------------------------------------- Fig 1 (baked, no fetch) */
// % of total population per 5-year bin, male/female. From WPP 2024 medium.
const SHAPES = {
  'Nigeria 2025': { m: [7.27,6.7,6.46,5.78,4.94,3.93,3.25,2.75,2.4,2.02,1.56,1.18,0.89,0.64,0.42,0.24,0.12,0.04,0.01,0,0],
                    f: [7.08,6.51,6.25,5.57,4.76,3.8,3.14,2.67,2.34,1.98,1.56,1.2,0.93,0.69,0.47,0.27,0.13,0.04,0.01,0,0],
                    tag: 'pyramid' },
  'United States 2025': { m: [2.74,2.87,3.1,3.37,3.44,3.37,3.53,3.6,3.44,3.19,2.97,3.01,3.06,2.82,2.28,1.72,1,0.49,0.2,0.05,0.01],
                          f: [2.61,2.74,2.93,3.18,3.24,3.15,3.29,3.37,3.25,3.04,2.86,2.95,3.09,2.98,2.54,2.02,1.29,0.74,0.36,0.11,0.02],
                          tag: 'column' },
  'Japan 2050': { m: [1.84,1.94,1.96,1.96,2.15,2.28,2.54,2.8,2.93,2.86,2.74,2.72,2.88,3.16,3.46,3.82,2.91,1.96,1.01,0.36,0.08],
                  f: [1.76,1.86,1.89,1.9,2.12,2.26,2.51,2.75,2.86,2.78,2.66,2.66,2.86,3.25,3.71,4.31,3.52,2.78,1.88,0.98,0.33],
                  tag: 'urn' },
};

function drawShapes() {
  const names = Object.keys(SHAPES);
  const traces = [], annotations = [], layoutAxes = {};
  // one full-width pyramid per row, top to bottom
  const rows = [[0.72, 1], [0.36, 0.64], [0, 0.28]];
  names.forEach((name, i) => {
    const s = SHAPES[name];
    const xa = i === 0 ? 'x' : 'x' + (i + 1);
    const ya = i === 0 ? 'y' : 'y' + (i + 1);
    traces.push({
      type: 'bar', orientation: 'h', xaxis: xa, yaxis: ya,
      x: s.m.map(v => -v), y: AGE_LABELS, marker: { color: ACCENT }, width: 0.82,
      customdata: s.m, showlegend: i === 0, name: 'Male', legendgroup: 'm',
      hovertemplate: `<b>${name}</b> · %{y}<br>male %{customdata}%<extra></extra>`,
    });
    traces.push({
      type: 'bar', orientation: 'h', xaxis: xa, yaxis: ya,
      x: s.f, y: AGE_LABELS, marker: { color: ORANGE }, width: 0.82,
      showlegend: i === 0, name: 'Female', legendgroup: 'f',
      hovertemplate: `<b>${name}</b> · %{y}<br>female %{x}%<extra></extra>`,
    });
    layoutAxes['xaxis' + (i ? i + 1 : '')] = Object.assign(
      grid({ range: [-7.8, 7.8], tickvals: [-6, -4, -2, 0, 2, 4, 6],
        ticktext: ['6%', '4%', '2%', '0', '2%', '4%', '6%'],
        tickfont: { size: 12, color: MUTED }, fixedrange: true }),
      { domain: [0, 1], anchor: ya });
    layoutAxes['yaxis' + (i ? i + 1 : '')] = grid({
      domain: rows[i], anchor: xa, dtick: 2,
      tickfont: { size: 12, color: MUTED }, fixedrange: true });
    annotations.push({
      text: `<b>${name}</b> · <span style="color:${MUTED}">${s.tag}</span>`,
      xref: 'paper', yref: ya + ' domain', x: 0.5, y: 1.1, showarrow: false,
      font: { size: 14 }, align: 'center',
    });
  });
  const layout = Object.assign({}, BASE, layoutAxes, {
    barmode: 'overlay', bargap: 0.06, height: 1150,
    margin: { l: 56, r: 12, t: 56, b: 34 },
    legend: { orientation: 'h', x: 1, xanchor: 'right', y: 1.03 },
    annotations,
  });
  const el = mount('fig-shapes');
  layout.height = sized(el, 1.6, 1250, 2400);
  Plotly.newPlot(el, traces, layout, NOPAD);
}

/* -------------------------------------------------- Fig 3 (stylized, baked) */
// KEEP IN SYNC with stylized_profiles() in scripts/build_demographics_data.py:
// these same curves are the weights of the shipped economic support ratio.
function drawLifecycle() {
  const ages = [], yl = [], cons = [];
  for (let a = 0; a <= 90; a += 1) {
    ages.push(a);
    // stylized NTA-average shapes, % of peak labor income
    const ramp = 100 / (1 + Math.exp(-(a - 30) / 5.5));       // rise to peak ~48
    const fade = 1 / (1 + Math.exp((a - 61) / 4.5));          // exit ramp
    yl.push(Math.max(0, ramp * fade * 1.19 - (a < 15 ? 100 : 0)));
    let c = 34 + 24 / (1 + Math.exp(-(a - 10) / 4));          // childhood rise (education)
    c += 12 / (1 + Math.exp(-(a - 22) / 3));                  // adult plateau
    c += 10 / (1 + Math.exp(-(a - 74) / 6));                  // late-life health tilt
    cons.push(c);
  }
  // region fills between the curves, split at crossovers
  const traces = [];
  let start = 0;
  const sign = i => Math.sign(cons[i] - yl[i]);
  for (let i = 1; i <= ages.length; i++) {
    if (i === ages.length || sign(i) !== sign(start)) {
      const end = Math.min(i + 1, ages.length);
      const deficit = sign(start) >= 0;
      traces.push({ x: ages.slice(start, end), y: yl.slice(start, end), type: 'scatter', mode: 'lines',
        line: { width: 0 }, hoverinfo: 'skip', showlegend: false });
      traces.push({ x: ages.slice(start, end), y: cons.slice(start, end), type: 'scatter', mode: 'lines',
        fill: 'tonexty', fillcolor: deficit ? WARN_SOFT : GOOD_SOFT,
        line: { width: 0 }, hoverinfo: 'skip', showlegend: false });
      start = i;
    }
  }
  traces.push({ x: ages, y: yl, name: 'Labor income yₗ(a)', type: 'scatter', mode: 'lines',
    line: { color: ACCENT, width: 2.4 },
    hovertemplate: 'age %{x} · income %{y:.0f}<extra></extra>' });
  traces.push({ x: ages, y: cons, name: 'Consumption c(a)', type: 'scatter', mode: 'lines',
    line: { color: ORANGE, width: 2.4 },
    hovertemplate: 'age %{x} · consumption %{y:.0f}<extra></extra>' });
  const layout = Object.assign({}, BASE, {
    height: 480,
    legend: { orientation: 'h', x: 0.5, xanchor: 'center', y: 1.14 },
    xaxis: grid({ title: { text: 'age', font: { size: 13, color: MUTED } }, fixedrange: true, dtick: 10 }),
    yaxis: grid({ title: { text: '% of peak labor income', font: { size: 13, color: MUTED } },
      fixedrange: true, rangemode: 'tozero' }),
    annotations: [
      { x: 9, y: 22, text: 'childhood<br>deficit', showarrow: false, font: { size: 12.5, color: WARN } },
      { x: 44, y: 25, text: 'working-life<br>surplus', showarrow: false, font: { size: 12.5, color: '#2F7A4A' } },
      { x: 81, y: 25, text: 'old-age<br>deficit', showarrow: false, font: { size: 12.5, color: WARN } },
    ],
  });
  const el = mount('fig-lifecycle');
  layout.height = sized(el, 0.85, 560, 1000);
  Plotly.newPlot(el, traces, layout, NOPAD);
}

/* ------------------------------------------------------------ data loading */
const state = {
  meta: null, countries: null,          // countries-summary.json
  weights: null, preset: 'zeihan',
  selected: null,
  scores: {}, cov: {},
  detailCache: new Map(),               // cache key -> Promise(detail json)
  playTimer: null,
  view: 'world',                        // 'world' | 'states'
  statesMeta: null, states: null,       // states-summary.json (lazy)
  stateScores: {},
  worldWeights: null,                   // stashed while in states view
};

const fmt = (v, d = 2) => (v === null || v === undefined) ? '—' : (+v).toFixed(d);
const fmtPop = t => (t === null || t === undefined) ? '—'
  : t >= 1e6 ? (t / 1e6).toFixed(2) + ' bn'
  : t >= 1e3 ? (t / 1e3).toFixed(1) + ' M'
  : Math.round(t) + ' k';

async function loadData() {
  const [summary, featured] = await Promise.all([
    fetch('data/countries-summary.json').then(r => r.json()),
    fetch('data/featured-series.json').then(r => r.json()),
  ]);
  state.meta = summary.meta;
  state.countries = summary.countries;
  state.weights = Object.assign({}, state.meta.presets.zeihan);
  return featured;
}

/* ----------------------------------------- Fig 2 + Fig 4 (featured series) */
function drawTFR(featured) {
  const order = ['KOR', 'CHN', 'IND', 'USA', 'DEU', 'NGA'];   // fixed hue order
  const years = featured.years;
  const upto = years.indexOf(2025) + 1;
  const traces = order.filter(k => featured.countries[k]).map(k => ({
    x: years.slice(0, upto), y: featured.countries[k].tfr.slice(0, upto),
    name: featured.countries[k].n, type: 'scatter', mode: 'lines',
    line: { color: CC[k], width: 2.2 },
    hovertemplate: `<b>${featured.countries[k].n}</b> %{x}: %{y:.2f}<extra></extra>`,
  }));
  const layout = Object.assign({}, BASE, {
    height: 500,
    legend: { orientation: 'h', x: 0.5, xanchor: 'center', y: -0.16 },
    xaxis: grid({ fixedrange: true, dtick: 10 }),
    yaxis: grid({ title: { text: 'births per woman (TFR)', font: { size: 13, color: MUTED } },
      fixedrange: true, rangemode: 'tozero' }),
    shapes: [{ type: 'line', x0: years[0], x1: 2025, y0: 2.1, y1: 2.1,
      line: { color: MUTED, width: 1.4, dash: 'dash' } }],
    annotations: [
      { x: 1953, y: 2.45, text: 'replacement ≈ 2.1', showarrow: false, font: { size: 11.5, color: MUTED }, xanchor: 'left' },
    ],
  });
  const el = mount('fig-tfr');
  layout.height = sized(el, 0.85, 580, 1000);
  Plotly.newPlot(el, traces, layout, NOPAD);
}

function drawSupport(featured) {
  const order = ['NGA', 'IND', 'USA', 'CHN', 'KOR', 'JPN', 'DEU'];
  const years = featured.years;
  const cut = years.indexOf(2025);
  const traces = [];
  order.filter(k => featured.countries[k]).forEach(k => {
    const c = featured.countries[k];
    traces.push({ x: years.slice(0, cut + 1), y: c.sr.slice(0, cut + 1), name: c.n,
      legendgroup: k, type: 'scatter', mode: 'lines', line: { color: CC[k], width: 2.2 },
      hovertemplate: `<b>${c.n}</b> %{x}: %{y:.1f} workers/retiree<extra></extra>` });
    traces.push({ x: years.slice(cut), y: c.sr.slice(cut), showlegend: false,
      legendgroup: k, type: 'scatter', mode: 'lines', line: { color: CC[k], width: 2.2, dash: 'dot' },
      hovertemplate: `<b>${c.n}</b> %{x} (proj.): %{y:.1f}<extra></extra>` });
  });
  const layout = Object.assign({}, BASE, {
    height: 540,
    legend: { orientation: 'h', x: 0.5, xanchor: 'center', y: -0.16 },
    xaxis: grid({ fixedrange: true, dtick: 25 }),
    yaxis: grid({ title: { text: 'workers (20–64) per retiree (65+), log scale', font: { size: 13, color: MUTED } },
      type: 'log', tickvals: [1, 2, 4, 8, 16, 32], fixedrange: true, range: [Math.log10(0.8), Math.log10(36)] }),
    shapes: [{ type: 'rect', xref: 'paper', x0: 0, x1: 1, y0: Math.log10(0.8), y1: Math.log10(2),
      fillcolor: 'rgba(184,58,46,.07)', line: { width: 0 } }],
    annotations: [
      { xref: 'paper', x: 0.011, y: Math.log10(1.55), text: 'pay-as-you-go breaks down', showarrow: false,
        font: { size: 12, color: WARN }, xanchor: 'left' },
      { x: 2025, yref: 'paper', y: 1.04, text: '← estimates · projections →', showarrow: false, font: { size: 11.5, color: MUTED } },
    ],
  });
  const el = mount('fig-sr');
  layout.height = sized(el, 0.9, 620, 1050);
  Plotly.newPlot(el, traces, layout, NOPAD);
}

/* Fig 5 — only when World Bank data has been backfilled into the dataset. */
function drawCurrentAccount() {
  const rows = Object.entries(state.countries)
    .filter(([, c]) => c.ca !== null && c.ca !== undefined && c.ma && c.pop > 1000);
  if (rows.length < 30) return;                       // WB not shipped yet
  document.getElementById('fig-ca-wrap').hidden = false;
  document.getElementById('fig-ca-note').hidden = true;
  const label = new Set(['DEU', 'JPN', 'CHN', 'KOR', 'USA', 'NGA', 'NOR', 'SAU']);
  const traces = [{
    type: 'scatter', mode: 'markers',
    x: rows.map(([, c]) => c.ma), y: rows.map(([, c]) => c.ca),
    marker: { size: rows.map(([, c]) => Math.max(6, 2.2 * Math.log10(c.pop))), sizemode: 'diameter',
      color: 'rgba(31,78,158,.45)', line: { color: PAPER, width: 1 } },
    text: rows.map(([, c]) => c.n),
    hovertemplate: '<b>%{text}</b><br>median age %{x:.1f} · current account %{y:.1f}% GDP<extra></extra>',
    showlegend: false,
  }];
  const layout = Object.assign({}, BASE, {
    height: 520,
    xaxis: grid({ title: { text: 'median age', font: { size: 13, color: MUTED } }, fixedrange: true }),
    yaxis: grid({ title: { text: 'current account, % GDP', font: { size: 13, color: MUTED } }, fixedrange: true, zerolinecolor: MUTED }),
    annotations: rows.filter(([k]) => label.has(k)).map(([k, c]) => ({
      x: c.ma, y: c.ca, text: c.n, showarrow: false, yshift: 11, font: { size: 11.5, color: MUTED } })),
  });
  const el = mount('fig-ca');
  layout.height = sized(el, 0.9, 620, 1050);
  Plotly.newPlot(el, traces, layout, NOPAD);
}

/* ------------------------------------------------------------- the scoring */
function computeScores() {
  const w = state.weights;
  const comps = state.meta.components.map(c => c.id);
  const totalW = comps.reduce((s, k) => s + (w[k] || 0), 0) || 1;
  for (const [iso3, c] of Object.entries(state.countries)) {
    let num = 0, den = 0;
    for (const k of comps) {
      const z = c.z[k];
      if (z !== null && z !== undefined && w[k] > 0) { num += w[k] * z; den += w[k]; }
    }
    state.scores[iso3] = den > 0 ? num / den : null;
    state.cov[iso3] = den / totalW;
  }
}

/* Parity check against the Python pipeline (zeihan preset, all components).
   v1.1 (canonical POADR): JPN z = {dems:-1.58, demt:-0.555, geo:1, agri:-1,
   ener:-1.5, trade:-0.5, cap:1}
   S = .25(-1.58)+.20(-.555)+.15(1)+.10(-1)+.10(-1.5)+.10(-.5)+.10(1) = -0.556 */
function parityCheck() {
  if (state.preset !== 'zeihan') return;
  const s = state.scores.JPN;
  if (s !== null && Math.abs(s - (-0.556)) > 0.01) {
    console.warn('score parity check failed: JPN zeihan =', s);
  }
}

/* ------------------------------------------------------------------ the map */
const DIVERGING = [
  [0, '#8F2D23'], [0.25, '#CE7E75'], [0.5, '#E8E5E0'], [0.75, '#7391C4'], [1, '#163D7D'],
];

function hoverData(iso3) {
  const c = state.countries[iso3];
  const covWarn = state.cov[iso3] < 0.5 ? '⚠ low data coverage for these weights' : '';
  return [c.n, fmt(c.ma, 1), fmt(c.ma50, 1), fmt(c.sr, 1), fmt(c.tfr, 2), fmt(c.wrr, 2),
          fmt(c.esr, 2), covWarn];
}

const COLORBAR = { title: { text: 'score', font: { size: 12.5 } }, thickness: 10, len: 0.6,
  tickvals: [-2, -1, 0, 1, 2], outlinewidth: 0, tickfont: { size: 11.5 } };

function worldMapSpec() {
  const isos = Object.keys(state.countries);
  const trace = {
    type: 'choropleth', locationmode: 'ISO-3',
    locations: isos,
    z: isos.map(k => state.scores[k]),
    zmin: -2, zmax: 2, colorscale: DIVERGING,
    customdata: isos.map(hoverData),
    colorbar: COLORBAR,
    marker: { line: { color: PAPER, width: 0.4 } },
    hovertemplate:
      '<b>%{customdata[0]}</b> · score %{z:.2f}<br>' +
      'median age %{customdata[1]} → %{customdata[2]} by 2050<br>' +
      'workers/retiree (headcount) %{customdata[3]} · TFR %{customdata[4]}<br>' +
      'entrants per exit %{customdata[5]} · eff. workers/consumer %{customdata[6]}<br>' +
      '<span style="color:#f4c7c2">%{customdata[7]}</span>' +
      '<extra>click for full workup</extra>',
  };
  const layout = Object.assign({}, BASE, {
    margin: { l: 0, r: 0, t: 0, b: 0 },
    geo: {
      projection: { type: 'natural earth' }, showframe: false, showcoastlines: false,
      showland: true, landcolor: '#F1EFEA', bgcolor: PAPER,
      showcountries: false, resolution: 110,
    },
    dragmode: false,
  });
  return { trace, layout };
}

function stateHoverData(u) {
  const s = state.states[u];
  return [s.n, fmt(s.ma, 1), fmt(s.ma50, 1), fmt(s.sr, 1), fmt(s.esr, 2),
          fmt(s.wrr, 2), fmt(s.dommig, 0)];
}

function statesMapSpec() {
  const units = Object.keys(state.states);
  const trace = {
    type: 'choropleth', locationmode: 'USA-states',
    locations: units,
    z: units.map(u => state.stateScores[u]),
    zmin: -2, zmax: 2, colorscale: DIVERGING,
    customdata: units.map(stateHoverData),
    colorbar: COLORBAR,
    marker: { line: { color: PAPER, width: 0.6 } },
    hovertemplate:
      '<b>%{customdata[0]}</b> · score %{z:.2f}<br>' +
      'median age %{customdata[1]} → %{customdata[2]} by 2050 (closed-state)<br>' +
      'workers/retiree (headcount) %{customdata[3]} · eff. workers/consumer %{customdata[4]}<br>' +
      'entrants per exit %{customdata[5]} · net domestic migration %{customdata[6]}k/yr' +
      '<extra>click for full workup</extra>',
  };
  const layout = Object.assign({}, BASE, {
    margin: { l: 0, r: 0, t: 0, b: 0 },
    geo: { scope: 'usa', showframe: false, showlakes: false, bgcolor: PAPER,
      landcolor: '#F1EFEA' },
    dragmode: false,
  });
  return { trace, layout };
}

let mapInitialized = false;
function renderMap() {
  const spec = state.view === 'world' ? worldMapSpec() : statesMapSpec();
  if (!mapInitialized) {
    Plotly.newPlot(mount('map'), [spec.trace], spec.layout,
      Object.assign({}, NOPAD, { topojsonURL: 'vendor/topojson/', scrollZoom: false }));
    document.getElementById('map').on('plotly_click', ev => {
      const loc = ev.points && ev.points[0] && ev.points[0].location;
      if (!loc) return;
      location.hash = (state.view === 'world' ? '#country/' : '#state/') + loc;
    });
    mapInitialized = true;
  } else {
    Plotly.react('map', [spec.trace], spec.layout);
  }
}

function recolorMap() {
  if (state.view === 'world') {
    const isos = Object.keys(state.countries);
    Plotly.restyle('map', {
      z: [isos.map(k => state.scores[k])],
      customdata: [isos.map(hoverData)],
    });
  } else if (state.states) {
    computeStateScores();
    const units = Object.keys(state.states);
    Plotly.restyle('map', {
      z: [units.map(u => state.stateScores[u])],
      customdata: [units.map(stateHoverData)],
    });
  }
}

/* ------------------------------------------------------- weights & presets */
function renderSliders() {
  const holder = document.getElementById('sliders');
  holder.innerHTML = '';
  for (const comp of state.meta.components) {
    const div = document.createElement('div');
    div.className = 'sl' + (comp.authored ? ' authored' : '');
    div.innerHTML =
      `<label><span class="nm">${comp.label}</span><span class="pct" data-pct="${comp.id}"></span></label>
       <input type="range" min="0" max="100" step="1" data-w="${comp.id}"
              aria-label="weight: ${comp.label}">`;
    holder.appendChild(div);
  }
  holder.addEventListener('input', ev => {
    const id = ev.target.dataset.w;
    if (!id) return;
    state.weights[id] = +ev.target.value / 100;
    state.preset = null;
    document.querySelectorAll('#presets button').forEach(b => b.classList.remove('on'));
    scheduleRescore();
  });
  syncSliders();
}

function syncSliders() {
  const w = state.weights;
  const total = Object.values(w).reduce((a, b) => a + b, 0) || 1;
  document.querySelectorAll('#sliders input[type=range]').forEach(inp => {
    inp.value = Math.round((w[inp.dataset.w] || 0) * 100);
  });
  document.querySelectorAll('#sliders .pct').forEach(el => {
    el.textContent = Math.round(100 * (w[el.dataset.pct] || 0) / total) + '%';
  });
}

let rescoreTimer = null;
function scheduleRescore() {
  syncSliders();
  clearTimeout(rescoreTimer);
  rescoreTimer = setTimeout(() => {
    const total = Object.values(state.weights).reduce((a, b) => a + b, 0);
    if (total === 0) {                        // all-zero fallback: pure demographics
      state.weights = Object.assign({}, state.meta.presets.puredemo);
      state.preset = 'puredemo';
      document.querySelector('#presets [data-preset=puredemo]').classList.add('on');
      syncSliders();
    }
    if (state.view === 'world') computeScores();
    recolorMap();                             // states branch recomputes internally
    if (state.selected) {
      if (state.view === 'world') renderDecomp(state.selected);
      else renderStateDecomp(state.selected);
    }
  }, 60);
}

function wirePresets() {
  document.getElementById('presets').addEventListener('click', ev => {
    const p = ev.target.dataset.preset;
    if (!p) return;
    state.preset = p;
    state.weights = Object.assign({}, state.meta.presets[p]);
    document.querySelectorAll('#presets button').forEach(b => b.classList.toggle('on', b.dataset.preset === p));
    syncSliders();
    computeScores();
    parityCheck();
    recolorMap();
    if (state.selected) renderDecomp(state.selected);
  });
}

/* ----------------------------------------------------------- country panel */
function fetchDetail(iso3) {
  if (!state.detailCache.has(iso3)) {
    state.detailCache.set(iso3, fetch('data/countries/' + iso3 + '.json')
      .then(r => { if (!r.ok) throw new Error(iso3 + ' not found'); return r.json(); })
      .catch(err => { state.detailCache.delete(iso3); throw err; }));
  }
  return state.detailCache.get(iso3);
}

function classifyStage(c) {
  if (c.ma < 25) return ['pre-dividend', 'a young population whose dividend window has not fully opened'];
  if (c.ma < 33) return ['dividend window', 'inside the demographic dividend — the working share is still rising'];
  if (c.ma < 41) return ['peak workforce', 'at or near peak working-age share; the dividend is ending'];
  if (c.ma < 47) return ['early contraction', 'past the peak — the workforce has begun to shrink'];
  return ['deep contraction', 'deep in workforce contraction with a top-heavy age structure'];
}

function autoNarrative(iso3) {
  const c = state.countries[iso3];
  const [stage, gloss] = classifyStage(c);
  const bits = [];
  bits.push(`<b>${c.n}</b> is in the <b>${stage}</b> phase: ${gloss}.`);
  bits.push(`Median age ${fmt(c.ma, 1)} today, heading to ${fmt(c.ma50, 1)} by 2050; ` +
    `${fmt(c.sr, 1)} workers support each retiree` +
    (c.sr !== null && c.sr < 2.5 ? ' — already inside the zone where pay-as-you-go arithmetic strains.' : '.'));
  if (c.wrr !== null) {
    bits.push(c.wrr < 0.85
      ? `The labor-market turnstile runs backwards: only ${fmt(c.wrr, 2)} entrants arrive per worker retiring.`
      : c.wrr > 1.5
        ? `The turnstile still spins forward: ${fmt(c.wrr, 2)} entrants per retiring worker.`
        : `Workforce replacement is near balance (${fmt(c.wrr, 2)} entrants per exit).`);
  }
  if (c.mom !== null) {
    bits.push(c.mom < 0.97
      ? `Built-in momentum is negative — the population shrinks ~${Math.round((1 - c.mom) * 100)}% by 2050 even before fertility moves again.`
      : c.mom > 1.15
        ? `Age-structure momentum alone grows the population ~${Math.round((c.mom - 1) * 100)}% by 2050.`
        : `Population is roughly plateaued through 2050 (${fmt(c.mom, 2)}×).`);
  }
  if (c.tfr !== null && c.tfr < 1.4) bits.push(`Fertility of ${fmt(c.tfr, 2)} locks a still-smaller replacement generation behind the current one.`);
  return '<p>' + bits.join(' ') + '</p><p style="color:var(--muted);font-size:.85rem">Auto-generated from the instrument panel; this country has no hand-written portrait (yet).</p>';
}

function statBox(label, value) {
  return `<div class="stat"><div class="v">${value}</div><div class="l">${label}</div></div>`;
}

async function selectCountry(iso3) {
  const c = state.countries[iso3];
  if (!c) return;
  state.selected = iso3;
  if (state.playTimer) { clearInterval(state.playTimer); state.playTimer = null; }
  const panel = document.getElementById('country-panel');
  panel.innerHTML = `<div class="closed-hint">Loading ${c.n}…</div>`;
  panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

  let d;
  try { d = await fetchDetail(iso3); }
  catch (e) { panel.innerHTML = `<div class="closed-hint">No detail file for ${c.n}.</div>`; return; }
  if (state.selected !== iso3) return;    // user clicked elsewhere while loading

  const score = state.scores[iso3];
  const covWarn = state.cov[iso3] < 0.5 ? `<span class="cov">⚠ score covers only ${Math.round(state.cov[iso3] * 100)}% of chosen weights</span>` : '';
  const tpl = document.getElementById('narrative-' + iso3);
  panel.innerHTML = `
    <div class="cp-head">
      <h3>${c.n}</h3>
      <span class="score" style="color:${score >= 0 ? ACCENT : WARN}">score ${score === null ? '—' : (score >= 0 ? '+' : '') + score.toFixed(2)}</span>
      ${covWarn}
    </div>
    <div class="statstrip">
      ${statBox('population', fmtPop(c.pop))}
      ${statBox('median age', fmt(c.ma, 1))}
      ${statBox('median 2050', fmt(c.ma50, 1))}
      ${statBox('TFR', fmt(c.tfr, 2))}
      ${statBox('workers / retiree (headcount)', fmt(c.sr, 1))}
      ${statBox('eff. workers / consumer', fmt(c.esr, 2))}
      ${statBox('prospective OADR', fmt(c.poadr, 2))}
      ${statBox('old-age begins (RLE 15y)', c.pt === null || c.pt === undefined ? '—' : fmt(c.pt, 1) + 'y')}
      ${statBox('entrants / exit', fmt(c.wrr, 2))}
      ${statBox('pop 2050 ÷ 2025', fmt(c.mom, 2))}
    </div>
    <div class="cp-grid">
      <div>
        <div class="pyr-controls">
          <button id="pyr-play" aria-label="animate">▶</button>
          <input type="range" id="pyr-year" min="0" max="${d.pyramid.years.length - 1}" step="1">
          <span id="pyr-label" class="readout" style="font-weight:700;min-width:3ch"></span>
          <button id="pyr-mode" title="toggle % / absolute" style="background:#fff;color:var(--muted);border:1px solid var(--rule)">%</button>
        </div>
        <div id="cp-pyramid" style="height:420px"></div>
      </div>
      <div><div id="cp-sparks" style="height:420px"></div></div>
      <div class="full"><div id="cp-decomp" style="height:200px"></div></div>
    </div>
    <div class="cp-narrative">
      <div class="k">${tpl ? 'Portrait' : 'Auto-workup'}</div>
      ${tpl ? tpl.innerHTML : autoNarrative(iso3)}
      ${d.context_notes ? '<dl class="ctxnotes">' + Object.entries(d.context_notes).map(([k, v]) =>
        `<dt>${k}:</dt><dd>${v}</dd>`).join('') + '</dl>' : ''}
    </div>`;

  drawPyramid(d);
  drawSparks(d);
  renderDecomp(iso3);
  const input = document.getElementById('country-input');
  if (input && input.value !== c.n) input.value = c.n;
}

/* ------------------------------------------------------- panel sub-figures */
function drawPyramid(d) {
  const years = d.pyramid.years;
  const el = document.getElementById('cp-pyramid');
  const slider = document.getElementById('pyr-year');
  const label = document.getElementById('pyr-label');
  const modeBtn = document.getElementById('pyr-mode');
  let mode = 'pct';
  let idx = years.indexOf(2025); if (idx < 0) idx = 0;

  const totals = years.map((y, i) => {
    const m = d.pyramid.m[i], f = d.pyramid.f[i];
    return (m && f) ? m.reduce((a, b) => a + b, 0) + f.reduce((a, b) => a + b, 0) : null;
  });
  // fixed axis range across all years so the animation doesn't rescale
  let maxPct = 0, maxAbs = 0;
  years.forEach((y, i) => {
    const m = d.pyramid.m[i], f = d.pyramid.f[i];
    if (!m || !totals[i]) return;
    for (let b = 0; b < m.length; b++) {
      maxAbs = Math.max(maxAbs, m[b], f[b]);
      maxPct = Math.max(maxPct, 100 * m[b] / totals[i], 100 * f[b] / totals[i]);
    }
  });

  function arrays(i) {
    const m = d.pyramid.m[i], f = d.pyramid.f[i];
    if (mode === 'pct') {
      return { m: m.map(v => -100 * v / totals[i]), f: f.map(v => 100 * v / totals[i]),
        hm: m.map(v => (100 * v / totals[i]).toFixed(2) + '%'), hf: f.map(v => (100 * v / totals[i]).toFixed(2) + '%'),
        range: [-maxPct * 1.06, maxPct * 1.06] };
    }
    return { m: m.map(v => -v), f: f.slice(),
      hm: m.map(v => fmtPop(v)), hf: f.map(v => fmtPop(v)),
      range: [-maxAbs * 1.06, maxAbs * 1.06] };
  }

  function render(i) {
    if (!d.pyramid.m[i]) return;
    idx = i;
    slider.value = i;
    label.textContent = years[i];
    const a = arrays(i);
    const traces = [
      { type: 'bar', orientation: 'h', x: a.m, y: AGE_LABELS, marker: { color: ACCENT }, width: 0.85,
        name: 'Male', customdata: a.hm, hovertemplate: '%{y} male: %{customdata}<extra></extra>' },
      { type: 'bar', orientation: 'h', x: a.f, y: AGE_LABELS, marker: { color: ORANGE }, width: 0.85,
        name: 'Female', customdata: a.hf, hovertemplate: '%{y} female: %{customdata}<extra></extra>' },
    ];
    const layout = Object.assign({}, BASE, {
      barmode: 'overlay', bargap: 0.08, height: 420, showlegend: false,
      margin: { l: 44, r: 10, t: 8, b: 24 },
      xaxis: grid({ range: a.range, fixedrange: true,
        tickvals: [a.range[0] * 0.66, 0, a.range[1] * 0.66],
        ticktext: mode === 'pct'
          ? [(maxPct * 0.7).toFixed(0) + '%', '0', (maxPct * 0.7).toFixed(0) + '%']
          : [fmtPop(maxAbs * 0.7), '0', fmtPop(maxAbs * 0.7)] }),
      yaxis: grid({ tickfont: { size: 11, color: MUTED }, fixedrange: true }),
      annotations: [
        { xref: 'paper', yref: 'paper', x: 0.03, y: 0.98, text: 'M', showarrow: false, font: { size: 11, color: ACCENT } },
        { xref: 'paper', yref: 'paper', x: 0.97, y: 0.98, text: 'F', showarrow: false, font: { size: 11, color: ORANGE } },
      ],
    });
    Plotly.react(el, traces, layout, NOPAD);
    RESIZER.observe(el);
  }

  slider.addEventListener('input', () => render(+slider.value));
  modeBtn.addEventListener('click', () => {
    mode = mode === 'pct' ? 'abs' : 'pct';
    modeBtn.textContent = mode === 'pct' ? '%' : '#';
    render(idx);
  });
  document.getElementById('pyr-play').addEventListener('click', ev => {
    if (state.playTimer) { clearInterval(state.playTimer); state.playTimer = null; ev.target.textContent = '▶'; return; }
    ev.target.textContent = '⏸';
    if (idx >= years.length - 1) idx = 0;
    state.playTimer = setInterval(() => {
      if (idx >= years.length - 1) { clearInterval(state.playTimer); state.playTimer = null; ev.target.textContent = '▶'; return; }
      render(idx + 1);
    }, 220);
  });
  render(idx);
}

function drawSparks(d, panelsOverride, dtick) {
  const s = d.series;
  const popM = s.pop.map(v => v === null ? null : v / 1000);   // thousands → millions
  const panels = panelsOverride || [
    { key: 'tfr', title: 'fertility (TFR)', color: ACCENT },
    { key: 'sr', title: 'workers / retiree', color: WARN },
    { key: 'ma', title: 'median age', color: '#6A4FA3' },
    { key: 'pop', title: 'population (millions)', color: '#2F7A4A', data: popM },
  ];
  const traces = [], annotations = [], layoutAxes = {};
  const shapes = [];
  panels.forEach((p, i) => {
    const xa = i === 0 ? 'x' : 'x' + (i + 1), ya = i === 0 ? 'y' : 'y' + (i + 1);
    traces.push({ x: s.years, y: p.data || s[p.key], xaxis: xa, yaxis: ya, type: 'scatter', mode: 'lines',
      line: { color: p.color, width: 1.8 }, showlegend: false, connectgaps: false,
      hovertemplate: '%{x}: %{y:.6~r}<extra>' + p.title + '</extra>' });
    const col = i % 2, row = i < 2 ? 0 : 1;
    layoutAxes['xaxis' + (i ? i + 1 : '')] = grid({ domain: [col * 0.55, col * 0.55 + 0.45],
      anchor: ya, tickfont: { size: 11, color: MUTED }, dtick: dtick || 50, fixedrange: true });
    layoutAxes['yaxis' + (i ? i + 1 : '')] = grid({ domain: [row === 0 ? 0.58 : 0, row === 0 ? 1 : 0.42],
      anchor: xa, tickfont: { size: 11, color: MUTED }, nticks: 4, fixedrange: true,
      rangemode: p.key === 'ma' ? 'normal' : 'tozero' });
    annotations.push({ xref: xa + ' domain', yref: ya + ' domain', x: 0.02, y: 1.16,
      text: p.title, showarrow: false, font: { size: 11.5, color: MUTED }, xanchor: 'left' });
    shapes.push({ type: 'line', xref: xa, yref: ya + ' domain',
      x0: 2025, x1: 2025, y0: 0, y1: 1, line: { color: RULE, width: 1, dash: 'dot' } });
  });
  const layout = Object.assign({}, BASE, layoutAxes, {
    height: 420, margin: { l: 40, r: 6, t: 24, b: 22 }, annotations, shapes,
  });
  Plotly.newPlot('cp-sparks', traces, layout, NOPAD);
  RESIZER.observe(document.getElementById('cp-sparks'));
}

function renderDecomp(iso3) {
  const el = document.getElementById('cp-decomp');
  if (!el) return;
  const c = state.countries[iso3];
  const comps = state.meta.components;
  const w = state.weights;
  const den = comps.reduce((s, k) => (c.z[k.id] !== null && c.z[k.id] !== undefined && w[k.id] > 0) ? s + w[k.id] : s, 0) || 1;
  const rows = comps.map(k => {
    const z = c.z[k.id];
    const active = z !== null && z !== undefined && w[k.id] > 0;
    return {
      label: k.label + (k.authored ? ((c.ctxa || []).includes(k.id) ? ' ✎' : ' ·') : ''),
      contrib: active ? (w[k.id] * z) / den : 0,
      missing: z === null || z === undefined,
    };
  }).reverse();
  const traces = [{
    type: 'bar', orientation: 'h',
    y: rows.map(r => r.label),
    x: rows.map(r => r.contrib),
    marker: { color: rows.map(r => r.missing ? RULE : r.contrib >= 0 ? ACCENT : WARN) },
    customdata: rows.map(r => r.missing ? 'no data — excluded & disclosed' : 'contribution to score'),
    hovertemplate: '%{y}: %{x:.3f}<br>%{customdata}<extra></extra>', width: 0.7,
  }];
  const layout = Object.assign({}, BASE, {
    height: 214, margin: { l: 210, r: 12, t: 24, b: 44 },
    xaxis: grid({ zerolinecolor: MUTED, fixedrange: true,
      title: { text: 'weighted contribution w·z under current sliders (✎ = authored rubric, · = default/derived)', font: { size: 11.5, color: MUTED } } }),
    yaxis: grid({ tickfont: { size: 11.5 }, fixedrange: true }),
  });
  Plotly.react(el, traces, layout, NOPAD);
  RESIZER.observe(el);
}

/* --------------------------------------------------------- US-state view */
function computeStateScores() {
  if (!state.states) return;
  const wd = state.weights.dems || 0, wt = state.weights.demt || 0;
  for (const [u, s] of Object.entries(state.states)) {
    let num = 0, den = 0;
    if (s.z.dems !== null && s.z.dems !== undefined && wd > 0) { num += wd * s.z.dems; den += wd; }
    if (s.z.demt !== null && s.z.demt !== undefined && wt > 0) { num += wt * s.z.demt; den += wt; }
    state.stateScores[u] = den > 0 ? num / den : null;
  }
  const p = state.statesMeta && state.statesMeta.parity;
  if (p && Math.abs(wd - wt) < 1e-9 && state.stateScores[p.unit] != null &&
      Math.abs(state.stateScores[p.unit] - p.score) > 0.01) {
    console.warn('state score parity check failed:', p.unit, state.stateScores[p.unit], 'vs', p.score);
  }
}

async function setView(v) {
  if (v === state.view) return;
  const pending = document.getElementById('states-pending');
  if (v === 'states') {
    if (!state.states) {
      try {
        const r = await fetch('data/states-summary.json');
        if (!r.ok) throw new Error('no state dataset');
        const j = await r.json();
        state.statesMeta = j.meta;
        state.states = j.states;
      } catch (e) {
        if (pending) pending.hidden = false;
        document.querySelectorAll('#view-toggle button').forEach(b =>
          b.classList.toggle('on', b.dataset.view === 'world'));
        return;
      }
    }
    state.view = 'states';
    state.worldWeights = Object.assign({}, state.weights);
    if (!state.weights.dems && !state.weights.demt) {
      state.weights.dems = 0.5; state.weights.demt = 0.5;
    }
    document.getElementById('sliders').classList.add('states-mode');
    document.getElementById('presets').classList.add('off');
    computeStateScores();
  } else {
    state.view = 'world';
    if (state.worldWeights) state.weights = state.worldWeights;
    document.getElementById('sliders').classList.remove('states-mode');
    document.getElementById('presets').classList.remove('off');
    computeScores();
  }
  if (pending) pending.hidden = true;
  document.querySelectorAll('#view-toggle button').forEach(b =>
    b.classList.toggle('on', b.dataset.view === state.view));
  state.selected = null;
  if (state.playTimer) { clearInterval(state.playTimer); state.playTimer = null; }
  document.getElementById('country-panel').innerHTML =
    '<div class="closed-hint">Click a ' + (state.view === 'world' ? 'country' : 'state') +
    ' on the map — or type one above — to open its workup.</div>';
  const input = document.getElementById('country-input');
  if (input) input.value = '';
  syncSliders();
  renderMap();
  rebuildPicker();
}

function wireViewToggle() {
  const holder = document.getElementById('view-toggle');
  if (!holder) return;
  holder.addEventListener('click', ev => {
    const v = ev.target.dataset.view;
    if (v) setView(v);
  });
}

function fetchStateDetail(u) {
  const key = 'S:' + u;
  if (!state.detailCache.has(key)) {
    state.detailCache.set(key, fetch('data/states/' + u + '.json')
      .then(r => { if (!r.ok) throw new Error(u + ' not found'); return r.json(); })
      .catch(err => { state.detailCache.delete(key); throw err; }));
  }
  return state.detailCache.get(key);
}

function autoStateNarrative(u) {
  const s = state.states[u];
  const bits = [];
  bits.push(`<b>${s.n}</b>: median age ${fmt(s.ma, 1)} today, drifting to ${fmt(s.ma50, 1)} ` +
    `by 2050 <i>if nobody moved</i> — and people move; that's the point of the closed-state ` +
    `projection below.`);
  if (s.dommig !== null) {
    bits.push(s.dommig > 5
      ? `Right now the state is importing its demography: net domestic migration of ` +
        `+${fmt(s.dommig, 0)}k people a year does what no birth rate can — it adds ` +
        `working-age adults directly.`
      : s.dommig < -5
        ? `Right now the state is exporting people: net domestic migration of ` +
          `${fmt(s.dommig, 0)}k a year, which ages the remaining structure faster than ` +
          `births alone imply.`
        : `Domestic migration is roughly balanced (${fmt(s.dommig, 0)}k/yr), so the ` +
          `built-in structure below is close to the real trajectory.`);
  }
  if (s.natinc !== null) {
    bits.push((s.natinc > 0 ? `Births still exceed deaths (+${fmt(s.natinc, 0)}k/yr).`
      : `Deaths now exceed births (${fmt(s.natinc, 0)}k/yr) — growth, if any, is entirely imported.`));
  }
  bits.push(`${fmt(s.sr, 1)} workers per retiree (headcount); ${fmt(s.wrr, 2)} labor-market ` +
    `entrants per exit.`);
  return '<p>' + bits.join(' ') + '</p>';
}

function renderStateDecomp(u) {
  const el = document.getElementById('cp-decomp');
  if (!el || !state.states) return;
  const s = state.states[u];
  const comps = (state.statesMeta && state.statesMeta.components) || [];
  const wAll = { dems: state.weights.dems || 0, demt: state.weights.demt || 0 };
  const den = comps.reduce((acc, k) => (s.z[k.id] != null && wAll[k.id] > 0) ? acc + wAll[k.id] : acc, 0) || 1;
  const rows = comps.map(k => ({
    label: k.label,
    contrib: (s.z[k.id] != null && wAll[k.id] > 0) ? (wAll[k.id] * s.z[k.id]) / den : 0,
    missing: s.z[k.id] == null,
  })).reverse();
  const traces = [{
    type: 'bar', orientation: 'h',
    y: rows.map(r => r.label), x: rows.map(r => r.contrib),
    marker: { color: rows.map(r => r.missing ? RULE : r.contrib >= 0 ? ACCENT : WARN) },
    hovertemplate: '%{y}: %{x:.3f}<extra></extra>', width: 0.55,
  }];
  const layout = Object.assign({}, BASE, {
    height: 150, margin: { l: 210, r: 12, t: 20, b: 40 },
    xaxis: grid({ zerolinecolor: MUTED, fixedrange: true,
      title: { text: 'weighted contribution w·z (states score on demographic components only)', font: { size: 11.5, color: MUTED } } }),
    yaxis: grid({ tickfont: { size: 11.5 }, fixedrange: true }),
  });
  Plotly.react(el, traces, layout, NOPAD);
  RESIZER.observe(el);
}

async function selectState(u) {
  const s = state.states && state.states[u];
  if (!s) return;
  state.selected = u;
  if (state.playTimer) { clearInterval(state.playTimer); state.playTimer = null; }
  const panel = document.getElementById('country-panel');
  panel.innerHTML = `<div class="closed-hint">Loading ${s.n}…</div>`;
  panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

  let d;
  try { d = await fetchStateDetail(u); }
  catch (e) { panel.innerHTML = `<div class="closed-hint">No detail file for ${s.n}.</div>`; return; }
  if (state.selected !== u) return;

  computeStateScores();
  const score = state.stateScores[u];
  panel.innerHTML = `
    <div class="cp-head">
      <h3>${s.n}</h3>
      <span class="score" style="color:${score >= 0 ? ACCENT : WARN}">score ${score == null ? '—' : (score >= 0 ? '+' : '') + score.toFixed(2)}</span>
      <span style="font-size:.75rem;color:var(--muted)">demographic components only</span>
    </div>
    <div class="statstrip">
      ${statBox('population', fmtPop(s.pop))}
      ${statBox('median age', fmt(s.ma, 1))}
      ${statBox('median 2050 (closed)', fmt(s.ma50, 1))}
      ${statBox('workers / retiree (headcount)', fmt(s.sr, 1))}
      ${statBox('eff. workers / consumer', fmt(s.esr, 2))}
      ${statBox('prospective OADR', fmt(s.poadr, 2))}
      ${statBox('entrants / exit', fmt(s.wrr, 2))}
      ${statBox('pop 2050 ÷ 2025 (closed)', fmt(s.mom, 2))}
      ${statBox('net dom. migration', (s.dommig == null ? '—' : (s.dommig > 0 ? '+' : '') + fmt(s.dommig, 0) + 'k/yr'))}
      ${statBox('births − deaths', (s.natinc == null ? '—' : (s.natinc > 0 ? '+' : '') + fmt(s.natinc, 0) + 'k/yr'))}
    </div>
    <div class="cp-grid">
      <div>
        <div class="pyr-controls">
          <button id="pyr-play" aria-label="animate">▶</button>
          <input type="range" id="pyr-year" min="0" max="${d.pyramid.years.length - 1}" step="1">
          <span id="pyr-label" class="readout" style="font-weight:700;min-width:3ch"></span>
          <button id="pyr-mode" title="toggle % / absolute" style="background:#fff;color:var(--muted);border:1px solid var(--rule)">%</button>
        </div>
        <div id="cp-pyramid" style="height:420px"></div>
        <p style="font-size:.75rem;color:var(--muted);margin:.3rem 0 0">${d.note || ''}</p>
      </div>
      <div><div id="cp-sparks" style="height:420px"></div></div>
      <div class="full"><div id="cp-decomp" style="height:150px"></div></div>
    </div>
    <div class="cp-narrative">
      <div class="k">Auto-workup</div>
      ${autoStateNarrative(u)}
    </div>`;

  drawPyramid(d);
  drawSparks(d, [
    { key: 'esr', title: 'eff. workers / consumer', color: ACCENT },
    { key: 'sr', title: 'workers / retiree (headcount)', color: WARN },
    { key: 'ma', title: 'median age', color: '#6A4FA3' },
    { key: 'pop', title: 'population (millions)', color: '#2F7A4A',
      data: d.series.pop.map(v => v === null ? null : v / 1000) },
  ], 10);
  renderStateDecomp(u);
  const input = document.getElementById('country-input');
  if (input && input.value !== s.n) input.value = s.n;
}

/* ------------------------------------------------------ routing & pickers */
function wireRouting() {
  const apply = () => {
    const mc = location.hash.match(/^#country\/([A-Z]{3})$/);
    const ms = location.hash.match(/^#state\/([A-Z]{2})$/);
    if (mc && state.countries[mc[1]]) {
      if (state.view !== 'world') { setView('world').then(() => selectCountry(mc[1])); }
      else selectCountry(mc[1]);
    } else if (ms) {
      if (state.view !== 'states') {
        setView('states').then(() => { if (state.states && state.states[ms[1]]) selectState(ms[1]); });
      } else if (state.states && state.states[ms[1]]) {
        selectState(ms[1]);
      }
    }
  };
  window.addEventListener('hashchange', apply);
  apply();
}

let pickerByName = {};
function rebuildPicker() {
  const input = document.getElementById('country-input');
  const list = document.getElementById('country-list');
  list.innerHTML = '';
  pickerByName = {};
  const src = state.view === 'world' ? state.countries : state.states;
  const prefix = state.view === 'world' ? '#country/' : '#state/';
  Object.entries(src || {})
    .sort((a, b) => a[1].n.localeCompare(b[1].n))
    .forEach(([code, c]) => {
      pickerByName[c.n.toLowerCase()] = prefix + code;
      const opt = document.createElement('option');
      opt.value = c.n;
      list.appendChild(opt);
    });
  input.placeholder = state.view === 'world' ? 'Type a name… e.g. Japan' : 'Type a state… e.g. Utah';
}

function wirePicker() {
  rebuildPicker();
  document.getElementById('country-input').addEventListener('change', ev => {
    const target = pickerByName[ev.target.value.trim().toLowerCase()];
    if (target) location.hash = target;
  });
}

/* ------------------------------------------------------------ portraits */
function buildPortraits() {
  const holder = document.getElementById('portraits-list');
  if (!holder || !state.meta.featured) return;
  const cards = state.meta.featured
    .filter(iso3 => state.countries[iso3])
    .map(iso3 => {
      const c = state.countries[iso3];
      const tpl = document.getElementById('narrative-' + iso3);
      const teaserEl = tpl && tpl.content ? tpl.content.querySelector('[data-teaser]') : null;
      const teaser = teaserEl ? teaserEl.textContent : classifyStage(c)[1] + '.';
      return `<div class="portrait"><b><a href="#country/${iso3}">${c.n}</a></b>
        <span style="color:var(--muted);font-size:.8rem"> · median age ${fmt(c.ma, 1)} → ${fmt(c.ma50, 1)} · TFR ${fmt(c.tfr, 2)}</span>
        <p>${teaser}</p></div>`;
    });
  holder.innerHTML = cards.join('');
}

/* ------------------------------------------------------------------- boot */
document.addEventListener('DOMContentLoaded', () => {
  drawShapes();
  drawLifecycle();
  loadData().then(featured => {
    drawTFR(featured);
    drawSupport(featured);
    computeScores();
    parityCheck();
    renderSliders();
    wirePresets();
    renderMap();
    drawCurrentAccount();
    wirePicker();
    wireViewToggle();
    buildPortraits();
    wireRouting();
  }).catch(err => {
    document.getElementById('map').innerHTML =
      '<div class="ph">Could not load the dataset (' + err + '). The prose and baked figures above still work.</div>';
  });
});
