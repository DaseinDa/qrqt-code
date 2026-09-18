"""Supplementary Figures 1 and 2 of "Quantum-Resistant Quantum Teleportation".

Renamed from the author's Figure61.py. ONE script produces BOTH figures:

  Supplementary Fig. 1  log2pr_vs_m.pdf      Pade vs exact log2 P_LWE against lattice
                                             dimension m = 5..60, at a = 0.3, b = 2.7,
                                             T_BKZ = 2^30 s, ||b1|| = 10, d_i = 2, s = 2
  Supplementary Fig. 2  log2Pr_vs_TBKZ.pdf   the same comparison against log2 T_BKZ =
                                             20..98, at a = 1.8, b = 2.7, m = 500,
                                             ||b1|| = 10, d_i = 2, s = 2

Those are the parameters the code actually uses. The captions printed in the submitted
Supplementary Information had the two a values transposed and gave m = 30, d_i = 1 for
Supplementary Fig. 2 (values copied from a superseded script that produced no published
figure); the captions were corrected on 2026-09-17 to match this file.

Changes from the original: the two hardcoded /home/xin/... save paths now write to OUTDIR,
and DejaVu Serif is pinned because the published PDFs were rendered with it.
"""
import os
OUTDIR = os.environ.get("QRQT_OUTDIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "output"))
os.makedirs(OUTDIR, exist_ok=True)

import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erf
import matplotlib as mpl

# ── Professional style ────────────────────────────────────────────
mpl.rcParams.update({
    'font.family': 'serif',
    # Pinned, not a preference list: the published supplementary PDFs were
    # rendered with DejaVu Serif, and Supplementary Fig. 1 reproduces pixel for
    # pixel only with it. Asking for Times New Roman first silently changes the
    # page geometry on any machine that has Times.
    'font.serif': ['DejaVu Serif'],
    'text.usetex': False,
    'mathtext.fontset': 'cm',
    'font.size': 11,
    'axes.labelsize': 13,
    'axes.titlesize': 12,
    'legend.fontsize': 10,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'axes.linewidth': 0.9,
    'xtick.major.width': 0.7,
    'ytick.major.width': 0.7,
    'xtick.minor.visible': True,
    'ytick.minor.visible': True,
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'xtick.top': True,
    'ytick.right': True,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.05,
})

C_EXACT = '#1f77b4'
C_PADE  = '#d62728'
C_ERROR = '#2ca02c'

# ── Functions ─────────────────────────────────────────────────────
def log2_Pr_exact(m, a, b, T_BKZ, s, b1_norm, di=None):
    if di is None:
        di = np.ones(m)
    gamma = 2 * a / (np.log2(T_BKZ) + b)
    lambda_ = b1_norm * np.sqrt(np.pi) / (2 * s)
    i_vals = np.arange(1, m + 1)
    z_i = di * lambda_ * 2 ** (-gamma * (i_vals - 1))
    return np.sum(np.log2(erf(z_i)))

def log2_Pr_pade(m, a, b, T_BKZ, s, b1_norm, di=None, pade_a=0.140012):
    if di is None:
        di = np.ones(m)
    gamma = 2 * a / (np.log2(T_BKZ) + b)
    lambda_ = b1_norm * np.sqrt(np.pi) / (2 * s)
    i_vals = np.arange(1, m + 1)
    W_i = (di**2) * (lambda_**2) * 2 ** (-2 * gamma * (i_vals - 1))
    exponent = - (W_i * (4 / np.pi + pade_a * W_i)) / (1 + pade_a * W_i)
    erf_approx = np.sqrt(1 - np.exp(exponent))
    return np.sum(np.log2(erf_approx))

def get_di_vector(m, value=2):
    return np.full(m, value)


# ══════════════════════════════════════════════════════════════════
# Figure 1: log2 Pr vs m  (with relative error subplot)
# ══════════════════════════════════════════════════════════════════
m_vals = np.arange(5, 61)
exact_arr = np.array([log2_Pr_exact(m, 0.3, 2.7, 2**30, 2, 10, get_di_vector(m, 2)) for m in m_vals])
pade_arr  = np.array([log2_Pr_pade(m, 0.3, 2.7, 2**30, 2, 10, get_di_vector(m, 2)) for m in m_vals])

# Relative error (avoid division by zero for near-zero exact values)
with np.errstate(divide='ignore', invalid='ignore'):
    rel_err_m = np.where(
        (np.abs(exact_arr) > 1e-30) & np.isfinite(pade_arr),
        np.abs((pade_arr - exact_arr) / exact_arr),
        0.0)
    rel_err_m = np.where(np.isfinite(rel_err_m), rel_err_m, 0.0)

scale = 1e-8

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6.5, 5.8),
                                 height_ratios=[3, 1.2],
                                 sharex=True)
fig.subplots_adjust(hspace=0.08)

# --- Main plot ---
# Exact first, then Padé on top with dashes visible
ax1.plot(m_vals, exact_arr / scale, color=C_EXACT, lw=2.0,
         label='Exact', zorder=3)
ax1.plot(m_vals, pade_arr / scale, color=C_PADE, lw=1.8, ls='--', dashes=(6, 3),
         label=u'Pad\u00e9 approx', zorder=4)

# Markers only in the "interesting" region where curves diverge (m >= 48)
mask_marker = m_vals >= 45
idx_sparse = np.arange(0, mask_marker.sum(), 3)  # every 3rd point in this region
m_mark = m_vals[mask_marker][idx_sparse]
ax1.plot(m_mark, exact_arr[mask_marker][idx_sparse] / scale, 'o',
         color=C_EXACT, ms=5, mfc='white', mew=1.4, zorder=5)
ax1.plot(m_mark, pade_arr[mask_marker][idx_sparse] / scale, 's',
         color=C_PADE, ms=5, mfc='white', mew=1.4, zorder=5)

ax1.set_ylabel(r'$\log_2 \Pr$  $(\times 10^{-8})$')
ax1.legend(frameon=True, fancybox=False, edgecolor='0.65',
           loc='lower left', borderpad=0.5, handlelength=2.2)
ax1.grid(True, ls=':', lw=0.35, color='0.8', zorder=0)
ax1.set_xlim(m_vals[0], m_vals[-1])
# Remove x tick labels on top plot (shared axis)
ax1.tick_params(labelbottom=False)

# --- Annotation: (a) ---
ax1.text(0.02, 0.95, '(a)', transform=ax1.transAxes,
         fontsize=12, fontweight='bold', va='top')

# --- Error subplot ---
# Only show relative error where |exact| is large enough to be meaningful
threshold_m = np.abs(exact_arr) > 1e-15
rel_err_plot_m = np.where(threshold_m, rel_err_m, np.nan)
ax2.semilogy(m_vals, rel_err_plot_m, color=C_ERROR, lw=1.5, zorder=3)
ax2.fill_between(m_vals, rel_err_plot_m, alpha=0.12, color=C_ERROR, zorder=2)
ax2.set_xlabel(r'$m$')
ax2.set_ylabel('Relative error')
ax2.grid(True, ls=':', lw=0.35, color='0.8', zorder=0)
ax2.set_xlim(m_vals[0], m_vals[-1])
# Sensible y-limits
valid_err = rel_err_m[(rel_err_m > 0) & np.isfinite(rel_err_m) & threshold_m]
if len(valid_err) > 0:
    ax2.set_ylim(valid_err.min() * 0.3, valid_err.max() * 3)

ax2.text(0.02, 0.90, '(b)', transform=ax2.transAxes,
         fontsize=12, fontweight='bold', va='top')

fig.savefig(os.path.join(OUTDIR, 'log2pr_vs_m.pdf'))
plt.close(fig)


# ══════════════════════════════════════════════════════════════════
# Figure 2: log2 Pr vs T_BKZ  (with relative error subplot)
# ══════════════════════════════════════════════════════════════════
T_exp = np.arange(20, 100, 2)
T_vals = 2.0 ** T_exp
m_fixed = 500
di_fixed = get_di_vector(m_fixed, value=2)

exact_T = np.array([log2_Pr_exact(m_fixed, 1.8, 2.7, T, 2, 10, di_fixed) for T in T_vals])
pade_T  = np.array([log2_Pr_pade(m_fixed, 1.8, 2.7, T, 2, 10, di_fixed) for T in T_vals])

with np.errstate(divide='ignore', invalid='ignore'):
    rel_err_T = np.where(
        (np.abs(exact_T) > 1e-30) & np.isfinite(pade_T),
        np.abs((pade_T - exact_T) / exact_T),
        0.0)
    rel_err_T = np.where(np.isfinite(rel_err_T), rel_err_T, 0.0)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6.5, 5.8),
                                 height_ratios=[3, 1.2],
                                 sharex=True)
fig.subplots_adjust(hspace=0.08)

# --- Main plot ---
ax1.plot(T_exp, exact_T, color=C_EXACT, lw=2.0,
         label='Exact', zorder=3)
ax1.plot(T_exp, pade_T, color=C_PADE, lw=1.8, ls='--', dashes=(6, 3),
         label=u'Pad\u00e9 approx', zorder=4)

# Evenly spaced markers along the full range
idx_m2 = np.arange(0, len(T_exp), 5)
ax1.plot(T_exp[idx_m2], exact_T[idx_m2], 'o',
         color=C_EXACT, ms=5, mfc='white', mew=1.4, zorder=5)
ax1.plot(T_exp[idx_m2], pade_T[idx_m2], 's',
         color=C_PADE, ms=5.5, mfc='white', mew=1.4, zorder=4)

ax1.set_ylabel(r'$\log_2 \Pr$')
ax1.legend(frameon=True, fancybox=False, edgecolor='0.65',
           loc='lower right', borderpad=0.5, handlelength=2.2)
ax1.grid(True, ls=':', lw=0.35, color='0.8', zorder=0)
ax1.set_xlim(T_exp[0], T_exp[-1])
ax1.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(
    lambda x, _: f'{x:,.0f}'))
ax1.tick_params(labelbottom=False)

ax1.text(0.02, 0.95, '(a)', transform=ax1.transAxes,
         fontsize=12, fontweight='bold', va='top')

# --- Error subplot ---
threshold_T = np.abs(exact_T) > 1e-15
rel_err_plot_T = np.where(threshold_T & (rel_err_T > 0), rel_err_T, np.nan)
ax2.semilogy(T_exp, rel_err_plot_T, color=C_ERROR, lw=1.5, zorder=3)
ax2.fill_between(T_exp, rel_err_plot_T, alpha=0.12, color=C_ERROR, zorder=2)
ax2.set_xlabel(r'$\log_2 T_{\mathrm{BKZ}}$')
ax2.set_ylabel('Relative error')
ax2.grid(True, ls=':', lw=0.35, color='0.8', zorder=0)
ax2.set_xlim(T_exp[0], T_exp[-1])
valid_err_T = rel_err_T[(rel_err_T > 0) & np.isfinite(rel_err_T) & threshold_T]
if len(valid_err_T) > 0:
    ax2.set_ylim(valid_err_T.min() * 0.3, valid_err_T.max() * 3)

ax2.text(0.02, 0.90, '(b)', transform=ax2.transAxes,
         fontsize=12, fontweight='bold', va='top')

fig.savefig(os.path.join(OUTDIR, 'log2Pr_vs_TBKZ.pdf'))
plt.close(fig)

print("Done – both figures saved.")
