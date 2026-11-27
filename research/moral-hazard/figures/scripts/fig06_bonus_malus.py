"""Figure 6. Bonus-malus as a Markov chain. Illustrative, toy-example claim rates."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from style import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Arc
from matplotlib.patches import FancyArrowPatch as FAP

# 3 classes: 1 best, 3 worst
# no claim -> one class better (or stay at 1); claim -> one class worse (or stay at 3)
# q(0)=1/2, q(1)=1/5  from the toy example
# stationary: a=0 uniform (1/3 each); a=1 = (16/21, 4/21, 1/21)


def draw_chain(ax):
    ax.set_xlim(0, 10)
    ax.set_ylim(0.2, 4.6)
    ax.axis("off")
    ax.set_title("A.  Transition rule on three rating classes", loc="left", fontsize=9, color=TEXT, pad=2)
    xs = [2.0, 5.0, 8.0]
    labels = ["Class 1\nbest premium", "Class 2", "Class 3\nworst premium"]
    for x, lab in zip(xs, labels):
        ax.add_patch(FancyBboxPatch((x-0.95, 2.05), 1.9, 1.15,
                                    boxstyle="round,pad=0.1,rounding_size=0.15",
                                    facecolor=ACCENT_SOFT, edgecolor=ACCENT, lw=1.1, zorder=3))
        ax.text(x, 2.62, lab, ha="center", va="center", fontsize=7.4, color=TEXT, zorder=4)

    def arr(x1, y1, x2, y2, text, color, rad=0.0, off=(0, 0.2)):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=1.15,
                                    mutation_scale=9, connectionstyle=f"arc3,rad={rad}"),
                    zorder=2)
        mx, my = (x1+x2)/2 + off[0], (y1+y2)/2 + off[1]
        ax.text(mx, my, text, fontsize=6.4, color=color, ha="center", va="center")

    # no-claim arrows leftward on top
    arr(4.05, 3.22, 2.95, 3.22, "no claim,  1 − q(a)", TEAL, rad=0, off=(0, 0.22))
    arr(7.05, 3.22, 5.95, 3.22, "no claim,  1 − q(a)", TEAL, rad=0, off=(0, 0.22))
    # self loop class 1 no claim
    ax.annotate("", xy=(1.15, 3.05), xytext=(1.15, 2.25),
                arrowprops=dict(arrowstyle="-|>", color=TEAL, lw=1.1, mutation_scale=8,
                                connectionstyle="arc3,rad=0.8"), zorder=2)
    ax.text(0.35, 2.65, "no claim\n(stay)", fontsize=6.2, color=TEAL, ha="center")

    # claim arrows rightward on bottom
    arr(2.95, 2.03, 4.05, 2.03, "claim,  q(a)", VERM, rad=0, off=(0, -0.28))
    arr(5.95, 2.03, 7.05, 2.03, "claim,  q(a)", VERM, rad=0, off=(0, -0.28))
    ax.annotate("", xy=(8.85, 2.25), xytext=(8.85, 3.05),
                arrowprops=dict(arrowstyle="-|>", color=VERM, lw=1.1, mutation_scale=8,
                                connectionstyle="arc3,rad=0.8"), zorder=2)
    ax.text(9.65, 2.65, "claim\n(stay)", fontsize=6.2, color=VERM, ha="center")

    ax.text(0.2, 0.45,
            "A claim-free year moves one class better; a claim, one class worse.\n"
            "The claim probability is q(a) from Section 3.7.",
            fontsize=6.5, color=MUTED, va="bottom")


def panel_b(ax):
    ax.set_title("B.  Stationary distribution, by prevention", loc="left", fontsize=9, color=TEXT, pad=4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    classes = np.array([1, 2, 3])
    pi0 = np.array([1/3, 1/3, 1/3])
    pi1 = np.array([16/21, 4/21, 1/21])
    w = 0.32
    ax.bar(classes - w/2, pi0, width=w, color=VERM, label="a = 0,  q = 1/2", zorder=3)
    ax.bar(classes + w/2, pi1, width=w, color=ACCENT, label="a = 1,  q = 1/5", zorder=3)
    # exact labels
    for x, y, col, dx in (
        *[(i+1 - w/2, pi0[i], VERM, 0) for i in range(3)],
        *[(i+1 + w/2, pi1[i], ACCENT, 0) for i in range(3)],
    ):
        ax.text(x, y + 0.02, f"{y:.3f}", ha="center", va="bottom", fontsize=6.4, color=MUTED)
    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(["Class 1\n(best)", "Class 2", "Class 3\n(worst)"])
    ax.set_ylabel("Stationary probability")
    ax.set_ylim(0, 0.95)
    ax.legend(frameon=False, fontsize=7.0, loc="upper right")
    ax.text(0.55, 0.78,
            "High prevention puts most of the\nmass in the best class, so the\nfuture premium is an incentive\ninstrument for today's action.",
            fontsize=6.5, color=MUTED, transform=ax.transAxes, va="top")


def main():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.85), dpi=200)
    draw_chain(axes[0])
    panel_b(axes[1])
    fig.text(
        0.08, 0.01,
        "Illustrative transition rule, with the claim probabilities of Section 3.7.  "
        "The stationary distributions are exact for this three-class chain:  "
        "(1/3, 1/3, 1/3) if a = 0, and  (16/21, 4/21, 1/21) if a = 1.",
        fontsize=6.2, color=MUTED,
    )
    fig.subplots_adjust(wspace=0.22, left=0.04, right=0.99, top=0.88, bottom=0.22)
    save(fig, "figure06-bonus-malus")
    print("figure06", 16/21, 4/21, 1/21)

if __name__ == "__main__":
    main()
