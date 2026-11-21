"""Figure 9. Moral hazard vs adverse selection as two graphs, and the tests."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from style import *
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, FancyBboxPatch as FBP
from matplotlib.patches import Circle, Rectangle
import matplotlib.patches as mpatches

def node(ax, x, y, w, h, label, kind):
    colors = {
        "hidden": (HIDDEN_SOFT, HIDDEN),
        "obs": (ACCENT_SOFT, ACCENT),
        "decision": (GOLD_SOFT, GOLD),
        "event": ("#FFFFFF", ACCENT),
        "cut": ("#F4F4F4", "#AAAAAA"),
        "do": (GOLD_SOFT, GOLD),
    }
    fc, ec = colors[kind]
    ls = (0, (2.5, 1.5)) if kind == "cut" else "-"
    ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h,
                                boxstyle="round,pad=0.08,rounding_size=0.12",
                                facecolor=fc, edgecolor=ec, lw=1.05, linestyle=ls, zorder=3))
    ax.text(x, y, label, ha="center", va="center", fontsize=7.2, color=TEXT, zorder=4)


def edge(ax, x1, y1, x2, y2, kind="solid", rad=0.0, color=None):
    if color is None:
        color = "#AAAAAA" if kind == "cut" else ACCENT
    ls = (0, (3, 2)) if kind == "cut" else "-"
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.15 if kind != "cut" else 0.9,
                                mutation_scale=9, linestyle=ls,
                                connectionstyle=f"arc3,rad={rad}"),
                zorder=2)


def panel(ax, title, mode):
    ax.set_xlim(0, 10)
    ax.set_ylim(0.15, 6.3)
    ax.axis("off")
    ax.set_title(title, loc="left", fontsize=8.7, color=TEXT, pad=2)

    # layout: theta at top, coverage left, L/claims right, maybe a or m in the middle
    # y: theta 5.0, middle 3.1, bottom 1.4
    if mode.startswith("as"):
        node(ax, 5.0, 5.15, 1.7, 0.7, "θ  type", "hidden")
        if mode == "as_obs":
            node(ax, 2.3, 2.7, 2.1, 0.75, "coverage", "decision")
            edge(ax, 4.15, 4.80, 2.9, 3.10)  # theta -> coverage
        else:
            node(ax, 2.3, 2.7, 2.1, 0.75, "do(coverage)", "do")
            edge(ax, 4.15, 4.80, 2.9, 3.10, kind="cut")  # cut
            ax.text(3.15, 4.05, "cut", fontsize=6.2, color="#888888", style="italic")
        node(ax, 7.7, 2.7, 1.8, 0.75, "claims  k", "event")
        edge(ax, 5.85, 4.80, 7.2, 3.10)  # theta -> k
        if mode == "as_obs":
            ax.text(5.0, 0.55,
                    "Type is a common cause.\n"
                    "Chosen coverage and claims are associated.\n"
                    "That association is not a test of moral hazard.",
                    fontsize=6.4, color=MUTED, ha="center", va="bottom")
        else:
            ax.text(5.0, 0.55,
                    "Random assignment cuts the edge into coverage.\n"
                    "If this is the only path, coverage and claims\n"
                    "are then independent.  (RAND would find no effect.)",
                    fontsize=6.4, color=MUTED, ha="center", va="bottom")

    if mode.startswith("mh"):
        if mode == "mh_obs":
            node(ax, 2.3, 2.7, 2.1, 0.75, "coverage", "decision")
        else:
            node(ax, 2.3, 2.7, 2.1, 0.75, "do(coverage)", "do")
        node(ax, 5.0, 2.7, 1.7, 0.7, "a  or  m", "hidden")
        node(ax, 7.7, 2.7, 1.8, 0.75, "claims  k", "event")
        edge(ax, 3.35, 2.7, 4.15, 2.7, color=HIDDEN)  # coverage -> a  (the MH edge)
        edge(ax, 5.85, 2.7, 6.80, 2.7, color=HIDDEN)
        ax.text(5.0, 3.25, "moral-hazard path", fontsize=6.2, color=HIDDEN,
                ha="center", style="italic")
        if mode == "mh_obs":
            ax.text(5.0, 0.55,
                    "Coverage causes use or prevention, which causes claims.\n"
                    "The same raw association now has a causal path.\n"
                    "Observationally, it still looks like the left column.",
                    fontsize=6.4, color=MUTED, ha="center", va="bottom")
        else:
            ax.text(5.0, 0.55,
                    "do(coverage) leaves the causal path intact.\n"
                    "Coverage and claims remain associated.\n"
                    "That remaining association is the RAND result.",
                    fontsize=6.4, color=MUTED, ha="center", va="bottom")


def main():
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 6.2), dpi=200)
    panel(axes[0, 0], "A.  Adverse selection only,  coverage chosen", "as_obs")
    panel(axes[0, 1], "B.  Adverse selection only,  after do(coverage)", "as_do")
    panel(axes[1, 0], "C.  Moral hazard (a causal path),  coverage chosen", "mh_obs")
    panel(axes[1, 1], "D.  Moral hazard,  after do(coverage)", "mh_do")
    fig.text(
        0.06, 0.012,
        "Schematic subgraphs of Figure 8.  A dashed arrow is an edge that the intervention has cut.  "
        "The Chiappori–Salanié positive-correlation test is a test of some remaining path in A or C, not of one graph against the other.  "
        "RAND is a version of the right-hand column.",
        fontsize=6.2, color=MUTED,
    )
    fig.subplots_adjust(wspace=0.06, hspace=0.22, left=0.03, right=0.99, top=0.95, bottom=0.10)
    save(fig, "figure09-d-separation")
    print("figure09")

if __name__ == "__main__":
    main()
