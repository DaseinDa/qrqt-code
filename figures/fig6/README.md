# Fig. 6, final — corrected Holevo quantity χ (option (a))

**Status: final; corrected derivation approved 2026-11-03 (option (a):
amplitude damping on Bob's half of the Bell pair before Alice's Bell measurement).** The figure itself
carries no draft marking (journal style). Formula, numbers, layout and size are those of
`../variant_A/` (the judges' winner); the judges' three ranked edits were applied, and the
user's rule of 2026-10-21 (every figure carries a conventional legend; label blocks or
line-end labels alone are not accepted) replaced all direct labels by legends.

| file | content |
|---|---|
| `fig6_final.py` | plotting script; FIGURE BRIEF docstring at the top; data assertions, six-colour palette validation, legend-clearance and label-collision assertions and `scifig.audit` run on every execution (the script aborts on any FAIL or WARN) |
| `fig6_final.pdf`, `fig6_final.png` | vector + 600 dpi raster, 12.0 x 5.5 cm (1.5 column, Science Advances) |
| `fig6_final_panelA.csv` | source data, panel A: `gamma, alpha_sq, chi_bits` for \|α\|² = 0.1, 0.3, 0.5 (1001 γ points each) |
| `fig6_final_panelB.csv` | source data, panel B: `alpha_sq, gamma, chi_bits` for γ = 0.1, 0.3, 0.5 (1001 \|α\|² points each) |
| `audit.txt` | complete console output of the last run (data assertions, palette validation, `scifig.audit`) |

Run: `MPLBACKEND=Agg python fig6_final.py` (reads only the skill scripts and
`../../../holevo/holevo_correct.py`; writes only into this folder; bytecode caching is
switched off so no `__pycache__` is left elsewhere).

## Judges' edits applied (verdict section "fig6", ranked)

1. **Panel A labels.** The three leader lines of variant A are replaced by a compact
   conventional legend in the empty upper-right region: `|α|² = 0.5 / 0.3 / 0.1`, entries
   top to bottom in curve order (coloured line handles, black 6.5 pt text, no frame). A
   leader to the 0.3 curve cannot reach it from below without crossing the blue curve
   (blue lies below vermilion everywhere in (0, 1)), so a legend is the only crossing-free
   option. The script asserts that the legend box (1 pt pad) contains no data point
   (nearest curve 0.277 bit away).

**Legends (user rule 2026-10-21).** Panel B's line-end labels were likewise replaced by a
compact legend `γ = 0.1 / 0.3 / 0.5` (curve order) in the empty lower-right region below
the γ = 0.5 curve and entirely to the right of the dotted guide (box |α|² ∈ [0.57, 0.91],
χ ∈ [0.02, 0.29]; nearest curve 0.074 bit away; asserted). The `χ(1) = 0` annotation and
the "symmetric about ½" guide label are kept.
2. **Panel B symmetry guide.** Now mid grey `#777777`, 0.65 pt, coarse round dots
   (dash pattern (1.0, 3.0) x line width), drawn from χ = 0 to 0.90 and stopping below the
   kept label "symmetric about ½". Visible in print.
3. **Colours across panels.** All six hues are validated together (see below). The γ set of
   variant A (Okabe–Ito purple/orange/sky) fails the joint check (green–purple under
   deuteranopia 7.6 < 8) and vermilion–orange (15.6) / blue–sky were judged visibly too
   close, so the γ family was changed to magenta / mustard / cyan — the three hues that sit
   between blue, vermilion and green on the hue wheel. Both x-labels now end in
   "(dimensionless)".

## Colour map (fixed; use the same entity → colour in every figure of the paper)

| entity | hex | name | source |
|---|---|---|---|
| \|α\|² = 0.1 | `#0072B2` | blue | Okabe–Ito 0 |
| \|α\|² = 0.3 | `#D55E00` | vermilion | Okabe–Ito 1 |
| \|α\|² = 0.5 | `#009E73` | bluish green | Okabe–Ito 2 |
| γ = 0.1 | `#AA3377` | magenta | Tol "bright" purple |
| γ = 0.3 | `#E6AB02` | mustard | ColorBrewer Dark2 |
| γ = 0.5 | `#33BBEE` | cyan | Tol "vibrant" cyan |
| χ(1) = 0 marker, annotations | `#555555` | dark grey | — |
| symmetry guide | `#777777` | mid grey | — |

The \|α\|² family is unchanged from variant A and `holevo/fig6_comparison_v2.py`. The γ
family differs from both (they used Okabe–Ito 3, 4, 5); if γ = 0.1/0.3/0.5 appear in any
other figure of the paper, that figure should adopt the three hues above.

`scifig.validate_palette` on all six hues together (`audit.txt`):
min ΔE normal 18.5 (green–cyan; vermilion–mustard is also 18.5), protan 12.2 (blue–magenta),
deutan 10.3 (green–magenta), tritan 8.6 (blue–green, a pair inside panel A, unchanged from
the paper's \|α\|² map); all six within the lightness band → **PASS**.
Cross-panel pairs only: min ΔE normal 18.5, min ΔE CVD 10.3 (variant A: 15.6 / 7.6 FAIL).
Per panel: A 18.7 / 8.6, B 28.1 / 22.7.

`scifig.audit(target_width="onehalf", journal_mode=True)`: **0 FAIL, 0 WARN**
(12.0 cm width; 28 text items, smallest 6.0 pt; no overlapping text boxes; 3 curves per
panel; colour separation OK in both panels). The shared y-axis label is set on panel B in
code and hidden (drawn once, on panel A), so the audit records both panels as labelled.

## What the caption must say

- Title sentence (Science style, bold): corrected Holevo quantity of the Bell-outcome-
  conditioned states under amplitude damping of Bob's half of the Bell pair.
- Definition used for both panels (must match the text exactly):
  χ = h(γ) − [h(δ_β) + h(δ_α)]/2, δ_x = sqrt(1 − 4γ(1−γ)|x|⁴), h(x) = H₂((1+x)/2),
  with the damping applied before Alice's Bell measurement (option (a)).
- **(A)** χ versus the damping γ for \|α\|² = 0.1, 0.3, 0.5 (blue, vermilion, green);
  χ = 1 bit at γ = 0 and χ(γ = 1) = 0 (open circle). State explicitly:
  **"the 0.3 and 0.5 curves differ by less than about 0.03 bit"** (the actual maximum
  difference is 0.020 bit, at γ = 0.5), so that readers do not expect visible separation.
- **(B)** χ versus the input weight \|α\|² for γ = 0.1, 0.3, 0.5 (magenta, mustard, cyan);
  χ is symmetric about \|α\|² = 1/2 (dotted guide) with its maximum there and equal values
  at \|α\|² = 0 and 1.
- The quoted check values of the text, at \|α\|² = 0.6: χ = 0.832, 0.620, 0.452 bit for
  γ = 0.1, 0.3, 0.5 (reproduced by the plotted formula; asserted in the script).
- γ and \|α\|² are dimensionless; χ is in bits (both already in the axis labels).
- Source data: `fig6_final_panelA.csv` and `fig6_final_panelB.csv`.

## Verification carried out by the script on every run

- χ(γ = 0) = 1 bit, χ(γ = 1) = 0, monotone decreasing in γ, symmetric about \|α\|² = 1/2 with
  the maximum at 1/2, end values h(γ) − h(|1 − 2γ|)/2; ordering χ(0.5) ≥ χ(0.3) ≥ χ(0.1).
- Every plotted curve equals `holevo/holevo_correct.py::chi_K_closed` (1e-12) and its
  3-qubit density-matrix simulation `chi_K_sim` (1e-9) at γ ∈ {0, 0.1, 0.3, 0.5, 0.9, 1}.
- Quoted values 0.832 / 0.620 / 0.452 bit at \|α\|² = 0.6 reproduced (tolerance 1.5e-3).
- max |χ(0.5) − χ(0.3)| < 0.03 bit (caption statement).

## Hand-off checklist (sci-figure skill, section 7)

- Message stated in one sentence in the brief; both panels show it at first glance.
- 3 curves per panel; colour = one variable per panel in fixed order; six-colour validator PASS.
- Conventional legends (user rule 2026-10-21): A upper right in curve order, B lower right
  below γ = 0.5 and right of the guide; both asserted to cover no data (audit: no legend
  covers a curve).
- Text ≥ 6 pt at 12 cm; bold panel letters A, B; axis labels with "(bits)" / "(dimensionless)".
- Audit: 0 FAIL, 0 WARN.
- Files: PDF (vector) + PNG (600 dpi); script with the brief at the top; source-data CSVs.
