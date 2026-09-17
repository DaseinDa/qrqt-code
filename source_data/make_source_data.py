#!/usr/bin/env python3
"""Write the Source Data files for "Quantum-Resistant Quantum Teleportation".

Nature Communications asks for the numerical values behind every data figure. This script
regenerates them from the same code that draws the figures, so the CSVs cannot drift from
the plots.

  SourceData_Fig3a.csv              memory lifetime vs distance, 0-100 m, six PQC schemes
  SourceData_Fig3b.csv              the same over 0-500 m, plus the four coherence
                                    benchmarks, their shaded bands and the margin annotation
  SourceData_Fig5.csv               P_LWE, P_SWAP and P_joint vs storage time
  SourceData_SupplementaryFig1.csv  exact and Pade log2 P_LWE vs lattice dimension m
  SourceData_SupplementaryFig2.csv  the same vs log2 T_BKZ

Figs. 1 and 4 are TikZ schematics and Fig. 2 is vector artwork, so none of them plots data.
Figs. 6 and 7 and the Supplementary Holevo figures are the collaborator's; their values
have to come from that author.

Usage:  python make_source_data.py [--outdir DIR]
"""
import argparse
import csv
import math
import os
import sys

import numpy as np
from scipy.special import erf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "figures", "fig3"))
sys.path.insert(0, os.path.join(HERE, "..", "figures", "fig5"))

from fig3_common import PQC_DATA, PLOT_ORDER                      # noqa: E402
from plot_fig5_joint_probability import (                          # noqa: E402
    p_lwe, p_swap, M, S, A, B, B1_NORM, D_I, T_COH, T_MIN, T_MAX, N_T)

NIST_LEVEL = {"Kyber512": 1, "Kyber768": 3, "Kyber1024": 5,
              "FrodoKEM-640": 1, "FrodoKEM-976": 3, "FrodoKEM-1344": 5}
PLATFORMS = [  # exactly as in figures/fig3/pqc_plot_fig3b.py
    {"name": "Trapped ions", "T2": "1 h",    "y": 3.6e12},
    {"name": "NV center",    "T2": "1 s",    "y": 1e9},
    {"name": "SC cavity",    "T2": "34 ms",  "y": 3.4e7},
    {"name": "Fluxonium",    "T2": "1.4 ms", "y": 1.4e6},
]


def _w(path, header, rows, notes=()):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        for n in notes:
            fh.write("# %s\n" % n)
        wr = csv.writer(fh)
        wr.writerow(header)
        wr.writerows(rows)
    print("wrote %-36s %5d rows" % (os.path.basename(path), len(rows)))


def fig3(outdir, panel, dmax, npts=50):
    d = np.linspace(0, dmax, npts)
    rows = []
    for name in PLOT_ORDER:
        icpt, slope = PQC_DATA[name]
        for di, yi in zip(d, icpt + slope * d):
            rows.append([panel, name, NIST_LEVEL[name], "%.4f" % di, "%.4f" % yi])
    _w(os.path.join(outdir, "SourceData_Fig%s.csv" % panel),
       ["panel", "scheme", "nist_level", "distance_m", "memory_lifetime_ns"], rows,
       ["Source Data for Fig. %s, Quantum-Resistant Quantum Teleportation" % panel,
        "memory_lifetime_ns = PQC processing latency + 5 ns/m fibre propagation",
        "PQC latencies are those of Table 1 of the main text"])
    return d


def fig3b_benchmarks(outdir, d):
    rows = [[p["name"], p["T2"], "%.6g" % p["y"], "%.6g" % (p["y"] / 3), "%.6g" % (p["y"] * 3)]
            for p in PLATFORMS]
    max_pqc = max(PQC_DATA[n][0] + PQC_DATA[n][1] * d[-1] for n in PLOT_ORDER)
    min_coh = min(p["y"] for p in PLATFORMS)
    _w(os.path.join(outdir, "SourceData_Fig3b_coherence_benchmarks.csv"),
       ["platform", "reported_T2", "coherence_ns", "band_lower_ns", "band_upper_ns"], rows,
       ["Source Data for the top panel of Fig. 3b: reported coherence times and the",
        "factor-of-three shaded bands drawn around each of them.",
        "Margin annotation: min coherence %.6g ns / max PQC requirement at %g m %.6g ns"
        " = %.2f, printed as '>%d x margin'"
        % (min_coh, d[-1], max_pqc, min_coh / max_pqc, math.floor(min_coh / max_pqc))])


def fig5(outdir):
    t = np.linspace(T_MIN, T_MAX, N_T)
    lwe, swap = p_lwe(t), p_swap(t)
    rows = [["%.6f" % ti, "%.10f" % l, "%.10f" % w, "%.10f" % (l * w)]
            for ti, l, w in zip(t, lwe, swap)]
    k = int(np.argmax(lwe * swap))
    _w(os.path.join(outdir, "SourceData_Fig5.csv"),
       ["time_s", "P_LWE", "P_SWAP", "P_joint"], rows,
       ["Source Data for Fig. 5, Quantum-Resistant Quantum Teleportation",
        "m=%d, s=%g, a=%g, b=%g, ||b1||=%g, d_i=%g, T_coh=%g s" % (M, S, A, B, B1_NORM, D_I, T_COH),
        "maximum at t* = %.2f s with P_joint = %.4f (printed on the figure as 16 s and 0.645)"
        % (t[k], (lwe * swap)[k])])


# --- the two supplementary panels, same formulas as figures/supplementary --------------
def _log2_exact(m, a, b, T, s, b1, di):
    g = 2 * a / (np.log2(T) + b)
    lam = b1 * np.sqrt(np.pi) / (2 * s)
    i = np.arange(1, m + 1)
    return float(np.sum(np.log2(erf(di * lam * 2.0 ** (-g * (i - 1))))))


def _log2_pade(m, a, b, T, s, b1, di, pa=0.140012):
    g = 2 * a / (np.log2(T) + b)
    lam = b1 * np.sqrt(np.pi) / (2 * s)
    i = np.arange(1, m + 1)
    W = (di ** 2) * (lam ** 2) * 2.0 ** (-2 * g * (i - 1))
    with np.errstate(divide="ignore", invalid="ignore"):
        return float(np.sum(np.log2(np.sqrt(1 - np.exp(-(W * (4 / np.pi + pa * W)) / (1 + pa * W))))))


def si_figs(outdir):
    rows = [["%d" % m, "%.10f" % _log2_exact(m, 0.3, 2.7, 2 ** 30, 2, 10, 2),
             "%.10f" % _log2_pade(m, 0.3, 2.7, 2 ** 30, 2, 10, 2)]
            for m in range(5, 61)]
    _w(os.path.join(outdir, "SourceData_SupplementaryFig1.csv"),
       ["m", "log2_P_LWE_exact", "log2_P_LWE_pade"], rows,
       ["Source Data for Supplementary Fig. 1",
        "a=0.3, b=2.7, T_BKZ=2^30 s, ||b1||=10, d_i=2, s=2"])
    rows = [["%d" % e, "%.10f" % _log2_exact(500, 1.8, 2.7, 2.0 ** e, 2, 10, 2),
             "%.10f" % _log2_pade(500, 1.8, 2.7, 2.0 ** e, 2, 10, 2)]
            for e in range(20, 100, 2)]
    _w(os.path.join(outdir, "SourceData_SupplementaryFig2.csv"),
       ["log2_T_BKZ", "log2_P_LWE_exact", "log2_P_LWE_pade"], rows,
       ["Source Data for Supplementary Fig. 2",
        "a=1.8, b=2.7, m=500, ||b1||=10, d_i=2, s=2"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=HERE)
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    fig3(args.outdir, "3a", 100)
    d = fig3(args.outdir, "3b", 500)
    fig3b_benchmarks(args.outdir, d)
    fig5(args.outdir)
    si_figs(args.outdir)


if __name__ == "__main__":
    main()
