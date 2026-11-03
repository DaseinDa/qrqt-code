# -*- coding: utf-8 -*-
"""scifig — helpers for publication-quality matplotlib figures, plus a colour
validator and an audit of the rendered figure.

Usage
-----
    import sys; sys.path.insert(0, r"<skill dir>/scripts"); import scifig
    W, H = scifig.setup(width="onehalf", aspect=0.6)
    fig, axes = plt.subplots(1, 2, figsize=(W, H))
    ...
    scifig.panel_label(axes[0], "A")
    scifig.label_line_ends(axes[0])
    scifig.audit(fig, target_width="onehalf")   # 0 FAIL required
    scifig.save(fig, "out/fig6")                 # .pdf + .png

Everything here is plain matplotlib + numpy; no other dependency.
"""
from __future__ import annotations

import itertools
import math
import os
import sys

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.text import Text
from matplotlib.transforms import Bbox

CM = 1.0 / 2.54
# Final printed widths in cm (see references/journal-specs.md; verify per journal).
WIDTHS = {"single": 8.9, "onehalf": 12.0, "double": 18.3}

# Fixed categorical order (Okabe & Ito, CVD-safe). Never cycle, never reorder.
OKABE_ITO = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#F0E442", "#000000"]
TOL_BRIGHT = ["#4477AA", "#EE6677", "#228833", "#CCBB44", "#66CCEE", "#AA3377", "#BBBBBB"]
BASELINE_GREY = "#8C8C8C"
BASELINE_GREY_2 = "#BFBFBF"
LINESTYLES = ["-", (0, (6, 3)), (0, (1.2, 1.8))]  # solid, dashed, dotted
MARKERS = ["o", "s", "^", "D", "v"]

# ----------------------------------------------------------------------------
# rcParams
# ----------------------------------------------------------------------------

def setup(width="single", height_cm=None, aspect=0.75, base_pt=7.0, font="DejaVu Sans",
          palette=None):
    """Set rcParams for a figure drawn at its final printed size.

    width: 'single' | 'onehalf' | 'double' | number (cm)
    aspect: height/width when height_cm is not given
    base_pt: body text size at final size (labels); ticks and legend are base-1
    Returns (width_in, height_in) for plt.subplots(figsize=...).
    """
    w_cm = WIDTHS.get(width, width) if not isinstance(width, (int, float)) else float(width)
    h_cm = float(height_cm) if height_cm else w_cm * aspect
    colors = list(palette) if palette else OKABE_ITO[:6]
    mpl.rcParams.update({
        "figure.figsize": (w_cm * CM, h_cm * CM),
        "figure.dpi": 150,
        "savefig.dpi": 600,
        "font.family": "sans-serif",
        "font.sans-serif": [font, "Arial", "Helvetica", "Liberation Sans"],
        "font.size": base_pt,
        "axes.labelsize": base_pt,
        "axes.titlesize": base_pt + 1,
        "xtick.labelsize": base_pt - 1,
        "ytick.labelsize": base_pt - 1,
        "legend.fontsize": base_pt - 1,
        "legend.title_fontsize": base_pt - 1,
        "axes.linewidth": 0.6,
        "lines.linewidth": 1.2,
        "lines.markersize": 3.5,
        "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "xtick.minor.width": 0.4, "ytick.minor.width": 0.4,
        "xtick.major.size": 2.5, "ytick.major.size": 2.5,
        "xtick.minor.size": 1.5, "ytick.minor.size": 1.5,
        "xtick.direction": "out", "ytick.direction": "out",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.prop_cycle": mpl.cycler(color=colors),
        "axes.grid": False,
        "legend.frameon": False,
        "legend.handlelength": 2.2,
        "legend.borderaxespad": 0.3,
        "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
        "mathtext.fontset": "dejavusans",
        "figure.constrained_layout.use": True,
    })
    return w_cm * CM, h_cm * CM


# ----------------------------------------------------------------------------
# Drawing helpers
# ----------------------------------------------------------------------------

def panel_label(ax, letter, x=-0.16, y=1.04, size=None, weight="bold"):
    """Bold panel letter outside the top-left corner (axes coordinates)."""
    size = size or mpl.rcParams["font.size"] + 2
    return ax.text(x, y, letter, transform=ax.transAxes, fontsize=size, fontweight=weight,
                   ha="right", va="bottom")


def label_line_ends(ax, lines=None, labels=None, pad_frac=0.01, fontsize=None, min_gap_frac=0.045,
                    side="right"):
    """Write each line's label at its right (or left) end, in the line's colour,
    nudging labels apart vertically so they do not overlap (simple 1-D de-overlap).
    Lines without a label (label starts with '_') are skipped.
    """
    lines = [l for l in (lines or ax.get_lines()) if isinstance(l, Line2D)]
    fontsize = fontsize or mpl.rcParams["axes.labelsize"]
    items = []
    for i, l in enumerate(lines):
        lab = (labels[i] if labels else l.get_label())
        if not lab or str(lab).startswith("_"):
            continue
        x, y = l.get_xdata(), l.get_ydata()
        x = np.asarray(x, float); y = np.asarray(y, float)
        ok = np.isfinite(x) & np.isfinite(y)
        if not ok.any():
            continue
        x, y = x[ok], y[ok]
        idx = int(np.argmax(x)) if side == "right" else int(np.argmin(x))
        items.append([x[idx], y[idx], str(lab), l.get_color()])
    if not items:
        return []
    # de-overlap in axes-fraction units
    y0, y1 = ax.get_ylim()
    span = (y1 - y0) if ax.get_yscale() == "linear" else None
    items.sort(key=lambda t: t[1])
    if span:
        gap = min_gap_frac * span
        for k in range(1, len(items)):
            if items[k][1] - items[k - 1][1] < gap:
                items[k][1] = items[k - 1][1] + gap
    x0, x1 = ax.get_xlim()
    dx = (x1 - x0) * pad_frac if ax.get_xscale() == "linear" else 0
    texts = []
    for x, y, lab, col in items:
        t = ax.text(x + dx if side == "right" else x - dx, y, lab, color=col, fontsize=fontsize,
                    ha="left" if side == "right" else "right", va="center", clip_on=False)
        texts.append(t)
    return texts


def save(fig, path_no_ext, formats=("pdf", "png"), dpi=600):
    os.makedirs(os.path.dirname(os.path.abspath(path_no_ext)) or ".", exist_ok=True)
    out = []
    for f in formats:
        p = f"{path_no_ext}.{f}"
        fig.savefig(p, dpi=dpi, bbox_inches="tight", pad_inches=0.02)
        out.append(p)
    w, h = fig.get_size_inches()
    print("saved %s  (%.1f x %.1f cm)" % (", ".join(out), w / CM, h / CM))
    return out


# ----------------------------------------------------------------------------
# Colour mathematics: sRGB -> OKLab, CVD simulation (Machado et al. 2009), dE
# ----------------------------------------------------------------------------

def _hex_to_rgb(h):
    if isinstance(h, (tuple, list)):
        return np.array(h[:3], float)
    return np.array(mpl.colors.to_rgb(h), float)


def _srgb_to_linear(c):
    c = np.asarray(c, float)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _linear_to_oklab(rgb):
    r, g, b = rgb
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = np.cbrt(l), np.cbrt(m), np.cbrt(s)
    return np.array([
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    ])


# Machado, Oliveira & Fernandes (2009) severity-1.0 matrices, applied in linear RGB.
_CVD = {
    "protan": np.array([[0.152286, 1.052583, -0.204868],
                        [0.114503, 0.786281, 0.099216],
                        [-0.003882, -0.048116, 1.051998]]),
    "deutan": np.array([[0.367322, 0.860646, -0.227968],
                        [0.280085, 0.672501, 0.047413],
                        [-0.011820, 0.042940, 0.968881]]),
    "tritan": np.array([[1.255528, -0.076749, -0.178779],
                        [-0.078411, 0.930809, 0.147602],
                        [0.004733, 0.691367, 0.303900]]),
}


def _oklab(color, cvd=None):
    lin = _srgb_to_linear(_hex_to_rgb(color))
    if cvd:
        lin = np.clip(_CVD[cvd] @ lin, 0, 1)
    return _linear_to_oklab(lin)


def delta_e(c1, c2, cvd=None):
    """OKLab distance x 100 (same scale as the dataviz validator)."""
    return float(np.linalg.norm(_oklab(c1, cvd) - _oklab(c2, cvd)) * 100)


def validate_palette(colors, background="#FFFFFF", min_de_normal=15.0, min_de_cvd=8.0,
                     lightness=(0.30, 0.80), min_bg_contrast=0.22, verbose=True):
    """Check a categorical palette: pairwise separation (normal + 3 CVD types),
    lightness band against the background, and contrast with the background.
    Returns dict with 'pass' and the worst pairs. Prints a report when verbose.
    """
    cols = list(colors)
    rep = {"pass": True, "pairs": [], "lightness": [], "min": {}}
    for mode in (None, "protan", "deutan", "tritan"):
        worst = (1e9, None)
        for a, b in itertools.combinations(range(len(cols)), 2):
            d = delta_e(cols[a], cols[b], mode)
            rep["pairs"].append((mode or "normal", cols[a], cols[b], d))
            if d < worst[0]:
                worst = (d, (cols[a], cols[b]))
        rep["min"][mode or "normal"] = worst
        thr = min_de_normal if mode is None else min_de_cvd
        if worst[1] is not None and worst[0] < thr:
            rep["pass"] = False
    bg_L = _oklab(background)[0]
    for c in cols:
        L = _oklab(c)[0]
        ok = lightness[0] <= L <= lightness[1] and abs(L - bg_L) >= min_bg_contrast
        rep["lightness"].append((c, L, ok))
        if not ok:
            rep["pass"] = False
    if verbose:
        print("palette validation (OKLab dE x100):")
        for mode, (d, pair) in rep["min"].items():
            thr = min_de_normal if mode == "normal" else min_de_cvd
            flag = "ok " if (pair is None or d >= thr) else "FAIL"
            print("  %s  min pair dE = %5.1f  (need >= %g)  %s" % (flag, d, thr, pair))
        for c, L, ok in rep["lightness"]:
            print("  %s  %s  L=%.2f" % ("ok " if ok else "FAIL", c, L))
        print("  =>", "PASS" if rep["pass"] else "FAIL")
    return rep


# ----------------------------------------------------------------------------
# Audit of a rendered figure
# ----------------------------------------------------------------------------

def _bbox_overlap(b1, b2):
    return not (b1.x1 <= b2.x0 or b2.x1 <= b1.x0 or b1.y1 <= b2.y0 or b2.y1 <= b1.y0)


def _data_lines(ax):
    out = []
    for l in ax.get_lines():
        x = np.asarray(l.get_xdata(), float)
        if x.size >= 2 and l.get_visible() and l.get_linestyle() != "None":
            out.append(l)
    return out


def audit(fig, target_width=None, min_font_pt=6.0, max_lines=6, min_de_normal=15.0,
          min_de_cvd=8.0, journal_mode=False, verbose=True):
    """Check the rendered figure the way a referee or production editor would.
    Returns list of (level, message); level in {'FAIL','WARN','OK'}.
    """
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    msgs = []

    # 1. physical width
    w_in, h_in = fig.get_size_inches()
    w_cm = w_in / CM
    if target_width is not None:
        tw = WIDTHS.get(target_width, target_width) if not isinstance(target_width, (int, float)) else float(target_width)
        if abs(w_cm - tw) / tw > 0.05:
            msgs.append(("WARN", "figure width %.1f cm differs from target %.1f cm" % (w_cm, tw)))
        else:
            msgs.append(("OK", "figure width %.1f cm (target %.1f)" % (w_cm, tw)))

    # 2. text sizes & overlaps (all Text artists with content)
    texts = [t for t in fig.findobj(Text) if t.get_text().strip() and t.get_visible()]
    small = [t for t in texts if t.get_fontsize() < min_font_pt]
    if small:
        msgs.append(("FAIL", "%d text items below %.0f pt: %s" % (
            len(small), min_font_pt, ", ".join(repr(t.get_text()[:18]) + "@%.1fpt" % t.get_fontsize() for t in small[:5]))))
    else:
        msgs.append(("OK", "all %d text items >= %.0f pt (smallest %.1f pt)" % (
            len(texts), min_font_pt, min(t.get_fontsize() for t in texts) if texts else 0)))
    boxes = []
    for t in texts:
        try:
            boxes.append((t, t.get_window_extent(renderer)))
        except Exception:
            pass
    overlaps = []
    for (t1, b1), (t2, b2) in itertools.combinations(boxes, 2):
        if b1.width > 0 and b2.width > 0 and _bbox_overlap(b1, b2):
            overlaps.append((t1.get_text()[:20], t2.get_text()[:20]))
    if overlaps:
        msgs.append(("WARN", "%d overlapping text pairs, e.g. %s" % (len(overlaps), overlaps[:3])))
    else:
        msgs.append(("OK", "no overlapping text boxes"))

    # 3. per-axes checks
    for k, ax in enumerate(fig.get_axes()):
        if not ax.get_visible() or getattr(ax, "_scifig_skip", False):
            continue
        tag = "axes[%d]" % k
        lines = _data_lines(ax)
        if len(lines) > max_lines:
            msgs.append(("FAIL", "%s: %d curves in one panel (max %d) -> split into panels" % (tag, len(lines), max_lines)))
        elif lines:
            msgs.append(("OK", "%s: %d curves" % (tag, len(lines))))
        # identical colour+linestyle
        seen = {}
        for l in lines:
            key = (mpl.colors.to_hex(l.get_color()), str(l.get_linestyle()), round(l.get_linewidth(), 2))
            seen.setdefault(key, []).append(l.get_label())
        dup = {k_: v for k_, v in seen.items() if len(v) > 1}
        if dup:
            msgs.append(("FAIL", "%s: curves share colour+linestyle+width: %s" % (tag, list(dup.values())[:3])))
        # colour separation among distinct colours (ignoring greys, which are baselines)
        cols = []
        for l in lines:
            h = mpl.colors.to_hex(l.get_color())
            r, g, b = _hex_to_rgb(h)
            is_grey = max(r, g, b) - min(r, g, b) < 0.08
            if not is_grey and h not in cols:
                cols.append(h)
        if len(cols) >= 2:
            rep = validate_palette(cols, min_de_normal=min_de_normal, min_de_cvd=min_de_cvd, verbose=False)
            dn = rep["min"]["normal"][0]
            dc = min(rep["min"][m][0] for m in ("protan", "deutan", "tritan"))
            lvl = "OK" if (dn >= min_de_normal and dc >= min_de_cvd) else "FAIL"
            msgs.append((lvl, "%s: %d colours, min dE normal %.1f (>=%g), min dE CVD %.1f (>=%g)" % (
                tag, len(cols), dn, min_de_normal, dc, min_de_cvd)))
        # axis labels
        if lines and (not ax.get_xlabel().strip() and not ax.get_shared_x_axes().joined(ax, ax)):
            pass
        if lines and not ax.get_xlabel().strip():
            msgs.append(("WARN", "%s: no x label (ok only if shared with a labelled panel)" % tag))
        if lines and not ax.get_ylabel().strip():
            msgs.append(("WARN", "%s: no y label (ok only if shared with a labelled panel)" % tag))
        # legend
        leg = ax.get_legend()
        if leg is not None and leg.get_visible():
            n = len(leg.get_texts())
            if n > 6:
                msgs.append(("WARN", "%s: legend has %d entries -> direct labels or caption" % (tag, n)))
            lb = leg.get_window_extent(renderer)
            covered = 0
            for l in lines:
                xy = ax.transData.transform(np.column_stack([l.get_xdata(), l.get_ydata()]))
                xy = xy[np.isfinite(xy).all(axis=1)]
                if xy.size and ((xy[:, 0] >= lb.x0) & (xy[:, 0] <= lb.x1) & (xy[:, 1] >= lb.y0) & (xy[:, 1] <= lb.y1)).any():
                    covered += 1
            if covered:
                msgs.append(("WARN", "%s: legend box covers %d curve(s) -> move it or use direct labels" % (tag, covered)))
        # in-panel title
        if journal_mode and ax.get_title().strip():
            msgs.append(("WARN", "%s: in-panel title '%s' (journal figures carry titles in the caption)" % (tag, ax.get_title()[:30])))

    if verbose:
        order = {"FAIL": 0, "WARN": 1, "OK": 2}
        print("scifig audit:")
        for lvl, m in sorted(msgs, key=lambda t: order[t[0]]):
            print("  %-4s %s" % (lvl, m))
        nf = sum(1 for l, _ in msgs if l == "FAIL"); nw = sum(1 for l, _ in msgs if l == "WARN")
        print("  => %d FAIL, %d WARN" % (nf, nw))
    return msgs


if __name__ == "__main__":
    # self-test: palette + a tiny figure
    validate_palette(OKABE_ITO[:3])
    validate_palette(OKABE_ITO[:6])
    W, H = setup("single")
    fig, ax = plt.subplots(figsize=(W, H))
    x = np.linspace(0, 1, 50)
    for i, a in enumerate((0.1, 0.3, 0.5)):
        ax.plot(x, 1 - a * x, label="|a|^2 = %.1f" % a)
    ax.set_xlabel("x"); ax.set_ylabel("y (bits)")
    panel_label(ax, "A"); label_line_ends(ax)
    audit(fig, target_width="single")
