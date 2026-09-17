#!/usr/bin/env python3
"""Figure 5 of "Quantum-Resistant Quantum Teleportation": the joint classical--quantum
attack probability P_joint(t) and its two factors.

PROVENANCE NOTE. This script is a post-hoc reimplementation, not the original code. The
script that produced the submitted Figure/P_joint.pdf (created 2026-06-11) did not survive
in either of the project's code folders; a 2026-09-17 provenance audit re-ran every
candidate and none reproduced it. The figure is nevertheless fully determined by the
equation and the parameters printed in its own caption, which is what this file evaluates.
Running it reproduces the two values annotated on the published figure, t* = 16.4 s and
P_joint(t*) = 0.645, which is the check that justifies using it for Source Data.

Do not confuse the submitted figure with code_from_D/PQNet/claude_figure2/P_joint.pdf:
that file has the same name but is the output of a superseded script (m = 80, T_coh = 1 s,
log2 axis, P_SWAP = e^{-t/T_coh}) merely renamed.

Equations (main text, "A bounded joint classical--quantum attack window" and Methods):
    lambda      = ||b1|| sqrt(pi) / (2 s)
    gamma(t)    = 2 a / (log2 t + b)
    P_LWE(t)    = prod_{i=1..m} erf( d_i lambda 2^{-gamma(t) (i-1)} )
    P_SWAP(t)   = (1/2) ( 1 + e^{-t / T_coh} )
    P_joint(t)  = P_LWE(t) * P_SWAP(t)

Usage:  python plot_fig5_joint_probability.py [--outdir DIR] [--csv]
"""
import argparse
import os
import numpy as np
from scipy.special import erf

# --- parameters, exactly as printed in the Fig. 5 caption -------------------------
M = 30            # number of Gram-Schmidt layers in the product
S = 2.0           # standard deviation of the Gaussian LWE error
A = 0.3           # BKZ runtime fit coefficient a
B = 2.7           # BKZ runtime fit coefficient b
B1_NORM = 10.0    # ||b~_1||, length of the first Gram-Schmidt vector
D_I = 2.0         # integer search radius of every Nearest-Planes layer
T_COH = 20.0      # adversary's quantum memory coherence time, seconds

# gamma(t) diverges at t = 2^-b ~ 0.154 s, so the model is only evaluated for t >= 1 s.
# The upper limit matches the published figure's axis, which runs to 140 s.
T_MIN, T_MAX, N_T = 1.0, 140.0, 2781


def p_lwe(t, m=M, s=S, a=A, b=B, b1_norm=B1_NORM, d_i=D_I):
    """Probability that BKZ reduction plus Nearest-Planes decoding recovers the secret."""
    t = np.atleast_1d(np.asarray(t, dtype=float))
    lam = b1_norm * np.sqrt(np.pi) / (2.0 * s)
    gamma = 2.0 * a / (np.log2(t) + b)                      # shape (T,)
    i = np.arange(1, m + 1)                                 # shape (m,)
    z = d_i * lam * 2.0 ** (-np.outer(gamma, i - 1))        # shape (T, m)
    return np.prod(erf(z), axis=1)


def p_swap(t, t_coh=T_COH):
    """Fidelity-equivalent success probability of the SWAP attack; -> 1/2, not 0."""
    return 0.5 * (1.0 + np.exp(-np.asarray(t, dtype=float) / t_coh))


def p_joint(t):
    return p_lwe(t) * p_swap(t)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default="output")
    ap.add_argument("--csv", action="store_true", help="also write the Source Data CSV")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    t = np.linspace(T_MIN, T_MAX, N_T)
    lwe, swap, joint = p_lwe(t), p_swap(t), p_joint(t)
    k = int(np.argmax(joint))
    print("t*            = %.2f s" % t[k])
    print("P_joint(t*)   = %.4f" % joint[k])
    print("P_LWE(t*)     = %.4f" % lwe[k])
    print("P_SWAP(t*)    = %.4f" % swap[k])

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "serif", "font.size": 10, "axes.linewidth": 0.8})
    fig, ax = plt.subplots(figsize=(5.0, 3.4))
    ax.plot(t, lwe, color="tab:green", lw=1.6, label=r"$P_{\mathrm{LWE}}$")
    ax.plot(t, swap, color="tab:red", lw=1.6, ls="--", label=r"$P_{\mathrm{SWAP}}$")
    ax.plot(t, joint, color="tab:blue", lw=1.8, ls="-.", label=r"$P_{\mathrm{joint}}$")
    ax.axvline(t[k], color="0.5", lw=0.8, ls=":")
    ax.annotate(r"$t^{*}=%.0f$ s, $P_{\mathrm{joint}}=%.3f$" % (t[k], joint[k]),
                xy=(t[k], joint[k]), xytext=(t[k] + 4, joint[k] - 0.12), fontsize=8,
                arrowprops=dict(arrowstyle="->", lw=0.7, color="0.4"))
    ax.set_xlabel("Time $t$ (s)")
    ax.set_ylabel("Probability")
    ax.set_xlim(T_MIN, T_MAX)
    ax.set_ylim(0, 1.02)
    ax.legend(frameon=False, loc="lower right")
    ax.grid(alpha=0.25, lw=0.5)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(args.outdir, "P_joint." + ext), dpi=300)
    print("wrote", os.path.join(args.outdir, "P_joint.pdf"))

    if args.csv:
        path = os.path.join(args.outdir, "SourceData_Fig5.csv")
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write("# Source Data for Fig. 5, Quantum-Resistant Quantum Teleportation\n")
            fh.write("# P_LWE, P_SWAP and P_joint vs storage time t, for the caption parameters\n")
            fh.write("# m=%d, s=%g, a=%g, b=%g, ||b1||=%g, d_i=%g, T_coh=%g s\n"
                     % (M, S, A, B, B1_NORM, D_I, T_COH))
            fh.write("time_s,P_LWE,P_SWAP,P_joint\n")
            for ti, l, w, j in zip(t, lwe, swap, joint):
                fh.write("%.6f,%.10f,%.10f,%.10f\n" % (ti, l, w, j))
        print("wrote", path)


if __name__ == "__main__":
    main()
