# -*- coding: utf-8 -*-
"""
FIGURE BRIEF  (Supplementary Fig. S2, final -- label fig:attack_time, SI Note 2-3,
               "Padé-approximated versus exact log2 P_LWE as a function of the BKZ time")
Message (one sentence a referee should take away):
  At the fixed lattice rank m = 500 the Winitzki-Padé closed form of log2 P_LWE (SI Eq.
  pade_log_prob) reproduces the exact erf product (SI Eq. PLWE_final) over log2 T_BKZ = 58-98
  with a relative error below 5e-5 (down to 4e-7), i.e. in the cryptographically relevant
  regime |log2 P_LWE| ~ 3e3-6e3 the approximation is accurate; below log2 T_BKZ = 58 it is not
  evaluated because the smallest error-function arguments underflow double precision.
Reader's first glance should land on:
  the dashed vermilion Padé curve lying on the solid blue exact curve in A from log2 T = 58
  onward, and the relative-error curve in B staying under 1e-4.
Form: line family (two coincident model curves) + one error curve; two stacked panels, shared x.
Panels: A (top) log2 P_LWE (x 1e3) vs log2 T_BKZ: exact over 20-98, Padé over 58-98;
  B (bottom) relative error |log2 P_Padé - log2 P_exact| / |log2 P_exact| on a log axis, 58-98.
Content and arithmetic reproduce the old figure build_v2/Figure/log2Pr_vs_TBKZ.pdf, whose
  script is code_from_D/PQNet/PQNet_Figure/improve/Figure61.py (read-only): same grid
  (log2 T_BKZ = 20, 22, ..., 98), same expression order, same mask (Padé finite, error > 0).
  Styling differences only: no open markers on the model curves (the dash already separates
  the coincident curves), no fill under the error curve, no grid, journal sizes and letters;
  y values of A in units of 10^3 instead of comma-separated thousands.
Encoding table:
  evaluation method -> colour (categorical, fixed order) -> 2
                        exact #0072B2 blue (solid), Padé #D55E00 vermilion (dashed, drawn
                        on top so that both colours stay visible where the curves coincide)
  relative error    -> colour #009E73 green, its own panel (B)                 -> 1
  quantity          -> panel (value / error)                                    -> 2
Curves per panel: A 2, B 1  (all <= 6)
Legend: A, lower right (empty: the curve rises from the lower left to the upper right); B has
  a single series named by its y label, no legend. Direct annotations for the key number only:
  the start of the Padé curve, log2 T_BKZ = 58 (A), and a grey note in B saying why the error
  curve starts there (anti-pattern 11).
Target width: single column 8.5 cm (user), height 7.8 cm. Sizes (Fig. 3 convention): axis
  labels 7.5 pt; tick labels, legend, annotations and notes 7 pt; panel letters 9 pt bold.
  matplotlib._mathtext.SHRINK_FACTOR = 6/7 (as in fig3_final.py / fig5_final.py) so every
  sub/superscript of a 7 pt string prints at 6.0 pt; the script parses every mathtext string
  and asserts that the smallest printed glyph is >= 6 pt.
Palette: Okabe-Ito indices 0, 1, 2 (validated 3-subset of palettes.md); validate_palette ->
  min dE normal 18.7, protan 13.0, deutan 11.0, tritan 8.6: PASS (asserted below).
What could be misread, and how the figure prevents it:
  - "the Padé curve is missing where the curves coincide": dashed vermilion on top of solid
    blue; the legend names both.
  - "the Padé curve / error curve was cut off at the left": the annotation in A marks the
    start at log2 T_BKZ = 58 and the note in B states the reason (underflow of the smallest
    erf arguments in double precision).
  - "log2 P_LWE is of order 1": the y label of A carries the (x 1e3) scale.
  - "this is the Lindner-Peikert calibration": the caption must say illustrative set B (SI
    Table tab:bkz_params): a = 1.8, b = 2.7, m = 500, ||b1|| = 10, d_i = 2, s = 2, not (1.8, 110).

STYLE SELF-REVIEW (references/anti-patterns.md, checked before drawing)
  1  shades of one hue ......... no: three distinct Okabe-Ito hues.
  2  dash as the only cue ...... no: the dashed curve also differs in hue; the dash is what
                                 keeps the underlying solid curve visible (coincident curves).
  3/4 > 6 curves / big legend .. no: 2 + 1 curves; a two-entry legend in an empty corner.
  5  text < 6 pt ............... no: audit asserts >= 6 pt; own glyph check covers sub/superscripts.
  6  in-panel titles ........... none (journal mode); the caption carries the title.
  11 curve stops unexplained ... no: annotation in A and note in B explain the start at 58.
  12 unit-less axes ............ x label states that T_BKZ is in seconds; log2 P_LWE is
                                 dimensionless with the scale in the label; relative error too.
  13 colour per entity ......... exact = blue, Padé = vermilion in S1 and S2 alike.
  14 frames / grids ............ top/right spines off, no grid, no fills.
  15 paragraphs in the figure .. one two-line annotation and one two-line note.
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
# Illustrative set B of SI Table tab:bkz_params, as stated in the caption of fig:attack_time.
A, B = 1.8, 2.7            # BKZ runtime fit  log2 delta_root = a / (log2 T_BKZ + b)
M = 500                    # lattice rank (number of Gram-Schmidt layers), fixed
B1, DI, S = 10.0, 2.0, 2.0  # ||b1||, search width d_i, Gaussian parameter s
W_PADE = 0.140012          # Winitzki's constant w
L_GRID = np.arange(20, 100, 2, dtype=float)  # log2 T_BKZ = 20, 22, ..., 98 (T_BKZ in s)
FLOOR = 1e-15

# The two evaluations keep the expression order of the original script (improve/Figure61.py).


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
    """SI Eq. pade_log_prob: sum_i log2 sqrt(1 - exp(-W_i (4/pi + w W_i)/(1 + w W_i))), W_i = z_i^2.
    For the smallest z_i the term 1 - exp(-x) underflows to 0 in double precision and that
    layer contributes log2(0) = -inf: the sum is then -inf (not evaluated)."""
    gamma, lam = _gamma_lambda(log2T)
    i = np.arange(1, m + 1)
    W = (DI ** 2) * (lam ** 2) * 2.0 ** (-2.0 * gamma * (i - 1))
    with np.errstate(divide="ignore"):
        return float(np.sum(np.log2(np.sqrt(1.0 - np.exp(-(W * (4.0 / np.pi + W_PADE * W)) / (1.0 + W_PADE * W))))))


EX = np.array([log2p_exact(M, l) for l in L_GRID])
PA = np.array([log2p_pade(M, l) for l in L_GRID])
FINITE = np.isfinite(PA)
with np.errstate(divide="ignore", invalid="ignore"):
    REL = np.where(FINITE, np.abs((PA - EX) / EX), np.nan)
DEFINED = FINITE & (np.abs(EX) > FLOOR) & (REL > 0)
L_FIRST = float(L_GRID[DEFINED][0])

# ---------------------------------------------------------------- checks against the old figure
print("== Supplementary Fig. S2 (fig:attack_time): values read off build_v2/Figure/log2Pr_vs_TBKZ.pdf ==")
print("exact log2 P_LWE: %.2f at log2 T = 20, %.2f at 98 (old figure: about -18,000 / -3,000)" % (EX[0], EX[-1]))
assert abs(EX[0] - (-18162.15)) < 0.1 and abs(EX[-1] - (-2965.96)) < 0.1
print("Padé finite from log2 T_BKZ = %g onward (caption: ~58); -inf below" % L_GRID[FINITE][0])
assert L_FIRST == 58.0 and L_GRID[FINITE][0] == 58.0 and np.all(np.isinf(PA[~FINITE]))
k_min = int(np.nanargmin(REL))
print("relative error: %.3e at 58, min %.3e at %g, %.3e at 98; max %.3e" % (REL[DEFINED][0], REL[k_min], L_GRID[k_min], REL[-1], np.nanmax(REL)))
assert abs(REL[DEFINED][0] - 4.393e-5) < 1e-7 and L_GRID[k_min] == 62 and abs(REL[k_min] - 3.573e-7) < 1e-9
assert abs(REL[-1] - 6.131e-6) < 1e-8 and np.nanmax(REL) < 5e-5

np.savetxt(os.path.join(HERE, "figS2_final_source_data.csv"),
           np.column_stack([L_GRID, EX, np.where(FINITE, PA, np.nan), np.where(DEFINED, REL, np.nan)]), delimiter=",",
           fmt=["%g", "%.10e", "%.10e", "%.6e"],
           header=("log2_T_BKZ_s,log2P_LWE_exact,log2P_LWE_pade,relative_error "
                   "(a=%g,b=%g,m=%d,||b1||=%g,d_i=%g,s=%g,w=%g; double precision; "
                   "relative_error = |pade-exact|/|exact|; nan where the Pade sum underflows (log2 T_BKZ < 58))"
                   % (A, B, M, B1, DI, S, W_PADE)), encoding="utf-8")

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
XLAB = r"BKZ time $\log_2 T_{\mathrm{BKZ}}$  ($T_{\mathrm{BKZ}}$ in s)"

# ---- A: exact (20-98) and Padé (58-98) log2 P_LWE, scaled by 1e-3
l_ex, = axA.plot(L_GRID, 1e-3 * EX, color=C_EX, lw=LW, ls="-", label="Exact (erf product)", zorder=3)
l_pa, = axA.plot(L_GRID[FINITE], 1e-3 * PA[FINITE], color=C_PA, lw=LW, ls=(0, (6, 3)), label="Padé approximation", zorder=4)
axA.set_xlim(20, 98)
axA.set_ylim(-19.5, -2.0)
axA.set_yticks([-16, -12, -8, -4])           # explicit: a locator also creates labels outside the view
axA.set_ylabel(r"$\log_2 P_{\mathrm{LWE}}$  ($\times 10^{3}$)")
axA.set_xlabel(XLAB); axA.xaxis.label.set_visible(False)      # printed on B (shared axis)
# the key number: where the Padé curve starts
y58 = 1e-3 * PA[FINITE][0]
axA.annotate("Padé evaluated from\n$\\log_2 T_{\\mathrm{BKZ}} = %g$" % L_FIRST, xy=(L_FIRST, y58), xytext=(62.0, -9.6),
             fontsize=ANN, color=C_PA, ha="left", va="top", linespacing=1.15,
             arrowprops=dict(arrowstyle="-", color=C_PA, lw=0.5, shrinkB=2.5))
legA = axA.legend([l_ex, l_pa], [l_ex.get_label(), l_pa.get_label()], loc="lower right", fontsize=LEG,
                  frameon=False, handlelength=2.2, handletextpad=0.5, labelspacing=0.15,
                  borderaxespad=0.3, borderpad=0.0)

# ---- B: relative error (log axis), 58-98
l_re, = axB.plot(L_GRID[DEFINED], REL[DEFINED], color=C_RE, lw=LW, label="Relative error", zorder=3)
axB.set_yscale("log")
axB.set_ylim(1e-7, 2e-4)
axB.set_yticks([1e-7, 1e-6, 1e-5, 1e-4])
axB.yaxis.set_minor_locator(LogLocator(base=10, subs=(2, 5), numticks=10))
axB.yaxis.set_minor_formatter(NullFormatter())
axB.set_ylabel("Relative error")
axB.set_xlabel(XLAB)
axB.set_xticks([20, 40, 60, 80])
axB.xaxis.set_minor_locator(MultipleLocator(10))
# why the curve starts at 58 (anti-pattern 11: say it on the plot); fits left of log2 T = 56
axB.text(21.0, 1.1e-4, "not evaluated\nbelow %g: the erf\narguments underflow" % L_FIRST,
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
ann = [t for t in axA.texts][0]
# Annotation.get_window_extent includes the leader line, which by construction ends on the
# curve; measure the text box alone (the leader's end is shrinkB = 2.5 pt from the curve).
cl, who = clearance(axA, Text.get_window_extent(ann, r))
print("A annotation text: clearance to nearest curve %.2f mm (%s)" % (cl, who))
assert cl >= 1.0, "annotation too close to data"
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
scifig.save(fig, os.path.join(HERE, "figS2_final"))
