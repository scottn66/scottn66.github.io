"""Figure 10. Basis risk scatter and an oracle game. Illustrative."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from style import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch

# DGP, fixed seed, stated in the caption.
# Index Y ~ LogNormal, log Y ~ N(mu, sigma)
# Actual loss L = Y * exp(eta), eta ~ N(0, s^2), independent.
# Parametric: pay I0 if Y >= threshold, else 0.
RNG = np.random.default_rng(20261118)
MU, SIGMA, S_ETA = np.log(40.0), 0.55, 0.45
THRESH, I0 = 50.0, 80.0
N = 120
Y = RNG.lognormal(MU, SIGMA, N)
L = Y * np.exp(RNG.normal(0.0, S_ETA, N))
PAY = np.where(Y >= THRESH, I0, 0.0)


def panel_a(ax):
    ax.set_title("A.  Basis risk under a parametric trigger", loc="left", fontsize=9, color=TEXT, pad=4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    # regions
    xmax, ymax = 160, 160
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, ymax)
    # 45-degree perfect indemnity
    ax.plot([0, 150], [0, 150], color="#B0B0B0", lw=0.8, zorder=1, label="Perfect indemnity,  I = L")
    ax.axhline(I0, color=GOLD, lw=0.8, ls=(0, (3, 1.6)), zorder=1)
    ax.text(8, I0 + 4, f"parametric payout  I = {int(I0)}", fontsize=6.3, color=GOLD, va="bottom")
    # points
    paid = PAY > 0
    ax.scatter(L[~paid], PAY[~paid], s=18, color=VERM, marker="o", lw=0.4, edgecolor=TEXT,
               alpha=0.85, zorder=3, label="Trigger not met")
    ax.scatter(L[paid], PAY[paid], s=22, color=ACCENT, marker="D", lw=0.4, edgecolor=TEXT,
               alpha=0.85, zorder=3, label="Trigger met")
    # call out the two basis-risk regions
    ax.text(110, 12, "Loss, little or no payout\n(uninsured residual)", fontsize=6.4,
            color=VERM, ha="center")
    ax.text(25, 115, "Payout with little loss", fontsize=6.4, color=ACCENT, ha="center")
    ax.set_xlabel("Actual loss  L")
    ax.set_ylabel("Contract payout")
    ax.legend(frameon=False, fontsize=6.5, loc="upper left")


def node(ax, x, y, w, h, text, kind):
    colors = {
        "nature": ("#FFFFFF", ACCENT),
        "principal": (GOLD_SOFT, GOLD),
        "hidden": (HIDDEN_SOFT, HIDDEN),
        "terminal": ("#F4F4F4", "#888888"),
    }
    fc, ec = colors[kind]
    ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h,
                                boxstyle="round,pad=0.08,rounding_size=0.12",
                                facecolor=fc, edgecolor=ec, lw=1.05, zorder=3))
    ax.text(x, y, text, ha="center", va="center", fontsize=6.5, color=TEXT, zorder=4, linespacing=1.15)


def arr(ax, x1, y1, x2, y2, text=None, off=(0, 0.12)):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=0.95, mutation_scale=8),
                zorder=2)
    if text:
        ax.text((x1+x2)/2+off[0], (y1+y2)/2+off[1], text,
                fontsize=6.1, color=MUTED, ha="center", va="center")


def panel_b(ax):
    ax.set_xlim(0, 10)
    ax.set_ylim(0.0, 5.0)
    ax.axis("off")
    ax.set_title("B.  The oracle's hidden action  (illustrative payoffs)", loc="left",
                 fontsize=9, color=TEXT, pad=2)
    # Tree for the tempting branch: true index is "no pay"
    # Nature (already in this branch) -> Oracle reports Pay or No pay
    # If No pay (honest): payoff (oracle keeps stake 40)
    # If Pay (lie): Nature detects with p=1/2
    #   detected: stake slashed, 0
    #   not detected: stake 40 + bribe 25 = 65
    # IC: honest 40 >= 0.5*65 + 0.5*0 = 32.5, so honest.
    # If S were 20: 20 < 0.5*(20+25)=22.5, lie.
    node(ax, 1.15, 3.15, 1.7, 0.85, "True index:\nno payout due", "nature")
    node(ax, 4.15, 3.15, 1.8, 0.85, "Oracle\nreports?", "hidden")
    arr(ax, 2.02, 3.15, 3.23, 3.15)
    node(ax, 6.85, 4.25, 2.15, 0.7, "Reports honestly\nkeeps stake  40", "terminal")
    node(ax, 6.85, 2.05, 2.05, 0.7, "Misreports\n(pays a false trigger)", "hidden")
    arr(ax, 5.05, 3.40, 5.75, 4.25, "honest", off=(-0.05, 0.18))
    arr(ax, 5.05, 2.90, 5.75, 2.05, "lie", off=(-0.15, -0.18))
    node(ax, 9.15, 2.55, 1.55, 0.65, "Detected\n(p = 1/2)\nslashed:  0", "terminal")
    node(ax, 9.15, 1.45, 1.55, 0.65, "Not detected\nstake + bribe\n65", "terminal")
    arr(ax, 7.90, 2.15, 8.35, 2.55)
    arr(ax, 7.90, 1.85, 8.35, 1.45)

    ax.text(0.2, 0.25,
            "Illustrative: stake S = 40, bribe b = 25, detection probability 1/2.\n"
            "Honest payoff 40  >  expected payoff from lying 32.5, so honesty is incentive compatible.\n"
            "If the stake were 20, the inequality would reverse (20 < 22.5) and the oracle would lie.\n"
            "The hidden action has moved to the reporter of the index.",
            fontsize=6.3, color=MUTED, va="bottom")


def main():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 4.15), dpi=200)
    panel_a(axes[0])
    panel_b(axes[1])
    fig.text(
        0.06, 0.008,
        f"Panel A is illustrative, seed 20261118, n = {N}.  "
        "log Y ~ N(log 40, 0.55²),  L = Y e^η with η ~ N(0, 0.45²),  "
        f"and the contract pays {int(I0)} if Y ≥ {int(THRESH)}, otherwise 0.  "
        "Points off the 45-degree line are basis risk, not an estimated market.",
        fontsize=6.1, color=MUTED,
    )
    fig.subplots_adjust(wspace=0.18, left=0.07, right=0.99, top=0.90, bottom=0.22)
    save(fig, "figure10-parametric-oracle")
    n_loss_nopay = int(((PAY == 0) & (L > 10)).sum())
    n_pay_small = int(((PAY > 0) & (L < 20)).sum())
    print("figure10", n_loss_nopay, n_pay_small, PAY.mean(), L.mean())

if __name__ == "__main__":
    main()
