/* The Shape of People to Come — section 10 (the cohort view).

   Loaded after forecast.js and shares its top-level tokens and helpers (FC,
   fcSum, fcSigned, fcEsc, fcNarrow, fcFixedHeight, fcEnsureBase … and, through
   them, app.js's CC, BASE, grid, mount, sized). Section 9 reads the pyramids one
   calendar year at a time; this file reads the same pyramids along a diagonal.

   A cohort `b` is the people aged 0–4 in year b. It sits in five-year bin i in
   year b + 5i. That is the resident cohort, so it moves with migration as well
   as survival. Each of the five quantities below has one implementation, which
   the life strip, the cards, the table and the prose audit all call. */
'use strict';

const CO = {
  b: 2000,                  // the reader's cohort
  mode: 'benefit',          // pension card: 'benefit' = benefits held, 'contrib' = contributions held
  drawn: false, seq: 0,
  mounted: {},
  memo: new Map(),          // 'ISO3:b' -> the five quantities
};
const CO_RHO = 0.40;        // illustrative replacement rate; ratios between cohorts do not depend on it
const CO_GAP = 25;          // the parents' cohort is b − 25
const CO_LO = 1950, CO_HI = 2010;                 // cohorts the reader can choose
const CO_FIRST = CO_LO - CO_GAP;                  // first cohort drawn: the 1950 cohort's parents
const CO_HOME = 'USA';      // shown when no country is followed
// Neutral grays: the parents' cohort · every other cohort. No gray is far from
// all seven country hues at once, so the parents' cohort never relies on color
// alone: its bar is hatched and its line is thinner.
const CO_PARENT = '#8A8F98', CO_REST = '#D8DAE0';

const coCode = () => FC.focus || CO_HOME;
const coRange = b => (b - 4) + '–' + b;           // the birth years in cohort b

/* --------------------------------------------------------- the quantities */
// Position of calendar year y on the five-year grid, or -1 when it is off it.
function coIx(years, y) {
  const j = (y - years[0]) / 5;
  return Number.isInteger(j) && j >= 0 && j < years.length ? j : -1;
}

// 1 · Career growth term, pp/yr: 100 · ln(ESR[b+65] / ESR[b+25]) / 40.
function coCareer(esr, years, b) {
  const a = coIx(years, b + 25), z = coIx(years, b + 65);
  return a < 0 || z < 0 ? null : 100 * Math.log(esr[z] / esr[a]) / 40;
}

// 2 · Workers (20–64) per retiree (65+) in the year the cohort reaches `age`.
function coSrAt(sr, years, b, age) {
  const j = coIx(years, b + age);
  return j < 0 ? null : sr[j];
}

// 3 · Fixed-benefit pay-as-you-go: the contribution rate rho / SR[t], averaged
// over the nine grid years b+20 … b+60 in which the cohort is of working age.
function coContribution(sr, years, b, rho) {
  let s = 0;
  for (let t = b + 20; t <= b + 60; t += 5) {
    const j = coIx(years, t);
    if (j < 0) return null;
    s += rho / sr[j];
  }
  return s / 9;
}

// 4 · Fixed-contribution pay-as-you-go: the annual rate r that solves
//   sum over i = 4..20 of CF_i · (1 + r)^(−5(i − 4)) = 0,
// with CF_i = −P[b+5i][i] while the cohort works (i ≤ 12) and
// CF_i = +P[b+5i][i] · SR[b+5i] once it has retired (i ≥ 13). The cash flows are
// in wage units, so r is the return net of wage growth. It needs data to year
// b + 100, which the grid has only for b ≤ 2000. One sign change, so one root.
function coReturn(P, sr, years, b) {
  const cf = [];
  for (let i = 4; i <= 20; i++) {
    const j = coIx(years, b + 5 * i);
    if (j < 0) return null;
    cf.push(i <= 12 ? -P[j][i] : P[j][i] * sr[j]);
  }
  const npv = r => { let s = 0; for (let k = 0; k < cf.length; k++) s += cf[k] * Math.pow(1 + r, -5 * k); return s; };
  let lo = -0.5, hi = 0.5;
  if (!(npv(lo) > 0 && npv(hi) < 0)) return null;
  for (let it = 0; it < 60; it++) {
    const mid = (lo + hi) / 2;
    if (npv(mid) > 0) lo = mid; else hi = mid;
  }
  return (lo + hi) / 2;
}

// 5 · Entry market: entrants (20–24) per imminent retiree (60–64) in the year
// the cohort is 20–24.
function coEntry(P, years, b) {
  const j = coIx(years, b + 20);
  return j < 0 || !(P[j][12] > 0) ? null : P[j][4] / P[j][12];
}

function coCohort(e, b) {
  const key = e.code + ':' + b;
  if (CO.memo.has(key)) return CO.memo.get(key);
  const yrs = FC.years, g = coCareer(e.esr, yrs, b);
  const q = {
    b, g,
    cum: g === null ? null : 100 * (Math.exp(g * 40 / 100) - 1),   // the same term compounded over the forty years
    sr45: coSrAt(e.sr, yrs, b, 45), sr70: coSrAt(e.sr, yrs, b, 70),
    c: coContribution(e.sr, yrs, b, CO_RHO),
    r: coReturn(e.P, e.sr, yrs, b),
    em: coEntry(e.P, yrs, b),
  };
  Object.keys(q).forEach(k => { if (q[k] !== null && !Number.isFinite(q[k])) q[k] = null; });
  CO.memo.set(key, q);
  return q;
}

// Known-answer check. In a stable population P[y][i] = exp(n(y − 5i)) · l_i the
// pay-as-you-go return is the population growth rate, e^n − 1 a year, whatever
// the survival curve l_i. Runs once on load, on the grid the data uses.
(function coKnownAnswer() {
  const years = [];
  for (let y = 1950; y <= 2100; y += 5) years.push(y);
  const l = [];
  for (let i = 0; i < 21; i++) l.push(Math.exp(-Math.pow(i / 16, 4)));
  [0.01, 0, -0.01].forEach(n => {
    const P = years.map(y => l.map((li, i) => Math.exp(n * (y - 5 * i)) * li));
    const sr = P.map(row => fcSum(row, 4, 12) / fcSum(row, 13, 20));
    const want = 100 * (Math.exp(n) - 1);
    [1950, 1975, 2000].forEach(b => {
      const got = coReturn(P, sr, years, b);
      if (got === null || Math.abs(100 * got - want) > 0.05)
        console.warn('[cohort] known-answer check failed: stable population with n =', n, '· cohort', b,
          '· returned', got === null ? null : (100 * got).toFixed(3), '· expected', want.toFixed(3));
    });
  });
})();

/* ------------------------------------------------------------ prose audit */
// data-fc="co:<quantity>:<ISO3>:<cohort>" — the numbers this section's prose
// quotes. `cx` is the fixed-benefit contribution relative to the parents' cohort.
function coProse(key) {
  const m = /^co:(g|sr45|sr70|c|cx|r|em):([A-Z]{3}):(\d{4})$/.exec(key);
  const e = m && FC.ents.get(m[2]);
  if (!e) return undefined;
  const q = coCohort(e, +m[3]), p = coCohort(e, +m[3] - CO_GAP);
  switch (m[1]) {
    case 'g': return q.g === null ? undefined : fcSigned(q.g, 2);
    case 'sr45': return q.sr45 === null ? undefined : q.sr45.toFixed(1);
    case 'sr70': return q.sr70 === null ? undefined : q.sr70.toFixed(1);
    case 'c': return q.c === null ? undefined : (100 * q.c).toFixed(1) + '%';
    case 'cx': return q.c === null || p.c === null ? undefined : (q.c / p.c).toFixed(2);
    case 'r': return q.r === null ? undefined : fcSigned(100 * q.r, 2);
    default: return q.em === null ? undefined : q.em.toFixed(2);
  }
}
FC.resolvers.push(coProse);

/* ------------------------------------------------ Fig 9 · the life strip */
// Workers per retiree along one cohort's life: age 0–100 across, the calendar
// year under each age.
function coPath(e, b) {
  const o = { age: [], sr: [], yr: [] };
  for (let a = 0; a <= 100; a += 5) {
    const j = coIx(FC.years, b + a);
    if (j >= 0) { o.age.push(a); o.sr.push(e.sr[j]); o.yr.push(b + a); }
  }
  return o;
}

function coDrawStrip(e) {
  const el = CO.mounted.strip || (CO.mounted.strip = mount('fig-life'));
  const narrow = fcNarrow(el), b = CO.b, p = b - CO_GAP, hue = CC[e.code] || INK;
  const me = coPath(e, b), pa = coPath(e, p);
  const height = sized(el, 0.6, 400, 540);
  const margin = { l: narrow ? 42 : 54, r: narrow ? 10 : 16, t: 34, b: narrow ? 112 : 100 };
  const plotH = height - margin.t - margin.b;
  const ymax = Math.max.apply(null, me.sr.concat(pa.sr)) * 1.24;

  // solid to 2025, dotted after, as in Figure 4
  const line = (o, proj, color, width, name) => {
    const k = [];
    o.yr.forEach((y, i) => { if (proj ? y >= 2025 : y <= 2025) k.push(i); });
    return { x: k.map(i => o.age[i]), y: k.map(i => +o.sr[i].toFixed(3)), type: 'scatter', mode: 'lines', hoverinfo: 'skip',
      name: name || '', showlegend: !!name, line: { color, width, dash: proj ? 'dot' : 'solid' } };
  };
  // one invisible point per grid year carries the hover, so every label is a data point
  const hover = (o, label) => ({ x: o.age, y: o.sr.map(v => +v.toFixed(3)), customdata: o.yr, type: 'scatter', mode: 'markers',
    showlegend: false, marker: { size: 10, opacity: 0, color: INK },
    hovertemplate: `<b>${label} %{x}</b> · %{customdata}<br>%{y:.1f} workers per retiree<extra></extra>` });

  const calls = [45, 70].map(a => {
    const i = me.age.indexOf(a);
    if (i < 0) return null;
    const k = pa.age.indexOf(a), v = me.sr[i], pv = k < 0 ? null : pa.sr[k];
    const next = me.sr[i + 1] === undefined ? v : me.sr[i + 1], prev = i > 0 ? me.sr[i - 1] : v;
    const falling = next <= prev;
    // keep the label off the parents' curve, and off the axis when the point sits low
    let below = pv === null || pv >= v;
    if (below && (v / ymax) * plotH < 62) below = false;
    const right = below ? !falling : falling;
    const lift = !below && pv !== null && pv > v ? (pv - v) / ymax * plotH : 0;
    return { a, v, pv, yr: me.yr[i], below, right, lift };
  }).filter(Boolean);

  const traces = [
    line(pa, false, CO_PARENT, 1.75, `your parents' cohort · born ${coRange(p)}`), line(pa, true, CO_PARENT, 1.75),
    line(me, false, hue, 3.25, `you · born ${coRange(b)}`), line(me, true, hue, 3.25),
    { x: calls.map(c => c.a), y: calls.map(c => c.v), type: 'scatter', mode: 'markers', hoverinfo: 'skip', showlegend: false,
      marker: { size: 11, color: hue, line: { color: PAPER, width: 2 } } },
    hover(pa, "your parents' cohort at"), hover(me, 'you at'),
  ];

  const now = 2025 - b;
  const band = (x0, x1, fillcolor) => ({ type: 'rect', xref: 'x', yref: 'paper', x0, x1, y0: 0, y1: 1, fillcolor, opacity: 0.55,
    line: { width: 0 }, layer: 'below' });
  const top = { yref: 'paper', y: 1, yanchor: 'bottom', showarrow: false, font: { size: 11.5, color: MUTED } };
  const ticks = [];
  for (let a = 0; a <= 100; a += narrow ? 20 : 10) ticks.push(a);
  const layout = Object.assign({}, BASE, {
    margin, height, hovermode: 'x',
    legend: { orientation: 'h', x: 0.5, xanchor: 'center', yref: 'container', y: 0.01, yanchor: 'bottom', font: { size: narrow ? 11 : 12 } },
    xaxis: grid({ fixedrange: true, range: [-2, 102], tickvals: ticks, tickangle: 0, showgrid: false,
      ticktext: ticks.map(a => `<b>${a}</b><br><span style="color:${MUTED}">${b + a}</span>`),
      title: { text: 'your age, with the calendar year beneath', font: { size: narrow ? 12 : 13, color: MUTED }, standoff: narrow ? 14 : 8 } }),
    yaxis: grid({ title: { text: 'workers per retiree', font: { size: 13, color: MUTED } }, fixedrange: true,
      range: [0, ymax], rangemode: 'tozero' }),
    shapes: [
      band(20, 65, GOOD_SOFT), band(65, 102, WARN_SOFT),
      { type: 'line', xref: 'x', yref: 'paper', x0: now, x1: now, y0: 0, y1: 1, line: { color: MUTED, width: 1 } },
    ],
    annotations: [
      Object.assign({ x: 42.5, text: narrow ? 'working years' : 'working years · 20 to 64' }, top),
      Object.assign({ x: 83.5, text: narrow ? 'retirement' : 'retirement · 65 and over' }, top),
      { x: now, yref: 'paper', y: 0, yanchor: 'bottom', xanchor: now > 70 ? 'right' : 'left', xshift: now > 70 ? -5 : 5,
        text: narrow ? '2025' : (now > 70 ? 'dotted = projected · 2025' : '2025 · dotted = projected'), showarrow: false,
        font: { size: 11.5, color: MUTED } },
    ].concat(calls.map(c => ({
      x: c.a, y: c.v, ax: (c.right ? 1 : -1) * (narrow ? 20 : 46), ay: c.below ? (narrow ? 30 : 38) : -Math.round((narrow ? 30 : 38) + c.lift),
      text: narrow ? `<b>${c.v.toFixed(1)}</b> at ${c.a}`
        : `<b>${c.v.toFixed(1)}</b> at age ${c.a}, in ${c.yr}` + (c.pv === null ? '' : `<br><span style="color:${MUTED}">parents at ${c.a}: ${c.pv.toFixed(1)}</span>`),
      showarrow: true, arrowhead: 0, arrowwidth: 1, arrowcolor: MUTED, standoff: 7, align: 'center',
      font: { size: narrow ? 11.5 : 12, color: INK }, bgcolor: 'rgba(255,255,255,.88)', borderpad: 2,
    }))),
  });
  Plotly.react(el, traces, layout, NOPAD);
}

// Table view of Figure 9, so no value is readable by hover alone.
function coStripTable(e) {
  const host = document.getElementById('life-table');
  if (!host) return;
  const b = CO.b, p = b - CO_GAP;
  const cell = (bb, a) => {
    const j = coIx(FC.years, bb + a);
    return j < 0 ? '<td>–</td>' : `<td>${e.sr[j].toFixed(1)} <small>(${bb + a})</small></td>`;
  };
  let body = '';
  for (let a = 0; a <= 100; a += 5)
    body += `<tr${a === 45 || a === 70 ? ' class="is-focus"' : ''}><th scope="row">${a}</th>${cell(b, a)}${cell(p, a)}</tr>`;
  host.innerHTML = `<table class="ledger tight"><thead><tr><th scope="col">Age</th>
    <th scope="col">You, born ${coRange(b)} <small>(year)</small></th>
    <th scope="col">Your parents' cohort, born ${coRange(p)} <small>(year)</small></th></tr></thead><tbody>${body}</tbody></table>`;
}

/* ------------------------------------------------- Fig 10 · the three cards */
// One bar per cohort from 1925 to 2010: the reader's in the country hue, the
// parents' hatched gray, the rest light. Selecting a bar moves to that cohort.
function coDrawBars(id, e, pick, fmt) {
  const el = CO.mounted[id] || (CO.mounted[id] = mount(id));
  const hue = CC[e.code] || INK, x = [], y = [], color = [], hatch = [], text = [], cd = [];
  for (let b = CO_FIRST; b <= CO_HI; b += 5) {
    const v = pick(coCohort(e, b));
    const who = b === CO.b ? 'you' : b === CO.b - CO_GAP ? "your parents' cohort" : '';
    x.push(b); y.push(v === null ? null : +v.toFixed(4));
    color.push(b === CO.b ? hue : who ? CO_PARENT : CO_REST);
    hatch.push(who && b !== CO.b ? '/' : '');
    text.push(who && v !== null ? fmt(v) : '');
    cd.push([coRange(b), v === null ? '' : fmt(v), who ? ' · ' + who : '']);
  }
  const vals = y.filter(v => v !== null);
  const lo = Math.min(0, Math.min.apply(null, vals)), hi = Math.max(0, Math.max.apply(null, vals));
  const pad = (hi - lo || 1) * 0.26;                       // room for the two value labels
  const trace = { type: 'bar', x, y, width: 3.5, marker: { color, pattern: { shape: hatch, size: 5, solidity: 0.5 } },
    text, textposition: 'outside', textangle: 0, constraintext: 'none', cliponaxis: false,
    textfont: { size: 11.5, color: INK }, customdata: cd,
    hovertemplate: 'born %{customdata[0]}%{customdata[2]}<br><b>%{customdata[1]}</b><extra></extra>' };
  const layout = Object.assign({}, BASE, {
    height: fcFixedHeight(el, 178), margin: { l: 40, r: 6, t: 8, b: 26 }, showlegend: false, barcornerradius: 3,
    xaxis: { fixedrange: true, range: [CO_FIRST - 3.4, CO_HI + 3.4], tickvals: [1925, 1950, 1975, 2000], tickangle: 0,
      tickfont: { size: 11, color: MUTED }, showgrid: false, zeroline: false, linecolor: RULE, ticks: '' },
    yaxis: grid({ fixedrange: true, range: [lo < 0 ? lo - pad : 0, hi > 0 ? hi + pad : 0], nticks: 6,
      tickfont: { size: 11, color: MUTED }, zeroline: true, zerolinecolor: MUTED, zerolinewidth: 1 }),
  });
  Plotly.react(el, [trace], layout, NOPAD);
  if (!el._coClick) {
    el._coClick = true;
    el.on('plotly_click', ev => {
      const bb = ev.points && ev.points[0] && ev.points[0].x;
      if (bb >= CO_LO && bb <= CO_HI) coSetBirth(bb);
    });
  }
}

function coCards(e) {
  const b = CO.b, p = b - CO_GAP, q = coCohort(e, b), pq = coCohort(e, p), name = fcEsc(e.name);
  const set = (id, html) => { const el = document.getElementById(id); if (el) el.innerHTML = html; };
  const Par = `Your parents' cohort (born ${coRange(p)})`;
  const noPar = `The data start in 1950, so this cannot be computed for your parents' cohort (born ${coRange(p)}).`;
  const key = ` <span class="co-key"><i class="co-sw" style="background:${CC[e.code] || INK}"></i>you
    <i class="co-sw" style="background:repeating-linear-gradient(135deg,${CO_PARENT} 0 2px,#fff 2px 4px)"></i>your parents' cohort</span>`;
  const better = (mine, theirs, up) => Math.abs(mine - theirs) < 0.005 ? 'The two are the same.'
    : (mine > theirs) === up ? 'Yours is the better of the two.' : 'Theirs was the better of the two.';

  // 1 · career weather
  const word = q.g <= -0.05 ? 'a headwind' : q.g >= 0.05 ? 'a tailwind' : 'close to neutral';
  set('co-g-big', fcSigned(q.g, 2));
  set('co-g-unit', `points a year · ${word}`);
  set('co-g-say', `Between ages 25 and 65 (${b + 25}–${b + 65}), the age mix ${q.g < 0 ? 'takes' : 'adds'} ${Math.abs(q.g).toFixed(2)} points a year
    ${q.g < 0 ? 'from' : 'to'} the growth of income per person. ` + (Math.abs(q.cum) < 0.5
    ? 'Over the forty years that leaves income per person about where productivity alone would put it.'
    : `Over the forty years that compounds to income per person ${Math.abs(q.cum).toFixed(0)}% ${q.cum < 0 ? 'lower' : 'higher'} than productivity growth alone would deliver.`));
  set('co-g-par', `${Par}: ${fcSigned(pq.g, 2)}. ${better(q.g, pq.g, true)}`);
  set('cap-co-g', `Career term by birth cohort, ${name} (points a year).${key}`);
  coDrawBars('fig-co-g', e, c => c.g, v => fcSigned(v, 2));

  // 2 · the pension deal
  const held = CO.mode === 'benefit', rho = Math.round(100 * CO_RHO);
  set('co-p-eq', held
    ? 'contribution rate <b>=</b> replacement rate <b>÷</b> workers per retiree'
    : 'replacement rate <b>=</b> contribution rate <b>×</b> workers per retiree');
  if (held) {
    const c = 100 * q.c;
    if (pq.c !== null) {
      set('co-p-big', (q.c / pq.c).toFixed(2) + '×');
      set('co-p-unit', "your parents' contribution rate");
      set('co-p-say', `To keep pensions at ${rho}% of average pay, your cohort's workers pay ${c.toFixed(1)}% of their pay,
        averaged over ages 20 to 64. ${Par} paid ${(100 * pq.c).toFixed(1)}%. The ${rho}% is only an illustration: the ratio
        between the two cohorts is the same whatever it is.`);
    } else {
      set('co-p-big', c.toFixed(1) + '%');
      set('co-p-unit', `of pay, to keep pensions at ${rho}% of average pay`);
      set('co-p-say', `That is your cohort's contribution rate averaged over ages 20 to 64. The ${rho}% is only an illustration. ${noPar}`);
    }
    set('cap-co-p', `Contribution rate that holds pensions at ${rho}% of pay, by birth cohort, ${name} (% of pay).${key}`);
    coDrawBars('fig-co-p', e, x => x.c === null ? null : 100 * x.c, v => v.toFixed(1) + '%');
  } else {
    if (q.r === null) {
      set('co-p-big', 'n/a');
      set('co-p-unit', 'needs data beyond 2100');
      set('co-p-say', `This return follows your cohort until it is 100. The UN projection stops at 2100, so it can be
        computed only for cohorts born in 2000 or earlier. Choose an earlier cohort, or switch to “Benefits held”.`);
    } else {
      set('co-p-big', fcSigned(100 * q.r, 2) + '%');
      set('co-p-unit', 'a year, on top of wage growth');
      set('co-p-say', `Hold the contribution rate still, and pensions rise and fall with the number of workers. What your
        cohort pays in between 20 and 64 then comes back in retirement at wage growth ${q.r >= 0 ? 'plus' : 'minus'}
        ${Math.abs(100 * q.r).toFixed(2)}% a year. ` + (pq.r === null ? noPar : `${Par}: ${fcSigned(100 * pq.r, 2)}%. ${better(q.r, pq.r, true)}`));
    }
    set('cap-co-p', `Pay-as-you-go return on top of wage growth, by birth cohort, ${name} (% a year). Cohorts after 2000 need data past 2100.${key}`);
    coDrawBars('fig-co-p', e, x => x.r === null ? null : 100 * x.r, v => fcSigned(v, 2));
  }

  // 3 · the entry market
  if (q.em === null) {
    set('co-e-big', 'n/a'); set('co-e-unit', ''); set('co-e-par', '');
    set('co-e-say', 'One of the two age groups is too small to count in this country.');
  } else {
    set('co-e-big', q.em.toFixed(2));
    set('co-e-unit', `people aged 20–24 for each person aged 60–64, in ${b + 20}`);
    set('co-e-say', q.em < 0.95
      ? 'That year more people are about to leave work than are arriving to replace them. For someone starting out, that is a scarce market: fewer rivals for each job being vacated.'
      : q.em < 1.25 ? 'That year about one person arrives for each one about to leave. Someone starting out is neither scarce nor surplus.'
      : q.em < 2 ? `That year ${q.em.toFixed(2)} young adults arrive for each older worker about to leave. Arrivals outnumber the jobs being vacated, though not by much.`
      : `That year ${q.em.toFixed(2)} young adults arrive for each older worker about to leave. For someone starting out, that is a crowded door.`);
    set('co-e-par', pq.em === null ? noPar : `${Par}: ${pq.em.toFixed(2)}, in ${p + 20}. ${better(q.em, pq.em, false).replace('better', 'less crowded')}`);
  }
  set('cap-co-e', `Entrants per retiree-to-be by birth cohort, ${name}.${key}`);
  coDrawBars('fig-co-e', e, c => c.em, v => v.toFixed(2));
}

/* --------------------------------------------- the reader's own sentences */
function coTakeaways(e) {
  const b = CO.b, p = b - CO_GAP, q = coCohort(e, b), pq = coCohort(e, p);
  const set = (key, html) => document.querySelectorAll(`[data-tk="${key}"]`).forEach(el => { el.innerHTML = ' ' + html; });
  const nm = `<b>${fcEsc(e.name)}, born ${coRange(b)}:</b>`;
  set('co-strip', `${nm} ${q.sr45.toFixed(1)} workers per retiree when you are 45 (${b + 45}) and ${q.sr70.toFixed(1)} when you are 70
    (${b + 70}). Your parents' cohort had ${pq.sr45.toFixed(1)} and ${pq.sr70.toFixed(1)} at the same ages.`);
  const pension = pq.c === null ? `a contribution rate of ${(100 * q.c).toFixed(1)}% of pay with benefits held`
    : `${(q.c / pq.c).toFixed(2)} times your parents' contribution rate with benefits held`;
  const ret = q.r === null ? '' : `, or a return of wage growth ${q.r >= 0 ? 'plus' : 'minus'} ${Math.abs(100 * q.r).toFixed(2)}% a year with contributions held`;
  const entry = q.em === null ? '' : `; ${q.em.toFixed(2)} entrants per retiree-to-be in ${b + 20}` + (pq.em === null ? '' : ` (parents ${pq.em.toFixed(2)})`);
  set('co-cards', `${nm} a career term of ${fcSigned(q.g, 2)} points a year (parents ${fcSigned(pq.g, 2)}); ${pension}${ret}${entry}.`);
}

/* -------------------------------------------------------------- controls */
function coSyncControls() {
  const b = CO.b;
  const t = document.getElementById('co-title');
  if (t) t.textContent = coRange(b);
  const s = document.getElementById('co-year');
  if (s) { s.value = b; s.setAttribute('aria-valuetext', `born ${b - 4} to ${b}`); }
  const o = document.getElementById('co-year-out');
  if (o) o.textContent = coRange(b);
  document.querySelectorAll('#co-presets button').forEach(btn => {
    const on = +btn.dataset.b === b;
    btn.classList.toggle('on', on); btn.setAttribute('aria-pressed', on);
  });
  document.querySelectorAll('#co-mode button').forEach(btn => {
    const on = btn.dataset.mode === CO.mode;
    btn.classList.toggle('on', on); btn.setAttribute('aria-pressed', on);
  });
}

// Draw everything for the current cohort and country, if that country's data is here.
function coPaint() {
  const e = FC.ents.get(coCode());
  if (!e) return;
  coDrawStrip(e); coStripTable(e); coCards(e); coTakeaways(e);
  const who = document.getElementById('co-who');
  if (who) who.innerHTML = FC.focus ? `Showing <b>${fcEsc(e.name)}</b>, the country you are following.`
    : `Showing <b>${fcEsc(e.name)}</b>. Choose a country to follow it here and in every figure above.`;
}

function coSetBirth(b) {
  b = Math.min(CO_HI, Math.max(CO_LO, 5 * Math.round(b / 5)));
  if (b === CO.b) return;
  CO.b = b;
  coSyncControls();
  if (CO.drawn) coPaint();
}

async function coRender() {
  const seq = ++CO.seq, code = coCode();
  try { await fcEnsureBase(); await fcEnsureEntity(code); }
  catch (err) { if (seq === CO.seq && !CO.drawn) coFail(err); return; }
  if (seq !== CO.seq) return;                      // a newer choice superseded this one
  const first = !CO.drawn;
  CO.drawn = true;
  coPaint();
  if (first) fcAuditProse();
}

function coFail(err) {
  ['fig-life', 'fig-co-g', 'fig-co-p', 'fig-co-e'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = '<div class="ph">Could not load the cohort data (' + fcEsc(err) + ').</div>';
  });
}

/* -------------------------------------------------------------------- boot */
document.addEventListener('demographics:ready', () => {
  const sec = document.getElementById('cohort');
  if (!sec) return;
  coSyncControls();
  const presets = document.getElementById('co-presets');
  if (presets) presets.addEventListener('click', ev => {
    const btn = ev.target.closest('button[data-b]');
    if (btn) coSetBirth(+btn.dataset.b);
  });
  const slider = document.getElementById('co-year');
  if (slider) slider.addEventListener('input', () => coSetBirth(+slider.value));
  const mode = document.getElementById('co-mode');
  if (mode) mode.addEventListener('click', ev => {
    const btn = ev.target.closest('button[data-mode]');
    if (!btn || btn.dataset.mode === CO.mode) return;
    CO.mode = btn.dataset.mode;
    coSyncControls();
    const e = FC.ents.get(coCode());
    if (CO.drawn && e) coCards(e);
  });
  // labels and margins depend on the container width; redraw when it crosses the breakpoint
  const strip = document.getElementById('fig-life');
  if (strip && 'ResizeObserver' in window) {
    let last = fcNarrow(strip);
    new ResizeObserver(() => {
      const now = fcNarrow(strip);
      if (now === last) return;
      last = now;
      if (CO.drawn) coPaint();
    }).observe(strip);
  }
  // like section 9, the section draws when the reader gets near it
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(es => { if (es.some(x => x.isIntersecting)) { io.disconnect(); coRender(); } }, { rootMargin: '1400px 0px' });
    io.observe(sec);
  } else coRender();
});

// following a country anywhere on the page moves this section to it
document.addEventListener('demographics:focus', () => { if (CO.drawn) coRender(); });
