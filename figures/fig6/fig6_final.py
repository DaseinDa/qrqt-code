# -*- coding: utf-8 -*-
"""
FIGURE BRIEF (Fig. 6, FINAL draft -- corrected Holevo quantity, option (a); journal figure)
Status: final (approved 2026-11-03; README.md). Derived from variant_A/fig6_variantA.py (judges'
  winner) with the judges' three ranked edits applied; formula, numbers and layout unchanged.
Message (one sentence a referee should take away): under amplitude damping of Bob's half
  of the Bell pair, the Holevo quantity chi of the four Bell-outcome-conditioned states
  falls monotonically from 1 bit at gamma = 0 to 0 at gamma = 1 and, at fixed gamma, is
  symmetric in the input weight |alpha|^2 about 1/2.
Reader's first glance should land on: panel A, three nearly coincident curves falling to
  the marked point chi(1) = 0; panel B, three arches mirrored about the dotted guide at
  |alpha|^2 = 1/2.
Form: line family (two panels, side by side).
Panels: 2 (A: chi vs gamma, family |alpha|^2; B: chi vs |alpha|^2, family gamma);
  shared y axis (0 to 1.05 bit), both x axes span [0, 1], both x quantities dimensionless.
Encoding table:
  |alpha|^2 (panel A family) -> colour, Okabe-Ito 0,1,2 (blue, vermilion, green)       -> 3
  gamma     (panel B family) -> colour, magenta #AA3377 (Tol bright), mustard #E6AB02
                                (ColorBrewer Dark2), cyan #33BBEE (Tol vibrant)         -> 3
      (the three panel-B hues sit between the three panel-A hues on the hue wheel, so no
       hue is near-duplicated across panels; all six are validated TOGETHER, see Palette.
       Variant A's purple/orange/sky failed that joint check: green-purple deutan 7.6.)
  swept variable -> panel; linestyle unused (all solid 1.2 pt)
Curves per panel: 3.
Direct labels or legend? Conventional legends (user rule 2026-10-21: every figure carries
  a legend; label blocks / line-end labels alone are not accepted). A: compact legend
  "|alpha|^2 = 0.5 / 0.3 / 0.1", entries top to bottom in curve order, in the empty
  upper-right region (the three curves end at the same point (1, 0) and the 0.3 / 0.5
  curves are < 0.03 bit apart, so no leader could reach the 0.3 curve without crossing a
  neighbour -- judges' defect 1). B: compact legend "gamma = 0.1 / 0.3 / 0.5" in curve
  order, lower right below the gamma = 0.5 curve and to the right of the dotted guide.
  Both legends are asserted to cover no data point and not to straddle the guide.
Target width: 1.5 column (12 cm x 5.5 cm); 7 pt body, 6 pt ticks, 6.5 pt annotations,
  9 pt bold panel letters (A, B -- Science Advances). No in-panel titles.
Palette: ALL SIX hues validated together with scifig.validate_palette (asserted at run
  time): min dE normal 18.5 (vermilion-mustard), min dE CVD 8.6 (blue-green under tritan,
  a pair inside panel A that is the paper's fixed |alpha|^2 colour map) -> PASS.
  Cross-panel pairs alone: min normal 18.5, min CVD 10.3 (variant A: 15.6 / 7.6 FAIL).
What could be misread, and how the figure prevents it:
  - "the curves in A coincide, is that a plotting error?" -> they are the data: the 0.5
    and 0.3 curves differ by at most 0.020 bit (at gamma = 0.5); the legend lists the
    entries in the stacking order, and the caption must say the two differ by less than
    about 0.03 bit so that no visible separation is expected.
  - "does chi really vanish at gamma = 1?" -> open marker + text "chi(1) = 0".
  - "is B symmetric or just flat?" -> dotted guide at 1/2, visible in print (#777777,
    0.65 pt, coarse round dots) and labelled "symmetric about 1/2"; the arches' equal
    end values at |alpha|^2 = 0 and 1 are visible.
  - "gamma and |alpha|^2 have units?" -> "(dimensionless)" written in both x-labels.
  - The status is stated in README.md only, not in the figure.
Data: computed here from the corrected closed form (Eq. holevo-final of r3_proposal.tex)
  chi(gamma, |alpha|^2) = h(gamma) - [h(delta_beta) + h(delta_alpha)]/2,
  delta_x = sqrt(1 - 4 gamma (1-gamma) |x|^4), h(x) = H_2((1+x)/2);
  asserted against holevo/holevo_correct.py (closed form AND the 3-qubit simulation)
  and against the quoted values 0.832 / 0.620 / 0.452 bit at |alpha|^2 = 0.6, gamma =
  0.1 / 0.3 / 0.5; chi(gamma = 1) = 0.
"""
import os
import sys
sys.dont_write_bytecode = True   # never leave a __pycache__ in holevo/ or the skill folder

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

if hasattr(sys.stdout, "reconfigure"):            # Windows console / redirected stdout
    sys.stdout.reconfigure(encoding="utf-8")

_REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(_REPO, "tools"))
sys.path.insert(0, os.path.join(_REPO, "holevo"))
import scifig  # noqa: E402
import holevo_correct as hc  # noqa: E402  (read-only import; nothing there is modified)

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(OUT_DIR, "fig6_final")

# ----------------------------------------------------------------------------- data


def h(x):
    """Manuscript h(x) = H_2((1+x)/2); h(0) = 1, h(1) = 0."""
    x = np.clip(np.asarray(x, dtype=float), 0.0, 1.0)
    out = np.zeros_like(x)
    for v in ((1 + x) / 2, (1 - x) / 2):
        m = v > 0
        out[m] -= v[m] * np.log2(v[m])
    return out


def chi_cor(g, a2):
    """Corrected chi(gamma, |alpha|^2), Eq. holevo-final (option (a))."""
    g, a2 = np.asarray(g, float), np.asarray(a2, float)
    d_beta = np.sqrt(np.clip(1 - 4 * g * (1 - g) * (1 - a2) ** 2, 0, 1))
    d_alpha = np.sqrt(np.clip(1 - 4 * g * (1 - g) * a2 ** 2, 0, 1))
    return h(g) - 0.5 * (h(d_beta) + h(d_alpha))


x = np.linspace(0.0, 1.0, 1001)
LEVELS = (0.1, 0.3, 0.5)

# --- assertions on the stated values and limits (before plotting) -------------------
_g = np.array([0.1, 0.3, 0.5, 0.9, 1.0])
assert np.allclose(chi_cor(_g, 0.6), [0.832, 0.620, 0.452, 0.126, 0.000], atol=1.5e-3), chi_cor(_g, 0.6)
for a2 in LEVELS + (0.6, 0.0, 1.0):
    y = chi_cor(x, a2)
    assert abs(y[0] - 1.0) < 1e-12, "chi(0) must be 1 bit"
    assert abs(y[-1]) < 1e-12, "chi(1) must be 0"
    assert np.all(np.diff(y) <= 1e-12), "chi must decrease monotonically in gamma"
    assert np.all((y >= -1e-12) & (y <= 1 + 1e-12))
for g in LEVELS:
    y = chi_cor(g, x)
    assert np.allclose(y, y[::-1], atol=1e-12), "chi must be symmetric about |alpha|^2 = 1/2"
    assert np.argmax(y) == 500, "maximum must sit at |alpha|^2 = 1/2"
    assert abs(y[0] - (h(g) - 0.5 * h(abs(1 - 2 * g)))) < 1e-12, "end value h(g) - h(|1-2g|)/2"
# family ordering in A: at every gamma in (0,1), chi(0.5) >= chi(0.3) >= chi(0.1)
assert np.all(chi_cor(x[1:-1], 0.5) >= chi_cor(x[1:-1], 0.3) - 1e-12)
assert np.all(chi_cor(x[1:-1], 0.3) >= chi_cor(x[1:-1], 0.1) - 1e-12)
# caption statement: the 0.3 and 0.5 curves differ by less than about 0.03 bit
GAP_53 = float(np.max(chi_cor(x, 0.5) - chi_cor(x, 0.3)))
assert GAP_53 < 0.03, GAP_53

# --- cross-check against holevo_correct.py: closed form and 3-qubit simulation --------
for a2 in (0.1, 0.3, 0.5, 0.6):
    al, be = np.sqrt(a2), np.sqrt(1 - a2)
    assert np.allclose(chi_cor(x, a2), hc.chi_K_closed(al, be, x)["empty"], atol=1e-12)
    for g in (0.0, 0.1, 0.3, 0.5, 0.9, 1.0):
        chi_sim = hc.chi_K_sim(al, be, g)[0]["empty"]
        assert abs(chi_sim - float(chi_cor(g, a2))) < 1e-9, (a2, g, chi_sim, chi_cor(g, a2))
print("data assertions passed: chi(0)=1, chi(1)=0, monotone in gamma, symmetric about 1/2,")
print("  quoted values at |alpha|^2=0.6 reproduced (0.832/0.620/0.452 bit),")
print("  closed form == holevo_correct.chi_K_closed (1e-12) == chi_K_sim 3-qubit simulation (1e-9),")
print("  max |chi(0.5) - chi(0.3)| = %.4f bit (< 0.03, caption statement)" % GAP_53)

# ----------------------------------------------------------------------------- colours
COL_ALPHA = scifig.OKABE_ITO[0:3]                 # |alpha|^2 family (panel A): blue, vermilion, green
COL_GAMMA = ["#AA3377", "#E6AB02", "#33BBEE"]     # gamma family (panel B): magenta, mustard, cyan
SIX = COL_ALPHA + COL_GAMMA
print("palette: panel A (|alpha|^2 = 0.1/0.3/0.5) =", COL_ALPHA)
print("palette: panel B (gamma = 0.1/0.3/0.5)     =", COL_GAMMA)
print("--- all six hues of both panels together ---")
REP6 = scifig.validate_palette(SIX)
assert REP6["pass"], "six-colour palette failed the validator"
_CVD = ("protan", "deutan", "tritan")
_cross = [(a, b) for a in COL_ALPHA for b in COL_GAMMA]
XN = min(scifig.delta_e(a, b) for a, b in _cross)
XC = min(scifig.delta_e(a, b, m) for a, b in _cross for m in _CVD)
print("cross-panel pairs only: min dE normal %.1f (>=15), min dE CVD %.1f (>=8)" % (XN, XC))
assert XN >= 15 and XC >= 8

# ----------------------------------------------------------------------------- figure
W, H = scifig.setup(width="onehalf", aspect=0.46)          # 12.0 x 5.5 cm
fig, (axA, axB) = plt.subplots(1, 2, figsize=(W, H), sharey=True)

GREY, GUIDE = "#555555", "#777777"
ALPHA2, GAMMA, CHI = "|\u03b1|\u00b2", "\u03b3", "\u03c7"
LAB = matplotlib.rcParams["axes.labelsize"]


def plot_family(ax, sweep_is_gamma, colors):
    lines = []
    for lev, col in zip(LEVELS, colors):
        y = chi_cor(x, lev) if sweep_is_gamma else chi_cor(lev, x)
        (l,) = ax.plot(x, y, color=col, lw=1.2, solid_capstyle="round", label="_%.1f" % lev)
        lines.append(l)
    return lines


def assert_clear_of_curves(ax, texts, lines, pad_pt=1.0):
    """Every text box (plus pad) must contain no point of any data curve."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    pad = pad_pt / 72.0 * fig.dpi
    for t in texts:
        bb = t.get_window_extent(r)
        for l in lines:
            xy = ax.transData.transform(np.column_stack([l.get_xdata(), l.get_ydata()]))
            inside = ((xy[:, 0] >= bb.x0 - pad) & (xy[:, 0] <= bb.x1 + pad) &
                      (xy[:, 1] >= bb.y0 - pad) & (xy[:, 1] <= bb.y1 + pad))
            assert not inside.any(), "label %r collides with curve %s" % (t.get_text(), l.get_label())


TICKS = [0, 0.25, 0.5, 0.75, 1.0]
TICKLAB = ["0", "0.25", "0.5", "0.75", "1"]

# --- Panel A: chi vs gamma, family = |alpha|^2 ------------------------------------
la = plot_family(axA, True, COL_ALPHA)
axA.set_xlim(0, 1); axA.set_ylim(0, 1.05)
axA.set_xticks(TICKS); axA.set_xticklabels(TICKLAB)
axA.set_yticks(TICKS); axA.set_yticklabels(TICKLAB)
axA.set_xlabel("damping %s (dimensionless)" % GAMMA)
axA.set_ylabel("Holevo %s (bits)" % CHI)
# Conventional legend (user rule 2026-10-21) in the empty upper-right region, entries top
# to bottom in curve order (0.5 on top, 0.3 just below, 0.1 lowest -- ordering asserted
# above); covers no data (checked by the audit and by assert_legend_clear below).
for l, lev in zip(la, LEVELS):
    l.set_label("%s = %.1f" % (ALPHA2, lev))
legA = axA.legend(handles=la[::-1], loc="upper right", bbox_to_anchor=(1.0, 0.88),
                  fontsize=LAB - 0.5, handlelength=1.8, labelspacing=0.3, borderaxespad=0.0)
# the limit that matters: chi(1) = 0
axA.plot([1.0], [0.0], marker="o", ms=2.8, mfc="white", mec=GREY, mew=0.6, ls="None",
         zorder=5, clip_on=False)
# label in the empty region under the curves (they lie above 0.15 bit for gamma < 0.8),
# with a thin grey leader running below the curves to the marked point (1, 0)
t_chi1 = axA.text(0.78, 0.035, "%s(1) = 0" % CHI, color=GREY, ha="right", va="bottom",
                  clip_on=False, fontsize=LAB - 0.5, zorder=6)
axA.annotate("", xy=(1.0, 0.0), xytext=(0.795, 0.045), textcoords="data", zorder=4,
             arrowprops=dict(arrowstyle="-", color=GREY, lw=0.5, shrinkA=0, shrinkB=2.0))

# --- Panel B: chi vs |alpha|^2, family = gamma -------------------------------------
lb = plot_family(axB, False, COL_GAMMA)
axB.set_xlim(0, 1); axB.set_ylim(0, 1.05)
axB.set_xticks(TICKS); axB.set_xticklabels(TICKLAB)
axB.set_xlabel("input weight %s (dimensionless)" % ALPHA2)
axB.set_ylabel(axA.get_ylabel())            # shared y axis: label recorded, drawn once (on A)
axB.yaxis.label.set_visible(False)
axB.tick_params(labelleft=False)
# symmetry guide: mid grey, 0.65 pt, coarse round dots -> visible in print (judges' edit 2)
axB.vlines(0.5, 0, 0.90, color=GUIDE, lw=0.65, ls=(0, (1.0, 3.0)), capstyle="round", zorder=0)
t_sym = axB.text(0.5, 0.93, "symmetric about \u00bd", color=GREY, ha="center", va="bottom",
                 fontsize=LAB - 0.5)
for l, lev in zip(lb, LEVELS):
    l.set_label("%s = %.1f" % (GAMMA, lev))
# Conventional legend (user rule 2026-10-21) in the empty lower-right region below the
# gamma = 0.5 curve, entries in curve order (0.1 on top), kept right of the dotted guide.
legB = axB.legend(handles=lb, loc="lower center", bbox_to_anchor=(0.74, 0.02),
                  fontsize=LAB - 0.5, handlelength=1.8, labelspacing=0.3, borderaxespad=0.0)

scifig.panel_label(axA, "A", x=-0.20)
scifig.panel_label(axB, "B", x=-0.06)

# every in-panel label must sit clear of every curve (the audit only checks legend boxes)
assert_clear_of_curves(axA, [t_chi1], la)
assert_clear_of_curves(axB, [t_sym], lb)


def assert_legend_clear(tag, ax, leg, lines, pad_pt=1.0, avoid_x=None):
    """The legend box (plus pad) must contain no point of any data curve and, if avoid_x
    is given, must not straddle the vertical guide drawn at that data x. Prints the box
    in data units and the distance to the nearest curve so the clearance is on record."""
    fig.canvas.draw()
    bb = leg.get_window_extent(fig.canvas.get_renderer())
    pad = pad_pt / 72.0 * fig.dpi
    gaps = []
    for l in lines:
        xy = ax.transData.transform(np.column_stack([l.get_xdata(), l.get_ydata()]))
        inside = ((xy[:, 0] >= bb.x0 - pad) & (xy[:, 0] <= bb.x1 + pad) &
                  (xy[:, 1] >= bb.y0 - pad) & (xy[:, 1] <= bb.y1 + pad))
        assert not inside.any(), "%s: legend covers curve %s" % (tag, l.get_label())
        m = (xy[:, 0] >= bb.x0) & (xy[:, 0] <= bb.x1)
        if m.any():
            gaps.append(np.min(np.abs(xy[m, 1] - np.clip(xy[m, 1], bb.y0, bb.y1))))
    if avoid_x is not None:
        px = ax.transData.transform((avoid_x, 0))[0]
        assert not (bb.x0 - pad <= px <= bb.x1 + pad), "%s: legend straddles the guide" % tag
    inv = ax.transData.inverted()
    (x0, y0), (x1, y1) = inv.transform([(bb.x0, bb.y0), (bb.x1, bb.y1)])
    gap_bit = (min(gaps) / fig.dpi * 2.54) / (ax.bbox.height / fig.dpi * 2.54) * np.diff(ax.get_ylim())[0] if gaps else float("inf")
    print("%s: legend box x = [%.2f, %.2f], chi = [%.2f, %.2f]; nearest curve %.3f bit away"
          % (tag, x0, x1, y0, y1, gap_bit))


assert_legend_clear("panel A", axA, legA, la)
assert_legend_clear("panel B", axB, legB, lb, avoid_x=0.5)

# ----------------------------------------------------------------------------- audit + save
report = scifig.audit(fig, target_width="onehalf", journal_mode=True)
N_FAIL = sum(1 for lvl, _ in report if lvl == "FAIL")
N_WARN = sum(1 for lvl, _ in report if lvl == "WARN")
assert N_FAIL == 0 and N_WARN == 0, "audit reported %d FAIL, %d WARN" % (N_FAIL, N_WARN)
scifig.save(fig, OUT)

# ----------------------------------------------------------------------------- source data
hdr = ("# Fig. 6 (final draft) source data: chi = h(gamma) - [h(delta_beta)+h(delta_alpha)]/2, "
       "delta_x = sqrt(1-4 gamma(1-gamma)|x|^4), h(x) = H2((1+x)/2); "
       "asserted equal (1e-9) to the 3-qubit simulation in holevo_correct.py\n")
with open(os.path.join(OUT_DIR, "fig6_final_panelA.csv"), "w", encoding="utf-8") as f:
    f.write(hdr + "gamma,alpha_sq,chi_bits\n")
    for lev in LEVELS:
        for g, c in zip(x, chi_cor(x, lev)):
            f.write("%.4f,%.2f,%.10f\n" % (g, lev, c))
with open(os.path.join(OUT_DIR, "fig6_final_panelB.csv"), "w", encoding="utf-8") as f:
    f.write(hdr + "alpha_sq,gamma,chi_bits\n")
    for lev in LEVELS:
        for a2, c in zip(x, chi_cor(lev, x)):
            f.write("%.4f,%.2f,%.10f\n" % (a2, lev, c))
print("source data written: fig6_final_panelA.csv, fig6_final_panelB.csv")
