"""boundary_witness.py -- Proposition 3.7 (Boundary-Witness Compatibility) harness.

On a DECLARED boundary-witness-compatible subclass:
  - a single graph map  rho: U -> M^carrier  (vmap + emap),
  - a declared oriented, NON-contractible upper cycle Gamma with
        (H-a)  rho_*[Gamma] = [gamma_i]   in H_1(M)   (oriented, degree 1),
  - an envelope realisation omega_tilde on U with
        (H-b)  [omega_tilde] = rho^*[eta]  in H^1(U),
the net-circulation  sigma^(M) = <omega_tilde, Gamma>  EQUALS the transported
witness period  <eta, gamma_i>  (Proposition 3.7). Proof (companion): mode+closed =>
sigma = <omega_tilde,Gamma> = <rho^*eta,Gamma> (H-b) = <eta,rho_*Gamma> (Lemma 3.6,
transpose-adjunction) = <eta,gamma_i> (H-a).

This module CHECKS the declared compatibility data and, when it holds, verifies the
period identity; it REJECTS declarations violating (H-a) (wrong degree / class) or
(H-b) ([omega_tilde] != rho^*[eta]) or the non-contractible-cycle requirement. It
does NOT prove XV.2 -- M^cost = c*|sigma| remains a declared structural law; only
the *net-circulation* sigma is evaluated as the transported witness period here.

Stdlib only, -O-safe. Reuses the hardened graph_hodge cohomology core.
"""
from fractions import Fraction
import graph_hodge as gh
from graph_hodge import (Graph, period, induced_pullback, induced_pushforward,
                         cycle_class_coeffs, check)


def cohomologous(U, a, b):
    """[a] = [b] in H^1(U): a-b has zero period on every cycle (a-b is a coboundary)."""
    for z in U.fundamental_cycles():
        if period(a, z) != period(b, z):
            return False
    return True


def is_noncontractible_cycle(U, Gamma):
    """True iff Gamma is a genuine 1-cycle of U with NON-zero homology class
    (boundary-layer-admissible requires this; a contractible / null-homologous
    Gamma, or a 1-dimensional / tree envelope with b1=0, is excluded)."""
    if U.b1() == 0:
        return False
    try:
        cls = cycle_class_coeffs(U, Gamma)     # raises if Gamma is not a cycle
    except AssertionError:
        return False
    return any(c != 0 for c in cls.values())


def check_H_a(M, rho_emap, Gamma, gamma_i):
    """(H-a): rho_*[Gamma] = [gamma_i] as oriented, degree-1 homology classes."""
    pushed = induced_pushforward(rho_emap, Gamma)
    cls_p = cycle_class_coeffs(M, pushed)
    cls_g = cycle_class_coeffs(M, gamma_i)
    check(cls_p == cls_g,
          "H-a fails: rho_*[Gamma]=%r != [gamma_i]=%r (need oriented degree-1)" % (cls_p, cls_g))


def check_H_b(U, rho_emap, eta, omega_tilde):
    """(H-b): [omega_tilde] = rho^*[eta] in H^1(U)."""
    pulled = induced_pullback(rho_emap, eta)
    check(cohomologous(U, omega_tilde, pulled),
          "H-b fails: [omega_tilde] != rho^*[eta] (not cohomologous on U)")


def boundary_witness_sigma(M, U, rho_vmap, rho_emap, Gamma, gamma_i, eta, omega_tilde):
    """Validate the compatible-subclass declaration and return the forced sigma^(M)
    = <omega_tilde, Gamma>, asserting it equals the transported witness period
    <eta, gamma_i> (Proposition 3.7). Raises on any violated hypothesis.

    gamma_i must be THE recurrence cycle carrying the witness (Definition 3.5):
    a NON-ZERO class in H_1(M) with <eta, gamma_i> != 0. A zero gamma_i (with a
    collapsing rho) would satisfy H-a/H-b vacuously and fake the identity as 0 = 0."""
    U.check_graph_map(M, rho_vmap, rho_emap)          # rho really is a graph map U->M
    check(is_noncontractible_cycle(U, Gamma),
          "Gamma is not a non-contractible 1-cycle of U (not boundary-layer-admissible)")
    cls_g = cycle_class_coeffs(M, gamma_i)            # raises if gamma_i is not a cycle
    check(any(c != 0 for c in cls_g.values()),
          "gamma_i must be a NON-ZERO class in H_1(M) (a zero class trivialises H-a)")
    check(period(eta, gamma_i) != 0,
          "gamma_i must be witness-bearing: <eta, gamma_i> != 0 (Definition 3.5)")
    check_H_a(M, rho_emap, Gamma, gamma_i)
    check_H_b(U, rho_emap, eta, omega_tilde)
    sigma = period(omega_tilde, Gamma)
    forced = period(eta, gamma_i)                     # <eta, gamma_i>, the witness period
    check(sigma == forced,
          "Proposition 3.7 identity fails: sigma=%s != transported witness period=%s" % (sigma, forced))
    return sigma


# ---- fixtures -----------------------------------------------------------
def _triangle():
    """M = C_3 (lower carrier): vertices b0,b1,b2; oriented triangle."""
    V = ["b0", "b1", "b2"]
    E = [("b0", "b1"), ("b1", "b2"), ("b2", "b0")]
    return Graph(V, E)


def _prism():
    """U = triangular prism retracting to the bottom triangle M by collapsing verticals."""
    V = ["b0", "b1", "b2", "t0", "t1", "t2"]
    E = [("b0", "b1"), ("b1", "b2"), ("b2", "b0"),    # 0,1,2 bottom
         ("t0", "t1"), ("t1", "t2"), ("t2", "t0"),    # 3,4,5 top
         ("b0", "t0"), ("b1", "t1"), ("b2", "t2")]    # 6,7,8 verticals
    U = Graph(V, E)
    vmap = {"b0": "b0", "b1": "b1", "b2": "b2", "t0": "b0", "t1": "b1", "t2": "b2"}
    emap = {0: [(0, +1)], 1: [(1, +1)], 2: [(2, +1)],
            3: [(0, +1)], 4: [(1, +1)], 5: [(2, +1)],
            6: [], 7: [], 8: []}
    Gamma_top = {3: +1, 4: +1, 5: +1}
    return U, vmap, emap, Gamma_top


def _cycle(n, label):
    V = ["%s%d" % (label, i) for i in range(n)]
    E = [(V[i], V[(i + 1) % n]) for i in range(n)]
    return Graph(V, E)


def selftest():
    results = []
    one = Fraction(1)

    # --- Q1: compatible prism instance -> sigma = transported witness period ---
    M = _triangle()
    gamma_i = M.fundamental_cycles()[0]                # the triangle, {0:1,1:1,2:1}
    eta = {0: one, 1: one, 2: one}                     # angular; witness period = 3
    U, vmap, emap, Gamma = _prism()
    omega_tilde = induced_pullback(emap, eta)          # a valid rho^*eta realisation
    sigma = boundary_witness_sigma(M, U, vmap, emap, Gamma, gamma_i, eta, omega_tilde)
    check(sigma == period(eta, gamma_i) == 3, "Q1: sigma must equal witness period 3, got %s" % sigma)
    results.append("Q1 compatible prism: sigma = transported witness period (3): OK")

    # --- Q2: degree-m cover REJECTED by H-a (rho_*[Gamma] = m[gamma_i], m!=1) ---
    k, m = 3, 2
    Mk = _cycle(k, "c")
    gk = Mk.fundamental_cycles()[0]
    etak = {e: one for e in range(k)}
    Umk = _cycle(m * k, "d")
    emap_cov = {j: [(j % k, +1)] for j in range(m * k)}
    vmap_cov = {"d%d" % j: "c%d" % (j % k) for j in range(m * k)}
    Gam_cov = Umk.fundamental_cycles()[0]
    ot_cov = induced_pullback(emap_cov, etak)          # H-b holds by construction
    try:
        boundary_witness_sigma(Mk, Umk, vmap_cov, emap_cov, Gam_cov, gk, etak, ot_cov)
        raise RuntimeError("degree-2 cover should be rejected by H-a")
    except AssertionError as e:
        check("H-a" in str(e), "Q2 must fail at H-a, got: %s" % e)
    # and the identity WOULD break without H-a (sigma = m*period != period):
    check(period(ot_cov, Gam_cov) == m * period(etak, gk),
          "Q2 teeth: without H-a sigma=m*period; H-a is load-bearing")
    results.append("Q2 degree-2 cover rejected by H-a (H-a load-bearing): OK")

    # --- Q3: H-b violation REJECTED (omega_tilde not cohomologous to rho^*eta) ---
    ot_bad = dict(omega_tilde)
    ot_bad[3] = ot_bad[3] + 1                           # perturb one top edge: no longer rho^*eta
    try:
        boundary_witness_sigma(M, U, vmap, emap, Gamma, gamma_i, eta, ot_bad)
        raise RuntimeError("H-b violation should be rejected")
    except AssertionError as e:
        check("H-b" in str(e), "Q3 must fail at H-b, got: %s" % e)
    results.append("Q3 H-b violation (non-cohomologous omega_tilde) rejected: OK")

    # --- Q4: contractible / tree envelope REJECTED (no non-contractible cycle) ---
    tree = Graph(["p", "q", "r"], [("p", "q"), ("q", "r")])   # b1 = 0
    check(not is_noncontractible_cycle(tree, {0: 1}), "Q4a: tree envelope must be rejected")
    # a non-tree U but a NULL-homologous declared Gamma (a back-and-forth chain) also rejected
    check(not is_noncontractible_cycle(U, {6: +1}), "Q4b: a single tree-edge chain is not a cycle -> rejected")
    results.append("Q4 contractible/1D envelope + null Gamma rejected: OK")

    # --- Q5: ZERO / non-witness-bearing gamma_i REJECTED (anti-vacuous H-a) ---
    # a rho collapsing everything + gamma_i = {} satisfies H-a/H-b vacuously (0 = 0);
    # the declaration must be rejected: gamma_i is not a witness-bearing class.
    vmap0 = {v: "b0" for v in U.V}
    emap0 = {i: [] for i in range(len(U.E))}
    try:
        boundary_witness_sigma(M, U, vmap0, emap0, Gamma, {}, eta, {})
        raise RuntimeError("zero gamma_i with collapsing rho must be rejected")
    except AssertionError as e:
        check("NON-ZERO" in str(e) or "witness-bearing" in str(e),
              "Q5 must fail at the gamma_i guard, got: %s" % e)
    # a genuine cycle that is eta-orthogonal must also be rejected (witness-bearing)
    eta_perp = {0: one, 1: -one, 2: Fraction(0)}       # <eta_perp, triangle> = 0
    check(period(eta_perp, gamma_i) == 0, "Q5 setup: eta_perp orthogonal to gamma_i")
    ot_perp = induced_pullback(emap, eta_perp)
    try:
        boundary_witness_sigma(M, U, vmap, emap, Gamma, gamma_i, eta_perp, ot_perp)
        raise RuntimeError("non-witness-bearing gamma_i must be rejected")
    except AssertionError as e:
        check("witness-bearing" in str(e), "Q5b must fail at witness-bearing, got: %s" % e)
    results.append("Q5 zero / non-witness-bearing gamma_i rejected (anti-vacuous): OK")

    # --- Q6: H-b is COHOMOLOGICAL equality, not pointwise (positive control) ---
    # omega_tilde + df is cohomologous to rho^*eta but NOT pointwise equal; it must
    # PASS and give the same sigma (Lemma 3.3 gauge-invariance of the period).
    f = {"b0": Fraction(0), "b1": Fraction(5), "b2": Fraction(-2),
         "t0": Fraction(1), "t1": Fraction(3), "t2": Fraction(4)}
    df = gh.coboundary(U, f)
    ot_shift = {e: omega_tilde.get(e, Fraction(0)) + df.get(e, Fraction(0))
                for e in range(len(U.E))}
    check(ot_shift != induced_pullback(emap, eta), "Q6 setup: shifted form differs pointwise")
    sigma6 = boundary_witness_sigma(M, U, vmap, emap, Gamma, gamma_i, eta, ot_shift)
    check(sigma6 == 3, "Q6: cohomologous-but-not-equal realisation must pass with sigma=3, got %s" % sigma6)
    results.append("Q6 H-b cohomological (pointwise-shifted realisation passes, same sigma): OK")

    # --- Q7: quantisation (Prop 3.11) -- integral eta => sigma integer != 0 ---
    # the prism instance: eta integer-valued (integral), gamma_i integral -> sigma = 3,
    # an integer with |sigma| >= 1: M = c*|sigma| lies on the lattice {c, 2c, ...}.
    check(sigma == 3 and sigma == int(sigma) and abs(sigma) >= 1,
          "Q7: integral witness gives an integer sigma with |sigma| >= 1 (floor)")
    # the integrality hypothesis is LOAD-BEARING: a half-integer eta (still a valid
    # declaration) yields sigma = 3/2 -- off the integer lattice; Prop 3.11 does not
    # apply to it, and the M-only lattice falsifier must not be quoted for such data.
    eta_half = {0: Fraction(1, 2), 1: Fraction(1, 2), 2: Fraction(1, 2)}
    ot_half = induced_pullback(emap, eta_half)
    sigma_half = boundary_witness_sigma(M, U, vmap, emap, Gamma, gamma_i, eta_half, ot_half)
    check(sigma_half == Fraction(3, 2) and sigma_half != int(sigma_half),
          "Q7: half-integer eta gives non-integer sigma -- integrality is load-bearing")
    results.append("Q7 quantisation: integral eta -> integer sigma (floor >= 1); hypothesis load-bearing: OK")

    return results


if __name__ == "__main__":
    for line in selftest():
        print(line)
    print("boundary_witness selftest: 7/7 OK")
