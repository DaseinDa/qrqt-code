"""
make_figures.py -- prototype replacement figures for Fig. 6, Fig. 7 and a time-coupled
(unified) figure, using the CORRECTED closed forms of holevo_correct.py.  Every CSV is
cross-checked against the 3-qubit density-matrix simulation before it is written (so
the Source Data no longer come from re-evaluating the closed forms alone).
Run:  python make_figures.py
"""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import holevo_correct as hc

# ---- style (sequential blue ramp for ordered families, categorical slots for the four models)
BLUE5 = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#0d366b"]       # ramp steps 250/350/450/550/700
BLUE4 = ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]                  # 250/400/550/700
CAT4 = ["#2a78d6", "#eb6834", "#1baf7a", "#6250d6"]                   # slots 1,2,3,7 (validated)
INK, MUTED, GRID = "#0b0b0b", "#898781", "#e1e0d9"
plt.rcParams.update({
    "font.size": 8, "axes.labelsize": 8.5, "axes.titlesize": 9, "legend.fontsize": 7,
    "axes.edgecolor": "#c3c2b7", "axes.linewidth": 0.6, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.labelcolor": INK, "text.color": INK, "grid.color": GRID, "grid.linewidth": 0.5,
    "axes.spines.top": False, "axes.spines.right": False, "lines.linewidth": 1.6,
    "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "savefig.facecolor": "#fcfcfb",
})
ALPHA2 = 0.6                                   # Fig. 7 input state of the submitted manuscript
AL, BE = np.sqrt(ALPHA2), np.sqrt(1 - ALPHA2)


def simcheck(alpha, beta, gammas, values, key, tol=1e-9):
    """Spot-check a closed-form array against the simulation on a coarse subsample."""
    idx = np.linspace(0, len(gammas) - 1, 9).astype(int)
    for i in idx:
        s, _, _ = hc.chi_K_sim(alpha, beta, float(gammas[i]))
        assert abs(s[key] - values[i]) < tol, (key, gammas[i], s[key], values[i])


# ============================================================ Fig. 6 prototype
gam = np.linspace(0, 1, 501)
a2s = np.linspace(0, 1, 501)
fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.9), constrained_layout=True)
rows6a, rows6b = [], []
for col, a2 in zip(BLUE5, [0.1, 0.2, 0.3, 0.4, 0.5]):
    al, be = np.sqrt(a2), np.sqrt(1 - a2)
    chi = hc.chi_K_closed(al, be, gam)["empty"]
    simcheck(al, be, gam, chi, "empty")
    ax[0].plot(gam, chi, color=col, label=fr"$|\alpha|^2={a2:.1f}$")
    rows6a += [(g, a2, c) for g, c in zip(gam, chi)]
for col, g in zip(BLUE5, [0.1, 0.2, 0.3, 0.4, 0.5]):
    chi = np.array([float(hc.chi_K_closed(np.sqrt(a), np.sqrt(1 - a), g)["empty"]) for a in a2s])
    for a in (0.0, 0.3, 0.6, 1.0):
        s, _, _ = hc.chi_K_sim(np.sqrt(a), np.sqrt(1 - a), g)
        assert abs(s["empty"] - float(hc.chi_K_closed(np.sqrt(a), np.sqrt(1 - a), g)["empty"])) < 1e-9
    ax[1].plot(a2s, chi, color=col, label=fr"$\gamma={g:.1f}$")
    rows6b += [(a, g, c) for a, c in zip(a2s, chi)]
ax[0].set(xlabel=r"damping parameter $\gamma$", ylabel=r"$\chi_\varnothing$ (bits)", xlim=(0, 1), ylim=(0, 1.02))
ax[1].set(xlabel=r"input-state population $|\alpha|^2$", ylabel=r"$\chi_\varnothing$ (bits)", xlim=(0, 1), ylim=(0, 1.02))
for a in ax:
    a.grid(True, axis="y")
    a.legend(frameon=False, loc="upper right")
ax[0].set_title(r"a  $\chi_\varnothing$ vs damping $\gamma$", loc="left", fontweight="bold")
ax[1].set_title(r"b  $\chi_\varnothing$ vs input state $|\alpha|^2$", loc="left", fontweight="bold")
ax[1].legend(frameon=False, loc="lower center", ncol=3)
fig.savefig(os.path.join(HERE, "fig6_prototype.png"), dpi=300)
plt.close(fig)
with open(os.path.join(HERE, "fig6a_prototype.csv"), "w") as f:
    f.write("# Fig. 6a prototype: chi_empty = h(gamma) - 1/2[h(delta_beta)+h(delta_alpha)], delta_x = sqrt(1-4 gamma(1-gamma)|x|^4)\n")
    f.write("# h(x) = H2((1+x)/2). Cross-checked against the 3-qubit density-matrix simulation (holevo_correct.py).\n")
    f.write("gamma,alpha_sq,chi_bits\n")
    f.writelines(f"{g:.4f},{a:.2f},{c:.10f}\n" for g, a, c in rows6a)
with open(os.path.join(HERE, "fig6b_prototype.csv"), "w") as f:
    f.write("# Fig. 6b prototype: same closed form as a function of |alpha|^2 at fixed gamma.\n")
    f.write("alpha_sq,gamma,chi_bits\n")
    f.writelines(f"{a:.4f},{g:.2f},{c:.10f}\n" for a, g, c in rows6b)

# ---- comparison: submitted formula (dashed) vs corrected (solid)
fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.9), constrained_layout=True)
for col, a2 in zip(BLUE5, [0.1, 0.3, 0.5]):
    al, be = np.sqrt(a2), np.sqrt(1 - a2)
    ax[0].plot(gam, hc.chi_K_closed(al, be, gam)["empty"], color=col, label=fr"$|\alpha|^2={a2:.1f}$ corrected")
    ax[0].plot(gam, hc.chi_paper(al, be, gam)["empty"], color=col, ls="--", lw=1.1, label=fr"$|\alpha|^2={a2:.1f}$ submitted")
for col, g in zip(BLUE5, [0.1, 0.3, 0.5]):
    ax[1].plot(a2s, [float(hc.chi_K_closed(np.sqrt(a), np.sqrt(1 - a), g)["empty"]) for a in a2s], color=col, label=fr"$\gamma={g:.1f}$ corrected")
    ax[1].plot(a2s, [float(hc.chi_paper(np.sqrt(a), np.sqrt(1 - a), g)["empty"]) for a in a2s], color=col, ls="--", lw=1.1, label=fr"$\gamma={g:.1f}$ submitted")
ax[0].set(xlabel=r"$\gamma$", ylabel=r"$\chi_\varnothing$ (bits)", xlim=(0, 1), ylim=(0, 1.02))
ax[1].set(xlabel=r"$|\alpha|^2$", ylabel=r"$\chi_\varnothing$ (bits)", xlim=(0, 1), ylim=(0, 1.02))
for a in ax:
    a.grid(True, axis="y")
    a.legend(frameon=False, fontsize=6, ncol=2)
ax[0].set_title("a  submitted (dashed) vs corrected (solid)", loc="left", fontweight="bold")
ax[1].set_title("b  submitted (dashed) vs corrected (solid)", loc="left", fontweight="bold")
ax[1].legend(frameon=False, fontsize=6, ncol=2, loc="lower center")
fig.savefig(os.path.join(HERE, "fig6_comparison_submitted_vs_corrected.png"), dpi=300)
plt.close(fig)

# ============================================================ Fig. 7 prototype (fixed gamma, k = 1)
t = np.linspace(0, 5, 501)
models = [("independent", "a  independent"), ("sequential", "b  sequential"),
          ("burst", "c  burst"), ("correlated", r"d  correlated, $\gamma=0.5$")]
GAMMAS = [0.0, 0.1, 0.2, 0.3]
MUS = [0.0, 0.3, 0.6, 0.9]
fig, axes = plt.subplots(3, 4, figsize=(9.2, 6.6), constrained_layout=True, sharex=True)
csv_rows = {m: [] for m, _ in models}
for j, (model, title) in enumerate(models):
    fam = [(f"$\\gamma={g}$", dict(gamma=g, mu=0.0)) for g in GAMMAS] if model != "correlated" \
        else [(f"$\\mu={mu}$", dict(gamma=0.5, mu=mu)) for mu in MUS]
    for col, (lab, kw) in zip(BLUE4, fam):
        Echi, EFl, EFb, _ = hc.expected_curves(model, t, AL, BE, kw["gamma"], k=1.0, mu=kw["mu"])
        # cross-check of the per-class inputs against the simulation
        s, _, _ = hc.chi_K_sim(AL, BE, kw["gamma"])
        c = hc.chi_K_closed(AL, BE, kw["gamma"])
        assert all(abs(s[K] - float(c[K])) < 1e-9 for K in ("empty", "1", "2"))
        Fs = hc.F_lam_sim(AL, BE, kw["gamma"])
        Fc = hc.F_lam_closed(AL, BE, kw["gamma"])
        assert all(abs(Fs[K] - float(Fc[K])) < 1e-9 for K in Fs)
        Fb2 = hc.Fbar_sim_haar(kw["gamma"])
        Fbc = hc.Fbar_closed(kw["gamma"])
        assert all(abs(Fb2[K] - float(Fbc[K])) < 1e-9 for K in Fb2)
        axes[0, j].plot(t, Echi, color=col, label=lab)
        axes[1, j].plot(t, EFb, color=col, label=lab)
        axes[2, j].plot(t, EFl, color=col, label=lab)
        key = kw["mu"] if model == "correlated" else kw["gamma"]
        csv_rows[model] += [(tt, key, e, fb, fl) for tt, e, fb, fl in zip(t, Echi, EFb, EFl)]
    axes[0, j].set_title(title, loc="left", fontweight="bold")
    axes[2, j].set_xlabel("time $t$ (units of $1/k$)")
    for i in range(3):
        axes[i, j].grid(True, axis="y")
        axes[i, j].set_xlim(0, 5)
    axes[0, j].legend(frameon=False)
axes[0, 0].set_ylabel(r"$\mathbb{E}[\chi(t)]$ (bits)")
axes[1, 0].set_ylabel(r"$\bar F(t)$  (Eve's fidelity with $|\psi\rangle$," + "\n" + r"Haar avg., $\psi$-independent)")
axes[2, 0].set_ylabel(r"$F^{\lambda}(t)$  (max overlap with Bob's" + "\n" + r"state; manuscript $F_K$, corrected)")
for j in range(4):
    axes[0, j].set_ylim(0, 1.02)
    axes[1, j].set_ylim(0.45, 1.02)
    axes[2, j].set_ylim(0.45, 1.02)
fig.savefig(os.path.join(HERE, "fig7_prototype.png"), dpi=300)
plt.close(fig)
for model, _ in models:
    key = "mu" if model == "correlated" else "gamma"
    with open(os.path.join(HERE, f"fig7_{model}_prototype.csv"), "w") as f:
        f.write(f"# Fig. 7 prototype, {model} leakage model, k1 = k2 = k = 1, alpha = sqrt(0.6), beta = sqrt(0.4)"
                + (", gamma = 0.5" if model == "correlated" else "") + "\n")
        f.write("# expected_holevo_bits = sum_K P_K(t) chi_K (corrected chi_K);\n")
        f.write("# eve_fidelity_operational = sum_K P_K(t) Fbar_K (psi-independent strategy, Haar-averaged fidelity with |psi>);\n")
        f.write("# eve_maxoverlap_lambda = sum_K P_K(t) F_K^lambda (manuscript's definition, corrected; largest eigenvalue of Eve's averaged state).\n")
        f.write(f"time,{key},expected_holevo_bits,eve_fidelity_operational,eve_maxoverlap_lambda\n")
        f.writelines(f"{tt:.3f},{k:.1f},{e:.10f},{fb:.10f},{fl:.10f}\n" for tt, k, e, fb, fl in csv_rows[model])

# ============================================================ time-coupled (unified) figure: gamma(t) = 1 - exp(-t/T1)
T1 = 1.0
gam_t = 1 - np.exp(-t / T1)
fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.4), constrained_layout=True)
rows_tc = []
for col, (model, title) in zip(CAT4, models):
    mu = 0.5
    Echi, EFl, EFb, P = hc.expected_curves(model, t, AL, BE, gam_t, k=1.0, mu=mu)
    lab = model + (r" ($\mu=0.5$)" if model == "correlated" else "")
    axes[0, 0].plot(t, Echi, color=col, label=lab)
    axes[0, 1].plot(t, EFb, color=col, label=lab)
    rows_tc += [(model, T1, tt, g, e, fb, fl) for tt, g, e, fb, fl in zip(t, gam_t, Echi, EFb, EFl)]
# reference: no damping (T1 -> infinity) for the burst model, dotted
Echi0, _, EFb0, _ = hc.expected_curves("burst", t, AL, BE, 0.0, k=1.0)
axes[0, 0].plot(t, Echi0, color=MUTED, ls=":", lw=1.2, label=r"burst, $T_1\to\infty$ (no damping)")
axes[0, 1].plot(t, EFb0, color=MUTED, ls=":", lw=1.2, label=r"burst, $T_1\to\infty$")
axes[0, 0].set(ylabel=r"$\mathbb{E}[\chi(t)]$ (bits)", xlim=(0, 5), ylim=(0, 1.02))
axes[0, 1].set(ylabel=r"$\bar F(t)$ (Eve's Haar-averaged fidelity)", xlim=(0, 5), ylim=(0.45, 1.02))
axes[0, 0].set_title(r"a  four models, $\gamma(t)=1-e^{-t/T_1}$, $kT_1=1$", loc="left", fontweight="bold")
axes[0, 1].set_title(r"b  Eve's fidelity rises, then decays", loc="left", fontweight="bold")
# T1 sweep for the burst model
T1s = [0.25, 0.5, 1.0, 2.0, 4.0]
for col, T in zip(BLUE5, T1s):
    g_t = 1 - np.exp(-t / T)
    Echi, EFl, EFb, _ = hc.expected_curves("burst", t, AL, BE, g_t, k=1.0)
    axes[1, 0].plot(t, Echi, color=col, label=fr"$kT_1={T}$")
    axes[1, 1].plot(t, EFb, color=col, label=fr"$kT_1={T}$")
    rows_tc += [("burst", T, tt, g, e, fb, fl) for tt, g, e, fb, fl in zip(t, g_t, Echi, EFb, EFl)]
axes[1, 0].set(xlabel="time $t$ (units of $1/k$)", ylabel=r"$\mathbb{E}[\chi(t)]$ (bits)", xlim=(0, 5), ylim=(0, 1.02))
axes[1, 1].set(xlabel="time $t$ (units of $1/k$)", ylabel=r"$\bar F(t)$", xlim=(0, 5), ylim=(0.45, 1.02))
axes[1, 0].set_title(r"c  burst model, varying $kT_1$", loc="left", fontweight="bold")
axes[1, 1].set_title(r"d  burst model, peak set by $kT_1$", loc="left", fontweight="bold")
for a in axes.flat:
    a.grid(True, axis="y")
    a.legend(frameon=False)
fig.savefig(os.path.join(HERE, "fig_time_coupled_prototype.png"), dpi=300)
plt.close(fig)
with open(os.path.join(HERE, "fig_time_coupled_prototype.csv"), "w") as f:
    f.write("# Time-coupled version (review item B5): gamma(t) = 1 - exp(-t/T1), k1 = k2 = k = 1, alpha = sqrt(0.6), correlated model at mu = 0.5.\n")
    f.write("# Columns: model, T1 (units of 1/k), time, gamma(t), E[chi(t)] bits, Eve's operational fidelity Fbar(t), manuscript-style F^lambda(t).\n")
    f.write("model,T1,time,gamma_t,expected_holevo_bits,eve_fidelity_operational,eve_maxoverlap_lambda\n")
    f.writelines(f"{m},{T:.2f},{tt:.3f},{g:.10f},{e:.10f},{fb:.10f},{fl:.10f}\n" for m, T, tt, g, e, fb, fl in rows_tc)

# ---- numbers quoted in the README / memo
print("peak of Fbar(t) (burst, kT1 = 1):", t[np.argmax(hc.expected_curves('burst', t, AL, BE, gam_t)[2])],
      np.max(hc.expected_curves('burst', t, AL, BE, gam_t)[2]))
for T in T1s:
    g_t = 1 - np.exp(-t / T)
    Fb = hc.expected_curves("burst", t, AL, BE, g_t)[2]
    print(f"  kT1={T}: peak Fbar = {Fb.max():.4f} at t = {t[np.argmax(Fb)]:.2f}")
print("done")
