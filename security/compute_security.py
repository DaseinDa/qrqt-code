#!/usr/bin/env python3
"""
QRQT -> Science Advances revision, task "security" (review items A3, B4, B7).

Evaluates the paper's design rule
        P_break(T_rot + T_E * ln(1/(2 eps))) <= 2 eps
at the published core-SVP security levels of ML-KEM / FrodoKEM, compares with Shor
resource estimates for RSA-2048 / ECC-256, and recomputes the toy Fig. 5 quantity
Delta P(t) = (1/2) P_LWE(t0 + t) exp(-t/T_coh).

Everything is written to the folder that contains this script. No manuscript file
is touched. Python 3.11 + numpy + scipy + matplotlib only.

Model (stated once, used everywhere):
    P_break(t) = min(1, t * R / 2^lambda)
with lambda the published core-SVP exponent (classical 0.292*beta, quantum 0.265*beta,
"plausible" 0.2075*beta) and R the attacker's sustained sieve throughput in
core-SVP operations per second. The linear form is exactly the bit-security
definition (advantage <= work / 2^lambda): an attacker who has spent W = t*R
operations against a lambda-bit primitive has advantage at most W / 2^lambda.
It is an upper envelope of the real all-or-nothing sieve (which succeeds only when
W reaches 2^lambda), so every margin below is conservative.
"""
import json
import math
import os

import numpy as np
from scipy.special import erf

HERE = os.path.dirname(os.path.abspath(__file__))
DAY = 86400.0
HOUR = 3600.0
YEAR = 365.25 * DAY

# ----------------------------------------------------------------------------------
# (1) Published security estimates (all numbers copied from the cited tables)
# ----------------------------------------------------------------------------------
# Kyber round-3 specification v3.02 (4 Aug 2021), Table 4, p. 21: core-SVP methodology,
#   primal attack only; lattice dim d, BKZ block size beta, classical 0.292 beta,
#   quantum 0.265 beta; plus the refined gate-count estimate (Sec. 5.2).
#   ML-KEM (FIPS 203, Aug 2024) standardises the same three parameter sets
#   (n=256, k=2/3/4, q=3329, eta1=3/2/2, eta2=2, (du,dv)=(10,4)/(10,4)/(11,5)).
# FrodoKEM specification (4 Jun 2021), Table 2, p. 24 ("Security bounds", LWE security
#   C / Q / P = classical / quantum / plausible, i.e. 0.292 / 0.265 / 0.2075 beta) and
#   Table 10, p. 43 (primal / dual attack cost on a single LWE instance).
SCHEMES = [
    # name, NIST cat, beta, lambda_classical, lambda_quantum, lambda_plausible, refined_log2_gates, source
    ("ML-KEM-512",   1, 406, 118, 107, round(0.2075 * 406, 1), 151.5,
     "Kyber spec v3.02 Table 4 (d=999, beta=406); plausible 0.2075*beta derived here; refined gates Sec. 5.2"),
    ("ML-KEM-768",   3, 626, 183, 166, round(0.2075 * 626, 1), 215.1,
     "Kyber spec v3.02 Table 4 (d=1419, beta=626); plausible 0.2075*beta derived here; refined gates Sec. 5.2"),
    ("ML-KEM-1024",  5, 878, 256, 232, round(0.2075 * 878, 1), 287.3,
     "Kyber spec v3.02 Table 4 (d=1885, beta=878); plausible 0.2075*beta derived here; refined gates Sec. 5.2"),
    ("FrodoKEM-640",  1, None, 145, 132, 104, None,
     "FrodoKEM spec 2021-06-04 Table 2 (LWE security C/Q/P); Table 10 single-instance primal 150.8/137.6/109.6"),
    ("FrodoKEM-976",  3, None, 210, 191, 150, None,
     "FrodoKEM spec 2021-06-04 Table 2; Table 10 single-instance primal 216.0/196.7/156.0"),
    ("FrodoKEM-1344", 5, None, 275, 250, 197, None,
     "FrodoKEM spec 2021-06-04 Table 2; Table 10 single-instance primal 281.6/256.3/202.6"),
]

with open(os.path.join(HERE, "security_estimates.csv"), "w", encoding="utf-8") as fh:
    fh.write("# Published core-SVP security estimates. lambda = log2(operations). "
             "classical 2^(0.292 beta), quantum-sieving 2^(0.265 beta), plausible lower bound 2^(0.2075 beta).\n")
    fh.write("# Sources: Kyber round-3 spec v3.02 (2021-08-04) Table 4 p.21; FrodoKEM spec (2021-06-04) "
             "Table 2 p.24 and Table 10 p.43. ML-KEM parameter sets = Kyber v3.02 parameter sets (FIPS 203).\n")
    fh.write("scheme,nist_category,bkz_beta,lambda_classical,lambda_quantum,lambda_plausible,"
             "refined_log2_gates_classical,source\n")
    for s in SCHEMES:
        fh.write(",".join("" if v is None else str(v) for v in s[:7]) + ',"' + s[7] + '"\n')

# ----------------------------------------------------------------------------------
# (2) Design rule on the (T_rot, T_E) grid
# ----------------------------------------------------------------------------------
LOG2R = [40, 60, 80]
R_DESC = {
    40: "2^40 ~ 1.1e12 core-SVP ops/s: one large HPC installation "
        "(the core-SVP unit is one vector operation in dimension beta, >= beta ~ 400-900 cycles, "
        "so 2^40 ops/s is ~1e5 cores at 3 GHz; counting one op as one cycle it is ~350 cores).",
    60: "2^60 ~ 1.2e18 ops/s: ~1e6 times the above; of the order of all general-purpose computing "
        "on Earth devoted to the attack (JEDI, 4.5 PFlop/s, is 2^52 flop/s; 2^60 is 256 JEDIs if one op = one flop).",
    80: "2^80 ~ 1.2e24 ops/s: a hypothetical future adversary 2^20 times stronger again; exceeds the "
        "Bitcoin network (~1e21 SHA-256 hashes/s ~ 2^70 hashes/s) by ~1000x at the hash level.",
}
T_ROT = [("1 day", DAY), ("30 days", 30 * DAY), ("1 year", YEAR)]
T_E = [("1 ms", 1e-3), ("1 s", 1.0), ("1 h", HOUR), ("24 h", DAY), ("inf", math.inf)]
EPS = [32, 64]  # eps = 2^-32, 2^-64


def margin_log10(lam, log2R, trot, te, eps_log2):
    """log10( 2 eps 2^lambda / (R (T_rot + T_E ln(1/2eps))) ). >0 means rule satisfied."""
    L = math.log(2.0 ** (eps_log2 - 1))  # ln(1/(2 eps)) with eps = 2^-eps_log2
    window = trot + te * L
    if math.isinf(window):
        return -math.inf, L, window, 0.0  # P_break saturates at 1 -> rule fails
    log10_p = (math.log10(window) + log2R * math.log10(2) - lam * math.log10(2))
    log10_p = min(0.0, log10_p)  # P_break = min(1, ...)
    m = (1 - eps_log2) * math.log10(2) - log10_p  # log10(2 eps) - log10(P_break)
    return m, L, window, log10_p


rows = []
for name, cat, beta, lc, lq, lp, lg, src in SCHEMES:
    for model, lam in [("classical", lc), ("quantum", lq), ("plausible", lp)] + ([("refined_gates", lg)] if lg else []):
        for log2R in LOG2R:
            for trl, tr in T_ROT:
                for tel, te in T_E:
                    for e in EPS:
                        m, L, window, log10p = margin_log10(lam, log2R, tr, te, e)
                        rows.append(dict(scheme=name, cost_model=model, lambda_bits=lam, log2_R=log2R,
                                         T_rot=trl, T_rot_s=tr, T_E=tel, T_E_s=te, eps_log2=e, ln_1_over_2eps=round(L, 3),
                                         window_s=window, log10_Pbreak=log10p, margin_log10=m,
                                         satisfied=(m > 0)))
with open(os.path.join(HERE, "design_rule_margins.csv"), "w", encoding="utf-8") as fh:
    fh.write("# Design rule P_break(T_rot + T_E ln(1/2eps)) <= 2 eps with P_break(t)=min(1, t R / 2^lambda).\n")
    fh.write("# margin_log10 = log10(2 eps) - log10 P_break(window); > 0 means satisfied. "
             "T_E = inf: window infinite, P_break = 1, rule fails for every finite lambda (long-term security required).\n")
    keys = list(rows[0].keys())
    fh.write(",".join(keys) + "\n")
    for r in rows:
        fh.write(",".join(str(r[k]) for k in keys) + "\n")

# Closed forms that follow from the linear model
def te_max(lam, log2R, trot, eps_log2):
    """Largest adversary memory lifetime for which the rule holds."""
    L = math.log(2.0 ** (eps_log2 - 1))
    budget = 2.0 ** (lam - log2R + 1 - eps_log2)  # 2 eps 2^lambda / R  [s]
    return (budget - trot) / L, budget


def lam_req(log2R, trot, te, eps_log2):
    """Minimum core-SVP exponent that satisfies the rule."""
    L = math.log(2.0 ** (eps_log2 - 1))
    return log2R + math.log2(trot + te * L) + eps_log2 - 1


def fmt_t(sec):
    if math.isinf(sec):
        return "inf"
    if sec < 0:
        return "<0 (fails at T_E=0)"
    for unit, val in (("y", YEAR), ("d", DAY), ("h", HOUR), ("min", 60.0), ("s", 1.0), ("ms", 1e-3), ("us", 1e-6)):
        if sec >= val:
            return f"{sec / val:.3g} {unit}"
    return f"{sec:.2e} s"


md = []
md.append("# Design rule at published core-SVP levels\n")
md.append("Model: `P_break(t) = min(1, t R / 2^lambda)`; rule `P_break(T_rot + T_E ln(1/2eps)) <= 2 eps`; "
          "margin = log10(2 eps) - log10 P_break(window) (positive = satisfied). "
          "ln(1/2eps) = %.2f (eps = 2^-32) and %.2f (eps = 2^-64).\n" % (math.log(2 ** 31), math.log(2 ** 63)))
md.append("Attacker throughput R (core-SVP operations per second):\n")
for k in LOG2R:
    md.append(f"- {R_DESC[k]}")
md.append("")

for e in EPS:
    for log2R in LOG2R:
        md.append(f"## eps = 2^-{e}, R = 2^{log2R} ops/s, T_rot = 30 days — margin log10 (positive = OK)\n")
        md.append("| scheme | model | lambda | T_E = 1 ms | 1 s | 1 h | 24 h | inf |")
        md.append("|---|---|---|---|---|---|---|---|")
        for name, cat, beta, lc, lq, lp, lg, src in SCHEMES:
            models = [("classical", lc), ("quantum", lq)] + ([("refined gates (classical)", lg)] if lg else [])
            for model, lam in models:
                cells = []
                for tel, te in T_E:
                    m = margin_log10(lam, log2R, 30 * DAY, te, e)[0]
                    cells.append("fails (-inf)" if math.isinf(m) else f"{m:+.1f}")
                md.append(f"| {name} | {model} | {lam} | " + " | ".join(cells) + " |")
        md.append("")

md.append("## Largest tolerable adversary memory lifetime T_E,max = (2 eps 2^lambda / R - T_rot) / ln(1/2eps)\n")
md.append("| scheme | model | lambda | eps | R=2^40, T_rot=1 d | R=2^40, 1 y | R=2^60, 1 d | R=2^60, 1 y | R=2^80, 1 d | R=2^80, 1 y |")
md.append("|---|---|---|---|---|---|---|---|---|---|")
for name, cat, beta, lc, lq, lp, lg, src in SCHEMES:
    for model, lam in [("classical", lc), ("quantum", lq)] + ([("refined gates", lg)] if lg else []):
        for e in EPS:
            cells = []
            for log2R in LOG2R:
                for trl, tr in ((T_ROT[0]), (T_ROT[2])):
                    cells.append(fmt_t(te_max(lam, log2R, tr, e)[0]))
            md.append(f"| {name} | {model} | {lam} | 2^-{e} | " + " | ".join(cells) + " |")
md.append("")

md.append("## Minimum core-SVP exponent required, lambda_req = log2 R + log2(T_rot + T_E ln(1/2eps)) + log2(1/2eps)\n")
md.append("| R | T_rot | T_E | lambda_req (eps=2^-32) | lambda_req (eps=2^-64) |")
md.append("|---|---|---|---|---|")
for log2R in LOG2R:
    for trl, tr in T_ROT:
        for tel, te in T_E[2:]:
            if math.isinf(te):
                md.append(f"| 2^{log2R} | {trl} | inf | inf (long-term security) | inf |")
            else:
                md.append(f"| 2^{log2R} | {trl} | {tel} | {lam_req(log2R, tr, te, 32):.1f} | {lam_req(log2R, tr, te, 64):.1f} |")
md.append("")
md.append("Reading: ML-KEM-512 has lambda = 118 (classical) / 107 (quantum sieving); ML-KEM-768 183/166; "
          "ML-KEM-1024 256/232; FrodoKEM-640 145/132; -976 210/191; -1344 275/250.\n")
with open(os.path.join(HERE, "design_rule_table.md"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(md))

# ----------------------------------------------------------------------------------
# (3) Shor comparison and the "PQC necessary vs sufficient" map
# ----------------------------------------------------------------------------------
# Published resource estimates (verified on the arXiv abstract pages, 2026-10-20):
SHOR = [
    # label, target, runtime_s, qubits, source
    ("RSA-2048, Gidney & Ekera 2021", "RSA-2048", 8 * HOUR, "20e6 physical",
     "Quantum 5, 433 (2021), arXiv:1905.09749: ~8 h, 20 M noisy qubits, 1e-3 gate error, 1 us cycle"),
    ("RSA-2048, Gidney 2025", "RSA-2048", 7 * DAY, "<1e6 physical",
     "arXiv:2505.15917: < 1 week, < 1 M noisy qubits, 0.1% gate error, 1 us cycle, 10 us reaction time"),
    ("ECC-256, Litinski 2023", "ECC-256", 10 * 60.0, "~6.9e6 physical (6000 modules x 1152)",
     "arXiv:2306.08585: 50 M Toffoli; one key per 10 min with 10 us code cycle, non-local connections, 10% threshold"),
    ("ECC-256, Babbush et al. 2026 (Google)", "ECC-256", 10 * 60.0, "<0.5e6 physical",
     "arXiv:2603.28846: <1200 logical qubits & <90 M Toffoli (or <1450 & <70 M); 'minutes' on superconducting "
     "hardware at 1e-3 error; taken here as 10 min"),
    ("ECC-256, Haener et al. 2026 (IonQ)", "ECC-256", 25.7 * DAY, "19,397 physical (trapped ion)",
     "arXiv:2609.05625: 25.7 days, 19,397 physical qubits, ~63% success per attempt"),
    ("ECC-256 (P-256), Haener et al. 2020", "ECC-256", None, "2124 logical (Low-W)",
     "PQCrypto 2020, arXiv:2001.09580 Table 1: 2124 logical qubits, T-count 1.72*2^32, T-depth 1.98*2^30 "
     "(logical only; no physical runtime stated)"),
]
with open(os.path.join(HERE, "shor_estimates.csv"), "w", encoding="utf-8") as fh:
    fh.write("label,target,runtime_s,qubits,source\n")
    for lab, tg, rt, qb, src in SHOR:
        fh.write(f'"{lab}",{tg},{"" if rt is None else rt},"{qb}","{src}"\n')

# Ephemeral ECDH per round: fresh key each round, so head start T_rot = 0; the rule becomes
#   P_Shor(T_E ln(1/2eps)) <= 2 eps, with P_Shor(t) = 0 for t < T_Shor and ~1 after (given a CRQC).
# => ephemeral ECDH is safe under the paper's own rule iff T_E < T_Shor / ln(1/2eps).
ecdh_rows = []
for lab, tg, rt, qb, src in SHOR:
    if rt is None:
        continue
    for e in EPS:
        L = math.log(2 ** (e - 1))
        ecdh_rows.append((lab, tg, rt, e, rt / L))
with open(os.path.join(HERE, "ecdh_safe_memory_threshold.csv"), "w", encoding="utf-8") as fh:
    fh.write("# Ephemeral ECDH/RSA safe under the time-bounded rule iff T_E < T_Shor / ln(1/2eps)\n")
    fh.write("estimate,target,T_Shor_s,eps_log2,T_E_threshold_s,T_E_threshold_human\n")
    for lab, tg, rt, e, th in ecdh_rows:
        fh.write(f'"{lab}",{tg},{rt},{e},{th:.4g},{fmt_t(th)}\n')

# Map on the (T_rot, T_E) plane, eps = 2^-32, ML-KEM quantum-sieving exponents, R in {2^40,2^60,2^80}
trot_grid = np.logspace(math.log10(HOUR), math.log10(10 * YEAR), 121)
te_grid = np.logspace(-3, math.log10(10 * YEAR), 121)
L32 = math.log(2 ** 31)
T_SHOR_FAST = 10 * 60.0   # ECC-256: Litinski 2023 / Babbush 2026
T_SHOR_SLOW = 25.7 * DAY  # ECC-256: IonQ 2026
map_rows = []
for log2R in LOG2R:
    for tr in trot_grid[::10]:
        for te in te_grid[::10]:
            ecdh_safe = te * L32 < T_SHOR_FAST
            ok = {}
            for name, cat, beta, lc, lq, lp, lg, src in SCHEMES[:3]:
                ok[name] = margin_log10(lq, log2R, tr, te, 32)[0] > 0
            if ecdh_safe:
                region = "A: ephemeral ECDH already safe (PQC not necessary against this adversary)"
            elif ok["ML-KEM-512"]:
                region = "B: PQC necessary and ML-KEM-512 sufficient"
            elif ok["ML-KEM-768"]:
                region = "B': PQC necessary; ML-KEM-768 sufficient, ML-KEM-512 not"
            elif ok["ML-KEM-1024"]:
                region = "B'': PQC necessary; only ML-KEM-1024 sufficient"
            else:
                region = "C: rule fails for all ML-KEM levels (shorten T_rot / bound T_E / long-term security)"
            map_rows.append((log2R, tr, te, ecdh_safe, ok["ML-KEM-512"], ok["ML-KEM-768"], ok["ML-KEM-1024"], region))
with open(os.path.join(HERE, "pqc_necessity_map.csv"), "w", encoding="utf-8") as fh:
    fh.write("# eps = 2^-32; quantum-sieving core-SVP exponents 107/166/232; ECDH threshold uses T_Shor(ECC-256) = 10 min\n")
    fh.write("log2_R,T_rot_s,T_E_s,ecdh_safe,mlkem512_ok,mlkem768_ok,mlkem1024_ok,region\n")
    for r in map_rows:
        fh.write(",".join(str(x) for x in r[:7]) + f',"{r[7]}"\n')

# ----------------------------------------------------------------------------------
# (4) Toy Fig. 5: Delta P(t) = (1/2) P_LWE(t0 + t) e^{-t/T_coh}
# ----------------------------------------------------------------------------------
M, S, A, B, B1, DI, TCOH = 30, 2.0, 0.3, 2.7, 10.0, 2.0, 20.0
TROT_TOY = 20.0  # illustrative rotation period for the toy panel, = T_coh (authors' choice; see memo)


def p_lwe_toy(t):
    t = np.atleast_1d(np.asarray(t, dtype=float))
    lam = B1 * math.sqrt(math.pi) / (2 * S)
    g = 2 * A / (np.log2(t) + B)
    i = np.arange(1, M + 1)
    return np.prod(erf(DI * lam * 2.0 ** (-np.outer(g, i - 1))), axis=1)


t_fine = np.linspace(0.5, 150.0, 299001)
pl = p_lwe_toy(t_fine)
pj = pl * 0.5 * (1 + np.exp(-t_fine / TCOH))
dp0 = 0.5 * pl * np.exp(-t_fine / TCOH)
k_j, k_d = int(np.argmax(pj)), int(np.argmax(dp0))
toy = dict(t_star_Pjoint=float(t_fine[k_j]), Pjoint_max=float(pj[k_j]),
           t_star_DeltaP_t0_0=float(t_fine[k_d]), DeltaP_max_t0_0=float(dp0[k_d]),
           P_LWE_at_tstar_DeltaP=float(pl[k_d]))
fig5 = {}
t_plot = np.concatenate(([0.0], np.linspace(0.5, 150.0, 2991)))
for label, t0 in (("t0=0", 0.0), ("t0=T_rot/2", TROT_TOY / 2), ("t0=T_rot", TROT_TOY)):
    tt = t_plot if t0 > 0 else t_plot[1:]
    d = 0.5 * p_lwe_toy(t0 + tt) * np.exp(-tt / TCOH)
    k = int(np.argmax(d))
    fig5[label] = (tt, d, float(tt[k]), float(d[k]))
    toy[f"t_star_{label}"] = float(tt[k])
    toy[f"DeltaP_max_{label}"] = float(d[k])
with open(os.path.join(HERE, "fig5a_deltaP.csv"), "w", encoding="utf-8") as fh:
    fh.write("# Replacement Fig. 5a: Delta P(t) = 0.5 P_LWE(t0+t) exp(-t/T_coh); toy parameters "
             f"m={M}, s={S}, a={A}, b={B}, ||b1||={B1}, d_i={DI}, T_coh={TCOH} s; T_rot(toy)={TROT_TOY} s\n")
    fh.write("t_s,DeltaP_t0_0,DeltaP_t0_half_Trot,DeltaP_t0_Trot,P_LWE_t0_0,P_joint_t0_0\n")
    tt = t_plot[1:]
    d0 = fig5["t0=0"][1]
    d1 = np.interp(tt, fig5["t0=T_rot/2"][0], fig5["t0=T_rot/2"][1])
    d2 = np.interp(tt, fig5["t0=T_rot"][0], fig5["t0=T_rot"][1])
    pl2 = p_lwe_toy(tt)
    for i in range(len(tt)):
        fh.write(f"{tt[i]:.6f},{d0[i]:.6e},{d1[i]:.6e},{d2[i]:.6e},{pl2[i]:.10f},{pl2[i]*0.5*(1+math.exp(-tt[i]/TCOH)):.10f}\n")

# Lindner-Peikert sanity check at the calibrated fit (a,b) = (1.8,110) for beta = 406 (ML-KEM-512)
def delta_root(beta):
    return ((math.pi * beta) ** (1 / beta) * beta / (2 * math.pi * math.e)) ** (1 / (2 * (beta - 1)))


lp = {}
for name, beta in (("ML-KEM-512", 406), ("ML-KEM-768", 626), ("ML-KEM-1024", 878)):
    d = delta_root(beta)
    lp[name] = dict(beta=beta, delta_root=d, log2_T_s=1.8 / math.log2(d) - 110)

# ----------------------------------------------------------------------------------
# Figures (prototypes)
# ----------------------------------------------------------------------------------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

C1, C2, C3, INK, INK2, GRID = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e6e4df"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": INK2,
                     "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False})

# --- Fig. 5a prototype: toy Delta P (log scale, three head starts) + deployed-parameter panel
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.4, 3.3))
for (label, (tt, d, ts, dm)), col in zip(fig5.items(), (C1, C2, C3)):
    ax1.plot(tt, d, color=col, lw=2, label=label.replace("t0", "$t_0$").replace("T_rot", "$T_{\\rm rot}$"))
    ax1.plot([ts], [dm], "o", ms=5, color=col, mec="white", mew=1)
ax1.set_yscale("log")
ax1.set_ylim(1e-6, 1)
ax1.set_xlim(0, 150)
ax1.set_xlabel("storage time $t$ since interception (s)")
ax1.set_ylabel(r"$\Delta P(t)=\frac{1}{2} P_{\rm LWE}(t_0+t)\,e^{-t/T_{\rm coh}^E}$")
ax1.set_title("(a) toy parameters of Fig. 5 ($T_{\\rm coh}^E$ = 20 s, $T_{\\rm rot}$ = 20 s)", fontsize=9, loc="left")
ax1.annotate(f"$t^*$ = {toy['t_star_DeltaP_t0_0']:.1f} s", xy=(toy['t_star_DeltaP_t0_0'], toy['DeltaP_max_t0_0']),
             xytext=(40, 0.5), fontsize=8, color=INK2, arrowprops=dict(arrowstyle="-", color=INK2, lw=0.6))
ax1.grid(color=GRID, lw=0.5)
ax1.legend(frameon=False, fontsize=8, loc="lower left")

tt2 = np.logspace(-3, math.log10(10 * YEAR), 600)
for (name, lam), col in zip((("ML-KEM-512", 107), ("ML-KEM-768", 166), ("ML-KEM-1024", 232)), (C1, C2, C3)):
    T_E_dep = DAY
    log10_dp = (np.log10(0.5) + np.minimum(0.0, np.log10((30 * DAY + tt2) * 2.0 ** 60 / 2.0 ** lam))
                - tt2 / T_E_dep / math.log(10))
    ax2.plot(tt2, log10_dp, color=col, lw=2, label=f"{name} ($\\lambda$={lam}, quantum sieving)")
ax2.axhline(-32 * math.log10(2), color=INK2, lw=0.8, ls="--")
ax2.text(2e-3, -32 * math.log10(2) + 1.5, r"$\epsilon = 2^{-32}$", fontsize=8, color=INK2)
ax2.axhline(-64 * math.log10(2), color=INK2, lw=0.8, ls=":")
ax2.text(2e-3, -64 * math.log10(2) + 1.5, r"$\epsilon = 2^{-64}$", fontsize=8, color=INK2)
ax2.set_xscale("log")
ax2.set_ylim(-120, 0)
ax2.set_xlabel("storage time $t$ since interception (s)")
ax2.set_ylabel(r"$\log_{10}\,\Delta P(t)$ (upper bound)")
ax2.set_title("(b) deployed: $R=2^{60}$/s, $T_{\\rm rot}$ = 30 d, $T_{\\rm coh}^E$ = 24 h",
              fontsize=9, loc="left")
ax2.grid(color=GRID, lw=0.5)
ax2.legend(frameon=False, fontsize=7.5, loc="lower left")
fig.tight_layout()
fig.savefig(os.path.join(HERE, "fig5a_deltaP_prototype.png"), dpi=200)
plt.close(fig)

# --- PQC necessity map
fig, axes = plt.subplots(1, 3, figsize=(11, 3.6), sharey=True)
for ax, log2R in zip(axes, LOG2R):
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(HOUR, 10 * YEAR); ax.set_ylim(1e-3, 10 * YEAR)
    # ECDH-safe band
    ax.axhspan(1e-3, T_SHOR_FAST / L32, color=GRID, alpha=0.9, lw=0)
    ax.text(1.3 * HOUR, 1.6e-3, "A: ephemeral ECDH already safe\n($T_E\\,\\ln(1/2\\epsilon) < T_{\\rm Shor}$, ECC-256 in 10 min)",
            fontsize=7, color=INK2, va="bottom")
    ax.axhline(T_SHOR_SLOW / L32, color=INK2, lw=0.8, ls=":")
    ax.text(8 * YEAR, T_SHOR_SLOW / L32 * 0.45, "ECDH threshold if ECC-256 takes 25.7 d (IonQ 2026)",
            fontsize=6.5, color=INK2, ha="right", va="top")
    notes = []
    for (name, lam), col in zip((("ML-KEM-512", 107), ("ML-KEM-768", 166), ("ML-KEM-1024", 232)), (C1, C2, C3)):
        budget = 2.0 ** (lam - log2R + 1 - 32)   # 2 eps 2^lambda / R  [s]
        tr = trot_grid[trot_grid < budget]
        if len(tr) == 0:
            notes.append((f"{name}: fails everywhere here\n(budget {fmt_t(budget)})", col))
            continue
        te = (budget - tr) / L32
        if te[0] > 10 * YEAR:
            notes.append((f"{name}: holds everywhere here\n(budget {fmt_t(budget)})", col))
            continue
        ax.plot(tr, te, color=col, lw=2, label=f"{name} boundary ($\\lambda$={lam})")
        ax.text(tr[0] * 1.2, te[0] * 0.45, f"{name} boundary", fontsize=7, color=col)
    for j, (txt, col) in enumerate(notes):
        ax.text(1.3 * HOUR, 3 * YEAR / (12.0 ** j), txt, fontsize=6.5, color=col, va="top")
    ax.set_title(f"$R = 2^{{{log2R}}}$ ops/s", fontsize=9)
    ax.set_xlabel("key-rotation period $T_{\\rm rot}$ (s)")
    for v, lab in ((DAY, "1 d"), (30 * DAY, "30 d"), (YEAR, "1 y")):
        ax.axvline(v, color=GRID, lw=0.6)
        ax.text(v, 12 * YEAR, lab, fontsize=7, color=INK2, ha="center")
    for v, lab in ((1.0, "1 s"), (HOUR, "1 h"), (DAY, "24 h")):
        ax.axhline(v, color=GRID, lw=0.6)
    ax.grid(False)
axes[0].set_ylabel("adversary memory lifetime $T_{\\rm coh}^E$ (s)")
fig.suptitle("When is PQC necessary vs sufficient?  $\\epsilon=2^{-32}$, quantum-sieving core-SVP $\\lambda$ = 107/166/232.\n"
             "Grey band A: ephemeral ECDH already safe. Above it (B): PQC necessary; the design rule holds below a scheme's "
             "boundary. Top edge $T_E\\to\\infty$: rule = long-term security.",
             fontsize=8, color=INK)
fig.tight_layout(rect=(0, 0, 1, 0.93))
fig.savefig(os.path.join(HERE, "pqc_necessity_map_prototype.png"), dpi=200)
plt.close(fig)

# ----------------------------------------------------------------------------------
# Summary for the memo
# ----------------------------------------------------------------------------------
summary = dict(toy=toy, lindner_peikert_check=lp,
               ecdh_thresholds={f"{lab} eps=2^-{e}": fmt_t(th) for lab, tg, rt, e, th in ecdh_rows},
               te_max_examples={})
for name, cat, beta, lc, lq, lp_, lg, src in SCHEMES:
    for model, lam in (("classical", lc), ("quantum", lq)):
        for log2R in LOG2R:
            for e in EPS:
                tm, budget = te_max(lam, log2R, 30 * DAY, e)
                summary["te_max_examples"][f"{name} {model} R=2^{log2R} eps=2^-{e} Trot=30d"] = \
                    dict(budget_s=budget, budget=fmt_t(budget), T_E_max=fmt_t(tm))
with open(os.path.join(HERE, "summary.json"), "w", encoding="utf-8") as fh:
    json.dump(summary, fh, indent=1)
print(json.dumps(toy, indent=1))
print(json.dumps(lp, indent=1))
for lab, tg, rt, e, th in ecdh_rows:
    print(f"{lab:40s} eps=2^-{e}: ECDH safe iff T_E < {fmt_t(th)}")
print("done")
