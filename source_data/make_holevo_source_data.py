#!/usr/bin/env python3
"""Source Data for Figs. 6 and 7 of "Quantum-Resistant Quantum Teleportation".

PROVENANCE NOTE. The code that drew these six panels belongs to the co-author who carried
out the information-theoretic analysis and is not in this repository. What this script does
instead is evaluate the closed-form expressions the paper itself states, at the parameters
printed on each panel. It is therefore an independent recomputation, not the original code.

Its agreement with the published panels is checked by --verify, which compares against
values read directly off the figures (curve start points, long-time limits and the
sequential-model crossing). Replace these CSVs with the co-author's own numbers when they
become available.

Closed forms (Results 3 and 4, Supplementary Notes 9-11):
    a = |alpha|^2 + gamma |beta|^2      b = (1-gamma)|beta|^2      c = alpha beta* sqrt(1-gamma)
    r = Re(c)    D = ab - |c|^2    delta = sqrt(1 - 4D)
    h(x) = -((1+x)/2) log2((1+x)/2) - ((1-x)/2) log2((1-x)/2)

    chi_none = 1 - h(delta)           F_none = 1/2
    chi_1    = h(|1-2a|) - h(delta)   F_1    = (1 + |1-2a|)/2
    chi_2    = h(2|r|)   - h(delta)   F_2    = 1/2 + |r|
    chi_12   = 0                      F_12   = (1 + delta)/2

    E[chi(t)] = sum_K P_K(t) chi_K          F(t) = sum_K P_K(t) F_K

Figure 6 uses the reduced form chi(gamma,|alpha|^2) = 1 - h(sqrt(1 - 4 gamma(1-gamma)(1-|alpha|^2)^2)).

Usage:  python make_holevo_source_data.py [--outdir DIR] [--verify]
"""
import argparse
import csv
import os
import numpy as np

ALPHA2, BETA2 = 0.6, 0.4          # the input state alpha = sqrt(0.6), beta = sqrt(0.4)
T = np.linspace(0.0, 5.0, 501)    # the time axis of every Fig. 7 panel
GAMMAS_7 = [0.0, 0.1, 0.2, 0.3]   # legend of panels (a), (b), (c)
MUS = [0.0, 0.3, 0.6, 0.9]        # legend of panel (d)
GAMMA_D, K = 0.5, 1.0             # panel (d) holds gamma fixed
ALPHA2_6A = [0.10, 0.20, 0.30, 0.40, 0.50]   # legend of Fig. 6a
GAMMAS_6B = [0.1, 0.2, 0.3, 0.4, 0.5]        # legend of Fig. 6b


def h(x):
    x = np.clip(np.asarray(x, dtype=float), 0.0, 1.0)
    p, q = (1 + x) / 2, (1 - x) / 2
    with np.errstate(divide="ignore", invalid="ignore"):
        t1 = np.where(p > 0, p * np.log2(p), 0.0)
        t2 = np.where(q > 0, q * np.log2(q), 0.0)
    return -(t1 + t2)


def per_class(gamma, alpha2=ALPHA2, beta2=BETA2):
    """chi_K and F_K for K = none, {1}, {2}, {1,2}."""
    a = alpha2 + gamma * beta2
    b = (1 - gamma) * beta2
    c = np.sqrt(alpha2 * beta2 * (1 - gamma))     # alpha, beta real and positive here
    r = c
    delta = np.sqrt(max(0.0, 1 - 4 * (a * b - c ** 2)))
    hd = h(delta)
    chi = {"none": 1 - hd, "1": h(abs(1 - 2 * a)) - hd, "2": h(2 * abs(r)) - hd, "12": 0.0}
    F = {"none": 0.5, "1": (1 + abs(1 - 2 * a)) / 2, "2": 0.5 + abs(r), "12": (1 + delta) / 2}
    return chi, F


def probs(model, t, k1=1.0, k2=1.0, k=K, mu=0.0):
    """Knowledge-class probabilities P_K(t)."""
    if model == "independent":
        return {"none": np.exp(-(k1 + k2) * t),
                "1": (1 - np.exp(-k1 * t)) * np.exp(-k2 * t),
                "2": np.exp(-k1 * t) * (1 - np.exp(-k2 * t)),
                "12": (1 - np.exp(-k1 * t)) * (1 - np.exp(-k2 * t))}
    if model == "sequential":                      # k1 == k2 == k here
        p0 = np.exp(-k * t)
        p1 = k * t * np.exp(-k * t)
        return {"none": p0, "1": p1, "2": np.zeros_like(t), "12": 1 - p0 - p1}
    if model == "burst":
        p0 = np.exp(-k * t)
        return {"none": p0, "1": np.zeros_like(t), "2": np.zeros_like(t), "12": 1 - p0}
    if model == "correlated":
        p0 = np.exp(-(2 - mu) * k * t)
        p1 = np.exp(-mu * k * t) * (1 - np.exp(-(1 - mu) * k * t)) * np.exp(-(1 - mu) * k * t)
        p2 = p1
        return {"none": p0, "1": p1, "2": p2, "12": 1 - p0 - p1 - p2}
    raise ValueError(model)


def curves(model, gamma, **kw):
    chi, F = per_class(gamma)
    P = probs(model, T, **kw)
    return (sum(P[k] * chi[k] for k in P), sum(P[k] * F[k] for k in P))


def write(path, header, rows, notes):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        for n in notes:
            fh.write("# %s\n" % n)
        w = csv.writer(fh)
        w.writerow(header); w.writerows(rows)
    print("wrote %-40s %5d rows" % (os.path.basename(path), len(rows)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    NOTE = ["Recomputed from the closed forms in the paper, not from the co-author's code.",
            "Input state alpha = sqrt(0.6), beta = sqrt(0.4)."]

    # ---- Fig. 6 -------------------------------------------------------------------
    g = np.linspace(0.0, 1.0, 501)
    rows = [["%.4f" % gi, "%.2f" % a2, "%.10f" % (1 - h(np.sqrt(1 - 4 * gi * (1 - gi) * (1 - a2) ** 2)))]
            for a2 in ALPHA2_6A for gi in g]
    write(os.path.join(args.outdir, "SourceData_Fig6a.csv"),
          ["gamma", "alpha_sq", "chi_bits"], rows,
          ["Source Data for Fig. 6a: Holevo quantity vs damping parameter"] + NOTE[:1])
    a2 = np.linspace(0.0, 1.0, 501)
    rows = [["%.4f" % x, "%.2f" % gi, "%.10f" % (1 - h(np.sqrt(1 - 4 * gi * (1 - gi) * (1 - x) ** 2)))]
            for gi in GAMMAS_6B for x in a2]
    write(os.path.join(args.outdir, "SourceData_Fig6b.csv"),
          ["alpha_sq", "gamma", "chi_bits"], rows,
          ["Source Data for Fig. 6b: Holevo quantity vs input-state amplitude"] + NOTE[:1])

    # ---- Fig. 7 -------------------------------------------------------------------
    for panel, model, extra in (("7a", "independent", {}), ("7b", "sequential", {}), ("7c", "burst", {})):
        rows = []
        for gi in GAMMAS_7:
            ch, fi = curves(model, gi, **extra)
            rows += [["%.3f" % ti, "%.1f" % gi, "%.10f" % c, "%.10f" % f] for ti, c, f in zip(T, ch, fi)]
        write(os.path.join(args.outdir, "SourceData_Fig%s.csv" % panel),
              ["time", "gamma", "expected_holevo_bits", "eve_fidelity"], rows,
              ["Source Data for Fig. %s: %s leakage model, k1 = k2 = k = 1" % (panel, model)] + NOTE)
    rows = []
    for mu in MUS:
        ch, fi = curves("correlated", GAMMA_D, mu=mu)
        rows += [["%.3f" % ti, "%.1f" % mu, "%.10f" % c, "%.10f" % f] for ti, c, f in zip(T, ch, fi)]
    write(os.path.join(args.outdir, "SourceData_Fig7d.csv"),
          ["time", "mu", "expected_holevo_bits", "eve_fidelity"], rows,
          ["Source Data for Fig. 7d: correlated leakage model, gamma = 0.5, k = 1"] + NOTE)

    # ---- check against values read off the published panels ------------------------
    if args.verify:
        print("\n%-46s %10s %10s %8s" % ("check (read off the figure)", "figure", "computed", "diff"))
        checks = []
        for gi, want in zip(GAMMAS_7, [1.00, 0.89, 0.82, 0.78]):
            checks.append(("Fig. 7a  E[chi(0)]  gamma=%.1f" % gi, want, curves("independent", gi)[0][0]))
        for gi, want in zip(GAMMAS_7, [0.997, 0.982, 0.965, 0.958]):
            checks.append(("Fig. 7a  F(5)       gamma=%.1f" % gi, want, curves("independent", gi)[1][-1]))
        checks.append(("Fig. 7d  E[chi(0)]  gamma=0.5", 0.745, curves("correlated", GAMMA_D, mu=0.0)[0][0]))
        checks.append(("Fig. 7d  F(5)       mu=0.0", 0.955, curves("correlated", GAMMA_D, mu=0.0)[1][-1]))
        checks.append(("Fig. 7*  F(0)       any", 0.500, curves("burst", 0.2)[1][0]))
        checks.append(("Fig. 6a  chi at gamma=0", 1.000, 1 - h(np.sqrt(1 - 0))))
        ok = True
        for label, want, got in checks:
            d = abs(want - got); ok &= d < 0.006
            print("%-46s %10.3f %10.4f %8.4f%s" % (label, want, got, d, "" if d < 0.006 else "  <-- MISMATCH"))
        print("\nall checks within reading precision of the figures:", ok)


if __name__ == "__main__":
    main()
