# scottn66.github.io

## Site quality

`.github/workflows/site-quality.yml` fails the build on broken internal links and assets, on external HTTP 404 and 410, and on WCAG 2.1 AA regressions against `.github/site-quality/pa11y-baseline.json`. Timeouts, HTTP 403, and HTTP 429 do not fail the job. A tracked file over 1 MiB fails unless it is listed in `.github/site-quality/byte-budget-allowlist.txt`. See `.github/site-quality/README.md`.

Contrast errors already in that file are grandfathered. A page's count may not go up. A count that goes down fails until you lower the baseline in the same PR. Any non-contrast error fails, except the deferred codes named in `.github/site-quality/pa11y-ratchet.js`.

To regenerate the baseline, serve the site and run:

```
python3 -m http.server 4173
SITE_PORT=4173 node .github/site-quality/pa11y-ratchet.js update
```

`pa11y-ci` is installed by the workflow (`PA11Y_CI` can point at another binary). The update command refuses to record a new non-contrast error.
