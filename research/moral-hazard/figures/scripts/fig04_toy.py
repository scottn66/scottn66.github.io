"""Figure 4. Toy example: first best, second best, agency cost."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from style import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

W, L = 121.0, 96.0
u = np.sqrt
q1, q0 = 0.2, 0.5
c1 = 1.0
ALPHA = 0.6250771562076095
PI_SB = 0.2 * (1 - ALPHA) * L
WN_SB, WL_SB = W - PI_SB, W - PI_SB - ALPHA * L
W_FB = W - q1 * L  # 101.8
EU_FB = u(W_FB) - c1
EU_UN = 0.8 * u(W) + 0.2 * u(W - L) - c1  # 8.8  (best uninsured is a=1)
# EU as function of alpha under zero-profit premium for a=1


def wealth(alpha):
    pi = q1 * (1 - alpha) * L
    return W - pi, W - pi - alpha * L


def eu(alpha, a, q):
    wn, wl = wealth(alpha)
    cost = c1 if a == 1 else 0.0
    return (1 - q) * u(wn) + q * u(wl) - cost


def fair_wl(wn, q):
    return (W - q * L - (1 - q) * wn) / q


def panel_a(ax):
    ax.set_xlim(50, 148)
    ax.set_ylim(12, 128)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("Wealth if no loss")
    ax.set_ylabel("Wealth if loss")
    ax.set_title("A.  State-contingent wealth", loc="left", fontsize=9, color=TEXT, pad=4)
    ax.plot([50, 126], [50, 126], color="#B0B0B0", lw=0.75, zorder=1)
    ax.text(116, 118, "full insurance", fontsize=6.3, color=MUTED, rotation=45)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # high-prevention fair odds, from endowment to FB
    wn = np.linspace(W_FB, W, 200)
    ax.plot(wn, fair_wl(wn, q1), color=ACCENT, lw=1.45, zorder=2, label="High-prevention fair odds")
    # low-prevention fair odds (where full insurance at a=0 would sit)
    wn0 = np.linspace(W - q0 * L, W, 200)
    ax.plot(wn0, fair_wl(wn0, q0), color=VERM, lw=1.15, ls=(0, (3.2, 1.6)),
            zorder=2, label="Low-prevention fair odds")

    pts = [
        (W, W - L, TEXT, "o", "Uninsured  (121, 25)", 3, -9),
        (W_FB, W_FB, TEAL, "s", "First best  (101.80, 101.80)", 3.2, 3.5),
        (WN_SB, WL_SB, ACCENT, "D", "Second best  (113.80, 53.79)", 3.2, -10),
        (W - q0 * L, W - q0 * L, VERM, "x", "Full ins. at low-prevention price", 3.2, -9),
    ]
    # the last point is (73,73); might crowd H-like. Place carefully.
    ax.plot([W], [W-L], "o", color=TEXT, ms=7, zorder=5, mew=0.5, mec=TEXT)
    ax.annotate("Uninsured\n(121, 25)", (W, W-L), xytext=(W+6, 18),
                fontsize=6.7, ha="left", va="center")
    ax.plot([W_FB], [W_FB], "s", color=TEAL, ms=7.5, zorder=5, mew=0.5, mec=TEXT)
    ax.annotate("First best\n(101.80, 101.80)", (W_FB, W_FB), xytext=(W_FB+4, W_FB+8),
                fontsize=6.7, ha="left", va="bottom")
    ax.plot([WN_SB], [WL_SB], "D", color=ACCENT, ms=7.2, zorder=5, mew=0.5, mec=TEXT)
    ax.annotate("Second best\n(113.80, 53.79)", (WN_SB, WL_SB), xytext=(WN_SB+3, WL_SB-2),
                fontsize=6.7, ha="left", va="top")
    ax.plot([73], [73], "x", color=VERM, ms=7, zorder=5, mew=1.2)
    ax.annotate("Full insurance at the\nlow-prevention price", (73, 73),
                xytext=(70, 58), fontsize=6.5, ha="right", va="top", color=MUTED)

    ax.annotate("", xy=(WN_SB, WL_SB), xytext=(W_FB, W_FB),
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=0.8, mutation_scale=8,
                                connectionstyle="arc3,rad=-0.15"))


def panel_b(ax):
    ax.set_title("B.  Expected utility against coinsurance", loc="left", fontsize=9, color=TEXT, pad=4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    alphas = np.linspace(0, 1, 250)
    eu1 = [eu(a, 1, q1) for a in alphas]
    eu0 = [eu(a, 0, q0) for a in alphas]
    ax.plot(alphas, eu1, color=ACCENT, lw=1.6, label="Expected utility if a = 1")
    ax.plot(alphas, eu0, color=VERM, lw=1.5, ls=(0, (3.2, 1.6)), label="Expected utility if a = 0")
    # IC threshold
    ax.axvline(ALPHA, color=GOLD, lw=1.1, ls="-")
    ax.axhline(EU_FB, color=TEAL, lw=0.9, ls=(0, (1.5, 1.2)))
    ax.axhline(EU_UN, color=TEXT, lw=0.7, ls=(0, (0.8, 1.2)))
    eu_sb = eu(ALPHA, 1, q1)
    ax.plot([ALPHA], [eu_sb], "D", color=ACCENT, ms=7, zorder=5, mew=0.5, mec=TEXT)
    ax.plot([0], [EU_FB], "s", color=TEAL, ms=6.5, zorder=5, mew=0.5, mec=TEXT)

    # mark agency cost as a vertical bracket at the right, or a double arrow near alpha*
    ax.annotate(
        "", xy=(0.72, EU_FB), xytext=(0.72, eu_sb),
        arrowprops=dict(arrowstyle="<->", color=TEAL, lw=1.05, mutation_scale=7),
    )
    ax.text(0.735, (EU_FB + eu_sb) / 2, "agency\ncost\n≈ 0.088", fontsize=6.6,
            color=TEAL, va="center", ha="left")

    ax.set_xlabel("Coinsurance rate  α  (insured's share of the loss)")
    ax.set_ylabel("Expected utility")
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(7.6, 10.35)
    ax.set_xticks([0, 0.25, ALPHA, 0.8, 1.0])
    ax.set_xticklabels(["0\n(full ins.)", "0.25", "α* ≈ 0.625", "0.80", "1\n(uninsured)"])
    ax.legend(frameon=False, loc="upper right", fontsize=7.0)
    ax.text(ALPHA, 7.68, "IC binds", fontsize=6.4, color=GOLD, ha="center", va="bottom")


def main():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 4.35), dpi=200)
    panel_a(axes[0])
    panel_b(axes[1])
    handles = [
        Line2D([0], [0], color=ACCENT, lw=1.45, label="High-prevention fair odds  (q = 1/5)"),
        Line2D([0], [0], color=VERM, lw=1.15, ls=(0, (3.2, 1.6)), label="Low-prevention fair odds  (q = 1/2)"),
        Line2D([0], [0], color="#B0B0B0", lw=0.8, label="Full-insurance line"),
    ]
    # panel A needs its own legend inside; panel B has one
    axes[0].legend(handles=handles, frameon=False, loc="upper left", fontsize=6.2, bbox_to_anchor=(0.0, 0.62))
    fig.text(
        0.08, 0.01,
        "Illustrative, from Section 3.7.  W = 121,  L = 96,  u(w) = √w,  c(0) = 0,  c(1) = 1,  "
        "and the premium is the zero-profit indemnity at a = 1.  "
        "At α*, the agent is willing to take high prevention; smaller α unravels to a = 0.",
        fontsize=6.2, color=MUTED,
    )
    fig.subplots_adjust(wspace=0.28, left=0.08, right=0.99, top=0.90, bottom=0.22)
    save(fig, "figure04-toy-example")
    print("figure04", WN_SB, WL_SB, eu(ALPHA, 1, q1), EU_FB)

if __name__ == "__main__":
    main()
