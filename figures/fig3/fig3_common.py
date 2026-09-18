"""
Shared data and style for Fig. 3 (a)/(b).

PQC intercepts (processing latency, ns) follow the main text; the slope is the
fibre propagation delay, 5 us/km = 5 ns/m, identical for every scheme.
"""
import os

import matplotlib.pyplot as plt

SLOPE_NS_PER_M = 5.0  # fibre propagation delay, 5 us/km

PQC_INTERCEPT_NS = {
    'Kyber512': 2300,
    'Kyber768': 3100,
    'Kyber1024': 4200,
    'FrodoKEM-640': 15700,
    'FrodoKEM-976': 28400,
    'FrodoKEM-1344': 45100,
}

PQC_DATA = {name: (icpt, SLOPE_NS_PER_M) for name, icpt in PQC_INTERCEPT_NS.items()}

COLORS = {
    'Kyber512': '#08519c', 'Kyber768': '#3182bd', 'Kyber1024': '#6baed6',
    'FrodoKEM-640': '#a50f15', 'FrodoKEM-976': '#de2d26', 'FrodoKEM-1344': '#fb6a4a',
}
MARKERS = {
    'Kyber512': 'o', 'Kyber768': 's', 'Kyber1024': '^',
    'FrodoKEM-640': 'o', 'FrodoKEM-976': 's', 'FrodoKEM-1344': '^',
}
LINESTYLES = {
    'Kyber512': '-', 'Kyber768': '--', 'Kyber1024': ':',
    'FrodoKEM-640': '-', 'FrodoKEM-976': '--', 'FrodoKEM-1344': ':',
}
MARKER_OFFSETS = {
    'Kyber512': 0, 'Kyber768': 2, 'Kyber1024': 4,
    'FrodoKEM-640': 0, 'FrodoKEM-976': 2, 'FrodoKEM-1344': 4,
}
PLOT_ORDER = ['FrodoKEM-1344', 'FrodoKEM-976', 'FrodoKEM-640',
              'Kyber1024', 'Kyber768', 'Kyber512']

# Output directory. In the manuscript tree this pointed at ../Figure, which meant a
# re-run overwrote the submitted PDFs in place; in this repository it defaults to a local
# output/ folder and can be overridden with the QRQT_OUTDIR environment variable.
FIG_DIR = os.environ.get('QRQT_OUTDIR',
                         os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output'))
os.makedirs(FIG_DIR, exist_ok=True)


def apply_style():
    plt.rcParams.update({
        'font.family': 'serif',
        # Pinned, not a preference list: the published Fig. 3 PDFs were rendered with
    # Times New Roman (on Windows). On a machine without it matplotlib falls back
    # to DejaVu Serif and the output will not be byte-identical.
    'font.serif': ['Times New Roman'],
        'font.size': 14,
        'font.weight': 'medium',
        'axes.labelsize': 16,
        'axes.labelweight': 'bold',
        'axes.linewidth': 1.2,
        'xtick.major.width': 1.2,
        'ytick.major.width': 1.2,
        'xtick.direction': 'in',
        'ytick.direction': 'in',
        'xtick.top': True,
        'ytick.right': True,
        'xtick.labelsize': 13,
        'ytick.labelsize': 13,
        'mathtext.fontset': 'dejavuserif',
    })


def save(fig, stem):
    for ext in ('png', 'pdf'):
        fig.savefig(os.path.join(FIG_DIR, f'{stem}.{ext}'), dpi=300,
                    bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f'saved {stem}.png / .pdf -> {FIG_DIR}')


def write_source_data():
    path = os.path.join(FIG_DIR, 'fig3_source_data.csv')
    with open(path, 'w', newline='') as fh:
        fh.write('scheme,intercept_ns,slope_ns_per_m\n')
        for name, (icpt, slope) in PQC_DATA.items():
            fh.write(f'{name},{icpt},{slope:g}\n')
    print(f'wrote {path}')
