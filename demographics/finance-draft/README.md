# Finance section draft: the productivity-weighted age structure

Review draft on the `review/demographics-finance` branch. Not part of the live site. See `REVIEW.md` for the reviewer brief.

Open `index.html` (`data/data.js` is loaded as a script, so opening the file directly works; a local HTTP server also works). The page matches the live demographics essay's type, color, Plotly 2.35.2 and KaTeX, and is meant to sit beside Figure 3 of [The Shape of People to Come](https://scottn66.github.io/demographics/), not replace it.

## What this tests

A person's labor income peaks in the forties (age 44 on the measured NTA average). Weighting a country's age distribution by that lifecycle gives a single score \(S\): how much of the high-earning part of the life the country's current (or 2050) age structure is sitting on.

\[ S_t = \sum_a w(a)\, s(a,t) \]

A weighted product is not used: labor income is zero in childhood, so any product collapses to zero in every country. The economic support ratio \(SR\) is shown as a companion (toggle on the ranking chart).

## Result, in brief

The hypothesis is informative. In 2025, \(S\) is highest among large economies in Saudi Arabia, South Korea, China, Iran and Thailand, and lowest in Niger, Nigeria, Ethiopia, Pakistan and Kenya. The full 236-country list is led by Gulf states with working-age migrant populations (Qatar 0.713) and ends in young Central and West Africa (Central African Republic 0.297). The 2025-to-2050 change is the sharper finding: South Korea falls from 0.579 (17th of 236) to 0.466 (188th); the Philippines rises from 0.493 (135th) to 0.556 (10th); India rises from 0.518 (101st) to 0.542 (19th). The world population-weighted average barely moves (0.500 to 0.501). Against median age, \(S\) has the predicted inverted-U.

This is not a GDP ranking. See the caveats on the page.

## Data, actually used

- **Population.** UN World Population Prospects 2024, medium variant, 5-year age groups for 2025 and 2050, taken from the country files already shipped with the live essay (`demographics/data/countries/*.json`), themselves built from the [PPgp/wpp2024](https://github.com/PPgp/wpp2024) package. Official UN page: https://population.un.org/wpp/. License: [CC BY 3.0 IGO](https://creativecommons.org/licenses/by/3.0/igo/).
- **Labor-income and consumption profiles.** 56 NTA country-team ("Country estimate") profiles, unweighted average, from Mason, Lee, Abrigo and Lee, "Support Ratio and Demographic Dividends: Estimates for the World," UN DESA Population Division Technical Paper 2017/1. Downloaded from https://ntaccounts.org/doc/repository/Yl%20and%20C%20CSV.csv (a copy is in `data/source/nta-yl-c-2017.csv`). Project page: https://ntaccounts.org/web/nta/show/Documents/UNPD%20Project%202016. Unit: each profile is normalized so the mean of ages 30 to 49 equals 1.
- **Stylized comparison curve.** The same formula as Figure 3 on the live page (`stylized_profiles()` in `scripts/build_demographics_data.py`), renormalized to a 30-49 mean of 1. Country scores from the measured average and from the stylized curve correlate at 0.99. The measured average is the primary weight.

## Files

- `index.html` and `finance.js`: the self-contained prototype.
- `data/data.js`: embedded data the page loads (no fetch).
- `data/scores.json`: all 236 countries, with ranks.
- `data/display.json`: the 34-country test set, including age-share vectors.
- `data/profiles.json`: the NTA average, the stylized pair, and 7 country-example profiles.
- `data/report.txt`: a text dump of leaderboards, written by the compute script.
- `data/source/`: the downloaded NTA CSV and the UNPD project page.
- `scripts/compute_scores.py`: recomputes everything from the NTA CSV plus a local checkout of `scottn66.github.io` (the run that produced these files used `/tmp/portfolio-ro/scottn66.github.io`).
- Plotly.js 2.35.2 and KaTeX 0.16.9 load from pinned CDN URLs with SRI hashes (byte-identical to the copies the live site self-hosts).
- `screenshots/`: crops of the four figures.

## Relation to the live essay

Sections 3 and 4 of the live page already define the life-cycle of labor income and the NTA economic support ratio, and the atlas already reports a per-country ESR (computed from a stylized profile and single-year ages). This draft adds a finance-section framing, a measured NTA average as the weight, the simpler headcount-denominator score \(S\), and visualizations the live page does not have: a 2025/2050 dumbbell, an inverted-U scatter of all 236 countries, and small-multiples of age structure under the weight curve. It is not folded into the atlas (section 7 of the essay). The site's `cartography.html` is a different project (city street maps).
