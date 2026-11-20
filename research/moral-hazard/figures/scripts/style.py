"""Shared typography and color for the moral-hazard article figures."""

from pathlib import Path
import matplotlib as mpl
import matplotlib.pyplot as plt

ROOT = Path("/home/box/shared/portfolio-moral-hazard")
FIGDIR = ROOT / "figures"

TEXT = "#1E1E1E"
MUTED = "#555555"
ACCENT = "#1F4E9E"
ACCENT_SOFT = "#DCE6F4"
GOLD = "#C9A227"
GOLD_SOFT = "#F6EFD8"
HIDDEN = "#6B4C9A"
HIDDEN_SOFT = "#EDE3F7"
VERM = "#D55E00"
ORANGE = "#E69F00"
TEAL = "#009E73"
SKY = "#56B4E9"
LINE = "#4A4A4A"
RULE = "#C8C8C8"
PAPER = "#FFFFFF"

# Wong-inspired, used with line style or marker, not color alone
TYPE_H = VERM
TYPE_L = ACCENT

mpl.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 8.5,
    "axes.titlesize": 9.5,
    "axes.labelsize": 8.5,
    "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5,
    "legend.fontsize": 7.5,
    "axes.edgecolor": "#444444",
    "axes.linewidth": 0.7,
    "axes.labelcolor": TEXT,
    "text.color": TEXT,
    "xtick.color": TEXT,
    "ytick.color": TEXT,
    "figure.facecolor": PAPER,
    "axes.facecolor": PAPER,
    "savefig.facecolor": PAPER,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.08,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
})


def save(fig, stem):
    FIGDIR.mkdir(parents=True, exist_ok=True)
    png = FIGDIR / f"{stem}.png"
    svg = FIGDIR / f"{stem}.svg"
    fig.savefig(png, dpi=200)
    fig.savefig(svg)
    plt.close(fig)
    return png, svg


def panel_label(ax, letter, x=-0.08, y=1.06):
    ax.text(x, y, letter, transform=ax.transAxes, fontsize=11,
            fontweight="bold", va="bottom", ha="right", color=TEXT)
