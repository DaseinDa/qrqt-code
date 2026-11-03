#!/usr/bin/env python3
"""
QRQT feasibility (R1) recomputation for the Science Advances revision.

Implements review items B1 (precomputed KEM schedule), B2 (fidelity-target
d_max), B3 (measured latencies + ciphertext serialization), A2 (traceable
latency inputs) and B8 (new main-figure prototype).

Every input constant is documented inline with its source.  Run with
    python -I timing_model.py
from any directory; all outputs are written next to this script.

Outputs
  dmax_fidelity_grid.csv      full grid: scheme x latency model x schedule x link rate x T_coh x F*
  dmax_headline.md            markdown tables of the headline cases
  schedules_penalty.csv/.md   on-path vs precomputed KEM distance penalty
  serialization.csv/.md       ciphertext sizes, serialization times, bits per teleported qubit
  fig_dmax_vs_Tcoh.png/.pdf   prototype main figure (review B8)
  fig_dmax_vs_Tcoh_data.csv   curve data behind the figure
"""
import csv
import math
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

OUT = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------------------
# 1. Physical constants and protocol constants (paper values)
# ----------------------------------------------------------------------------
V_FIBER_KM_PER_US = 0.2        # v_fiber = 2e5 km/s = 0.2 km/us (5 us/km), as in the paper (R1, Methods)
T_LOCAL_US = 0.1               # local operations (Bell prep + gates + BSM + Pauli correction), paper Methods: 0.13 us rounded to 0.1 us
F_CLASSICAL = 2.0 / 3.0        # measure-and-prepare limit for a qubit
F_HARD_CUTOFF = 0.5 * (1.0 + math.exp(-1.0))   # fidelity at tau_m = T_coh under F(t) = (1+e^{-t/T_coh})/2 -> 0.6839

# Memory decay model used in R2 (Eq. fswap): F(t) = (1 + e^{-t/T_coh})/2
# Inverting F(tau_m) >= F*  ->  tau_m <= T_coh ln(1/(2F*-1))
def budget_factor(F_star):
    """ln(1/(2F*-1)): the fraction of T_coh available for tau_m at fidelity target F*."""
    return math.log(1.0 / (2.0 * F_star - 1.0))

# ----------------------------------------------------------------------------
# 2. Scheme table: ciphertext sizes (verified against the specs) and KEM latencies
# ----------------------------------------------------------------------------
# Ciphertext sizes:
#   ML-KEM: FIPS 203 (Aug 2024), Table 3 "Sizes (in bytes) of keys and ciphertexts of ML-KEM":
#           ML-KEM-512 ct 768, ML-KEM-768 ct 1088, ML-KEM-1024 ct 1568 (ek 800/1184/1568).
#   FrodoKEM: round-3 specification (June 2021), Table 5 "Size (in bytes) of inputs and outputs":
#           FrodoKEM-640 ct 9,720; -976 ct 15,744; -1344 ct 21,632 (pk 9,616/15,632/21,520).
# Cycle counts (encaps + decaps; keygen amortized over the key lifetime):
#   Kyber round-3 spec v3.02, Table 2, one core of Intel Core i7-4770K (Haswell) at 3492 MHz:
#       ref  (portable C): 512: 154524+187960 = 342484; 768: 235260+274900 = 510160; 1024: 346648+396584 = 743232
#       AVX2:              512:  45200+ 34572 =  79772; 768:  67624+ 53156 = 120780; 1024:  97324+ 79128 = 176452
#   FrodoKEM round-3 spec, Table 6 (AES128 matrix, AES-NI, "Optimized Implementation (AES from OpenSSL)",
#       3.4 GHz Intel Core i7-6700 Skylake), Total (Encaps+Decaps) in kcycles: 640: 3,171; 976: 5,951; 1344: 9,903
#   FrodoKEM round-3 spec, Table 7 (SHAKE128 matrix, "Optimized Implementation (plain C SHAKE)"), Total kcycles:
#       640: 15,590; 976: 34,072; 1344: 61,077   <- used as the *portable* (no AES-NI, no AVX2) FrodoKEM figure
# All cycle counts are normalized to a 3 GHz clock, as the paper does (T = cycles / 3e9 s).
CLOCK_HZ = 3.0e9

SCHEMES = [
    # name,            family,     level, ct_bytes, T1_us (Table 1), cyc_avx2,  cyc_portable
    ("ML-KEM-512",     "ML-KEM",   1,       768,     2.3,            79772,     342484),
    ("ML-KEM-768",     "ML-KEM",   3,      1088,     3.1,           120780,     510160),
    ("ML-KEM-1024",    "ML-KEM",   5,      1568,     4.2,           176452,     743232),
    ("FrodoKEM-640",   "FrodoKEM", 1,      9720,    15.7,          3171000,   15590000),
    ("FrodoKEM-976",   "FrodoKEM", 3,     15744,    28.4,          5951000,   34072000),
    ("FrodoKEM-1344",  "FrodoKEM", 5,     21632,    45.1,          9903000,   61077000),
]
NO_PQC = ("no-PQC reference", "none", 0, 0, 0.0, 0, 0)

LATENCY_MODELS = {
    # key: (label, KEM time function in us, AEAD time per side in us)
    "A_table1":   ("Table 1 throughput-equivalent (JEDI, paper)", lambda s: s[4], 0.25),
    "B_avx2":     ("single-core AVX2 / AES-NI, 3 GHz",            lambda s: s[5] / CLOCK_HZ * 1e6, 0.25),
    "C_portable": ("single-core portable C, 3 GHz",               lambda s: s[6] / CLOCK_HZ * 1e6, 1.0),
}
# AEAD (AES-128-GCM) on a 1-byte payload, 12-byte nonce, 16-byte tag, per side:
#   Linux-kernel tcrypt benchmark of aesni AES-GCM (LKML, Jan 2021, Icelake desktop, turbo off):
#   128-bit key, 16-byte block: 689 cycles/op encrypt, 689 cycles/op decrypt (AVX2 path).
#   689 cycles / 3 GHz = 0.23 us  -> 0.25 us per side with AES-NI (models A, B).
#   Without AES-NI/PCLMULQDQ a table-based or bitsliced AES-GCM of one block costs a few thousand cycles
#   (key schedule + 2-3 block encryptions + GHASH setup); 1.0 us per side is the conservative end of the
#   0.1-1 us range assumed in the task and is used for the portable model (C).  This is an assumption, not a
#   measurement of a specific library.

AEAD_PAYLOAD_B = 1    # two correction bits, byte-aligned
AEAD_NONCE_B = 12     # explicit 96-bit GCM nonce (could be implicit/counter-derived: then 0)
AEAD_TAG_B = 16       # 128-bit tag
C2_BYTES = AEAD_PAYLOAD_B + AEAD_NONCE_B + AEAD_TAG_B   # 29 B

LINK_RATES = {"inf": math.inf, "1Gbps": 1e9, "10Gbps": 1e10}   # bit/s; 'inf' = no serialization (paper's implicit assumption)

T_COH_LIST_US = [100.0, 1e3, 1e4, 1e5, 1e6]     # 0.1 ms, 1 ms, 10 ms, 100 ms, 1 s
F_TARGETS = [("2/3", F_CLASSICAL), ("hard", F_HARD_CUTOFF), ("0.8", 0.8), ("0.9", 0.9), ("0.95", 0.95), ("0.99", 0.99)]
# F* = 2/3 (classical measure-and-prepare limit) gives ln 3 = 1.0986: only 10% more budget than the paper's hard cutoff.
# ln(1/(2F*-1)) diverges only as F* -> 1/2 (maximally mixed), not at 2/3.


def t_ser_us(nbytes, rate_bps):
    return 0.0 if rate_bps == math.inf else nbytes * 8.0 / rate_bps * 1e6


def t_fixed_us(scheme, model_key, schedule, rate_bps):
    """Distance-independent delay on Bob's memory-critical path (us)."""
    label, kem_fn, t_aead = LATENCY_MODELS[model_key]
    if scheme[1] == "none":                    # no-PQC reference: 2 plaintext bits on the wire
        return T_LOCAL_US + t_ser_us(1, rate_bps)
    if schedule == "on-path":                  # paper's ordering: KEM after the Bell measurement
        return T_LOCAL_US + kem_fn(scheme) + 2 * t_aead + t_ser_us(scheme[3] + C2_BYTES, rate_bps)
    elif schedule == "precomputed":            # KEM done before the BSM; only AEAD(2 bits) on the critical path
        return T_LOCAL_US + 2 * t_aead + t_ser_us(C2_BYTES, rate_bps)
    raise ValueError(schedule)


def d_max_km(T_coh_us, F_key, F_star, t_fixed, n_trips=1):
    """d_max = v [T_coh ln(1/(2F*-1)) - T_fixed] / n_trips.  n_trips = 2 for a heralded link with source at Alice."""
    budget = T_coh_us if F_key == "hard" else T_coh_us * budget_factor(F_star)
    return V_FIBER_KM_PER_US * (budget - t_fixed) / n_trips


# ----------------------------------------------------------------------------
# 3. Full grid (task item 1 + 2 + 3 combined)
# ----------------------------------------------------------------------------
rows = []
for model_key, (model_label, _, _) in LATENCY_MODELS.items():
    for schedule in ("on-path", "precomputed"):
        for rate_key, rate in LINK_RATES.items():
            for scheme in SCHEMES + [NO_PQC]:
                tf = t_fixed_us(scheme, model_key, schedule, rate)
                for T_coh in T_COH_LIST_US:
                    for F_key, F_star in F_TARGETS:
                        d = d_max_km(T_coh, F_key, F_star, tf)
                        rows.append({
                            "latency_model": model_key, "latency_model_label": model_label,
                            "schedule": schedule, "link_rate": rate_key,
                            "scheme": scheme[0], "nist_level": scheme[2],
                            "T_coh_us": T_coh, "F_target": F_key, "F_star_value": round(F_star, 5),
                            "budget_factor_ln": 1.0 if F_key == "hard" else round(budget_factor(F_star), 6),
                            "T_fixed_us": round(tf, 4),
                            "d_max_km": round(d, 3), "feasible": d > 0,
                            "T_coh_at_dmax0_us": round(tf / (1.0 if F_key == "hard" else budget_factor(F_star)), 3),
                        })
with open(os.path.join(OUT, "dmax_fidelity_grid.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)


def lookup(model_key, schedule, rate_key, scheme_name, T_coh, F_key):
    for r in rows:
        if (r["latency_model"] == model_key and r["schedule"] == schedule and r["link_rate"] == rate_key
                and r["scheme"] == scheme_name and r["T_coh_us"] == T_coh and r["F_target"] == F_key):
            return r
    raise KeyError


def fmt(d):
    return "infeasible" if d <= 0 else f"{d:.1f}"


# ----------------------------------------------------------------------------
# 4. Headline markdown tables
# ----------------------------------------------------------------------------
md = []
md.append("# d_max with a fidelity target: headline cases\n")
md.append("Model: F(t) = (1 + e^{-t/T_coh})/2 (paper Eq. fswap), so tau_m <= T_coh ln(1/(2F*-1)).  "
          "d_max(F*) = v [T_coh ln(1/(2F*-1)) - T_fixed], v = 0.2 km/us.  "
          f"'hard' = the paper's cutoff tau_m = T_coh, which corresponds to F* = (1+e^-1)/2 = {F_HARD_CUTOFF:.4f}.  "
          "F* = 2/3 (classical measure-and-prepare limit) gives ln 3 = 1.0986, i.e. the paper's hard cutoff is only 10% "
          "stricter than the classical limit (the budget diverges only as F* -> 1/2).  "
          "Geometry as in the paper: one one-way classical trip d/v on Bob's memory (a heralded link with the "
          "source at Alice replaces d/v by 2d/v and halves every entry).\n")
md.append("Budget factors ln(1/(2F*-1)): " + ", ".join(
    f"F*={k}: {1.0 if k=='hard' else budget_factor(v):.4f}" for k, v in F_TARGETS) + "\n")

md.append("## Table H1. Reproduction of the paper's Table 1 (model A, on-path, no serialization, hard cutoff, T_coh = 1 ms)\n")
md.append("| Scheme | T_PQC (us) | T_fixed (us) | d_max (km) | paper Table 1 (km) |")
md.append("|---|---|---|---|---|")
paper_t1 = {"ML-KEM-512": 199.5, "ML-KEM-768": 199.4, "ML-KEM-1024": 199.1,
            "FrodoKEM-640": 196.8, "FrodoKEM-976": 194.3, "FrodoKEM-1344": 191.0}
for s in SCHEMES:
    tf = T_LOCAL_US + s[4]                       # exactly the paper's T_fixed definition (no AEAD, no serialization)
    md.append(f"| {s[0]} | {s[4]} | {tf:.1f} | {V_FIBER_KM_PER_US*(1e3-tf):.1f} | {paper_t1[s[0]]} |")
md.append("")

for T_coh, T_label in [(1e3, "1 ms"), (100.0, "0.1 ms"), (1e4, "10 ms")]:
    for model_key, (model_label, _, _) in LATENCY_MODELS.items():
        md.append(f"## T_coh = {T_label}, latency model {model_key[0]}: {model_label}; link 1 Gb/s; C2 = {C2_BYTES} B\n")
        md.append("| Scheme | schedule | T_fixed (us) | F*=2/3 | hard (F=0.684) | F*=0.8 | F*=0.9 | F*=0.95 | F*=0.99 |")
        md.append("|---|---|---|---|---|---|---|---|---|")
        for s in SCHEMES + [NO_PQC]:
            for schedule in (("on-path", "precomputed") if s[1] != "none" else ("on-path",)):
                cells = []
                for F_key, _ in F_TARGETS:
                    r = lookup(model_key, schedule, "1Gbps", s[0], T_coh, F_key)
                    cells.append(fmt(r["d_max_km"]))
                tf = lookup(model_key, schedule, "1Gbps", s[0], T_coh, "hard")["T_fixed_us"]
                name = s[0] if s[1] != "none" else "no-PQC (2 plaintext bits)"
                md.append(f"| {name} | {schedule} | {tf:.2f} | " + " | ".join(cells) + " |")
        md.append("")

with open(os.path.join(OUT, "dmax_headline.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md))

# ----------------------------------------------------------------------------
# 5. Schedules: on-path vs precomputed penalty (task item 2)
# ----------------------------------------------------------------------------
pen_rows = []
for model_key, (model_label, kem_fn, t_aead) in LATENCY_MODELS.items():
    for rate_key, rate in LINK_RATES.items():
        for s in SCHEMES:
            tf_on = t_fixed_us(s, model_key, "on-path", rate)
            tf_pre = t_fixed_us(s, model_key, "precomputed", rate)
            tf_ref = t_fixed_us(NO_PQC, model_key, "on-path", rate)
            # distance penalty relative to the no-PQC reference is independent of T_coh and F*:
            pen_rows.append({
                "latency_model": model_key, "link_rate": rate_key, "scheme": s[0],
                "T_KEM_us": round(kem_fn(s), 3), "T_AEAD_per_side_us": t_aead,
                "T_ser_C1C2_us": round(t_ser_us(s[3] + C2_BYTES, rate), 4), "T_ser_C2_us": round(t_ser_us(C2_BYTES, rate), 4),
                "T_fixed_onpath_us": round(tf_on, 4), "T_fixed_precomputed_us": round(tf_pre, 4), "T_fixed_noPQC_us": round(tf_ref, 4),
                "penalty_onpath_km": round(V_FIBER_KM_PER_US * (tf_on - tf_ref), 4),
                "penalty_precomputed_km": round(V_FIBER_KM_PER_US * (tf_pre - tf_ref), 4),
                "KEM_rounds_per_core_per_s": round(1e6 / kem_fn(s), 1),
                # share of the budget at T_coh = 1 ms, F* = 0.9 (budget = 223.1 us):
                "onpath_share_of_budget_1ms_F0.9_pct": round(100 * tf_on / (1e3 * budget_factor(0.9)), 2),
                "T_coh_for_dmax0_onpath_F0.9_us": round(tf_on / budget_factor(0.9), 2),
                "T_coh_for_dmax0_onpath_F0.99_us": round(tf_on / budget_factor(0.99), 2),
            })
with open(os.path.join(OUT, "schedules_penalty.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(pen_rows[0].keys()))
    w.writeheader(); w.writerows(pen_rows)

md = ["# On-path vs precomputed KEM: distance penalty relative to the no-PQC reference\n",
      "penalty = v (T_fixed - T_fixed,noPQC); independent of T_coh and F* (it shifts every d_max curve by a constant).  "
      "T_fixed,on-path = T_loc + T_KEM(encaps+decaps) + 2 T_AEAD + T_ser(C1+C2); "
      "T_fixed,precomputed = T_loc + 2 T_AEAD + T_ser(C2); T_fixed,noPQC = T_loc + T_ser(1 B).  "
      "T_AEAD = 0.25 us/side (AES-NI, 689 cycles at 3 GHz; models A, B) or 1.0 us/side (software AES-GCM assumption; model C).\n"]
for model_key, (model_label, _, _) in LATENCY_MODELS.items():
    md.append(f"## Model {model_key[0]}: {model_label}\n")
    md.append("| Scheme | T_KEM (us) | KEM rounds/s/core | penalty on-path, no ser. (km) | on-path 1 Gb/s (km) | on-path 10 Gb/s (km) | precomputed 1 Gb/s (km) | on-path share of 1 ms/F*=0.9 budget | T_coh where d_max=0 (on-path, 1 Gb/s, F*=0.9) |")
    md.append("|---|---|---|---|---|---|---|---|---|")
    for s in SCHEMES:
        r_inf = next(r for r in pen_rows if r["latency_model"] == model_key and r["link_rate"] == "inf" and r["scheme"] == s[0])
        r_1 = next(r for r in pen_rows if r["latency_model"] == model_key and r["link_rate"] == "1Gbps" and r["scheme"] == s[0])
        r_10 = next(r for r in pen_rows if r["latency_model"] == model_key and r["link_rate"] == "10Gbps" and r["scheme"] == s[0])
        md.append(f"| {s[0]} | {r_1['T_KEM_us']:.1f} | {r_1['KEM_rounds_per_core_per_s']:.0f} | {r_inf['penalty_onpath_km']:.2f} | "
                  f"{r_1['penalty_onpath_km']:.2f} | {r_10['penalty_onpath_km']:.2f} | {r_1['penalty_precomputed_km']:.3f} | "
                  f"{r_1['onpath_share_of_budget_1ms_F0.9_pct']:.1f}% | {r_1['T_coh_for_dmax0_onpath_F0.9_us']/1e3:.3f} ms |")
    md.append("")
with open(os.path.join(OUT, "schedules_penalty.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md))

# ----------------------------------------------------------------------------
# 6. Serialization (task item 3)
# ----------------------------------------------------------------------------
ser_rows = []
for s in SCHEMES:
    total_B = s[3] + C2_BYTES
    ser_rows.append({
        "scheme": s[0], "ciphertext_C1_bytes": s[3], "C2_bytes(payload+nonce+tag)": C2_BYTES, "total_bytes_per_round": total_B,
        "bits_per_teleported_qubit_perround_KEM": 8 * total_B,
        "bits_per_qubit_if_KEM_amortized_over_1000_rounds": round(8 * C2_BYTES + 8 * s[3] / 1000.0, 1),
        "bits_per_qubit_AEAD_only_implicit_nonce": 8 * (AEAD_PAYLOAD_B + AEAD_TAG_B),
        "T_ser_1Gbps_us": round(t_ser_us(total_B, 1e9), 3), "T_ser_10Gbps_us": round(t_ser_us(total_B, 1e10), 3),
        "T_ser_over_T_PQC_table1": round(t_ser_us(total_B, 1e9) / s[4], 2),
        "classical_traffic_Mbps_at_1MHz_pair_rate": round(8 * total_B * 1e6 / 1e6, 1),
        "dmax_loss_1Gbps_km_vs_no_serialization": round(V_FIBER_KM_PER_US * t_ser_us(total_B, 1e9), 3),
        "dmax_loss_10Gbps_km_vs_no_serialization": round(V_FIBER_KM_PER_US * t_ser_us(total_B, 1e10), 3),
    })
with open(os.path.join(OUT, "serialization.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(ser_rows[0].keys()))
    w.writeheader(); w.writerows(ser_rows)
md = ["# Ciphertext serialization\n",
      "Sizes: ML-KEM ciphertexts 768/1088/1568 B (FIPS 203, Table 3); FrodoKEM ciphertexts 9,720/15,744/21,632 B "
      "(FrodoKEM round-3 spec, Table 5).  C2 = 1 B payload (2 bits) + 12 B nonce + 16 B tag = 29 B.  "
      "T_ser = 8 bytes / rate; no framing overhead included (Ethernet+IP+UDP adds ~66 B per packet, i.e. +0.5 us at 1 Gb/s).\n",
      "| Scheme | C1 (B) | C1+C2 (B) | bits per teleported qubit (KEM per round) | bits/qubit, KEM amortized over 1000 rounds | T_ser 1 Gb/s (us) | T_ser 10 Gb/s (us) | T_ser(1 Gb/s)/T_PQC(Table 1) | d_max loss at 1 Gb/s (km) | d_max loss at 10 Gb/s (km) |",
      "|---|---|---|---|---|---|---|---|---|---|"]
for r in ser_rows:
    md.append(f"| {r['scheme']} | {r['ciphertext_C1_bytes']} | {r['total_bytes_per_round']} | {r['bits_per_teleported_qubit_perround_KEM']} | "
              f"{r['bits_per_qubit_if_KEM_amortized_over_1000_rounds']} | {r['T_ser_1Gbps_us']:.2f} | {r['T_ser_10Gbps_us']:.3f} | "
              f"{r['T_ser_over_T_PQC_table1']:.2f}x | {r['dmax_loss_1Gbps_km_vs_no_serialization']:.2f} | {r['dmax_loss_10Gbps_km_vs_no_serialization']:.3f} |")
md.append("")
md.append(f"AEAD-only (precomputed KEM, implicit nonce): {8*(AEAD_PAYLOAD_B+AEAD_TAG_B)} bits per teleported qubit; "
          f"with explicit 12-B nonce: {8*C2_BYTES} bits.\n")
with open(os.path.join(OUT, "serialization.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md))

# ----------------------------------------------------------------------------
# 7. Figure prototype (task item 4; review B8)
# ----------------------------------------------------------------------------
T_grid = np.logspace(1, 6, 400)      # 10 us .. 1 s (in us)
fig_rate = 1e9                        # 1 Gb/s link for the on-path curves
criteria = [("hard", F_HARD_CUTOFF, "d_max (km), hard cutoff\n(tau_m = T_coh, F = 0.684)"),
            ("0.9", 0.9, "d_max (km), target F* = 0.9\n(tau_m = 0.223 T_coh)")]

# colors: two hues (family), lightness step + line style for the NIST level
# Palette validated with the dataviz validator (light surface #fcfcfb): categorical order
# #5598e7,#eb6834,#2a78d6,#c2481a,#1c5cab,#f08a5a passes all gates; each family is a monotone ordinal ramp.
# Level is doubly encoded (lightness step + line style), so hue only has to carry the family.
COL = {"ML-KEM": {1: "#5598e7", 3: "#2a78d6", 5: "#1c5cab"},
       "FrodoKEM": {1: "#f08a5a", 3: "#eb6834", 5: "#c2481a"}}
LS = {1: (0, (1.2, 1.2)), 3: (0, (4, 1.5)), 5: "solid"}
INK, INK2, MUTED, GRID, BASE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.labelsize": 8.5, "axes.titlesize": 9,
                     "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "legend.fontsize": 7, "axes.edgecolor": BASE,
                     "axes.linewidth": 0.8, "xtick.color": MUTED, "ytick.color": MUTED, "axes.labelcolor": INK2})

fig, axes = plt.subplots(2, 3, figsize=(10.5, 6.6), sharex=True, sharey=True)
fig.patch.set_facecolor("#fcfcfb")
Y_FLOOR = 0.1   # km; curves below this are "infeasible" (d_max <= 0 is -inf on a log axis)
fig_data = {"T_coh_us": T_grid}

# memory platform bands (paper's benchmark values; labelled honestly, review B7)
platforms = [
    # label, T_coh (us), fill, hatch, label anchor ('top' or 'bottom' of the panel)
    ("fluxonium 1.4 ms (microwave)", 1.4e3, "#e1e0d9", "//", "top"),
    ("SC cavity 34 ms (microwave)", 3.4e4, "#e1e0d9", "//", "top"),
    ("NV ensemble ~1 s (e-spin T2, 77 K, DD)", 1e6, "#e1e0d9", None, "bottom"),
]
for i, (ckey, F_star, ctitle) in enumerate(criteria):
    for j, (model_key, (model_label, kem_fn, t_aead)) in enumerate(LATENCY_MODELS.items()):
        ax = axes[i, j]
        ax.set_facecolor("#fcfcfb")
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xlim(10, 1e6); ax.set_ylim(Y_FLOOR, 3e5)
        ax.grid(True, which="major", color=GRID, lw=0.6); ax.grid(False, which="minor")
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        # platform bands (factor-of-3 width around the benchmark, as in the paper's Fig. 3b)
        for name, Tc, col, hatch, anchor in platforms:
            ax.axvspan(Tc / 3, Tc * 3, color=col, alpha=0.55, lw=0, zorder=0)
            if hatch:
                ax.axvspan(Tc / 3, Tc * 3, facecolor="none", edgecolor="#c3c2b7", hatch=hatch, lw=0, zorder=0)
            if i == 0:   # vertical label inside the band, top row only (the curves are far from the band's top/bottom there)
                ax.text(Tc, 2.2e5 if anchor == "top" else 0.13, name, rotation=90, ha="center",
                        va="top" if anchor == "top" else "bottom", fontsize=6.3, color=INK2, zorder=5)
        # loss-limited reach band: 0.2 dB/km direct fiber, 20-40 dB (100-200 km) without repeaters
        ax.axhspan(100, 200, color="#fde7d9", alpha=0.7, lw=0, zorder=0)
        ax.axhline(200, color="#eb6834", lw=0.7, ls=(0, (2, 2)), zorder=1)
        if j == 0:
            ax.text(12, 230, "direct-fibre loss limit\n20-40 dB at 0.2 dB/km (100-200 km)",
                    fontsize=6.3, color="#9a3a10", va="bottom", ha="left", zorder=5, linespacing=1.1)
        # scheme curves (on-path, 1 Gb/s)
        for s in SCHEMES:
            tf = t_fixed_us(s, model_key, "on-path", fig_rate)
            d = np.array([d_max_km(T, ckey, F_star, tf) for T in T_grid])
            fig_data[f"{model_key}|{s[0]}|on-path|{ckey}"] = d
            dm = np.where(d > Y_FLOOR, d, np.nan)
            ax.plot(T_grid, dm, color=COL[s[1]][s[2]], ls=LS[s[2]], lw=1.6 if s[2] == 5 else 1.4, zorder=3)
            # x-intercept marker (d_max = 0)
            T0 = tf / (1.0 if ckey == "hard" else budget_factor(F_star))
            ax.plot([T0], [Y_FLOOR * 1.15], marker="v", ms=4, color=COL[s[1]][s[2]], zorder=4, clip_on=False)
        # precomputed-KEM reference (scheme-independent up to the AEAD cost): only AEAD(2 bits) on the critical path
        tf_pre = t_fixed_us(SCHEMES[0], model_key, "precomputed", fig_rate)
        d_pre = np.array([d_max_km(T, ckey, F_star, tf_pre) for T in T_grid])
        fig_data[f"{model_key}|precomputed-KEM|{ckey}"] = d_pre
        ax.plot(T_grid, np.where(d_pre > Y_FLOOR, d_pre, np.nan), color=INK2, lw=2.2, alpha=0.8, zorder=2)
        tf_ref = t_fixed_us(NO_PQC, model_key, "on-path", fig_rate)
        d_ref = np.array([d_max_km(T, ckey, F_star, tf_ref) for T in T_grid])
        fig_data[f"{model_key}|no-PQC|{ckey}"] = d_ref
        ax.plot(T_grid, np.where(d_ref > Y_FLOOR, d_ref, np.nan), color=INK, lw=0.8, ls=(0, (1, 1.5)), zorder=2)
        if i == 0:
            ax.set_title(f"{'ABC'[j]}: {model_label}", color=INK, loc="left")
        if j == 0:
            ax.set_ylabel(ctitle, color=INK2)
        if i == 1:
            ax.set_xlabel("Bob's memory coherence time T_coh (us)", color=INK2)
        ax.set_xticks([10, 100, 1e3, 1e4, 1e5, 1e6])
        ax.set_xticklabels(["10 us", "100 us", "1 ms", "10 ms", "100 ms", "1 s"])

# legend (identity by colour + line style; a legend plus direct labelling in the first panel)
handles = []
for s in SCHEMES:
    handles.append(Line2D([0], [0], color=COL[s[1]][s[2]], ls=LS[s[2]], lw=1.6 if s[2] == 5 else 1.4, label=f"{s[0]}, on-path KEM"))
handles.append(Line2D([0], [0], color=INK2, lw=2.2, alpha=0.8, label="precomputed KEM (2-bit AEAD on path)"))
handles.append(Line2D([0], [0], color=INK, lw=0.8, ls=(0, (1, 1.5)), label="no PQC (2 plaintext bits)"))
handles.append(Line2D([0], [0], marker="v", color=MUTED, lw=0, ms=4, label="T_coh at which d_max = 0"))
handles.append(Patch(facecolor="#e1e0d9", edgecolor="#c3c2b7", hatch="//", label="memory benchmark (x3 band); hatched = microwave, needs transduction"))
handles.append(Patch(facecolor="#fde7d9", edgecolor="#eb6834", label="direct-fibre loss-limited reach (20-40 dB)"))
fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 0.0), handlelength=2.6,
           columnspacing=1.6)
fig.suptitle("Prototype main figure (review B8): d_max vs T_coh for six KEMs, three latency models, two feasibility criteria",
             fontsize=9.5, color=INK, x=0.01, ha="left", y=0.995)
fig.text(0.01, 0.955, "v_fiber = 2e5 km/s.  tau_m = T_loc + T_KEM + 2 T_AEAD + T_ser(C1+C2, 1 Gb/s) + d/v with one one-way classical trip "
         "(a heralded link with the source at Alice replaces d/v by 2d/v and halves d_max).\n"
         "Trapped-ion (1 h) and rare-earth (6 h) spin coherences lie off-scale to the right; the microwave benchmarks have no optical "
         "interface and would need microwave-optical transduction.",
         fontsize=6.8, color=INK2, va="top", linespacing=1.3)
fig.tight_layout(rect=(0, 0.11, 1, 0.925))
fig.savefig(os.path.join(OUT, "fig_dmax_vs_Tcoh.png"), dpi=200, facecolor=fig.get_facecolor())
fig.savefig(os.path.join(OUT, "fig_dmax_vs_Tcoh.pdf"), facecolor=fig.get_facecolor())

with open(os.path.join(OUT, "fig_dmax_vs_Tcoh_data.csv"), "w", newline="") as f:
    keys = list(fig_data.keys())
    w = csv.writer(f)
    w.writerow(["# d_max in km; negative = infeasible; columns: latency_model|scheme|schedule|criterion; on-path uses a 1 Gb/s link"])
    w.writerow(keys)
    for k in range(len(T_grid)):
        w.writerow([f"{fig_data[c][k]:.4f}" for c in keys])

print("done")
