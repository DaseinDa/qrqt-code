# QRQT -- code and Source Data

Code and data behind **Quantum-Resistant Quantum Teleportation** (Xin Jin, Nitish Kumar Chandra,
Mohadeseh Azari, Jinglei Cheng, Zilin Shen, Kaushik P. Seshadreesan, Junyu Liu),
[arXiv:2604.16101](https://arxiv.org/abs/2604.16101).

Every script here regenerates a figure, a table or a numerical check of the paper, and every
machine-readable file named in the paper's Data/Code Availability statement is in this repository
under exactly that name. All scripts locate their inputs relative to their own location; run them
from any working directory. Nothing writes outside the repository.

## Layout

| folder | contents |
|---|---|
| `figures/fig2/` | build scripts of the Fig. 2 overview diagram, unchanged since the first release of this repository |
| `figures/fig3/` | `fig3_final.py` -> Fig. 3 (`fig3_final.pdf/.png`), Source Data `fig3_final_source_data.csv`, `audit.txt`, `CAPTION_NOTE.md` |
| `figures/fig5/` | `fig5_final.py` -> Fig. 5, Source Data `fig5_final_curves_linear.csv`, `fig5_final_curves_log.csv` |
| `figures/fig6/` | `fig6_final.py` -> Fig. 6, Source Data `fig6_final_panelA.csv`, `fig6_final_panelB.csv` (`README.md` = caption note) |
| `figures/fig7/` | `fig7_final.py` -> Fig. 7 and the single-panel SM versions `fig7_panelA..D.pdf/.png`, Source Data `fig7_final_source_data.csv` |
| `figures/figS1S2/` | `figS1_final.py`, `figS2_final.py` -> Supplementary Figs. S1 (Pade comparison) and S2 (attack time) and their `*_source_data.csv` |
| `figures/tikz/` | TikZ sources of Fig. 1 (`fig1_qrqt_standalone.tex`) and Fig. 4 (`fig4_swap_standalone.tex`) |
| `tables/` | `compute_table_latency_v2.py` -> Tables 1 and 2 as `table_latency_v2.csv` (machine-readable) and `table_latency_v2.tex` |
| `holevo/` | `holevo_correct.py` (closed forms + 3-qubit density-matrix simulation), `verify_holevo.py`, `r3r4_check.py`, `make_figures.py`, their outputs |
| `security/` | `compute_security.py` -> `design_rule_table.md` (design-rule margins) and `fig5a_deltaP.csv` (input of Fig. 5); `si_design_rule_margins.py` (SM margin table + cross-check) |
| `timing/` | `timing_model.py` -> `dmax_fidelity_grid.csv`, `fig_dmax_vs_Tcoh_data.csv` (inputs of Fig. 3) |
| `measurement/` | liboqs latency measurement: C harness, build and campaign scripts, parser, summarizer, log, and the raw results of the five campaigns |
| `tools/scifig.py` | plotting helper (figure size, palette check, audit) imported by all figure scripts |

## Install

```bash
python -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt                   # numpy, matplotlib, scipy, mpmath (pinned)
```

Python 3.11 was used. The figure scripts use matplotlib's bundled DejaVu Sans, so no system font
is needed. `tools/scifig.py` is found because each figure script inserts `<repository root>/tools`
into `sys.path` right before `import scifig`; if you move a script, edit that one line.

## Regenerate the figures

Each command regenerates the figure, its Source Data CSV and (for Figs. 3 and 7) `audit.txt`
next to the script. Figs. 5, 6, S1 and S2 print their audit to stdout; redirect it to keep it.
Regenerated CSV and PNG files are byte-identical to the committed ones; the PDFs differ only in
the embedded `/CreationDate`. Every script asserts its plotted values against the closed forms
(and, for Figs. 6 and 7, against the density-matrix simulation in `holevo/holevo_correct.py`)
and stops with an `AssertionError` if a check fails.

```bash
python figures/fig3/fig3_final.py                        # reads timing/*.csv                     (~2 s)
python figures/fig5/fig5_final.py   > figures/fig5/audit.txt       # reads security/fig5a_deltaP.csv   (~15 s)
python figures/fig6/fig6_final.py   > figures/fig6/audit.txt       # imports holevo/holevo_correct.py  (~1 s)
python figures/fig7/fig7_final.py                        # imports holevo_correct.py, cross-checks against holevo/fig7_*_prototype.csv (~15 s)
python figures/figS1S2/figS1_final.py > figures/figS1S2/audit_S1.txt
python figures/figS1S2/figS2_final.py > figures/figS1S2/audit_S2.txt
```

Figs. 1 and 4 are TikZ: `pdflatex fig1_qrqt_standalone.tex` and `pdflatex fig4_swap_standalone.tex`
in `figures/tikz/` (needs `tikz`, `newtxtext`, `newtxmath`).

## Regenerate the tables

```bash
python -I tables/compute_table_latency_v2.py             # Tables 1 and 2 from the cited public benchmarks -> table_latency_v2.csv / .tex
python -I security/compute_security.py                   # design-rule margins -> security/design_rule_table.md (+ fig5a_deltaP.csv and auxiliary CSV/PNG)
python -I security/si_design_rule_margins.py             # SM margin table numbers; cross-checks design_rule_table.md
python timing/timing_model.py                            # latency model -> timing/*.csv (inputs of Fig. 3) and auxiliary tables
```

`compute_table_latency_v2.py` uses no measured data: its inputs are the cycle counts of the Kyber
(v3.02, Table 2) and FrodoKEM (2021, Tables 6-7) specifications, normalized to 3 GHz, plus the
stated serialization and AEAD assumptions (see its docstring).

## Holevo verification

```bash
python holevo/verify_holevo.py                           # every closed form vs. the 3-qubit simulation; optimality of Eve's strategies -> verification_table.md/.csv (~1 min)
python -I holevo/r3r4_check.py > holevo/r3r4_check.txt   # 118 checks of the formulas in the Holevo sections and SM notes (all PASS)
python holevo/make_figures.py                            # prototype curves; writes the fig7_*_prototype.csv used as cross-check inputs by fig7_final.py and r3r4_check.py
```

`holevo_correct.py` is a library (no side effects): amplitude damping on Bob's half of the Bell
pair before Alice's measurement, conditional states, Holevo quantities, maximal overlaps,
reconstruction fidelities, and the leakage models of the Holevo section. The committed
`r3r4_check.txt` holds two consecutive runs (the first run and the round-3 re-run); a fresh run
reproduces the second block.

## Latency measurement (SM table of measured latencies)

Measured on a 12th Gen Intel Core i9-12950HX under WSL2 (Ubuntu 24.04, gcc 13.3.0, OpenSSL 3.0.13)
with **liboqs 0.16.0, commit `5a1a854b0dc9f2141bdc771c555ee60c37950183`**, built twice
(`build_liboqs_wsl_r1.sh`): native (`OQS_OPT_TARGET=auto`: AVX2, AES-NI) and generic (portable C).
`run_campaign_r1.sh <label>` runs one campaign: the C harness `bench_oqs_percentiles.c`
(per-sample `clock_gettime(CLOCK_MONOTONIC_RAW)`, 1e5/2e4/5e3 repetitions depending on operation
length, warm-up, p50/p90/p99) for ML-KEM-512/768/1024, FrodoKEM and eFrodoKEM 640/976/1344
(AES and SHAKE) in both builds, liboqs' own `speed_kem` (parsed by `parse_speed_output.py`), and
`openssl speed -evp aes-128-gcm`; pinned with `taskset -c 2 chrt -f 50`, CPU frequency not
controlled (turbo on, recorded as such). Five campaigns `results/x86_turbo_default_run1..5`
(raw CSV, logs and `metadata.txt` with compiler, library commit and CMake options).

```bash
python measurement/summarize_campaigns_r1.py             # median over campaigns of the per-campaign p50, min-max spread, derived T_KEM, T_fixed, d_max -> results/summary_r1.csv, summary_r1_derived.csv, SUMMARY_r1.md
```

The summarizer runs anywhere from the committed raw CSVs. Re-running the campaigns needs Linux or
WSL2 and a liboqs build; see `MEASUREMENT_LOG_r1.md` for the exact procedure and the KAT self-tests.

## Dependencies between the pieces

`timing_model.py` -> `fig3_final.py`; `compute_security.py` -> `fig5_final.py`;
`holevo_correct.py` -> `fig6_final.py`, `fig7_final.py`, `verify_holevo.py`, `r3r4_check.py`, `make_figures.py`;
`make_figures.py` -> cross-check inputs of `fig7_final.py` and `r3r4_check.py`;
`compute_security.py` -> cross-check input of `si_design_rule_margins.py`.
All intermediate files are committed, so each script can also be run on its own.

## License

MIT, see `LICENSE`.

## Citation

```bibtex
@article{Jin2026QRQT,
  title   = {Quantum-Resistant Quantum Teleportation},
  author  = {Jin, Xin and Chandra, Nitish Kumar and Azari, Mohadeseh and Cheng, Jinglei and
             Shen, Zilin and Seshadreesan, Kaushik P. and Liu, Junyu},
  journal = {arXiv preprint arXiv:2604.16101},
  year    = {2026}
}
```
