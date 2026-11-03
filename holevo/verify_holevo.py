"""
verify_holevo.py -- numerical verification of every closed form in holevo_correct.py against a
direct 3-qubit density-matrix simulation.  Writes verification_table.md and verification_table.csv
next to this file.  Run:  python verify_holevo.py
"""
import os, sys, itertools
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import holevo_correct as hc

np.set_printoptions(precision=6, suppress=True, linewidth=120)
lines = []


def say(s=""):
    print(s)
    lines.append(s)


# ---------------------------------------------------------------- 0. labelling and commutation
say("# Verification of the corrected R3/R4 analysis (3-qubit density-matrix simulation)")
say()
say("## 0. Sanity checks on the simulation itself")
alpha, beta = np.sqrt(0.6), np.sqrt(0.4)
cs0 = hc.simulate_conditional_states(alpha, beta, 0.0)
ok = True
for (m1, m2), (p, r) in cs0.items():
    target = hc.sigma_m(m1, m2) @ hc.psi_vec(alpha, beta)
    ok &= abs(p - 0.25) < 1e-12 and np.allclose(r, np.outer(target, target.conj()), atol=1e-12)
say(f"- gamma=0: p_m = 1/4 and Bob holds X^m1 Z^m2 |psi> for every outcome: {'PASS' if ok else 'FAIL'}")
maxdiff = 0.0
for g in (0.1, 0.5, 0.9):
    A = hc.simulate_conditional_states(alpha, beta, g, damping_after_measurement=False)
    B = hc.simulate_conditional_states(alpha, beta, g, damping_after_measurement=True)
    for m in A:
        maxdiff = max(maxdiff, abs(A[m][0] - B[m][0]), np.max(np.abs(A[m][1] - B[m][1])))
say(f"- damping before vs after Alice's measurement, max |difference| over all outcomes: {maxdiff:.1e} (they commute)")

# ---------------------------------------------------------------- 1. conditional states and spectra
say()
say("## 1. Conditional states, probabilities, spectra, averaged state")
grid_g = [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
grid_a2 = [0.0, 0.25, 0.6, 1.0]
worst_state = worst_p = worst_avg = worst_det = 0.0
worst_pauli = 0.0
for g, a2 in itertools.product(grid_g, grid_a2):
    al, be = np.sqrt(a2), np.sqrt(1 - a2)
    sim = hc.simulate_conditional_states(al, be, g)
    cl = hc.conditional_states_closed(al, be, g)
    for m in sim:
        worst_p = max(worst_p, abs(sim[m][0] - 0.25))
        worst_state = max(worst_state, np.max(np.abs(sim[m][1] - cl[m])))
    rho_avg = sum(sim[m][0] * sim[m][1] for m in sim)
    worst_avg = max(worst_avg, np.max(np.abs(rho_avg - np.diag([(1 + g) / 2, (1 - g) / 2]))))
    d_beta, d_alpha = hc.deltas(al, be, g)
    for m in sim:
        det = np.real(np.linalg.det(sim[m][1]))
        target = g * (1 - g) * (be ** 4 if m[0] == 0 else al ** 4)
        worst_det = max(worst_det, abs(det - target))
    # how far the submitted Pauli-conjugate assumption is from the truth
    rho00 = sim[(0, 0)][1]
    for m in sim:
        S = hc.sigma_m(*m)
        worst_pauli = max(worst_pauli, np.max(np.abs(sim[m][1] - S @ rho00 @ S.conj().T)))
say(f"- grid: gamma in {grid_g}, |alpha|^2 in {grid_a2}")
say(f"- max |p_m - 1/4|                                   : {worst_p:.1e}")
say(f"- max |rho_m(sim) - AD(sigma_m psi sigma_m^dag)|     : {worst_state:.1e}")
say(f"- max |rho_avg(sim) - diag((1+g)/2,(1-g)/2)|         : {worst_avg:.1e}")
say(f"- max |det rho_m - g(1-g)|beta|^4 (m1=0) / |alpha|^4 (m1=1)| : {worst_det:.1e}")
say(f"- max |rho_m(sim) - sigma_m rho_00 sigma_m^dag| (submitted assumption): {worst_pauli:.3f}  <-- NOT small")
say()
say("Example gamma = 0.5, |alpha|^2 = 0.6 (the parameters of Fig. 7):")
sim = hc.simulate_conditional_states(alpha, beta, 0.5)
for m in sim:
    say(f"  rho_{m[0]}{m[1]} = {np.real(sim[m][1]).tolist()}  eig = {np.linalg.eigvalsh(sim[m][1]).round(6).tolist()}")
say(f"  rho_avg = {np.real(sum(sim[m][0]*sim[m][1] for m in sim)).round(6).tolist()}")

# ---------------------------------------------------------------- 2. chi_K
say()
say("## 2. Holevo quantities chi_K: closed form vs simulation (bits)")
say()
say("| gamma | alpha^2 | chi_empty sim | chi_empty closed | chi_empty SUBMITTED | chi_{1} sim | chi_{1} closed | chi_{2} sim | chi_{2} closed |")
say("|---|---|---|---|---|---|---|---|---|")
csv = ["gamma,alpha_sq,chi_empty_sim,chi_empty_closed,chi_empty_submitted,chi_1_sim,chi_1_closed,chi_1_submitted,"
       "chi_2_sim,chi_2_closed,chi_2_submitted,Flam_empty_sim,Flam_empty_closed,Flam_1_sim,Flam_1_closed,"
       "Flam_2_sim,Flam_2_closed,Flam_12_sim,Flam_12_closed"]
worst_chi = 0.0
worst_F = 0.0
for g, a2 in itertools.product(grid_g, grid_a2):
    al, be = np.sqrt(a2), np.sqrt(1 - a2)
    s, _, _ = hc.chi_K_sim(al, be, g)
    c = hc.chi_K_closed(al, be, g)
    p = hc.chi_paper(al, be, g)
    Fs = hc.F_lam_sim(al, be, g)
    Fc = hc.F_lam_closed(al, be, g)
    for K in ("empty", "1", "2"):
        worst_chi = max(worst_chi, abs(s[K] - float(c[K])))
    for K in ("empty", "1", "2", "12"):
        worst_F = max(worst_F, abs(Fs[K] - float(Fc[K])))
    say(f"| {g:.1f} | {a2:.2f} | {s['empty']:.4f} | {float(c['empty']):.4f} | {float(p['empty']):.4f} | "
        f"{s['1']:.4f} | {float(c['1']):.4f} | {s['2']:.4f} | {float(c['2']):.4f} |")
    csv.append(",".join(f"{v:.10f}" for v in [g, a2, s['empty'], float(c['empty']), float(p['empty']),
                                                s['1'], float(c['1']), float(p['1']), s['2'], float(c['2']), float(p['2']),
                                                Fs['empty'], float(Fc['empty']), Fs['1'], float(Fc['1']),
                                                Fs['2'], float(Fc['2']), Fs['12'], float(Fc['12'])]))
say()
say(f"- max |chi_K(closed) - chi_K(sim)| over the grid and K in {{empty,{{1}},{{2}}}}: {worst_chi:.1e}")
say(f"- chi at gamma = 1 (all |alpha|^2): simulation gives {hc.chi_K_sim(alpha, beta, 1.0)[0]['empty']:.2e}; "
    f"submitted formula gives {float(hc.chi_paper(alpha, beta, 1.0)['empty']):.2f}")

# complex-phase input
say()
say("Complex input alpha = sqrt(0.6), beta = sqrt(0.4) e^{i 0.7} (tests the Re(alpha beta^*) dependence of chi_{2}):")
al, be = np.sqrt(0.6), np.sqrt(0.4) * np.exp(0.7j)
for g in (0.2, 0.5):
    s, _, _ = hc.chi_K_sim(al, be, g)
    c = hc.chi_K_closed(al, be, g)
    say(f"  gamma={g}: chi_empty sim {s['empty']:.6f} closed {float(c['empty']):.6f}; "
        f"chi_1 sim {s['1']:.6f} closed {float(c['1']):.6f}; chi_2 sim {s['2']:.6f} closed {float(c['2']):.6f}")

# ---------------------------------------------------------------- 3. F_K^lambda
say()
say("## 3. Manuscript-style F_K (largest eigenvalue of Eve's averaged state), closed vs simulation")
say(f"- max |F_K^lam(closed) - F_K^lam(sim)| over the grid, all four K: {worst_F:.1e}")
say()
say("| gamma | F_empty (corr.) | F_empty (subm.) | F_{1} (corr.) | F_{1} (subm.) | F_{2} (corr.) | F_{2} (subm.) | F_{12} (corr.) | F_{12} (subm.) |  (|alpha|^2 = 0.6)")
say("|---|---|---|---|---|---|---|---|---|")
for g in (0.0, 0.1, 0.3, 0.5, 0.9, 1.0):
    Fc = hc.F_lam_closed(alpha, beta, g)
    Fp = hc.F_lam_paper(alpha, beta, g)
    say(f"| {g:.1f} | {float(Fc['empty']):.4f} | {float(Fp['empty']):.4f} | {float(Fc['1']):.4f} | {float(Fp['1']):.4f} | "
        f"{float(Fc['2']):.4f} | {float(Fp['2']):.4f} | {float(Fc['12']):.4f} | {float(Fp['12']):.4f} |")

# ---------------------------------------------------------------- 4. operational Fbar
say()
say("## 4. Operational adversary fidelity Fbar_K (psi-independent strategy, Haar average)")
say()
say("| gamma | K | closed form | 2-design (exact Haar, sim) | Monte Carlo (4000 psi, sim) |")
say("|---|---|---|---|---|")
worst_Fb = 0.0
for g in (0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0):
    cl = hc.Fbar_closed(g)
    d2 = hc.Fbar_sim_haar(g)
    mc = hc.Fbar_sim_haar_mc(g, n=4000, seed=1)
    for K in ("empty", "1", "2", "12"):
        worst_Fb = max(worst_Fb, abs(float(cl[K]) - d2[K]))
        say(f"| {g:.1f} | {K} | {float(cl[K]):.6f} | {d2[K]:.6f} | {mc[K]:.4f} |")
say()
say(f"- max |Fbar_K(closed) - Fbar_K(2-design sim)|: {worst_Fb:.1e}")
say("- Fbar_{12} equals (2 F_e + 1)/3 with F_e = (1+sqrt(1-gamma))^2/4, the known average fidelity of standard "
    "teleportation through the amplitude-damped Bell pair (Bob applies the Pauli correction).")

# ---------------------------------------------------------------- 5. optimality of Fbar over all CPTP recoveries
say()
say("## 5. Is the Pauli-correction strategy optimal?  Numerical maximisation over ALL CPTP recovery maps")
say("Entanglement fidelity F_e(Lambda o N_K) maximised over Stinespring isometries V: C^2 -> C^2 (x) C^4 "
    "(Kraus rank up to 4), 40 random restarts, BFGS.  Haar-average fidelity = (2 F_e + 1)/3.")
from scipy.optimize import minimize

def kraus_from_params(x):
    M = (x[:16] + 1j * x[16:]).reshape(8, 2)
    Q, _ = np.linalg.qr(M)            # 8x2 isometry
    return [Q[2 * k:2 * k + 2, :] for k in range(4)]

def Fe_composed(Rs, pre_kraus):
    # F_e(Lambda o N) = 1/4 sum_{j,k} |Tr(R_j N_k)|^2
    return sum(abs(np.trace(R @ N)) ** 2 for R in Rs for N in pre_kraus) / 4

def pre_kraus_for(K, g):
    E = hc.ad_kraus(g)
    P0, P1 = np.diag([1, 0]).astype(complex), np.diag([0, 1]).astype(complex)
    if K == "12":
        return E
    if K == "1":   # Z-dephasing (average over m2) then AD
        return [Ek @ P for Ek in E for P in (P0, P1)]
    if K == "2":   # X-dephasing (average over m1) then AD
        return [Ek @ U / np.sqrt(2) for Ek in E for U in (hc.I2, hc.X)]
    raise ValueError

say()
say("| gamma | K | Fbar closed (Pauli correction) | best found over all CPTP | difference |")
say("|---|---|---|---|---|")
rng = np.random.default_rng(7)
for g in (0.2, 0.5, 0.8):
    for K in ("1", "2", "12"):
        pre = pre_kraus_for(K, g)
        best = 0.0
        for _ in range(40):
            x0 = rng.normal(size=32)
            res = minimize(lambda x: -Fe_composed(kraus_from_params(x), pre), x0, method="BFGS")
            best = max(best, -res.fun)
        Fbar_best = (2 * best + 1) / 3
        cl = float(hc.Fbar_closed(g)[K])
        say(f"| {g:.1f} | {K} | {cl:.6f} | {Fbar_best:.6f} | {Fbar_best - cl:+.1e} |")

# ---------------------------------------------------------------- 6. the review's table
say()
say("## 6. Reproduction of the review's table (|alpha|^2 = 0.6)")
say()
say("| gamma | chi correct (sim) | chi submitted formula |")
say("|---|---|---|")
for g in (0.1, 0.3, 0.5, 0.9, 1.0):
    s, _, _ = hc.chi_K_sim(alpha, beta, g)
    say(f"| {g:.1f} | {s['empty']:.3f} | {float(hc.chi_paper(alpha, beta, g)['empty']):.3f} |")

with open(os.path.join(HERE, "verification_table.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
with open(os.path.join(HERE, "verification_table.csv"), "w", encoding="utf-8") as f:
    f.write("\n".join(csv) + "\n")
print("\nwrote verification_table.md and verification_table.csv")
