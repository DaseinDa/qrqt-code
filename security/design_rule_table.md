# Design rule at published core-SVP levels

Model: `P_break(t) = min(1, t R / 2^lambda)`; rule `P_break(T_rot + T_E ln(1/2eps)) <= 2 eps`; margin = log10(2 eps) - log10 P_break(window) (positive = satisfied). ln(1/2eps) = 21.49 (eps = 2^-32) and 43.67 (eps = 2^-64).

Attacker throughput R (core-SVP operations per second):

- 2^40 ~ 1.1e12 core-SVP ops/s: one large HPC installation (the core-SVP unit is one vector operation in dimension beta, >= beta ~ 400-900 cycles, so 2^40 ops/s is ~1e5 cores at 3 GHz; counting one op as one cycle it is ~350 cores).
- 2^60 ~ 1.2e18 ops/s: ~1e6 times the above; of the order of all general-purpose computing on Earth devoted to the attack (JEDI, 4.5 PFlop/s, is 2^52 flop/s; 2^60 is 256 JEDIs if one op = one flop).
- 2^80 ~ 1.2e24 ops/s: a hypothetical future adversary 2^20 times stronger again; exceeds the Bitcoin network (~1e21 SHA-256 hashes/s ~ 2^70 hashes/s) by ~1000x at the hash level.

## eps = 2^-32, R = 2^40 ops/s, T_rot = 30 days — margin log10 (positive = OK)

| scheme | model | lambda | T_E = 1 ms | 1 s | 1 h | 24 h | inf |
|---|---|---|---|---|---|---|---|
| ML-KEM-512 | classical | 118 | +7.7 | +7.7 | +7.7 | +7.5 | fails (-inf) |
| ML-KEM-512 | quantum | 107 | +4.4 | +4.4 | +4.4 | +4.2 | fails (-inf) |
| ML-KEM-512 | refined gates (classical) | 151.5 | +17.8 | +17.8 | +17.8 | +17.6 | fails (-inf) |
| ML-KEM-768 | classical | 183 | +27.3 | +27.3 | +27.3 | +27.1 | fails (-inf) |
| ML-KEM-768 | quantum | 166 | +22.2 | +22.2 | +22.2 | +21.9 | fails (-inf) |
| ML-KEM-768 | refined gates (classical) | 215.1 | +37.0 | +37.0 | +37.0 | +36.7 | fails (-inf) |
| ML-KEM-1024 | classical | 256 | +49.3 | +49.3 | +49.3 | +49.0 | fails (-inf) |
| ML-KEM-1024 | quantum | 232 | +42.1 | +42.1 | +42.0 | +41.8 | fails (-inf) |
| ML-KEM-1024 | refined gates (classical) | 287.3 | +58.7 | +58.7 | +58.7 | +58.5 | fails (-inf) |
| FrodoKEM-640 | classical | 145 | +15.9 | +15.9 | +15.8 | +15.6 | fails (-inf) |
| FrodoKEM-640 | quantum | 132 | +11.9 | +11.9 | +11.9 | +11.7 | fails (-inf) |
| FrodoKEM-976 | classical | 210 | +35.4 | +35.4 | +35.4 | +35.2 | fails (-inf) |
| FrodoKEM-976 | quantum | 191 | +29.7 | +29.7 | +29.7 | +29.5 | fails (-inf) |
| FrodoKEM-1344 | classical | 275 | +55.0 | +55.0 | +55.0 | +54.8 | fails (-inf) |
| FrodoKEM-1344 | quantum | 250 | +47.5 | +47.5 | +47.5 | +47.2 | fails (-inf) |

## eps = 2^-32, R = 2^60 ops/s, T_rot = 30 days — margin log10 (positive = OK)

| scheme | model | lambda | T_E = 1 ms | 1 s | 1 h | 24 h | inf |
|---|---|---|---|---|---|---|---|
| ML-KEM-512 | classical | 118 | +1.7 | +1.7 | +1.7 | +1.5 | fails (-inf) |
| ML-KEM-512 | quantum | 107 | -1.6 | -1.6 | -1.6 | -1.8 | fails (-inf) |
| ML-KEM-512 | refined gates (classical) | 151.5 | +11.8 | +11.8 | +11.8 | +11.6 | fails (-inf) |
| ML-KEM-768 | classical | 183 | +21.3 | +21.3 | +21.3 | +21.0 | fails (-inf) |
| ML-KEM-768 | quantum | 166 | +16.2 | +16.2 | +16.2 | +15.9 | fails (-inf) |
| ML-KEM-768 | refined gates (classical) | 215.1 | +30.9 | +30.9 | +30.9 | +30.7 | fails (-inf) |
| ML-KEM-1024 | classical | 256 | +43.3 | +43.3 | +43.2 | +43.0 | fails (-inf) |
| ML-KEM-1024 | quantum | 232 | +36.0 | +36.0 | +36.0 | +35.8 | fails (-inf) |
| ML-KEM-1024 | refined gates (classical) | 287.3 | +52.7 | +52.7 | +52.7 | +52.4 | fails (-inf) |
| FrodoKEM-640 | classical | 145 | +9.8 | +9.8 | +9.8 | +9.6 | fails (-inf) |
| FrodoKEM-640 | quantum | 132 | +5.9 | +5.9 | +5.9 | +5.7 | fails (-inf) |
| FrodoKEM-976 | classical | 210 | +29.4 | +29.4 | +29.4 | +29.2 | fails (-inf) |
| FrodoKEM-976 | quantum | 191 | +23.7 | +23.7 | +23.7 | +23.5 | fails (-inf) |
| FrodoKEM-1344 | classical | 275 | +49.0 | +49.0 | +49.0 | +48.7 | fails (-inf) |
| FrodoKEM-1344 | quantum | 250 | +41.5 | +41.5 | +41.4 | +41.2 | fails (-inf) |

## eps = 2^-32, R = 2^80 ops/s, T_rot = 30 days — margin log10 (positive = OK)

| scheme | model | lambda | T_E = 1 ms | 1 s | 1 h | 24 h | inf |
|---|---|---|---|---|---|---|---|
| ML-KEM-512 | classical | 118 | -4.3 | -4.3 | -4.3 | -4.5 | fails (-inf) |
| ML-KEM-512 | quantum | 107 | -7.6 | -7.6 | -7.6 | -7.9 | fails (-inf) |
| ML-KEM-512 | refined gates (classical) | 151.5 | +5.8 | +5.8 | +5.8 | +5.5 | fails (-inf) |
| ML-KEM-768 | classical | 183 | +15.3 | +15.3 | +15.2 | +15.0 | fails (-inf) |
| ML-KEM-768 | quantum | 166 | +10.1 | +10.1 | +10.1 | +9.9 | fails (-inf) |
| ML-KEM-768 | refined gates (classical) | 215.1 | +24.9 | +24.9 | +24.9 | +24.7 | fails (-inf) |
| ML-KEM-1024 | classical | 256 | +37.2 | +37.2 | +37.2 | +37.0 | fails (-inf) |
| ML-KEM-1024 | quantum | 232 | +30.0 | +30.0 | +30.0 | +29.8 | fails (-inf) |
| ML-KEM-1024 | refined gates (classical) | 287.3 | +46.7 | +46.7 | +46.6 | +46.4 | fails (-inf) |
| FrodoKEM-640 | classical | 145 | +3.8 | +3.8 | +3.8 | +3.6 | fails (-inf) |
| FrodoKEM-640 | quantum | 132 | -0.1 | -0.1 | -0.1 | -0.3 | fails (-inf) |
| FrodoKEM-976 | classical | 210 | +23.4 | +23.4 | +23.4 | +23.2 | fails (-inf) |
| FrodoKEM-976 | quantum | 191 | +17.7 | +17.7 | +17.7 | +17.4 | fails (-inf) |
| FrodoKEM-1344 | classical | 275 | +43.0 | +43.0 | +42.9 | +42.7 | fails (-inf) |
| FrodoKEM-1344 | quantum | 250 | +35.4 | +35.4 | +35.4 | +35.2 | fails (-inf) |

## eps = 2^-64, R = 2^40 ops/s, T_rot = 30 days — margin log10 (positive = OK)

| scheme | model | lambda | T_E = 1 ms | 1 s | 1 h | 24 h | inf |
|---|---|---|---|---|---|---|---|
| ML-KEM-512 | classical | 118 | -1.9 | -1.9 | -1.9 | -2.3 | fails (-inf) |
| ML-KEM-512 | quantum | 107 | -5.2 | -5.2 | -5.2 | -5.6 | fails (-inf) |
| ML-KEM-512 | refined gates (classical) | 151.5 | +8.2 | +8.2 | +8.2 | +7.8 | fails (-inf) |
| ML-KEM-768 | classical | 183 | +17.7 | +17.7 | +17.6 | +17.3 | fails (-inf) |
| ML-KEM-768 | quantum | 166 | +12.6 | +12.6 | +12.5 | +12.2 | fails (-inf) |
| ML-KEM-768 | refined gates (classical) | 215.1 | +27.3 | +27.3 | +27.3 | +26.9 | fails (-inf) |
| ML-KEM-1024 | classical | 256 | +39.6 | +39.6 | +39.6 | +39.3 | fails (-inf) |
| ML-KEM-1024 | quantum | 232 | +32.4 | +32.4 | +32.4 | +32.0 | fails (-inf) |
| ML-KEM-1024 | refined gates (classical) | 287.3 | +49.1 | +49.1 | +49.0 | +48.7 | fails (-inf) |
| FrodoKEM-640 | classical | 145 | +6.2 | +6.2 | +6.2 | +5.8 | fails (-inf) |
| FrodoKEM-640 | quantum | 132 | +2.3 | +2.3 | +2.3 | +1.9 | fails (-inf) |
| FrodoKEM-976 | classical | 210 | +25.8 | +25.8 | +25.8 | +25.4 | fails (-inf) |
| FrodoKEM-976 | quantum | 191 | +20.1 | +20.1 | +20.1 | +19.7 | fails (-inf) |
| FrodoKEM-1344 | classical | 275 | +45.4 | +45.4 | +45.3 | +45.0 | fails (-inf) |
| FrodoKEM-1344 | quantum | 250 | +37.8 | +37.8 | +37.8 | +37.4 | fails (-inf) |

## eps = 2^-64, R = 2^60 ops/s, T_rot = 30 days — margin log10 (positive = OK)

| scheme | model | lambda | T_E = 1 ms | 1 s | 1 h | 24 h | inf |
|---|---|---|---|---|---|---|---|
| ML-KEM-512 | classical | 118 | -7.9 | -7.9 | -7.9 | -8.3 | fails (-inf) |
| ML-KEM-512 | quantum | 107 | -11.2 | -11.2 | -11.3 | -11.6 | fails (-inf) |
| ML-KEM-512 | refined gates (classical) | 151.5 | +2.2 | +2.2 | +2.1 | +1.8 | fails (-inf) |
| ML-KEM-768 | classical | 183 | +11.6 | +11.6 | +11.6 | +11.3 | fails (-inf) |
| ML-KEM-768 | quantum | 166 | +6.5 | +6.5 | +6.5 | +6.1 | fails (-inf) |
| ML-KEM-768 | refined gates (classical) | 215.1 | +21.3 | +21.3 | +21.3 | +20.9 | fails (-inf) |
| ML-KEM-1024 | classical | 256 | +33.6 | +33.6 | +33.6 | +33.2 | fails (-inf) |
| ML-KEM-1024 | quantum | 232 | +26.4 | +26.4 | +26.4 | +26.0 | fails (-inf) |
| ML-KEM-1024 | refined gates (classical) | 287.3 | +43.0 | +43.0 | +43.0 | +42.7 | fails (-inf) |
| FrodoKEM-640 | classical | 145 | +0.2 | +0.2 | +0.2 | -0.2 | fails (-inf) |
| FrodoKEM-640 | quantum | 132 | -3.7 | -3.7 | -3.7 | -4.1 | fails (-inf) |
| FrodoKEM-976 | classical | 210 | +19.8 | +19.8 | +19.8 | +19.4 | fails (-inf) |
| FrodoKEM-976 | quantum | 191 | +14.1 | +14.1 | +14.0 | +13.7 | fails (-inf) |
| FrodoKEM-1344 | classical | 275 | +39.3 | +39.3 | +39.3 | +39.0 | fails (-inf) |
| FrodoKEM-1344 | quantum | 250 | +31.8 | +31.8 | +31.8 | +31.4 | fails (-inf) |

## eps = 2^-64, R = 2^80 ops/s, T_rot = 30 days — margin log10 (positive = OK)

| scheme | model | lambda | T_E = 1 ms | 1 s | 1 h | 24 h | inf |
|---|---|---|---|---|---|---|---|
| ML-KEM-512 | classical | 118 | -13.9 | -13.9 | -14.0 | -14.3 | fails (-inf) |
| ML-KEM-512 | quantum | 107 | -17.3 | -17.3 | -17.3 | -17.6 | fails (-inf) |
| ML-KEM-512 | refined gates (classical) | 151.5 | -3.9 | -3.9 | -3.9 | -4.2 | fails (-inf) |
| ML-KEM-768 | classical | 183 | +5.6 | +5.6 | +5.6 | +5.2 | fails (-inf) |
| ML-KEM-768 | quantum | 166 | +0.5 | +0.5 | +0.5 | +0.1 | fails (-inf) |
| ML-KEM-768 | refined gates (classical) | 215.1 | +15.3 | +15.3 | +15.3 | +14.9 | fails (-inf) |
| ML-KEM-1024 | classical | 256 | +27.6 | +27.6 | +27.6 | +27.2 | fails (-inf) |
| ML-KEM-1024 | quantum | 232 | +20.4 | +20.4 | +20.4 | +20.0 | fails (-inf) |
| ML-KEM-1024 | refined gates (classical) | 287.3 | +37.0 | +37.0 | +37.0 | +36.6 | fails (-inf) |
| FrodoKEM-640 | classical | 145 | -5.8 | -5.8 | -5.8 | -6.2 | fails (-inf) |
| FrodoKEM-640 | quantum | 132 | -9.7 | -9.7 | -9.8 | -10.1 | fails (-inf) |
| FrodoKEM-976 | classical | 210 | +13.8 | +13.8 | +13.7 | +13.4 | fails (-inf) |
| FrodoKEM-976 | quantum | 191 | +8.0 | +8.0 | +8.0 | +7.6 | fails (-inf) |
| FrodoKEM-1344 | classical | 275 | +33.3 | +33.3 | +33.3 | +32.9 | fails (-inf) |
| FrodoKEM-1344 | quantum | 250 | +25.8 | +25.8 | +25.8 | +25.4 | fails (-inf) |

## Largest tolerable adversary memory lifetime T_E,max = (2 eps 2^lambda / R - T_rot) / ln(1/2eps)

| scheme | model | lambda | eps | R=2^40, T_rot=1 d | R=2^40, 1 y | R=2^60, 1 d | R=2^60, 1 y | R=2^80, 1 d | R=2^80, 1 y |
|---|---|---|---|---|---|---|---|---|---|
| ML-KEM-512 | classical | 118 | 2^-32 | 2.08e+05 y | 2.08e+05 y | 72.2 d | 55.3 d | <0 (fails at T_E=0) | <0 (fails at T_E=0) |
| ML-KEM-512 | classical | 118 | 2^-64 | <0 (fails at T_E=0) | <0 (fails at T_E=0) | <0 (fails at T_E=0) | <0 (fails at T_E=0) | <0 (fails at T_E=0) | <0 (fails at T_E=0) |
| ML-KEM-512 | quantum | 107 | 2^-32 | 101 y | 101 y | <0 (fails at T_E=0) | <0 (fails at T_E=0) | <0 (fails at T_E=0) | <0 (fails at T_E=0) |
| ML-KEM-512 | quantum | 107 | 2^-64 | <0 (fails at T_E=0) | <0 (fails at T_E=0) | <0 (fails at T_E=0) | <0 (fails at T_E=0) | <0 (fails at T_E=0) | <0 (fails at T_E=0) |
| ML-KEM-512 | refined gates | 151.5 | 2^-32 | 2.52e+15 y | 2.52e+15 y | 2.4e+09 y | 2.4e+09 y | 2.29e+03 y | 2.29e+03 y |
| ML-KEM-512 | refined gates | 151.5 | 2^-64 | 2.89e+05 y | 2.89e+05 y | 101 d | 92.3 d | <0 (fails at T_E=0) | <0 (fails at T_E=0) |
| ML-KEM-768 | classical | 183 | 2^-32 | 7.66e+24 y | 7.66e+24 y | 7.3e+18 y | 7.3e+18 y | 6.96e+12 y | 6.96e+12 y |
| ML-KEM-768 | classical | 183 | 2^-64 | 8.77e+14 y | 8.77e+14 y | 8.37e+08 y | 8.37e+08 y | 798 y | 798 y |
| ML-KEM-768 | quantum | 166 | 2^-32 | 5.84e+19 y | 5.84e+19 y | 5.57e+13 y | 5.57e+13 y | 5.31e+07 y | 5.31e+07 y |
| ML-KEM-768 | quantum | 166 | 2^-64 | 6.69e+09 y | 6.69e+09 y | 6.38e+03 y | 6.38e+03 y | 2.2 d | <0 (fails at T_E=0) |
| ML-KEM-768 | refined gates | 215.1 | 2^-32 | 3.52e+34 y | 3.52e+34 y | 3.36e+28 y | 3.36e+28 y | 3.21e+22 y | 3.21e+22 y |
| ML-KEM-768 | refined gates | 215.1 | 2^-64 | 4.04e+24 y | 4.04e+24 y | 3.85e+18 y | 3.85e+18 y | 3.67e+12 y | 3.67e+12 y |
| ML-KEM-1024 | classical | 256 | 2^-32 | 7.23e+46 y | 7.23e+46 y | 6.9e+40 y | 6.9e+40 y | 6.58e+34 y | 6.58e+34 y |
| ML-KEM-1024 | classical | 256 | 2^-64 | 8.29e+36 y | 8.29e+36 y | 7.9e+30 y | 7.9e+30 y | 7.54e+24 y | 7.54e+24 y |
| ML-KEM-1024 | quantum | 232 | 2^-32 | 4.31e+39 y | 4.31e+39 y | 4.11e+33 y | 4.11e+33 y | 3.92e+27 y | 3.92e+27 y |
| ML-KEM-1024 | quantum | 232 | 2^-64 | 4.94e+29 y | 4.94e+29 y | 4.71e+23 y | 4.71e+23 y | 4.49e+17 y | 4.49e+17 y |
| ML-KEM-1024 | refined gates | 287.3 | 2^-32 | 1.91e+56 y | 1.91e+56 y | 1.82e+50 y | 1.82e+50 y | 1.74e+44 y | 1.74e+44 y |
| ML-KEM-1024 | refined gates | 287.3 | 2^-64 | 2.19e+46 y | 2.19e+46 y | 2.09e+40 y | 2.09e+40 y | 1.99e+34 y | 1.99e+34 y |
| FrodoKEM-640 | classical | 145 | 2^-32 | 2.79e+13 y | 2.79e+13 y | 2.66e+07 y | 2.66e+07 y | 25.3 y | 25.3 y |
| FrodoKEM-640 | classical | 145 | 2^-64 | 3.19e+03 y | 3.19e+03 y | 1.09 d | <0 (fails at T_E=0) | <0 (fails at T_E=0) | <0 (fails at T_E=0) |
| FrodoKEM-640 | quantum | 132 | 2^-32 | 3.4e+09 y | 3.4e+09 y | 3.24e+03 y | 3.24e+03 y | 1.08 d | <0 (fails at T_E=0) |
| FrodoKEM-640 | quantum | 132 | 2^-64 | 142 d | 134 d | <0 (fails at T_E=0) | <0 (fails at T_E=0) | <0 (fails at T_E=0) | <0 (fails at T_E=0) |
| FrodoKEM-976 | classical | 210 | 2^-32 | 1.03e+33 y | 1.03e+33 y | 9.8e+26 y | 9.8e+26 y | 9.35e+20 y | 9.35e+20 y |
| FrodoKEM-976 | classical | 210 | 2^-64 | 1.18e+23 y | 1.18e+23 y | 1.12e+17 y | 1.12e+17 y | 1.07e+11 y | 1.07e+11 y |
| FrodoKEM-976 | quantum | 191 | 2^-32 | 1.96e+27 y | 1.96e+27 y | 1.87e+21 y | 1.87e+21 y | 1.78e+15 y | 1.78e+15 y |
| FrodoKEM-976 | quantum | 191 | 2^-64 | 2.25e+17 y | 2.25e+17 y | 2.14e+11 y | 2.14e+11 y | 2.04e+05 y | 2.04e+05 y |
| FrodoKEM-1344 | classical | 275 | 2^-32 | 3.79e+52 y | 3.79e+52 y | 3.62e+46 y | 3.62e+46 y | 3.45e+40 y | 3.45e+40 y |
| FrodoKEM-1344 | classical | 275 | 2^-64 | 4.34e+42 y | 4.34e+42 y | 4.14e+36 y | 4.14e+36 y | 3.95e+30 y | 3.95e+30 y |
| FrodoKEM-1344 | quantum | 250 | 2^-32 | 1.13e+45 y | 1.13e+45 y | 1.08e+39 y | 1.08e+39 y | 1.03e+33 y | 1.03e+33 y |
| FrodoKEM-1344 | quantum | 250 | 2^-64 | 1.29e+35 y | 1.29e+35 y | 1.23e+29 y | 1.23e+29 y | 1.18e+23 y | 1.18e+23 y |

## Minimum core-SVP exponent required, lambda_req = log2 R + log2(T_rot + T_E ln(1/2eps)) + log2(1/2eps)

| R | T_rot | T_E | lambda_req (eps=2^-32) | lambda_req (eps=2^-64) |
|---|---|---|---|---|
| 2^40 | 1 day | 1 h | 88.3 | 120.9 |
| 2^40 | 1 day | 24 h | 91.9 | 124.9 |
| 2^40 | 1 day | inf | inf (long-term security) | inf |
| 2^40 | 30 days | 1 h | 92.3 | 124.4 |
| 2^40 | 30 days | 24 h | 93.1 | 125.6 |
| 2^40 | 30 days | inf | inf (long-term security) | inf |
| 2^40 | 1 year | 1 h | 95.9 | 127.9 |
| 2^40 | 1 year | 24 h | 96.0 | 128.1 |
| 2^40 | 1 year | inf | inf (long-term security) | inf |
| 2^60 | 1 day | 1 h | 108.3 | 140.9 |
| 2^60 | 1 day | 24 h | 111.9 | 144.9 |
| 2^60 | 1 day | inf | inf (long-term security) | inf |
| 2^60 | 30 days | 1 h | 112.3 | 144.4 |
| 2^60 | 30 days | 24 h | 113.1 | 145.6 |
| 2^60 | 30 days | inf | inf (long-term security) | inf |
| 2^60 | 1 year | 1 h | 115.9 | 147.9 |
| 2^60 | 1 year | 24 h | 116.0 | 148.1 |
| 2^60 | 1 year | inf | inf (long-term security) | inf |
| 2^80 | 1 day | 1 h | 128.3 | 160.9 |
| 2^80 | 1 day | 24 h | 131.9 | 164.9 |
| 2^80 | 1 day | inf | inf (long-term security) | inf |
| 2^80 | 30 days | 1 h | 132.3 | 164.4 |
| 2^80 | 30 days | 24 h | 133.1 | 165.6 |
| 2^80 | 30 days | inf | inf (long-term security) | inf |
| 2^80 | 1 year | 1 h | 135.9 | 167.9 |
| 2^80 | 1 year | 24 h | 136.0 | 168.1 |
| 2^80 | 1 year | inf | inf (long-term security) | inf |

Reading: ML-KEM-512 has lambda = 118 (classical) / 107 (quantum sieving); ML-KEM-768 183/166; ML-KEM-1024 256/232; FrodoKEM-640 145/132; -976 210/191; -1344 275/250.
