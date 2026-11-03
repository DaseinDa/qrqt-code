# Measurement log — round 1 (started 2026-10-21, within the scope approved in the authors' review §10)

## Scope actually executed
- Isolated working directory inside the WSL2 guest: `/root/qrqt-bench/` (sources, two install prefixes, binaries, logs). Nothing on the Windows host was changed; no BIOS or power-plan change; no Python venv/pip (round 1 uses the C harness and liboqs' own `speed_kem` only).
- Packages installed in the WSL guest with apt: `cmake 3.28.3`, `ninja-build`, `libssl-dev` (build dependencies only).

## Library
- liboqs tag **0.16.0**, commit `5a1a854b0dc9f2141bdc771c555ee60c37950183` (2026-07-09), cloned with `--depth 1 --branch 0.16.0`.
- Two builds, each `-DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=ON -DOQS_USE_OPENSSL=ON -DOQS_DIST_BUILD=OFF`:
  - `native`: `-DOQS_OPT_TARGET=auto` → compiled for this host (AVX2, AES-NI; no AVX-512 on the i9-12950HX) → prefix `/root/qrqt-bench/oqs-native`
  - `generic`: `-DOQS_OPT_TARGET=generic` → portable C only → prefix `/root/qrqt-bench/oqs-generic`
- Toolchain: gcc 13.3.0 (Ubuntu 24.04), OpenSSL 3.0.13 (for AES-GCM via EVP), ninja.
- KAT self-tests (`tests/kat_kem`) passed for all 15 KEMs in both builds before any timing.

## Algorithm identity in this release (dump_alg_info)
liboqs 0.16.0 renamed the unsalted FrodoKEM of the 2021 specification to **eFrodoKEM** and ships the **salted FrodoKEM** under the plain name. Both are built and timed separately; the historical cycle counts in Table 1 (FrodoKEM specification 2021, Tables 6–7) correspond to the eFrodoKEM sizes.

| algorithm (liboqs name) | NIST cat. | public key (B) | secret key (B) | ciphertext (B) | shared secret (B) |
|---|---|---|---|---|---|
| ML-KEM-768 | 3 | 1184 | 2400 | 1088 | 32 |
| FrodoKEM-640-AES (salted) | 1 | 9616 | 19888 | **9752** | 16 |
| eFrodoKEM-640-AES (unsalted, = 2021 spec) | 1 | 9616 | 19888 | **9720** | 16 |
| FrodoKEM-1344-AES (salted) | 5 | 21520 | 43088 | **21696** | 32 |
| eFrodoKEM-1344-AES (unsalted) | 5 | 21520 | 43088 | **21632** | 32 |
(ML-KEM-512/1024 ciphertexts 768/1568 B; FrodoKEM-976 salted 15792 B vs eFrodoKEM-976 15744 B — from the liboqs algorithm pages, to be confirmed from `dump_alg_info` in the campaign metadata.)

## What is timed (round 1)
- C harness `bench_oqs_percentiles.c` (per-sample `clock_gettime(CLOCK_MONOTONIC_RAW)`, min/p50/mean/p90/p99/max/stdev): `keygen`, `encaps`, `decaps`, `encaps_decaps` for the 15 KEMs; AES-128-GCM and AES-256-GCM `aead_encrypt`/`aead_decrypt` for a **1-byte payload** (the QRQT message: two correction bits in one byte + 12-byte nonce + 16-byte tag) and for a 16-byte block (reference); timer-overhead baseline row. Fresh nonce and full init/update/final per call (per-round cost, no key-schedule reuse).
- liboqs `speed_kem` (mean/population stdev, cycles via TSC) for the same 15 KEMs, 10 s per operation.
- `openssl speed -evp aes-128-gcm -bytes 16` as a cross-check.
- Pinning: `taskset -c 2 chrt -f 50` inside WSL (vCPU 2; Hyper-V maps it opaquely). Frequency state: default Windows power plan, turbo enabled, not controlled, recorded in the label.
- Samples: n = 1e5 (ops ≤ 100 µs), 2e4 (100 µs–1 ms), 5e3 (> 1 ms); warm-up 1000 (100 for > 1 ms); five independent campaigns planned, median-of-medians reported.
- Not timed in round 1: ML-DSA (built, `--no-sig`), ARM, FPGA (literature values in `hardware_literature.csv`).

## Status
- 2026-10-21: build + KAT done; quick validation campaign (`x86_turbo_default_quick`, reduced n) running; full campaigns `x86_turbo_default_run1..5` to follow. Results: `results/<label>/merged_<label>.csv` (schema `results_schema.csv`).
- The Table 1 "measured" column stays empty until the five full campaigns are done and summarized; a microbenchmark of the classical primitives is not an end-to-end teleportation measurement.

## Quick validation campaign (reduced n; label x86_turbo_default_quick; 2026-10-21) — pipeline check only, not for the paper
p50 of encaps+decaps (µs), native AVX2/AES-NI | portable C; this laptop under its default power plan (turbo on, ~5 GHz single-core):
ML-KEM-512 14.1 | 34.9; ML-KEM-768 21.5 | 54.0; ML-KEM-1024 30.4 | 80.2;
FrodoKEM-640-AES 555 | 641; -976-AES 1075 | 1259; -1344-AES 1911 | 2214; FrodoKEM-640/976/1344-SHAKE 1400/2834/5198 | 3414/7619/14198;
eFrodoKEM within ±10 % of the salted FrodoKEM of the same size/variant.
AES-128-GCM per side, 1-byte payload: 0.53 µs encrypt / 0.54 µs decrypt (16-byte block: 0.54 / 0.52) — the 0.25 µs/side assumption of Table 1 is optimistic by ~2x on this machine with OpenSSL 3.0.13 EVP (full init/update/final per call).
Timer overhead 0.015 µs. Consistency with the 2021 specification cycle counts normalized to 3 GHz (26.6/40.3/58.8 µs; 1057/1984/3301 µs) is as expected for a ~5 GHz turbo core (ratio ≈ 0.53–0.58 for ML-KEM and FrodoKEM-AES).
Full campaigns (n = 1e5/2e4/5e3, 10 s speed_kem, five repeats) to be run on an idle machine; the measured column is filled only from those.

## Status 2026-11-03
- Five full campaigns done, `x86_turbo_default_run1` .. `run5`, started 2026-11-02 17:17:58Z, 17:53:29Z, 18:29:23Z, 19:04:25Z and 19:39:35Z (UTC; about 35 min each; last one finished 2026-11-02 20:14Z = 2026-11-03 04:14 local time), same host, builds and pinning as above (default power plan, turbo enabled, frequency not controlled). Per campaign: `results/x86_turbo_default_run<k>/metadata.txt`, `c_harness_native.csv` / `c_harness_generic.csv` (C harness, per-sample `clock_gettime(CLOCK_MONOTONIC_RAW)`), `speed_native.csv` / `speed_generic.csv` + `speed_kem_*.log` (liboqs `speed_kem`, cross-check only), `openssl_aes128gcm.log` (cross-check only), `merged_x86_turbo_default_run<k>.csv`.
- Summary files: `results/summary_r1.csv` (per build x algorithm x operation: median/min/max over the five campaigns of the per-campaign p50, median p90, p99, mean, min of min), `results/summary_r1_derived.csv` (per algorithm x build: keygen/encaps/decaps p50, T_KEM = encaps + decaps with the min-max spread of the five campaign medians, |C1|, T_ser at 1 Gb/s, AEAD per side, T_fixed, d_max at 1 ms / 10 ms under the hard cutoff and at F* = 0.90, T_B,min(F*) at d = 0), `results/SUMMARY_r1.md` (human summary and comparison with the 3 GHz public benchmarks).
- Where the numbers went (revision v2 drafts, 2026-11-03): `si_v2/appendix_JEDI.tex`, new Sec. "Measured single-core latencies on the authors' hardware" (label `appendix:measured_latency`) with Supplementary Table `tab:measured_latency` (six parameter sets of Table 1; ML-KEM-512/768/1024 and eFrodoKEM-640/976/1344 = unsalted 2021 scheme, AES variant as fast / SHAKE variant as portable; T_KEM with spread, T_fixed, d_max at 1 ms hard cutoff and F* = 0.90; AES-128-GCM per side and the salted-vs-eFrodoKEM deviation, max 1.6 %, in caption and text); the `[PENDING: measured latencies]` marker and the empty "meas." column of Supplementary Table `tab:latency_sources` removed. `drafts_v2/compute_table_latency_v2.py`: Table 1 caption now points to the SI table (script re-run; `table_latency_v2.csv` byte-identical, `r1.tex` block re-spliced). `drafts_v2/methods.tex`: measurement described in the latency-model subsection with the pointer. `drafts_v2/discussion.tex`: ML-KEM-768 AVX2 19.65 us; FrodoKEM-640-AES 85.7 km under the hard cutoff at 1 ms on this core, infeasible at F* = 0.90; headline distances keep the public 3 GHz reference. `si_v2/appendix_latency.tex`: pointer sentences; empty "measured" column of Supplementary Table `tab:pqc_memory_time` removed.
- Not used in the manuscript: `speed_kem` cycle counts and `openssl speed` (cross-checks), AES-256-GCM, the quick validation campaign of 2026-10-21, ARM/FPGA literature values.
- The measured values are as-measured at the uncontrolled turbo frequency (ratio to the 3 GHz public benchmarks 0.47-0.49 for the AVX2/AES-NI builds); the public-benchmark table remains the reference of the main-text distances (DECISIONS_round3 section A).
