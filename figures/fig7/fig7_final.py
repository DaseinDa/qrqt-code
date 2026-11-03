# -*- coding: utf-8 -*-
"""fig7_final.py -- Fig. 7 (stochastic leakage of the correction bits), FINAL, corrected closed forms.

Run:  MPLBACKEND=Agg python fig7_final.py
Writes into this folder only: fig7_final.pdf / .png (600 dpi), fig7_final_source_data.csv, audit.txt,
and the four single-panel SI versions fig7_panelA..D.pdf / .png (1 column, 8.5 cm).
Inputs (read-only): ../../../holevo/holevo_correct.py (closed forms + 3-qubit density-matrix simulation),
../../../holevo/fig7_*_prototype.csv (cross-check of the Holevo and max-overlap columns).
Metric: E[F_lambda](t) (maximal overlap, the approved metric), NOT the Haar-averaged F-bar.

FIGURE BRIEF
Message (one sentence a referee should take away):
  As the correction bits leak, the information E[chi(t)] that Eve can still extract about the
  unrevealed bits decays from chi_empty (1 / 0.832 / 0.717 / 0.620 bit for gamma = 0 / 0.1 / 0.2 / 0.3)
  toward zero while her maximal overlap F(t) with Bob's state rises from (1+gamma)/2 toward
  F_{12} = 1.000 / 0.976 / 0.956 / 0.941; because the start value rises with gamma and the asymptote
  falls, the F(t) curves cross (t = 0.65-1.50/k independent, 1.35-2.82/k sequential, 1.12-1.48/k
  burst), whereas in the correlated model the correlation strength mu has no visible effect.
Reader's first glance should land on:
  the four falling chi curves fanning out at t = 0 in A-C, the four rising F curves crossing inside the
  shaded window below them, and the single visible curve in D with the note that the four mu curves
  coincide.
Form: line families; 2 x 2 panels, each panel = two stacked subplots with a shared time axis
  (top E[chi(t)], bottom F(t)).
Panels: A independent exponential leakage (k1 = k2 = 1); B sequential leakage (k1 = k2 = 1);
  C burst leakage (k = 1); D correlated leakage (k = 1, gamma = 0.5). Identical axes in all panels
  (t in [0, 5] units of 1/k; chi in [0, 1.02] bit; F in [0.47, 1.02]). Leakage model -> panel.
Encoding table:
  gamma (A-C family)  -> colour, categorical, fixed order, same hue for the same gamma in A, B, C -> 4:
                         gamma = 0 #0072B2 blue, 0.1 #D55E00 vermilion, 0.2 #009E73 green,
                         0.3 #AA3377 magenta  (the first four hues of the paper's validated six-set)
  mu (D family)       -> colour, categorical, a DISTINCT set, never shown beside the gamma set -> 4:
                         mu = 0 #33BBEE cyan, 0.3 #AAAA00 olive, 0.6 #F781BF pink, 0.9 #332288 indigo
  model               -> panel; quantity (chi / F) -> subplot row; linestyle unused (all solid 1.2 pt)
  crossing window     -> light grey band in the F subplot + the two numbers written beside it
Curves per subplot: 4.
Legend: one compact legend per panel (upper right of the top subplot, the empty region above the
  decaying chi curves), entries in curve order; direct annotations only for the key numbers (crossing
  window t_min-t_max in A-C; "four curves coincide (within 0.002 bit / 0.001)" in D).
Panel D insets (coordinator's refinement): each D subplot carries a framed zoom inset (40 % x 56 % of
  the subplot, in the empty region: upper middle of the chi subplot, lower right of the F subplot)
  showing the window t = 0.65-0.67/k around the point of largest mu-dependence (t = 0.664/k), with a
  tight y range (chi 0.2305-0.2385 bit, ticks 0.232 / 0.235 / 0.238; F 0.8349-0.8377, ticks 0.835 /
  0.836 / 0.837) in which the four curves are 2-3 pt apart; same four colours, no legend; an open
  marker on the main curve at t = 0.66 and a thin grey connector to the inset's lower-left corner; the
  inset's y ticks sit on its right so that the connector corner is free of tick labels.
Target width: double column, 18.3 cm x 14.0 cm; 7 pt axis labels, 6 pt ticks, 6.5 pt legend and
  annotations, 9 pt bold panel letters A-D (Science Advances); mathtext has no sub/superscripts, and
  SHRINK_FACTOR = 6/7 is set anyway so that any would be >= 6 pt. SI versions: 8.5 cm x 7.8 cm, same
  sizes, own legend, no panel letter.
Palette: all EIGHT hues validated together at run time (scifig.validate_palette, asserted PASS):
  within the gamma set the weakest pair is blue-green under tritanopia (8.6 >= 8, the paper's fixed
  pair); within the mu set min dE normal >= 15 and CVD >= 8; every cross-set pair also passes
  (min normalised margin 1.08). An exhaustive search over 46 candidate hues found no passing
  eight-colour set that contains Fig. 6's gamma hues (magenta #AA3377 for 0.1 AND mustard #E6AB02
  for 0.3), so the gamma -> colour map of Fig. 7 cannot be made identical to Fig. 6's {0.1, 0.3,
  0.5} map; Fig. 7 therefore carries its own fixed gamma map (documented in CAPTION_NOTE.md).
What could be misread, and how the figure prevents it:
  - "only one curve in D -- plotting error?" -> annotation in both D subplots: the four mu curves
    coincide (they differ by < 0.002 bit and < 0.001); the legend still lists the four entries.
  - "do the F curves really cross?" -> shaded window with the crossing interval written beside it,
    computed by bisection from the closed forms and asserted against the text's numbers.
  - "why does F start above 1/2?" -> F(0) = (1+gamma)/2 is visible on the axis; the caption must say
    it is the maximal overlap (largest eigenvalue of Eve's averaged state), which rewards the bias
    of the damped qubit toward |0>, not a reconstruction fidelity.
  - "are both subplots evaluated at the same input?" -> yes, fixed |alpha|^2 = 0.6 for chi AND F
    (the Haar-averaged F-bar is not plotted); the caption must say so.
  - units: chi in bits, t in units of 1/k, F dimensionless -- all in the axis labels.
Style self-review against references/anti-patterns.md: 1 (shades of one hue) no, eight distinct
  validated hues; 2 (dash vs solid families) no linestyles; 3 (> 6 curves) four per subplot;
  4 (legend covering data) legends sit above the decaying chi curves, clearance asserted; 5 (< 6 pt)
  none, checked incl. mathtext glyphs; 6 (in-panel titles) none; 8 (colour = version and parameter)
  model is a panel; 10 (inset) none; 11 (off-scale) none; 12 (units) all axes; 13 (same entity, same
  colour) one gamma map for A-C, mu map only in D, cross-figure note in CAPTION_NOTE.md; 15 (prose)
  only two short annotations per panel; 21/22 (user rules) own hue per series, legend in every panel.
Data: computed here from the manuscript's closed forms (r4_proposal.tex Eqs. leak-indep ... leak-corr,
  leakage-expected; si_v2/holevo_07_proposal.tex chi_K and F_K), asserted equal to
  holevo/holevo_correct.py (closed forms, 1e-12) and to its 3-qubit density-matrix simulation
  (chi_K_sim, F_lam_sim; 1e-9) at a coarse t subsample; the quoted numbers of the text are asserted.
"""
from __future__ import annotations

import csv
import io
import itertools
import math
import os
import sys

sys.dont_write_bytecode = True   # never leave a __pycache__ in holevo/ or the skill folder

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib._mathtext as _mathtext
# Sub/superscripts: matplotlib shrinks them to 0.70 of the base size (7 pt -> 4.9 pt, below the 6 pt production
# minimum).  Use 6/7 instead so that every sub/superscript of a 7 pt string is exactly 6 pt (fig3_final.py).
_mathtext.SHRINK_FACTOR = 6.0 / 7.0
_mathtext.GROW_FACTOR = 1.0 / _mathtext.SHRINK_FACTOR
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.mathtext import MathTextParser
from matplotlib.text import Text

HERE = os.path.dirname(os.path.abspath(__file__))           # <repo>/figures/fig7
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))     # repository root
SKILL_SCRIPTS = os.path.join(REPO, "tools")                 # scifig.py
WORK = REPO
sys.path.insert(0, SKILL_SCRIPTS)
sys.path.insert(0, os.path.join(WORK, "holevo"))
import scifig  # noqa: E402
import holevo_correct as hc  # noqa: E402  (read-only import; nothing there is modified)

OUT = HERE
os.makedirs(OUT, exist_ok=True)


class _Tee(io.TextIOBase):
    """Duplicate stdout into audit.txt (the script's complete console output)."""

    def __init__(self, path):
        self.f = open(path, "w", encoding="utf-8")
        self.o = sys.stdout
        try:
            self.o.reconfigure(errors="replace")
        except Exception:
            pass

    def write(self, s):
        self.o.write(s); self.f.write(s); return len(s)

    def flush(self):
        self.o.flush(); self.f.flush()


sys.stdout = _Tee(os.path.join(OUT, "audit.txt"))

# ----------------------------------------------------------------------------
# 1. Model inputs (decided: r4_proposal.tex / DECISIONS_round3) and the closed forms, re-typed from the
#    manuscript (independent of holevo_correct.py, which is used only to CHECK them below)
# ----------------------------------------------------------------------------
A2, B2 = 0.6, 0.4                      # |alpha|^2, |beta|^2 (alpha = sqrt(0.6), beta = sqrt(0.4), real)
AL, BE = math.sqrt(A2), math.sqrt(B2)
K_RATE = 1.0                           # k1 = k2 = k = 1 (time in units of 1/k)
GAMMAS = (0.0, 0.1, 0.2, 0.3)          # panels A-C
MUS = (0.0, 0.3, 0.6, 0.9)             # panel D
GAMMA_D = 0.5                          # panel D damping
T = np.linspace(0.0, 5.0, 501)         # plotted and written time grid (step 0.01/k)
KEYS = ("empty", "1", "2", "12")


def H2(p):
    p = np.asarray(p, dtype=float)
    out = np.zeros_like(p)
    m = (p > 0) & (p < 1)
    out[m] = -p[m] * np.log2(p[m]) - (1 - p[m]) * np.log2(1 - p[m])
    return out


def h(x):
    """Manuscript h(x) = H_2((1+x)/2); h(0) = 1, h(1) = 0."""
    return H2((1.0 + np.clip(np.abs(np.asarray(x, dtype=float)), 0.0, 1.0)) / 2.0)


def class_values(g):
    """chi_K (bits) and F_K (maximal overlap) for the four knowledge classes at damping g,
    SI Note holevo_07 Eqs. chi-K / F-K (corrected forms), input |alpha|^2 = 0.6."""
    d_beta = math.sqrt(1 - 4 * g * (1 - g) * B2 ** 2)
    d_alpha = math.sqrt(1 - 4 * g * (1 - g) * A2 ** 2)
    a = A2 + g * B2
    ap = B2 + g * A2
    r = AL * BE * math.sqrt(1 - g)                      # Re(alpha beta*) sqrt(1-gamma), real amplitudes
    S_ind = 0.5 * (float(h(d_beta)) + float(h(d_alpha)))
    chi = {"empty": float(h(g)) - S_ind,
           "1": 0.5 * (float(h(abs(1 - 2 * a))) - float(h(d_beta))) + 0.5 * (float(h(abs(1 - 2 * ap))) - float(h(d_alpha))),
           "2": float(h(math.sqrt(g ** 2 + 4 * r ** 2))) - S_ind,
           "12": 0.0}
    F = {"empty": (1 + g) / 2,
         "1": 0.5 + 0.25 * (abs(1 - 2 * a) + abs(1 - 2 * ap)),
         "2": 0.5 * (1 + math.sqrt(g ** 2 + 4 * r ** 2)),
         "12": 0.5 + 0.25 * (d_beta + d_alpha)}
    return chi, F


def P_K(model, t, k=K_RATE, mu=0.0):
    """Knowledge-class probabilities, r4_proposal.tex Eqs. leak-indep, leak-seq, leak-burst, leak-corr."""
    t = np.asarray(t, dtype=float)
    e = np.exp(-k * t)
    if model == "independent":
        return {"empty": e * e, "1": (1 - e) * e, "2": e * (1 - e), "12": (1 - e) ** 2}
    if model == "sequential":
        return {"empty": e, "1": k * t * e, "2": np.zeros_like(t), "12": 1 - e - k * t * e}
    if model == "burst":
        return {"empty": e, "1": np.zeros_like(t), "2": np.zeros_like(t), "12": 1 - e}
    if model == "correlated":
        P0 = np.exp(-(2 - mu) * k * t)
        P1 = np.exp(-mu * k * t) * (1 - np.exp(-(1 - mu) * k * t)) * np.exp(-(1 - mu) * k * t)
        return {"empty": P0, "1": P1, "2": P1.copy(), "12": 1 - P0 - 2 * P1}
    raise ValueError(model)


def curves(model, t, g, mu=0.0):
    """E[chi](t) in bits, F(t) = E[F_lambda](t), and P_K(t) -- Eq. leakage-expected."""
    chi, F = class_values(g)
    P = P_K(model, t, K_RATE, mu)
    return sum(P[K] * chi[K] for K in KEYS), sum(P[K] * F[K] for K in KEYS), P


PANELS = (("A", "independent", "gamma", GAMMAS, None),
          ("B", "sequential", "gamma", GAMMAS, None),
          ("C", "burst", "gamma", GAMMAS, None),
          ("D", "correlated", "mu", MUS, GAMMA_D))
MODEL_NAME = {"independent": "independent exponential leakage", "sequential": "sequential leakage",
              "burst": "burst leakage", "correlated": "correlated leakage"}


def family(panel):
    """List of (parameter value, gamma, mu, E_chi, F, P) for one panel."""
    letter, model, par, values, gfix = panel
    out = []
    for v in values:
        g, mu = (v, 0.0) if par == "gamma" else (gfix, v)
        Echi, F, P = curves(model, T, g, mu)
        out.append((v, g, mu, Echi, F, P))
    return out


DATA = {p[0]: family(p) for p in PANELS}

# panel D zoom insets: the same closed forms on a fine grid around the point of largest mu-dependence
T_INS = np.linspace(0.645, 0.675, 301)
INS_XLIM, INS_XTICKS = (0.65, 0.67), [0.655, 0.66, 0.665]
INS_TOP = dict(ylim=(0.2305, 0.2385), yticks=[0.232, 0.235, 0.238])
INS_BOT = dict(ylim=(0.8349, 0.8377), yticks=[0.835, 0.836, 0.837])
T_MARK = 0.66                                   # marked point on the main curves (connector start)
DATA_INS = [(mu, curves("correlated", T_INS, GAMMA_D, mu)) for mu in MUS]

# ----------------------------------------------------------------------------
# 2. Assertions: closed forms, simulation, probabilities, limits, quoted numbers, prototypes
# ----------------------------------------------------------------------------
print("== data checks (alpha = sqrt(0.6), beta = sqrt(0.4), k = 1) ==")
# (a) per-class inputs equal holevo_correct's closed forms (1e-12) and its 3-qubit simulation (1e-9)
SIM = {}
for g in GAMMAS + (GAMMA_D,):
    chi, F = class_values(g)
    chi_hc, F_hc = hc.chi_K_closed(AL, BE, g), hc.F_lam_closed(AL, BE, g)
    chi_sim, F_sim = hc.chi_K_sim(AL, BE, g)[0], hc.F_lam_sim(AL, BE, g)
    SIM[g] = (chi_sim, F_sim)
    for K in KEYS:
        assert abs(chi[K] - float(chi_hc[K])) < 1e-12 and abs(F[K] - float(F_hc[K])) < 1e-12, (g, K)
        assert abs(chi[K] - chi_sim[K]) < 1e-9 and abs(F[K] - F_sim[K]) < 1e-9, (g, K, chi[K], chi_sim[K], F[K], F_sim[K])
    print("  gamma=%.1f  chi_K = %.4f / %.4f / %.4f / %.4f   F_K = %.4f / %.4f / %.4f / %.4f  (empty / {1} / {2} / {1,2})"
          % ((g,) + tuple(chi[K] for K in KEYS) + tuple(F[K] for K in KEYS)))
# (b) every plotted value equals holevo_correct.expected_curves (1e-12); P_K equals hc.P_K, sums to 1, >= 0
SUB = np.arange(0, len(T), 50)          # coarse subsample for the simulation check (11 points)
for letter, model, par, values, gfix in PANELS:
    for v, g, mu, Echi, F, P in DATA[letter]:
        Echi_hc, F_hc, _Fb, P_hc = hc.expected_curves(model, T, AL, BE, g, k=K_RATE, mu=mu)
        assert np.max(np.abs(Echi - Echi_hc)) < 1e-12 and np.max(np.abs(F - F_hc)) < 1e-12, (letter, v)
        for K in KEYS:
            assert np.max(np.abs(P[K] - P_hc[K])) < 1e-12 and np.all(P[K] >= -1e-15), (letter, v, K)
        assert np.max(np.abs(sum(P[K] for K in KEYS) - 1.0)) < 1e-12, (letter, v)
        # 3-qubit density-matrix evaluation of the per-class inputs, weighted with P_K, at the subsample
        chi_sim, F_sim = SIM[g]
        E_sim = sum(P[K][SUB] * chi_sim[K] for K in KEYS)
        F_simt = sum(P[K][SUB] * F_sim[K] for K in KEYS)
        assert np.max(np.abs(Echi[SUB] - E_sim)) < 1e-9 and np.max(np.abs(F[SUB] - F_simt)) < 1e-9, (letter, v)
        # limits: t = 0 and large t
        chi0, F0 = class_values(g)
        assert abs(Echi[0] - chi0["empty"]) < 1e-12 and abs(F[0] - F0["empty"]) < 1e-12
        assert abs(F0["empty"] - (1 + g) / 2) < 1e-12
        E_inf, F_inf, _ = curves(model, np.array([50.0]), g, mu)
        assert abs(E_inf[0]) < 1e-15 and abs(F_inf[0] - F0["12"]) < 1e-15, (letter, v)
        # monotone: chi falls, F rises; chi lies between 0 and chi_empty; F between F_empty and F_12
        assert np.all(np.diff(Echi) < 0) and np.all(np.diff(F) > 0), (letter, v)
        assert np.all(Echi >= 0) and np.all(Echi <= chi0["empty"] + 1e-15)
        assert np.all(F >= F0["empty"] - 1e-15) and np.all(F <= F0["12"] + 1e-15)
print("  every plotted value == holevo_correct.expected_curves (1e-12); P_K == hc.P_K, P_K >= 0, sum P_K = 1 (1e-12);")
print("  subsample (%d t values per curve) == P_K-weighted 3-qubit simulation chi_K_sim / F_lam_sim (1e-9);" % len(SUB))
print("  limits: E[chi](0) = chi_empty, F(0) = (1+gamma)/2, E[chi](50) = 0, F(50) = F_{12} (1e-15); chi falls, F rises.")
# (c) model identities stated in the text
for g in GAMMAS:
    Eb, Fb, _ = curves("burst", T, g)
    c0, F0 = class_values(g)
    assert np.allclose(Eb, np.exp(-T) * c0["empty"], atol=1e-14)
    assert np.allclose(Fb, np.exp(-T) * F0["empty"] + (1 - np.exp(-T)) * F0["12"], atol=1e-14)
for K in KEYS:                                   # mu = 0 is the independent model, mu = 1 the burst model
    assert np.allclose(P_K("correlated", T, mu=0.0)[K], P_K("independent", T)[K], atol=1e-14)
    assert np.allclose(P_K("correlated", T, mu=1.0)[K], P_K("burst", T)[K], atol=1e-14)
print("  burst: E[chi] = e^-kt chi_empty, F = e^-kt F_empty + (1-e^-kt) F_12; correlated mu=0 == independent, mu=1 == burst.")

# (d) quoted numbers of r4_proposal.tex / holevo_07_proposal.tex
Q = {g: class_values(g) for g in GAMMAS + (GAMMA_D,)}
assert np.allclose([Q[g][0]["empty"] for g in GAMMAS], [1.0, 0.832, 0.717, 0.620], atol=5e-4)     # chi_empty
assert np.allclose([Q[g][1]["empty"] for g in GAMMAS], [0.50, 0.55, 0.60, 0.65], atol=1e-12)      # F_empty
assert np.allclose([Q[g][1]["12"] for g in GAMMAS], [1.000, 0.976, 0.956, 0.941], atol=5e-4)      # F_12
assert np.allclose([Q[g][1]["1"] for g in GAMMAS], [0.60, 0.59, 0.60, 0.65], atol=5e-3)           # F_1
assert abs(Q[GAMMA_D][0]["empty"] - 0.452) < 5e-4 and abs(Q[GAMMA_D][1]["empty"] - 0.75) < 1e-12
assert abs(Q[GAMMA_D][1]["12"] - 0.929) < 5e-4 and abs(Q[GAMMA_D][1]["1"] - 0.750) < 5e-4 and abs(Q[GAMMA_D][1]["2"] - 0.927) < 5e-4
print("  quoted values reproduced: chi_empty = 1 / 0.832 / 0.717 / 0.620 bit; F_empty = 0.50 / 0.55 / 0.60 / 0.65;")
print("    F_12 = 1.000 / 0.976 / 0.956 / 0.941; F_1 = 0.60 / 0.59 / 0.60 / 0.65 (gamma = 0 / 0.1 / 0.2 / 0.3);")
print("    gamma = 0.5: chi_empty = 0.452 bit, F_empty = 0.75, F_1 = 0.750, F_2 = 0.927, F_12 = 0.929.")

# ordering of the chi curves in gamma (A-C) and the crossing windows of the F curves
TF = np.linspace(0.0, 5.0, 50001)


def bisect_root(f, a, b, tol=1e-12):
    fa = f(a)
    for _ in range(200):
        m = 0.5 * (a + b)
        fm = f(m)
        if fa * fm <= 0:
            b = m
        else:
            a, fa = m, fm
        if b - a < tol:
            break
    return 0.5 * (a + b)


CROSS = {}
for letter, model, par, values, gfix in PANELS[:3]:
    fine = {g: curves(model, TF, g)[:2] for g in GAMMAS}
    for g1, g2 in zip(GAMMAS[:-1], GAMMAS[1:]):          # chi ordering kept at every t > 0
        d = fine[g1][0][1:] - fine[g2][0][1:]
        assert np.all(d > 0), (letter, g1, g2)
    roots = []
    for g1, g2 in itertools.combinations(GAMMAS, 2):
        d = fine[g1][1] - fine[g2][1]
        s = np.where(np.sign(d[:-1]) * np.sign(d[1:]) < 0)[0]
        assert len(s) == 1, (letter, g1, g2, len(s))     # exactly one crossing per pair
        i = int(s[0])
        f = lambda x, g1=g1, g2=g2: float(curves(model, np.array([x]), g1)[1][0] - curves(model, np.array([x]), g2)[1][0])
        roots.append(((g1, g2), bisect_root(f, TF[i], TF[i + 1])))
    CROSS[letter] = (min(r for _, r in roots), max(r for _, r in roots), roots)
    print("  %s %s: F crossings at t = %s; window %.3f-%.3f /k"
          % (letter, model, ", ".join("%.3f (%.1f vs %.1f)" % (r, p[0], p[1]) for p, r in roots), CROSS[letter][0], CROSS[letter][1]))
assert abs(CROSS["A"][0] - 0.650) < 2e-3 and abs(CROSS["A"][1] - 1.499) < 2e-3      # text: 0.6-1.5
assert abs(CROSS["B"][0] - 1.352) < 2e-3 and abs(CROSS["B"][1] - 2.817) < 2e-3      # text: 1.4-2.8
assert abs(CROSS["C"][0] - 1.124) < 2e-3 and abs(CROSS["C"][1] - 1.478) < 2e-3      # text: 1.1-1.5
# panel D: the four mu curves coincide within the quoted tolerances
spread_chi = max(np.max(np.abs(a[3] - b[3])) for a, b in itertools.combinations(DATA["D"], 2))
spread_F = max(np.max(np.abs(a[4] - b[4])) for a, b in itertools.combinations(DATA["D"], 2))
assert spread_chi < 0.002 and spread_F < 1e-3, (spread_chi, spread_F)
for a, b in zip(DATA["D"][:-1], DATA["D"][1:]):      # larger mu -> faster decay of chi (text statement)
    assert np.all(a[3][1:] - b[3][1:] > 0)
print("  D (gamma = 0.5): max spread over mu = %.5f bit (chi, < 0.002) and %.6f (F, < 0.001); larger mu decays faster." % (spread_chi, spread_F))
# inset data: equal to holevo_correct (1e-12); the window holds all four curves; the largest spread lies inside it
_fine = np.linspace(0.0, 5.0, 50001)
_dchi = curves("correlated", _fine, GAMMA_D, 0.0)[0] - curves("correlated", _fine, GAMMA_D, 0.9)[0]
_dF = curves("correlated", _fine, GAMMA_D, 0.9)[1] - curves("correlated", _fine, GAMMA_D, 0.0)[1]
T_PEAK_CHI, T_PEAK_F = float(_fine[np.argmax(_dchi)]), float(_fine[np.argmax(_dF)])
assert INS_XLIM[0] <= T_PEAK_CHI <= INS_XLIM[1] and INS_XLIM[0] <= T_PEAK_F <= INS_XLIM[1], (T_PEAK_CHI, T_PEAK_F)
_w = (T_INS >= INS_XLIM[0]) & (T_INS <= INS_XLIM[1])
for mu, (Echi_i, F_i, P_i) in DATA_INS:
    Echi_hc, F_hc, _Fb, _P = hc.expected_curves("correlated", T_INS, AL, BE, GAMMA_D, k=K_RATE, mu=mu)
    assert np.max(np.abs(Echi_i - Echi_hc)) < 1e-12 and np.max(np.abs(F_i - F_hc)) < 1e-12, mu
    assert np.all(Echi_i[_w] > INS_TOP["ylim"][0]) and np.all(Echi_i[_w] < INS_TOP["ylim"][1]), (mu, Echi_i[_w].min(), Echi_i[_w].max())
    assert np.all(F_i[_w] > INS_BOT["ylim"][0]) and np.all(F_i[_w] < INS_BOT["ylim"][1]), (mu, F_i[_w].min(), F_i[_w].max())
_i66 = int(np.argmin(np.abs(T_INS - T_MARK)))
_sep_chi = min(DATA_INS[j][1][0][_i66] - DATA_INS[j + 1][1][0][_i66] for j in range(3))
_sep_F = min(DATA_INS[j + 1][1][1][_i66] - DATA_INS[j][1][1][_i66] for j in range(3))
print("  D insets: window t = %.2f-%.2f/k contains the largest mu-spread (chi at t = %.3f, F at t = %.3f);" % (INS_XLIM + (T_PEAK_CHI, T_PEAK_F)))
print("    chi range %.4f-%.4f bit (ticks %s), F range %.4f-%.4f (ticks %s); at t = 0.66 adjacent curves are >= %.5f bit / %.6f apart"
      % (INS_TOP["ylim"] + (INS_TOP["yticks"],) + INS_BOT["ylim"] + (INS_BOT["yticks"], _sep_chi, _sep_F)))
print("    values at t = 0.66, mu = 0 / 0.3 / 0.6 / 0.9: chi = %s bit; F = %s"
      % (" / ".join("%.5f" % d[1][0][_i66] for d in DATA_INS), " / ".join("%.6f" % d[1][1][_i66] for d in DATA_INS)))

# (e) prototype CSVs: the Holevo column must match exactly; the max-overlap column is recomputed and compared
for letter, model, par, values, gfix in PANELS:
    path = os.path.join(WORK, "holevo", "fig7_%s_prototype.csv" % model)
    with open(path, newline="") as f:
        rows = [r for r in csv.reader(ln for ln in f if not ln.startswith("#"))]
    hdr, rows = rows[0], rows[1:]
    assert hdr == ["time", par, "expected_holevo_bits", "eve_fidelity_operational", "eve_maxoverlap_lambda"], hdr
    w_chi = w_F = 0.0
    for r in rows:
        tt, v, chi_p, _fbar, fl_p = map(float, r)
        g, mu = (v, 0.0) if par == "gamma" else (gfix, v)
        Echi, F, _ = curves(model, np.array([tt]), g, mu)
        w_chi = max(w_chi, abs(float(Echi[0]) - chi_p)); w_F = max(w_F, abs(float(F[0]) - fl_p))
    assert w_chi < 1e-9 and w_F < 1e-9, (model, w_chi, w_F)
    print("  prototype fig7_%s_prototype.csv (%d rows): max |dE[chi]| = %.1e, max |dF_lambda| = %.1e (10-decimal file)" % (model, len(rows), w_chi, w_F))

# ----------------------------------------------------------------------------
# 3. Colour plan: all eight hues validated together
# ----------------------------------------------------------------------------
COL_GAMMA = {0.0: "#0072B2", 0.1: "#D55E00", 0.2: "#009E73", 0.3: "#AA3377"}   # blue, vermilion, green, magenta
COL_MU = {0.0: "#33BBEE", 0.3: "#AAAA00", 0.6: "#F781BF", 0.9: "#332288"}      # cyan, olive, pink, indigo
EIGHT = [COL_GAMMA[g] for g in GAMMAS] + [COL_MU[m] for m in MUS]
print("== palette ==")
print("  gamma = 0 / 0.1 / 0.2 / 0.3 ->", [COL_GAMMA[g] for g in GAMMAS])
print("  mu    = 0 / 0.3 / 0.6 / 0.9 ->", [COL_MU[m] for m in MUS])
REP8 = scifig.validate_palette(EIGHT)
assert REP8["pass"], "eight-colour palette failed the validator"
for name, cols in (("gamma set", [COL_GAMMA[g] for g in GAMMAS]), ("mu set", [COL_MU[m] for m in MUS])):
    rep = scifig.validate_palette(cols, verbose=False)
    assert rep["pass"], name
    print("  %s alone: min dE normal %.1f, protan %.1f, deutan %.1f, tritan %.1f -> PASS" % (
        name, rep["min"]["normal"][0], rep["min"]["protan"][0], rep["min"]["deutan"][0], rep["min"]["tritan"][0]))
_cross = [(a, b) for a in COL_GAMMA.values() for b in COL_MU.values()]
XN = min(scifig.delta_e(a, b) for a, b in _cross)
XC = min(scifig.delta_e(a, b, m) for a, b in _cross for m in ("protan", "deutan", "tritan"))
print("  cross-set pairs only: min dE normal %.1f (>= 15), min dE CVD %.1f (>= 8)" % (XN, XC))
assert XN >= 15 and XC >= 8

# ----------------------------------------------------------------------------
# 4. Drawing
# ----------------------------------------------------------------------------
GREY_TXT, BAND = "#555555", "#000000"
LW = 1.2
ANN = 6.5                 # annotations and legends
XLAB = "time $t$ (1/$k$)"
YLAB_CHI = r"$\mathbb{E}[\chi(t)]$ (bits)"
YLAB_F = "overlap $F(t)$\n(dimensionless)"
XLIM, YLIM_CHI, YLIM_F = (0, 5), (0, 1.02), (0.47, 1.02)
TICK_CHI = ([0, 0.25, 0.5, 0.75, 1.0], ["0", "0.25", "0.5", "0.75", "1"])
TICK_F = ([0.5, 0.6, 0.7, 0.8, 0.9, 1.0], ["0.5", "0.6", "0.7", "0.8", "0.9", "1"])


def draw_panel(fig, ax_top, ax_bot, panel, show_ylabels=True):
    """Draw one panel (top: E[chi], bottom: F) and return (lines_top, lines_bot, legend, annotations)."""
    letter, model, par, values, gfix = panel
    sym = r"$\gamma$" if par == "gamma" else r"$\mu$"
    cmap = COL_GAMMA if par == "gamma" else COL_MU
    lt, lb = [], []
    for v, g, mu, Echi, F, P in DATA[letter]:
        lab = "%s = %g" % (sym, v)
        (l1,) = ax_top.plot(T, Echi, color=cmap[v], lw=LW, solid_capstyle="round", label=lab, zorder=3)
        (l2,) = ax_bot.plot(T, F, color=cmap[v], lw=LW, solid_capstyle="round", label=lab, zorder=3)
        lt.append(l1); lb.append(l2)
    ax_top.set_xlim(*XLIM); ax_top.set_ylim(*YLIM_CHI)
    ax_bot.set_xlim(*XLIM); ax_bot.set_ylim(*YLIM_F)
    ax_top.set_xticks(range(0, 6)); ax_bot.set_xticks(range(0, 6))
    ax_top.set_yticks(TICK_CHI[0]); ax_top.set_yticklabels(TICK_CHI[1])
    ax_bot.set_yticks(TICK_F[0]); ax_bot.set_yticklabels(TICK_F[1])
    # shared time axis: the x label is set on both (audit) and drawn once, on the bottom subplot
    ax_top.set_xlabel(XLAB); ax_top.xaxis.label.set_visible(False); ax_top.tick_params(labelbottom=False)
    ax_bot.set_xlabel(XLAB)
    ax_top.set_ylabel(YLAB_CHI); ax_bot.set_ylabel(YLAB_F, linespacing=1.15)
    if not show_ylabels:                   # right column of the 2 x 2 figure: same quantity and range as the left
        ax_top.yaxis.label.set_visible(False); ax_bot.yaxis.label.set_visible(False)
    # one compact legend per panel, upper right of the top subplot (above the decaying chi curves)
    leg = ax_top.legend(handles=lt, loc="upper right", bbox_to_anchor=(1.0, 1.0), fontsize=ANN,
                        handlelength=1.8, labelspacing=0.3, borderaxespad=0.0, handletextpad=0.6)
    ann = []
    if letter in CROSS:                    # key numbers: the crossing window of the F curves
        t0, t1, _ = CROSS[letter]
        ax_bot.axvspan(t0, t1, color=BAND, alpha=0.07, lw=0, zorder=0)
        ann.append(ax_bot.text(t1 + 0.12, YLIM_F[0] + 0.015, "crossings\n$t$ = %.2f\u2013%.2f" % (t0, t1), color=GREY_TXT,
                               fontsize=ANN, ha="left", va="bottom", linespacing=1.1, zorder=6))
    else:                                  # panel D: the four mu curves coincide -> statement + zoom insets
        ann.append(ax_top.text(3.9, 0.25, "four curves coincide\n(within 0.002 bit)", color=GREY_TXT,
                               fontsize=ANN, ha="center", va="center", linespacing=1.1, zorder=6))
        ann.append(ax_bot.text(1.0, 0.56, "four curves coincide\n(within 0.001)", color=GREY_TXT,
                               fontsize=ANN, ha="center", va="center", linespacing=1.1, zorder=6))
        for ax, row, spec, box in ((ax_top, 0, INS_TOP, (0.17, 0.42, 0.40, 0.56)),
                                   (ax_bot, 1, INS_BOT, (0.50, 0.14, 0.40, 0.56))):
            ins = ax.inset_axes(box)
            for mu, (Echi_i, F_i, _P) in DATA_INS:
                ins.plot(T_INS, (Echi_i, F_i)[row], color=COL_MU[mu], lw=0.9, solid_capstyle="butt",
                         label="%s = %g" % (r"$\mu$", mu), zorder=3)
            ins.set_xlim(*INS_XLIM); ins.set_ylim(*spec["ylim"])
            ins.set_xticks(INS_XTICKS); ins.set_xticklabels(["%g" % v for v in INS_XTICKS])
            ins.set_yticks(spec["yticks"]); ins.set_yticklabels(["%.3f" % v for v in spec["yticks"]])
            ins.yaxis.tick_right()                                     # keep the lower-left corner label-free
            ins.tick_params(labelsize=6.0, length=1.5, width=0.5, pad=1.5)
            for sp in ins.spines.values():                             # framed inset
                sp.set_visible(True); sp.set_linewidth(0.6); sp.set_color(GREY_TXT)
            ins.set_xlabel(ax.get_xlabel()); ins.xaxis.label.set_visible(False)   # same quantities as the parent
            ins.set_ylabel(ax.get_ylabel()); ins.yaxis.label.set_visible(False)
            # marked point on the main curves and a thin connector to the inset's lower-left corner
            y_mark = float(curves("correlated", np.array([T_MARK]), GAMMA_D, 0.0)[row][0])
            ax.plot([T_MARK], [y_mark], marker="o", ms=2.6, mfc="white", mec=GREY_TXT, mew=0.6, ls="None", zorder=5)
            con = ax.annotate("", xy=(box[0], box[1]), xycoords="axes fraction", xytext=(T_MARK, y_mark),
                              textcoords="data", zorder=4,
                              arrowprops=dict(arrowstyle="-", color=GREY_TXT, lw=0.5, shrinkA=2.2, shrinkB=0))
            ann.append(ins); ann.append(con)
    return lt, lb, leg, ann


def check_clearance(fig, ax, items, lines, pad_pt=1.0, what=""):
    """Every text / legend / inset box (plus pad) must contain no point of any data curve of the parent
    axes; a connector must enter no text box of the figure. Prints the clearance."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    pad = pad_pt / 72.0 * fig.dpi
    for it in items:
        if isinstance(it, matplotlib.text.Annotation):            # connector line: sample it, test against all text boxes
            p0 = np.array(it.get_transform().transform(it.get_position()), float)   # textcoords end (on the curve)
            p1 = np.array(it.axes.transAxes.transform(it.xy), float)                 # xycoords end (inset corner)
            pts = np.column_stack([np.linspace(p0[0], p1[0], 200), np.linspace(p0[1], p1[1], 200)])
            for t in fig.findobj(Text):
                if t.get_text().strip() and t.get_visible():
                    tb = t.get_window_extent(r)
                    hit = ((pts[:, 0] >= tb.x0) & (pts[:, 0] <= tb.x1) & (pts[:, 1] >= tb.y0) & (pts[:, 1] <= tb.y1))
                    assert not hit.any(), "%s: connector crosses text %r" % (what, t.get_text()[:20])
            print("  %s: %-30s crosses no text box" % (what, "'connector'"))
            continue
        if isinstance(it, matplotlib.axes.Axes):                   # inset: its tight box (frame + tick labels)
            bb = it.get_tightbbox(r)
            name = "inset"
        else:
            bb = it.get_window_extent(r)
            name = it.get_text().replace("\n", " / ")[:28] if isinstance(it, Text) else "legend"
        gap = np.inf
        for l in lines:
            xy = ax.transData.transform(np.column_stack([l.get_xdata(), l.get_ydata()]))
            inside = ((xy[:, 0] >= bb.x0 - pad) & (xy[:, 0] <= bb.x1 + pad) &
                      (xy[:, 1] >= bb.y0 - pad) & (xy[:, 1] <= bb.y1 + pad))
            assert not inside.any(), "%s: %r collides with curve %s" % (what, name, l.get_label())
            m = (xy[:, 0] >= bb.x0) & (xy[:, 0] <= bb.x1)
            if m.any():
                gap = min(gap, float(np.min(np.abs(xy[m, 1] - np.clip(xy[m, 1], bb.y0, bb.y1)))))
        print("  %s: %-30s clear of all curves (nearest point %.1f pt below/above the box)"
              % (what, repr(name), gap / fig.dpi * 72.0 if np.isfinite(gap) else float("nan")))


def mathtext_min_glyph(fig):
    parser = MathTextParser("path")
    mn = 99.0
    for t in fig.findobj(Text):
        if t.get_visible() and "$" in t.get_text():
            for part in t.get_text().split("\n"):
                if "$" in part:
                    res = parser.parse(part, dpi=72, prop=t.get_fontproperties())
                    mn = min(mn, min(gl[1] for gl in res.glyphs))
    return mn


def run_audit(fig, target, tag):
    report = scifig.audit(fig, target_width=target, journal_mode=True)
    n_fail = sum(1 for lvl, _ in report if lvl == "FAIL")
    n_warn = sum(1 for lvl, _ in report if lvl == "WARN")
    mg = mathtext_min_glyph(fig)
    print("  %s mathtext check: smallest glyph %.2f pt (need >= 6)" % (tag, mg))
    assert mg >= 6.0 - 1e-6, mg
    assert n_fail == 0 and n_warn == 0, "%s: audit reported %d FAIL, %d WARN" % (tag, n_fail, n_warn)
    # inset axes are child axes (not in fig.get_axes()), so scifig.audit's per-axes loop skips them; their tick
    # labels ARE in its figure-wide text check. Repeat the per-axes checks for every inset explicitly.
    for ax in fig.get_axes():
        for k, ins in enumerate(ax.child_axes):
            lines = [l for l in ins.get_lines() if np.asarray(l.get_xdata()).size >= 2 and l.get_linestyle() != "None"]
            cols = []
            for l in lines:
                hx = matplotlib.colors.to_hex(l.get_color())
                if hx not in cols:
                    cols.append(hx)
            rep = scifig.validate_palette(cols, verbose=False)
            dn = rep["min"]["normal"][0]
            dc = min(rep["min"][m][0] for m in ("protan", "deutan", "tritan"))
            labels_ok = bool(ins.get_xlabel().strip() and ins.get_ylabel().strip())
            ticks = [t for t in ins.get_xticklabels() + ins.get_yticklabels() if t.get_text().strip()]
            smallest = min(t.get_fontsize() for t in ticks)
            assert len(lines) <= 6 and len(cols) == len(lines) and dn >= 15 and dc >= 8 and labels_ok and smallest >= 6.0, \
                (tag, len(lines), cols, dn, dc, labels_ok, smallest)
            print("  %s inset audit (%s): %d curves, %d colours, min dE normal %.1f (>=15), min dE CVD %.1f (>=8), "
                  "labels set, %d tick labels >= %.1f pt, no legend -> OK"
                  % (tag, "top" if ax.get_ylabel().startswith("$\\mathbb") else "bottom", len(lines), len(cols), dn, dc,
                     len(ticks), smallest))
    return report


# ---- main figure: 2 x 2 panels, each two stacked subplots ------------------------------------------
print("== main figure ==")
W, H = scifig.setup(width="double", height_cm=14.0, base_pt=7.0)
fig = plt.figure(figsize=(W, H))
outer = fig.add_gridspec(2, 2, hspace=0.16, wspace=0.10)
AXES = {}
for idx, panel in enumerate(PANELS):
    r, c = divmod(idx, 2)
    inner = outer[r, c].subgridspec(2, 1, hspace=0.07)
    ax_top = fig.add_subplot(inner[0])
    ax_bot = fig.add_subplot(inner[1], sharex=ax_top)
    lt, lb, leg, ann = draw_panel(fig, ax_top, ax_bot, panel, show_ylabels=(c == 0))
    scifig.panel_label(ax_top, panel[0], x=-0.17 if c == 0 else -0.085, y=1.05, size=9)
    AXES[panel[0]] = (ax_top, ax_bot, lt, lb, leg, ann)

def _on(a, ax):
    """True if artist a belongs to ax (texts, connectors) or is an inset of ax."""
    return (a.axes is ax) or (isinstance(a, matplotlib.axes.Axes) and a in ax.child_axes)


fig.canvas.draw()
for letter, (ax_top, ax_bot, lt, lb, leg, ann) in AXES.items():
    check_clearance(fig, ax_top, [leg] + [a for a in ann if _on(a, ax_top)], lt, what="panel %s top" % letter)
    check_clearance(fig, ax_bot, [a for a in ann if _on(a, ax_bot)], lb, what="panel %s bottom" % letter)
run_audit(fig, "double", "main")
scifig.save(fig, os.path.join(OUT, "fig7_final"))
plt.close(fig)

# ---- SI single-panel versions (1 column, 8.5 cm), own legend, same colours, no panel letter ---------
for panel in PANELS:
    letter = panel[0]
    print("== SI single panel %s (%s) ==" % (letter, MODEL_NAME[panel[1]]))
    W1, H1 = scifig.setup(width=8.5, height_cm=7.8, base_pt=7.0)
    f1 = plt.figure(figsize=(W1, H1))
    g1 = f1.add_gridspec(2, 1, hspace=0.07)
    a_top = f1.add_subplot(g1[0]); a_bot = f1.add_subplot(g1[1], sharex=a_top)
    lt, lb, leg, ann = draw_panel(f1, a_top, a_bot, panel, show_ylabels=True)
    f1.canvas.draw()
    check_clearance(f1, a_top, [leg] + [a for a in ann if _on(a, a_top)], lt, what="SI %s top" % letter)
    check_clearance(f1, a_bot, [a for a in ann if _on(a, a_bot)], lb, what="SI %s bottom" % letter)
    run_audit(f1, 8.5, "SI %s" % letter)
    scifig.save(f1, os.path.join(OUT, "fig7_panel%s" % letter))
    plt.close(f1)

# ----------------------------------------------------------------------------
# 5. Source data and the numbers for the caption
# ----------------------------------------------------------------------------
with open(os.path.join(OUT, "fig7_final_source_data.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["# Fig. 7 (final) source data. E_chi_bits = sum_K P_K(t) chi_K, F_overlap = sum_K P_K(t) F_K (maximal overlap F_K^lambda, "
                "NOT the Haar-averaged F-bar); corrected chi_K, F_K of SI Note holevo_07 (amplitude damping gamma on Bob's half of "
                "|Phi+> before Alice's Bell measurement), input alpha = sqrt(0.6), beta = sqrt(0.4), k1 = k2 = k = 1; "
                "P_K from r4 Eqs. leak-indep/leak-seq/leak-burst/leak-corr. Every row equals holevo_correct.expected_curves (1e-12); "
                "a coarse subsample equals the P_K-weighted 3-qubit density-matrix simulation (1e-9). t in units of 1/k."])
    w.writerow(["panel", "model", "parameter", "parameter_value", "gamma", "mu", "k", "t", "E_chi_bits", "F_overlap",
                "P_empty", "P_1", "P_2", "P_12"])
    for letter, model, par, values, gfix in PANELS:
        for v, g, mu, Echi, F, P in DATA[letter]:
            for i, t in enumerate(T):
                w.writerow([letter, model, par, "%g" % v, "%g" % g, "%g" % mu, "%g" % K_RATE, "%.2f" % t,
                            "%.10f" % Echi[i], "%.10f" % F[i],
                            "%.10f" % P["empty"][i], "%.10f" % P["1"][i], "%.10f" % P["2"][i], "%.10f" % P["12"][i]])
    for mu, (Echi_i, F_i, P_i) in DATA_INS:          # panel D zoom insets (fine grid, same closed forms)
        for i, t in enumerate(T_INS):
            w.writerow(["D_inset", "correlated", "mu", "%g" % mu, "%g" % GAMMA_D, "%g" % mu, "%g" % K_RATE, "%.4f" % t,
                        "%.10f" % Echi_i[i], "%.10f" % F_i[i],
                        "%.10f" % P_i["empty"][i], "%.10f" % P_i["1"][i], "%.10f" % P_i["2"][i], "%.10f" % P_i["12"][i]])
print("source data written: fig7_final_source_data.csv (%d rows incl. %d inset rows)"
      % (len(T) * sum(len(p[3]) for p in PANELS) + len(T_INS) * len(MUS), len(T_INS) * len(MUS)))

print("== numbers per curve (t = 0, 1, 5; units of 1/k) ==")
for letter, model, par, values, gfix in PANELS:
    for v, g, mu, Echi, F, P in DATA[letter]:
        i1 = int(np.argmin(np.abs(T - 1.0)))
        print("  %s %-11s %s=%.1f gamma=%.1f: E[chi](0)=%.4f E[chi](1)=%.4f E[chi](5)=%.4f | F(0)=%.4f F(1)=%.4f F(5)=%.4f | F_12=%.4f"
              % (letter, model, par, v, g, Echi[0], Echi[i1], Echi[-1], F[0], F[i1], F[-1], class_values(g)[1]["12"]))
print("done")
