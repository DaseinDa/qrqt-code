# Measurement summary, round 1 (five full campaigns, x86_turbo_default_run1 .. x86_turbo_default_run5)

Host: 12th Gen Intel(R) Core(TM) i9-12950HX; Ubuntu 24.04.4 LTS; gcc 13.3.0; OpenSSL 3.0.13; liboqs 0.16.0 (commit 5a1a854b); native build = OQS_OPT_TARGET=auto (AVX2, AES-NI), generic build = portable C. Pinned with taskset -c 2 chrt -f 50 inside WSL2; CPU frequency not controlled (default Windows power plan, turbo on). Per campaign: n = 1e5 reps (ops <= 100 us), 2e4 (100 us-1 ms), 5e3 (> 1 ms), warm-up 1000/100; per-sample clock_gettime(CLOCK_MONOTONIC_RAW); timer overhead 0.014 us (p50). Reported: median over the five campaigns of the per-campaign p50, with the min-max of the five p50s as the spread.

## AES-128-GCM, 1-byte payload (12-byte nonce, 16-byte tag), fresh init/update/final per call, us per side

| build | encrypt p50 | decrypt p50 |
|---|---|---|
| avx2 | 0.482 | 0.478 |
| generic | 0.500 | 0.497 |

(The public-benchmark tables assume 0.25 us per side; measured here about 0.5 us per side with OpenSSL EVP and a full context set-up per call.)

## KEM latencies (us), median of five campaign p50 values; T_KEM = encaps + decaps; derived T_fixed and d_max use the Table 1 model (0.1 us local, measured AEAD per side, serialization of |C1| + 29 B at 1 Gb/s)

| algorithm | build | keygen | encaps | decaps | T_KEM (spread) | |C1| B | T_ser | T_fixed | d_max 1 ms hard | d_max 1 ms F*=0.90 | d_max 10 ms hard | d_max 10 ms F*=0.90 | T_B,min(F*) at d=0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ML-KEM-512 | avx2 | 5.20 | 5.84 | 7.04 | 12.88 (12.840-13.578) | 768 | 6.38 | 20.31 | 195.94 | 40.57 | 1995.94 | 442.22 | 0.091 ms |
| ML-KEM-512 | generic | 14.03 | 15.34 | 18.23 | 33.57 (33.411-34.373) | 768 | 6.38 | 41.04 | 191.79 | 36.42 | 1991.79 | 438.08 | 0.184 ms |
| ML-KEM-768 | avx2 | 8.46 | 8.92 | 10.73 | 19.65 (19.634-20.193) | 1088 | 8.94 | 29.65 | 194.07 | 38.7 | 1994.07 | 440.36 | 0.133 ms |
| ML-KEM-768 | generic | 23.00 | 22.96 | 27.44 | 50.40 (49.767-54.603) | 1088 | 8.94 | 60.43 | 187.91 | 32.54 | 1987.91 | 434.2 | 0.271 ms |
| ML-KEM-1024 | avx2 | 11.49 | 12.32 | 15.24 | 27.57 (27.201-28.667) | 1568 | 12.78 | 41.40 | 191.72 | 36.35 | 1991.72 | 438.01 | 0.185 ms |
| ML-KEM-1024 | generic | 34.71 | 33.55 | 41.38 | 74.93 (72.020-79.430) | 1568 | 12.78 | 88.80 | 182.24 | 26.87 | 1982.24 | 428.53 | 0.398 ms |
| eFrodoKEM-640-AES | avx2 | 182.11 | 253.44 | 239.01 | 492.45 (489.551-514.234) | 9720 | 77.99 | 571.50 | 85.7 | infeasible | 1885.7 | 331.99 | 2.561 ms |
| eFrodoKEM-640-AES | generic | 209.34 | 307.94 | 295.63 | 603.56 (598.781-615.342) | 9720 | 77.99 | 682.65 | 63.47 | infeasible | 1863.47 | 309.76 | 3.059 ms |
| eFrodoKEM-976-AES | avx2 | 345.50 | 480.64 | 455.77 | 936.42 (932.621-968.874) | 15744 | 126.18 | 1063.66 | infeasible | infeasible | 1787.27 | 233.56 | 4.767 ms |
| eFrodoKEM-976-AES | generic | 413.02 | 621.03 | 594.36 | 1215.39 (1213.900-1233.470) | 15744 | 126.18 | 1342.67 | infeasible | infeasible | 1731.47 | 177.75 | 6.017 ms |
| eFrodoKEM-1344-AES | avx2 | 623.63 | 817.89 | 782.05 | 1599.94 (1591.750-1707.298) | 21632 | 173.29 | 1774.29 | infeasible | infeasible | 1645.14 | 91.43 | 7.951 ms |
| eFrodoKEM-1344-AES | generic | 761.55 | 1081.53 | 1040.01 | 2121.53 (2116.796-2144.833) | 21632 | 173.29 | 2295.92 | infeasible | infeasible | 1540.82 | infeasible | 10.289 ms |
| eFrodoKEM-640-SHAKE | avx2 | 573.00 | 624.46 | 610.92 | 1235.39 (1224.739-1272.580) | 9720 | 77.99 | 1314.44 | infeasible | infeasible | 1737.11 | 183.4 | 5.891 ms |
| eFrodoKEM-640-SHAKE | generic | 1475.72 | 1578.84 | 1557.89 | 3136.73 (3125.904-3169.740) | 9720 | 77.99 | 3215.82 | infeasible | infeasible | 1356.84 | infeasible | 14.411 ms |
| eFrodoKEM-976-SHAKE | avx2 | 1236.52 | 1334.16 | 1291.61 | 2625.77 (2583.998-2727.120) | 15744 | 126.18 | 2753.02 | infeasible | infeasible | 1449.4 | infeasible | 12.337 ms |
| eFrodoKEM-976-SHAKE | generic | 3269.77 | 3515.94 | 3458.43 | 6974.36 (6933.669-7033.597) | 15744 | 126.18 | 7101.64 | infeasible | infeasible | 579.67 | infeasible | 31.825 ms |
| eFrodoKEM-1344-SHAKE | avx2 | 2207.82 | 2366.08 | 2327.41 | 4693.49 (4661.769-4738.543) | 21632 | 173.29 | 4867.84 | infeasible | infeasible | 1026.43 | infeasible | 21.815 ms |
| eFrodoKEM-1344-SHAKE | generic | 5966.68 | 6354.87 | 6310.95 | 12665.82 (12585.867-12712.302) | 21632 | 173.29 | 12840.20 | infeasible | infeasible | infeasible | infeasible | 57.542 ms |
| FrodoKEM-640-AES | avx2 | 182.24 | 254.90 | 237.95 | 492.85 (490.494-498.606) | 9752 | 78.25 | 572.16 | 85.57 | infeasible | 1885.57 | 331.86 | 2.564 ms |
| FrodoKEM-640-AES | generic | 208.12 | 309.38 | 301.78 | 611.15 (602.811-641.351) | 9752 | 78.25 | 690.50 | 61.9 | infeasible | 1861.9 | 308.19 | 3.094 ms |
| FrodoKEM-976-AES | avx2 | 348.22 | 483.35 | 456.26 | 939.61 (931.858-1005.917) | 15792 | 126.57 | 1067.24 | infeasible | infeasible | 1786.55 | 232.84 | 4.783 ms |
| FrodoKEM-976-AES | generic | 414.63 | 617.56 | 593.56 | 1211.12 (1206.300-1334.500) | 15792 | 126.57 | 1338.78 | infeasible | infeasible | 1732.24 | 178.53 | 6.000 ms |
| FrodoKEM-1344-AES | avx2 | 623.31 | 818.02 | 775.19 | 1593.21 (1587.634-1628.941) | 21696 | 173.80 | 1768.07 | infeasible | infeasible | 1646.39 | 92.67 | 7.923 ms |
| FrodoKEM-1344-AES | generic | 745.51 | 1090.73 | 1050.29 | 2141.03 (2125.421-2221.639) | 21696 | 173.80 | 2315.92 | infeasible | infeasible | 1536.82 | infeasible | 10.379 ms |
| FrodoKEM-640-SHAKE | avx2 | 573.81 | 623.93 | 611.07 | 1235.00 (1225.001-1309.144) | 9752 | 78.25 | 1314.31 | infeasible | infeasible | 1737.14 | 183.43 | 5.890 ms |
| FrodoKEM-640-SHAKE | generic | 1472.83 | 1598.86 | 1587.91 | 3186.77 (3142.252-3395.881) | 9752 | 78.25 | 3266.11 | infeasible | infeasible | 1346.78 | infeasible | 14.637 ms |
| FrodoKEM-976-SHAKE | avx2 | 1228.69 | 1307.29 | 1282.22 | 2589.52 (2577.042-2615.208) | 15792 | 126.57 | 2717.14 | infeasible | infeasible | 1456.57 | infeasible | 12.177 ms |
| FrodoKEM-976-SHAKE | generic | 3277.66 | 3515.74 | 3474.06 | 6989.80 (6955.417-7169.920) | 15792 | 126.57 | 7117.47 | infeasible | infeasible | 576.51 | infeasible | 31.896 ms |
| FrodoKEM-1344-SHAKE | avx2 | 2220.45 | 2339.20 | 2321.74 | 4660.94 (4620.057-4778.454) | 21696 | 173.80 | 4835.80 | infeasible | infeasible | 1032.84 | infeasible | 21.671 ms |
| FrodoKEM-1344-SHAKE | generic | 5972.54 | 6344.70 | 6290.55 | 12635.25 (12591.330-12734.373) | 21696 | 173.80 | 12810.15 | infeasible | infeasible | infeasible | infeasible | 57.408 ms |

## Comparison with the public benchmarks normalized to 3 GHz (Table 1 inputs)

| algorithm | build | measured T_KEM (us) | public benchmark at 3 GHz (us) | ratio measured/public |
|---|---|---|---|---|
| ML-KEM-512 | avx2 | 12.88 | 26.6 | 0.48 |
| ML-KEM-512 | generic | 33.57 | 114.2 | 0.29 |
| ML-KEM-768 | avx2 | 19.65 | 40.3 | 0.49 |
| ML-KEM-768 | generic | 50.40 | 170.1 | 0.30 |
| ML-KEM-1024 | avx2 | 27.57 | 58.8 | 0.47 |
| ML-KEM-1024 | generic | 74.93 | 247.7 | 0.30 |
| eFrodoKEM-640-AES | avx2 | 492.45 | 1057.0 | 0.47 |
| eFrodoKEM-976-AES | avx2 | 936.42 | 1984.0 | 0.47 |
| eFrodoKEM-1344-AES | avx2 | 1599.94 | 3301.0 | 0.48 |
| eFrodoKEM-640-SHAKE | generic | 3136.73 | 5197.0 | 0.60 |
| eFrodoKEM-976-SHAKE | generic | 6974.36 | 11357.0 | 0.61 |
| eFrodoKEM-1344-SHAKE | generic | 12665.82 | 20359.0 | 0.62 |

The ratio is consistent with a core running near its turbo frequency (about 5 GHz) relative to the 3 GHz normalization; the measurements are reported as they are, without frequency normalization, because the frequency was not controlled.

