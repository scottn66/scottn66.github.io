"""Figure 5. Deductible vs coinsurance once losses can vary."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from style import *
import numpy as np
import matplotlib.pyplot as plt

ALPHA = 0.6250771562076095
L_STAR = 96.0
D = ALPHA * L_STAR  # ≈ 60.01  same contract at the toy-example loss


def I_ded(L):
    return np.maximum(L - D, 0)


def I_co(L):
    return (1 - ALPHA) * L


def oop_ded(L):
    return np.minimum(L, D)


def oop_co(L):
    return ALPHA * L


def main():
    L = np.linspace(0, 150, 400)
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.55), dpi=200)

    ax = axes[0]
    ax.plot(L, I_ded(L), color=ACCENT, lw=1.7, label=f"Deductible  d ≈ {D:.0f}")
    ax.plot(L, I_co(L), color=VERM, lw=1.7, ls=(0, (3.2, 1.6)),
            label=f"Coinsurance  α ≈ {ALPHA:.3f}")
    ax.plot(L, L, color="#B0B0B0", lw=0.8, label="Full indemnity,  I = L")
    ax.axvline(L_STAR, color=GOLD, lw=0.9, ls="-")
    ax.plot([L_STAR], [I_ded(L_STAR)], "o", color=TEXT, ms=6, zorder=5, mew=0.5, mec=TEXT)
    ax.set_title("A.  Indemnity  I(L)", loc="left", fontsize=9, color=TEXT, pad=4)
    ax.set_xlabel("Loss  L")
    ax.set_ylabel("Indemnity")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xlim(0, 150)
    ax.set_ylim(0, 155)
    ax.legend(frameon=False, fontsize=6.7, loc="upper left")
    ax.text(L_STAR + 2, 8, "L = 96\n(toy example)", fontsize=6.3, color=GOLD, va="bottom")

    ax = axes[1]
    ax.plot(L, oop_ded(L), color=ACCENT, lw=1.7, label="Deductible")
    ax.plot(L, oop_co(L), color=VERM, lw=1.7, ls=(0, (3.2, 1.6)), label="Coinsurance")
    ax.axvline(L_STAR, color=GOLD, lw=0.9, ls="-")
    ax.plot([L_STAR], [oop_ded(L_STAR)], "o", color=TEXT, ms=6, zorder=5, mew=0.5, mec=TEXT)
    ax.set_title("B.  Insured's out-of-pocket", loc="left", fontsize=9, color=TEXT, pad=4)
    ax.set_xlabel("Loss  L")
    ax.set_ylabel("Out-of-pocket payment")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xlim(0, 150)
    ax.set_ylim(0, 100)
    ax.legend(frameon=False, fontsize=6.7, loc="upper left")
    ax.annotate("Same contract at L = 96:\nboth leave 60 with the insured",
                xy=(L_STAR, D), xytext=(108, 30),
                fontsize=6.6, color=MUTED,
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=0.7, mutation_scale=7))

    fig.text(
        0.08, 0.01,
        "Illustrative.  The two instruments are calibrated to be identical at the single loss of Section 3.7, "
        "d = αL ≈ 60 at L = 96, and then evaluated at other loss sizes.  "
        "A deductible concentrates residual risk on the first layer; coinsurance spreads it.",
        fontsize=6.2, color=MUTED,
    )
    fig.subplots_adjust(wspace=0.28, left=0.08, right=0.99, top=0.88, bottom=0.24)
    save(fig, "figure05-deductible-coinsurance")
    print("figure05", float(I_ded(L_STAR)), float(I_co(L_STAR)), float(D))

if __name__ == "__main__":
    main()
