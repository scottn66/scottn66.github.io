// WCAG 2.1 AA for the site's top-level pages (repo-root documents and
// project front doors). Nested reports, heatmaps, and vendored plots are
// out of this list; lychee still checks every HTML file for broken links.
//
// Ignores are one URL and one rule, each with a reason. Do not add a
// site-wide ignore.

const port = process.env.SITE_PORT || '4173';
const origin = `http://127.0.0.1:${port}`;

const rootPages = [
  'index.html',
  'HMM.html',
  'MAB.html',
  'Q.html',
  'actuarial-pricing.html',
  'applied-decision-theory.html',
  'arxiv_scraper.html',
  'cartography.html',
  'cartography_landing.html',
  'conscious-agents-conjectures.html',
  'conscious-agents.html',
  'dashboard.html',
  'decision-theory.html',
  'mandelbrot.html',
  'mandelbrot_landing.html',
  'ner-taggers.html',
  'resume.html',
  'sep_scraper.html',
  'wikipedia_scraper.html',
];

const projectFrontDoors = [
  'bitcoin-power-law/',
  'demographics/',
  'robot-arm-sim/',
  'solar/',
  'sun/',
];

const urls = [...rootPages, ...projectFrontDoors].map((path) => {
  const url = `${origin}/${path}`;

  // #country/ISO and #state/XX are routes in demographics/app.js (hashchange),
  // not element ids, so the named-anchor check is a false positive here.
  if (path === 'demographics/') {
    return {
      url,
      ignore: [
        'WCAG2AA.Principle2.Guideline2_4.2_4_1.G1,G123,G124.NoSuchID',
      ],
    };
  }

  // modal-title is an empty template inside a display:none Bootstrap dialog;
  // openModal() fills the heading before the dialog is shown.
  if (path === 'dashboard.html') {
    return {
      url,
      ignore: [
        'WCAG2AA.Principle1.Guideline1_3.1_3_1.H42.2',
      ],
    };
  }

  return url;
});

module.exports = {
  defaults: {
    standard: 'WCAG2AA',
    runners: ['htmlcs'],
    timeout: 60000,
    wait: 400,
    includeNotices: false,
    includeWarnings: false,
    chromeLaunchConfig: {
      executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome',
      args: [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--headless=new',
      ],
    },
  },
  concurrency: 4,
  urls,
};
