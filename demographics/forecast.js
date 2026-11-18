/* The Shape of People to Come — section 9 (the forecast) and the
   "follow one country through every figure" thread.

   Loaded after app.js and shares its top-level tokens and helpers (state, CC,
   BASE, grid, mount, sized, fetchDetail …). Everything here is computed in the
   browser from the same pyramids the atlas uses: data/world.json (built by
   scripts/build_demographics_world.py) plus data/countries/<ISO3>.json. There
   is one implementation of each quantity, so a figure, the ledger and the
   prose cannot disagree; fcAuditProse() rewrites any number in the text that
   drifts from what the data says and logs it. */
'use strict';

const FC = {
  years: null, i25: -1, i50: -1,
  ents: new Map(),          // code -> derived entity
  base: null,               // Promise: world + featured ten
  focus: null,              // ISO3 being followed, or null
  k: 0,                     // working-life extension by 2050 (years)
  drawn: false,
  mounted: {},
};
const FC_WORLD = 'WLD';
const FC_SHORT = {
  CHN: 'China', JPN: 'Japan', KOR: 'South Korea', DEU: 'Germany', ITA: 'Italy',
  RUS: 'Russia', USA: 'United States', MEX: 'Mexico', IND: 'India', NGA: 'Nigeria',
};
const FC_LIGHT = '#9DB4DA';                       // light step of the accent hue
const FC_DIVERGING = [                            // warm pole · neutral gray · cool pole
  [0, '#B83A2E'], [0.25, '#E0A9A2'], [0.5, '#F0EFEC'], [0.75, '#9DB4DA'], [1, '#1F4E9E'],
];
const FC_ZMAX = 1.5;                              // pp/yr at full saturation
// "By birth year" table: six countries by four cohorts. `rho` is the
// illustrative replacement rate behind the contribution levels; the ratio
// between two cohorts does not depend on it.
const FC_COHORT = { iso: ['USA', 'KOR', 'JPN', 'DEU', 'CHN', 'NGA'], born: [1950, 1975, 1990, 2000], rho: 0.40 };

const fcName = code => code === FC_WORLD ? 'World'
  : (FC_SHORT[code] || (state.countries[code] && state.countries[code].n) || code);
const fcEsc = s => String(s).replace(/[&<>"]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch]));
const fcSigned = (v, d = 1) => (v >= 0 ? '+' : '−') + Math.abs(v).toFixed(d);
const fcSum = (row, a, b) => { let s = 0; for (let i = a; i <= b; i++) s += row[i]; return s; };
const fcArgmax = a => a.indexOf(Math.max.apply(null, a));
const fcFeatured = () => (state.meta && state.meta.featured) || [];

/* ------------------------------------------------------------ the profiles */
// KEEP IN SYNC with drawLifecycle() in app.js and stylized_profiles() in
// scripts/build_demographics_data.py. `k` moves the exit from work k years
// later and leaves consumption alone; k = 0 is the Figure 3 curve. Weights are
// averaged inside each 5-year bin to match the pyramids.
const FC_PROFILES = new Map();
function fcWeights(k) {
  const key = Math.round(k * 10);
  if (FC_PROFILES.has(key)) return FC_PROFILES.get(key);
  const kk = key / 10, yl = [], c = [];
  for (let a = 0; a <= 100; a++) {
    const aa = Math.min(a, 90);
    const ramp = 100 / (1 + Math.exp(-(aa - 30) / 5.5));
    const fade = 1 / (1 + Math.exp((aa - (61 + kk)) / 4.5));
    yl.push(Math.max(0, ramp * fade * 1.19 - (aa < 15 ? 100 : 0)));
    let v = 34 + 24 / (1 + Math.exp(-(aa - 10) / 4));
    v += 12 / (1 + Math.exp(-(aa - 22) / 3));
    v += 10 / (1 + Math.exp(-(aa - 74) / 6));
    c.push(v);
  }
  const bin = v => {
    const out = [];
    for (let b = 0; b < 100; b += 5) out.push((v[b] + v[b + 1] + v[b + 2] + v[b + 3] + v[b + 4]) / 5);
    out.push(v[100]);
    return out;
  };
  const w = { yl: bin(yl), c: bin(c) };
  FC_PROFILES.set(key, w);
  return w;
}
function fcEsr(row, k) {
  const w = fcWeights(k);
  let n = 0, d = 0;
  for (let b = 0; b < 21; b++) { n += w.yl[b] * row[b]; d += w.c[b] * row[b]; }
  return n / d;
}

/* ------------------------------------------------------------ the entities */
function fcCrossDown(series, thr, years) {
  for (let j = 1; j < series.length; j++) {
    const a = series[j - 1], b = series[j];
    if (a === null || b === null || a === undefined || b === undefined) continue;
    if (a >= thr && b < thr) return years[j - 1] + (years[j] - years[j - 1]) * (a - thr) / (a - b);
  }
  return null;
}

function fcAddEntity(code, pyr, series) {
  if (FC.ents.has(code)) return FC.ents.get(code);
  const years = pyr.years;
  if (!FC.years) { FC.years = years; FC.i25 = years.indexOf(2025); FC.i50 = years.indexOf(2050); }
  const i25 = FC.i25, i50 = FC.i50;
  const P = years.map((_, j) => pyr.m[j].map((v, b) => v + pyr.f[j][b]));
  const esr = P.map(row => fcEsr(row, 0));
  const g = [];
  for (let j = 0; j < years.length - 1; j++) g.push(100 * Math.log(esr[j + 1] / esr[j]) / (years[j + 1] - years[j]));
  const e = {
    code, name: fcName(code), P, esr, g,
    sr: P.map(row => fcSum(row, 4, 12) / fcSum(row, 13, 20)),      // 20–64 over 65+
    wa: P.map(row => fcSum(row, 4, 12)),
    pop: P.map(row => fcSum(row, 0, 20)),
    tfr: series && series.tfr ? series.tfr : null,
  };
  // average demographic growth term 2025→2050 if working lives are k years longer by 2050
  e.g2550 = k => 100 * Math.log(fcEsr(P[i50], k) / esr[i25]) / (years[i50] - years[i25]);
  e.dEsr50 = esr[i50] / esr[i25] - 1;
  e.kStar = 0;                                   // break-even extension; null = more than 15 years
  if (esr[i50] < esr[i25]) {
    e.kStar = null;
    for (let k10 = 1; k10 <= 150; k10++) {
      if (fcEsr(P[i50], k10 / 10) >= esr[i25]) { e.kStar = k10 / 10; break; }
    }
  }
  e.iWaPeak = fcArgmax(e.wa); e.iEsrPeak = fcArgmax(esr); e.iPopPeak = fcArgmax(e.pop);
  e.iDivPeak = fcArgmax(g);
  e.srCross2 = fcCrossDown(e.sr, 2, years);
  // share of each group in year t that was already born in 2025
  e.born = years.map((y, j) => {
    if (j < i25) return null;
    const lo = Math.round((y - years[i25]) / 5), row = P[j], top = Math.min(lo, 20);
    const w0 = fcWeights(0);
    let pn = 0, pd = 0, cn = 0, cd = 0;
    for (let b = 0; b < 21; b++) {
      pd += w0.yl[b] * row[b]; cd += w0.c[b] * row[b];
      if (b >= lo) { pn += w0.yl[b] * row[b]; cn += w0.c[b] * row[b]; }
    }
    return {
      wa: lo <= 4 ? 1 : lo >= 13 ? 0 : fcSum(row, lo, 12) / fcSum(row, 4, 12),
      old: lo <= 13 ? 1 : fcSum(row, top, 20) / fcSum(row, 13, 20),
      all: fcSum(row, top, 20) / fcSum(row, 0, 20),
      prod: pn / pd, cons: cn / cd,
    };
  });
  FC.ents.set(code, e);
  return e;
}

/* ------------------------------------------------ the two cohort identities */
// Cohort b is the people aged 0–4 in year b; five years later they are the 5–9
// bin, and so on. It is a resident cohort, so migration is included. Both
// functions return null when the years they need fall off the 1950–2100 grid.

// 1 · Career growth term (pp/yr): section 4's growth identity averaged over
// the forty years the cohort is aged 25 to 64.
function fcCareerG(e, b) {
  const yrs = FC.years, i = yrs.indexOf(b + 25), j = yrs.indexOf(b + 65);
  return i < 0 || j < 0 ? null : 100 * Math.log(e.esr[j] / e.esr[i]) / (yrs[j] - yrs[i]);
}
// 2 · Pay-as-you-go arithmetic: contribution rate = replacement rate / workers
// per retiree. This is the mean of retirees per worker over the nine grid years
// b+20 … b+60; multiply it by a replacement rate to get the contribution rate.
function fcCareerLoad(e, b) {
  const yrs = FC.years, i = yrs.indexOf(b + 20), j = yrs.indexOf(b + 60);
  if (i < 0 || j < 0) return null;
  let s = 0;
  for (let t = i; t <= j; t++) s += 1 / e.sr[t];
  return s / (j - i + 1);
}

function fcEnsureBase() {
  if (!FC.base) {
    // the featured ten, plus any country the cohort table needs that is not one of them
    const feat = fcFeatured(), need = feat.concat(FC_COHORT.iso.filter(c => !feat.includes(c) && state.countries[c]));
    FC.base = Promise.all([
      fetch('data/world.json').then(r => { if (!r.ok) throw new Error('world.json missing'); return r.json(); }),
      ...need.map(iso => fetchDetail(iso)),
    ]).then(([world, ...ds]) => {
      fcAddEntity(FC_WORLD, world.pyramid, null);
      ds.forEach((d, i) => fcAddEntity(need[i], d.pyramid, d.series));
      fcParity();
    }).catch(err => { FC.base = null; throw err; });
  }
  return FC.base;
}
async function fcEnsureEntity(code) {
  if (FC.ents.has(code)) return FC.ents.get(code);
  const d = await fetchDetail(code);
  return fcAddEntity(code, d.pyramid, d.series);
}

// The support ratio here comes from 5-year bins; the shipped one from single
// ages. They must agree to the third decimal or the section is not describing
// the same object as the atlas.
function fcParity() {
  fcFeatured().forEach(iso => {
    const e = FC.ents.get(iso), shipped = state.countries[iso] && state.countries[iso].esr;
    if (e && shipped && Math.abs(e.esr[FC.i25] - shipped) > 0.004)
      console.warn('[forecast] support-ratio parity drift for', iso, e.esr[FC.i25].toFixed(4), 'vs shipped', shipped);
  });
}

/* ---------------------------------------------------------------- rows */
// World first, then the featured ten in the order their dividend ended; a
// followed country outside the ten is added at the top.
function fcRows() {
  const feat = fcFeatured().filter(c => FC.ents.has(c))
    .sort((a, b) => FC.ents.get(a).iEsrPeak - FC.ents.get(b).iEsrPeak || FC.ents.get(a).iDivPeak - FC.ents.get(b).iDivPeak);
  const rows = [FC_WORLD, ...feat];
  if (FC.focus && FC.ents.has(FC.focus) && !rows.includes(FC.focus)) rows.unshift(FC.focus);
  return rows.map(c => FC.ents.get(c));
}
const fcNarrow = el => el.clientWidth < 560;
// These figures are sized by their row count, not their width. app.js's RESIZER
// autosizes any figure without declared proportions to its container, which has
// no height of its own, so declare a fixed height through the same mechanism.
const fcFixedHeight = (el, h) => sized(el, 1, h, h);
const fcLabel = (e, narrow) => narrow ? (e.code === FC_WORLD ? 'World' : e.code) : e.name;

/* --------------------------------------------- Fig 6 · the certainty horizon */
function fcDrawHorizon() {
  const el = FC.mounted.horizon || (FC.mounted.horizon = mount('fig-horizon'));
  const w = FC.ents.get(FC_WORLD), narrow = fcNarrow(el);
  const yrs = FC.years.slice(FC.i25), born = w.born.slice(FC.i25);
  const mk = (key, name, color, width) => ({
    x: yrs, y: born.map(b => +(100 * b[key]).toFixed(1)), name, type: 'scatter', mode: 'lines',
    line: { color, width }, hovertemplate: `%{x} · %{y:.0f}% of ${name} already born<extra></extra>`,
  });
  const traces = [
    mk('old', 'retirees (65+)', ORANGE, 2.4),
    mk('wa', 'workers (20–64)', ACCENT, 2.4),
    mk('all', 'everyone', MUTED, 1.6),
  ];
  const lab = { showarrow: false, font: { size: narrow ? 11 : 12.5, color: INK } };
  const layout = Object.assign({}, BASE, {
    margin: { l: 50, r: 16, t: 34, b: 40 },
    legend: { orientation: 'h', x: 0.5, xanchor: 'center', y: -0.14 },
    xaxis: grid({ fixedrange: true, range: [2025, 2100.5], tickvals: [2025, 2045, 2060, 2075, 2090, 2100] }),
    yaxis: grid({ title: { text: 'share already born in 2025', font: { size: 13, color: MUTED } },
      fixedrange: true, range: [0, 114], ticksuffix: '%', tickvals: [0, 25, 50, 75, 100] }),
    shapes: [2045, 2090].map(x => ({ type: 'line', x0: x, x1: x, y0: 0, y1: 100, line: { color: MUTED, width: 1 } })),
    annotations: [
      Object.assign({ x: 2045, y: 107, text: narrow ? 'workers known<br>to 2045' : 'every worker is already born → 2045', xanchor: 'center' }, lab),
      Object.assign({ x: 2090, y: 107, text: narrow ? 'retirees known<br>to 2090' : 'every retiree is already born → 2090', xanchor: 'right' }, lab),
      Object.assign({ x: 2066, y: 54, text: 'workers', xanchor: 'left', xshift: 8 }, lab),
      Object.assign({ x: 2068, y: 96, text: 'retirees', xanchor: 'center', yshift: -12 }, lab),
      Object.assign({ x: 2040, y: 79, text: 'everyone', xanchor: 'right', xshift: -8 }, lab),
    ],
  });
  layout.height = sized(el, 0.7, 440, 720);
  Plotly.react(el, traces, layout, NOPAD);
}

/* ----------------------------------------- Fig 7 · the demographic growth term */
function fcDrawGrowth() {
  const el = FC.mounted.growth || (FC.mounted.growth = mount('fig-growth'));
  const narrow = fcNarrow(el);
  const rows = fcRows().slice().reverse();                // plotly draws the first row at the bottom
  const yrs = FC.years, mids = yrs.slice(0, -1).map((y, j) => (y + yrs[j + 1]) / 2);
  const labels = rows.map(e => (FC.focus === e.code ? '<b>' + fcEsc(fcLabel(e, narrow)) + '</b>' : fcEsc(fcLabel(e, narrow))));
  const trace = {
    type: 'heatmap', x: mids, y: labels, z: rows.map(e => e.g.map(v => +v.toFixed(3))),
    customdata: rows.map(e => e.g.map((_, j) => [yrs[j], yrs[j + 1], e.name])),
    zmin: -FC_ZMAX, zmax: FC_ZMAX, colorscale: FC_DIVERGING, xgap: 2, ygap: 2,
    hovertemplate: '<b>%{customdata[2]}</b> %{customdata[0]}–%{customdata[1]}<br>%{z:+.2f} pp/yr<extra></extra>',
    showscale: !narrow,
    colorbar: { thickness: 10, len: 0.7, outlinewidth: 0, tickvals: [-1.5, -1, -0.5, 0, 0.5, 1, 1.5],
      ticktext: ['−1.5', '−1.0', '−0.5', '0', '+0.5', '+1.0', '+1.5'], tickfont: { size: 11, color: MUTED },
      title: { text: 'pp / yr', font: { size: 11.5, color: MUTED } } },
  };
  const shapes = [2025, 2045].map(x => ({ type: 'line', xref: 'x', yref: 'paper', x0: x, x1: x, y0: 0, y1: 1,
    line: { color: INK, width: x === 2025 ? 1.6 : 1 } }));
  const fi = rows.findIndex(e => e.code === FC.focus);
  if (fi >= 0) shapes.push({ type: 'rect', xref: 'paper', yref: 'y', x0: 0, x1: 1, y0: fi - 0.5, y1: fi + 0.5,
    line: { color: INK, width: 1.6 }, fillcolor: 'rgba(0,0,0,0)' });
  const top = { yref: 'paper', y: 1.01, yanchor: 'bottom', showarrow: false, font: { size: 11.5, color: MUTED } };
  const layout = Object.assign({}, BASE, {
    margin: { l: narrow ? 48 : 104, r: narrow ? 10 : 6, t: 38, b: 36 },
    height: fcFixedHeight(el, Math.max(360, rows.length * (narrow ? 30 : 38) + 96)),
    xaxis: grid({ fixedrange: true, range: [1950, 2100], dtick: narrow ? 50 : 25, tickangle: 0, showgrid: false }),
    yaxis: { fixedrange: true, automargin: false, tickfont: { size: narrow ? 11 : 12.5, color: INK }, showgrid: false },
    shapes,
    annotations: [
      Object.assign({ x: 2025, text: narrow ? '2025' : 'history ← 2025', xanchor: narrow ? 'center' : 'right', xshift: narrow ? 0 : -4 }, top),
      Object.assign({ x: 2045, text: narrow ? '2045' : '2045 → workers not yet born', xanchor: narrow ? 'center' : 'left', xshift: narrow ? 0 : 4 }, top),
    ],
  });
  Plotly.react(el, [trace], layout, NOPAD);
  if (!el._fcClick) {
    el._fcClick = true;
    el.on('plotly_click', ev => {
      const cd = ev.points && ev.points[0] && ev.points[0].customdata;
      const hit = cd && [...FC.ents.values()].find(e => e.name === cd[2]);
      if (hit && hit.code !== FC_WORLD) fcSetFocus(hit.code === FC.focus ? null : hit.code);
    });
  }
  fcGrowthTable();
}

// Table view of Figure 7: decade averages, so no value is readable by hover alone.
function fcGrowthTable() {
  const host = document.getElementById('growth-table');
  if (!host) return;
  const yrs = FC.years, decades = [];
  for (let j = 0; j + 1 < yrs.length - 1; j += 2) decades.push(j);
  const head = decades.map(j => `<th scope="col">${yrs[j]}s</th>`).join('');
  const body = fcRows().map(e => `<tr${FC.focus === e.code ? ' class="is-focus"' : ''}><th scope="row">${fcEsc(e.name)}</th>${
    decades.map(j => { const v = (e.g[j] + e.g[j + 1]) / 2; return `<td>${fcSigned(v, 1)}</td>`; }).join('')}</tr>`).join('');
  host.innerHTML = `<table class="ledger tight"><thead><tr><th scope="col">pp / yr</th>${head}</tr></thead><tbody>${body}</tbody></table>`;
}

/* ------------------------------------------------------ Fig 8 · the hurdle */
function fcDrawHurdle() {
  const el = FC.mounted.hurdle || (FC.mounted.hurdle = mount('fig-hurdle'));
  const narrow = fcNarrow(el), k = FC.k;
  const rows = fcRows().slice().sort((a, b) => b.g2550(0) - a.g2550(0));   // worst ends up on top
  const y = rows.map(e => (FC.focus === e.code ? '<b>' + fcEsc(fcLabel(e, narrow)) + '</b>' : fcEsc(fcLabel(e, narrow))));
  const x0 = rows.map(e => e.g2550(0)), xk = rows.map(e => e.g2550(k));
  const lx = [], ly = [];
  rows.forEach((e, i) => { lx.push(x0[i], xk[i], null); ly.push(y[i], y[i], null); });
  const cd = rows.map(e => [e.name, e.code]);
  const traces = [
    { x: lx, y: ly, type: 'scatter', mode: 'lines', line: { color: FC_LIGHT, width: 2 }, hoverinfo: 'skip', showlegend: false },
    { x: x0, y, customdata: cd, name: "today's working lives", type: 'scatter', mode: 'markers',
      marker: { color: FC_LIGHT, size: 12, line: { color: PAPER, width: 2 } },
      hovertemplate: '<b>%{customdata[0]}</b><br>today\'s working lives: %{x:+.2f} pp/yr<extra></extra>' },
    { x: xk, y, customdata: cd, name: `working lives +${k.toFixed(1)} years by 2050`, type: 'scatter', mode: 'markers',
      visible: k > 0, showlegend: k > 0,
      marker: { color: ACCENT, size: 12, line: { color: PAPER, width: 2 } },
      hovertemplate: `<b>%{customdata[0]}</b><br>+${k.toFixed(1)} years by 2050: %{x:+.2f} pp/yr<extra></extra>` },
  ];
  // fixed axis so the slider moves the dots, not the scale
  const all = rows.map(e => [e.g2550(0), e.g2550(10)]).flat();
  const lo = Math.min.apply(null, all) - 0.12, hi = Math.max.apply(null, all) + 0.12;
  const note = e => e.kStar === 0 ? 'no gap' : e.kStar === null ? (narrow ? '> 15 y' : 'break-even > 15 y')
    : (narrow ? `+${e.kStar.toFixed(1)} y` : `break-even +${e.kStar.toFixed(1)} y`);
  const ticks = [];
  for (let t = Math.ceil(lo * 2) / 2; t <= hi; t += narrow ? 1 : 0.5) ticks.push(+t.toFixed(1));
  const layout = Object.assign({}, BASE, {
    margin: { l: narrow ? 48 : 104, r: narrow ? 56 : 132, t: 30, b: 44 },
    height: fcFixedHeight(el, Math.max(380, rows.length * (narrow ? 32 : 40) + 110)),
    legend: { orientation: 'h', x: 0.5, xanchor: 'center', y: -0.16 },
    xaxis: grid({ title: { text: narrow ? 'growth term 2025–2050 (pp / yr)' : 'demographic growth term, 2025–2050 (pp / yr)', font: { size: 13, color: MUTED } },
      fixedrange: true, range: [lo, hi], zeroline: true, zerolinecolor: INK, zerolinewidth: 1.4,
      tickvals: ticks, ticktext: ticks.map(t => t === 0 ? '0' : fcSigned(t, 1)), tickangle: 0 }),
    yaxis: { fixedrange: true, tickfont: { size: narrow ? 11 : 12.5, color: INK }, showgrid: false },
    shapes: [
      { type: 'rect', xref: 'x', yref: 'paper', x0: lo, x1: 0, y0: 0, y1: 1, fillcolor: 'rgba(184,58,46,.055)', line: { width: 0 }, layer: 'below' },
    ],
    annotations: rows.map((e, i) => ({ xref: 'paper', x: 1, xanchor: 'left', xshift: 8, y: y[i], text: note(e),
      showarrow: false, font: { size: narrow ? 10.5 : 11.5, color: MUTED } }))
      .concat([
        { xref: 'x', yref: 'paper', x: lo, y: 1.0, yanchor: 'bottom', xanchor: 'left', xshift: 4, text: 'headwind', showarrow: false, font: { size: 11.5, color: MUTED } },
        { xref: 'x', yref: 'paper', x: hi, y: 1.0, yanchor: 'bottom', xanchor: 'right', xshift: -4, text: 'tailwind', showarrow: false, font: { size: 11.5, color: MUTED } },
      ]),
  });
  Plotly.react(el, traces, layout, NOPAD);
  if (!el._fcClick) {
    el._fcClick = true;
    el.on('plotly_click', ev => {
      const c = ev.points && ev.points[0] && ev.points[0].customdata && ev.points[0].customdata[1];
      if (c && c !== FC_WORLD) fcSetFocus(c === FC.focus ? null : c);
    });
  }
  const out = document.getElementById('lever-out');
  if (out) {
    const feat = fcFeatured().map(c => FC.ents.get(c)).filter(Boolean);
    const neg = feat.filter(e => e.g2550(k) < 0).length;
    out.textContent = k === 0
      ? `With working lives as they are, ${neg} of the ${feat.length} featured countries face a negative term.`
      : `With working lives ${k.toFixed(1)} years longer by 2050, ${neg} of the ${feat.length} still face a negative term.`;
  }
}

/* -------------------------------------------------------------- the ledger */
// filled: everyone the claim rests on is already born · half: partly · open: mostly not yet born
function fcCert(level) {
  const t = ['rests mostly on births that have not happened', 'rests partly on births that have not happened',
    'rests only on people already born'][level];
  return `<span class="cert c${level}" role="img" aria-label="${t}" title="${t}"></span>`;
}
function fcLedger() {
  const host = document.getElementById('ledger');
  if (!host) return;
  const yrs = FC.years, last = yrs.length - 1;
  const when = (y, adultsOnly) => y <= 2045 ? (adultsOnly || y <= 2025 ? 2 : 1) : y <= 2065 ? 1 : 0;
  const peak = (i, adultsOnly) => {
    if (i >= last) return `<td>${fcCert(0)}after 2100</td>`;
    const y = yrs[i];
    return `<td class="${y < 2025 ? 'past' : ''}">${fcCert(when(y, adultsOnly))}${y <= 2025 ? '' : 'c. '}${y}</td>`;
  };
  const cross = e => {
    if (e.srCross2 === null) return `<td>${fcCert(0)}after 2100</td>`;
    const y = Math.round(e.srCross2);
    return `<td class="${y < 2025 ? 'past' : ''}">${fcCert(when(y, true))}c. ${y}</td>`;
  };
  const body = fcRows().map(e => {
    const g = e.g2550(0);
    const kcell = e.kStar === 0 ? 'none' : e.kStar === null ? 'over 15 years' : `+${e.kStar.toFixed(1)} years`;
    const name = e.code === FC_WORLD ? '<b>World</b>'
      : `<button type="button" class="rowpick" data-code="${e.code}" aria-pressed="${FC.focus === e.code}">${fcEsc(e.name)}</button>`;
    return `<tr${FC.focus === e.code ? ' class="is-focus"' : ''}>
      <th scope="row">${name}</th>
      ${peak(e.iWaPeak, true)}${peak(e.iEsrPeak, false)}${cross(e)}
      <td>${fcCert(1)}${fcSigned(g, 2)}</td>
      <td>${fcCert(1)}${fcSigned(100 * e.dEsr50, 0)}%</td>
      <td>${fcCert(1)}${kcell}</td>
      ${peak(e.iPopPeak, false)}
    </tr>`;
  }).join('');
  host.innerHTML = `<table class="ledger">
    <thead><tr>
      <th scope="col">Country</th>
      <th scope="col">Working-age<br>peak</th>
      <th scope="col">Dividend<br>ends</th>
      <th scope="col">Two workers<br>per retiree</th>
      <th scope="col">Growth term<br>2025–50 <small>pp/yr</small></th>
      <th scope="col">Support ratio<br>by 2050</th>
      <th scope="col">Break-even<br>working life</th>
      <th scope="col">Population<br>peak</th>
    </tr></thead><tbody>${body}</tbody></table>`;
  host.querySelectorAll('.rowpick').forEach(b => b.addEventListener('click', () =>
    fcSetFocus(b.dataset.code === FC.focus ? null : b.dataset.code)));
}

/* ------------------------------------------- the two identities by birth year */
// One table, two layouts: the measures side by side where there is room, and
// stacked as two row groups on a narrow screen so no column is off-screen.
function fcCohortTable() {
  const host = document.getElementById('cohort-table');
  if (!host) return;
  const born = FC_COHORT.born, rho = FC_COHORT.rho;
  const ents = FC_COHORT.iso.map(c => FC.ents.get(c)).filter(Boolean);
  const dash = '<td>–</td>';
  const cols = [
    { head: 'Career growth term <small>pp/yr, by birth year</small>',
      cell: (e, b) => { const v = fcCareerG(e, b); return v === null ? dash : `<td>${fcSigned(v, 2)}</td>`; } },
    { head: `Contribution at ${Math.round(100 * rho)}% replacement <small>by birth year</small>`,
      cell: (e, b) => { const v = fcCareerLoad(e, b); return v === null ? dash : `<td>${(100 * rho * v).toFixed(1)}%</td>`; } },
  ];
  const years = born.map(b => `<th scope="col">${b}</th>`).join('');
  const row = (e, parts) => `<tr${FC.focus === e.code ? ' class="is-focus"' : ''}><th scope="row">${fcEsc(e.name)}</th>${parts}</tr>`;
  const tbl = '<table class="ledger" aria-labelledby="cohort-identities" aria-describedby="cohort-key">';
  if (fcNarrow(host)) {
    host.innerHTML = `${tbl}<thead><tr><th scope="col">Country</th>${years}</tr></thead>${cols.map(c =>
      `<tbody><tr><th scope="rowgroup" colspan="${born.length + 1}">${c.head}</th></tr>${
        ents.map(e => row(e, born.map(b => c.cell(e, b)).join(''))).join('')}</tbody>`).join('')}</table>`;
    return;
  }
  host.innerHTML = `${tbl}<colgroup></colgroup>${cols.map(() => `<colgroup span="${born.length}"></colgroup>`).join('')}
    <thead><tr><th scope="col" rowspan="2">Country</th>${cols.map(c => `<th scope="colgroup" colspan="${born.length}">${c.head}</th>`).join('')}</tr>
    <tr>${cols.map(() => years).join('')}</tr></thead>
    <tbody>${ents.map(e => row(e, cols.map(c => born.map(b => c.cell(e, b)).join('')).join(''))).join('')}</tbody></table>`;
}

/* ------------------------------------------------------------- prose audit */
// Every number the new prose states is tagged data-fc="key"; this recomputes
// each from the data and replaces the text if it has drifted.
function fcProseValues() {
  const m = {}, yrs = FC.years;
  // Figure 5 (needs only the summary file)
  const rows = Object.values(state.countries).filter(c => c.ca !== null && c.ca !== undefined && c.ma && c.pop > 1000);
  if (rows.length >= 30) {
    const grp = (lo, hi) => rows.filter(c => c.ma >= lo && c.ma < hi);
    const young = grp(0, 25), old = grp(40, 200), mean = a => a.reduce((s, c) => s + c.ca, 0) / a.length;
    m['ca:young:pos'] = String(young.filter(c => c.ca > 0).length); m['ca:young:n'] = String(young.length);
    m['ca:young:mean'] = fcSigned(mean(young), 1);
    m['ca:old:pos'] = String(old.filter(c => c.ca > 0).length); m['ca:old:n'] = String(old.length);
    m['ca:old:mean'] = fcSigned(mean(old), 1);
    const mx = rows.reduce((s, c) => s + c.ma, 0) / rows.length, my = mean(rows);
    let sxy = 0, sxx = 0, syy = 0;
    rows.forEach(c => { sxy += (c.ma - mx) * (c.ca - my); sxx += (c.ma - mx) ** 2; syy += (c.ca - my) ** 2; });
    m['ca:r'] = (sxy / Math.sqrt(sxx * syy)).toFixed(2);
  }
  const w = FC.ents.get(FC_WORLD);
  if (!w) return m;
  [2050, 2060, 2070].forEach(y => {
    const b = w.born[yrs.indexOf(y)];
    m['born:wa:' + y] = Math.round(100 * b.wa) + '%'; m['born:all:' + y] = Math.round(100 * b.all) + '%';
    m['born:prod:' + y] = Math.round(100 * b.prod) + '%'; m['born:cons:' + y] = Math.round(100 * b.cons) + '%';
  });
  m['born:old:2100'] = Math.round(100 * w.born[yrs.length - 1].old) + '%';
  m['world:esrpeak'] = String(yrs[w.iEsrPeak]);
  m['world:esrtrough'] = String(yrs[w.esr.indexOf(Math.min.apply(null, w.esr))]);
  m['world:g'] = fcSigned(w.g2550(0), 1);
  FC.ents.forEach((e, code) => {
    m['g:' + code] = fcSigned(e.g2550(0), 1);
    m['k:' + code] = e.kStar === null ? '15+' : e.kStar.toFixed(1);
    m['desr:' + code] = fcSigned(100 * e.dEsr50, 0) + '%';
    m['divpk:' + code] = fcSigned(e.g[e.iDivPeak], 1);
    if (e.srCross2 !== null) m['sr2:' + code] = String(Math.round(e.srCross2));
    if (e.tfr) { const x = fcCrossDown(e.tfr, 2.1, yrs); if (x !== null) m['tfrx:' + code] = String(Math.round(x)); }
  });
  // the cohort identities: growth term, contribution level, and the ratio of
  // the contribution rate between an earlier cohort a and a later cohort b
  m['coh:rho'] = Math.round(100 * FC_COHORT.rho) + '%';
  FC_COHORT.iso.forEach(code => {
    const e = FC.ents.get(code);
    if (!e) return;
    FC_COHORT.born.forEach(b => {
      const g = fcCareerG(e, b), load = fcCareerLoad(e, b);
      if (g !== null) m[`coh:g:${code}:${b}`] = fcSigned(g, 2);
      if (load === null) return;
      m[`coh:c:${code}:${b}`] = (100 * FC_COHORT.rho * load).toFixed(1) + '%';
      FC_COHORT.born.forEach(a => {
        const from = a < b ? fcCareerLoad(e, a) : null;
        if (from !== null) m[`coh:x:${code}:${a}:${b}`] = (load / from).toFixed(1);
      });
    });
  });
  return m;
}
function fcAuditProse() {
  const vals = fcProseValues();
  document.querySelectorAll('[data-fc]').forEach(el => {
    const v = vals[el.dataset.fc];
    if (v === undefined) return;
    if (el.textContent.trim() !== v) {
      console.warn('[forecast] prose drift:', el.dataset.fc, JSON.stringify(el.textContent.trim()), '→', JSON.stringify(v));
      el.textContent = v;
    }
  });
}

/* --------------------------------------------------- follow-a-country thread */
function fcTakeaways() {
  const set = (key, html) => document.querySelectorAll(`[data-tk="${key}"]`).forEach(el => { el.innerHTML = html ? ' ' + html : ''; });
  const code = FC.focus, e = code && FC.ents.get(code), c = code && state.countries[code];
  if (!e) { ['tfr', 'sr', 'ca', 'horizon', 'growth', 'hurdle'].forEach(k => set(k, '')); return; }
  const yrs = FC.years, i25 = FC.i25, nm = `<b>${fcEsc(e.name)}:</b>`;
  // fertility
  if (e.tfr) {
    const hist = e.tfr.slice(0, i25 + 1).filter(v => v !== null && v !== undefined);
    const mx = Math.max.apply(null, hist), x = fcCrossDown(e.tfr, 2.1, yrs);
    const tail = x === null ? (e.tfr[i25] < 2.1 ? 'below replacement for the whole period' : 'above replacement through 2100 on the UN medium path')
      : x <= 2025 ? `below replacement since about ${Math.round(x)}` : `projected to cross replacement around ${Math.round(x)}`;
    set('tfr', `${nm} peaked at ${mx.toFixed(2)} births per woman in ${yrs[e.tfr.indexOf(mx)]}, now ${(+e.tfr[i25]).toFixed(2)}; ${tail}.`);
  } else set('tfr', '');
  // headcount ratio
  const mn = Math.min.apply(null, e.sr), x2 = e.srCross2;
  const when = x2 === null ? 'stays above two workers per retiree through 2100'
    : x2 < 2025 ? `fell through two workers per retiree around ${Math.round(x2)}` : `reaches two workers per retiree around ${Math.round(x2)}`;
  set('sr', `${nm} ${e.sr[i25].toFixed(1)} workers per retiree today; ${when}; low point ${mn.toFixed(2)} in ${yrs[e.sr.indexOf(mn)]}.`);
  // current account
  set('ca', c && c.ca !== null && c.ca !== undefined
    ? `${nm} median age ${(+c.ma).toFixed(1)}, current account ${fcSigned(c.ca, 1)}% of GDP.` : '');
  // horizon
  const b50 = e.born[yrs.indexOf(2050)], b70 = e.born[yrs.indexOf(2070)];
  set('horizon', `${nm} ${Math.round(100 * b50.wa)}% of its 2050 working-age population and ${Math.round(100 * b70.wa)}% of its 2070 one are already born — somewhere; migration decides how many of them are residents.`);
  // growth term
  const ip = e.iDivPeak, ye = yrs[e.iEsrPeak];
  const turn = e.iEsrPeak >= yrs.length - 1 ? 'the support ratio is still rising in 2100'
    : ye <= 2025 ? `the support ratio peaked in ${ye}` : `the support ratio keeps rising until about ${ye}`;
  set('growth', `${nm} the term peaked at ${fcSigned(e.g[ip], 2)} pp/yr in ${yrs[ip]}–${yrs[ip + 1]}; ${turn}; it averages ${fcSigned(e.g2550(0), 2)} over 2025–2050.`);
  // hurdle
  set('hurdle', e.kStar === 0 ? `${nm} no gap to close — its support ratio is higher in 2050 than today.`
    : e.kStar === null ? `${nm} more than fifteen extra working years would be needed to hold the 2025 support ratio.`
    : `${nm} holding the 2025 support ratio takes working lives about ${e.kStar.toFixed(1)} years longer by 2050.`);
}

// Which country a trace drawn by app.js belongs to: Figure 4 carries the ISO
// code as its legend group, Figure 2 only the country's name.
function fcTraceCode(t) {
  if (t.meta === '__focus') return '__focus';
  if (t.legendgroup && state.countries[t.legendgroup]) return t.legendgroup;
  return (FC.nameToCode && FC.nameToCode[t.name]) || null;
}

// Emphasise the followed country in a line figure drawn by app.js; if it is not
// one of that figure's series, overlay it.
function fcEmphasizeLines(elId, kind) {
  const el = document.getElementById(elId);
  if (!el || !el.data) return;
  const drop = [];
  el.data.forEach((t, i) => { if (t.meta === '__focus') drop.push(i); });
  if (drop.length) Plotly.deleteTraces(el, drop);
  const code = FC.focus, e = code && FC.ents.get(code);
  const has = !!code && el.data.some(t => fcTraceCode(t) === code);
  Plotly.restyle(el, {
    'line.width': el.data.map(t => (code && fcTraceCode(t) === code) ? 4 : 2.2),
    opacity: el.data.map(t => (!code || fcTraceCode(t) === code) ? 1 : 0.28),
  });
  if (!e || has) return;
  const yrs = FC.years, cut = FC.i25, color = CC[code] || INK, add = [];
  if (kind === 'tfr' && e.tfr) {
    add.push({ x: yrs.slice(0, cut + 1), y: e.tfr.slice(0, cut + 1), name: e.name, meta: '__focus', type: 'scatter', mode: 'lines',
      line: { color, width: 4 }, hovertemplate: `<b>${fcEsc(e.name)}</b> %{x}: %{y:.2f}<extra></extra>` });
  } else if (kind === 'sr') {
    add.push({ x: yrs.slice(0, cut + 1), y: e.sr.slice(0, cut + 1), name: e.name, legendgroup: '__focus', meta: '__focus', type: 'scatter', mode: 'lines',
      line: { color, width: 4 }, hovertemplate: `<b>${fcEsc(e.name)}</b> %{x}: %{y:.1f} workers/retiree<extra></extra>` });
    add.push({ x: yrs.slice(cut), y: e.sr.slice(cut), showlegend: false, legendgroup: '__focus', meta: '__focus', type: 'scatter', mode: 'lines',
      line: { color, width: 4, dash: 'dot' }, hovertemplate: `<b>${fcEsc(e.name)}</b> %{x} (proj.): %{y:.1f}<extra></extra>` });
  }
  if (add.length) Plotly.addTraces(el, add);
}
function fcEmphasizeScatter() {
  const el = document.getElementById('fig-ca');
  if (!el || !el.data) return;
  const drop = [];
  el.data.forEach((t, i) => { if (t.meta === '__focus') drop.push(i); });
  if (drop.length) Plotly.deleteTraces(el, drop);
  const c = FC.focus && state.countries[FC.focus];
  if (!c || c.ca === null || c.ca === undefined || !c.ma) return;
  // Figure 5 already labels a handful of countries; don't print the name twice
  const labeled = (el.layout.annotations || []).some(an => an.text === c.n);
  Plotly.addTraces(el, [{ x: [c.ma], y: [c.ca], meta: '__focus', type: 'scatter', mode: labeled ? 'markers' : 'markers+text',
    text: [fcName(FC.focus)], textposition: 'top center', textfont: { size: 12.5, color: INK },
    marker: { size: 17, color: CC[FC.focus] || INK, line: { color: PAPER, width: 2 } }, showlegend: false,
    hovertemplate: `<b>${fcEsc(fcName(FC.focus))}</b><br>median age %{x:.1f} · current account %{y:.1f}% GDP<extra></extra>` }]);
}

function fcFocusUI() {
  const code = FC.focus;
  document.querySelectorAll('.follow .chip').forEach(b => {
    const on = b.dataset.code === code;
    b.classList.toggle('on', on);
    b.setAttribute('aria-pressed', on);
  });
  document.querySelectorAll('.follow input').forEach(inp => {
    inp.value = code && !fcFeatured().includes(code) ? fcName(code) : '';
  });
  const pill = document.getElementById('focus-pill');
  if (pill) {
    pill.hidden = !code;
    if (code) pill.innerHTML = `<span>Following <b>${fcEsc(fcName(code))}</b></span>
      <a href="#country/${code}">open in atlas</a>
      <button type="button" aria-label="Stop following ${fcEsc(fcName(code))}">✕</button>`;
    const x = pill.querySelector('button');
    if (x) x.addEventListener('click', () => fcSetFocus(null));
  }
}

let fcFocusSeq = 0;
async function fcSetFocus(code) {
  if (code && !state.countries[code]) return;
  FC.focus = code || null;
  const seq = ++fcFocusSeq;
  fcFocusUI();
  try {
    await fcEnsureBase();
    if (FC.focus) await fcEnsureEntity(FC.focus);
  } catch (err) { console.warn('[forecast] could not load data for the followed country:', err); return; }
  if (seq !== fcFocusSeq) return;                 // a newer choice superseded this one
  fcEmphasizeLines('fig-tfr', 'tfr');
  fcEmphasizeLines('fig-sr', 'sr');
  fcEmphasizeScatter();
  if (FC.drawn) { fcDrawGrowth(); fcDrawHurdle(); fcLedger(); fcCohortTable(); }
  fcTakeaways();
}

function fcBuildFollow() {
  const byName = {};
  Object.entries(state.countries).forEach(([code, c]) => { byName[c.n.toLowerCase()] = code; });
  Object.entries(FC_SHORT).forEach(([code, n]) => { byName[n.toLowerCase()] = code; });
  const options = Object.values(state.countries).map(c => c.n).sort((a, b) => a.localeCompare(b))
    .map(n => `<option value="${fcEsc(n)}"></option>`).join('');
  document.querySelectorAll('.follow').forEach((host, idx) => {
    const chips = fcFeatured().filter(c => state.countries[c]).map(c =>
      `<button type="button" class="chip" data-code="${c}" aria-pressed="false"><i style="background:${CC[c] || MUTED}"></i>${fcEsc(fcName(c))}</button>`).join('');
    host.innerHTML = `<div class="chips" role="group" aria-label="Follow a country through the figures">${chips}</div>
      <label class="any">or any other: <input type="text" list="follow-list-${idx}" placeholder="type a country" autocomplete="off" aria-label="Follow any country" />
      <datalist id="follow-list-${idx}">${options}</datalist></label>`;
    host.querySelectorAll('.chip').forEach(b => b.addEventListener('click', () =>
      fcSetFocus(b.dataset.code === FC.focus ? null : b.dataset.code)));
    host.querySelector('input').addEventListener('change', ev => {
      const hit = byName[ev.target.value.trim().toLowerCase()];
      if (hit) fcSetFocus(hit);
    });
  });
}

/* -------------------------------------------------------------------- boot */
function fcDrawAll() {
  FC.drawn = true;
  fcDrawHorizon(); fcDrawGrowth(); fcDrawHurdle(); fcLedger(); fcCohortTable(); fcAuditProse(); fcTakeaways();
}
// The three figures and the cohort table choose their layout by container
// width; redraw when the container crosses the breakpoint (rotation, a resized
// window).
function fcWatchWidth() {
  const el = document.getElementById('fig-growth');
  if (!el || !('ResizeObserver' in window)) return;
  let last = fcNarrow(el);
  new ResizeObserver(() => {
    const now = fcNarrow(el);
    if (now === last) return;
    last = now;
    if (FC.drawn) { fcDrawHorizon(); fcDrawGrowth(); fcDrawHurdle(); fcCohortTable(); }
  }).observe(el);
}
function fcFail(err) {
  ['fig-horizon', 'fig-growth', 'fig-hurdle'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = '<div class="ph">Could not load the forecast data (' + fcEsc(err) + ').</div>';
  });
}

// Figure 4 gets the same 2045 line as Figures 6 and 7: left of it every worker
// in the ratio is already born.
function fcMarkWorkerHorizon() {
  const el = document.getElementById('fig-sr');
  if (!el || !el.layout) return;
  Plotly.relayout(el, {
    shapes: (el.layout.shapes || []).concat([{ type: 'line', xref: 'x', yref: 'paper', x0: 2045, x1: 2045, y0: 0, y1: 1,
      line: { color: MUTED, width: 1 } }]),
    annotations: (el.layout.annotations || []).concat([{ x: 2045, yref: 'paper', y: 0.985, yanchor: 'top', xanchor: 'left',
      xshift: 5, align: 'left', text: 'after 2045 the workers<br>are not yet born', showarrow: false,
      font: { size: 11.5, color: MUTED } }]),
  });
}

document.addEventListener('demographics:ready', () => {
  FC.nameToCode = {};
  Object.entries(state.countries).forEach(([code, c]) => { FC.nameToCode[c.n] = code; });
  fcBuildFollow();
  fcMarkWorkerHorizon();
  fcWatchWidth();
  fcAuditProse();                                  // Figure 5 numbers need no extra fetch
  // clicking a line or a point follows that country
  ['fig-tfr', 'fig-sr'].forEach(id => {
    const el = document.getElementById(id);
    if (el && el.on) el.on('plotly_click', ev => {
      const c = ev.points && ev.points[0] && fcTraceCode(ev.points[0].data);
      if (c && c !== '__focus') fcSetFocus(c === FC.focus ? null : c);
    });
  });
  const ca = document.getElementById('fig-ca');
  if (ca && ca.on) ca.on('plotly_click', ev => {
    const c = ev.points && ev.points[0] && FC.nameToCode[ev.points[0].text];
    if (c && ev.points[0].data.meta !== '__focus') fcSetFocus(c === FC.focus ? null : c);
  });
  const lever = document.getElementById('lever');
  if (lever) lever.addEventListener('input', () => {
    FC.k = +lever.value;
    const v = document.getElementById('lever-val');
    if (v) v.textContent = '+' + FC.k.toFixed(1) + ' years';
    if (FC.drawn) fcDrawHurdle();
  });
  // the section's data is fetched when the reader gets near it
  const sec = document.getElementById('forecast');
  const go = () => fcEnsureBase().then(() => { if (!FC.drawn) fcDrawAll(); }).catch(fcFail);
  if (sec && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver(es => { if (es.some(e => e.isIntersecting)) { io.disconnect(); go(); } }, { rootMargin: '1400px 0px' });
    io.observe(sec);
  } else if (sec) go();
});

// choosing a country in the atlas follows it everywhere else
document.addEventListener('demographics:select', ev => {
  if (ev.detail && ev.detail.iso3 && ev.detail.iso3 !== FC.focus) fcSetFocus(ev.detail.iso3);
});
