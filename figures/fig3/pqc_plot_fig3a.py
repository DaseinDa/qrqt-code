"""
Fig 3(a): Memory-time requirements for PQC schemes -- short-range (0-100 m).
Standalone version with symlog y-axis. Intercepts follow the main text; slope
is 5 ns/m (fibre propagation delay) for every scheme.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.lines import Line2D

from fig3_common import (PQC_DATA, COLORS, MARKERS, LINESTYLES, MARKER_OFFSETS,
                         PLOT_ORDER, apply_style, save, write_source_data)

apply_style()

distance_a = np.linspace(0, 100, 50)
memory_times_a = {n: icpt + slope * distance_a for n, (icpt, slope) in PQC_DATA.items()}

fig, ax = plt.subplots(figsize=(6, 5))

for name in PLOT_ORDER:
    ax.plot(distance_a, memory_times_a[name],
            color=COLORS[name], linestyle=LINESTYLES[name], linewidth=2.2,
            marker=MARKERS[name], markersize=7, markevery=(MARKER_OFFSETS[name], 7),
            markeredgecolor='white', markeredgewidth=0.7, zorder=2)

# Symlog: short linear stub 0-1000 ns, log above (lines span 2,300-45,600 ns)
Y_MIN, Y_MAX = 0, 80000
ax.set_yscale('symlog', linthresh=1000, linscale=0.2)
ax.set_xlabel('Distance (m)')
ax.set_ylabel('Memory lifetime (ns)')
ax.set_xlim(0, 100)
ax.set_ylim(Y_MIN, Y_MAX)


def plain_formatter(x, pos):
    return '0' if x == 0 else f'{int(x)}'


ax.yaxis.set_major_formatter(ticker.FuncFormatter(plain_formatter))
ax.set_yticks([0, 1000, 2000, 3000, 5000, 10000, 20000, 30000, 50000])
ax.yaxis.set_minor_locator(ticker.NullLocator())

# Family labels: FrodoKEM above its top line, Kyber below its bottom line
bbox_props = dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85)
ax.text(92, 62000, 'FrodoKEM', fontsize=15, color='#a50f15',
        fontweight='bold', ha='center', va='center', bbox=bbox_props)
ax.text(92, 1550, 'Kyber', fontsize=15, color='#08519c',
        fontweight='bold', ha='center', va='center', bbox=bbox_props)

legend_elements = [
    Line2D([0], [0], color='#3182bd', lw=2.2, label='Kyber'),
    Line2D([0], [0], color='#de2d26', lw=2.2, label='FrodoKEM'),
    Line2D([0], [0], color='#555555', linestyle='-', marker='o',
           markersize=5, lw=1.2, markeredgecolor='white', markeredgewidth=0.5, label='Level 1'),
    Line2D([0], [0], color='#555555', linestyle='--', marker='s',
           markersize=4.5, lw=1.2, markeredgecolor='white', markeredgewidth=0.5, label='Level 3'),
    Line2D([0], [0], color='#555555', linestyle=':', marker='^',
           markersize=4.5, lw=1.2, markeredgecolor='white', markeredgewidth=0.5, label='Level 5'),
]
leg = ax.legend(handles=legend_elements, loc='upper left',
                bbox_to_anchor=(0.0, -0.12),
                framealpha=0.95, edgecolor='#cccccc',
                fontsize=9, handlelength=2.4, borderpad=0.6,
                labelspacing=0.4, handletextpad=0.6,
                ncol=3, columnspacing=1.0)
leg.get_frame().set_linewidth(0.6)

plt.tight_layout()
save(fig, 'fig3a_memory_time_short_range')
write_source_data()
print(f'Fig 3(a) y-limits: {Y_MIN}-{Y_MAX} ns (symlog, linthresh=1000)')
