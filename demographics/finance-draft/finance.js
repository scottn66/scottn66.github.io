/* Finance section draft: charts and table. Data is window.FINANCE_DATA. */
'use strict';

const INK = '#1E1E1E', MUTED = '#555', RULE = '#E5E5EA', PAPER = '#FFFFFF';
const ACCENT = '#1F4E9E', WARN = '#B83A2E', GOOD = '#2F7A4A', ORANGE = '#D97036', GOLD = '#C9A227';
const GOOD_SOFT = 'rgba(47,122,74,0.55)', WARN_SOFT = 'rgba(184,58,46,0.55)';
const FONT = {
  family: '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Helvetica,Arial,sans-serif',
  color: INK, size: 12.5,
};
const BASE = {
  paper_bgcolor: PAPER, plot_bgcolor: PAPER, font: FONT,
  margin: { l: 46, r: 18, t: 28, b: 38 },
  hoverlabel: { bgcolor: '#1b2330', font: { color: '#fff', size: 12 }, bordercolor: '#1b2330' },
};
const NOPAD = { displayModeBar: false, responsive: true, staticPlot: false };

const CC = {
  USA: '#1F4E9E', CHN: '#B83A2E', DEU: '#A8861D', NGA: '#2F7A4A',
  JPN: '#6A4FA3', KOR: '#0782AF', IND: '#C2632F',
  ITA: '#8B3A62', BRA: '#3D7A5A', MEX: '#C47A3A',
  FRA: '#3A5F8A', GBR: '#555555', ETH: '#4A8A5A',
  SAU: '#1A7A6A', IRN: '#9A4A2A', THA: '#2A6A8A',
  ESP: '#A05A3A', POL: '#6A3A5A', NER: '#2F7A4A',
};

function plotWidth(el) {
  const cs = getComputedStyle(el);
  return el.clientWidth - (parseFloat(cs.paddingLeft) || 0) - (parseFloat(cs.paddingRight) || 0);
}
const RESIZER = new ResizeObserver(entries => {
  for (const e of entries) {
    const el = e.target;
    if (!el.classList.contains('js-plotly-plot') || !el.offsetWidth || !el._fullLayout) continue;
    const ratio = parseFloat(el.dataset.hratio);
    const w = plotWidth(el);
    try {
      if (el.dataset.fixedHeight) {
        const h = +el.dataset.fixedHeight;
        const cur = el._fullLayout || {};
        if (Math.abs((cur.width || 0) - w) > 2 || Math.abs((cur.height || 0) - h) > 2)
          Plotly.relayout(el, { width: w, height: h });
      } else if (ratio) {
        const target = Math.round(Math.min(Math.max(w * ratio, +el.dataset.hmin || 0), +el.dataset.hmax || 1e4));
        const cur = el._fullLayout || {};
        if (Math.abs((cur.width || 0) - w) > 2 || Math.abs((cur.height || 0) - target) > 2)
          Plotly.relayout(el, { width: w, height: target });
      } else {
        Plotly.Plots.resize(el);
      }
    } catch (err) {
      /* plot was purged mid-resize; the next draw will set size */
    }
  }
});
function sized(el, ratio, hmin, hmax) {
  el.dataset.hratio = ratio; el.dataset.hmin = hmin; el.dataset.hmax = hmax;
  return Math.round(Math.min(Math.max(plotWidth(el) * ratio, hmin), hmax));
}
const grid = (ax) => Object.assign({ gridcolor: RULE, zerolinecolor: RULE, linecolor: RULE, tickcolor: RULE }, ax);
function mount(id) {
  const el = typeof id === 'string' ? document.getElementById(id) : id;
  try { RESIZER.unobserve(el); } catch (e) {}
  if (el.classList && el.classList.contains('js-plotly-plot')) {
    try { Plotly.purge(el); } catch (e) {}
  }
  el.innerHTML = '';
  delete el.dataset.fixedHeight;
  RESIZER.observe(el);
  return el;
}

const state = {
  mode: 'dumbbell',
  year: 2025,
  sort: 'S25',
  metric: 'S',
};

function D() {
  if (!window.FINANCE_DATA) throw new Error('FINANCE_DATA not loaded');
  return window.FINANCE_DATA;
}

function drawWeight() {
  const d = D();
  const traces = [];
  const exampleOrder = ['USA', 'JPN', 'DEU', 'CHN', 'IND', 'NGA'];
  const exampleColors = {
    USA: CC.USA, JPN: CC.JPN, DEU: CC.DEU, CHN: CC.CHN, IND: CC.IND, NGA: CC.NGA,
  };
  exampleOrder.forEach(iso => {
    const ex = d.examples[iso];
    if (!ex) return;
    traces.push({
      x: d.ages, y: ex.yl, type: 'scatter', mode: 'lines',
      name: ex.name + ' (' + ex.year + ')',
      line: { color: exampleColors[iso], width: 1.15 },
      opacity: 0.55,
      hovertemplate: '<b>' + ex.name + '</b> (' + ex.year + ')<br>age %{x}: %{y:.2f}<extra></extra>',
    });
  });
  traces.push({
    x: d.ages, y: d.c_avg, type: 'scatter', mode: 'lines',
    name: 'Consumption, NTA average',
    line: { color: ORANGE, width: 1.8, dash: 'dash' },
    hovertemplate: 'consumption, age %{x}: %{y:.2f}<extra></extra>',
  });
  traces.push({
    x: d.ages, y: d.yl_sty, type: 'scatter', mode: 'lines',
    name: 'Stylized curve (live Fig 3)',
    line: { color: GOLD, width: 1.7, dash: 'dot' },
    hovertemplate: 'stylized, age %{x}: %{y:.2f}<extra></extra>',
  });
  traces.push({
    x: d.ages, y: d.yl_avg, type: 'scatter', mode: 'lines',
    name: 'Labor income, NTA average (the weight)',
    line: { color: ACCENT, width: 2.8 },
    hovertemplate: 'NTA average, age %{x}: %{y:.2f}<extra></extra>',
  });
  const layout = Object.assign({}, BASE, {
    height: 460,
    legend: { orientation: 'h', x: 0, y: 1.16, font: { size: 11 } },
    margin: { l: 52, r: 16, t: 64, b: 42 },
    xaxis: grid({ title: { text: 'age', font: { size: 13, color: MUTED } },
      dtick: 10, range: [0, 90], fixedrange: true }),
    yaxis: grid({ title: { text: 'relative to the 30-49 mean', font: { size: 13, color: MUTED } },
      rangemode: 'tozero', fixedrange: true, dtick: 0.2 }),
    shapes: [{
      type: 'line', x0: d.meta.peak_age, x1: d.meta.peak_age, y0: 0, y1: 1.15,
      line: { color: RULE, width: 1, dash: 'dot' },
    }],
    annotations: [{
      x: d.meta.peak_age, y: 1.16, text: 'peak at ' + d.meta.peak_age,
      showarrow: false, font: { size: 11, color: MUTED }, xanchor: 'left', xshift: 6,
    }],
  });
  // The y-axis title used an en-dash in "30-49"; keep a hyphen.
  layout.yaxis.title.text = 'relative to the 30-49 mean';
  const el = mount('fig-weight');
  layout.height = sized(el, 0.62, 420, 640);
  Plotly.newPlot(el, traces, layout, NOPAD);
}

function metricKeys(metric) {
  if (metric === 'esr') {
    return { v25: 'esr25', v50: 'esr50', r25: 'rE25', r50: 'rE50', label: 'economic support ratio SR' };
  }
  return { v25: 'S25', v50: 'S50', r25: 'rS25', r50: 'rS50', label: 'productivity-weighted age structure S' };
}

function sortedDisplay() {
  const rows = D().display.slice();
  const m = metricKeys(state.metric);
  const key = state.sort === 'S25' ? m.v25 : state.sort === 'S50' ? m.v50 : 'dS';
  // For ESR, "change" is still dS of S; compute dESR on the fly.
  rows.sort((a, b) => {
    let va, vb;
    if (state.sort === 'dS' && state.metric === 'esr') {
      va = a.esr50 - a.esr25;
      vb = b.esr50 - b.esr25;
    } else {
      va = a[key];
      vb = b[key];
    }
    return vb - va;
  });
  return rows;
}

function drawRank() {
  const d = D();
  const m = metricKeys(state.metric);
  const rows = sortedDisplay();
  const names = rows.map(r => r.short);
  const y = names.slice().reverse(); // top of chart = highest under current sort
  const rowsRev = rows.slice().reverse();
  const v25 = rowsRev.map(r => r[m.v25]);
  const v50 = rowsRev.map(r => r[m.v50]);
  const world = state.metric === 'S' ? d.meta.world_S_2025 : null;

  const traces = [];
  if (state.mode === 'dumbbell') {
    rowsRev.forEach((r, i) => {
      const a = r[m.v25], b = r[m.v50];
      const up = b >= a;
      traces.push({
        x: [a, b], y: [y[i], y[i]], type: 'scatter', mode: 'lines',
        line: { color: up ? GOOD_SOFT : WARN_SOFT, width: 3 },
        showlegend: false, hoverinfo: 'skip',
      });
    });
    traces.push({
      x: v25, y: y, type: 'scatter', mode: 'markers', name: '2025',
      marker: { color: ACCENT, size: 9, symbol: 'circle' },
      customdata: rowsRev.map(r => {
        const dlt = state.metric === 'esr' ? (r.esr50 - r.esr25) : r.dS;
        return [r.short, r[m.v25], r[m.v50], dlt, r[m.r25], r[m.r50], r.ma, r.ma50];
      }),
      hovertemplate: '<b>%{customdata[0]}</b><br>2025: %{customdata[1]:.3f} (rank %{customdata[4]})<br>2050: %{customdata[2]:.3f} (rank %{customdata[5]})<br>change: %{customdata[3]:+.3f}<br>median age %{customdata[6]} to %{customdata[7]}<extra>2025</extra>',
    });
    traces.push({
      x: v50, y: y, type: 'scatter', mode: 'markers', name: '2050',
      marker: { color: ORANGE, size: 9, symbol: 'circle-open', line: { width: 2, color: ORANGE } },
      customdata: rowsRev.map(r => {
        const dlt = state.metric === 'esr' ? (r.esr50 - r.esr25) : r.dS;
        return [r.short, r[m.v25], r[m.v50], dlt, r[m.r25], r[m.r50]];
      }),
      hovertemplate: '<b>%{customdata[0]}</b><br>2025: %{customdata[1]:.3f}<br>2050: %{customdata[2]:.3f} (rank %{customdata[5]})<br>change: %{customdata[3]:+.3f}<extra>2050</extra>',
    });
  } else {
    const year = state.year;
    const vals = rowsRev.map(r => year === 2025 ? r[m.v25] : r[m.v50]);
    const colors = rowsRev.map(r => {
      const dlt = state.metric === 'esr' ? (r.esr50 - r.esr25) : r.dS;
      if (year === 2050) return dlt >= 0 ? GOOD : WARN;
      return ACCENT;
    });
    traces.push({
      x: vals, y: y, type: 'bar', orientation: 'h',
      marker: { color: colors },
      name: String(year),
      customdata: rowsRev.map(r => {
        const dlt = state.metric === 'esr' ? (r.esr50 - r.esr25) : r.dS;
        return [r.short, r[m.v25], r[m.v50], dlt, r[m.r25], r[m.r50], year === 2025 ? r[m.v25] : r[m.v50]];
      }),
      hovertemplate: '<b>%{customdata[0]}</b><br>this bar: %{customdata[6]:.3f}<br>2025: %{customdata[1]:.3f} (rank %{customdata[4]})<br>2050: %{customdata[2]:.3f} (rank %{customdata[5]})<br>change: %{customdata[3]:+.3f}<extra></extra>',
      showlegend: false,
    });
  }

  const shapes = [];
  const annotations = [];
  if (world != null && state.metric === 'S') {
    shapes.push({
      type: 'line', x0: world, x1: world, y0: -0.6, y1: y.length - 0.4, yref: 'y',
      line: { color: MUTED, width: 1, dash: 'dot' },
    });
    annotations.push({
      x: world, y: 1.015, yref: 'paper', text: 'world avg 0.50',
      showarrow: false, font: { size: 11, color: MUTED }, xanchor: 'center', yanchor: 'bottom',
    });
  }

  const el = mount('fig-rank');
  const h = Math.max(760, rows.length * 23 + 110);
  el.style.height = h + 'px';
  el.style.minHeight = h + 'px';
  el.dataset.fixedHeight = String(h);
  const xmin = state.metric === 'S' ? 0.28 : 0.34;
  const xmax = state.metric === 'S' ? 0.64 : 0.68;
  const layout = Object.assign({}, BASE, {
    height: h,
    width: plotWidth(el),
    autosize: false,
    margin: { l: 128, r: 28, t: 42, b: 46 },
    legend: { orientation: 'h', x: 0, xanchor: 'left', y: 1.03, font: { size: 12 } },
    barmode: 'overlay',
    bargap: 0.28,
    xaxis: grid({
      title: { text: m.label + '  (axis starts at ' + xmin + ', not zero)', font: { size: 12, color: MUTED } },
      range: [xmin, xmax], fixedrange: true, dtick: 0.05,
    }),
    yaxis: grid({
      automargin: true, fixedrange: true, tickfont: { size: 12 },
      type: 'category',
    }),
    shapes, annotations,
  });
  Plotly.newPlot(el, traces, layout, Object.assign({}, NOPAD, { responsive: false }));
  fillTable(rows, m);
}

function fillTable(rows, m) {
  const tb = document.querySelector('#score-table tbody');
  if (!tb) return;
  tb.innerHTML = rows.map(r => {
    const dlt = r.dS;
    const cls = dlt >= 0 ? 'pos' : 'neg';
    const sign = dlt >= 0 ? '+' : '';
    return '<tr>'
      + '<td>' + r.short + '</td>'
      + '<td class="num">' + r.S25.toFixed(3) + '</td>'
      + '<td class="num">' + r.rS25 + '</td>'
      + '<td class="num">' + r.S50.toFixed(3) + '</td>'
      + '<td class="num">' + r.rS50 + '</td>'
      + '<td class="num ' + cls + '">' + sign + dlt.toFixed(3) + '</td>'
      + '<td class="num">' + r.esr25.toFixed(3) + '</td>'
      + '<td class="num">' + r.ma.toFixed(1) + '</td>'
      + '<td class="num">' + r.ma50.toFixed(1) + '</td>'
      + '</tr>';
  }).join('');
}

function drawScatter() {
  const d = D();
  const rest = d.all.filter(r => !r.display);
  const disp = d.all.filter(r => r.display);
  const sizeOf = pop => {
    // pop is in thousands. 10m -> ~8, 1.4bn -> ~28
    const m = Math.max(0.2, (pop || 200) / 1000);
    return Math.max(5, Math.min(32, 4 + 5 * Math.sqrt(m)));
  };
  const traces = [];
  traces.push({
    x: rest.map(r => r.ma), y: rest.map(r => r.S25),
    type: 'scatter', mode: 'markers', name: 'other countries',
    marker: {
      color: '#c5c9d1', size: rest.map(r => sizeOf(r.pop)),
      opacity: 0.7, line: { width: 0 },
    },
    customdata: rest.map(r => [r.short, r.S25, r.S50, r.dS, r.rS25, r.rS50, r.pop, r.ma50]),
    hovertemplate: '<b>%{customdata[0]}</b><br>median age %{x:.1f}<br>S 2025: %{customdata[1]:.3f} (rank %{customdata[4]})<br>S 2050: %{customdata[2]:.3f} (rank %{customdata[5]})<br>change %{customdata[3]:+.3f}<br>pop %{customdata[6]:,.0f} thousand<extra></extra>',
  });
  traces.push({
    x: disp.map(r => r.ma), y: disp.map(r => r.S25),
    type: 'scatter', mode: 'markers', name: 'test set',
    marker: {
      color: disp.map(r => CC[r.iso3] || ACCENT),
      size: disp.map(r => sizeOf(r.pop)),
      opacity: 0.92,
      line: { width: 0.8, color: '#fff' },
    },
    customdata: disp.map(r => [r.short, r.S25, r.S50, r.dS, r.rS25, r.rS50, r.pop, r.ma50]),
    hovertemplate: '<b>%{customdata[0]}</b><br>median age %{x:.1f}<br>S 2025: %{customdata[1]:.3f} (rank %{customdata[4]})<br>S 2050: %{customdata[2]:.3f} (rank %{customdata[5]})<br>change %{customdata[3]:+.3f}<br>pop %{customdata[6]:,.0f} thousand<extra></extra>',
  });
  const labels = ['QAT', 'ARE', 'SAU', 'KOR', 'CHN', 'USA', 'IND', 'JPN', 'NGA', 'NER', 'PHL', 'ITA'];
  const labRows = d.all.filter(r => labels.includes(r.iso3));
  traces.push({
    x: labRows.map(r => r.ma), y: labRows.map(r => r.S25),
    type: 'scatter', mode: 'text', name: '',
    text: labRows.map(r => r.short),
    textposition: labRows.map(r => ({
      QAT: 'top center', ARE: 'middle left', SAU: 'top center',
      KOR: 'top right', CHN: 'bottom right', USA: 'bottom left',
      IND: 'top left', JPN: 'middle right', NGA: 'bottom right',
      NER: 'bottom left', PHL: 'bottom left', ITA: 'bottom right',
    }[r.iso3] || 'top right')),
    textfont: { size: 10.5, color: INK },
    hoverinfo: 'skip', showlegend: false,
  });
  const el = mount('fig-scatter');
  const layout = Object.assign({}, BASE, {
    height: sized(el, 0.68, 460, 680),
    margin: { l: 54, r: 18, t: 20, b: 48 },
    legend: { orientation: 'h', x: 1, xanchor: 'right', y: 1.04 },
    xaxis: grid({
      title: { text: 'median age, 2025', font: { size: 13, color: MUTED } },
      fixedrange: true, dtick: 5, range: [14, 58],
    }),
    yaxis: grid({
      title: { text: 'S, 2025', font: { size: 13, color: MUTED } },
      fixedrange: true, range: [0.26, 0.76],
    }),
  });
  Plotly.newPlot(el, traces, layout, NOPAD);
}

function drawMultiples() {
  const d = D();
  const host = document.getElementById('fig-multiples');
  host.innerHTML = '';
  const isos = d.meta.small_multiples;
  const mid = d.midpoints;
  const w = d.weights_5yr;
  isos.forEach((iso, idx) => {
    const r = d.display.find(x => x.iso3 === iso);
    if (!r) return;
    const wrap = document.createElement('figure');
    wrap.style.margin = '0';
    const div = document.createElement('div');
    div.className = 'chart';
    div.id = 'fig-m-' + iso;
    div.innerHTML = '<div class="ph">loading…</div>';
    wrap.appendChild(div);
    host.appendChild(wrap);

    const shares25 = r.shares25.map(s => s * 100);
    const shares50 = r.shares50.map(s => s * 100);
    const traces = [
      {
        x: mid, y: shares25, type: 'scatter', mode: 'lines',
        name: '2025 share', fill: 'tozeroy',
        line: { color: ACCENT, width: 1.2 },
        fillcolor: 'rgba(31,78,158,0.22)',
        hovertemplate: '2025 · age %{x}: %{y:.1f}%<extra></extra>',
        showlegend: false,
      },
      {
        x: mid, y: shares50, type: 'scatter', mode: 'lines',
        name: '2050 share',
        line: { color: ORANGE, width: 1.7 },
        hovertemplate: '2050 · age %{x}: %{y:.1f}%<extra></extra>',
        showlegend: false,
      },
      {
        x: mid, y: w, type: 'scatter', mode: 'lines',
        name: 'weight w(a)', yaxis: 'y2',
        line: { color: GOLD, width: 2, dash: 'dot' },
        hovertemplate: 'weight %{y:.2f}<extra></extra>',
        showlegend: false,
      },
    ];
    const el = mount(div);
    const layout = Object.assign({}, BASE, {
      height: 260,
      margin: { l: 36, r: 36, t: 32, b: 32 },
      showlegend: false,
      title: {
        text: '<b>' + r.short + '</b>  ·  S ' + r.S25.toFixed(3) + ' to ' + r.S50.toFixed(3),
        font: { size: 13, color: INK },
        x: 0, xanchor: 'left',
      },
      xaxis: grid({ range: [0, 102], dtick: 20, fixedrange: true, tickfont: { size: 10, color: MUTED } }),
      yaxis: grid({
        range: [0, 10.5], dtick: 2, fixedrange: true,
        title: { text: idx % 3 === 0 ? '% of pop.' : '', font: { size: 10, color: MUTED } },
        tickfont: { size: 10, color: MUTED },
      }),
      yaxis2: {
        overlaying: 'y', side: 'right', range: [0, 1.15], dtick: 0.5,
        showgrid: false, fixedrange: true,
        title: { text: idx % 3 === 2 || true ? '' : '', font: { size: 10, color: GOLD } },
        tickfont: { size: 10, color: GOLD },
      },
    });
    Plotly.newPlot(el, traces, layout, NOPAD);
  });
}

function bindToggles() {
  function onGroup(id, attr, key, after) {
    const root = document.getElementById(id);
    root.addEventListener('click', ev => {
      const btn = ev.target.closest('button');
      if (!btn) return;
      root.querySelectorAll('button').forEach(b => b.classList.toggle('on', b === btn));
      const val = btn.getAttribute(attr);
      state[key] = (key === 'year') ? +val : val;
      after();
    });
  }
  onGroup('view-mode', 'data-mode', 'mode', () => {
    document.getElementById('year-wrap').hidden = state.mode !== 'bars';
    drawRank();
  });
  onGroup('year-mode', 'data-year', 'year', () => drawRank());
  onGroup('sort-mode', 'data-sort', 'sort', () => drawRank());
  onGroup('metric-mode', 'data-metric', 'metric', () => drawRank());
}

function fillStats() {
  const d = D();
  const set = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
  set('stat-world', d.meta.world_S_2025.toFixed(2));
  set('stat-world50', d.meta.world_S_2050.toFixed(2));
  set('stat-peak', String(d.meta.peak_age));
  const kor = d.display.find(r => r.iso3 === 'KOR');
  if (kor) set('stat-kor', kor.dS.toFixed(3).replace('0.', '.').replace(/^-0/, '-0').replace(/^-/, '-'));
  // Use a minus sign that's a hyphen to avoid unicode em issues: use ASCII hyphen.
  if (kor) set('stat-kor', kor.dS.toFixed(2));
}

function main() {
  fillStats();
  drawWeight();
  bindToggles();
  drawRank();
  drawScatter();
  drawMultiples();
  if (window.renderMathInElement) {
    renderMathInElement(document.body, {
      delimiters: [
        { left: '\\[', right: '\\]', display: true },
        { left: '\\(', right: '\\)', display: false },
      ],
      throwOnError: false,
    });
  }
  const tog = document.getElementById('toc-toggle');
  if (tog) tog.addEventListener('click', () => document.querySelector('.toc').classList.toggle('open'));
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', main);
else main();
