"""Margins of the design rule at the published core-SVP exponents, for Supplementary Table
tab:design_rule_margins in si_v2/appendix_BKZ.tex.  Cost-to-success mapping adopted for the
sensitivity analysis: P_break(T) = min(1, T R / 2^lambda); rule P_break(T_rot + T_E ln(1/2eps)) <= 2 eps;
margin = log10[ 2 eps 2^lambda / ( R (T_rot + T_E ln(1/2eps)) ) ]  (decades; positive = satisfied).
Reference grid T_rot = 30 d, T_E = 24 h.  The exponents are those quoted in Sec. appendix:core_svp_reference
(Kyber specification v3.02 Table 4; FrodoKEM specification Table 2; Kyber refined classical gate counts).
The script also checks the numbers against _sciadv_work/security/design_rule_table.md (T_E = 24 h column).
Run:  python -I si_design_rule_margins.py
"""
import math, os, re

lam = {  # scheme: (classical, quantum, refined gate count or None)
    "ML-KEM-512": (118, 107, 151.5),
    "ML-KEM-768": (183, 166, 215.1),
    "ML-KEM-1024": (256, 232, 287.3),
    "FrodoKEM-640": (145, 132, None),
    "FrodoKEM-976": (210, 191, None),
    "FrodoKEM-1344": (275, 250, None),
}
T_rot = 30 * 86400.0
T_E = 24 * 3600.0
combos = [(32, 40), (32, 60), (32, 80), (64, 40), (64, 60), (64, 80)]   # (-log2 eps, log2 R)


def margin(l, e, r, Trot=T_rot, TE=T_E):
    L = math.log(2 ** (e - 1))            # ln(1/(2 eps)) with eps = 2^-e
    return (l - e + 1 - r) * math.log10(2) - math.log10(Trot + TE * L)


print("margin (decades) at T_rot = 30 d, T_E = 24 h; columns (eps, R) =", combos)
rows = []
for s, (lc, lq, lg) in lam.items():
    for name, l in (("classical", lc), ("quantum", lq), ("refined gates", lg)):
        if l is None:
            continue
        vals = [margin(l, e, r) for e, r in combos]
        rows.append((s, name, l, vals))
        print(f"{s:14s} {name:14s} lambda={l:6}  " + "  ".join(f"{v:+6.1f}" for v in vals))

print()
print("ML-KEM-768 quantum, eps=2^-32, R=2^80: %.4f decades" % margin(166, 32, 80))
print("ML-KEM-768 quantum, eps=2^-64, R=2^80, T_rot = 1 yr: %.2f decades" % margin(166, 64, 80, Trot=365.25 * 86400))
print("ML-KEM-512 quantum, eps=2^-32, R=2^60: %.2f; classical: %.2f" % (margin(107, 32, 60), margin(118, 32, 60)))
print("ML-KEM-512 quantum, eps=2^-32, R=2^60: time budget 2 eps 2^lambda / R = %.1f h" % (2 ** (107 - 31 - 60) / 3600))

# cross-check against the security package's table (T_E = 24 h column)
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "security", "design_rule_table.md")
if os.path.exists(path):
    txt = open(path, encoding="utf-8").read()
    bad = 0
    for sec in re.finditer(r"## eps = 2\^-(\d+), R = 2\^(\d+) ops/s, T_rot = 30 days.*?\n\n(.*?)\n\n", txt, re.S):
        e, r = int(sec.group(1)), int(sec.group(2))
        for line in sec.group(3).splitlines():
            m = re.match(r"\| (\S+) \| (classical|quantum|refined gates \(classical\)) \| ([\d.]+) \| [^|]*\| [^|]*\| [^|]*\| ([+-][\d.]+) \|", line)
            if not m:
                continue
            l = float(m.group(3)); ref = float(m.group(4))
            mine = margin(l, e, r)
            if abs(mine - ref) > 0.051:
                bad += 1
                print("MISMATCH", m.group(1), m.group(2), e, r, mine, ref)
    print("cross-check against security/design_rule_table.md (T_E = 24 h):", "all rows agree to 0.05" if bad == 0 else f"{bad} mismatches")
