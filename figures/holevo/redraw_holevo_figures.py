#!/usr/bin/env python3
"""Redraw Figs. 6 and 7 from the verified Source Data, at Nature lettering size.

WHY. The co-author's published panels are raster (JPEG, 790 px wide) with the
in-panel lettering set for a full-page view. Placed at their size in the Nature
Communications layout the axis tick labels print at about 2.0 pt and the in-panel
titles at about 3.5 pt, against the 5-7 pt that Nature asks for. The resolution is
fine (365 dpi); the type is simply too small relative to the plot, which no
placement change can fix.

WHAT THIS DOES. It redraws the same six panels - same curves, same colours, same
legends, same axis ranges - from source_data/SourceData_Fig6*.csv and
SourceData_Fig7*.csv, which were themselves recomputed from the closed forms the
paper states and checked panel by panel against the published images. Two things
change:

  * output is vector PDF, drawn at exactly the size it is placed at in the
    manuscript, with 7 pt axis labels and 6 pt ticks and legends, so the lettering
    prints at the size it is drawn;
  * the in-panel titles are dropped. Every one of them repeats what the figure
    legend already says ("Holevo information (Independent Leakage Model) where
    k1 = k2 = 1." vs the legend's "(a) independent exponential leakage with rates
    k1 = k2 = 1"), and removing them returns that space to the plots.

THIS IS AN OFFER, NOT A SUBSTITUTION. The manuscript still includes the
co-author's original JPEGs. These PDFs are written to Holevo/regen/ for the
co-author to compare and approve.

Usage:  python redraw_holevo_figures.py [--outdir DIR] [--compare]
"""
import argparse
import csv
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "..", "source_data"))

# Placed size in the manuscript: Fig. 6 subfigures at 0.48\textwidth and Fig. 7
# subfigures at 0.42\textwidth of a 5.15 in text block. Drawing at the placed size
# is what makes a point on the page a point in the file.
W6, H6 = 2.47, 1.78
W7, H7 = 2.16, 2.60

# matplotlib's default cycle, which the published panels use.
C = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
SER7 = [C[0], C[2], C[3], C[4]]          # the four gamma / mu series of Fig. 7
MARK6 = ["o", "s", "^", "*", "D"]

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["DejaVu Serif"],
    "mathtext.fontset": "dejavuserif",
    "font.size": 6.5,
    "axes.labelsize": 7,
    "axes.titlesize": 7,
    "legend.fontsize": 6,
    "xtick.labelsize": 6,
    "ytick.labelsize": 6,
    "axes.linewidth": 0.6,
    "grid.linewidth": 0.4,
    "grid.alpha": 0.45,
    "lines.linewidth": 1.1,
    "xtick.major.width": 0.5,
    "ytick.major.width": 0.5,
    "xtick.major.size": 2.2,
    "ytick.major.size": 2.2,
    "legend.frameon": True,
    "legend.framealpha": 0.9,
    "legend.borderpad": 0.3,
    "legend.labelspacing": 0.25,
    "legend.handlelength": 1.4,
    "legend.handletextpad": 0.5,
    # Not bbox="tight": that crops to the artists' extent, which is wider than
    # figsize here, so the file would be scaled down when placed and the
    # lettering would shrink with it. Constrained layout keeps everything in.
    "savefig.bbox": "standard",
    "figure.constrained_layout.use": True,
    "figure.constrained_layout.h_pad": 0.02,
    "figure.constrained_layout.w_pad": 0.02,
    "figure.constrained_layout.hspace": 0.03,
})


def read(name):
    """Return the CSV as a dict of column name -> numpy array, comments skipped."""
    path = os.path.join(SRC, name)
    with open(path, encoding="utf-8") as fh:
        rows = [r for r in csv.reader(l for l in fh if not l.startswith("#"))]
    head, body = rows[0], rows[1:]
    out = {}
    for j, k in enumerate(head):
        out[k] = np.array([float(r[j]) for r in body])
    return out


def series(d, xkey, skey, ykey):
    """Split a long-form CSV into one (x, y) pair per value of the series column."""
    for s in sorted(set(d[skey])):
        m = d[skey] == s
        yield s, d[xkey][m], d[ykey][m]


def fig6(outdir):
    # --- (a) chi vs the damping parameter, one curve per input amplitude --------
    d = read("SourceData_Fig6a.csv")
    fig, ax = plt.subplots(figsize=(W6, H6))
    for i, (s, x, y) in enumerate(series(d, "gamma", "alpha_sq", "chi_bits")):
        ax.plot(x, y, color=C[i], label=r"$|\alpha|^2 = %.2f$" % s)
        k = np.linspace(0, len(x) - 1, 10).astype(int)
        ax.plot(x[k], y[k], MARK6[i], color=C[i], ms=2.6, mew=0)
    ax.set_xlabel(r"Amplitude damping parameter $\gamma$")
    ax.set_ylabel(r"Holevo quantity $\chi$ (bits)")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.52)
    ax.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.grid(True, ls=":")
    ax.legend(ncol=2, loc="upper center", columnspacing=1.0, borderaxespad=0.2)
    fig.savefig(os.path.join(outdir, "Holevo_AD.pdf"))
    plt.close(fig)

    # --- (b) chi vs the input amplitude, one curve per damping parameter --------
    d = read("SourceData_Fig6b.csv")
    fig, ax = plt.subplots(figsize=(W6, H6))
    for i, (s, x, y) in enumerate(series(d, "alpha_sq", "gamma", "chi_bits")):
        ax.plot(x, y, color=C[i], label=r"$\gamma = %.1f$" % s)
        k = np.linspace(0, len(x) - 1, 10).astype(int)
        ax.plot(x[k], y[k], MARK6[i], color=C[i], ms=2.6, mew=0)
    ax.set_xlabel(r"$|\alpha|^2$")
    ax.set_ylabel(r"Holevo quantity $\chi$ (bits)")
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.03, 1.05)
    ax.grid(True, ls=":")
    ax.legend(loc="lower right")
    fig.savefig(os.path.join(outdir, "Holevo_gamma.pdf"))
    plt.close(fig)


PANELS7 = [
    ("SourceData_Fig7a.csv", "gamma", r"$\gamma = %.1f$", "ILM_1.pdf", False),
    ("SourceData_Fig7b.csv", "gamma", r"$\gamma = %.1f$", "SLM.pdf", False),
    ("SourceData_Fig7c.csv", "gamma", r"$\gamma = %.1f$", "BLM_1.pdf", False),
    ("SourceData_Fig7d.csv", "mu", r"$\mu = %.1f$", "CLM_1.pdf", True),
]


def fig7(outdir):
    for name, skey, lab, out, inset in PANELS7:
        d = read(name)
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(W7, H7), sharex=True)
        for i, (s, x, y) in enumerate(series(d, "time", skey, "expected_holevo_bits")):
            ax1.plot(x, y, color=SER7[i], label=lab % s)
        for i, (s, x, y) in enumerate(series(d, "time", skey, "eve_fidelity")):
            ax2.plot(x, y, color=SER7[i], label=lab % s)
        # Short labels: at 7 pt the descriptive versions are longer than the
        # 79 pt each subplot is tall, so they overflow and get clipped. The
        # figure legend names both quantities in full.
        ax1.set_ylabel(r"$\mathbb{E}[\chi(t)]$ (bits)")
        ax2.set_ylabel(r"Fidelity $F(t)$")
        ax2.set_xlabel(r"Time $t$")
        for ax in (ax1, ax2):
            ax.set_xlim(0, 5)
            ax.grid(True, ls=":")
        ax1.legend(loc="upper right")
        ax2.legend(loc="lower right")
        if inset:
            # the published panel (d) carries a zoom on 1.0 <= t <= 1.9
            ax1.set_ylim(top=0.92)
            axi = ax1.inset_axes([0.40, 0.30, 0.56, 0.36])
            for i, (s, x, y) in enumerate(series(d, "time", skey,
                                                 "expected_holevo_bits")):
                m = (x >= 1.0) & (x <= 1.9)
                axi.plot(x[m], y[m], color=SER7[i])
            axi.set_xlim(1.0, 1.9)
            axi.tick_params(labelsize=5, width=0.4, length=1.4, pad=1.2)
            for sp in axi.spines.values():
                sp.set_linewidth(0.4)
            ax1.indicate_inset_zoom(axi, edgecolor="0.4", linewidth=0.4)
        fig.savefig(os.path.join(outdir, out))
        plt.close(fig)


def compare(outdir):
    """Print, for each panel, the smallest text the reader has to read."""
    import fitz
    from PIL import Image
    H = os.path.normpath(os.path.join(HERE, "..", "..", "..",
                                      "natcomms_revision", "Holevo"))
    print("\n  panel            published raster            redrawn vector")
    for jpg, pdf, placed in (("Holevo_AD.jpg", "Holevo_AD.pdf", W6),
                             ("Holevo_gamma.jpg", "Holevo_gamma.pdf", W6),
                             ("ILM_1.jpg", "ILM_1.pdf", W7),
                             ("SLM.jpg", "SLM.pdf", W7),
                             ("BLM_1.jpg", "BLM_1.pdf", W7),
                             ("CLM_1.jpg", "CLM_1.pdf", W7)):
        im = Image.open(os.path.join(H, jpg)).convert("L")
        w = im.size[0]
        a = np.asarray(im)
        ink = (a < 200).sum(axis=1)
        bands, start = [], None
        for i, v in enumerate(ink > 0):
            if v and start is None:
                start = i
            elif not v and start is not None:
                bands.append(i - start)
                start = None
        small = min([b for b in bands if b <= 40], default=0)
        d = fitz.open(os.path.join(outdir, pdf))
        sizes = [sp["size"] for blk in d[0].get_text("dict")["blocks"]
                 for ln in blk.get("lines", []) for sp in ln["spans"]]
        scale = placed * 72.0 / d[0].rect.width
        print("   %-16s %5.2f pt smallest text     %5.2f pt smallest text"
              % (jpg.replace(".jpg", ""), small * (placed * 72.0 / w),
                 (min(sizes) * scale) if sizes else 0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=os.path.join(HERE, "output"))
    ap.add_argument("--compare", action="store_true")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    fig6(args.outdir)
    fig7(args.outdir)
    print("wrote 6 vector panels to %s" % args.outdir)
    if args.compare:
        compare(args.outdir)


if __name__ == "__main__":
    main()
