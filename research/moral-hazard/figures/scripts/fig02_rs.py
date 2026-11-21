"""Figure 2. Rothschild-Stiglitz in state-contingent wealth. Illustrative parameters."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from style import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

W, L = 121.0, 96.0
pL, pH = 0.2, 0.5
u = np.sqrt
WN_SEP, WL_SEP = 117.48807506696859, 39.047699732125636
WH_FI = W - pH * L          # 73
WL_FI = W - pL * L          # 101.8
E = (W, W - L)              # (121, 25)
LAM_A = 0.35                # mid pooling line, visually between the two fair-odds lines
LAM_B = 0.10                # scarce high-risk types; breaks the separating menu


def fair_wl(wn, p):
    return (W - p * L - (1 - p) * wn) / p


def indiff_wl(wn, p, u_bar):
    num = (u_bar - (1 - p) * np.sqrt(np.clip(wn, 1e-9, None))) / p
    out = np.full_like(wn, np.nan, dtype=float)
    ok = num > 0
    out[ok] = num[ok] ** 2
    return out


def setup_axes(ax, title):
    ax.set_xlim(66, 128)
    ax.set_ylim(8, 132)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("Wealth if no loss")
    ax.set_ylabel("Wealth if loss")
    ax.set_title(title, loc="left", fontsize=9, color=TEXT, pad=4)
    ax.plot([68, 126], [68, 126], color="#B0B0B0", lw=0.75, zorder=1)
    ax.text(114.5, 116.5, "full insurance", fontsize=6.3, color=MUTED,
            rotation=45, va="bottom", ha="left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(False)


def plot_fair(ax, p, color, ls, lw=1.4):
    # draw only the economically relevant segment: from near full insurance to endowment
    wn_fi = W - p * L
    wn = np.linspace(wn_fi, W, 200)
    ax.plot(wn, fair_wl(wn, p), color=color, ls=ls, lw=lw, zorder=2)


def plot_indiff(ax, p, u_bar, color, wn_min=68, wn_max=126):
    wn = np.linspace(wn_min, wn_max, 500)
    wl = indiff_wl(wn, p, u_bar)
    # clip to axes
    mask = (wl >= 8) & (wl <= 132)
    ax.plot(wn[mask], wl[mask], color="#333333", ls=(0, (1.4, 1.2)), lw=1.0, zorder=3)


def mark(ax, x, y, color, marker, text, textoff, ha="left", va="bottom"):
    ax.plot([x], [y], marker=marker, color=color, ms=7.2, zorder=6,
            mew=0.55, mec=TEXT)
    ax.annotate(text, (x, y), xytext=(x + textoff[0], y + textoff[1]),
                fontsize=7.0, color=TEXT, ha=ha, va=va)


def panel_a(ax):
    setup_axes(ax, "A.  A pooling contract can be cream-skimmed")
    p_avg = LAM_A * pH + (1 - LAM_A) * pL  # 0.35
    plot_fair(ax, pH, TYPE_H, "-")
    plot_fair(ax, pL, TYPE_L, "-")
    plot_fair(ax, p_avg, GOLD, (0, (3.6, 1.5)), lw=1.6)

    P = W - p_avg * L  # 87.4
    C = (112.0, fair_wl(112.0, pL))  # (112, 61.0)
    assert 0.5 * u(C[0]) + 0.5 * u(C[1]) < u(P)
    assert 0.8 * u(C[0]) + 0.2 * u(C[1]) > u(P)

    plot_indiff(ax, pH, u(P), TYPE_H, wn_min=70, wn_max=118)
    plot_indiff(ax, pL, u(P), TYPE_L, wn_min=70, wn_max=124)

    mark(ax, E[0], E[1], TEXT, "o", "E  uninsured", (2.0, -8.0))
    mark(ax, WH_FI, WH_FI, TYPE_H, "s", "H*", (2.2, -8.0))
    mark(ax, WL_FI, WL_FI, TYPE_L, "s", "L*  full insurance\nfor low risk", (2.0, 2.2))
    mark(ax, P, P, GOLD, "D", "P  pooling", (-2.0, 3.5), ha="right")
    mark(ax, C[0], C[1], TYPE_L, "^", "C  cream-skim", (2.2, -7.5))
    ax.annotate("", xy=C, xytext=(P, P),
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=0.8,
                                mutation_scale=8, connectionstyle="arc3,rad=0.12"))


def panel_b(ax):
    setup_axes(ax, "B.  The separating menu, and when it also fails")
    p_avg = LAM_B * pH + (1 - LAM_B) * pL  # 0.23
    plot_fair(ax, pH, TYPE_H, "-")
    plot_fair(ax, pL, TYPE_L, "-")
    plot_fair(ax, p_avg, GOLD, (0, (3.6, 1.5)), lw=1.6)

    B = (106.238, 74.420)
    plot_indiff(ax, pH, u(WH_FI), TYPE_H, wn_min=70, wn_max=122)
    uL_sep = 0.8 * u(WN_SEP) + 0.2 * u(WL_SEP)
    plot_indiff(ax, pL, uL_sep, TYPE_L, wn_min=90, wn_max=126)

    mark(ax, E[0], E[1], TEXT, "o", "E", (2.0, -8.0))
    mark(ax, WH_FI, WH_FI, TYPE_H, "s", "H*", (2.2, -8.0))
    mark(ax, WN_SEP, WL_SEP, TYPE_L, "s", "L°  separating", (-2.2, -9.0), ha="right")
    mark(ax, B[0], B[1], GOLD, "D", "B  pooling that\nbreaks L°", (2.3, 1.8))
    ax.annotate("", xy=B, xytext=(WN_SEP, WL_SEP),
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=0.8,
                                mutation_scale=8, connectionstyle="arc3,rad=-0.12"))


def main():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 5.15), dpi=200)
    panel_a(axes[0])
    panel_b(axes[1])
    handles = [
        Line2D([0], [0], color=TYPE_H, lw=1.4, label="High-risk fair odds  (p = 1/2)"),
        Line2D([0], [0], color=TYPE_L, lw=1.4, label="Low-risk fair odds  (p = 1/5)"),
        Line2D([0], [0], color=GOLD, lw=1.6, ls=(0, (3.6, 1.5)), label="Pooling fair odds"),
        Line2D([0], [0], color="#333333", lw=1.0, ls=(0, (1.4, 1.2)), label="Indifference curves"),
        Line2D([0], [0], color="#B0B0B0", lw=0.8, label="Full-insurance line"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False,
               bbox_to_anchor=(0.5, 0.045), fontsize=7.0)
    fig.text(
        0.08, 0.008,
        "Illustrative.  W = 121,  L = 96,  u(w) = √w.  Here p_L = 1/5 and p_H = 1/2 are pre-existing types, not chosen actions.  "
        "Panel A uses a pooling price with λ = 0.35.  Panel B uses λ = 0.10; the separating menu fails for λ below about 0.16.",
        fontsize=6.2, color=MUTED, wrap=True,
    )
    fig.subplots_adjust(wspace=0.28, left=0.08, right=0.99, top=0.92, bottom=0.22)
    save(fig, "figure02-rothschild-stiglitz")
    print("figure02")


if __name__ == "__main__":
    main()
