# Holevo figures

Figs. 6 and 7 of the main text and the Holevo figures of the Supplementary Information
were produced by the co-author who carried out the information-theoretic analysis. Their
code is not in this repository and is available from that author on request.

The quantities plotted are defined in the paper: the per-class Holevo quantities and
fidelities in Results, and the four stochastic leakage models in Supplementary Note 10.
`../../source_data/make_holevo_source_data.py` recomputes them from those closed forms to
produce the Source Data; see `FIGURE_INDEX.md` for how that recomputation was checked
against the published panels.

## `redraw_holevo_figures.py` — a typographic alternative, not the published artwork

The published panels are JPEGs 790 px wide with lettering set for a full-page view. Placed
at Nature Communications size the axis tick labels print at about **2.0 pt** and the
in-panel titles at about 3.5 pt, against the 5–7 pt Nature asks for. Resolution is not the
problem (the panels place at 365 dpi); the type is too small relative to the plot, and no
placement change fixes that — it needs a re-export.

This script redraws the same six panels from the verified Source Data: same curves, same
colours, same legends, same axis ranges. What changes is that the output is vector PDF
drawn at exactly the size it is placed at, with 7 pt axis labels and 6 pt ticks and
legends, and that the in-panel titles are dropped because each one repeats what the figure
legend already says.

```bash
python redraw_holevo_figures.py --outdir <dir> --compare
```

Measured with `--compare`, smallest lettering at placed size:

| panel | published raster | redrawn vector |
|---|---|---|
| Fig. 6a `Holevo_AD` | 2.9 pt | 6 pt (4.2 pt superscript) |
| Fig. 6b `Holevo_gamma` | 2.8 pt | 6 pt (4.9 pt superscript) |
| Fig. 7a `ILM_1` | 2.0 pt | 6 pt |
| Fig. 7b `SLM` | 2.0 pt | 6 pt |
| Fig. 7c `BLM_1` | 2.0 pt | 6 pt |
| Fig. 7d `CLM_1` | 2.0 pt | 5 pt (zoom-inset ticks) |

**The manuscript uses these PDFs**, written to `Holevo/vector/`, for main-text Figs. 6
and 7 and for Supplementary Figs. 3-8. The co-author's original rasters stay in
`Holevo/` and the Code availability statement records that the analysis behind the
panels is the co-author's and that their original plotting code is available on request.

Reverting is six `\includegraphics` paths in `nc_main_skeleton.tex` and
`_nc_work/si/holevo_0*.tex`.

The curves were checked both ways round: read back off the page with tick-mark axis
calibration and connected-component extraction, the published rasters agree with the
Source Data to 0.011 data units worst case, and these vector panels to 0.020 - both
inside one drawn line width.
