# Fig. 5 (final) -- what the caption must say

Files: `fig5_final.pdf` (vector, 12.0 x 9.2 cm, 1.5-column), `fig5_final.png` (600 dpi),
script `fig5_final.py` (brief + style self-review in the docstring, data assertions,
palette validation, scifig audit: 0 FAIL / 0 WARN, see `audit.txt`).
Per-glyph sizing (coordinator, 2026-10-21, Fig. 3 convention): axis labels 7.5 pt; legend
entries, annotations and tick labels 7 pt; matplotlib's mathtext shrink factor is set to
6/7 so every sub/superscript of a 7 pt string prints at exactly 6.0 pt (P_LWE, P_SWAP,
P_joint, P_LWE/2, t_0, 2^-32, T^E_coh, the 10^k tick labels). The script parses every
mathtext string and asserts the smallest printed glyph >= 6 pt (currently 6.00 pt), so no
production font-size flag is expected.

Legends (user rule, 2026-10-21): every panel carries a conventional legend (line sample +
label), so the caption does not need to tell the reader which colour is which curve; it
still has to define the quantities. Entries: A: P_LWE (cryptanalytic clock), P_SWAP
(memory clock), test baseline 1/2, T^E_coh = 20 s (illustrative); B: P_joint, Delta P,
P_LWE/2 (floor); C: Delta P, t0 = 0; head start t0 = 10-20 s (Delta P > epsilon from
t = 0 onward); epsilon = 2^-32. Line-end labels were removed. The numeric annotations
stay on the plot (maxima in B, window endpoints 0.87 s / 430 s and the region label
Delta P > epsilon in C). To make room for the four-row legend of A (3.7 x 1.4 cm at 7 pt)
the figure is 9.2 cm tall, not 8.3 cm (measured: at 8.3-9.0 cm the legend box touches or
crosses the 1/2 baseline; 9.2 cm is the smallest height with >= 0.8 mm clearance), the
T^E_coh guide in A is drawn from the 1/2 baseline upward, and the y axis of C has a
three-decade legend margin above 10^0 (spine, ticks and window shading stop at 10^0).

## Structure the caption has to describe (three panels, Science Advances style: bold
one-sentence title, then (A), (B), (C))

- **(A)** The two clocks as functions of the storage time t (0-60 s, linear):
  the cryptanalytic clock P_LWE(t) (blue, rising) and the memory clock
  P_SWAP(t) = (1 + e^{-t/T^E_coh})/2 (vermilion, decaying towards the test baseline 1/2,
  grey line). The dotted vertical line marks T^E_coh = 20 s, the **illustrative
  adversary-memory lifetime**. **Symbol change (coordinator, 2026-10-21):** the figure
  now uses the manuscript's binding symbol $T^{E}_{\mathrm{coh}}$ for Eve's memory
  lifetime, not $T_E$ as in variant B; the caption and the text must use the same
  symbol and keep the word "illustrative" (in the figure it is the legend entry
"T^E_coh = 20 s (illustrative)")
- **(B)** Their products on the same time axis: P_joint(t) = P_LWE(t) P_SWAP(t)
  (orange) and the stored-state gain Delta P(t) = P_joint(t) - P_LWE(t)/2
  = P_LWE(t) e^{-t/T^E_coh}/2 (purple). Filled circles mark the maxima; the thin grey
  curve is **P_LWE(t)/2, the floor P_joint settles on** once the stored state has
  decohered (P_SWAP -> 1/2), i.e. the value of cryptanalysis alone followed by a coin
  flip on the test.
- **(C)** Delta P on a log-log scale over 0.5-1000 s (t0 = 0, purple; x ticks 1 s ...
  1000 s). The horizontal line is the threshold epsilon = 2^-32; the shaded band is the
  window in which Delta P > epsilon, with its endpoints marked. The grey band is the
  head start t0 = 10 s and 20 s (the two curves lie within 0.1 decade of each other at
  t = 0.5 s and coincide beyond about 20 s, so they are drawn as one band); with a head
  start Delta P already exceeds epsilon at t = 0, so the window has no lower endpoint.

## Illustrative parameters (must be stated, with the word "illustrative")

P_LWE(T) = prod_{i=1}^{m} erf( d_i 2^{-2(i-1) a / (log2 T + b)} ||b1|| sqrt(pi) / (2 s) )
with m = 30, s = 2, a = 0.3, b = 2.7, ||b1|| = 10, d_i = 2; T^E_coh = 20 s;
head start t0 enters as P_LWE(t0 + t). P_LWE is set to 0 for T <= 2^-b (t -> 0 limit).

## Numbers (all reproduced by the script to the digits below; assertions in the script)

| head start t0 | max P_joint (t, value) | max Delta P (t, value) |
|---|---|---|
| 0      | 16.39 s, 0.645 | 11.11 s, 0.221 |
| 10 s   | 4.54 s, 0.777  | 1.11 s, 0.365  |
| 20 s   | 0 s, 0.933     | 0 s, 0.466     |

- Window Delta P > epsilon = 2^-32 (t0 = 0): [0.873, 429.75] s (figure labels: 0.87 s,
  430 s). The upper endpoint is set by the memory clock alone
  (e^{-t/T^E_coh} = 2 epsilon -> t = T^E_coh ln 2^31 = 429.75 s, P_LWE ~ 1 there); the lower
  endpoint by the cryptanalytic clock, which a head start removes:
  Delta P(t = 0; t0) = P_LWE(t0)/2 = 0.361 (t0 = 10 s), 0.466 (t0 = 20 s) > epsilon.
- Panel A/B x range 0-60 s; panel C 0.5-1000 s (log).

## Data files to cite in the caption / data-availability statement

- `fig5_final_curves_linear.csv`: t_s, P_LWE, P_SWAP, P_joint, DeltaP for t0 = 0 on
  0-60 s (1201 points; panels A and B).
- `fig5_final_curves_log.csv`: t_s, DeltaP_t0_0, DeltaP_t0_10s, DeltaP_t0_20s on
  0.5-1000 s (1500 log-spaced points; panel C); header records epsilon and the window.
- Source check: `_sciadv_work/security/fig5a_deltaP.csv` (0.5-150 s); the script asserts
  that the formula reproduces all five of its columns.

## Draft caption (adapt wording; keep every number)

**Fig. 5. The joint attack must beat two clocks, and only a finite window remains.**
(A) The cryptanalytic clock P_LWE(t) (blue) rises while the memory clock
P_SWAP(t) = (1 + e^{-t/T^E_coh})/2 (vermilion) decays towards the test baseline 1/2 (grey);
T^E_coh = 20 s (dotted) is an illustrative adversary-memory lifetime. Illustrative lattice
parameters: m = 30, s = 2, a = 0.3, b = 2.7, ||b1|| = 10, d_i = 2. (B) Their product
P_joint = P_LWE P_SWAP (orange) peaks at 16.4 s (0.645) and settles on the floor P_LWE/2
(grey); the stored-state gain Delta P = P_joint - P_LWE/2 (purple) peaks earlier, at
11.1 s (0.221). With a head start t0 (cryptanalysis started t0 before storage), the
maxima move to 4.54 s (0.777) and 1.11 s (0.365) for t0 = 10 s, and to t = 0 (0.933 and
0.466) for t0 = 20 s. (C) Delta P exceeds epsilon = 2^-32 only inside [0.87, 430] s
(shaded); the upper endpoint is fixed by T^E_coh alone, the lower one by the cryptanalytic
clock. With a head start of 10-20 s (grey band) Delta P > epsilon from t = 0 onward, so
only the upper endpoint remains. Curves: fig5_final_curves_linear.csv and
fig5_final_curves_log.csv.
