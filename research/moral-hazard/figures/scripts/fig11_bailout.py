"""Figure 11. Bailout as a time-inconsistency game. Illustrative payoffs."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from style import *
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.lines import Line2D

# Payoffs (Bank, Social), illustrative, unique BI.
# Safe fail prob 0.2, Risky fail prob 0.6
# Success: Safe (3, 6), Risky (5, 5)
# Fail + no bailout: (0, -8)
# Fail + bailout: (2, -4)
# Under commitment (no bailout): Bank Safe 2.4 > Risky 2.0; Social 3.2
# Under discretion: ex post bailout (-4 > -8); Bank Risky 3.2 > Safe 2.8; Social -0.4


def node(ax, x, y, w, h, text, kind, fs=6.5):
    colors = {
        "nature": ("#FFFFFF", ACCENT),
        "principal": (GOLD_SOFT, GOLD),
        "agent": (ACCENT_SOFT, ACCENT),
        "hidden": (HIDDEN_SOFT, HIDDEN),
        "terminal": ("#F4F4F4", "#888888"),
        "eq": (GOLD_SOFT, GOLD),
    }
    fc, ec = colors[kind]
    lw = 1.35 if kind == "eq" else 1.05
    ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h,
                                boxstyle="round,pad=0.07,rounding_size=0.12",
                                facecolor=fc, edgecolor=ec, lw=lw, zorder=3))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=TEXT,
            zorder=4, linespacing=1.12)


def arr(ax, x1, y1, x2, y2, text=None, off=(0, 0.14), color=ACCENT, lw=0.95):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=8),
                zorder=2)
    if text:
        ax.text((x1+x2)/2+off[0], (y1+y2)/2+off[1], text,
                fontsize=6.0, color=MUTED, ha="center", va="center")


def tree(ax, title, mode):
    """mode: 'commit' or 'discretion'."""
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.15, 5.15)
    ax.axis("off")
    ax.set_title(title, loc="left", fontsize=8.8, color=TEXT, pad=2)

    # Bank chooses at left
    node(ax, 1.15, 2.6, 1.55, 0.7, "Bank\nchooses risk", "agent")
    # Safe / Risky
    safe_kind = "eq" if mode == "commit" else "agent"
    risky_kind = "eq" if mode == "discretion" else "agent"
    node(ax, 3.15, 4.05, 1.25, 0.58, "Safe\n(fail 0.2)", safe_kind)
    node(ax, 3.15, 1.45, 1.25, 0.58, "Risky\n(fail 0.6)", risky_kind)
    arr(ax, 1.95, 2.85, 2.50, 4.05, "Safe", off=(-0.05, 0.18))
    arr(ax, 1.95, 2.35, 2.50, 1.45, "Risky", off=(-0.05, -0.18))

    def branch(y, p_fail, risky=False):
        # Nature
        node(ax, 5.15, y, 1.15, 0.55, "Nature", "nature")
        arr(ax, 3.80, y, 4.55, y)
        # success terminal
        node(ax, 7.55, y + 0.85, 1.7, 0.58,
             ("Success\n(5,  5)" if risky else "Success\n(3,  6)"), "terminal")
        arr(ax, 5.75, y+0.15, 6.68, y+0.85, f"1 − {p_fail}", off=(0.0, 0.14))
        # fail node: either terminal (commit) or regulator choice (discretion)
        if mode == "commit":
            node(ax, 7.55, y - 0.85, 1.7, 0.58, "Failure, no bailout\n(0,  −8)", "terminal")
            arr(ax, 5.75, y-0.15, 6.68, y-0.85, f"{p_fail}", off=(0.0, -0.16))
        else:
            node(ax, 7.20, y - 0.80, 1.35, 0.52, "Regulator\n(ex post)", "principal")
            arr(ax, 5.75, y-0.18, 6.50, y-0.80, f"{p_fail}", off=(-0.05, -0.16))
            node(ax, 8.95, y - 0.35, 1.40, 0.50, "Bailout\n(2,  −4)", "eq")
            node(ax, 8.95, y - 1.22, 1.40, 0.50, "No bailout\n(0,  −8)", "terminal")
            arr(ax, 7.90, y-0.70, 8.25, y-0.35, "bail out", off=(0.05, 0.14))
            arr(ax, 7.90, y-0.95, 8.25, y-1.22)

    branch(4.05, "0.2", risky=False)
    branch(1.45, "0.6", risky=True)

    if mode == "commit":
        note = "Bank:  Safe 2.4  >  Risky 2.0.\nSocial payoff:  3.2."
    else:
        note = "Ex post, −4  >  −8, so the regulator bails out.\nBank:  Risky 3.2  >  Safe 2.8.\nSocial payoff:  −0.4."
    ax.text(0.15, 0.08, note, fontsize=6.4, color=MUTED, va="bottom")


def main():
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 8.15), dpi=200)
    tree(axes[0], "A.  Commitment to no bailout", "commit")
    tree(axes[1], "B.  Discretion: the regulator re-optimizes after a failure", "discretion")
    fig.text(
        0.07, 0.008,
        "Illustrative payoffs, written (Bank, Social).  Gold border: the unique backward-induction path.  Not estimated.",
        fontsize=6.3, color=MUTED,
    )
    # Avoid bbox='tight' exploding the width if a label pokes out.
    fig.subplots_adjust(hspace=0.14, left=0.04, right=0.98, top=0.97, bottom=0.05)
    with plt.rc_context({"savefig.bbox": None}):
        fig.savefig(FIGDIR / "figure11-bailout.png", dpi=200, facecolor="white")
        fig.savefig(FIGDIR / "figure11-bailout.svg", facecolor="white")
    plt.close(fig)
    print("figure11", fig)

if __name__ == "__main__":
    main()
