"""Figure 1. Three extensive-form games with a shared visual grammar."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from style import *
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Ellipse, Circle
from matplotlib.lines import Line2D
import numpy as np

# node kinds: nature, principal (decision gold), agent (hidden purple if hidden), terminal

def node(ax, x, y, w, h, text, kind, z=4):
    colors = {
        "nature": ("#FFFFFF", ACCENT),
        "principal": (GOLD_SOFT, GOLD),
        "agent": (ACCENT_SOFT, ACCENT),
        "hidden": (HIDDEN_SOFT, HIDDEN),
        "terminal": ("#F4F4F4", "#888888"),
    }
    fc, ec = colors[kind]
    ax.add_patch(FancyBboxPatch((x - w/2, y - h/2), w, h,
                                boxstyle="round,pad=0.08,rounding_size=0.15",
                                facecolor=fc, edgecolor=ec, linewidth=1.05, zorder=z))
    ax.text(x, y, text, ha="center", va="center", fontsize=6.7, color=TEXT,
            zorder=z+1, linespacing=1.15)


def arrow(ax, x1, y1, x2, y2, label=None, label_off=(0, 0), ls="-", color=ACCENT):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=0.95,
                        linestyle=ls, mutation_scale=8, shrinkA=0, shrinkB=0),
        zorder=2,
    )
    if label:
        mx, my = (x1 + x2) / 2 + label_off[0], (y1 + y2) / 2 + label_off[1]
        ax.text(mx, my, label, fontsize=6.2, color=MUTED, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.08", fc="white", ec="none", alpha=0.85),
                zorder=5)


def dashed_box(ax, x, y, w, h, label):
    ax.add_patch(Rectangle((x, y), w, h, fill=False, ls=(0, (3, 2)),
                           ec=HIDDEN, lw=1.15, zorder=3))
    ax.text(x + w/2, y + h + 0.12, label, ha="center", va="bottom",
            fontsize=6.3, color=HIDDEN, style="italic")


def info_curve(ax, pts, label, label_pos):
    xs, ys = zip(*pts)
    # draw a slightly bowed dashed line through the points
    ax.plot(xs, ys, ls=(0, (3.2, 1.8)), color=HIDDEN, lw=1.2, zorder=3, solid_capstyle="round")
    # end caps
    for x, y in pts:
        ax.plot([x], [y], "o", ms=3.2, color=HIDDEN, zorder=3)
    ax.text(*label_pos, label, fontsize=6.3, color=HIDDEN, style="italic",
            ha="center", va="center")


def panel_frame(ax, title):
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.15, 4.35)
    ax.axis("off")
    ax.set_title(title, loc="left", fontsize=9, color=TEXT, pad=2, fontweight="medium")


def draw_mh(ax):
    panel_frame(ax, "A.  Hidden action  (moral hazard)")
    # left to right: Insurer offer | Agent accept | hidden a | Nature | terminals
    # y=2.2 main path, reject below
    node(ax, 0.95, 2.35, 1.55, 0.72, "Insurer\noffers contract", "principal")
    node(ax, 3.15, 2.35, 1.45, 0.72, "Insured\naccepts?", "agent")
    arrow(ax, 1.72, 2.35, 2.42, 2.35, "offer")

    # reject branch
    node(ax, 3.15, 0.55, 1.55, 0.62, "Reservation\n(uninsured)", "terminal")
    arrow(ax, 3.15, 1.97, 3.15, 0.90, "reject", label_off=(0.42, 0))

    # accept to hidden action (two nodes side by side in dashed box)
    node(ax, 5.55, 3.05, 1.20, 0.62, "a = 1\nprevention", "hidden")
    node(ax, 5.55, 1.65, 1.20, 0.62, "a = 0\nprevention", "hidden")
    dashed_box(ax, 4.80, 1.22, 1.55, 2.20, "a not observed")
    arrow(ax, 3.88, 2.50, 4.80, 3.05, "accept", label_off=(-0.05, 0.22))
    arrow(ax, 3.88, 2.20, 4.80, 1.65)

    # nature and outcomes: four leaves is tight; two nature nodes then L / no L
    node(ax, 7.55, 3.05, 1.05, 0.55, "Nature\nloss?", "nature")
    node(ax, 7.55, 1.65, 1.05, 0.55, "Nature\nloss?", "nature")
    arrow(ax, 6.17, 3.05, 7.00, 3.05)
    arrow(ax, 6.17, 1.65, 7.00, 1.65)

    node(ax, 9.25, 3.45, 1.15, 0.50, "Loss  ·  w, I", "terminal")
    node(ax, 9.25, 2.65, 1.15, 0.50, "No loss  ·  w", "terminal")
    node(ax, 9.25, 2.05, 1.15, 0.50, "Loss  ·  w, I", "terminal")
    node(ax, 9.25, 1.25, 1.15, 0.50, "No loss  ·  w", "terminal")
    arrow(ax, 8.10, 3.22, 8.66, 3.45, "q(1)", label_off=(0.0, 0.16))
    arrow(ax, 8.10, 2.88, 8.66, 2.65, "1−q(1)", label_off=(0.05, -0.16))
    arrow(ax, 8.10, 1.82, 8.66, 2.05, "q(0)", label_off=(0.0, 0.16))
    arrow(ax, 8.10, 1.48, 8.66, 1.25, "1−q(0)", label_off=(0.05, -0.16))

    ax.text(5.00, 0.18,
            "The insurer has already moved. The dashed box is the hidden action, not a later information set of the insurer.",
            fontsize=6.2, color=MUTED, ha="left", va="center")


def draw_screening(ax):
    panel_frame(ax, "B.  Screening  (uninformed party offers a menu)")
    node(ax, 0.95, 2.35, 1.35, 0.72, "Nature\ndraws type", "nature")
    node(ax, 3.20, 3.20, 1.20, 0.58, "θ = H\nhigh risk", "hidden")
    node(ax, 3.20, 1.50, 1.20, 0.58, "θ = L\nlow risk", "hidden")
    arrow(ax, 1.65, 2.50, 2.58, 3.20)
    arrow(ax, 1.65, 2.20, 2.58, 1.50)

    # principal offers, in an information set
    node(ax, 5.70, 3.20, 1.45, 0.62, "Insurer\noffers menu", "principal")
    node(ax, 5.70, 1.50, 1.45, 0.62, "Insurer\noffers menu", "principal")
    arrow(ax, 3.82, 3.20, 4.95, 3.20)
    arrow(ax, 3.82, 1.50, 4.95, 1.50)
    info_curve(ax, [(5.70, 2.86), (5.70, 1.84)],
               "information set:\ninsurer does not see θ", (7.55, 2.35))
    # a horizontal brace to the right of the two offer nodes
    ax.annotate("", xy=(6.50, 3.20), xytext=(6.50, 1.50),
                arrowprops=dict(arrowstyle="-", color=HIDDEN, lw=0, ls=""), zorder=1)
    # curved dashed connector on the right
    from matplotlib.patches import FancyBboxPatch, PathPatch
    from matplotlib.path import Path as MPath
    # already have vertical dashed line from info_curve

    node(ax, 8.85, 3.55, 1.55, 0.50, "H takes C_H", "agent")
    node(ax, 8.85, 2.85, 1.55, 0.50, "H takes C_L", "agent")
    node(ax, 8.85, 1.85, 1.55, 0.50, "L takes C_H", "agent")
    node(ax, 8.85, 1.15, 1.55, 0.50, "L takes C_L", "agent")
    arrow(ax, 6.45, 3.38, 8.06, 3.55)
    arrow(ax, 6.45, 3.02, 8.06, 2.85)
    arrow(ax, 6.45, 1.68, 8.06, 1.85)
    arrow(ax, 6.45, 1.32, 8.06, 1.15)

    ax.text(5.00, 0.18,
            "A separating menu is built so that each type's preferred item reveals the type. A pooling menu may be cream-skimmed.",
            fontsize=6.2, color=MUTED, ha="left", va="center")


def draw_signaling(ax):
    panel_frame(ax, "C.  Signaling  (informed party moves first)")
    node(ax, 0.95, 2.35, 1.35, 0.72, "Nature\ndraws type", "nature")
    node(ax, 3.15, 3.20, 1.20, 0.58, "θ = H", "hidden")
    node(ax, 3.15, 1.50, 1.20, 0.58, "θ = L", "hidden")
    arrow(ax, 1.65, 2.50, 2.53, 3.20)
    arrow(ax, 1.65, 2.20, 2.53, 1.50)

    node(ax, 5.45, 3.55, 1.25, 0.52, "Sends s_H", "agent")
    node(ax, 5.45, 2.85, 1.25, 0.52, "Sends s_L", "agent")
    node(ax, 5.45, 1.85, 1.25, 0.52, "Sends s_H", "agent")
    node(ax, 5.45, 1.15, 1.25, 0.52, "Sends s_L", "agent")
    arrow(ax, 3.77, 3.38, 4.80, 3.55, "signal", label_off=(0.0, 0.16))
    arrow(ax, 3.77, 3.02, 4.80, 2.85)
    arrow(ax, 3.77, 1.68, 4.80, 1.85)
    arrow(ax, 3.77, 1.32, 4.80, 1.15)

    # uninformed responses: if both types can send the same s, those two response nodes are in one info set
    node(ax, 8.15, 3.55, 1.70, 0.52, "Insurer replies\nto s_H", "principal")
    node(ax, 8.15, 2.85, 1.70, 0.52, "Insurer replies\nto s_L", "principal")
    node(ax, 8.15, 1.85, 1.70, 0.52, "Insurer replies\nto s_H", "principal")
    node(ax, 8.15, 1.15, 1.70, 0.52, "Insurer replies\nto s_L", "principal")
    arrow(ax, 6.10, 3.55, 7.28, 3.55)
    arrow(ax, 6.10, 2.85, 7.28, 2.85)
    arrow(ax, 6.10, 1.85, 7.28, 1.85)
    arrow(ax, 6.10, 1.15, 7.28, 1.15)

    # information set linking the two "reply to s_H" nodes (pooling on s_H)
    # curve to the right
    ys_h = [3.55, 1.85]
    ax.plot([9.15, 9.45, 9.45, 9.15], [3.55, 3.55, 1.85, 1.85],
            ls=(0, (3.2, 1.8)), color=HIDDEN, lw=1.15, zorder=3)
    ax.text(9.62, 2.70, "info. set\nafter s_H\n(if both\ncan send it)",
            fontsize=6.0, color=HIDDEN, style="italic", ha="left", va="center")

    ax.text(0.20, 0.18,
            "In a separating equilibrium the two types send different signals, and those information sets collapse to singletons.",
            fontsize=6.2, color=MUTED, ha="left", va="center")


def main():
    fig, axes = plt.subplots(3, 1, figsize=(7.2, 9.15), dpi=200)
    fig.subplots_adjust(hspace=0.22, left=0.04, right=0.98, top=0.99, bottom=0.015)
    draw_mh(axes[0])
    draw_screening(axes[1])
    draw_signaling(axes[2])
    # shared legend
    handles = [
        mpl.patches.Patch(facecolor=GOLD_SOFT, edgecolor=GOLD, label="Uninformed party's decision"),
        mpl.patches.Patch(facecolor=ACCENT_SOFT, edgecolor=ACCENT, label="Informed party's decision"),
        mpl.patches.Patch(facecolor=HIDDEN_SOFT, edgecolor=HIDDEN, label="Hidden type or hidden action"),
        mpl.patches.Patch(facecolor="#FFFFFF", edgecolor=ACCENT, label="Nature"),
        Line2D([0], [0], color=HIDDEN, ls=(0, (3.2, 1.8)), lw=1.2, label="Information set, or unobserved action"),
    ]
    # place legend at very bottom of figure
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False,
               bbox_to_anchor=(0.5, -0.01), fontsize=7.2)
    fig.subplots_adjust(bottom=0.045)
    save(fig, "figure01-three-games")
    print("figure01")

import matplotlib as mpl
if __name__ == "__main__":
    main()
