# -*- coding: utf-8 -*-
"""
FIGURE BRIEF  (Supplementary Fig. S1, final -- label fig:pade_comparison, SI Note 2-3,
               "Padé-approximated versus exact log2 P_LWE as a function of the lattice rank m")
Message (one sentence a referee should take away):
  Over m = 5-60 at T_BKZ = 2^30 s the Winitzki-Padé closed form of log2 P_LWE (SI Eq.
  pade_log_prob) lies on top of the exact erf product (SI Eq. PLWE_final); both are of order
  1e-8 or smaller, and the relative error of 1e-3 to 1.4e-1 (m = 35-60) is set, for m <~ 40,
  by the double-precision floor of these tiny values rather than by the approximation itself.
Reader's first glance should land on:
  the dashed vermilion Padé curve riding on the solid blue exact curve in A: both are 0 until
  m ~ 45 and drop to -1.2e-8 at m = 60.
Form: line family (two coincident model curves) + one error curve; two stacked panels, shared x.
Panels: A (top) log2 P_LWE (x 1e-8) vs m, exact and Padé; B (bottom) relative error
  |log2 P_Padé - log2 P_exact| / |log2 P_exact| on a log axis, drawn only where the original
  figure drew it: |log2 P_LWE| > 1e-15 in double precision, i.e. m >= 35.
Content and arithmetic reproduce the old figure build_v2/Figure/log2pr_vs_m.pdf, whose script
  is code_from_D/PQNet/PQNet_Figure/improve/Figure61.py (read-only): same grid (integer m =
  5..60), same expression order (so the rounding-floor part of panel B is the same), same mask.
  Styling differences only: no open markers on the model curves (the dash already separates
  the coincident curves), no fill under the error curve, no grid, journal sizes and letters.
Encoding table:
  evaluation method -> colour (categorical, fixed order) -> 2
                        exact #0072B2 blue (solid), Padé #D55E00 vermilion (dashed, drawn
                        on top so that both colours stay visible where the curves coincide)
  relative error    -> colour #009E73 green, its own panel (B)                 -> 1
  quantity          -> panel (value / error)                                    -> 2
Curves per panel: A 2, B 1  (all <= 6)
Legend: A, lower left (empty region: the curves run along y = 0 and drop only at the right
  edge); B has a single series named by its y label, no legend. Direct annotation: one grey
  note in B saying why the error curve starts at m = 35 (anti-pattern 11).
Target width: single column 8.5 cm (user), height 7.8 cm. Sizes (Fig. 3 convention): axis
  labels 7.5 pt; tick labels, legend and notes 7 pt; panel letters 9 pt bold.
  matplotlib._mathtext.SHRINK_FACTOR = 6/7 (as in fig3_final.py / fig5_final.py) so every
  sub/superscript of a 7 pt string prints at 6.0 pt; the script parses every mathtext string
  and asserts that the smallest printed glyph is >= 6 pt.
Palette: Okabe-Ito indices 0, 1, 2 (validated 3-subset of palettes.md); validate_palette ->
  min dE normal 18.7, protan 13.0, deutan 11.0, tritan 8.6: PASS (asserted below).
What could be misread, and how the figure prevents it:
  - "the Padé curve is missing / only one curve": dashed vermilion on top of solid blue, so
    both colours show along the whole curve; the legend names both.
  - "the error curve was cut off": the note in B states that for m < 35 |log2 P_LWE| is below
    1e-15, the double-precision floor, so the relative error is not drawn.
  - "log2 P_LWE is of order 1": the y label of A carries the (x 1e-8) scale.
  - "this is a real-lattice calibration": the caption must say illustrative set A (SI Table
    tab:bkz_params): a = 0.3, b = 2.7, T_BKZ = 2^30 s, ||b1|| = 10, d_i = 2, s = 2.

STYLE SELF-REVIEW (references/anti-patterns.md, checked before drawing)
  1  shades of one hue ......... no: three distinct Okabe-Ito hues.
  2  dash as the only cue ...... no: the dashed curve also differs in hue; the dash is what
                                 keeps the underlying solid curve visible (coincident curves).
  3/4 > 6 curves / big legend .. no: 2 + 1 curves; a two-entry legend in an empty corner.
  5  text < 6 pt ............... no: audit asserts >= 6 pt; own glyph check covers sub/superscripts.
  6  in-panel titles ........... none (journal mode); the caption carries the title.
  11 curve stops unexplained ... no: grey note in B explains the start at m = 35.
  12 unit-less axes ............ m is a count (lattice rank); log2 P_LWE is dimensionless with
                                 the scale in the label; relative error is dimensionless.
  13 colour per entity ......... exact = blue, Padé = vermilion in S1 and S2 alike.
  14 frames / grids ............ top/right spines off, no grid, no fills.
  15 paragraphs in the figure .. one three-line note.
  22 no legend ................. no: conventional legend in A.
"""
import os
import sys
import math
os.environ.setdefault("MPLBACKEND", "Agg")
import numpy as np
from scipy.special import erf
import matplotlib
matplotlib.use("Agg")
import matplotlib._mathtext as _mathtext
# Sub/superscripts: matplotlib shrinks them to 0.70 of the base size (7 pt -> 4.9 pt, below the
# 6 pt production minimum). As in fig3_final.py, use 6/7 so that every sub/superscript of a
# 7 pt string prints at exactly 6.0 pt (verified by the glyph check at the end).
_mathtext.SHRINK_FACTOR = 6.0 / 7.0
_mathtext.GROW_FACTOR = 1.0 / _mathtext.SHRINK_FACTOR
import matplotlib.pyplot as plt
from matplotlib.mathtext import MathTextParser
from matplotlib.text import Text
from matplotlib.ticker import MultipleLocator, LogLocator, NullFormatter

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools")))
import scifig

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- model (SI Note 2-3)
# Illustrative set A of SI Table tab:bkz_params, as stated in the caption of fig:pade_comparison.
A, B = 0.3, 2.7            # BKZ runtime fit  log2 delta_root = a / (log2 T_BKZ + b)
LOG2T = 30.0               # T_BKZ = 2^30 s
B1, DI, S = 10.0, 2.0, 2.0  # ||b1||, search width d_i, Gaussian parameter s
W_PADE = 0.140012          # Winitzki's constant w
M_GRID = np.arange(5, 61)  # lattice rank m = 5 ... 60 (integer: number of Gram-Schmidt layers)
FLOOR = 1e-15              # the relative error is drawn only where |log2 P_LWE| > FLOOR (as in the old figure)

# The two evaluations keep the expression order of the original script (improve/Figure61.py):
# for m <~ 40 the values are within a few ulp of 0 and the relative error depends on that order.


def _gamma_lambda(log2T):
    gamma = 2.0 * A / (log2T + B)                   # = 2 log2 delta_root  (SI Eq. delta_from_T)
    lam = B1 * np.sqrt(np.pi) / (2.0 * S)           # ||b1|| sqrt(pi) / (2 s)
    return gamma, lam


def log2p_exact(m, log2T):
    """log2 P_LWE = sum_i log2 erf(z_i),  z_i = d_i lam 2^{-gamma (i-1)}  (SI Eq. PLWE_final; scipy erf)."""
    gamma, lam = _gamma_lambda(log2T)
    i = np.arange(1, m + 1)
    z = DI * lam * 2.0 ** (-gamma * (i - 1))
    return float(np.sum(np.log2(erf(z))))


def log2p_pade(m, log2T):
    """SI Eq. pade_log_prob: sum_i log2 sqrt(1 - exp(-W_i (4/pi + w W_i)/(1 + w W_i))), W_i = z_i^2."""
    gamma, lam = _gamma_lambda(log2T)
    i = np.arange(1, m + 1)
    W = (DI ** 2) * (lam ** 2) * 2.0 ** (-2.0 * gamma * (i - 1))
    with np.errstate(divide="ignore"):
        return float(np.sum(np.log2(np.sqrt(1.0 - np.exp(-(W * (4.0 / np.pi + W_PADE * W)) / (1.0 + W_PADE * W))))))


EX = np.array([log2p_exact(m, LOG2T) for m in M_GRID])
PA = np.array([log2p_pade(m, LOG2T) for m in M_GRID])
with np.errstate(divide="ignore", invalid="ignore"):
    REL = np.abs((PA - EX) / EX)
DEFINED = np.isfinite(REL) & (np.abs(EX) > FLOOR) & (REL > 0)
M_FIRST = int(M_GRID[DEFINED][0])

# Reference only (not drawn): the true relative error of the Winitzki formula, evaluated with
# 40 significant digits, so that the caption can say which part of panel B is the rounding floor.
try:
    import mpmath as mp
    mp.mp.dps = 40

    def _true_rel(m):
        e = p = mp.mpf(0)
        for i in range(1, m + 1):
            z = mp.mpf(DI) * B1 * mp.sqrt(mp.pi) / (2 * S) * mp.mpf(2) ** (-2 * (i - 1) * mp.mpf(A) / (LOG2T + B))
            z2 = z * z
            e += mp.log(mp.erf(z), 2)
            p += mp.log(1 - mp.exp(-z2 * (4 / mp.pi + W_PADE * z2) / (1 + W_PADE * z2)), 2) / 2
        return float(abs(p - e) / abs(e))
    REL_TRUE = np.array([_true_rel(int(m)) for m in M_GRID])
except ImportError:                                  # the figure itself does not need mpmath
    REL_TRUE = np.full(M_GRID.shape, np.nan)

# ---------------------------------------------------------------- checks against the old figure
print("== Supplementary Fig. S1 (fig:pade_comparison): values read off build_v2/Figure/log2pr_vs_m.pdf ==")
print("log2 P_LWE at m = 60: exact %.4e, Padé %.4e (old figure: -1.24e-8 / -1.18e-8)" % (EX[-1], PA[-1]))
assert abs(EX[-1] - (-1.2301e-8)) < 2e-11 and abs(PA[-1] - (-1.1754e-8)) < 2e-11
print("double-precision floor: exact is 0 for m <= %d, Padé is 0 for m <= %d; |log2 P| <= 1e-15 for m <= %d"
      % (M_GRID[EX == 0].max(), M_GRID[PA == 0].max(), M_GRID[np.abs(EX) <= FLOOR].max()))
assert np.all(EX[M_GRID <= 30] == 0.0) and np.all(PA[M_GRID <= 30] == 0.0), "values far below the floor must be 0"
k_min = int(np.argmin(np.where(DEFINED, REL, np.inf)))
print("relative error (drawn): first at m = %d (%.3f); minimum %.3e at m = %d; %.3e at m = 60"
      % (M_FIRST, REL[DEFINED][0], REL[k_min], M_GRID[k_min], REL[-1]))
assert M_FIRST == 35 and abs(REL[DEFINED][0] - 0.1429) < 1e-3
assert M_GRID[k_min] == 44 and abs(REL[k_min] - 1.663e-3) < 1e-5 and abs(REL[-1] - 4.449e-2) < 1e-4
assert REL[DEFINED].max() < 0.2 and REL[DEFINED].min() > 1e-3
if np.isfinite(REL_TRUE).all():
    print("40-digit reference: true relative error %.3f at m = 5, %.3e at 35, %.3e at 44, %.3e at 60; "
          "drawn and true agree to < 5%% for m >= %d"
          % (REL_TRUE[0], REL_TRUE[M_GRID == 35][0], REL_TRUE[M_GRID == 44][0], REL_TRUE[-1],
             M_GRID[DEFINED][np.abs(REL[DEFINED] / REL_TRUE[DEFINED] - 1) < 0.05][0]))
    assert abs(REL_TRUE[-1] - REL[-1]) < 1e-5

np.savetxt(os.path.join(HERE, "figS1_final_source_data.csv"),
           np.column_stack([M_GRID, EX, PA, np.where(DEFINED, REL, np.nan), REL_TRUE]), delimiter=",",
           fmt=["%d", "%.10e", "%.10e", "%.6e", "%.6e"],
           header=("m,log2P_LWE_exact,log2P_LWE_pade,relative_error_drawn,relative_error_40digit_reference "
                   "(a=%g,b=%g,log2 T_BKZ=%g,||b1||=%g,d_i=%g,s=%g,w=%g; columns 2-4 in double precision as drawn; "
                   "relative_error = |pade-exact|/|exact|, nan where |log2P_LWE| <= 1e-15 (not drawn); "
                   "column 5 = same quantity with 40 significant digits, reference only, not in the figure)"
                   % (A, B, LOG2T, B1, DI, S, W_PADE)), encoding="utf-8")

# ---------------------------------------------------------------- palette
C_EX, C_PA, C_RE = scifig.OKABE_ITO[0], scifig.OKABE_ITO[1], scifig.OKABE_ITO[2]
NOTE_GREY = "#555555"
rep = scifig.validate_palette([C_EX, C_PA, C_RE])
assert rep["pass"]

# ---------------------------------------------------------------- figure
FIG_W, FIG_H = 8.5, 7.8                                   # cm (single column, user: 8.5 cm)
W, H = scifig.setup(width=FIG_W, height_cm=FIG_H, base_pt=7.5)
TICK, LEG, ANN = 7.0, 7.0, 7.0
matplotlib.rcParams.update({"xtick.labelsize": TICK, "ytick.labelsize": TICK, "legend.fontsize": LEG})
fig, (axA, axB) = plt.subplots(2, 1, figsize=(W, H), sharex=True,
                               gridspec_kw=dict(height_ratios=[2.2, 1.0]))
LW = 1.2
XLAB = "Lattice rank $m$ (number of Gram–Schmidt layers)"

# ---- A: exact and Padé log2 P_LWE (scaled by 1e8)
l_ex, = axA.plot(M_GRID, 1e8 * EX, color=C_EX, lw=LW, ls="-", label="Exact (erf product)", zorder=3)
l_pa, = axA.plot(M_GRID, 1e8 * PA, color=C_PA, lw=LW, ls=(0, (6, 3)), label="Padé approximation", zorder=4)
axA.set_xlim(5, 60)
axA.set_ylim(-1.4, 0.1)
axA.set_yticks([-1.2, -0.8, -0.4, 0.0])      # explicit: a locator also creates labels outside the view
axA.set_ylabel(r"$\log_2 P_{\mathrm{LWE}}$  ($\times 10^{-8}$)")
# the x axis is shared with B, which carries the printed label; same text here, hidden
axA.set_xlabel(XLAB); axA.xaxis.label.set_visible(False)
legA = axA.legend([l_ex, l_pa], [l_ex.get_label(), l_pa.get_label()], loc="lower left", fontsize=LEG,
                  frameon=False, handlelength=2.2, handletextpad=0.5, labelspacing=0.15,
                  borderaxespad=0.3, borderpad=0.0)

# ---- B: relative error (log axis), drawn only where |log2 P_LWE| > 1e-15
l_re, = axB.plot(M_GRID[DEFINED], REL[DEFINED], color=C_RE, lw=LW, label="Relative error", zorder=3)
axB.set_yscale("log")
axB.set_ylim(5e-4, 5e-1)
axB.set_yticks([1e-3, 1e-2, 1e-1])
axB.yaxis.set_minor_locator(LogLocator(base=10, subs=(2, 5), numticks=10))
axB.yaxis.set_minor_formatter(NullFormatter())
axB.set_ylabel("Relative error")
axB.set_xlabel(XLAB)
axB.set_xticks([10, 20, 30, 40, 50, 60])
axB.xaxis.set_minor_locator(MultipleLocator(5))
# why the curve starts at m = 35 (anti-pattern 11: say it on the plot)
axB.text(6.0, 2.6e-1, "not drawn for $m < %d$:\n$|\\log_2 P_{\\mathrm{LWE}}| < 10^{-15}$\n(double-precision floor)" % M_FIRST,
         fontsize=ANN, color=NOTE_GREY, ha="left", va="top", linespacing=1.15)

scifig.panel_label(axA, "A", x=-0.2, size=9)
scifig.panel_label(axB, "B", x=-0.2, size=9)
fig.align_ylabels([axA, axB])

# ---------------------------------------------------------------- own checks
fig.canvas.draw()
r = fig.canvas.get_renderer()
mm = 25.4 / fig.dpi


def clearance(ax, bb):
    """Smallest distance (mm) between a display-space box and any data curve of the axes."""
    best, who = 1e9, None
    for l in ax.get_lines():
        xy = l.get_transform().transform(np.column_stack([l.get_xdata(), l.get_ydata()]))
        xy = xy[np.isfinite(xy).all(axis=1)]
        if xy.shape[0] < 2:
            continue
        s = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(xy, axis=0).T))])
        si = np.linspace(0, s[-1], 4000)
        xy = np.column_stack([np.interp(si, s, xy[:, 0]), np.interp(si, s, xy[:, 1])])
        dx = np.maximum(np.maximum(bb.x0 - xy[:, 0], 0), xy[:, 0] - bb.x1)
        dy = np.maximum(np.maximum(bb.y0 - xy[:, 1], 0), xy[:, 1] - bb.y1)
        d = float(np.hypot(dx, dy).min()) * mm
        if d < best:
            best, who = d, l.get_label()
    return best, who


bbL = legA.get_window_extent(r)
cl, who = clearance(axA, bbL)
print("A legend: %.2f x %.2f cm; clearance to nearest curve %.2f mm (%s)" % (bbL.width * mm / 10, bbL.height * mm / 10, cl, who))
assert cl >= 1.0, "legend too close to data"
note = [t for t in axB.texts][0]
cl, who = clearance(axB, Text.get_window_extent(note, r))
print("B note: clearance to the error curve %.2f mm (%s)" % (cl, who))
assert cl >= 1.0, "note too close to data"

# per-glyph size check (Fig. 3 method): mathtext parsed with its own font properties
parser = MathTextParser("path")
min_glyph, where = 99.0, ""
for t in fig.findobj(Text):
    s = t.get_text()
    if not s.strip() or not t.get_visible():
        continue
    if "$" in s:
        for part in s.split("\n"):
            if "$" in part:
                res = parser.parse(part, dpi=72, prop=t.get_fontproperties())
                g = min(gl[1] for gl in res.glyphs)
                if g < min_glyph:
                    min_glyph, where = g, part
    elif t.get_fontsize() < min_glyph:
        min_glyph, where = t.get_fontsize(), s
print("glyph check: smallest printed glyph (incl. sub/superscripts) = %.2f pt in %r (need >= 6)" % (min_glyph, where[:40]))
assert min_glyph >= 6.0 - 1e-6, min_glyph

print()
report = scifig.audit(fig, target_width=FIG_W, journal_mode=True)
assert not any(l == "FAIL" for l, _ in report), "audit FAIL"
assert not any(l == "WARN" for l, _ in report), "audit WARN"
scifig.save(fig, os.path.join(HERE, "figS1_final"))
