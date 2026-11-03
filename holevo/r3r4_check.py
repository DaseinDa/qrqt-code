"""
r3r4_check.py -- numerical verification of every formula written into
r3_proposal.tex, r4_proposal.tex, holevo_06_proposal.tex, holevo_07_proposal.tex and
appendix_holevo_proposal.tex, against the direct 3-qubit density-matrix simulation of
_sciadv_work/holevo/holevo_correct.py and against the Fig. 7 prototype CSVs.
Run (from this folder):  python -I r3r4_check.py > r3r4_check.txt
"""
import os, sys, csv
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
HOLEVO = os.path.normpath(os.path.join(HERE, "..", "holevo"))
sys.path.insert(0, HOLEVO)
import holevo_correct as hc  # noqa: E402

h, H2 = hc.h, hc.H2
fails = []


def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    if not cond:
        fails.append(name)
    print(f"[{status}] {name}" + (f"  ({detail})" if detail else ""))


def psi_of(a2, phase=0.0):
    return np.sqrt(a2), np.sqrt(1 - a2) * np.exp(1j * phase)


def bob_reduced(al, be, g):
    """Tr_CA of (I x I x E_AD)(psi x Phi+): Bob's reduced state, no measurement information."""
    psi = hc.psi_vec(al, be)
    phi = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
    st = np.kron(psi, phi)
    rho3 = np.outer(st, st.conj())
    rho3 = sum(np.kron(np.eye(4), E) @ rho3 @ np.kron(np.eye(4), E).conj().T for E in hc.ad_kraus(g))
    return np.einsum("iaib->ab", rho3.reshape(4, 2, 4, 2))


print("=" * 78)
print("1. Conditional states, probabilities, averaged state (closed forms written in the proposal)")
print("=" * 78)
grid_g = [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
grid_a = [0.0, 0.25, 0.6, 1.0]
worst = dict(p=0.0, rho=0.0, avg=0.0, det=0.0, bobred=0.0)
for g in grid_g:
    for a2 in grid_a:
        for ph in (0.0, 0.7):
            al, be = psi_of(a2, ph)
            sim = hc.simulate_conditional_states(al, be, g)
            closed = hc.conditional_states_closed(al, be, g)
            psi = hc.psi_vec(al, be)
            A2, B2 = abs(al) ** 2, abs(be) ** 2
            for m, (p, r) in sim.items():
                worst["p"] = max(worst["p"], abs(p - 0.25))
                worst["rho"] = max(worst["rho"], np.abs(r - closed[m]).max())
                s = hc.sigma_m(*m)
                direct = hc.ad(s @ np.outer(psi, psi.conj()) @ s.conj().T, g)
                worst["rho"] = max(worst["rho"], np.abs(r - direct).max())
                det_expected = g * (1 - g) * (B2 ** 2 if m[0] == 0 else A2 ** 2)
                worst["det"] = max(worst["det"], abs(np.linalg.det(r).real - det_expected))
            rho_avg = sum(p * r for p, r in sim.values())
            worst["avg"] = max(worst["avg"], np.abs(rho_avg - np.diag([(1 + g) / 2, (1 - g) / 2])).max())
            worst["bobred"] = max(worst["bobred"], np.abs(bob_reduced(al, be, g) - rho_avg).max())
check("p_m = 1/4 for all outcomes", worst["p"] < 1e-12, "max dev %.1e" % worst["p"])
check("rho_m = E_AD(sigma_m psi sigma_m^dag) with entries (a,b,c) and (a',b',c'=c^*)", worst["rho"] < 1e-12, "max dev %.1e" % worst["rho"])
check("det rho_{0 m2} = g(1-g)|beta|^4, det rho_{1 m2} = g(1-g)|alpha|^4", worst["det"] < 1e-12, "max dev %.1e" % worst["det"])
check("rho_avg = diag((1+g)/2,(1-g)/2) = E_AD(I/2)", worst["avg"] < 1e-12, "max dev %.1e" % worst["avg"])
check("rho_avg equals Bob's reduced state Tr_CA[(I x E_AD)(psi x Phi+)] (no-signalling)", worst["bobred"] < 1e-12, "max dev %.1e" % worst["bobred"])

al, be = psi_of(0.6)
sim = hc.simulate_conditional_states(al, be, 0.5)
r00 = sim[(0, 0)][1]
Xr = hc.X @ r00 @ hc.X
dev = np.abs(sim[(1, 0)][1] - Xr).max()
check("submitted assumption rho_10 = X rho_00 X is violated at gamma=0.5, |alpha|^2=0.6", dev > 0.1, "max entry dev %.3f" % dev)
print("   rho_00 =", np.round(r00.real, 4).tolist(), " rho_10 =", np.round(sim[(1, 0)][1].real, 4).tolist(),
      " X rho_00 X =", np.round(Xr.real, 4).tolist())

print()
print("=" * 78)
print("2. chi_K closed forms vs simulation; boundary checks stated in the SI")
print("=" * 78)
worst_chi = 0.0
for g in grid_g:
    for a2 in grid_a:
        for ph in (0.0, 0.7):
            al, be = psi_of(a2, ph)
            s, _, _ = hc.chi_K_sim(al, be, g)
            c = hc.chi_K_closed(al, be, g)
            for K in ("empty", "1", "2", "12"):
                worst_chi = max(worst_chi, abs(s[K] - float(c[K])))
check("chi_empty = h(g) - [h(d_beta)+h(d_alpha)]/2 ; chi_1, chi_2, chi_12 = 0 vs simulation", worst_chi < 1e-12, "max dev %.1e" % worst_chi)

for g in (0.2, 0.5, 0.8):
    for a2 in (0.25, 0.6):
        al, be = psi_of(a2)
        A2, B2 = a2, 1 - a2
        a, ap = A2 + g * B2, B2 + g * A2
        b, bp = (1 - g) * B2, (1 - g) * A2
        check("1-2a = |beta|^2(1-2g)-|alpha|^2 (g=%s, a2=%s)" % (g, a2), abs((1 - 2 * a) - (B2 * (1 - 2 * g) - A2)) < 1e-14)
        check("1-2a' = |alpha|^2(1-2g)-|beta|^2 (g=%s, a2=%s)" % (g, a2), abs((1 - 2 * ap) - (A2 * (1 - 2 * g) - B2)) < 1e-14)
        sim = hc.simulate_conditional_states(al, be, g)
        avg_m2_0 = (sim[(0, 0)][1] + sim[(1, 0)][1]) / 2
        avg_m2_1 = (sim[(0, 1)][1] + sim[(1, 1)][1]) / 2
        r = np.real(al * np.conj(be)) * np.sqrt(1 - g)
        expect = np.array([[(1 + g) / 2, r], [r, (1 - g) / 2]])
        expect1 = np.array([[(1 + g) / 2, -r], [-r, (1 - g) / 2]])
        check("K={2}: (rho_00+rho_10)/2 = [[(1+g)/2, r],[r,(1-g)/2]], m2=1 with r -> -r (g=%s, a2=%s)" % (g, a2),
              np.abs(avg_m2_0 - expect).max() < 1e-14 and np.abs(avg_m2_1 - expect1).max() < 1e-14)
        ev = np.linalg.eigvalsh(avg_m2_0)
        check("K={2}: eigenvalue gap = sqrt(g^2+4r^2) (g=%s, a2=%s)" % (g, a2), abs((ev[1] - ev[0]) - np.sqrt(g ** 2 + 4 * r ** 2)) < 1e-13)
        avg_m1_0 = (sim[(0, 0)][1] + sim[(0, 1)][1]) / 2
        avg_m1_1 = (sim[(1, 0)][1] + sim[(1, 1)][1]) / 2
        check("K={1}: averaged states diag(a,b) for m1=0 and diag(a',b') for m1=1 (g=%s, a2=%s)" % (g, a2),
              np.abs(avg_m1_0 - np.diag([a, b])).max() < 1e-14 and np.abs(avg_m1_1 - np.diag([ap, bp])).max() < 1e-14)

for a2 in grid_a:
    al, be = psi_of(a2)
    s0, _, _ = hc.chi_K_sim(al, be, 0.0)
    check("gamma=0: chi_empty = 1 bit (|alpha|^2=%s)" % a2, abs(s0["empty"] - 1) < 1e-12, "%.12f" % s0["empty"])
    s1, _, st1 = hc.chi_K_sim(al, be, 1.0)
    allzero = all(np.abs(st1[m] - np.diag([1, 0])).max() < 1e-12 for m in st1)
    check("gamma=1: all four conditional states = |0><0| (|alpha|^2=%s)" % a2, allzero)
    check("gamma=1: chi_K = 0 for all K (|alpha|^2=%s)" % a2, max(abs(s1[K]) for K in s1) < 1e-12, "max %.1e" % max(abs(s1[K]) for K in s1))
gam = np.linspace(0, 1, 201)
for a2 in (0.1, 0.3, 0.6):
    c1 = hc.chi_K_closed(*psi_of(a2), gam)["empty"]
    c2 = hc.chi_K_closed(*psi_of(1 - a2), gam)["empty"]
    check("chi_empty symmetric under |alpha|^2 <-> |beta|^2 (a2=%s)" % a2, np.abs(c1 - c2).max() < 1e-12)
    check("chi_empty monotonically non-increasing in gamma (a2=%s)" % a2, bool(np.all(np.diff(c1) <= 1e-12)))
c_half = hc.chi_K_closed(*psi_of(0.5), gam)["empty"]
ok = True
for a2 in (0.0, 0.1, 0.25, 0.4, 0.75, 1.0):
    ok &= bool(np.all(hc.chi_K_closed(*psi_of(a2), gam)["empty"] <= c_half + 1e-12))
check("chi_empty maximal at |alpha|^2 = 1/2 for every gamma", ok)
c_zero = hc.chi_K_closed(*psi_of(1.0), gam)["empty"]
check("|0> or |1> input: chi_empty = h(gamma) - h(|1-2gamma|)/2", np.abs(c_zero - (h(gam) - h(np.abs(1 - 2 * gam)) / 2)).max() < 1e-12)
c6 = hc.chi_K_closed(*psi_of(0.6), gam)["empty"]
check("NO symmetry about gamma=1/2 (chi(0.1) != chi(0.9) at |alpha|^2=0.6)", abs(c6[20] - c6[180]) > 0.5, "chi(0.1)=%.3f, chi(0.9)=%.3f" % (c6[20], c6[180]))
# spread of the |alpha|^2 family in Fig. 6a (statement in the proposal: ordering reversed, spread small)
spread = np.max([np.abs(hc.chi_K_closed(*psi_of(0.5), gam)["empty"] - hc.chi_K_closed(*psi_of(0.1), gam)["empty"]).max()])
spread_full = np.max([np.abs(hc.chi_K_closed(*psi_of(0.5), gam)["empty"] - hc.chi_K_closed(*psi_of(0.0), gam)["empty"]).max()])
print("   max spread between |alpha|^2=0.5 and 0.1 curves over gamma: %.3f bit (full range 0.5 vs 0.0: %.3f bit)" % (spread, spread_full))
check("Fig. 6a family |alpha|^2 in [0.1,0.5]: spread below 0.1 bit (statement in R3 / SI Note 9)", spread < 0.1)

print()
print("=" * 78)
print("3. Renamed F_K (maximal overlap with Bob's conditional state) and proposed Fbar_K")
print("=" * 78)
worst_F = 0.0
for g in grid_g:
    for a2 in grid_a:
        al, be = psi_of(a2)
        Fs = hc.F_lam_sim(al, be, g)
        Fc = hc.F_lam_closed(al, be, g)
        for K in Fs:
            worst_F = max(worst_F, abs(Fs[K] - float(Fc[K])))
check("F_K closed forms (1+g)/2, 1/2+(|1-2a|+|1-2a'|)/4, (1+sqrt(g^2+4r^2))/2, 1/2+(d_beta+d_alpha)/4 vs simulation",
      worst_F < 1e-12, "max dev %.1e" % worst_F)
worst_Fb = 0.0
for g in (0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0):
    Fb2 = hc.Fbar_sim_haar(g)
    Fbc = hc.Fbar_closed(g)
    for K in Fb2:
        worst_Fb = max(worst_Fb, abs(Fb2[K] - float(Fbc[K])))
check("Fbar_K closed forms 1/2, 2/3-g/6, 1/2+sqrt(1-g)/6, 2/3-g/6+sqrt(1-g)/3 vs exact Haar (2-design) simulation",
      worst_Fb < 1e-12, "max dev %.1e" % worst_Fb)
mc = hc.Fbar_sim_haar_mc(0.3, n=2000, seed=1)
print("   Monte-Carlo Haar average at gamma=0.3 (2000 inputs):", {K: round(v, 4) for K, v in mc.items()},
      " closed:", {K: round(float(v), 4) for K, v in hc.Fbar_closed(0.3).items()})
for g in (0.0, 0.3, 0.7):
    Fe = (1 + np.sqrt(1 - g)) ** 2 / 4
    check("Fbar_12 = (2 F_e + 1)/3 with F_e = (1+sqrt(1-g))^2/4 (g=%s)" % g, abs(float(hc.Fbar_closed(g)["12"]) - (2 * Fe + 1) / 3) < 1e-14)
check("Fbar_1 = Fbar_2 = 2/3 at gamma=0", abs(float(hc.Fbar_closed(0.0)["1"]) - 2 / 3) < 1e-14 and abs(float(hc.Fbar_closed(0.0)["2"]) - 2 / 3) < 1e-14)
check("all Fbar_K -> 1/2 at gamma=1", max(abs(float(v) - 0.5) for v in hc.Fbar_closed(1.0).values()) < 1e-14)
check("Fbar_K decreasing in gamma for K = {1},{2},{1,2}", all(bool(np.all(np.diff(hc.Fbar_closed(gam)[K]) <= 1e-12)) for K in ("1", "2", "12")))
al, be = psi_of(0.6)
F1 = hc.F_lam_closed(al, be, 1.0)
sim1 = hc.simulate_conditional_states(al, be, 1.0)
psi = hc.psi_vec(al, be)
ov = {}
for m, (p, r) in sim1.items():
    U = np.linalg.matrix_power(hc.Z, m[1]) @ np.linalg.matrix_power(hc.X, m[0])
    ov[m] = float(np.real(psi.conj() @ (U @ r @ U.conj().T) @ psi))
ov_avg = sum(0.25 * v for v in ov.values())
check("gamma=1: F_12 = 1 while the fidelity with |psi> after Pauli correction is |alpha|^2 (m1=0), |beta|^2 (m1=1), 1/2 on average",
      abs(float(F1["12"]) - 1) < 1e-12 and abs(ov[(0, 0)] - 0.6) < 1e-12 and abs(ov[(1, 0)] - 0.4) < 1e-12 and abs(ov_avg - 0.5) < 1e-12,
      "F_12=%.3f, overlaps=%s, avg=%.3f" % (float(F1["12"]), {m: round(v, 3) for m, v in ov.items()}, ov_avg))
check("F_empty = (1+gamma)/2 > 1/2 for gamma>0 (guessing |0>)", abs(float(hc.F_lam_closed(al, be, 0.5)["empty"]) - 0.75) < 1e-14)
check("F_empty = largest eigenvalue of rho_avg", abs(float(hc.F_lam_closed(al, be, 0.5)["empty"]) - np.linalg.eigvalsh(np.diag([0.75, 0.25]))[-1]) < 1e-14)

print()
print("=" * 78)
print("4. Numbers quoted in the R3 text (|alpha|^2 = 0.6)")
print("=" * 78)
al, be = psi_of(0.6)
print("gamma  chi_empty chi_1  chi_2  | subm: chi_empty chi_1 chi_2 | F_empty F_1   F_2   F_12  | Fbar_1 Fbar_2 Fbar_12")
for g in (0.0, 0.1, 0.2, 0.3, 0.5, 0.9, 1.0):
    c = hc.chi_K_closed(al, be, g); cp = hc.chi_paper(al, be, g)
    F = hc.F_lam_closed(al, be, g); Fb = hc.Fbar_closed(g)
    print("%4.1f   %.3f     %.3f  %.3f  |       %.3f     %.3f %.3f | %.3f   %.3f %.3f %.3f | %.3f  %.3f  %.3f" % (
        g, float(c["empty"]), float(c["1"]), float(c["2"]), float(cp["empty"]), float(cp["1"]), float(cp["2"]),
        float(F["empty"]), float(F["1"]), float(F["2"]), float(F["12"]), float(Fb["1"]), float(Fb["2"]), float(Fb["12"])))

print()
print("=" * 78)
print("5. Fig. 7 curve descriptions (|alpha|^2 = 0.6, k1 = k2 = k = 1): E[chi(t)], F(t) = sum_K P_K F_K (renamed F_K), Fbar(t)")
print("=" * 78)
t = np.linspace(0, 5, 501)
GAMMAS = [0.0, 0.1, 0.2, 0.3]
MUS = [0.0, 0.3, 0.6, 0.9]


def load_csv(model):
    rows = {}
    with open(os.path.join(HOLEVO, "fig7_%s_prototype.csv" % model)) as f:
        rd = csv.reader(l for l in f if not l.startswith("#"))
        header = next(rd)
        for row in rd:
            rows.setdefault(float(row[1]), []).append([float(x) for x in row])
    return header, {k: np.array(v) for k, v in rows.items()}


for model in ("independent", "sequential", "burst", "correlated"):
    header, data = load_csv(model)
    fam = [(g, dict(gamma=g, mu=0.0)) for g in GAMMAS] if model != "correlated" else [(mu, dict(gamma=0.5, mu=mu)) for mu in MUS]
    worst_csv = 0.0
    curves = {}
    ic, ib, il = header.index("expected_holevo_bits"), header.index("eve_fidelity_operational"), header.index("eve_maxoverlap_lambda")
    for key, kw in fam:
        Echi, EFl, EFb, P = hc.expected_curves(model, t, al, be, kw["gamma"], k=1.0, mu=kw["mu"])
        d = data[key]
        worst_csv = max(worst_csv, np.abs(d[:, ic] - Echi).max(), np.abs(d[:, ib] - EFb).max(), np.abs(d[:, il] - EFl).max())
        curves[key] = (Echi, EFl, EFb, P)
        check("%s: sum_K P_K(t) = 1" % model, np.abs(sum(P.values()) - 1).max() < 1e-12)
    check("%s: recomputed E[chi], F (renamed F_K), Fbar agree with fig7_%s_prototype.csv" % (model, model), worst_csv < 1e-9, "max dev %.1e" % worst_csv)
    print("-- %s" % model)
    for key in curves:
        Echi, EFl, EFb, P = curves[key]
        lab = ("gamma=%s" % key) if model != "correlated" else ("mu=%s (gamma=0.5)" % key)
        mono_chi = bool(np.all(np.diff(Echi) <= 1e-12))
        mono_F = bool(np.all(np.diff(EFl) >= -1e-12))
        print("   %-20s E[chi](0)=%.3f E[chi](1)=%.3f E[chi](5)=%.4f dec=%s | F(0)=%.3f F(1)=%.3f F(5)=%.3f inc=%s | Fbar(1)=%.3f Fbar(5)=%.3f" % (
            lab, Echi[0], Echi[100], Echi[-1], mono_chi, EFl[0], EFl[100], EFl[-1], mono_F, EFb[100], EFb[-1]))
    if model != "correlated":
        keys = list(curves)
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                diff = curves[keys[i]][1] - curves[keys[j]][1]
                sc = np.where(np.diff(np.sign(diff[1:])) != 0)[0]
                if len(sc):
                    print("   F(t) crossing gamma=%s vs gamma=%s at t ~ %.2f" % (keys[i], keys[j], t[sc[0] + 1]))
                diffb = curves[keys[i]][2] - curves[keys[j]][2]
                scb = np.where(np.diff(np.sign(diffb[1:])) != 0)[0]
                if len(scb):
                    print("   Fbar(t) crossing gamma=%s vs gamma=%s at t ~ %.2f" % (keys[i], keys[j], t[scb[0] + 1]))
        Echi_order_ok = all(bool(np.all(curves[keys[i]][0] >= curves[keys[i + 1]][0] - 1e-12)) for i in range(len(keys) - 1))
        check("%s: E[chi(t)] curves keep their ordering in gamma (no crossing)" % model, Echi_order_ok)
        F_start_inc = all(curves[keys[i]][1][0] < curves[keys[i + 1]][1][0] for i in range(len(keys) - 1))
        F_end_dec = all(curves[keys[i]][1][-1] > curves[keys[i + 1]][1][-1] for i in range(len(keys) - 1))
        check("%s: F(t) starts increasing in gamma ((1+gamma)/2) and ends decreasing in gamma (F_12): curves cross" % model, F_start_inc and F_end_dec)
        Fb_order_ok = all(bool(np.all(curves[keys[i]][2][1:] >= curves[keys[i + 1]][2][1:] - 1e-12)) for i in range(len(keys) - 1))
        check("%s: Fbar(t) curves keep their ordering in gamma (no crossing) [proposed quantity, not plotted]" % model, Fb_order_ok)
    else:
        for tt in (0.5, 1.0, 2.0, 5.0):
            idx = int(round(tt / 5 * 500))
            print("   t=%s: E[chi] = %s  (mu = 0, 0.3, 0.6, 0.9)" % (tt, ", ".join("%.4f" % curves[m][0][idx] for m in MUS)))
            print("   t=%s: F     = %s" % (tt, ", ".join("%.4f" % curves[m][1][idx] for m in MUS)))
            print("   t=%s: Fbar  = %s" % (tt, ", ".join("%.4f" % curves[m][2][idx] for m in MUS)))
        chi_faster = all(bool(np.all(curves[MUS[i]][0] >= curves[MUS[i + 1]][0] - 1e-12)) for i in range(3))
        check("correlated: larger mu gives faster decay of E[chi(t)] (ordering holds for all t)", chi_faster)
        F_slower = all(bool(np.all(curves[MUS[i]][1][1:] >= curves[MUS[i + 1]][1][1:] - 1e-12)) for i in range(3))
        check("correlated: submitted sentence 'larger mu gives a slower early rise of F(t)' is FALSE with the renamed F_K", not F_slower)
        F_spread = max(np.abs(curves[m][1] - curves[0.0][1]).max() for m in MUS)
        check("correlated: F(t) curves differ by less than 1e-3 across mu (statement written in R4)", F_spread < 1e-3, "max spread %.1e" % F_spread)
        chi_spread = max(np.abs(curves[m][0] - curves[0.0][0]).max() for m in MUS)
        check("correlated: E[chi(t)] curves differ by at most 0.002 bit across mu (statement written in R4)", chi_spread < 2e-3, "max spread %.1e" % chi_spread)
        Fb_faster = all(bool(np.all(curves[MUS[i]][2][1:] <= curves[MUS[i + 1]][2][1:] + 1e-12)) for i in range(3))
        check("correlated: larger mu gives a FASTER early rise of Fbar(t) [proposed quantity]", Fb_faster)
        same_asym = max(abs(curves[m][1][-1] - curves[0.0][1][-1]) for m in MUS)
        print("   long-time F(5) spread across mu: %.2e; F_12 at gamma=0.5 = %.4f; F_empty = %.4f" % (
            same_asym, float(hc.F_lam_closed(al, be, 0.5)["12"]), float(hc.F_lam_closed(al, be, 0.5)["empty"])))
        same_chi = max(np.abs(curves[m][0] - curves[0.0][0]).max() for m in MUS)
        same_F = max(np.abs(curves[m][1] - curves[0.0][1]).max() for m in MUS)
        print("   max |difference| between mu-curves over t in [0,5]: E[chi] %.4f bit, F %.4f" % (same_chi, same_F))
g = 0.3
Echi, EFl, EFb, P = hc.expected_curves("burst", t, al, be, g)
c = hc.chi_K_closed(al, be, g); F = hc.F_lam_closed(al, be, g)
check("burst: E[chi(t)] = e^{-kt} chi_empty", np.abs(Echi - np.exp(-t) * float(c["empty"])).max() < 1e-12)
check("burst: F(t) = e^{-kt} F_empty + (1-e^{-kt}) F_12", np.abs(EFl - (np.exp(-t) * float(F["empty"]) + (1 - np.exp(-t)) * float(F["12"]))).max() < 1e-12)
print("-- per-class values vs gamma (|alpha|^2 = 0.6), used for the sequential-model sentence")
for g in GAMMAS + [0.4, 0.5]:
    c = hc.chi_K_closed(al, be, g); F = hc.F_lam_closed(al, be, g)
    print("   gamma=%s: chi_empty=%.4f chi_1=%.4f chi_2=%.4f | F_empty=%.4f F_1=%.4f F_2=%.4f F_12=%.4f" % (
        g, float(c["empty"]), float(c["1"]), float(c["2"]), float(F["empty"]), float(F["1"]), float(F["2"]), float(F["12"])))


print()
print("=" * 78)
print("6. Bloch-vector optimality proof of Fbar_K (round 3, decisions file Sec. B): A_K, translations,")
print("   Fbar(Lambda) = 1/2 + Tr(R A_K)/6, contraction R_ii <= 1, identity attains the bound")
print("=" * 78)
PAULIS = [hc.X, hc.Y, hc.Z]


def bloch(rho):
    return np.array([float(np.real(np.trace(P @ rho))) for P in PAULIS])


def rho_of_bloch(n):
    return 0.5 * (hc.I2 + sum(ni * P for ni, P in zip(n, PAULIS)))


def affine_of_map(phi):
    """Bloch-affine form (R, t) of a linear, trace-preserving qubit map phi: r -> R r + t."""
    t = bloch(phi(hc.I2 / 2))
    R = np.zeros((3, 3))
    for j in range(3):
        R[:, j] = bloch(phi(0.5 * PAULIS[j]))       # phi linear; traceless input P_j/2 maps to R e_j
    return R, t


def eve_effective_map(K, known, gamma):
    """Eve's post-correction effective channel for knowledge class K and known-bit value(s) `known`:
    rho -> average over the unrevealed bits of U_known E_AD(sigma_m rho sigma_m^dag) U_known^dag,
    built from the 3-qubit simulation (no closed forms), extended to mixed inputs by linearity."""
    def phi(rho):
        w, V = np.linalg.eigh(rho)
        out = np.zeros((2, 2), dtype=complex)
        for k in range(2):
            if abs(w[k]) < 1e-15:
                continue
            al, be = V[0, k], V[1, k]
            cs = hc.simulate_conditional_states(al, be, gamma)
            for (m1, m2), (p, r) in cs.items():
                if K == "1" and m1 != known:
                    continue
                if K == "2" and m2 != known:
                    continue
                if K == "12" and (m1, m2) != known:
                    continue
                U = {"empty": hc.I2, "1": np.linalg.matrix_power(hc.X, m1), "2": np.linalg.matrix_power(hc.Z, m2),
                     "12": np.linalg.matrix_power(hc.Z, m2) @ np.linalg.matrix_power(hc.X, m1)}[K]
                weight = {"empty": 1.0, "1": 2.0, "2": 2.0, "12": 4.0}[K]   # p_m = 1/4 -> conditional weights of the unrevealed bits
                out += w[k] * weight * p * (U @ r @ U.conj().T)
        return out
    return phi


def A_K_expected(K, g):
    s = np.sqrt(1 - g)
    return {"empty": np.zeros((3, 3)), "1": np.diag([0, 0, 1 - g]), "2": np.diag([s, 0, 0]),
            "12": np.diag([s, s, 1 - g])}[K]


worst_A = worst_t = 0.0
for g in (0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0):
    for K, knowns in (("empty", [None]), ("1", [0, 1]), ("2", [0, 1]), ("12", [(0, 0), (0, 1), (1, 0), (1, 1)])):
        for kn in knowns:
            R, t = affine_of_map(eve_effective_map(K, kn, g))
            worst_A = max(worst_A, np.abs(R - A_K_expected(K, g)).max())
            m1 = kn if K == "1" else (kn[0] if K == "12" else 0)
            t_exp = np.array([0, 0, (-1) ** m1 * g])            # +gamma e_z for m1 = 0, -gamma e_z for m1 = 1
            worst_t = max(worst_t, np.abs(t - t_exp).max())
check("Bloch-linear parts after correcting the known bits: A_empty = 0, A_1 = diag(0,0,1-g), A_2 = diag(sqrt(1-g),0,0), A_12 = diag(sqrt(1-g),sqrt(1-g),1-g)",
      worst_A < 1e-12, "max dev %.1e" % worst_A)
check("translation term is +gamma e_z when the known X bit is 0 and -gamma e_z when it is 1 (sign flip only; linear part unchanged)",
      worst_t < 1e-12, "max dev %.1e" % worst_t)

g = 0.4
R_ad, t_ad = affine_of_map(lambda r: hc.ad(r, g))
R_cj, t_cj = affine_of_map(lambda r: hc.X @ hc.ad(hc.X @ r @ hc.X, g) @ hc.X)
check("conjugate channel X E_AD(X . X) X: same Bloch-linear part diag(sqrt(1-g),sqrt(1-g),1-g), translation -gamma e_z instead of +gamma e_z (g=0.4)",
      np.abs(R_cj - R_ad).max() < 1e-14 and np.abs(R_ad - np.diag([np.sqrt(1 - g), np.sqrt(1 - g), 1 - g])).max() < 1e-14
      and np.abs(t_ad - [0, 0, g]).max() < 1e-14 and np.abs(t_cj - [0, 0, -g]).max() < 1e-14)
check("E_AD commutes with Z conjugation (Z-covariance): the known Z bit leaves the channel unchanged (g=0.4)",
      max(np.abs(hc.ad(hc.Z @ r @ hc.Z, g) - hc.Z @ hc.ad(r, g) @ hc.Z).max()
          for r in (rho_of_bloch([0.3, -0.5, 0.2]), rho_of_bloch([0.9, 0.1, -0.3]))) < 1e-14)
check("Fbar_K = 1/2 + Tr(A_K)/6 reproduces the four closed forms for all K on a gamma grid",
      max(abs(0.5 + np.trace(A_K_expected(K, gg)) / 6 - float(hc.Fbar_closed(gg)[K]))
          for gg in np.linspace(0, 1, 11) for K in ("empty", "1", "2", "12")) < 1e-14)


def random_cptp(rng, rank):
    """Random CPTP qubit map: Kraus operators are the 2x2 blocks of a Haar-random isometry C^2 -> C^2 (x) C^rank."""
    G = rng.normal(size=(2 * rank, 2)) + 1j * rng.normal(size=(2 * rank, 2))
    Q, _ = np.linalg.qr(G)
    Ks = [Q[2 * j:2 * j + 2, :] for j in range(rank)]
    return lambda r: sum(Kk @ r @ Kk.conj().T for Kk in Ks)


rng = np.random.default_rng(2026)
worst_formula = 0.0
worst_Rii = -1.0
worst_excess = -1.0
n_maps = 0
for g in (0.0, 0.2, 0.5, 0.8):
    for K, knowns in (("empty", [None]), ("1", [0, 1]), ("2", [0, 1]), ("12", [(0, 0), (1, 1)])):
        for kn in knowns:
            phi = eve_effective_map(K, kn, g)
            for rank in (1, 2, 3, 4):
                for _ in range(5):
                    Lam = random_cptp(rng, rank)
                    R, tL = affine_of_map(Lam)
                    worst_Rii = max(worst_Rii, np.max(np.diag(R)))
                    Fh = 0.0                      # exact Haar average via the 6-state 2-design
                    for (a, b) in hc.STABILIZER_STATES:
                        psi = hc.psi_vec(a, b)
                        out = Lam(phi(np.outer(psi, psi.conj())))
                        Fh += float(np.real(psi.conj() @ out @ psi)) / len(hc.STABILIZER_STATES)
                    pred = 0.5 + np.trace(R @ A_K_expected(K, g)) / 6
                    worst_formula = max(worst_formula, abs(Fh - pred))
                    worst_excess = max(worst_excess, Fh - float(hc.Fbar_closed(g)[K]))
                    n_maps += 1
check("Haar-average fidelity of an arbitrary CPTP recovery applied after Eve's correction equals 1/2 + Tr(R A_K)/6 (translation terms drop out), %d random maps" % n_maps,
      worst_formula < 1e-12, "max dev %.1e" % worst_formula)
check("Bloch-linear part of every random CPTP map satisfies R_ii <= 1", worst_Rii <= 1 + 1e-12, "max R_ii = %.6f" % worst_Rii)
check("no random CPTP recovery exceeds Fbar_K = 1/2 + Tr(A_K)/6; the identity attains it", worst_excess <= 1e-12, "max excess %.1e" % worst_excess)
n_ok = True
for _ in range(200):
    Lam = random_cptp(rng, int(rng.integers(1, 5)))
    R, tL = affine_of_map(Lam)
    for _ in range(20):
        n = rng.normal(size=3)
        n /= np.linalg.norm(n)
        if np.linalg.norm(R @ n) > 1 + 1e-12 or np.linalg.norm(R @ n + tL) > 1 + 1e-12:
            n_ok = False
check("|R n + t| <= 1 and |R n| <= 1 on the Bloch sphere for 200 random CPTP maps (contraction argument behind R_ii <= 1)", n_ok)
for K, knowns in (("1", [0, 1]), ("2", [0, 1]), ("12", [(0, 0), (0, 1), (1, 0), (1, 1)])):
    vals = []
    for kn in knowns:
        R, t = affine_of_map(eve_effective_map(K, kn, 0.3))
        vals.append(0.5 + np.trace(R) / 6)
    check("K={%s}, g=0.3: identity recovery gives 1/2 + Tr(A_K)/6 for every value of the known bits, so the average over them is the same" % K,
          max(abs(v - float(hc.Fbar_closed(0.3)[K])) for v in vals) < 1e-12)
print("   Fbar_K = 1/2 + Tr(A_K)/6 at gamma = 0.1 / 0.3 / 0.5:",
      {K: [round(float(hc.Fbar_closed(gg)[K]), 4) for gg in (0.1, 0.3, 0.5)] for K in ("empty", "1", "2", "12")})

print()
print("=" * 78)
print("SUMMARY:", "ALL CHECKS PASSED" if not fails else "%d FAILED: %s" % (len(fails), fails))
print("=" * 78)
