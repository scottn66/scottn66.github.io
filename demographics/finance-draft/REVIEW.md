# Reviewer brief: a productivity-weighted age-structure score

This folder is a draft. It is not part of the live site, and GitHub Pages does not serve this branch. It is a proposed finance section for the demographics essay [The Shape of People to Come](https://scottn66.github.io/demographics/), shared so independent reviewers can check the method before anything is published.

Please leave feedback as a GitHub issue on this repository (mention `review/demographics-finance` in the title) or as a comment on a commit in this branch. Specific objections with a source are the most useful kind.

Scott Nelson, Data Engineer

## The hypothesis

A person's labor income is low at entry to the labor market, rises through working life, peaks in middle age, and falls in retirement. Children and retirees sit at the two ends of the same curve. If that curve is used to weight a country's population by age, the result is one number per country: how much of its population sits in the high-earning ages. The draft asks whether that number, today and in 2050, sorts countries in a way that is informative.

## The score

For a country at date t, with population share s(a, t) at age a and a labor-income weight w(a):

```
S_t = Σ_a w(a) · s(a, t)
```

S is the average labor-income weight of a person drawn at random from the population. A population made entirely of 30-to-49-year-olds would score 1.

The weight is not a hand-drawn curve. It is the unweighted average of 56 country-team labor-income profiles from the National Transfer Accounts (NTA) project, published with Mason, Lee, Abrigo and Lee, "Support Ratio and Demographic Dividends: Estimates for the World," UN DESA Population Division Technical Paper 2017/1. Each profile is normalized so the mean labor income of ages 30 to 49 equals 1, which is the NTA convention, and the average is renormalized so that holds exactly. The average peaks at age 44, at 1.05. NTA profiles stop at age 90, so ages 91 to 100+ reuse the age-90 value. Single-year weights are averaged inside each 5-year age group to match the population data.

Population is UN World Population Prospects 2024, medium variant, 5-year age groups, for 2025 and 2050, taken from the country files the essay already ships in `demographics/data/countries/`.

## Why a sum and not a product

Scott's first idea allowed either a weighted sum or a weighted product. The product does not work here. Labor income is zero, or close to it, in childhood, so any product or geometric mean that includes the child ages is zero for every country. A product of population shares raised to the weights also changes with the width of the age bins, which is an arbitrary choice. The sum has neither problem, and it is already the numerator of the NTA economic support ratio.

## Cross-check against the support ratio

The NTA economic support ratio divides effective producers by effective consumers:

```
SR_t = Σ_a y_l(a) P(a, t) / Σ_a c(a) P(a, t)
```

using the matching 56-country average consumption profile c(a). Across all 236 countries and territories in 2025, S and SR correlate at 0.986. S computed with the measured NTA average and S computed with the stylized curve the essay already uses for its Figure 3 correlate at 0.992. Grouping by 5-year bins, compared with the essay's single-year support ratio, moves values by 0.001 on average. Levels of SR here are relative to the profiles, because labor income and consumption are each normalized to their own 30-to-49 mean, so they should not be compared with the essay's published SR levels. Ranks and changes are the reliable part.

## Main results

All figures come from `data/report.txt` and `data/scores.json`.

- Highest S in 2025: Qatar (0.713), United Arab Emirates (0.677), Kuwait (0.665), Bahrain (0.645). Lowest: Central African Republic (0.297), Niger (0.331), Somalia (0.335), DR Congo (0.339), Mali (0.340).
- Among the 34-country test set used in the charts, the top in 2025 is Saudi Arabia (0.580), South Korea (0.5785), China (0.569), Iran (0.562) and Thailand (0.561). The bottom is Niger (0.331), Nigeria (0.380), Ethiopia (0.391), Pakistan (0.413) and Kenya (0.415). The United States is 0.515 and Japan 0.495.
- The world population-weighted average is 0.5002 in 2025 and 0.5015 in 2050.
- The 2050 changes are the sharper result. South Korea goes from 17th of 236 to 188th (0.5785 to 0.466) and Taiwan from 18th to 183rd (0.577 to 0.468). Spain falls from 55th to 204th, Japan from 132nd to 216th. The Philippines goes from 135th to 10th (0.493 to 0.556), and India from 101st to 19th (0.518 to 0.542). Nigeria rises from 0.380 to 0.469 but stays below the world average.
- The 2025 and 2050 scores correlate at only 0.628 across countries, so the ranking is far from stable over 25 years.
- Against median age, S rises steeply in young countries, flattens between median ages of about 30 and 50, and falls in the oldest group. S correlates at 0.738 with median age and 0.772 with the share of people aged 45 to 64.

## Known caveats

- **Gulf migrant effect.** The top of the list is Gulf states whose working-age populations are large because of labor migration. That is a real feature of their age structure, but it says nothing about the income of the people counted, and the 2050 positions depend on migration assumptions in the medium variant.
- **One pooled profile.** Every country gets the same weight curve. That isolates age structure, but real profiles differ a lot. In the 56-country file, labor income peaks at 29 in Vietnam (2012) and 32 in China (2007), against 49 in the United States (2011). The profiles are vintages from 2002 to 2015.
- **Not GDP.** S says nothing about capital, education, productivity per worker, wages or institutions. A high score means the age structure is favorable under a common profile. It does not mean a country is rich or will grow.
- **Projection.** 2050 uses the UN medium variant. Most people of working age in 2050 are already alive, so the working ages are mostly a survival-and-aging calculation, but fertility and migration still move the child shares and, in migrant-heavy countries, the working-age counts.

## How to reproduce

From the repository root, with Python 3, numpy and pandas:

```
python3 demographics/finance-draft/scripts/compute_scores.py
```

Inputs:

- `demographics/finance-draft/data/source/nta-yl-c-2017.csv`, downloaded unchanged from https://ntaccounts.org/doc/repository/Yl%20and%20C%20CSV.csv (project page: https://ntaccounts.org/web/nta/show/Documents/UNPD%20Project%202016).
- `demographics/data/countries-summary.json` and `demographics/data/countries/*.json` on this branch, the essay's WPP 2024 files built by `scripts/build_demographics_data.py` from the [PPgp/wpp2024](https://github.com/PPgp/wpp2024) package.

Outputs are rewritten in `demographics/finance-draft/data/`: `scores.json` (all 236 with ranks), `profiles.json`, `display.json`, `report.txt` and `data.js`. Running the script on a fresh clone reproduced `scores.json` and `profiles.json` byte for byte.

To look at the page, clone the branch and open `demographics/finance-draft/index.html` in a browser. Plotly.js 2.35.2 and KaTeX 0.16.9 load from pinned CDN URLs with integrity hashes.

## Questions for reviewers

1. Is a pooled 56-country average a defensible weight for countries at very different income levels, or should low-income and high-income countries get separate profiles? The same NTA file also has model-estimated profiles for 165 countries, which could support either approach.
2. NTA labor income covers wages, most of mixed income, and labor-related taxes. Does it capture informal work well enough in countries where informal work is most of the labor market?
3. The weight is not split by sex. Where female labor participation is low, does the pooled curve overstate the score of the working ages? Would sex-specific profiles (available for some NTA countries) change the ranking?
4. How sensitive are the 2050 ranks to the WPP migration assumptions, particularly for the Gulf states and for countries with large emigration? Would the low or high variant change any conclusion?
5. The 2025 and 2050 scores correlate at 0.628. Is the 2050 rank stable enough to report country by country, or should the page only describe broad groups?
6. Should the weight be labor income at all? Alternatives include taxes paid by age, labor income net of consumption (the life-cycle surplus), or hours worked. Which would best match the claim that peak contribution comes in mid-to-late career?
7. Holding the profile fixed was a choice. Would a sensitivity run that uses each of the 56 countries' own profile tell you more than it confuses?
8. The profile peaks at 44, earlier than the "toward the end of the working career" framing in the original idea. Is that framing wrong, or is the NTA average dragged earlier by the younger-peaking countries?
9. Does averaging single-year weights inside 5-year groups, and reusing the age-90 value past 90, bias any country enough to matter?
10. Is there earlier published work that computes this exact headcount-denominator score? If so, please point to it so the page can cite it rather than present it as new.
