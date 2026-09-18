# Figure index

One row per graphic in *Quantum-Resistant Quantum Teleportation*, with the code in this
repository that produces it and how that was verified. Established by a provenance audit on
2026-09-17, re-verified on 2026-09-18: every candidate script was re-run and its output
compared against the submitted PDFs. The six published files are checksummed in
`checksums/published_figures.sha256`, whose paths are relative to the manuscript tree, not
to this repository.

| Figure | Published file | Code here | Status |
|---|---|---|---|
| Fig. 1 | inline TikZ in the manuscript | none | Schematic, no computation |
| Fig. 2 | `Figure/fig2_overview.pdf` | `figures/fig2/` | Scripted vector artwork finished in Adobe Illustrator; see below |
| Fig. 3a | `Figure/fig3a_memory_time_short_range.pdf` | `figures/fig3/pqc_plot_fig3a.py` | **Reproduces exactly** |
| Fig. 3b | `Figure/fig3b_memory_time_long_range.pdf` | `figures/fig3/pqc_plot_fig3b.py` | **Reproduces exactly** |
| Fig. 4 | inline TikZ in the manuscript | none | Schematic, no computation |
| Fig. 5 | `Figure/P_joint.pdf` | `figures/fig5/plot_fig5_joint_probability.py` | **Reimplementation**; see below |
| Fig. 6 | `Holevo/vector/Holevo_AD.pdf`, `Holevo_gamma.pdf` | `source_data/make_holevo_source_data.py` | Co-author's plot; curves recomputed from the paper's closed forms and verified against both panels |
| Fig. 7 | `Holevo/vector/ILM_1.pdf`, `SLM.pdf`, `BLM_1.pdf`, `CLM_1.pdf` | `source_data/make_holevo_source_data.py` | Co-author's plot; curves recomputed from the paper's closed forms and verified against all four panels |
| Supplementary Fig. 1 | `Figure/log2pr_vs_m.pdf` | `figures/supplementary/plot_pade_validation.py` | **Reproduces exactly** |
| Supplementary Fig. 2 | `Figure/log2Pr_vs_TBKZ.pdf` | `figures/supplementary/plot_pade_validation.py` | **Reproduces to within antialiasing on one gridline** (49 differing pixels at 300 dpi) |
| Supplementary Figs. 3-8 | the same six `Holevo/vector/` files as Figs. 6 and 7 | none | The Supplementary Information reproduces the main-text Holevo panels; no separate artwork |

"Reproduces exactly" means the regenerated PDF differs from the published one only in the
embedded `/CreationDate` (6-8 bytes) and the 300 dpi renders are pixel-identical.

The two published Fig. 6 panels were resampled to 300 dpi for the Nature Communications
version (`*_300dpi.png`); the underlying `Holevo_AD.jpg` and `Holevo_gamma.jpg` are the
co-author's originals and are what the recomputation was checked against.

## Fonts

Both plotting families originally asked for `['Times New Roman', 'DejaVu Serif']`, so which
font they got depended on the machine, and neither family reproduced on a machine whose
resolution differed from the author's. Each script now pins one family:

* `figures/supplementary/plot_pade_validation.py` -> **DejaVu Serif**. Verified: zero
  differing pixels for Supplementary Fig. 1, 49 for Supplementary Fig. 2. With Times New
  Roman available the page geometry changes (1736x1489 instead of 1767x1494) and neither
  panel reproduces.
* `figures/fig3/fig3_common.py` -> **Times New Roman**, which is what the published Fig. 3
  PDFs used. Verified: zero differing pixels for both panels.

## Figs. 6 and 7

The co-author's plotting code is not available. `source_data/make_holevo_source_data.py`
therefore evaluates the closed forms the paper states, at the parameters printed on each
panel, to produce the Source Data. It is an independent recomputation, not the original
code. Its agreement with the published panels was checked two ways: by drawing the
recomputed curves on the same axes and comparing them with the published images panel by
panel (all six panels agree, including the distinctive features that would expose an
error), and against values read off the printed figures (`--verify`).

`--verify` runs twelve checks against values read off the panels by eye, with a tolerance
of 0.006. Eleven pass; the twelfth is 0.0005 outside it and the script therefore reports
`False`. The full table, including the rows that are close to the tolerance:

| Check | Read off the panel | Recomputed | diff |
|---|---|---|---|
| Fig. 7a E[χ(0)], γ = 0.0 / 0.1 / 0.2 / 0.3 | 1.000 / 0.890 / 0.820 / 0.780 | 1.0000 / 0.8900 / 0.8246 / 0.7820 | ≤ 0.0046 |
| Fig. 7a F(5), γ = 0.0 / 0.1 | 0.997 / 0.982 | 0.9972 / 0.9829 | ≤ 0.0009 |
| Fig. 7a F(5), γ = 0.2 | 0.965 | 0.9715 | **0.0065** |
| Fig. 7a F(5), γ = 0.3 | 0.958 | 0.9632 | 0.0052 |
| Fig. 7d E[χ(0)], γ = 0.5 | 0.745 | 0.7498 | 0.0048 |
| Fig. 7d F(5), μ = 0.0 | 0.955 | 0.9564 | 0.0014 |
| Fig. 7* F(0), any model | 0.500 | 0.5000 | 0.0000 |
| Fig. 6a χ at γ = 0 | 1.000 | 1.0000 | 0.0000 |
| Fig. 6a minima at γ = 0.5, \|α\|² = 0.1…0.5 | 0.15, 0.28, 0.41, 0.53, 0.65 | same | — |

The three largest diffs all sit on the steep part of a fidelity curve, where reading a
value off a printed panel is worth about ±0.005; the visual overlay, which does not depend
on eyeball readings, shows no discrepancy. Replace these CSVs with the co-author's own
numbers when they become available.

### Lettering

The published panels are raster, 790 px wide, with lettering set for a full-page view. At
the size they are placed in the Nature Communications layout the axis tick labels print at
about 2.0 pt and the in-panel titles at about 3.5 pt, against the 5-7 pt Nature asks for.
Resolution is not the problem - the panels place at 365 dpi (main text) and 320 dpi
(Supplementary Information) - so no placement change fixes it.

`figures/holevo/redraw_holevo_figures.py` redraws all six panels from the Source Data as
vector PDFs at the placed size with 6-7 pt lettering, keeping the same curves, colours,
legends and axis ranges and dropping the in-panel titles, which repeat the figure legend.
**The manuscript now uses these**, at `Holevo/vector/*.pdf`, in both the main text and
the Supplementary Information; the co-author's original rasters are kept beside them in
`Holevo/`. See `figures/holevo/README.md`.

The substitution was checked by reading both versions back off the page. Each panel was
rendered, its axes calibrated from its own tick marks (matplotlib pads the data range by
5%, so the frame is not at the round numbers), and each series extracted as the widest
connected component of its colour, which excludes legend swatches and the zoom inset.
Against the same Source Data, the published rasters agree to **0.011** data units worst
case and the vector panels to **0.020** (the larger figure is Fig. 6a, where the marker
glyphs sit on the curve). Both are within one drawn line width, so the substitution does
not move any curve.

## Fig. 2

`figures/fig2/build_diagram.cjs` (Node, no npm dependencies) draws the whole overview
figure from `vector_charts.json` and `vector_people.json`, including the four schematic
leakage-model insets in panel (d). Re-running it regenerates the intermediate SVG
byte-identically. The final published PDF was then assembled in Adobe Illustrator using the
`.jsx` scripts under `figures/fig2/illustrator/`, so the last step **cannot be reproduced
headlessly** and needs Illustrator; set the `base` variable at the top of each `.jsx` to
your project root first. The helper `match_figure_palette.cjs` needs `npm install xml-js`.
The insets are hand-placed schematic icons of each leakage model's event pattern, not plots
of the closed-form expressions, which is what the figure legend says.

`build_diagram.cjs` writes its generated SVG/JSON next to itself rather than into an
`output/` directory; those generated files are gitignored.

## Fig. 5

The script that produced the submitted `P_joint.pdf` (created 2026-06-11) did not survive
in any of the project's code folders. `figures/fig5/plot_fig5_joint_probability.py` is a
post-hoc reimplementation written from Eq. (8) of the main text and the parameters printed
in the Fig. 5 legend. It is included because it reproduces the two values annotated on the
published figure:

| Quantity | Published annotation | This script |
|---|---|---|
| optimal attack time `t*` | 16 s | 16.40 s |
| `P_joint(t*)` | 0.645 | 0.6450 |

That agreement is what justifies using it to generate `source_data/SourceData_Fig5.csv`.
It regenerates the figure; it is not the original code, and the repository does not claim
otherwise.

`figures/fig5/joint2_beautiful_as_provided.py` is the author's own most recent working
script for this figure, kept as provided. It does **not** regenerate the published figure:
it uses `m = 80` and `T_coh = 1` s, plots log2 of the probabilities, and takes
`P_SWAP = exp(-t/T_coh)` rather than the published `(1 + exp(-t/T_coh))/2`. Its closed form
for `P_LWE` is the one the paper states. Run as provided it calls `plt.show()` and writes
`log2Pr_joint_beautiful.pdf` into the current working directory.

**Warning about a decoy.** The author's older working folder contains a file named
`claude_figure2/P_joint.pdf`. Despite the name it is *not* the published figure: it is the
output of the superseded script described in the previous paragraph. That PDF is
deliberately excluded from this repository.

## Source Data provenance

`source_data/make_source_data.py` imports `PQC_DATA` and `PLOT_ORDER` from `fig3_common`
and `p_lwe`, `p_swap` and the parameters from `plot_fig5_joint_probability`, so the CSVs
for Figs. 3a, 3b and 5 cannot drift from those plots. It does **not** import the
supplementary panel's functions or the Fig. 3b coherence-benchmark table; those are retyped
copies, so if `plot_pade_validation.py` or `pqc_plot_fig3b.py` changes, check them by hand.

The Padé column of `SourceData_SupplementaryFig2.csv` is blank for `log2 T_BKZ <= 56`: the
published plotting script evaluates `sqrt(1 - exp(x))`, which cancels to exactly zero in
double precision there, so the published figure draws no Padé point below about 58. A
`log2_P_LWE_pade_stable` column computed with `expm1` gives the values the approximation
actually takes; over the rows the figure does draw, the two agree to 5e-5 in relative terms.

## A correction this audit produced

`plot_pade_validation.py` shows that the two supplementary panels use

* Supplementary Fig. 1: `a = 0.3`, `b = 2.7`, `T_BKZ = 2^30` s, `||b1|| = 10`, `d_i = 2`, `s = 2`, `m = 5..60`
* Supplementary Fig. 2: `a = 1.8`, `b = 2.7`, `m = 500`, `||b1|| = 10`, `d_i = 2`, `s = 2`, `log2 T_BKZ = 20..98`

The captions in the submitted Supplementary Information had the two `a` values transposed
and gave `m = 30`, `d_i = 1` for Supplementary Fig. 2, values that came from a superseded
script which produced no published figure and that cannot generate the plotted y-range.
Both captions were corrected on 2026-09-17 to match the code above.

The captions also claimed the approximation achieves `< 1e-4` relative error. Recomputed
from this code, the relative error on `log2 P_LWE` is `1.7e-3` to `1.4e-1` over the region
Supplementary Fig. 1 plots -- because `log2 P_LWE` there is itself of order `1e-8`, so an
absolute agreement better than `1e-9` still reads as a large relative error -- and better
than `5e-5` over the region Supplementary Fig. 2 plots. Both captions and the two places in
the main text that repeated the claim were corrected on 2026-09-18.

## What is deliberately not here

Superseded scripts that would mislead a reader, in particular anything still carrying BIKE
(dropped from the paper) or the pre-revision PQC latencies of 412-620 ns, which contradict
Table 1's 2.3-45.1 us; the two Python virtual environments; compiled bytecode; renamed
output files that collide with published filenames; and one image carrying an
AI-generation marker in its metadata that the paper does not use.

The one superseded script that *is* here, `joint2_beautiful_as_provided.py`, is kept at the
author's direction as the most recent script they hold for Fig. 5, and is labelled as such
in its own header and in the Fig. 5 section above.
