# -*- coding: utf-8 -*-
"""Numerical checks of Proposition 2 (best use of a depolarizing memory), Supplementary Note 7.

1. Dual certificate: for every lambda in [1/2, 1], Z (x) I - W >= 0 with Tr Z = 3, where
   W = |v><v| + I (x) diag(lambda, 1 - lambda), |v> = sqrt(lambda)|00> + sqrt(1 - lambda)|11>, and
   Z = diag(3 lambda, 3 - 3 lambda) for lambda <= 3/4, Z = diag(3 - lambda, lambda) for lambda >= 3/4.
2. Direct optimization: the average fidelity of sum_k R_k o D_p o A_k over instruments {A_k} (Kraus form, several
   outcomes) and outcome-dependent channels R_k, from random starts, compared with max{(1 + p)/2, 2/3}.
Average fidelity of a qubit channel C: (2 F_e + 1)/3 with F_e = <Phi+| (id x C)(Phi+) |Phi+>.
Usage: python optimal_memory_check.py [--quick]
"""
import sys
import numpy as np
from scipy.optimize import minimize

I2 = np.eye(2)
PHI_V = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
PHI = np.outer(PHI_V, PHI_V.conj())


def certificate(n=2001):
    worst = np.inf
    for lam in np.linspace(0.5, 1.0, n):
        v = np.zeros(4); v[0] = np.sqrt(lam); v[3] = np.sqrt(1 - lam)
        W = np.outer(v, v) + np.kron(I2, np.diag([lam, 1 - lam]))
        Z = np.diag([3 * lam, 3 - 3 * lam]) if lam <= 0.75 else np.diag([3 - lam, lam])
        assert abs(np.trace(Z) - 3) < 1e-12
        worst = min(worst, np.linalg.eigvalsh(np.kron(Z, I2) - W).min())
    return worst


def inv_sqrt(S):
    w, U = np.linalg.eigh(S)
    return U @ np.diag(np.maximum(w, 1e-12) ** -0.5) @ U.conj().T


def avg_fidelity(x, p, nk, r, s):
    n1 = nk * r * 8
    K = (x[:n1:2] + 1j * x[1:n1:2]).reshape(nk, r, 2, 2)
    L = (x[n1::2] + 1j * x[n1 + 1::2]).reshape(nk, s, 2, 2)
    K = K @ inv_sqrt(np.einsum("kjab,kjac->bc", K.conj(), K))          # instrument: sum of K^dag K = I
    Fe = 0.0
    for k in range(nk):
        Lk = L[k] @ inv_sqrt(np.einsum("jab,jac->bc", L[k].conj(), L[k]))  # channel R_k: trace preserving
        X = sum(np.kron(I2, K[k, j]) @ PHI @ np.kron(I2, K[k, j]).conj().T for j in range(r))
        X = p * X + (1 - p) * np.kron(np.einsum("ijkj->ik", X.reshape(2, 2, 2, 2)), I2 / 2)   # memory D_p
        Y = sum(np.kron(I2, Lk[i]) @ X @ np.kron(I2, Lk[i]).conj().T for i in range(s))
        Fe += np.real(PHI_V.conj() @ Y @ PHI_V)
    return (2 * Fe + 1) / 3


def optimum(p, nk, r=2, s=4, starts=10, seed=0):
    rng = np.random.default_rng(seed)
    n = nk * r * 8 + nk * s * 8
    best = 0.0
    for _ in range(starts):
        res = minimize(lambda x: -avg_fidelity(x, p, nk, r, s), rng.normal(size=n), method="L-BFGS-B",
                       options={"maxiter": 800})
        best = max(best, -res.fun)
    return best


if __name__ == "__main__":
    quick = "--quick" in sys.argv
    print("dual certificate: smallest eigenvalue of Z(x)I - W over lambda in [1/2, 1]: %.2e" % certificate())
    ps = [0.2, 1 / 3, 0.5] if quick else [0.1, 0.25, 0.3, 1 / 3, 0.4, 0.5, 0.7, 0.9]
    for p in ps:
        f = optimum(p, nk=4 if quick else 6, starts=3 if quick else 10)
        ref = max((1 + p) / 2, 2 / 3)
        print("p = %.4f   best found %.6f   max{(1+p)/2, 2/3} = %.6f   difference %+.1e" % (p, f, ref, f - ref))
