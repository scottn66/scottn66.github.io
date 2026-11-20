Scripts that build the article figures. Shared typography is in `style.py`.

Dependencies: Python 3, matplotlib, and numpy. DejaVu Sans is used for labels
and should be present with matplotlib.

From this directory, regenerate every figure:

    ./regenerate.sh

Or run one script at a time:

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

Each script writes PNG and SVG next to this folder, as `../figureNN-*.png` and `.svg`.
Computed curves use stated, illustrative parameters, mostly the article's toy example
(W = 121, L = 96, u(w) = sqrt(w), q(0) = 1/2, q(1) = 1/5).

Figure 8 was first drawn without a dedicated script. `fig08_insurance_dag.py` now
regenerates it in the same style as the others.

Figure 11 must be saved with matplotlib's `savefig.bbox: tight` disabled, otherwise
a slightly overflowing label expands the canvas and the letter-page PDF shrinks the
trees. The script already does this; do not wrap its `savefig` in a tight bbox.

The reading PDF is a separate render of `article.md` and is not produced by these scripts.
