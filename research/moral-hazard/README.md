# Moral hazard: information, incentives, and the design of insurance

This folder is a **draft for review**. It is not linked from the live portfolio
site. Nothing here is wired into site navigation, templates, or widgets.

The article is `article.md`. A letter-size reading render is
`moral-hazard-article.pdf`. Supporting notes from the research pack
(`concept-map.md`, `concept-map.json`, `research-plan.md`,
`existing-coverage.md`, `figures-plan.md`, `self-review.md`) sit alongside it.

## Figures

Eleven figures live in `figures/` as PNG (for GitHub Markdown and the PDF) and
SVG. `article.md` references them with relative paths of the form
`figures/figureNN-….png`, so the Markdown file should render with its figures
when viewed on GitHub from this folder.

### How to regenerate the figures

Dependencies: Python 3, matplotlib, and numpy. Labels use DejaVu Sans, which
ships with matplotlib.

From `figures/scripts/`:

```bash
./regenerate.sh
```

Or run the scripts individually:

```bash
python3 fig01_three_games.py
python3 fig02_rs.py
python3 fig03_signals.py
python3 fig04_toy.py
python3 fig05_schedules.py
python3 fig06_bonus_malus.py
python3 fig07_hirshleifer.py
python3 fig08_insurance_dag.py
python3 fig09_dsep.py
python3 fig10_parametric.py
python3 fig11_bailout.py
```

Each script writes `../figureNN-*.png` and `.svg`. Computed curves use the
article's stated, illustrative parameters (mostly W = 121, L = 96,
u(w) = sqrt(w), q(0) = 1/2, q(1) = 1/5). They are not empirical estimates.

The reading PDF is a separate render of `article.md` (Markdown to HTML, KaTeX,
then headless Chrome to PDF). These scripts do not rebuild it.

### Figure 8

Figure 8 (the acyclic insurance DAG) was first drawn without a dedicated
script, so it could not be regenerated from this folder in the same way as the
other ten. That gap is closed: `fig08_insurance_dag.py` now rebuilds
`figure08-insurance-dag.png` and `.svg` in the shared style.

### Figure 11

Figure 11 must be saved with matplotlib's `savefig.bbox: tight` disabled.
Otherwise a slightly overflowing label expands the canvas and the letter-page
PDF shrinks the trees. `fig11_bailout.py` already does this.
