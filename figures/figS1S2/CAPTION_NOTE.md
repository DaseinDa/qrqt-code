# Supplementary Figs. S1 and S2 (final) -- what the captions must say

Labels: `fig:pade_comparison` (S1) and `fig:attack_time` (S2) in `si_v2/appendix_BKZ.tex`
(figure environments near lines 640-660). The SI text itself was NOT edited; it still points
at `Figure/log2pr_vs_m.pdf` and `Figure/log2Pr_vs_TBKZ.pdf`. To use the new figures the
`\includegraphics` paths have to be switched to `figS1_final.pdf` / `figS2_final.pdf` and the
two "panel~(b)" mentions in the captions to "panel~B" (bold uppercase letters, Science
Advances style). Everything in this folder was produced read-only from the SI note and from
the original plotting script `code_from_D/PQNet/PQNet_Figure/improve/Figure61.py`.

Files (this folder, `figures_v2/figS1S2/final/`):

| figure | script | vector | raster (600 dpi) | source data | audit |
|---|---|---|---|---|---|
| S1 | `figS1_final.py` | `figS1_final.pdf` | `figS1_final.png` | `figS1_final_source_data.csv` | `audit_S1.txt` |
| S2 | `figS2_final.py` | `figS2_final.pdf` | `figS2_final.png` | `figS2_final_source_data.csv` | `audit_S2.txt` |

Both: single column, 8.5 x 7.8 cm (user: 8.5 cm; bbox-tight PDF page 8.4 x 7.7 cm), two
stacked panels A (value) / B (relative error) sharing the x axis, panel letters bold
uppercase 9 pt, axis labels 7.5 pt, tick labels / legend / notes 7 pt, mathtext shrink
factor 6/7 so every sub/superscript prints at 6.0 pt (asserted per glyph), DejaVu Sans
embedded (Type 42), no grid, no in-panel titles. Colours (Okabe-Ito, validated: min dE
normal 18.7, protan 13.0, deutan 11.0, tritan 8.6): exact = blue #0072B2 solid, Padé =
vermilion #D55E00 dashed drawn on top (so both colours stay visible where the curves
coincide), relative error = green #009E73. Legend (conventional, frameless, in an empty
corner) in panel A of each figure: "Exact (erf product)", "Padé approximation". Panel B has a
single series named by its y label ("Relative error"). scifig audit: 0 FAIL / 0 WARN for both.

## Model (identical in both figures; SI Note 2-3)

log2 P_LWE = sum_{i=1}^{m} log2 erf(W_i),   W_i = d_i ||b1|| sqrt(pi)/(2 s) * 2^{-2(i-1) a/(log2 T_BKZ + b)}
(SI Eq. PLWE_final = main-text Eq. lwe_probability with the GSA decay and the runtime fit
log2 delta_root = a/(log2 T_BKZ + b)). This is the same P_LWE(T) as in main-text Fig. 5
(`fig5_final.py`), only with other illustrative parameters.
Padé (Winitzki, SI Eq. pade_log_prob): log2 P_LWE ~ sum_i 1/2 log2(1 - exp(-W_i^2 (4/pi + w W_i^2)/(1 + w W_i^2))),
w = 0.140012.
Relative error (panel B of both figures) = |log2 P_Padé - log2 P_exact| / |log2 P_exact|.
Both sums are evaluated in double precision with scipy's erf, in the expression order of the
original script, so the figures reproduce the old ones exactly (checked value by value).

## Fig. S1 -- `fig:pade_comparison` (log2 P_LWE versus the lattice rank m)

What it plots: A: log2 P_LWE in units of 10^-8 versus m = 5, 6, ..., 60 (integer rank =
number of Gram-Schmidt layers), exact (blue) and Padé (vermilion dashed). B: relative error
on a log axis, drawn for m = 35-60 only.
Parameters (illustrative set A of SI Table tab:bkz_params; must be stated with the word
"illustrative"): a = 0.3, b = 2.7, T_BKZ = 2^30 s, ||b1|| = 10, d_i = 2, s = 2, m from 5 to 60.
Numbers (asserted in the script):
- log2 P_LWE at m = 60: exact -1.230e-8, Padé -1.175e-8; both are exactly 0 in double
  precision for m <= 32 (exact) / m <= 31 (Padé), and |log2 P_LWE| < 1e-15 for m <= 34.
- relative error: first drawn point m = 35 (0.143); minimum 1.66e-3 at m = 44 (sign change
  of Padé - exact); 4.45e-2 at m = 60; range 1.7e-3 to 0.14, i.e. the caption's
  "10^-3-10^-1" is right (the maximum is 1.4 x 10^-1).
- Why B starts at m = 35: the original figure masked the relative error to |log2 P_LWE| >
  1e-15; for smaller m the values are 0 or a few ulp and the ratio is meaningless. The new
  figure keeps that mask and SAYS so on the plot (grey note in B: "not drawn for m < 35:
  |log2 P_LWE| < 10^-15 (double-precision floor)"). The caption should keep its sentence that
  an absolute agreement better than 10^-9 registers as a relative error of 10^-3-10^-1
  because log2 P_LWE itself is of order 10^-8 or smaller.
- Caveat for the caption writer (not shown in the figure): for m <= 45 the drawn relative
  error is dominated by rounding, not by the approximation (|log2 P| ~ 1e-15 ... 1e-12
  against a resolution of 1e-16). Column 5 of the CSV gives the same quantity evaluated
  with 40 significant digits: true relative error 0.28 at m = 5, 4.3e-2 at m = 35, 1.4e-3 at
  m = 44, 4.4e-2 at m = 60; drawn and true values agree to < 5 % for m >= 46. So the true
  Padé error over the plotted range is 1e-3-3e-1, the drawn one 2e-3-1.4e-1; the caption's
  order-of-magnitude statement holds either way. Nothing about this is new content: the
  figure shows exactly what the old one showed.
Data file: `figS1_final_source_data.csv` (m, log2P_LWE_exact, log2P_LWE_pade,
relative_error_drawn [nan where not drawn], relative_error_40digit_reference).

## Fig. S2 -- `fig:attack_time` (log2 P_LWE versus the BKZ time)

What it plots: A: log2 P_LWE in units of 10^3 versus log2 T_BKZ = 20, 22, ..., 98 (T_BKZ in
seconds; the x label says so) at the fixed rank m = 500, exact (blue, 20-98) and Padé
(vermilion dashed, 58-98 only). B: relative error on a log axis, 58-98.
Parameters (illustrative set B of SI Table tab:bkz_params; the caption must keep its
sentence that these are NOT the Lindner-Peikert fit (1.8, 110)): a = 1.8, b = 2.7, m = 500,
||b1|| = 10, d_i = 2, s = 2, log2 T_BKZ from 20 to 98.
Numbers (asserted in the script):
- exact log2 P_LWE: -18162 at log2 T_BKZ = 20, -5839 at 58, -2966 at 98.
- Padé: finite from log2 T_BKZ = 58 onward on the step-2 grid (first finite point 58; at 56
  the sum is -inf because 1 - exp(-W_i^2 ...) underflows to 0 for the smallest W_i; on a
  finer grid the threshold lies between 56.5 and 57). The figure marks the start with the
  annotation "Padé evaluated from log2 T_BKZ = 58" in A and the note "not evaluated below
  58: the erf arguments underflow" in B; the caption's existing explanation (underflow of the
  individual error-function arguments in double precision) is correct and should stay.
- relative error: 4.39e-5 at 58 (maximum), 2.77e-5 at 60, minimum 3.57e-7 at 62, 5.74e-6 at
  64, then 2.5e-6 ... 6.13e-6 at 98. The caption's "stays below 5 x 10^-5" holds
  (max 4.4 x 10^-5), and so does the S1 caption's cross-reference "below 10^-3 in the
  cryptographically relevant regime |log2 P_LWE| >~ 10^2".
Data file: `figS2_final_source_data.csv` (log2_T_BKZ_s, log2P_LWE_exact, log2P_LWE_pade
[nan below 58], relative_error [nan below 58]).

## Differences from the old figures (styling only; content identical)

- Panel letters: bold uppercase A, B outside the panel corner (old: "(a)", "(b)" inside).
- No open circle/square markers on the model curves (old: markers every 3rd point from
  m >= 45, every 5th point in T); the dashed-on-solid two-hue drawing already separates the
  coincident curves, and the markers were not data points.
- No light-green fill under the relative-error curve, no dotted grid, no top/right spines,
  no inward ticks; Okabe-Ito colours instead of the matplotlib defaults; sans-serif 7-7.5 pt
  at the final size instead of a 6.5-inch serif figure scaled down.
- S2 panel A: y values in units of 10^3 (label "(x 10^3)") instead of "-18,000"-style ticks;
  x label "BKZ time log2 T_BKZ (T_BKZ in s)" instead of a bare "log2 T_BKZ"; S1 x label
  "Lattice rank m (number of Gram-Schmidt layers)" instead of "m".
- In-plot explanations added (anti-pattern 11, "a curve that stops without saying why"):
  the S1-B note on the double-precision floor, the S2-A annotation and S2-B note on the
  underflow threshold 58. These are the only annotations; no other numbers are written on
  the plots.
- Grid, arithmetic and masks are those of the original script, so every drawn value is the
  old one.

## Draft captions (adapt wording; keep every number)

**Fig. S1. Padé approximation of the LWE success probability versus the lattice rank.**
Exact (blue) and Padé-approximated (vermilion, dashed) log2 P_LWE versus the number of
Gram-Schmidt layers m (the rank of the embedded lattice), Eq. (PLWE_final) and
Eq. (pade_log_prob). (A) log2 P_LWE in units of 10^-8. (B) Relative error
|log2 P_Padé - log2 P_exact| / |log2 P_exact|, drawn for m >= 35 only: for smaller m,
|log2 P_LWE| < 10^-15 lies at the double-precision floor and the ratio is not defined.
Over the range plotted log2 P_LWE is itself of order 10^-8 or smaller, so an absolute
agreement better than 10^-9 registers as a relative error of 10^-3-10^-1; in the
cryptographically relevant regime, |log2 P_LWE| >~ 10^2, the relative error of the same
approximation stays below 10^-3 (Fig. S2). The approximation reduces computation time by
orders of magnitude. Illustrative parameters (Table tab:bkz_params): a = 0.3, b = 2.7,
T_BKZ = 2^30 s, ||b1|| = 10, d_i = 2, Gaussian parameter s = 2, with m running from 5 to
60. Source data: figS1_final_source_data.csv.

**Fig. S2. Padé approximation of the LWE success probability versus the BKZ time.**
Exact (blue) and Padé-approximated (vermilion, dashed) log2 P_LWE versus the BKZ
computation time available to the adversary, at the fixed lattice rank m = 500. (A)
log2 P_LWE in units of 10^3. (B) Relative error, which stays below 5 x 10^-5 wherever the
approximation is evaluated. The Padé curve is drawn only from log2 T_BKZ = 58 onward,
because at shorter attack times the individual error-function arguments underflow double
precision. In the joint attack the time available to this stage is T_BKZ = t0 + t, where the
storage time t of the intercepted qubit is limited by Eve's memory lifetime T_coh^E while
the head start t0 is not. The parameters are illustrative values, chosen so that both curves
are visible on one axis (Table tab:bkz_params); they are not the empirical Lindner-Peikert
fit (a, b) = (1.8, 110), which is quoted in Methods as the reference calibration but is not
used for any figure (main-text Fig. 5 uses the illustrative pair (0.3, 2.7)). Parameters:
a = 1.8, b = 2.7, m = 500, ||b1|| = 10, d_i = 2, Gaussian parameter s = 2, with
log2 T_BKZ (T_BKZ in s) running from 20 to 98. Source data: figS2_final_source_data.csv.

## Hand-off checklist (sci-figure skill)

- Message stated in one sentence in each script's brief; visible at first glance (dashed on
  solid; error curve under 10^-4 in S2).
- <= 6 curves per panel (2 + 1); colour = evaluation method in fixed order; validator PASS.
- Compact legend in A of each figure, in an empty corner (clearance to data 29 mm / 23 mm);
  notes 5-6 mm from the curves; nothing covers data.
- Text >= 6 pt at the final width (smallest glyph 6.00 pt in the sub/superscripts); panel
  letters A/B; axis labels with units or "(x 10^k)".
- Audit: 0 FAIL, 0 WARN (both figures).
- Files: PDF (vector) + PNG (600 dpi) + CSV + script with the brief at the top.
