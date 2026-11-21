"""Figure 8. An acyclic graph of the insurance relationship."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from style import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, PathPatch, Polygon

plt.rcParams["font.family"] = "DejaVu Sans"
fig = plt.figure(figsize=(7.2, 4.35), dpi=200, facecolor="white")
ax = fig.add_axes([0.02, 0.12, 0.96, 0.86])
ax.set_xlim(0, 100)
ax.set_ylim(0, 70)
ax.axis("off")


def box(x, y, w, h, label, kind):
    colors = {
        "hidden": (HIDDEN_SOFT, HIDDEN),
        "obs": (ACCENT_SOFT, ACCENT),
        "decision": (GOLD_SOFT, GOLD),
        "event": ("#FFFFFF", ACCENT),
    }
    fc, ec = colors[kind]
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.25,rounding_size=0.6",
        facecolor=fc, edgecolor=ec, linewidth=1.15, zorder=3,
    ))
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
            fontsize=7.6, color=TEXT, zorder=4, linespacing=1.2)


nodes = {
    "spre":  (2, 52, 20, 10, "s_pre\ntest, underwriting", "obs"),
    "theta": (28, 52, 18, 10, "θ  type\n(hidden)", "hidden"),
    "a":     (54, 52, 18, 10, "a  prevention\n(hidden)", "hidden"),
    "spost": (78, 52, 20, 10, "s_post\ntelematics, audit", "obs"),
    "cov":   (10, 30, 26, 10, "coverage\npremium, contract", "decision"),
    "L":     (46, 30, 16, 10, "L  loss", "event"),
    "m":     (70, 30, 18, 10, "m  utilization\n(hidden)", "hidden"),
    "k":     (46, 13.5, 16, 9, "k  claim", "event"),
    "I":     (70, 13.5, 18, 9, "I  indemnity", "decision"),
}
for v in nodes.values():
    box(*v)


def center(key):
    x, y, w, h, lab, kind = nodes[key]
    return x, y, w, h, x + w / 2, y + h / 2


def edge(a, b, rad=0.0):
    xa, ya, wa, ha, axc, ayc = center(a)
    xb, yb, wb, hb, bxc, byc = center(b)
    dx, dy = bxc - axc, byc - ayc
    if abs(dx) >= abs(dy) * 0.85:
        start = (xa + wa, ayc) if dx > 0 else (xa, ayc)
        end = (xb, byc) if dx > 0 else (xb + wb, byc)
    else:
        start = (axc, ya) if dy < 0 else (axc, ya + ha)
        end = (bxc, yb + hb) if dy < 0 else (bxc, yb)
    ax.add_patch(FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=10, linewidth=1.0,
        color=ACCENT, connectionstyle=f"arc3,rad={rad}",
        shrinkA=1, shrinkB=1, zorder=2,
    ))


edge("theta", "spre", 0)
edge("spre", "cov", 0.04)
edge("theta", "cov", 0.10)
edge("theta", "L", -0.06)
edge("theta", "spost", 0.07)
edge("cov", "a", -0.10)
edge("cov", "m", 0.16)
edge("a", "L", 0)
edge("a", "spost", 0)
edge("L", "k", 0)
edge("m", "k", -0.08)
edge("k", "I", 0)
edge("spost", "I", 0)
# Route coverage -> indemnity under the claim node, to the right of the legend.
xa, ya, wa, ha, axc, ayc = center("cov")
xb, yb, wb, hb, bxc, byc = center("I")
# Leave the lower-right of coverage, drop under k, then rise into the bottom of I.
x0, y0 = xa + wa - 2.0, ya
x1, y1 = 40.0, 7.6
x2, y2 = bxc, 7.6
x3, y3 = bxc, yb
verts = [(x0, y0), (x0, y1), (x2, y2), (x3, y3)]
codes = [MPath.MOVETO, MPath.LINETO, MPath.LINETO, MPath.LINETO]
ax.add_patch(PathPatch(
    MPath(verts, codes), facecolor="none", edgecolor=ACCENT,
    linewidth=1.0, capstyle="round", joinstyle="round", zorder=2,
))
# Arrow head at the bottom of I.
head = np.array([[bxc, yb + 0.15], [bxc - 0.85, yb - 1.7], [bxc + 0.85, yb - 1.7]])
ax.add_patch(Polygon(head, closed=True, facecolor=ACCENT, edgecolor=ACCENT, linewidth=0, zorder=3))


# Legend stacked in the lower-left empty region so labels do not collide.
legend = [
    ("hidden", "Typically hidden (type, action, utilization)"),
    ("obs", "Observed signal"),
    ("decision", "Contract decision (premium, indemnity rule)"),
    ("event", "Realized event (loss, claim)"),
]
colors = {
    "hidden": (HIDDEN_SOFT, HIDDEN),
    "obs": (ACCENT_SOFT, ACCENT),
    "decision": (GOLD_SOFT, GOLD),
    "event": ("#FFFFFF", ACCENT),
}
ly = 18.0
for kind, name in legend:
    fc, ec = colors[kind]
    ax.add_patch(FancyBboxPatch(
        (2.0, ly - 1.0), 3.0, 2.2, boxstyle="round,pad=0.15,rounding_size=0.3",
        facecolor=fc, edgecolor=ec, linewidth=1.0, zorder=3,
    ))
    ax.text(6.0, ly + 0.15, name, va="center", fontsize=6.6, color=TEXT)
    ly -= 3.4
ax.text(
    2, 1.0,
    "Solid arrows are claimed causal or informational dependence.\nThe graph is a schematic, not an estimated model.",
    fontsize=6.3, color=MUTED,
)

if __name__ == "__main__":
    save(fig, "figure08-insurance-dag")
    print("figure08")
