# Fig. 3 (final, three panels A | B | C) — what the caption must say

Files: `fig3_final.pdf` (vector, DejaVu Sans embedded as Type 42 subsets), `fig3_final.png` (600 dpi),
source data `fig3_final_source_data.csv`, script `fig3_final.py`, audit `audit.txt`.  Double column,
18.3 cm x 7.5 cm nominal (PDF page after tight cropping 18.19 x 7.45 cm).  Smallest glyph in the PDF
6.0 pt (mathtext sub/superscripts); ticks and legend 6.5 pt, annotations 7 pt, axis labels 7.5 pt.

## Colour map (identical in every panel; state it once in the caption or rely on the legend)

| parameter set | hex | name |
|---|---|---|
| ML-KEM-512 | #33BBEE | cyan |
| ML-KEM-768 | #0072B2 | blue |
| ML-KEM-1024 | #AA3377 | magenta |
| FrodoKEM-640 | #E6AB02 | mustard |
| FrodoKEM-976 | #D55E00 | vermilion |
| FrodoKEM-1344 | #009E73 | green |
| no PQC (latency reference) | #8C8C8C | grey, thinner |

All six validated together (`scifig.validate_palette`): min pairwise OKLab dE 18.5 (normal, need >= 15),
10.3 / 11.0 (protan, deutan) and 8.6 (tritan, blue vs green; need >= 8) -> PASS.  All curves solid,
uniform 1.2 pt; no linestyle encoding anywhere.  The legend (single row below the panels) is the only key;
the caption need not repeat the entries, but must say that colours are the same in A, B and C.

## Required statements

1. **Model / formula (not written on the figure).**  Receiver-side (Bob) memory wait under the serial
   schedule `tau_m = T_fixed + d / v_fiber`, `v_fiber = 2e5 km/s`, i.e. slope 5 us/km on top of a
   scheme-dependent intercept `T_fixed` (single-core AVX2 / AES-NI at 3 GHz, 1 Gb/s link, latency model
   B, on-path schedule): ML-KEM-512/768/1024 = 33.57 / 49.80 / 72.19 us; FrodoKEM-640/976/1344 = 1135.6 /
   2110.5 / 3474.9 us; no-PQC reference 0.11 us.  Panel A carries no equation and no "slope" label any
   more, so the caption must give the formula and the slope.

2. **Panel A.**  tau_m versus distance for the six sets.  Horizontal guides: 1 ms = T_coh^B hard
   cutoff (tau_m = T_coh^B, label "hard cutoff"); 0.223 ms = usable fraction of a 1 ms memory at
   F* = 0.90, i.e. tau_m <= T_coh^B ln(1/(2F* - 1)) = 0.223 T_coh^B (label "F* = 0.90: 0.223 ms").
   Dots in the three ML-KEM colours mark the crossings: d_max = 193.3 / 190.0 / 185.6 km
   (512/768/1024) under the hard cutoff, written "186–193 km", and 37.9 / 34.7 / 30.2 km at
   F* = 0.90, written **"30–38 km"** (the labels no longer carry the prefix "ML-KEM:", the caption must
   say the dots are the ML-KEM crossings).  Every FrodoKEM set has tau_m > 1 ms at every distance
   (T_fixed > 1 ms): "infeasible" at 1 ms (note in the panel).  T_coh^B = 10 ms is off the panel-A scale;
   all six sets are feasible there (see B, C).  The three ML-KEM curves differ by < 40 us and nearly
   coincide for d > 50 km; they separate only near d = 0 (say so, so readers do not look for three lines).

3. **Panels B and C: criterion -> panel.**  d_max = v_fiber (f T_coh^B - T_fixed) versus memory
   lifetime, one curve per parameter set: **B** hard cutoff (f = 1, tau_m = T_coh^B); **C** F* = 0.90
   (f = 0.223, tau_m = 0.223 T_coh^B).  Grey line: no-PQC latency reference (same geometry without a
   KEM; a latency bound, not an equally protected alternative); it is the upper envelope of all curves.
   Triangles on the abscissa, in the set's colour, mark the knee T_coh^B = T_fixed (B) or T_fixed/0.223
   (C) where d_max = 0; below that lifetime the set is infeasible (key "d_max = 0" in the panel; the word
   "infeasible" must be in the caption).  Knees: B 33.6 / 49.8 / 72.2 us (ML-KEM) and 1.14 / 2.11 /
   3.47 ms (FrodoKEM); C 150 / 223 / 323 us and 5.09 / 9.46 / 15.6 ms.

4. **The knee message (B, C).**  The six curves coincide at large lifetimes (at 100 ms all lie within
   4 % of the no-PQC bound in B and within 15 % in C) and separate only at their knees: the scheme-dependent
   intercept T_fixed matters only when T_coh^B is comparable to T_fixed; once T_coh^B >> T_fixed the
   distance budget is set by the fibre delay alone.  Say this explicitly.

5. **Reference lifetimes.**  Dotted verticals at 1 ms (reference) and 10 ms (comparison) in B and C.
   ML-KEM-768 values marked by blue dots and written vertically beside the lines: B: 190 km (1 ms) and
   **1990 km (10 ms)**; C: 35 km (1 ms) and **436 km (10 ms)** (exact: 190.04 / 1990.04 / 34.67 /
   436.33 km).  At 10 ms all six sets are feasible under the hard cutoff (FrodoKEM-1344: 1305 km,
   ML-KEM-512: 1993 km).

6. **Source data.**  "Source data are provided in `fig3_final_source_data.csv`" (columns: panel,
   quantity, x, x_unit, scheme, criterion, T_fixed_us, value, value_unit; A: tau_m(d) for the six sets at
   51 distances 0–250 km plus the six marked crossings; B and C: d_max(T_coh^B) for the six sets and the
   no-PQC reference at 81 lifetimes 10 us – 100 ms (negative = infeasible), the six knees, and the two
   marked ML-KEM-768 points per panel).  Inputs: `_sciadv_work/timing/dmax_fidelity_grid.csv` (model
   B_avx2, on-path, 1 Gb/s) and the cross-check file `fig_dmax_vs_Tcoh_data.csv` (max deviation 6e-5 km).

## Suggested caption skeleton (Science Advances style)

**Fig. 3. Receiver-side memory requirement of the serial schedule.**  Colours identify the parameter
sets in all panels (legend).  (**A**) Memory wait tau_m = T_fixed + d/v_fiber (v_fiber = 2 x 10^5 km/s,
slope 5 us/km) versus distance (single-core AVX2/AES-NI, 1 Gb/s link).  Guides: the 1 ms hard cutoff and
its usable fraction 0.223 ms at F* = 0.90; dots mark the ML-KEM crossings (186–193 km and 30–38 km).
Every FrodoKEM set exceeds 1 ms at any distance.  (**B**, **C**) Maximum distance
d_max = v_fiber (f T_coh^B - T_fixed) versus memory lifetime under the hard cutoff (B, f = 1) and at
F* = 0.90 (C, f = 0.223); grey, no-PQC latency reference.  Triangles mark the knee d_max = 0 below which a
set is infeasible; the curves coincide for T_coh^B >> T_fixed and separate only at their knees.  Dots:
ML-KEM-768 at 1 ms (190 km; 35 km) and 10 ms (1990 km; 436 km).  Source data: fig3_final_source_data.csv.
