"""
holevo_correct.py -- corrected information-theoretic analysis for R3/R4 of QRQT.

Model (as stated in the manuscript, R3 / Methods / SI Note "Holevo Information with an
Amplitude-Damped Bell Pair"):
    input  |psi>_C = alpha|0> + beta|1>
    resource |Phi+>_{AB} = (|00>+|11>)/sqrt2
    amplitude damping E_AD (parameter gamma) on Bob's qubit B, applied BEFORE Alice's
    Bell measurement on (C,A).  Kraus: E0 = diag(1, sqrt(1-gamma)), E1 = sqrt(gamma)|0><1|.
    Outcome labels (m1, m2): in the ideal protocol Bob holds X^{m1} Z^{m2} |psi>,
    so the correction is U = Z^{m2} X^{m1} (manuscript convention, R3 first paragraph).

Because E_AD acts on B and the Bell projection acts on (C,A), the two commute, and the
(normalized) conditional state of Bob is

    rho_m = E_AD( sigma_m |psi><psi| sigma_m^dag ),   sigma_m = X^{m1} Z^{m2},  p_m = 1/4,

NOT sigma_m E_AD(psi) sigma_m^dag as the submitted text asserts.  E_AD commutes with Z
(Z-covariant) but not with X, so the m1 = 1 states differ from Pauli conjugates of rho_00.

Everything below is written with the manuscript's h(x) := H_2((1+x)/2), i.e. the binary
entropy of a qubit whose Bloch-vector length (eigenvalue gap) is x.  h(0) = 1, h(1) = 0.

Two families of "fidelity" are provided:
  * F_K^lam  : the manuscript's definition, F_K = max_sigma sum_i p_i <sigma|rho_i|sigma>
               = largest eigenvalue of Eve's averaged state, averaged over the bits she
               knows.  Reaching it requires knowing psi (the eigenvector depends on psi).
  * Fbar_K   : operational adversary fidelity -- Eve applies a CPTP map that may depend on
               the bits she knows but NOT on psi; fidelity <psi|out|psi> averaged over the
               unknown bits and over Haar-random psi.  Closed forms derived in the memo
               (Section 3) and verified numerically in verify_holevo.py.
"""
import numpy as np

# ----------------------------------------------------------------------------- basics
I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)


def H2(p):
    """Binary Shannon entropy in bits of a probability p (vectorised, safe at 0 and 1)."""
    p = np.asarray(p, dtype=float)
    out = np.zeros_like(p)
    mask = (p > 0) & (p < 1)
    pm = p[mask]
    out[mask] = -pm * np.log2(pm) - (1 - pm) * np.log2(1 - pm)
    return out


def h(x):
    """Manuscript's h(x): entropy of a qubit with eigenvalues (1 +/- x)/2.  h(0)=1, h(1)=0."""
    x = np.clip(np.abs(np.asarray(x, dtype=float)), 0.0, 1.0)
    return H2((1.0 + x) / 2.0)


def vn_entropy(rho):
    ev = np.linalg.eigvalsh(rho)
    ev = ev[ev > 1e-15]
    return float(-np.sum(ev * np.log2(ev)))


def holevo(probs, states):
    rho_avg = sum(p * r for p, r in zip(probs, states))
    return vn_entropy(rho_avg) - sum(p * vn_entropy(r) for p, r in zip(probs, states))


# ----------------------------------------------------------------------------- channel
def ad_kraus(gamma):
    E0 = np.array([[1, 0], [0, np.sqrt(1 - gamma)]], dtype=complex)
    E1 = np.array([[0, np.sqrt(gamma)], [0, 0]], dtype=complex)
    return [E0, E1]


def ad(rho, gamma):
    return sum(E @ rho @ E.conj().T for E in ad_kraus(gamma))


def sigma_m(m1, m2):
    """sigma_m = X^{m1} Z^{m2} (manuscript convention)."""
    return np.linalg.matrix_power(X, m1) @ np.linalg.matrix_power(Z, m2)


def psi_vec(alpha, beta):
    return np.array([alpha, beta], dtype=complex)


# ----------------------------------------------------------------------------- closed forms
def conditional_states_closed(alpha, beta, gamma):
    """The four corrected conditional states rho_m = AD(sigma_m psi sigma_m^dag), closed form.

    Returns dict {(m1,m2): 2x2 array}.  With
        a  = |alpha|^2 + gamma |beta|^2,  b  = (1-gamma)|beta|^2,  c  = alpha beta^* sqrt(1-gamma)
        a' = |beta|^2 + gamma |alpha|^2,  b' = (1-gamma)|alpha|^2, c' = beta alpha^* sqrt(1-gamma) = c^*
    rho_00 = [[a, c],[c*, b]],  rho_01 = [[a,-c],[-c*, b]],
    rho_10 = [[a', c'],[c'*, b']],  rho_11 = [[a',-c'],[-c'*, b']].
    """
    A2, B2 = abs(alpha) ** 2, abs(beta) ** 2
    s = np.sqrt(1 - gamma)
    a, b, c = A2 + gamma * B2, (1 - gamma) * B2, alpha * np.conj(beta) * s
    ap, bp, cp = B2 + gamma * A2, (1 - gamma) * A2, beta * np.conj(alpha) * s
    return {
        (0, 0): np.array([[a, c], [np.conj(c), b]]),
        (0, 1): np.array([[a, -c], [-np.conj(c), b]]),
        (1, 0): np.array([[ap, cp], [np.conj(cp), bp]]),
        (1, 1): np.array([[ap, -cp], [-np.conj(cp), bp]]),
    }


def deltas(alpha, beta, gamma):
    """Eigenvalue gaps.  det rho_{0 m2} = gamma(1-gamma)|beta|^4, det rho_{1 m2} = gamma(1-gamma)|alpha|^4."""
    A2, B2 = abs(alpha) ** 2, abs(beta) ** 2
    d_beta = np.sqrt(np.clip(1 - 4 * gamma * (1 - gamma) * B2 ** 2, 0, 1))
    d_alpha = np.sqrt(np.clip(1 - 4 * gamma * (1 - gamma) * A2 ** 2, 0, 1))
    return d_beta, d_alpha


def chi_K_closed(alpha, beta, gamma):
    """Corrected conditional Holevo quantities chi_K, K in {empty,{1},{2},{1,2}}.

    chi_K := sum over the bits in K (each value prob 1/2) of the Holevo quantity of the
    ensemble Eve faces given those bits (uniform over the unrevealed bits).

    chi_empty = h(gamma) - 1/2[h(delta_beta) + h(delta_alpha)]
    chi_{1}   = 1/2[h(|1-2a|) - h(delta_beta)] + 1/2[h(|1-2a'|) - h(delta_alpha)]
    chi_{2}   = h(sqrt(gamma^2 + 4 r^2)) - 1/2[h(delta_beta) + h(delta_alpha)],  r = Re(alpha beta^*) sqrt(1-gamma)
    chi_{12}  = 0
    """
    A2, B2 = abs(alpha) ** 2, abs(beta) ** 2
    gamma = np.asarray(gamma, dtype=float)
    d_beta, d_alpha = deltas(alpha, beta, gamma)
    S_ind = 0.5 * (h(d_beta) + h(d_alpha))           # mean conditional-state entropy
    a = A2 + gamma * B2
    ap = B2 + gamma * A2
    r = np.real(alpha * np.conj(beta)) * np.sqrt(1 - gamma)
    chi_e = h(gamma) - S_ind
    chi_1 = 0.5 * (h(np.abs(1 - 2 * a)) - h(d_beta)) + 0.5 * (h(np.abs(1 - 2 * ap)) - h(d_alpha))
    chi_2 = h(np.sqrt(gamma ** 2 + 4 * r ** 2)) - S_ind
    chi_12 = np.zeros_like(gamma)
    return {"empty": chi_e, "1": chi_1, "2": chi_2, "12": chi_12}


def chi_paper(alpha, beta, gamma):
    """The SUBMITTED closed forms (R3 Eqs. after 'Pauli conjugates'), for comparison only."""
    A2, B2 = abs(alpha) ** 2, abs(beta) ** 2
    gamma = np.asarray(gamma, dtype=float)
    delta = np.sqrt(np.clip(1 - 4 * gamma * (1 - gamma) * B2 ** 2, 0, 1))
    a = A2 + gamma * B2
    r = np.real(alpha * np.conj(beta)) * np.sqrt(1 - gamma)
    return {"empty": 1 - h(delta), "1": h(np.abs(1 - 2 * a)) - h(delta),
            "2": h(2 * np.abs(r)) - h(delta), "12": np.zeros_like(gamma)}


def F_lam_closed(alpha, beta, gamma):
    """Corrected version of the manuscript's F_K (largest eigenvalue of Eve's averaged state,
    averaged over the bits she knows).  Requires knowledge of psi to attain.

    F_empty = (1+gamma)/2
    F_{1}   = 1/2 + 1/4(|1-2a| + |1-2a'|)
    F_{2}   = 1/2(1 + sqrt(gamma^2 + 4 r^2))
    F_{12}  = 1/2 + 1/4(delta_beta + delta_alpha)
    """
    A2, B2 = abs(alpha) ** 2, abs(beta) ** 2
    gamma = np.asarray(gamma, dtype=float)
    d_beta, d_alpha = deltas(alpha, beta, gamma)
    a = A2 + gamma * B2
    ap = B2 + gamma * A2
    r = np.real(alpha * np.conj(beta)) * np.sqrt(1 - gamma)
    return {"empty": (1 + gamma) / 2,
            "1": 0.5 + 0.25 * (np.abs(1 - 2 * a) + np.abs(1 - 2 * ap)),
            "2": 0.5 * (1 + np.sqrt(gamma ** 2 + 4 * r ** 2)),
            "12": 0.5 + 0.25 * (d_beta + d_alpha)}


def F_lam_paper(alpha, beta, gamma):
    """The SUBMITTED F_K, for comparison only."""
    A2, B2 = abs(alpha) ** 2, abs(beta) ** 2
    gamma = np.asarray(gamma, dtype=float)
    delta = np.sqrt(np.clip(1 - 4 * gamma * (1 - gamma) * B2 ** 2, 0, 1))
    a = A2 + gamma * B2
    r = np.real(alpha * np.conj(beta)) * np.sqrt(1 - gamma)
    return {"empty": 0.5 * np.ones_like(gamma), "1": 0.5 * (1 + np.abs(1 - 2 * a)),
            "2": 0.5 + np.abs(r), "12": 0.5 * (1 + delta)}


def Fbar_closed(gamma):
    """Operational (psi-independent strategy, Haar-averaged) adversary fidelities.

    Fbar_empty = 1/2
    Fbar_{1}   = 2/3 - gamma/6                       (strategy: apply X^{m1}; psi arrives Z-dephased then damped)
    Fbar_{2}   = 1/2 + sqrt(1-gamma)/6               (strategy: apply Z^{m2}; psi arrives X-dephased then damped)
    Fbar_{12}  = 2/3 - gamma/6 + sqrt(1-gamma)/3     (strategy: full Pauli correction)
               = (2 F_e + 1)/3 with F_e = (1+sqrt(1-gamma))^2/4 = fully entangled fraction of (I x AD)(Phi+)
    All four are optimal over all CPTP recovery maps (proof in HOLEVO_MEMO.md, Sec. 3); they are
    independent of psi by construction and do not depend on |alpha|^2.
    """
    gamma = np.asarray(gamma, dtype=float)
    s = np.sqrt(1 - gamma)
    return {"empty": 0.5 * np.ones_like(gamma), "1": 2 / 3 - gamma / 6,
            "2": 0.5 + s / 6, "12": 2 / 3 - gamma / 6 + s / 3}


# ----------------------------------------------------------------------------- 3-qubit simulation
def bell_state(m1, m2):
    """|Phi_{m1 m2}>_{CA} = (Z^{m2} X^{m1} (x) I)|Phi+>, so that at gamma=0 Bob holds X^{m1}Z^{m2}|psi>
    up to a global phase (checked in verify_holevo.py)."""
    phi_plus = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
    U = np.linalg.matrix_power(Z, m2) @ np.linalg.matrix_power(X, m1)
    return np.kron(U, I2) @ phi_plus


def simulate_conditional_states(alpha, beta, gamma, damping_after_measurement=False):
    """Direct 3-qubit density-matrix simulation.  Qubit order (C, A, B).

    Builds rho_CAB = psi (x) Phi+_{AB}, applies the amplitude-damping Kraus operators on B,
    projects (C,A) onto the Bell state |Phi_m>, traces out (C,A).
    Returns dict m -> (p_m, normalized rho_m).  If damping_after_measurement=True the Kraus
    operators are applied after the projection instead (must give identical results: the
    operations act on disjoint subsystems and commute).
    """
    psi = psi_vec(alpha, beta)
    phi_plus = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
    state = np.kron(psi, phi_plus)                     # 8-vector, order C A B
    rho = np.outer(state, state.conj())
    kraus_B = [np.kron(np.eye(4), E) for E in ad_kraus(gamma)]
    if not damping_after_measurement:
        rho = sum(K @ rho @ K.conj().T for K in kraus_B)
    out = {}
    for m1 in (0, 1):
        for m2 in (0, 1):
            b = bell_state(m1, m2)
            P = np.kron(np.outer(b, b.conj()), I2)      # projector on (C,A), identity on B
            r = P @ rho @ P.conj().T
            if damping_after_measurement:
                r = sum(K @ r @ K.conj().T for K in kraus_B)
            # partial trace over C,A: reshape (4,2,4,2) and trace first/third
            r4 = r.reshape(4, 2, 4, 2)
            rhoB = np.einsum("iaib->ab", r4)
            p = float(np.real(np.trace(rhoB)))
            out[(m1, m2)] = (p, rhoB / p if p > 1e-14 else rhoB)
    return out


def chi_K_sim(alpha, beta, gamma):
    """chi_K from the simulation (no closed forms used)."""
    cs = simulate_conditional_states(alpha, beta, gamma)
    probs = {m: cs[m][0] for m in cs}
    states = {m: cs[m][1] for m in cs}
    # K = empty
    chi_e = holevo([probs[m] for m in states], [states[m] for m in states])
    # K = {1}: known m1; ensemble over m2 with conditional probs
    chi_1 = 0.0
    for m1 in (0, 1):
        pk = probs[(m1, 0)] + probs[(m1, 1)]
        chi_1 += pk * holevo([probs[(m1, m2)] / pk for m2 in (0, 1)], [states[(m1, m2)] for m2 in (0, 1)])
    chi_2 = 0.0
    for m2 in (0, 1):
        pk = probs[(0, m2)] + probs[(1, m2)]
        chi_2 += pk * holevo([probs[(m1, m2)] / pk for m1 in (0, 1)], [states[(m1, m2)] for m1 in (0, 1)])
    return {"empty": chi_e, "1": chi_1, "2": chi_2, "12": 0.0}, probs, states


def F_lam_sim(alpha, beta, gamma):
    """Largest eigenvalue of Eve's averaged state per knowledge class, from the simulation."""
    cs = simulate_conditional_states(alpha, beta, gamma)
    probs = {m: cs[m][0] for m in cs}
    states = {m: cs[m][1] for m in cs}
    lam = lambda r: float(np.max(np.linalg.eigvalsh(r)))
    F_e = lam(sum(probs[m] * states[m] for m in states))
    F_1 = sum((probs[(m1, 0)] + probs[(m1, 1)]) * lam(sum(probs[(m1, m2)] * states[(m1, m2)] for m2 in (0, 1))
                                                     / (probs[(m1, 0)] + probs[(m1, 1)])) for m1 in (0, 1))
    F_2 = sum((probs[(0, m2)] + probs[(1, m2)]) * lam(sum(probs[(m1, m2)] * states[(m1, m2)] for m1 in (0, 1))
                                                     / (probs[(0, m2)] + probs[(1, m2)])) for m2 in (0, 1))
    F_12 = sum(probs[m] * lam(states[m]) for m in states)
    return {"empty": F_e, "1": F_1, "2": F_2, "12": F_12}


# Eve's psi-independent strategies: what she applies to Bob's qubit given the bits she knows.
def eve_output(rhoB, m1, m2, K):
    if K == "empty":
        return rhoB
    if K == "1":
        U = np.linalg.matrix_power(X, m1)
    elif K == "2":
        U = np.linalg.matrix_power(Z, m2)
    else:
        U = np.linalg.matrix_power(Z, m2) @ np.linalg.matrix_power(X, m1)   # manuscript's U_{m1m2}
    return U @ rhoB @ U.conj().T


def Fbar_sim_for_psi(alpha, beta, gamma):
    """Fidelity <psi|out|psi> averaged over the unknown bits, for a FIXED psi (simulation)."""
    cs = simulate_conditional_states(alpha, beta, gamma)
    psi = psi_vec(alpha, beta)
    out = {}
    for K in ("empty", "1", "2", "12"):
        out[K] = sum(p * float(np.real(psi.conj() @ eve_output(r, m[0], m[1], K) @ psi))
                     for m, (p, r) in cs.items())
    return out


STABILIZER_STATES = [  # a qubit 2-design: exact Haar average of any degree-(2,2) polynomial in psi
    (1, 0), (0, 1),
    (1 / np.sqrt(2), 1 / np.sqrt(2)), (1 / np.sqrt(2), -1 / np.sqrt(2)),
    (1 / np.sqrt(2), 1j / np.sqrt(2)), (1 / np.sqrt(2), -1j / np.sqrt(2)),
]


def Fbar_sim_haar(gamma):
    """Exact Haar average of Fbar_K via the 6-state 2-design (simulation only)."""
    acc = {"empty": 0.0, "1": 0.0, "2": 0.0, "12": 0.0}
    for (a, b) in STABILIZER_STATES:
        f = Fbar_sim_for_psi(a, b, gamma)
        for K in acc:
            acc[K] += f[K] / len(STABILIZER_STATES)
    return acc


def Fbar_sim_haar_mc(gamma, n=4000, seed=0):
    """Monte-Carlo Haar average (independent check of the 2-design)."""
    rng = np.random.default_rng(seed)
    acc = {"empty": 0.0, "1": 0.0, "2": 0.0, "12": 0.0}
    for _ in range(n):
        v = rng.normal(size=2) + 1j * rng.normal(size=2)
        v /= np.linalg.norm(v)
        f = Fbar_sim_for_psi(v[0], v[1], gamma)
        for K in acc:
            acc[K] += f[K] / n
    return acc


# ----------------------------------------------------------------------------- leakage models (R4, k = 1)
def P_K(model, t, k=1.0, mu=0.5):
    """Knowledge-class probabilities P_K(t), exactly as in r4.tex Eqs. leak-indep ... leak-corr
    with k1 = k2 = k.  Returns dict with keys empty, 1, 2, 12 (arrays)."""
    t = np.asarray(t, dtype=float)
    e = np.exp(-k * t)
    if model == "independent":
        return {"empty": e * e, "1": (1 - e) * e, "2": e * (1 - e), "12": (1 - e) ** 2}
    if model == "sequential":
        P0 = e
        P1 = k * t * e
        return {"empty": P0, "1": P1, "2": np.zeros_like(t), "12": 1 - P0 - P1}
    if model == "burst":
        return {"empty": e, "1": np.zeros_like(t), "2": np.zeros_like(t), "12": 1 - e}
    if model == "correlated":
        P0 = np.exp(-(2 - mu) * k * t)
        P1 = np.exp(-mu * k * t) * (1 - np.exp(-(1 - mu) * k * t)) * np.exp(-(1 - mu) * k * t)
        P2 = P1.copy()
        return {"empty": P0, "1": P1, "2": P2, "12": 1 - P0 - P1 - P2}
    raise ValueError(model)


def expected_curves(model, t, alpha, beta, gamma, k=1.0, mu=0.5):
    """E[chi(t)], F^lam(t) (manuscript definition, corrected) and Fbar(t) (operational).
    gamma may be a scalar or an array of the same shape as t (time-coupled gamma(t))."""
    P = P_K(model, t, k, mu)
    chi = chi_K_closed(alpha, beta, gamma)
    Fl = F_lam_closed(alpha, beta, gamma)
    Fb = Fbar_closed(gamma)
    Echi = sum(P[K] * chi[K] for K in P)
    EFl = sum(P[K] * Fl[K] for K in P)
    EFb = sum(P[K] * Fb[K] for K in P)
    return Echi, EFl, EFb, P
