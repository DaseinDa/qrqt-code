"""
Fig 3(b): Memory-time requirements for PQC schemes -- long-range (0-500 m).
Broken axis: quantum-memory platforms (log, top) + PQC lines (linear, bottom).
Intercepts follow the main text; slope is 5 ns/m for every scheme.
"""
import math

import numpy as np
import matplotlib.pyplot as plt

from fig3_common import (PQC_DATA, COLORS, MARKERS, LINESTYLES, MARKER_OFFSETS,
                         PLOT_ORDER, apply_style, save)

apply_style()

distance_b = np.linspace(0, 500, 50)
memory_times_b = {n: icpt + slope * distance_b for n, (icpt, slope) in PQC_DATA.items()}

fig = plt.figure(figsize=(7, 6))
gs = fig.add_gridspec(2, 1, height_ratios=[1.1, 1], hspace=0.08,
                      left=0.12, right=0.82, bottom=0.10, top=0.95)
ax_top = fig.add_subplot(gs[0])
ax_bot = fig.add_subplot(gs[1])

# ============== Top Panel: Quantum Platforms (log scale) -- unchanged ==============
ax_top.set_yscale('log')
ax_top.set_xlim(0, 500)
ax_top.set_ylim(8e5, 1.5e13)

platforms = [
    {'name': 'Trapped ions', 'T2': '1 h',    'y': 3.6e12, 'color': '#8c6bb1'},
    {'name': 'NV center',    'T2': '1 s',    'y': 1e9,    'color': '#88bedc'},
    {'name': 'SC cavity',    'T2': '34 ms',  'y': 3.4e7,  'color': '#a8ddb5'},
    {'name': 'Fluxonium',    'T2': '1.4 ms', 'y': 1.4e6,  'color': '#fed976'},
]
for p in platforms:
    ax_top.axhspan(p['y'] / 3, p['y'] * 3, alpha=0.4, facecolor=p['color'],
                   edgecolor='none', zorder=1)
    ax_top.axhline(y=p['y'], color='#444444', linestyle=':',
                   linewidth=0.6, alpha=0.7, zorder=2)
    ax_top.text(520, p['y'], f"{p['name']}\n({p['T2']})", fontsize=14,
                va='center', ha='left', color='#222222', linespacing=0.9,
                fontweight='bold')

ax_top.set_xticklabels([])
ax_top.tick_params(axis='x', which='both', bottom=True, top=True, labelbottom=False)
ax_top.set_ylabel('Quantum coherence time (ns)')

# ============== Bottom Panel: PQC Lines (linear scale) ==============
for name in PLOT_ORDER:
    ax_bot.plot(distance_b, memory_times_b[name],
                color=COLORS[name], linestyle=LINESTYLES[name], linewidth=1.8,
                marker=MARKERS[name], markersize=5.5,
                markevery=(MARKER_OFFSETS[name], 7),
                markeredgecolor='white', markeredgewidth=0.6, zorder=3)

Y_MIN, Y_MAX = 0, 52000
ax_bot.set_xlim(0, 500)
ax_bot.set_ylim(Y_MIN, Y_MAX)
ax_bot.set_xlabel('Distance (m)')
ax_bot.set_ylabel('Memory lifetime (ns)')
ax_bot.set_yticks([0, 10000, 20000, 30000, 40000, 50000])

# End labels for line families, placed beside the middle line of each family
bbox_props = dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85)
ax_bot.text(515, memory_times_b['FrodoKEM-976'][-1], 'FrodoKEM', fontsize=14,
            color='#a50f15', fontweight='bold', ha='left', va='center', bbox=bbox_props)
ax_bot.text(515, memory_times_b['Kyber768'][-1], 'Kyber', fontsize=14,
            color='#08519c', fontweight='bold', ha='left', va='center', bbox=bbox_props)

# ============== Broken Axis Decoration ==============
ax_top.spines['bottom'].set_visible(False)
ax_bot.spines['top'].set_visible(False)
ax_top.tick_params(axis='x', which='both', bottom=False)

d = 0.012
kwargs = dict(transform=ax_top.transAxes, color='k', clip_on=False, linewidth=0.8)
ax_top.plot((-d, +d), (-d, +d), **kwargs)
ax_top.plot((1 - d, 1 + d), (-d, +d), **kwargs)
kwargs.update(transform=ax_bot.transAxes)
ax_bot.plot((-d, +d), (1 - d, 1 + d), **kwargs)
ax_bot.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)

# Gap annotation: margin = smallest coherence benchmark / largest PQC requirement at 500 m
min_coherence_ns = min(p['y'] for p in platforms)              # fluxonium, 1.4e6 ns
max_pqc_ns = max(v[-1] for v in memory_times_b.values())        # FrodoKEM-1344 at 500 m
margin_floor = math.floor(min_coherence_ns / max_pqc_ns)
margin_text = f'>{margin_floor}×\nmargin'
fig.text(0.72, 0.535, '▲', fontsize=11, ha='center', va='center', color='#555555')
fig.text(0.72, 0.49, '▼', fontsize=11, ha='center', va='center', color='#555555')
fig.text(0.745, 0.513, margin_text, fontsize=10, ha='left', va='center',
         color='#555555', linespacing=0.9, style='italic', fontweight='bold')

# Legend is in Fig 3(a); not repeated here.
save(fig, 'fig3b_memory_time_long_range')
print(f'Fig 3(b) bottom y-limits: {Y_MIN}-{Y_MAX} ns (linear)')
print(f'margin: {min_coherence_ns:.3g} / {max_pqc_ns:.0f} = {min_coherence_ns / max_pqc_ns:.2f}'
      f' -> annotation {margin_text!r}')
