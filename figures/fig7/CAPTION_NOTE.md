# Fig. 7 (final, 2 x 2 panels A-D, each = E[chi(t)] over F(t)) — what the caption must say

Files: `fig7_final.pdf` (vector, DejaVu Sans embedded as Type 42 subsets), `fig7_final.png` (600 dpi),
source data `fig7_final_source_data.csv`, script `fig7_final.py` (FIGURE BRIEF in the docstring),
audit `audit.txt` (complete console output of the last run).  Double column, 18.3 cm x 14.0 cm nominal
(PDF page after tight cropping 18.19 x 13.89 cm; SI panels 8.39 x 7.69 cm from 8.5 x 7.8 cm nominal).
Text sizes: axis labels 7 pt, ticks 6 pt, legends and annotations 6.5 pt, panel letters 9 pt bold;
no mathtext sub/superscripts (smallest glyph 6.5 pt, smallest text item 6.0 pt).
SI single-panel versions (SI Figs. 4-7 beside the derivations): `fig7_panelA.pdf` … `fig7_panelD.pdf`
(+ PNG), 1 column, 8.5 cm x 7.8 cm, own legend, same colours, y labels on every panel, **no panel letter**
(standalone figures; their captions should say "reproduces Fig. 7A/B/C/D of the main text").

Status: data from the corrected closed forms approved by N.K.C. (fixed-gamma, maximal-overlap version).
The figure itself carries no draft marking.  Nothing outside this folder was modified.

## Colour map (fixed; the same gamma has the same hue in A, B and C)

| series | hex | name |
|---|---|---|
| gamma = 0   (A-C) | `#0072B2` | blue |
| gamma = 0.1 (A-C) | `#D55E00` | vermilion |
| gamma = 0.2 (A-C) | `#009E73` | green |
| gamma = 0.3 (A-C) | `#AA3377` | magenta |
| mu = 0   (D) | `#33BBEE` | cyan |
| mu = 0.3 (D) | `#AAAA00` | olive |
| mu = 0.6 (D) | `#F781BF` | pink |
| mu = 0.9 (D) | `#332288` | indigo |
| crossing window (A-C) | black at 7 % opacity | light grey band |
| annotations | `#555555` | dark grey |

All eight hues validated together (`scifig.validate_palette`, asserted PASS): min pairwise OKLab dE 16.5
(normal, need >= 15; green-olive), 9.6 / 8.7 / 8.6 (protan / deutan / tritan, need >= 8).  Gamma set alone
18.7 / 12.2 / 10.3 / 8.6 (the tritan pair blue-green is the paper's fixed pair, as in Figs. 3 and 6); mu set
alone 25.1 / 9.6 / 9.4 / 13.7; cross-set pairs only 16.5 / 8.7.  All curves solid, uniform 1.2 pt; no
linestyle encoding.  Each panel has its own legend, so the caption need not list the colours, but it must
say that the colour key of A-C is one and the same.

**Cross-figure note.**  Fig. 6B uses magenta / mustard / cyan for gamma = 0.1 / 0.3 / 0.5.  An exhaustive
search over 46 candidate hues found no eight-colour set passing the validator that contains both of Fig. 6's
gamma = 0.1 and 0.3 hues, so Fig. 7 cannot share Fig. 6's gamma map (the families also differ:
{0, 0.1, 0.2, 0.3} here, {0.1, 0.3, 0.5} there).  Fig. 7 therefore carries its own fixed gamma map (above);
gamma = 0.5 is a fixed parameter of panel D, not a series.  If a paper-wide gamma map is wanted, Fig. 6B
would have to be recoloured (decision for the user / N.K.C.; not done here).

## Required statements

1. **Models and rates.**  (A) independent exponential leakage, k1 = k2 = 1; (B) sequential leakage,
   k1 = k2 = 1 (m2 can leak only after m1; the class {2} never occurs); (C) burst leakage, k = 1 (both bits
   at one exponential time; no partial-leakage phase); (D) correlated leakage, k = 1, gamma = 0.5, for the
   correlation parameter mu = 0, 0.3, 0.6, 0.9 (mu = 0 is the independent model, mu = 1 the burst model;
   both identities are asserted in the script).  Time t in units of 1/k, 0 <= t <= 5.  The class
   probabilities P_K(t) are Eqs. (leak-indep) … (leak-corr) of R4 / SI Note "Stochastic Models for Classical
   Information Leakage".

2. **Input state and damping.**  |psi> = alpha|0> + beta|1> with alpha = sqrt(0.6), beta = sqrt(0.4)
   (|alpha|^2 = 0.6), fixed; amplitude damping gamma on Bob's half of |Phi+> before Alice's Bell measurement,
   held fixed in time (not coupled to t).  Curves in A-C: gamma = 0, 0.1, 0.2, 0.3.

3. **Metric definitions (both subplots at the SAME fixed input).**  Top: E[chi(t)] = sum_K P_K(t) chi_K,
   the expected Holevo information (bits) that the adversary can extract about the unrevealed correction
   bits.  Bottom: F(t) = sum_K P_K(t) F_K with F_K the **maximal overlap** with Bob's conditional state
   (largest eigenvalue of Eve's averaged state, averaged over the bits she knows; attained only with
   knowledge of psi; a mathematical overlap, not a reconstruction fidelity and not a discrimination
   probability).  Per-class inputs chi_K and F_K are the corrected forms of SI Notes holevo-derivation /
   app:fidelity; chi_{1,2} = 0.  The Haar-averaged fidelity F-bar(t) is **not** plotted, so the two subplots
   carry the same input prior (the old "[PENDING: F or F-bar]" sentence of the caption/R4 text is resolved).

4. **Numbers at t = 0 (visible on the axes; quote them).**  E[chi](0) = chi_empty = 1, 0.832, 0.717,
   0.620 bit and F(0) = F_empty = (1 + gamma)/2 = 0.50, 0.55, 0.60, 0.65 for gamma = 0, 0.1, 0.2, 0.3
   (all models); panel D: E[chi](0) = 0.452 bit, F(0) = 0.75 (gamma = 0.5).

5. **Long-time behaviour.**  E[chi](t) decreases monotonically toward 0 and keeps its ordering in gamma
   (larger gamma lower at every t); F(t) increases monotonically toward F_{1,2} = 1/2 + (delta_beta +
   delta_alpha)/4 = 1.000, 0.976, 0.956, 0.941 (gamma = 0 … 0.3) and 0.929 (gamma = 0.5).  At t = 5 the
   curves are still slightly below the asymptote (A: 0.997 / 0.973 / 0.954 / 0.939; B: 0.983 / 0.960 /
   0.942 / 0.930; C: 0.997 / 0.973 / 0.954 / 0.939; D: 0.928), so write "toward", not "reach".  Burst
   model: E[chi](t) = e^{-kt} chi_empty and F(t) = e^{-kt} F_empty + (1 - e^{-kt}) F_{1,2} (asserted).

6. **Crossing of the F(t) curves (the shaded band + numbers in A-C).**  Because the start value
   (1 + gamma)/2 rises with gamma while the asymptote F_{1,2} falls, every pair of F curves crosses exactly
   once.  Windows (first to last pairwise crossing, bisection on the closed forms): **A 0.65-1.50/k**
   (pairs: 0.651, 0.750, 0.944, 0.876, 1.155, 1.499), **B 1.35-2.82/k** (1.353, 1.582, 1.977, 1.841,
   2.330, 2.818), **C 1.12-1.48/k** (1.124, 1.188, 1.270, 1.261, 1.360, 1.478).  The band is the window
   between the first and the last crossing; the numbers are written beside it.  The E[chi] curves never
   cross (asserted).  In B the intermediate class contributes F_{1} = 0.60, 0.59, 0.60, 0.65, close to
   F_empty, which is why the crossing is later.  Rounding remark for the R4 / SI text: it says "between
   t ~ 0.6/k and 1.5/k" for the independent model; the first crossing is at 0.651/k, which rounds to 0.7 at
   one decimal — write "0.65/k" (or "~0.7/k").  "1.4/k and 2.8/k" (sequential) and "1.1/k and 1.5/k"
   (burst) are consistent with 1.353 / 2.818 and 1.124 / 1.478.

7. **Panel D and its zoom insets.**  The four mu curves coincide at the scale of the panel: they differ by
   at most 0.0015 bit (E[chi]; larger mu decays slightly faster, asserted) and by at most 4 x 10^-4 (F) at
   any t, so the main axes show one visible curve (mu = 0.9, drawn last) and say so in both subplots
   ("four curves coincide (within 0.002 bit / within 0.001)").  **Each D subplot carries a framed zoom
   inset** (40 % x 56 % of the subplot; upper middle of the E[chi] subplot, lower right of the F subplot)
   showing the window **t = 0.65-0.67/k** around the point of largest mu-dependence (t = 0.664/k for both
   quantities) with a tight ordinate: **E[chi] 0.2305-0.2385 bit (ticks 0.232 / 0.235 / 0.238)** and
   **F 0.8349-0.8377 (ticks 0.835 / 0.836 / 0.837)**; there the four curves are resolved (at t = 0.66/k:
   E[chi] = 0.2352 / 0.2348 / 0.2343 / 0.2337 bit and F = 0.83606 / 0.83618 / 0.83632 / 0.83648 for
   mu = 0 / 0.3 / 0.6 / 0.9; adjacent curves >= 0.0004 bit and >= 1.1 x 10^-4 apart).  Same four colours as
   the legend, no legend inside the inset, y tick labels on the inset's right side; an open grey marker on
   the main curve at t = 0.66/k and a thin grey connector to the inset's lower-left corner mark the zoomed
   point.  The caption must say: "insets: zoom on t = 0.65-0.67/k (note the ordinate ranges), where the
   mu-dependence is largest; larger mu lowers E[chi] and raises F slightly", and that the near-coincidence
   is a property of the model, not a plotting error (F_{1} = 0.750 and F_{2} = 0.927 lie so close to
   F_empty = 0.75 and F_{1,2} = 0.929 that the class composition hardly matters).  The inset data are
   the same closed forms on a fine grid (301 points, t = 0.645-0.675/k; rows "D_inset" of the CSV).

8. **Axes.**  Shared time axis per panel (top subplot carries no tick labels); x "time t (1/k)";
   y "E[chi(t)] (bits)" and "overlap F(t) (dimensionless)".  The right column (B, D) has the same y
   quantities and ranges as the left column and repeats the tick labels but not the y-axis titles; say
   "axes as in A" or rely on the identical ticks.  Ranges: chi 0-1.02 bit, F 0.47-1.02.

9. **Source data.**  "Source data are provided in `fig7_final_source_data.csv`" (9220 rows; columns:
   panel, model, parameter (gamma | mu), parameter_value, gamma, mu, k, t, E_chi_bits, F_overlap, P_empty,
   P_1, P_2, P_12; 501 time points per curve, step 0.01/k, 16 curves, plus 4 x 301 rows "D_inset" for the
   zoom windows at step 1e-4/k).  Every row equals
   `holevo/holevo_correct.py::expected_curves` (1e-12) and, at 11 time points per curve, the P_K-weighted
   3-qubit density-matrix simulation (`chi_K_sim`, `F_lam_sim`; 1e-9).  The old prototypes
   `holevo/fig7_*_prototype.csv` agree in the Holevo and max-overlap columns to 5e-11 (their 10-decimal
   rounding); their `eve_fidelity_operational` column is the Haar-averaged F-bar and is not used.

## Numbers per curve (t = 0 and t = 5, units of 1/k) — from audit.txt

| panel / model | parameter | E[chi](0) | E[chi](5) | F(0) | F(5) | F_{1,2} |
|---|---|---|---|---|---|---|
| A independent | gamma = 0   | 1.0000 | 0.0071 | 0.5000 | 0.9972 | 1.0000 |
| A independent | gamma = 0.1 | 0.8319 | 0.0058 | 0.5500 | 0.9733 | 0.9759 |
| A independent | gamma = 0.2 | 0.7168 | 0.0049 | 0.6000 | 0.9537 | 0.9562 |
| A independent | gamma = 0.3 | 0.6198 | 0.0043 | 0.6500 | 0.9394 | 0.9414 |
| B sequential  | gamma = 0   | 1.0000 | 0.0394 | 0.5000 | 0.9832 | 1.0000 |
| B sequential  | gamma = 0.1 | 0.8319 | 0.0328 | 0.5500 | 0.9601 | 0.9759 |
| B sequential  | gamma = 0.2 | 0.7168 | 0.0283 | 0.6000 | 0.9418 | 0.9562 |
| B sequential  | gamma = 0.3 | 0.6198 | 0.0245 | 0.6500 | 0.9296 | 0.9414 |
| C burst       | gamma = 0   | 1.0000 | 0.0067 | 0.5000 | 0.9966 | 1.0000 |
| C burst       | gamma = 0.1 | 0.8319 | 0.0056 | 0.5500 | 0.9731 | 0.9759 |
| C burst       | gamma = 0.2 | 0.7168 | 0.0048 | 0.6000 | 0.9538 | 0.9562 |
| C burst       | gamma = 0.3 | 0.6198 | 0.0042 | 0.6500 | 0.9394 | 0.9414 |
| D correlated (gamma = 0.5) | mu = 0, 0.3, 0.6, 0.9 | 0.4517 | 0.0031 | 0.7500 | 0.9279 | 0.9291 |

Panel D at t = 1: E[chi] = 0.1678 / 0.1675 / 0.1670 / 0.1664 bit and F = 0.8628 / 0.8629 / 0.8630 / 0.8632
for mu = 0 / 0.3 / 0.6 / 0.9 (the largest spreads, 0.0015 bit and 4 x 10^-4, occur near t = 0.66).

## Suggested caption skeleton (Science Advances style)

**Fig. 7. Stochastic leakage of the correction bits.**  Each panel shows, for one leakage model, the
expected Holevo information E[chi(t)] that the adversary can extract about the unrevealed correction bits
(top) and her expected maximal overlap F(t) with Bob's conditional state (bottom), Eq. (leakage-expected),
with the class probabilities P_K(t) of Supplementary Note (si:leakage-models), the corrected chi_K and F_K
of Supplementary Notes (si:holevo-derivation, app:fidelity), input alpha = sqrt(0.6), beta = sqrt(0.4) and
k1 = k2 = k = 1 (t in units of 1/k).  (**A**) Independent exponential leakage, (**B**) sequential leakage,
(**C**) burst leakage, each for the amplitude-damping parameter gamma = 0, 0.1, 0.2, 0.3 held fixed in
time (same colours in A-C): E[chi] falls from chi_empty = 1, 0.832, 0.717, 0.620 bit toward 0, F rises
from (1 + gamma)/2 = 0.50, 0.55, 0.60, 0.65 toward F_{1,2} = 1.000, 0.976, 0.956, 0.941; the grey band
marks the interval in which the F curves cross (0.65-1.50/k, 1.35-2.82/k, 1.12-1.48/k).  (**D**) Correlated
leakage at gamma = 0.5 for mu = 0, 0.3, 0.6, 0.9: the four curves coincide (differences < 0.002 bit and
< 0.001), falling from 0.452 bit and rising from 0.75 toward 0.929; the insets zoom on t = 0.65-0.67/k
(ordinate ranges 0.2305-0.2385 bit and 0.8349-0.8377), where the mu-dependence is largest (open marker:
zoomed point).  Both subplots are evaluated at the
fixed input; F_K is the largest eigenvalue of Eve's averaged state, not a reconstruction fidelity.
Source data: fig7_final_source_data.csv.

## Verification carried out by the script on every run (audit.txt)

- Per-class chi_K, F_K re-typed from the manuscript equal `holevo_correct.chi_K_closed` / `F_lam_closed`
  (1e-12) and the 3-qubit simulation `chi_K_sim` / `F_lam_sim` (1e-9) for gamma = 0, 0.1, 0.2, 0.3, 0.5.
- Every plotted value equals `expected_curves` (1e-12); P_K equals `hc.P_K`, P_K >= 0, sum_K P_K = 1
  (1e-12); 11-point subsample per curve equals the P_K-weighted simulation (1e-9).
- Limits: E[chi](0) = chi_empty, F(0) = (1 + gamma)/2, E[chi](50/k) = 0, F(50/k) = F_{1,2} (1e-15);
  E[chi] strictly decreasing, F strictly increasing; chi ordering in gamma kept; exactly one crossing per
  pair of F curves in A-C; burst reductions; correlated mu = 0 / 1 = independent / burst.
- Quoted numbers reproduced (chi_empty, F_empty, F_{1}, F_{1,2}, the gamma = 0.5 values, the panel-D
  spreads, the crossing windows); prototype CSVs reproduced to 5e-11.
- Panel D insets: data equal `expected_curves` (1e-12); the window contains the point of largest
  mu-spread; every curve lies inside the inset's ordinate range; inset boxes (frame + tick labels) and
  the connectors clear of all curves / text boxes (asserted); explicit inset audit (4 curves, 4 colours,
  labels set, tick labels >= 6 pt) because `scifig.audit` iterates `fig.get_axes()` only (the inset tick
  labels are nevertheless in its figure-wide text check: 113 items >= 6 pt).
- Eight-colour palette PASS; legend and annotation boxes clear of every curve (1 pt pad, asserted);
  `scifig.audit(target_width='double', journal_mode=True)`: **0 FAIL, 0 WARN**; the four SI panels
  (`target_width=8.5`): 0 FAIL, 0 WARN each; mathtext glyphs >= 6.5 pt.

## Hand-off checklist (sci-figure skill, section 7)

- Message stated in one sentence in the brief; A-C show the fan-out at t = 0 and the crossing band, D the
  coincidence note, at first glance.
- 4 curves per subplot; colour = one variable per panel in fixed order; validator PASS for all eight hues.
- One compact legend per panel (upper right of the top subplot) + direct annotations only for the crossing
  windows and the panel-D coincidence; nothing covers data (asserted).
- Text >= 6 pt at 18.3 cm (ticks 6 pt, smallest glyph 6.5 pt); bold panel letters A-D; axis labels with
  "(bits)", "(1/k)", "(dimensionless)".
- Audit: 0 FAIL, 0 WARN (main figure and the four SI panels).
- Files: PDF (vector) + PNG (600 dpi); script with the brief at the top; source-data CSV; audit.txt.
