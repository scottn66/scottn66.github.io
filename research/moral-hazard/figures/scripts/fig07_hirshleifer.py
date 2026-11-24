"""Figure 7. Value of information for an individual vs in a risk-sharing market."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from style import *
import numpy as np
import matplotlib.pyplot as plt

# Individual (illustrative, same u and W):
# Can spend 40 to cancel the loss if it would have occurred.
# p = 1/2, W=121, L=96, u=sqrt.
# Never mitigate: EU = 8
# Always mitigate: wealth 81, EU = 9   <-- chosen without information
# Perfect info: mitigate only if the loss is coming, EU = 0.5*11 + 0.5*9 = 10
# EVPI = +1
#
# Market (same u, W, L, p=1/2, no mitigation, fair risk-neutral insurer):
# Fair full insurance, before revelation: wealth 73, EU = sqrt(73) ≈ 8.544
# Public revelation of the loss state before trade: no mutually beneficial trade, EU = 8
# Social value of public information ≈ -0.544

EU_NEVER = 8.0
EU_ALWAYS = 9.0
EU_INFO = 10.0
EVPI = 1.0
EU_MKT_INS = float(np.sqrt(73))
EU_MKT_REV = 8.0
SV = EU_MKT_REV - EU_MKT_INS


def bars(ax, labels, values, colors, title, ylabel, highlight_idx, callout):
    ax.set_title(title, loc="left", fontsize=9, color=TEXT, pad=4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    xs = np.arange(len(values))
    ax.bar(xs, values, color=colors, width=0.62, zorder=3, edgecolor=TEXT, lw=0.4)
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, fontsize=7.0)
    ax.set_ylabel(ylabel)
    ax.set_ylim(7.3, 10.6)
    ax.axhline(values[0], color=RULE, lw=0.6, zorder=1)
    for x, y in zip(xs, values):
        ax.text(x, y + 0.08, f"{y:.3f}", ha="center", va="bottom", fontsize=7.4, color=TEXT)
    ax.annotate(
        "", xy=(highlight_idx, values[highlight_idx]), xytext=(0, values[0]),
        arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=0.8, mutation_scale=8,
                        connectionstyle="arc3,rad=0.25"),
    )
    ax.text(0.98, 0.18, callout, transform=ax.transAxes, fontsize=7.2,
            color=TEXT, ha="right", va="bottom",
            bbox=dict(boxstyle="round,pad=0.25", fc="#F7F7F7", ec=RULE, lw=0.6))


def main():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.85), dpi=200, sharey=True)
    bars(
        axes[0],
        ["No information\n(always mitigate)", "Perfect information\n(mitigate only if needed)"],
        [EU_ALWAYS, EU_INFO],
        [ACCENT_SOFT, ACCENT],
        "A.  A single decision maker",
        "Expected utility",
        1,
        "EVPI  =  +1.000",
    )
    bars(
        axes[1],
        ["Fair insurance\nbefore revelation", "Public revelation\nbefore trade"],
        [EU_MKT_INS, EU_MKT_REV],
        [ACCENT, VERM],
        "B.  A risk-sharing market  (Hirshleifer)",
        "Expected utility",
        1,
        "Social value  ≈  −0.544",
    )
    fig.text(
        0.08, 0.01,
        "Illustrative, with u(w) = √w and W = 121.  "
        "Panel A: a loss of 96 occurs with probability 1/2, and a mitigation outlay of 40 cancels it.  "
        "Without information the agent always mitigates (EU = 9 rather than 8).  "
        "Panel B: the same preferences and loss, no mitigation, and a fair risk-neutral insurer.  "
        "The two panels are different decision problems; what is to be compared is the sign of the value of information.",
        fontsize=6.15, color=MUTED,
    )
    fig.subplots_adjust(wspace=0.18, left=0.08, right=0.99, top=0.88, bottom=0.28)
    save(fig, "figure07-hirshleifer")
    print("figure07", EU_MKT_INS, SV)

if __name__ == "__main__":
    main()
