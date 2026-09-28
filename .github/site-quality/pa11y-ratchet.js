#!/usr/bin/env node
'use strict';

// Compares a pa11y-ci WCAG2AA run to .github/site-quality/pa11y-baseline.json.
//
//   node .github/site-quality/pa11y-ratchet.js check
//   node .github/site-quality/pa11y-ratchet.js update
//
// The site must already be serving on $SITE_PORT (default 4173).
// check fails when a contrast count rises, a count falls (lower the baseline),
// an unscanned baseline page disappears, a page outside the baseline has
// errors, or any non-contrast error appears that is not in DEFERRED.

const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const BASELINE_PATH = path.join(__dirname, 'pa11y-baseline.json');

const CONTRAST_CODES = new Set([
  'WCAG2AA.Principle1.Guideline1_4.1_4_3.G18.Fail',
  'WCAG2AA.Principle1.Guideline1_4.1_4_3.G145.Fail',
]);

// Non-contrast errors that this PR is not allowed to restyle away.
// Counts are still ratcheted: a rise fails, a drop requires `update`.
const DEFERRED = {
  'bitcoin-power-law/': [
    'WCAG2AA.Principle4.Guideline4_1.4_1_2.H91.A.EmptyNoId',
  ],
};

function pa11yBin() {
  if (process.env.PA11Y_CI) return process.env.PA11Y_CI;
  const candidates = [
    '/tmp/site-quality/node_modules/.bin/pa11y-ci',
    path.join(ROOT, 'node_modules', '.bin', 'pa11y-ci'),
  ];
  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) return candidate;
  }
  return 'pa11y-ci';
}

function pageKey(pageUrl) {
  const pathname = new URL(pageUrl).pathname.replace(/^\//, '');
  return decodeURIComponent(pathname);
}

function runPa11y() {
  const bin = pa11yBin();
  const result = spawnSync(
    bin,
    ['--config', path.join(ROOT, '.pa11yci.js'), '--reporter', 'json'],
    {
      cwd: ROOT,
      encoding: 'utf8',
      env: process.env,
      maxBuffer: 64 * 1024 * 1024,
    },
  );
  const stdout = result.stdout || '';
  const start = stdout.indexOf('{');
  const end = stdout.lastIndexOf('}');
  if (start === -1 || end === -1) {
    process.stderr.write(result.stderr || '');
    process.stderr.write(stdout);
    throw new Error(`pa11y-ci produced no JSON (exit ${result.status})`);
  }
  let report;
  try {
    report = JSON.parse(stdout.slice(start, end + 1));
  } catch (error) {
    process.stderr.write(result.stderr || '');
    throw new Error(`pa11y-ci JSON parse failed: ${error.message}`);
  }
  if (result.error) throw result.error;
  if (result.status !== 0 && result.status !== 2) {
    process.stderr.write(result.stderr || '');
    throw new Error(`pa11y-ci failed to run (exit ${result.status})`);
  }
  return report;
}

function tally(report) {
  const pages = new Map();
  for (const [pageUrl, issues] of Object.entries(report.results || {})) {
    const key = pageKey(pageUrl);
    const contrast = {};
    const nonContrast = {};
    const runners = [];
    for (const issue of issues) {
      if (!issue || !issue.code) {
        runners.push(issue && issue.message ? issue.message : 'unknown runner error');
        continue;
      }
      if (CONTRAST_CODES.has(issue.code)) {
        contrast[issue.code] = (contrast[issue.code] || 0) + 1;
      } else {
        nonContrast[issue.code] = (nonContrast[issue.code] || 0) + 1;
      }
    }
    const contrastTotal = Object.values(contrast).reduce((sum, n) => sum + n, 0);
    pages.set(key, { contrastTotal, contrast, nonContrast, runners });
  }
  return pages;
}

function loadBaseline() {
  return JSON.parse(fs.readFileSync(BASELINE_PATH, 'utf8'));
}

function check() {
  const baseline = loadBaseline();
  const measured = tally(runPa11y());
  const failures = [];

  for (const [key, entry] of measured) {
    if (entry.runners.length) {
      failures.push(`${key} could not be tested: ${entry.runners.join('; ')}`);
    }
    const allowed = new Set(DEFERRED[key] || []);
    for (const [code, count] of Object.entries(entry.nonContrast)) {
      if (!allowed.has(code)) {
        failures.push(
          `${key} has ${count} non-contrast error(s) ${code}. Only contrast errors are grandfathered.`,
        );
      }
    }
    const base = baseline.pages && baseline.pages[key];
    if (!base) {
      const total =
        entry.contrastTotal +
        Object.values(entry.nonContrast).reduce((sum, n) => sum + n, 0);
      if (total > 0) {
        failures.push(
          `${key} is not in the baseline and has ${total} error(s). Fix them, or add a contrast count with \`node .github/site-quality/pa11y-ratchet.js update\` after reviewing them.`,
        );
      }
      continue;
    }
    if (entry.contrastTotal > base.contrast) {
      failures.push(
        `${key} contrast errors rose from ${base.contrast} to ${entry.contrastTotal}.`,
      );
    } else if (entry.contrastTotal < base.contrast) {
      failures.push(
        `${key} contrast errors fell from ${base.contrast} to ${entry.contrastTotal}. Lower the baseline in this PR: node .github/site-quality/pa11y-ratchet.js update`,
      );
    }
    const deferred = base.deferredNonContrast || {};
    for (const code of allowed) {
      const actual = entry.nonContrast[code] || 0;
      const expected = deferred[code] || 0;
      if (actual > expected) {
        failures.push(
          `${key} deferred non-contrast ${code} rose from ${expected} to ${actual}.`,
        );
      } else if (actual < expected) {
        failures.push(
          `${key} deferred non-contrast ${code} fell from ${expected} to ${actual}. Lower the baseline in this PR: node .github/site-quality/pa11y-ratchet.js update`,
        );
      }
    }
  }

  for (const key of Object.keys(baseline.pages || {})) {
    if (!measured.has(key)) {
      failures.push(
        `${key} is in the baseline but was not tested. Do not drop it from .pa11yci.js to hide errors.`,
      );
    }
  }

  if (failures.length) {
    console.error('pa11y ratchet failed:');
    for (const line of failures) console.error(`- ${line}`);
    process.exit(1);
  }
  const contrast = [...measured.values()].reduce((sum, entry) => sum + entry.contrastTotal, 0);
  console.log(`pa11y ratchet passed (${measured.size} pages, ${contrast} grandfathered contrast errors).`);
}

function update() {
  const measured = tally(runPa11y());
  const failures = [];
  const pages = {};

  for (const [key, entry] of measured) {
    if (entry.runners.length) {
      failures.push(`${key} could not be tested: ${entry.runners.join('; ')}`);
    }
    const allowed = new Set(DEFERRED[key] || []);
    for (const [code, count] of Object.entries(entry.nonContrast)) {
      if (!allowed.has(code)) {
        failures.push(
          `${key} has ${count} non-contrast error(s) ${code}. Fix them before updating the baseline; this script will not grandfather a new non-contrast code.`,
        );
      }
    }
    const deferred = {};
    for (const code of allowed) {
      const count = entry.nonContrast[code] || 0;
      if (count > 0) deferred[code] = count;
    }
    if (entry.contrastTotal > 0 || Object.keys(deferred).length) {
      pages[key] = { contrast: entry.contrastTotal };
      if (Object.keys(deferred).length) pages[key].deferredNonContrast = deferred;
    }
  }

  if (failures.length) {
    console.error('refusing to write the baseline:');
    for (const line of failures) console.error(`- ${line}`);
    process.exit(1);
  }

  const ordered = {};
  for (const key of Object.keys(pages).sort()) ordered[key] = pages[key];
  const document = {
    standard: 'WCAG2AA',
    notes:
      'Per-page WCAG 2.1 AA error counts. contrast is grandfathered (G18 and G145 only) and must match exactly: a rise fails the job, a drop means lower this file in the same PR. deferredNonContrast is an explicit allowlist for errors that are not contrast and are burned down in a later PR; any other non-contrast error fails. Regenerate with the site already serving: node .github/site-quality/pa11y-ratchet.js update',
    pages: ordered,
  };
  fs.writeFileSync(BASELINE_PATH, `${JSON.stringify(document, null, 2)}\n`);
  const contrast = Object.values(ordered).reduce((sum, entry) => sum + entry.contrast, 0);
  console.log(`wrote ${path.relative(ROOT, BASELINE_PATH)} (${Object.keys(ordered).length} pages, ${contrast} contrast errors).`);
}

const command = process.argv[2];
if (command === 'check') check();
else if (command === 'update') update();
else {
  console.error('usage: node .github/site-quality/pa11y-ratchet.js <check|update>');
  process.exit(1);
}
