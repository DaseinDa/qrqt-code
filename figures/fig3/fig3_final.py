# -*- coding: utf-8 -*-
"""fig3_final.py -- Fig. 3 (receiver-side memory requirement), FINAL, three panels, one colour per parameter set.

Run:  MPLBACKEND=Agg python fig3_final.py
Writes fig3_final.pdf / .png, fig3_final_source_data.csv and audit.txt into this folder only.
Inputs (read-only):
  _sciadv_work/timing/dmax_fidelity_grid.csv      (T_fixed and d_max grid; model B_avx2, on-path, 1Gbps)
  _sciadv_work/timing/fig_dmax_vs_Tcoh_data.csv   (independent curve data, used as a cross-check)

History: variant A (judges' winner) -> judges' edits applied -> user decision: every parameter set gets its own
colour, identical in every panel, and the figure carries one conventional legend; d_max is shown per criterion
in two panels (B hard cutoff, C F* = 0.90) with individual curves instead of family bands.

FIGURE BRIEF
Message (one sentence a referee should take away):
  Under the serial schedule Bob's memory wait is tau_m = T_fixed + d/v_fiber (5 us/km on top of a
  scheme-dependent intercept); with a 1 ms memory the ML-KEM sets reach 186-193 km under the hard cutoff but
  only 30-38 km at F* = 0.90, every single-core FrodoKEM set exceeds the 1 ms budget at any distance, and the
  six d_max(T_coh^B) curves coincide at large lifetimes and separate only at their knees (d_max = 0 feet).
Reader's first glance should land on:
  A: the three ML-KEM curves crossing the 1 ms guide near 190 km and the 0.223 ms guide near 35 km, the three
     FrodoKEM curves lying entirely above 1 ms.
  B, C: one bundle of curves with six feet on the abscissa (knees), cut by the 1 ms / 10 ms verticals at the
     labelled ML-KEM-768 dots (190 / 1990 km in B, 35 / 436 km in C).
Form: line family (A); line families on log-log axes (B, C), identical axes and identical colour key.
Panels: 3.  A: tau_m vs distance (0-250 km), six sets, fast latencies (single-core AVX2 / AES-NI, 3 GHz,
  1 Gb/s link).  B: d_max vs T_coh^B (10 us - 100 ms) under the hard cutoff tau_m = T_coh^B.  C: the same at
  F* = 0.90 (tau_m = 0.223 T_coh^B).  B and C share axes ranges; criterion -> panel (not linestyle).
Encoding table:
  parameter set    -> colour (categorical, fixed order, same in A/B/C) -> 6:
                      ML-KEM-512 #33BBEE, ML-KEM-768 #0072B2, ML-KEM-1024 #AA3377,
                      FrodoKEM-640 #E6AB02, FrodoKEM-976 #D55E00, FrodoKEM-1344 #009E73
  no-PQC reference -> baseline grey #8C8C8C, thinner, behind (reference guide) -> 1
  criterion        -> panel (B hard cutoff, C F* = 0.90)                       -> 2
  linestyle        -> not used (all curves solid, uniform 1.2 pt)
Curves per panel: 6 (+ the grey reference guide and the dotted/solid reference lifetimes).
Direct labels or legend?  One figure legend (single row below the panels: six sets + no PQC), nothing covers
  data; in-panel text is restricted to numbers and regime notes (186-193 km, 30-38 km, 190/1990 km, 35/436 km,
  "hard cutoff", "F* = 0.90: 0.223 ms", the FrodoKEM infeasibility note, the d_max = 0 key).
Target width: double column, 18.3 cm; height 7.5 cm; axis labels 7.5 pt, ticks 6.5 pt, annotations 7 pt,
  legend 6.5 pt, mathtext sub/superscripts 6.0 pt (>= 6 pt everywhere, verified in the PDF).
Palette: user-specified six hues (Okabe-Ito + Tol pools) validated together at run time (must PASS: all pairs
  normal dE >= 15, every CVD type >= 8).
What could be misread, and how the figure prevents it:
  - "the curve simply stops" at the knee -> triangles in the set's colour mark T_coh^B where d_max = 0, key
    "d_max = 0" written in B and C; "FrodoKEM: tau_m > 1 ms at all d (infeasible)" written in A.
  - the 10 ms comparison lifetime is off-scale in A -> "10 ms: off scale (see B, C)"; B and C draw the 10 ms
    line and label the ML-KEM-768 values beside the points.
  - the 0.223 ms guide could be read as a second device -> labelled "F* = 0.90: 0.223 ms" (caption: usable
    fraction of 1 ms).
  - slope vs intercept on a log axis -> the caption gives tau_m = T_fixed + d/v_fiber with the slope 5 us/km
    (CAPTION_NOTE.md); at this panel width an in-panel "slope 5 us/km" box cannot be placed on the bundle
    without overlapping another label, so the judges' caption option is used.
  - the three ML-KEM curves nearly coincide for d > 50 km in A -> the knee region (d < 40 km) separates them,
    the legend order matches the vertical order at d = 0, the caption says they differ by < 40 us.
  - no-PQC could be read as "equally protected" -> legend entry "no PQC (latency reference)".
Style self-review against references/anti-patterns.md: 1 (shades of one hue) no - six distinct hues, validated;
  2 (dash vs solid families) no linestyles at all; 3 (> 6 curves) six data curves per panel, the grey reference
  is a guide; 4 (legend covering data) legend outside the panels; 5 (< 6 pt) none incl. sub/superscripts;
  6 (titles) none; 8 (colour for version and parameter) criterion is a panel; 11 (off-scale/infeasible unsaid)
  annotated; 12 (units) all axes; 13 (same entity, same colour) one map for A/B/C; 15 (prose) short labels only.
"""
from __future__ import annotations

import csv
import io
import math
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib._mathtext as _mathtext
# Sub/superscripts: matplotlib shrinks them to 0.70 of the base size (7 pt -> 4.9 pt, below the 6 pt production
# minimum).  Use 6/7 instead so that every sub/superscript of a 7 pt string is exactly 6 pt (verified below).
_mathtext.SHRINK_FACTOR = 6.0 / 7.0
_mathtext.GROW_FACTOR = 1.0 / _mathtext.SHRINK_FACTOR
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PathCollection, PolyCollection
from matplotlib.lines import Line2D
from matplotlib.mathtext import MathTextParser
from matplotlib.path import Path
from matplotlib.text import Text
from matplotlib.ticker import FixedLocator, NullLocator, FuncFormatter

HERE = os.path.dirname(os.path.abspath(__file__))           # <repo>/figures/fig3
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))     # repository root
SKILL_SCRIPTS = os.path.join(REPO, "tools")                 # scifig.py
sys.path.insert(0, SKILL_SCRIPTS)
import scifig  # noqa: E402

WORK = REPO
GRID_CSV = os.path.join(WORK, "timing", "dmax_fidelity_grid.csv")
CURVE_CSV = os.path.join(WORK, "timing", "fig_dmax_vs_Tcoh_data.csv")
OUT = HERE
os.makedirs(OUT, exist_ok=True)


class _Tee(io.TextIOBase):
    """Duplicate stdout into audit.txt (the script's complete console output)."""

    def __init__(self, path):
        self.f = open(path, "w", encoding="utf-8")
        self.o = sys.stdout
        try:
            self.o.reconfigure(errors="replace")     # console code page may not know 'µ' / '▼'; the file is UTF-8
        except Exception:
            pass

    def write(self, s):
        self.o.write(s); self.f.write(s); return len(s)

    def flush(self):
        self.o.flush(); self.f.flush()


sys.stdout = _Tee(os.path.join(OUT, "audit.txt"))

# ----------------------------------------------------------------------------
# 1. Decided inputs and model
# ----------------------------------------------------------------------------
V_KM_PER_US = 0.2                       # v_fiber = 2e5 km/s
SLOPE_US_PER_KM = 1.0 / V_KM_PER_US     # 5 us/km
F_STAR = 0.90
LN_F = math.log(1.0 / (2.0 * F_STAR - 1.0))   # usable fraction of T_coh at F* = 0.90
assert abs(LN_F - 0.223144) < 1e-6, LN_F
T_REF_US, T_CMP_US = 1000.0, 10000.0    # T_coh^B reference 1 ms, comparison 10 ms
MODEL, SCHED, RATE = "B_avx2", "on-path", "1Gbps"   # fast latencies, serial schedule, 1 Gb/s link

SCHEMES = ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024", "FrodoKEM-640", "FrodoKEM-976", "FrodoKEM-1344"]
CAT = {"ML-KEM-512": 1, "ML-KEM-768": 3, "ML-KEM-1024": 5, "FrodoKEM-640": 1, "FrodoKEM-976": 3, "FrodoKEM-1344": 5}
FAMILY = {s: ("ML-KEM" if s.startswith("ML") else "FrodoKEM") for s in SCHEMES}
NOPQC = "no-PQC reference"
REP = "ML-KEM-768"


def dmax_km(T_us, t_fixed_us, crit):
    f = 1.0 if crit == "hard" else LN_F
    return V_KM_PER_US * (f * np.asarray(T_us, float) - t_fixed_us)


def tau_m_us(d_km, t_fixed_us):
    return t_fixed_us + SLOPE_US_PER_KM * np.asarray(d_km, float)


# ----------------------------------------------------------------------------
# 2. Read the decided data and assert the stated values before plotting
# ----------------------------------------------------------------------------
TF = {}
grid = {}
with open(GRID_CSV, newline="") as f:
    for r in csv.DictReader(f):
        if r["latency_model"] == MODEL and r["schedule"] == SCHED and r["link_rate"] == RATE:
            TF[r["scheme"]] = float(r["T_fixed_us"])
            grid[(r["scheme"], float(r["T_coh_us"]), r["F_target"])] = float(r["d_max_km"])
for s in SCHEMES + [NOPQC]:
    assert s in TF, s
# independent arithmetic from DECISIONS_round3 (Kyber512/768/1024 T_fixed 33.57/49.80/72.19 us)
assert abs(TF["ML-KEM-512"] - 33.57) < 0.01 and abs(TF["ML-KEM-768"] - 49.80) < 0.01 and abs(TF["ML-KEM-1024"] - 72.19) < 0.01
assert TF["FrodoKEM-640"] > T_REF_US and TF["FrodoKEM-976"] > T_REF_US and TF["FrodoKEM-1344"] > T_REF_US
assert TF[NOPQC] < 0.2

# model reproduces the grid for every scheme, T_coh and both criteria
for (s, T, crit), d_grid in grid.items():
    if crit in ("hard", "0.9"):
        assert abs(dmax_km(T, TF[s], crit) - d_grid) < 0.01, (s, T, crit, d_grid)

ml = ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"]
d_hard_1ms = [grid[(s, T_REF_US, "hard")] for s in ml]
d_f09_1ms = [grid[(s, T_REF_US, "0.9")] for s in ml]
assert 185.5 <= min(d_hard_1ms) < 186.0 and 193.0 < max(d_hard_1ms) <= 193.5, d_hard_1ms   # "186-193 km"
assert 30.0 <= min(d_f09_1ms) < 30.5 and 37.5 < max(d_f09_1ms) <= 38.5, d_f09_1ms          # "30-38 km"
assert abs(grid[(REP, T_REF_US, "hard")] - 190.04) < 0.01 and abs(grid[(REP, T_REF_US, "0.9")] - 34.67) < 0.01
assert abs(grid[(REP, T_CMP_US, "hard")] - 1990.04) < 0.01 and abs(grid[(REP, T_CMP_US, "0.9")] - 436.33) < 0.01
for s in ["FrodoKEM-640", "FrodoKEM-976", "FrodoKEM-1344"]:
    assert grid[(s, T_REF_US, "hard")] < 0 and grid[(s, T_REF_US, "0.9")] < 0, s       # infeasible at 1 ms
    assert grid[(s, T_CMP_US, "hard")] > 0                                              # feasible at 10 ms, hard
d_hard_10ms_all = [grid[(s, T_CMP_US, "hard")] for s in SCHEMES]
assert 1300 < min(d_hard_10ms_all) < 1310 and 1993 < max(d_hard_10ms_all) < 1994, d_hard_10ms_all
# slope of tau_m(d) is 5 us/km for every scheme
assert abs((tau_m_us(250, TF[REP]) - tau_m_us(0, TF[REP])) / 250 - 5.0) < 1e-9
# the labels written on the figure, checked against the data (not typed from memory)
assert "%d" % round(min(d_f09_1ms)) == "30" and "%d" % round(max(d_f09_1ms)) == "38"
assert "%d" % round(min(d_hard_1ms)) == "186" and "%d" % round(max(d_hard_1ms)) == "193"
assert "%d" % round(grid[(REP, T_REF_US, "hard")]) == "190" and "%d" % round(grid[(REP, T_REF_US, "0.9")]) == "35"
assert "%d" % round(grid[(REP, T_CMP_US, "hard")]) == "1990" and "%d" % round(grid[(REP, T_CMP_US, "0.9")]) == "436"
assert "%.3f" % (LN_F * T_REF_US / 1000.0) == "0.223"
# knees (d_max = 0) drawn as triangles: T_coh^B = T_fixed (hard) and T_fixed / 0.223 (F* = 0.90)
KNEE = {(s, "hard"): TF[s] for s in SCHEMES}
KNEE.update({(s, "0.9"): TF[s] / LN_F for s in SCHEMES})
for (s, crit), Tk in KNEE.items():
    assert abs(dmax_km(Tk, TF[s], crit)) < 1e-9, (s, crit)

# cross-check against the independently generated curve file (model B, on-path, hard / 0.9)
with open(CURVE_CSV, newline="") as f:
    lines = [ln for ln in f if not ln.startswith("#")]
hdr = lines[0].strip().split(",")
arr = np.array([[float(x) for x in ln.strip().split(",")] for ln in lines[1:]])
T_csv = arr[:, 0]
worst = 0.0
for s in SCHEMES + [NOPQC]:
    name = "no-PQC" if s == NOPQC else s
    for crit in ("hard", "0.9"):
        col = f"{MODEL}|{name}|on-path|{crit}" if s != NOPQC else f"{MODEL}|{name}|{crit}"
        j = hdr.index(col)
        worst = max(worst, float(np.max(np.abs(arr[:, j] - dmax_km(T_csv, TF[s], crit)))))
assert worst < 0.01, worst
print("data checks passed: T_fixed(us) =", {k: round(v, 2) for k, v in TF.items()},
      "| d_max(1 ms) hard", [round(x, 1) for x in d_hard_1ms], "F*=0.9", [round(x, 1) for x in d_f09_1ms],
      "| d_max(10 ms) ML-KEM-768 hard %.1f F*=0.9 %.1f" % (grid[(REP, T_CMP_US, "hard")], grid[(REP, T_CMP_US, "0.9")]),
      "| knees(us) hard", {s: round(KNEE[(s, "hard")], 1) for s in SCHEMES},
      "F*=0.9", {s: round(KNEE[(s, "0.9")], 1) for s in SCHEMES},
      "| max |curve CSV - model| = %.2e km" % worst)

# ----------------------------------------------------------------------------
# 3. Colour plan (validated: all six together), sizes
# ----------------------------------------------------------------------------
COL = {"ML-KEM-512": "#33BBEE", "ML-KEM-768": "#0072B2", "ML-KEM-1024": "#AA3377",
       "FrodoKEM-640": "#E6AB02", "FrodoKEM-976": "#D55E00", "FrodoKEM-1344": "#009E73"}
C_REF = scifig.BASELINE_GREY
C_GUIDE = "#555555"
C_TXT = "#333333"
pal = scifig.validate_palette([COL[s] for s in SCHEMES])
assert pal["pass"], "palette failed"
LW = 1.2             # uniform, all solid
LW_REF = 0.9
ANN = 7.0            # every in-panel annotation (sub/superscripts then 6.0 pt)
LEG = 6.5
LEAD_LW = 0.5

W, H = scifig.setup(width="double", height_cm=7.5, base_pt=7.5)
matplotlib.rcParams.update({"lines.dotted_pattern": [1.2, 1.8], "lines.scale_dashes": True})
fig, (axA, axB, axC) = plt.subplots(1, 3, figsize=(W, H), gridspec_kw={"width_ratios": [0.98, 1.01, 1.01], "wspace": 0.06})

ROTATED = []   # (text, ax, fn, x_anchor, x1, x2, offset_pt): re-aligned to the drawn curve after layout


def add_rotated(ax, text, fn, x_anchor, x1, x2, offset_pt, **kw):
    """Text parallel to the curve y = fn(x) (direction from x1 to x2 in display space), anchored at
    x_anchor on the curve and shifted offset_pt points along the curve normal (+ = above/left)."""
    t = ax.text(x_anchor, float(fn(x_anchor)), text, rotation=0, rotation_mode="anchor",
                ha="center", va="center", **kw)
    ROTATED.append((t, ax, fn, x_anchor, x1, x2, offset_pt))
    return t


def place_rotated():
    for t, ax, fn, xa, x1, x2, off in ROTATED:
        p1 = ax.transData.transform((x1, float(fn(x1))))
        p2 = ax.transData.transform((x2, float(fn(x2))))
        v = p2 - p1
        ang = math.degrees(math.atan2(v[1], v[0]))
        n = np.array([-v[1], v[0]]) / np.hypot(*v)              # unit normal, pointing to the upper-left side
        pa = ax.transData.transform((xa, float(fn(xa)))) + n * off * fig.dpi / 72.0
        xd, yd = ax.transData.inverted().transform(pa)
        t.set_position((xd, yd)); t.set_rotation(ang)


# ----------------------------------------------------------------------------
# 4. Panel A: tau_m vs distance, six sets, fast latencies
# ----------------------------------------------------------------------------
d = np.linspace(0.0, 250.0, 501)
for s in SCHEMES:                      # legend order; later sets drawn on top where the ML-KEM curves coincide
    axA.plot(d, tau_m_us(d, TF[s]), color=COL[s], ls="-", lw=LW, label=s, zorder=3)
axA.set_yscale("log")
axA.set_xlim(0, 250)
axA.set_ylim(20, 9000)
axA.set_xticks([0, 50, 100, 150, 200, 250])
yt = [20, 50, 100, 200, 500, 1000, 2000, 5000]
axA.yaxis.set_major_locator(FixedLocator(yt))
axA.yaxis.set_minor_locator(NullLocator())
axA.yaxis.set_major_formatter(FuncFormatter(lambda v, p: ("%g ms" % (v / 1000)) if v >= 1000 else ("%g µs" % v)))
axA.set_xlabel("Distance $d$ (km)")
axA.set_ylabel("Receiver memory wait $\\tau_m$")

# reference lifetimes (LineCollections, not data curves)
axA.hlines([T_REF_US, LN_F * T_REF_US], 0, 250, colors=C_GUIDE, lw=0.6, zorder=2)
axA.text(3, 0.955 * T_REF_US, "hard cutoff", fontsize=ANN, color=C_TXT, ha="left", va="top")   # the line sits on the 1 ms tick
axA.text(248, 0.94 * LN_F * T_REF_US, "$F$* = 0.90: 0.223 ms", fontsize=ANN, color=C_TXT, ha="right", va="top")
axA.text(3, 4750, "FrodoKEM: $\\tau_m$ > 1 ms\nat all $d$ (infeasible)", fontsize=ANN, color=C_TXT, ha="left", va="bottom",
         linespacing=1.1)

# crossing points of the ML-KEM curves with the two guides (labels + separate leaders)
for s, dh, df in zip(ml, d_hard_1ms, d_f09_1ms):
    axA.scatter([dh], [T_REF_US], s=9, color=COL[s], zorder=5, lw=0)
    axA.scatter([df], [LN_F * T_REF_US], s=9, color=COL[s], zorder=5, lw=0)
axA.text(248, 600, "186–193 km", fontsize=ANN, color=C_TXT, ha="right", va="center")     # ML-KEM crossings (dots in the
axA.text(60, 118, "30–38 km", fontsize=ANN, color=C_TXT, ha="left", va="center")          # three ML-KEM colours)
axA.add_collection(LineCollection([[(205.0, 685.0), (min(d_hard_1ms) + 1.0, 0.975 * T_REF_US)],
                                   [(58.0, 121.0), (max(d_f09_1ms) + 0.5, 0.985 * LN_F * T_REF_US)]],
                                  colors=C_TXT, linewidths=LEAD_LW, zorder=4, gid="leader"))
axA.text(247, 22, "10 ms: off scale (see B, C)", fontsize=ANN, color=C_TXT, ha="right", va="bottom")
# The equation / "slope 5 us/km" is NOT written in the panel (judges' option 1: caption).  At three panels across
# 18.3 cm, panel A is 1.45 in wide and a rotated 7 pt "slope 5 us/km" box cannot be placed along the ML-KEM
# bundle without its box overlapping "hard cutoff" or "186-193 km"; CAPTION_NOTE.md requires the formula.

# ----------------------------------------------------------------------------
# 5. Panels B (hard cutoff) and C (F* = 0.90): d_max vs T_coh^B, six individual curves + grey reference guide
# ----------------------------------------------------------------------------
T = np.logspace(1, 5, 4000)
FLOOR, TOP = 1.0, 5.0e4      # top leaves room for the vertical "1990 km" label above the bundle


def feas(s, crit):
    y = dmax_km(T, TF[s], crit)
    return np.where(y > 0, y, np.nan)


def panel_dmax(ax, crit, letter):
    # no-PQC reference: a guide (grey, thinner, behind), drawn as a LineCollection like the lifetime guides,
    # so the six parameter sets are the panel's data curves
    y_ref = feas(NOPQC, crit)
    ok = np.isfinite(y_ref)
    ax.add_collection(LineCollection([np.column_stack([T[ok], y_ref[ok]])], colors=C_REF, linewidths=LW_REF,
                                     zorder=2, gid="no PQC reference"))
    for s in SCHEMES:
        ax.plot(T, feas(s, crit), color=COL[s], ls="-", lw=LW, zorder=3, label=s)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(10, 1e5); ax.set_ylim(FLOOR, TOP)
    ax.xaxis.set_major_locator(FixedLocator([10, 100, 1000, 1e4, 1e5]))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: ("%g ms" % (v / 1000)) if v >= 1000 else ("%g µs" % v)))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_locator(FixedLocator([1, 10, 100, 1000, 1e4]))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: {1: "1", 10: "10", 100: "100", 1000: "1000", 10000: "10 000"}.get(int(round(v)), "")))
    ax.set_xlabel("Receiver memory lifetime $T^{B}_{\\mathrm{coh}}$")
    ax.set_ylabel("Maximum distance $d_{\\max}$ (km)")
    # reference lifetimes, short headers
    ax.vlines([T_REF_US, T_CMP_US], FLOOR, TOP, colors=C_GUIDE, lw=0.6, ls=(0, (1.2, 1.8)), zorder=2)
    ax.text(T_REF_US, TOP * 1.10, "1 ms", fontsize=ANN, color=C_TXT, ha="center", va="bottom", clip_on=False)
    ax.text(T_CMP_US, TOP * 1.10, "10 ms", fontsize=ANN, color=C_TXT, ha="center", va="bottom", clip_on=False)
    # knees: d_max = 0, triangle in the set's colour, key in the lower right
    for s in SCHEMES:
        ax.plot([KNEE[(s, crit)]], [FLOOR], marker="v", ms=3.5, color=COL[s], ls="None", clip_on=False, zorder=6)
    ax.text(12.0, 2.2e4, "▼ $d_{\\max}$ = 0", fontsize=ANN, color=C_TXT, ha="left", va="center")   # empty upper-left corner
    # ML-KEM-768 at the reference lifetimes: dot + value beside the point (+ short leader)
    pts = [(T_REF_US, grid[(REP, T_REF_US, crit)]), (T_CMP_US, grid[(REP, T_CMP_US, crit)])]
    ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=10, color=COL[REP], zorder=6, lw=0)
    scifig.panel_label(ax, letter, x=-0.22, size=9)
    return pts


ptsB = panel_dmax(axB, "hard", "B")
ptsC = panel_dmax(axC, "0.9", "C")
# Point labels: a 7 pt "1990 km" is 1.1 decades wide at this panel width, so no horizontal placement near the
# dots is free of data.  Each value is written vertically (reading upward) just left of its dotted lifetime line,
# starting right above the bundle, i.e. directly above its dot; the only dot on that line is the labelled one.
for ax, crit in ((axB, "hard"), (axC, "0.9")):
    for Tline, txt in ((T_REF_US, "%d km" % round(grid[(REP, T_REF_US, crit)])),
                       (T_CMP_US, "%d km" % round(grid[(REP, T_CMP_US, crit)]))):
        top_of_bundle = float(dmax_km(0.87 * Tline, TF[NOPQC], crit))      # grey reference = upper envelope
        ax.text(0.60 * Tline, 1.25 * top_of_bundle, txt, fontsize=ANN, color=COL[REP], ha="left", va="center",
                rotation=90, rotation_mode="anchor")

scifig.panel_label(axA, "A", x=-0.22, size=9)

# ----------------------------------------------------------------------------
# 6. One legend for the figure: single row below the panels (no free in-panel region holds seven entries
#    without covering data at >= 6.5 pt), handled by constrained layout ("outside" location)
# ----------------------------------------------------------------------------
handles = [Line2D([], [], color=COL[s], lw=LW, label=s) for s in SCHEMES]
handles.append(Line2D([], [], color=C_REF, lw=LW_REF, label="no PQC (latency reference)"))
leg = fig.legend(handles=handles, loc="outside lower center", ncol=len(handles), fontsize=LEG, frameon=False,
                 handlelength=1.6, handletextpad=0.5, columnspacing=1.2, borderaxespad=0.2)

# rotated labels follow the curves in display space: align after the layout has been computed (twice: the
# labels themselves can move the constrained layout by a hair)
for _ in range(2):
    fig.canvas.draw()
    place_rotated()

# ----------------------------------------------------------------------------
# 7. Own checks: mathtext glyph sizes; text vs data collisions (the skill audit checks text vs text only);
#    legend outside every axes
# ----------------------------------------------------------------------------
fig.canvas.draw()
renderer = fig.canvas.get_renderer()
texts = [t for t in fig.findobj(Text) if t.get_text().strip() and t.get_visible()]

parser = MathTextParser("path")
min_glyph = 99.0
for t in texts:
    if "$" in t.get_text():
        for part in t.get_text().split("\n"):
            if "$" in part:
                res = parser.parse(part, dpi=72, prop=t.get_fontproperties())
                min_glyph = min(min_glyph, min(g[1] for g in res.glyphs))
print("mathtext check: smallest glyph (incl. sub/superscripts) = %.2f pt (need >= 6)" % min_glyph)
assert min_glyph >= 6.0 - 1e-6, min_glyph


def text_polygon(t, pad_pt=1.0):
    rot = t.get_rotation()
    t.set_rotation(0)
    bb = t.get_window_extent(renderer)
    t.set_rotation(rot)
    pad = pad_pt * fig.dpi / 72.0
    c = np.array([[bb.x0 - pad, bb.y0 - pad], [bb.x1 + pad, bb.y0 - pad], [bb.x1 + pad, bb.y1 + pad], [bb.x0 - pad, bb.y1 + pad]])
    if abs(rot) < 1e-9:
        return c
    a = np.array(t.get_transform().transform(t.get_position()), float)   # rotation_mode='anchor'
    th = math.radians(rot)
    R = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])
    return (c - a) @ R.T + a


def _sample_segments(segs, n=120):
    pts = []
    for sg in segs:
        sg = np.asarray(sg, float)
        for k in range(len(sg) - 1):
            pts.append(np.column_stack([np.linspace(sg[k, 0], sg[k + 1, 0], n), np.linspace(sg[k, 1], sg[k + 1, 1], n)]))
    return np.vstack(pts) if pts else np.zeros((0, 2))


collisions = []
for ax in (axA, axB, axC):
    axbb = ax.get_window_extent(renderer)
    data_pts = []   # (name, display xy)
    for l in ax.get_lines():
        x = np.asarray(l.get_xdata(), float); y = np.asarray(l.get_ydata(), float)
        ok = np.isfinite(x) & np.isfinite(y)
        if not ok.any():
            continue
        xy = ax.transData.transform(np.column_stack([x[ok], y[ok]]))
        if x[ok].size == 1:    # knee marker: a 3.5 pt disc around the point
            r = 0.5 * l.get_markersize() * fig.dpi / 72.0
            ang = np.linspace(0, 2 * np.pi, 24)
            xy = xy + np.column_stack([r * np.cos(ang), r * np.sin(ang)])
        data_pts.append((l.get_label() or "marker", xy))
    for c in ax.collections:
        if c.get_gid() == "leader":
            continue
        if isinstance(c, LineCollection):
            segs = c.get_segments()
            xy = ax.transData.transform(_sample_segments(segs) if len(segs[0]) <= 2 else np.vstack(segs))
            data_pts.append((c.get_gid() or "reference line", xy))
        elif isinstance(c, PathCollection):
            xy = c.get_offset_transform().transform(c.get_offsets())
            data_pts.append(("points", xy))
    for t in texts:
        if t.axes is not ax:
            continue
        poly = Path(text_polygon(t))
        for name, xy in data_pts:
            inside = (xy[:, 0] >= axbb.x0 - 1) & (xy[:, 0] <= axbb.x1 + 1) & (xy[:, 1] >= axbb.y0 - 1) & (xy[:, 1] <= axbb.y1 + 1)
            if inside.any() and poly.contains_points(xy[inside]).any():
                collisions.append((t.get_text().replace("\n", " / ")[:32], name))
                if os.environ.get("FIG3_DEBUG"):
                    hit = xy[inside][poly.contains_points(xy[inside])]
                    inv = ax.transData.inverted()
                    print("   DEBUG %r poly(data)=%s  hits(data)=%s" % (
                        t.get_text()[:20], np.round(inv.transform(text_polygon(t)), 2).tolist(),
                        np.round(inv.transform(hit[[0, len(hit) // 2, -1]]), 2).tolist()))
print("text-vs-data check: %d collision(s)%s" % (len(collisions), (": " + "; ".join("%r touches %s" % c for c in collisions)) if collisions else ""))
if os.environ.get("FIG3_DEBUG"):      # axis-aligned text boxes (what scifig.audit compares), in data coordinates
    for ax, nm in ((axA, "A"), (axB, "B"), (axC, "C")):
        inv = ax.transData.inverted()
        for t in texts:
            if t.axes is ax:
                bb = t.get_window_extent(renderer)
                (x0, y0), (x1, y1) = inv.transform([[bb.x0, bb.y0], [bb.x1, bb.y1]])
                print("   DEBUG bbox %s %-26r x %.4g..%.4g  y %.4g..%.4g" % (nm, t.get_text().replace("\n", "/")[:26], x0, x1, y0, y1))

legbb = leg.get_window_extent(renderer)
leg_overlap = [k for k, ax in enumerate((axA, axB, axC)) if legbb.overlaps(ax.get_window_extent(renderer))]
print("legend check: %d entries, %.2f in wide, outside every panel: %s" % (
    len(leg.get_texts()), legbb.width / fig.dpi, "yes" if not leg_overlap else "NO (axes %s)" % leg_overlap))

# ----------------------------------------------------------------------------
# 8. Audit, save, source data
# ----------------------------------------------------------------------------
report = scifig.audit(fig, target_width="double")
n_fail = sum(1 for lvl, _ in report if lvl == "FAIL")
n_warn = sum(1 for lvl, _ in report if lvl == "WARN")
scifig.save(fig, os.path.join(OUT, "fig3_final"))
assert n_fail == 0, "audit reported %d FAIL" % n_fail
assert n_warn == 0, "audit reported %d WARN" % n_warn
assert not collisions, collisions
assert not leg_overlap, leg_overlap

with open(os.path.join(OUT, "fig3_final_source_data.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["# Fig. 3 (final) source data. Panel A: tau_m(d) = T_fixed + d/v, v = 0.2 km/us (2e5 km/s), latency model B_avx2, "
                "serial (on-path) schedule, 1 Gb/s link. Panels B (hard cutoff, f = 1) and C (F* = 0.90, f = ln(1/(2F*-1)) = 0.223144): "
                "d_max = v [f T_coh - T_fixed]; negative = infeasible; knee = T_coh at which d_max = 0 (triangles)."])
    w.writerow(["panel", "quantity", "x", "x_unit", "scheme", "criterion", "T_fixed_us", "value", "value_unit"])
    for s in SCHEMES:
        for x in np.linspace(0, 250, 51):
            w.writerow(["A", "tau_m", "%g" % x, "km", s, "", "%.4f" % TF[s], "%.4f" % tau_m_us(x, TF[s]), "us"])
    for s in ml:
        w.writerow(["A", "d_max_marked", "%.2f" % grid[(s, T_REF_US, "hard")], "km", s, "hard", "%.4f" % TF[s], "%.1f" % T_REF_US, "us"])
        w.writerow(["A", "d_max_marked", "%.2f" % grid[(s, T_REF_US, "0.9")], "km", s, "0.9", "%.4f" % TF[s], "%.1f" % T_REF_US, "us"])
    for panel, crit in (("B", "hard"), ("C", "0.9")):
        for s in SCHEMES + [NOPQC]:
            for x in np.logspace(1, 5, 81):
                w.writerow([panel, "d_max", "%.6g" % x, "us", s, crit, "%.4f" % TF[s], "%.4f" % dmax_km(x, TF[s], crit), "km"])
        for s in SCHEMES:
            w.writerow([panel, "knee", "%.4f" % KNEE[(s, crit)], "us", s, crit, "%.4f" % TF[s], "0", "km"])
        for x, y in (ptsB if panel == "B" else ptsC):
            w.writerow([panel, "d_max_marked", "%g" % x, "us", REP, crit, "%.4f" % TF[REP], "%.2f" % y, "km"])
print("done")
