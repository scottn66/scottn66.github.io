#!/usr/bin/env python3
"""Seaborn / matplotlib static figures for the power-law portfolio page.
Dark theme tuned to blend with the page's card backgrounds. Saves PNGs into
portfolio/bitcoin-power-law/assets/."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from statsmodels.graphics.tsaplots import plot_acf

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "bitcoin-power-law/assets"
RUN = ROOT / "runs/power_law"

CARD = "#11161b"
INK = "#dbe3ec"
MUTE = "#8b98a9"
ORANGE = "#f7931a"
BLUE = "#3b82f6"
GREEN = "#2ea043"
RED = "#f85149"
PURPLE = "#a371f7"


def _style():
    sns.set_theme(style="darkgrid")
    plt.rcParams.update({
        "figure.facecolor": CARD, "axes.facecolor": CARD, "savefig.facecolor": CARD,
        "axes.edgecolor": "#2a323d", "grid.color": "#222a33", "grid.alpha": 0.5,
        "text.color": INK, "axes.labelcolor": INK, "xtick.color": MUTE, "ytick.color": MUTE,
        "axes.titlecolor": INK, "font.size": 11, "axes.titlesize": 13,
        "font.family": "DejaVu Sans",
    })


def fig_residual_dist(econ):
    r = np.array(econ["residuals"]["values"])
    cur = r[-1]
    _style()
    fig, ax = plt.subplots(figsize=(6.6, 3.9))
    sns.histplot(r, bins=46, kde=True, color=ORANGE, edgecolor="none", alpha=0.55, ax=ax,
                 line_kws={"lw": 2})
    ax.axvline(0, color=MUTE, ls=":", lw=1.3, label="fair value")
    ax.axvline(cur, color=BLUE, lw=2, label=f"today ({cur:+.2f} dex)")
    ax.set_xlabel("residual  =  log₁₀(price) − power-law trend   (dex)")
    ax.set_ylabel("days")
    ax.set_title("Where Bitcoin trades relative to its trend (2016–2026)")
    ax.legend(frameon=False, fontsize=9, labelcolor=INK)
    fig.tight_layout()
    fig.savefig(ASSETS / "fig_residual_dist.png", dpi=140)
    plt.close(fig)


def fig_qq(econ):
    r = np.array(econ["residuals"]["values"])
    _style()
    fig, ax = plt.subplots(figsize=(5.6, 4.2))
    (osm, osr), (slope, intercept, _) = stats.probplot(r, dist="norm")
    pts = ax.scatter(osm, osr, s=10, color=PURPLE, alpha=0.5, edgecolor="none",
                     label="actual residuals")
    line, = ax.plot(osm, slope * osm + intercept, color=ORANGE, lw=2,
                    label="if perfectly Gaussian")
    # highlight the heavy tails
    ax.axvspan(osm.min(), -2, color=RED, alpha=0.06)
    ax.axvspan(2, osm.max(), color=RED, alpha=0.06)
    ax.set_xlabel("where a bell curve says the value should fall (σ)")
    ax.set_ylabel("where Bitcoin's deviation actually fell (dex)")
    ax.set_title("Q–Q plot: are the deviations Gaussian?")
    ax.legend(frameon=False, fontsize=9.5, labelcolor=INK, loc="upper left")
    ax.text(0.97, 0.05, "tails bend off the line →\nbig moves are fatter than a bell curve",
            transform=ax.transAxes, ha="right", va="bottom", color=MUTE, fontsize=9.5)
    fig.tight_layout()
    fig.savefig(ASSETS / "fig_qq.png", dpi=140)
    plt.close(fig)


def fig_lag(econ):
    """Lag-1 residual scatter — autocorrelation made visceral: today vs yesterday."""
    r = np.array(econ["residuals"]["values"])
    x, y = r[:-1], r[1:]
    rho = float(np.corrcoef(x, y)[0, 1])
    _style()
    fig, ax = plt.subplots(figsize=(5.6, 4.4))
    ax.scatter(x, y, s=7, color=BLUE, alpha=0.22, edgecolor="none")
    lim = [min(x.min(), y.min()) - 0.02, max(x.max(), y.max()) + 0.02]
    ax.plot(lim, lim, color=ORANGE, lw=2, ls="--", label="today = yesterday (45°)")
    ax.set_xlim(lim); ax.set_ylim(lim)
    ax.set_xlabel("yesterday's deviation from trend (dex)")
    ax.set_ylabel("today's deviation (dex)")
    ax.set_title(f"Each dot is one day · correlation ρ = {rho:.3f}")
    ax.legend(frameon=False, fontsize=9.5, labelcolor=INK, loc="upper left")
    ax.text(0.97, 0.05, "dots hug the diagonal →\ntoday ≈ yesterday →\nconsecutive days aren't independent",
            transform=ax.transAxes, ha="right", va="bottom", color=MUTE, fontsize=9.5)
    fig.tight_layout()
    fig.savefig(ASSETS / "fig_lag.png", dpi=140)
    plt.close(fig)


def fig_cycles(econ):
    p2p = econ["risk"]["peak_to_peak"]
    labels = [f"cycle {i+1}→{i+2}" for i in range(len(p2p))]
    vals = [p["multiple"] for p in p2p]
    _style()
    fig, ax = plt.subplots(figsize=(5.6, 3.8))
    bars = ax.bar(labels, vals, color=[ORANGE, "#e0851a", "#c9731a"][:len(vals)], width=0.6)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.4, f"{v:.1f}×",
                ha="center", color=INK, fontsize=12, fontweight="bold")
    ax.set_ylabel("peak-to-peak price multiple")
    ax.set_title("Diminishing returns: each cycle's gain shrinks")
    ax.set_ylim(0, max(vals) * 1.2)
    fig.tight_layout()
    fig.savefig(ASSETS / "fig_cycles.png", dpi=140)
    plt.close(fig)


def fig_aic(econ):
    recent = {m["key"]: m for m in econ["model_comparison"]["models"]}
    full = {m["key"]: m for m in econ["model_comparison_full"]["models"]}
    order = ["power", "exp", "stretched", "logistic"]
    names = {"power": "Power law", "exp": "Exponential", "stretched": "Stretched exp", "logistic": "Logistic"}
    keys = [k for k in order if k in recent and k in full]
    x = np.arange(len(keys))
    w = 0.38
    _style()
    fig, ax = plt.subplots(figsize=(6.8, 3.9))
    full_vals = [full[k]["delta_aic"] for k in keys]
    rec_vals = [recent[k]["delta_aic"] for k in keys]
    ax.bar(x - w / 2, full_vals, w, label="full history 2010–26", color=ORANGE)
    ax.bar(x + w / 2, rec_vals, w, label="recent 2016–26", color=BLUE)
    ax.set_xticks(x)
    ax.set_xticklabels([names[k] for k in keys], fontsize=10)
    ax.set_ylabel("ΔAIC  (lower = better; 0 = best)")
    ax.set_title("Model selection: who fits Bitcoin best?")
    ax.legend(frameon=False, fontsize=9, labelcolor=INK)
    ax.axhline(0, color=MUTE, lw=0.8)
    fig.tight_layout()
    fig.savefig(ASSETS / "fig_aic.png", dpi=140)
    plt.close(fig)


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    econ = json.loads((RUN / "econ.json").read_text())
    fig_residual_dist(econ)
    fig_qq(econ)
    fig_lag(econ)
    fig_cycles(econ)
    fig_aic(econ)
    # remove the retired ACF figure if present
    old = ASSETS / "fig_acf.png"
    if old.exists():
        old.unlink()
    print("wrote figures to", ASSETS)
    for p in sorted(ASSETS.glob("*.png")):
        print("  ", p.name, p.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
