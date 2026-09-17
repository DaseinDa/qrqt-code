# QRQT figure code

Code and Source Data for **Quantum-Resistant Quantum Teleportation**
(Jin, Chandra, Azari, Cheng, Shen, Seshadreesan & Liu).

Everything here regenerates a figure in the paper or the numerical values behind one.
`FIGURE_INDEX.md` says, for every graphic in the paper, which script produces it and how
that was checked. Read it first: two figures come from the collaborator and are not here,
one is vector artwork that needs Adobe Illustrator for its final step, and one is a
reimplementation rather than the original script.

## Install

```bash
python -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

The pinned versions are the ones the figures were verified against. `matplotlib` must
resolve **DejaVu Serif**, which is what the published PDFs were rendered with; a different
serif font changes the page geometry of the supplementary figures.

## Regenerate the figures

```bash
cd figures/fig3           && python pqc_plot_fig3a.py && python pqc_plot_fig3b.py
cd figures/fig5           && python plot_fig5_joint_probability.py
cd figures/supplementary  && python plot_pade_validation.py
```

Each writes into its own `output/` directory. Set `QRQT_OUTDIR` to send them elsewhere.
Nothing writes into the manuscript tree.

To check a regenerated file against the submitted one:

```bash
sha256sum -c checksums/published_figures.sha256
```

Expect the PDFs to differ only in the embedded `/CreationDate`; compare the 300 dpi PNG
renders for a byte-level match.

Fig. 2 is different. `figures/fig2/build_diagram.cjs` needs Node (verified on v20):

```bash
cd figures/fig2 && node build_diagram.cjs
```

That regenerates the intermediate vector drawing. The published PDF was then produced from
it in Adobe Illustrator with the scripts under `figures/fig2/illustrator/`, so the final
step cannot be run headlessly.

## Source Data

```bash
cd source_data && python make_source_data.py
```

writes the CSVs for Figs. 3a, 3b and 5 and Supplementary Figs. 1 and 2, plus the coherence
benchmarks and shaded bands of the top panel of Fig. 3b. They are generated from the same
code that draws the figures, so they cannot drift from the plots. The values behind
Figs. 6 and 7 and the Supplementary Holevo figures must come from the collaborator who
produced them.

## Layout

```
figures/fig3/            Fig. 3a and 3b: memory lifetime vs communication distance
figures/fig5/            Fig. 5: joint classical-quantum attack probability
figures/supplementary/   Supplementary Figs. 1 and 2: Pade approximation validation
figures/fig2/            Fig. 2: overview figure (Node + Illustrator)
source_data/             Source Data generator and the generated CSVs
checksums/               SHA-256 of the six published figure files
```
