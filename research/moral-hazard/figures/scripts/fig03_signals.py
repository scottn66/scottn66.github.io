"""Figure 3. Informativeness principle and Blackwell garbling. Illustrative."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from style import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib.table import Table

# Likelihood ratios, computed below and also printed.
# Outcome: P(x^H | a^H)=0.8, P(x^H | a^L)=0.5.  LR(x^H)=1.6, LR(x^L)=0.4.
# Informative s, independent of x given a: P(s=c | a^H)=0.75, P(s=c | a^L)=0.25.
#   LR(s=c)=3, LR(s=f)=1/3.
#   Joint LR(x,s)=LR(x) LR(s):
#     (H,c)=4.8, (H,f)=0.533, (L,c)=1.2, (L,f)=0.133
# Garbling of x: P(s=h | x^H)=0.9, P(s=h | x^L)=0.2, independent of a given x.
#   Then LR(x,s)=LR(x) for every s, so given x the signal does not change the ratio.

LR_INFO = {
    ("x^H", "c"): 0.8 * 0.75 / (0.5 * 0.25),  # 4.8
    ("x^H", "f"): 0.8 * 0.25 / (0.5 * 0.75),  # 0.533...
    ("x^L", "c"): 0.2 * 0.75 / (0.5 * 0.25),  # 1.2
    ("x^L", "f"): 0.2 * 0.25 / (0.5 * 0.75),  # 0.133...
}
# Given x^H, LR still depends on s: 4.8 vs 0.533
# Garble:
# f(x^H,s=h|a^H)=0.8*0.9=0.72; f(x^H,s=h|a^L)=0.5*0.9=0.45; LR=1.6
# same for s=l: 0.8*0.1/0.5*0.1=1.6


def box(ax, x, y, w, h, text, fc, ec, fs=7.4):
    ax.add_patch(FancyBboxPatch((x - w/2, y - h/2), w, h,
                                boxstyle="round,pad=0.08,rounding_size=0.12",
                                facecolor=fc, edgecolor=ec, lw=1.05, zorder=3))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=TEXT,
            zorder=4, linespacing=1.2)


def arrow(ax, x1, y1, x2, y2, text=None, off=(0, 0.18)):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=1.0, mutation_scale=9),
                zorder=2)
    if text:
        ax.text((x1+x2)/2 + off[0], (y1+y2)/2 + off[1], text,
                ha="center", va="center", fontsize=6.5, color=MUTED)


def draw_matrix(ax, left, bottom, cells, title, note, cols):
    """cells: list of (row_label, col_label, value_str, highlight bool)"""
    ax.text(left, bottom + 2.15, title, fontsize=8.6, color=TEXT, fontweight="bold")
    rows = ["x = high", "x = low"]
    # header
    col_x = [left + 1.35, left + 2.55]
    row_y = [bottom + 1.35, bottom + 0.55]
    ax.text(left + 0.15, bottom + 1.85, "LR(x, s)", fontsize=6.6, color=MUTED, ha="left")
    for i, c in enumerate(cols):
        ax.text(col_x[i], bottom + 1.85, c, ha="center", va="center", fontsize=6.6, color=MUTED)
    for j, r in enumerate(rows):
        ax.text(left + 0.15, row_y[j], r, ha="left", va="center", fontsize=6.6, color=MUTED)
    vals = cells
    for j in range(2):
        for i in range(2):
            val, hl = vals[j][i]
            fc = HIDDEN_SOFT if hl else ACCENT_SOFT
            ec = HIDDEN if hl else ACCENT
            rect = FancyBboxPatch((col_x[i]-0.52, row_y[j]-0.32), 1.04, 0.64,
                                  boxstyle="round,pad=0.04,rounding_size=0.08",
                                  facecolor=fc, edgecolor=ec, lw=1.0, zorder=3)
            ax.add_patch(rect)
            ax.text(col_x[i], row_y[j], val, ha="center", va="center",
                    fontsize=8.4, color=TEXT, zorder=4)
    ax.text(left, bottom + 0.05, note, fontsize=6.4, color=MUTED, va="top", linespacing=1.3)


def panel_a(ax):
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.5)
    ax.axis("off")
    ax.set_title("A.  When an extra signal belongs in the contract", loc="left",
                 fontsize=9, color=TEXT, pad=2)
    # two matrices side by side
    # Informative
    cells_i = [[("4.80", True), ("0.53", True)],
               [("1.20", True), ("0.13", True)]]
    draw_matrix(ax, 0.15, 1.55, cells_i,
                "s is informative about a, given x",
                "Given either outcome, the likelihood ratio still depends on s.\n"
                "The contract w(x, s) should use s.",
                ["s = clean", "s = flag"])
    # Garbling / sufficient
    cells_g = [[("1.60", False), ("1.60", False)],
               [("0.40", False), ("0.40", False)]]
    draw_matrix(ax, 5.15, 1.55, cells_g,
                "s is a noisy reading of x only",
                "Given x, the likelihood ratio does not depend on s.\n"
                "x is a sufficient statistic.  s can be ignored.",
                ["s = high", "s = low"])
    ax.text(0.15, 0.15,
            "Each cell is the likelihood ratio f(x, s | a high) / f(x, s | a low).  "
            "Illustrative probabilities are in the caption.",
            fontsize=6.4, color=MUTED, va="bottom")


def panel_b(ax):
    ax.set_xlim(0, 10)
    ax.set_ylim(0.15, 4.3)
    ax.axis("off")
    ax.set_title("B.  A Blackwell garbling", loc="left", fontsize=9, color=TEXT, pad=2)

    box(ax, 1.3, 2.4, 1.7, 0.9, "Hidden action\n(or the state)", HIDDEN_SOFT, HIDDEN)
    box(ax, 4.3, 2.4, 1.9, 0.9, "Experiment  s_A\n(finer signal)", ACCENT_SOFT, ACCENT)
    box(ax, 8.0, 2.4, 2.2, 0.9, "Experiment  s_B\n(garbled signal)", GOLD_SOFT, GOLD)
    arrow(ax, 2.18, 2.4, 3.32, 2.4, "depends on a")
    arrow(ax, 5.28, 2.4, 6.88, 2.4, "further noise,\nindependent of a", off=(0, 0.38))

    # small kernel annotation under s_B arrow
    ax.text(5.0, 1.25,
            "s_B is a garbling of s_A: it can be drawn from s_A by an extra layer of noise\n"
            "that does not depend on the action.  Every expected-utility decision maker then\n"
            "weakly prefers s_A to s_B (Blackwell 1953).  In the hidden-action problem, a principal\n"
            "should not pay for s_B if s_A is already in the contract: s_B cannot tighten the\n"
            "likelihood ratios given s_A.  The order is only partial; many real monitors are incomparable.",
            fontsize=6.6, color=MUTED, va="top")


def main():
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 6.4), dpi=200,
                             gridspec_kw={"height_ratios": [1.15, 1]})
    panel_a(axes[0])
    panel_b(axes[1])
    fig.subplots_adjust(hspace=0.18, left=0.04, right=0.98, top=0.95, bottom=0.03)
    save(fig, "figure03-informativeness-blackwell")
    print("figure03", {k: round(v, 4) for k, v in LR_INFO.items()})

if __name__ == "__main__":
    main()
