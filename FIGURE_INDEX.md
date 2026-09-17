# Figure index

One row per graphic in *Quantum-Resistant Quantum Teleportation*, with the code in this
repository that produces it and how that was verified. Established by a provenance audit on
2026-09-17 that re-ran every candidate script and compared the output against the submitted
PDFs; the six published files are checksummed in `checksums/published_figures.sha256`.

| Figure | Published file | Code here | Status |
|---|---|---|---|
| Fig. 1 | inline TikZ in the manuscript | none | Schematic, no computation |
| Fig. 2 | `Figure/fig2_overview.pdf` | `figures/fig2/` | Scripted vector artwork finished in Adobe Illustrator; see below |
| Fig. 3a | `Figure/fig3a_memory_time_short_range.pdf` | `figures/fig3/pqc_plot_fig3a.py` | **Reproduces exactly** |
| Fig. 3b | `Figure/fig3b_memory_time_long_range.pdf` | `figures/fig3/pqc_plot_fig3b.py` | **Reproduces exactly** |
| Fig. 4 | inline TikZ in the manuscript | none | Schematic, no computation |
| Fig. 5 | `Figure/P_joint.pdf` | `figures/fig5/plot_fig5_joint_probability.py` | **Reimplementation**; see below |
| Fig. 6 | `Holevo/Holevo_AD.jpg`, `Holevo_gamma.jpg` | none | Collaborator's; code held by that author |
| Fig. 7 | `Holevo/ILM_1.jpg`, `SLM.jpg`, `BLM_1.jpg`, `CLM_1.jpg` | none | Collaborator's; code held by that author |
| Supplementary Fig. 1 | `Figure/log2pr_vs_m.pdf` | `figures/supplementary/plot_pade_validation.py` | **Reproduces exactly** |
| Supplementary Fig. 2 | `Figure/log2Pr_vs_TBKZ.pdf` | `figures/supplementary/plot_pade_validation.py` | **Reproduces to within antialiasing on one gridline** |
| Supplementary Holevo figures | `Holevo/*.jpg` | none | Collaborator's |

"Reproduces exactly" means the regenerated PDF is byte-identical to the published one apart
from the embedded `/CreationDate`, and the 300 dpi PNG renders are md5-identical.

## Fig. 2

`figures/fig2/build_diagram.cjs` (Node) draws the whole overview figure from
`vector_charts.json` and `vector_people.json`, including the four schematic leakage-model
insets in panel (d). Re-running it regenerates the intermediate SVG byte-identically. The
final published PDF was then assembled in Adobe Illustrator using the `.jsx` scripts under
`figures/fig2/illustrator/`, so the last step **cannot be reproduced headlessly** and needs
Illustrator. The insets are hand-placed schematic icons of each leakage model's event
pattern, not plots of the closed-form expressions, which is what the figure legend says.

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

**Warning about a decoy.** The author's older working folder contains a file named
`claude_figure2/P_joint.pdf`. Despite the name it is *not* the published figure: it is the
output of a superseded script (`m = 80`, `T_coh = 1 s`, log-scale axis,
`P_SWAP = e^{-t/T_coh}` rather than `(1 + e^{-t/T_coh})/2`) that was renamed. It is
deliberately excluded from this repository.

## A correction this audit produced

`plot_pade_validation.py` shows that the two supplementary panels use

* Supplementary Fig. 1: `a = 0.3`, `b = 2.7`, `T_BKZ = 2^30` s, `||b1|| = 10`, `d_i = 2`, `s = 2`, `m = 5..60`
* Supplementary Fig. 2: `a = 1.8`, `b = 2.7`, `m = 500`, `||b1|| = 10`, `d_i = 2`, `s = 2`, `log2 T_BKZ = 20..98`

The captions in the submitted Supplementary Information had the two `a` values transposed
and gave `m = 30`, `d_i = 1` for Supplementary Fig. 2, values that came from a superseded
script which produced no published figure and that cannot generate the plotted y-range.
Both captions were corrected on 2026-09-17 to match the code above.

## What is deliberately not here

Superseded scripts that would mislead a reader, in particular anything still carrying BIKE
(dropped from the paper) or the pre-revision PQC latencies of 412-620 ns, which contradict
Table 1's 2.3-45.1 us; the two Python virtual environments; compiled bytecode; renamed
output files that collide with published filenames; and one image carrying an
AI-generation marker in its metadata that the paper does not use.
