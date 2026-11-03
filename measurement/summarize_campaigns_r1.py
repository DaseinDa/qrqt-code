# -*- coding: utf-8 -*-
"""Summarize the five full measurement campaigns (x86_turbo_default_run1..5):
   median over campaigns of the per-campaign p50 (C harness), with the spread of the five medians,
   for every (implementation, algorithm, operation); AES-128-GCM per side for the 1-byte QRQT message;
   derived T_KEM = encaps + decaps, T_fixed^meas and d_max^meas at T_coh^B = 1 ms and 10 ms.
   Writes results/summary_r1.csv, results/summary_r1_derived.csv and results/SUMMARY_r1.md.
   Run: python summarize_campaigns_r1.py
"""
import csv, glob, io, math, os, statistics, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
RUNS = sorted(glob.glob(os.path.join(RES, "x86_turbo_default_run[0-9]")))
assert len(RUNS) == 5, RUNS

rows = []
for r in RUNS:
    label = os.path.basename(r)
    for f in ("c_harness_native.csv", "c_harness_generic.csv"):
        with open(os.path.join(r, f), encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                row["run"] = label
                rows.append(row)
print("harness rows:", len(rows))

# ------------------------------------------------------------ per (impl, alg, op, msg) statistics
keys = {}
for row in rows:
    k = (row["implementation"], row["algorithm"], row["operation"], row["message_bytes"])
    keys.setdefault(k, []).append(row)
summary = []
for k, rs in sorted(keys.items()):
    p50s = [float(x["p50_us"]) for x in rs]
    p90s = [float(x["p90_us"]) for x in rs]
    p99s = [float(x["p99_us"]) for x in rs]
    means = [float(x["mean_us"]) for x in rs]
    mins = [float(x["min_us"]) for x in rs]
    summary.append({
        "implementation": k[0], "algorithm": k[1], "operation": k[2], "message_bytes": k[3],
        "n_campaigns": len(rs), "n_reps_per_campaign": rs[0]["n_reps"],
        "p50_median_us": statistics.median(p50s), "p50_min_us": min(p50s), "p50_max_us": max(p50s),
        "p90_median_us": statistics.median(p90s), "p99_median_us": statistics.median(p99s),
        "mean_median_us": statistics.median(means), "min_of_min_us": min(mins),
    })
with open(os.path.join(RES, "summary_r1.csv"), "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(summary[0].keys()))
    w.writeheader(); w.writerows(summary)
print("summary rows:", len(summary))

def get(impl, alg, op, msg="0"):
    for s in summary:
        if (s["implementation"], s["algorithm"], s["operation"], s["message_bytes"]) == (impl, alg, op, msg):
            return s
    raise KeyError((impl, alg, op, msg))

# ------------------------------------------------------------ derived quantities (same model as Table 1)
V_KM_PER_US = 0.2          # 2e5 km/s
T_LOCAL_US = 0.1
C2_BYTES = 29              # 1-byte payload + 12-byte nonce + 16-byte tag
LN125 = math.log(1.25)     # ln(1/(2F*-1)) at F* = 0.90
CT = {  # ciphertext bytes: ML-KEM (FIPS 203); eFrodoKEM = unsalted 2021 spec sizes (= Table 1); FrodoKEM = salted (liboqs 0.16.0)
    "ML-KEM-512": 768, "ML-KEM-768": 1088, "ML-KEM-1024": 1568,
    "eFrodoKEM-640-AES": 9720, "eFrodoKEM-976-AES": 15744, "eFrodoKEM-1344-AES": 21632,
    "eFrodoKEM-640-SHAKE": 9720, "eFrodoKEM-976-SHAKE": 15744, "eFrodoKEM-1344-SHAKE": 21632,
    "FrodoKEM-640-AES": 9752, "FrodoKEM-976-AES": 15792, "FrodoKEM-1344-AES": 21696,
    "FrodoKEM-640-SHAKE": 9752, "FrodoKEM-976-SHAKE": 15792, "FrodoKEM-1344-SHAKE": 21696,
}
def t_ser_us(ct): return 8.0 * (ct + C2_BYTES) / 1e3   # at 1 Gb/s, in us
def dmax(tcoh_us, tfixed_us, f=1.0):
    d = V_KM_PER_US * (f * tcoh_us - tfixed_us)
    return d if d > 0 else float("nan")

derived = []
aead = {}
for impl in ("avx2", "generic"):
    enc = get(impl, "AES-128-GCM", "aead_encrypt", "1")["p50_median_us"]
    dec = get(impl, "AES-128-GCM", "aead_decrypt", "1")["p50_median_us"]
    aead[impl] = (enc, dec)
for alg in CT:
    for impl in ("avx2", "generic"):
        e = get(impl, alg, "encaps"); d = get(impl, alg, "decaps"); kg = get(impl, alg, "keygen")
        try:
            ed = get(impl, alg, "encaps_decaps")["p50_median_us"]
        except KeyError:
            ed = float("nan")
        tkem = e["p50_median_us"] + d["p50_median_us"]
        tkem_lo = e["p50_min_us"] + d["p50_min_us"]; tkem_hi = e["p50_max_us"] + d["p50_max_us"]
        tfixed = T_LOCAL_US + tkem + aead[impl][0] + aead[impl][1] + t_ser_us(CT[alg])
        derived.append({
            "algorithm": alg, "implementation": impl, "keygen_p50_us": round(kg["p50_median_us"], 3),
            "encaps_p50_us": round(e["p50_median_us"], 3), "decaps_p50_us": round(d["p50_median_us"], 3),
            "T_KEM_us": round(tkem, 3), "T_KEM_spread_us": "%.3f-%.3f" % (tkem_lo, tkem_hi),
            "encaps_decaps_combined_p50_us": round(ed, 3) if ed == ed else "",
            "ciphertext_B": CT[alg], "T_ser_us": round(t_ser_us(CT[alg]), 3),
            "AEAD_enc_us": round(aead[impl][0], 3), "AEAD_dec_us": round(aead[impl][1], 3),
            "T_fixed_us": round(tfixed, 3),
            "dmax_1ms_hard_km": round(dmax(1000, tfixed), 2) if dmax(1000, tfixed) == dmax(1000, tfixed) else "infeasible",
            "dmax_1ms_F090_km": round(dmax(1000, tfixed, LN125), 2) if dmax(1000, tfixed, LN125) == dmax(1000, tfixed, LN125) else "infeasible",
            "dmax_10ms_hard_km": round(dmax(10000, tfixed), 2) if dmax(10000, tfixed) == dmax(10000, tfixed) else "infeasible",
            "dmax_10ms_F090_km": round(dmax(10000, tfixed, LN125), 2) if dmax(10000, tfixed, LN125) == dmax(10000, tfixed, LN125) else "infeasible",
            "T_Bmin_F090_d0_ms": round(tfixed / LN125 / 1000, 4),
        })
with open(os.path.join(RES, "summary_r1_derived.csv"), "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(derived[0].keys()))
    w.writeheader(); w.writerows(derived)

# ------------------------------------------------------------ markdown
meta = open(os.path.join(RUNS[0], "metadata.txt"), encoding="utf-8", errors="replace").read().splitlines()
timer = get("avx2", "none", "timer_overhead")["p50_median_us"]
md = []
md.append("# Measurement summary, round 1 (five full campaigns, %s .. %s)\n" % (os.path.basename(RUNS[0]), os.path.basename(RUNS[-1])))
md.append("Host: %s; %s; gcc 13.3.0; OpenSSL 3.0.13; liboqs 0.16.0 (commit 5a1a854b); native build = OQS_OPT_TARGET=auto (AVX2, AES-NI), generic build = portable C. "
          "Pinned with taskset -c 2 chrt -f 50 inside WSL2; CPU frequency not controlled (default Windows power plan, turbo on). "
          "Per campaign: n = 1e5 reps (ops <= 100 us), 2e4 (100 us-1 ms), 5e3 (> 1 ms), warm-up 1000/100; per-sample clock_gettime(CLOCK_MONOTONIC_RAW); timer overhead %.3f us (p50). "
          "Reported: median over the five campaigns of the per-campaign p50, with the min-max of the five p50s as the spread.\n" % (meta[3].split(":")[-1].strip(), meta[2], timer))
md.append("## AES-128-GCM, 1-byte payload (12-byte nonce, 16-byte tag), fresh init/update/final per call, us per side\n")
md.append("| build | encrypt p50 | decrypt p50 |\n|---|---|---|")
for impl in ("avx2", "generic"):
    md.append("| %s | %.3f | %.3f |" % (impl, aead[impl][0], aead[impl][1]))
md.append("\n(The public-benchmark tables assume 0.25 us per side; measured here about 0.5 us per side with OpenSSL EVP and a full context set-up per call.)\n")
md.append("## KEM latencies (us), median of five campaign p50 values; T_KEM = encaps + decaps; derived T_fixed and d_max use the Table 1 model (0.1 us local, measured AEAD per side, serialization of |C1| + 29 B at 1 Gb/s)\n")
md.append("| algorithm | build | keygen | encaps | decaps | T_KEM (spread) | |C1| B | T_ser | T_fixed | d_max 1 ms hard | d_max 1 ms F*=0.90 | d_max 10 ms hard | d_max 10 ms F*=0.90 | T_B,min(F*) at d=0 |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for d in derived:
    md.append("| %s | %s | %.2f | %.2f | %.2f | %.2f (%s) | %d | %.2f | %.2f | %s | %s | %s | %s | %.3f ms |" % (
        d["algorithm"], d["implementation"], d["keygen_p50_us"], d["encaps_p50_us"], d["decaps_p50_us"], d["T_KEM_us"], d["T_KEM_spread_us"],
        d["ciphertext_B"], d["T_ser_us"], d["T_fixed_us"], d["dmax_1ms_hard_km"], d["dmax_1ms_F090_km"], d["dmax_10ms_hard_km"], d["dmax_10ms_F090_km"], d["T_Bmin_F090_d0_ms"]))
md.append("\n## Comparison with the public benchmarks normalized to 3 GHz (Table 1 inputs)\n")
pub = {"ML-KEM-512": (26.6, 114.2), "ML-KEM-768": (40.3, 170.1), "ML-KEM-1024": (58.8, 247.7),
       "eFrodoKEM-640-AES": (1057, None), "eFrodoKEM-976-AES": (1984, None), "eFrodoKEM-1344-AES": (3301, None),
       "eFrodoKEM-640-SHAKE": (None, 5197), "eFrodoKEM-976-SHAKE": (None, 11357), "eFrodoKEM-1344-SHAKE": (None, 20359)}
md.append("| algorithm | build | measured T_KEM (us) | public benchmark at 3 GHz (us) | ratio measured/public |\n|---|---|---|---|---|")
for d in derived:
    if d["algorithm"] in pub:
        ref = pub[d["algorithm"]][0 if d["implementation"] == "avx2" else 1]
        if ref:
            md.append("| %s | %s | %.2f | %.1f | %.2f |" % (d["algorithm"], d["implementation"], d["T_KEM_us"], ref, d["T_KEM_us"] / ref))
md.append("\nThe ratio is consistent with a core running near its turbo frequency (about 5 GHz) relative to the 3 GHz normalization; the measurements are reported as they are, without frequency normalization, because the frequency was not controlled.\n")
open(os.path.join(RES, "SUMMARY_r1.md"), "w", encoding="utf-8", newline="\n").write("\n".join(md) + "\n")
print("\n".join(md))
