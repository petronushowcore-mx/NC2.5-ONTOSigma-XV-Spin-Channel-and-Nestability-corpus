"""nestability.py -- Proposition 2.4 (Nestability Margin) harness.

Stdlib only (fractions.Fraction). -O-safe (uses check(), not assert).

The nestability margin quantifies Theorem 1 (Nestability Criterion): a substrate is
nestable iff it carries a subcritical admissible trajectory -- a non-empty admissible
motion whose cumulative burden stays strictly below capacity. The margin

    mu_nest(S) = 1 - min{ Phi_S(gamma)/C_S : gamma admissible, |gamma| >= 1 }

is > 0 exactly when such a motion exists (Theorem 1), and mu_nest >= delta is a
robustness certificate: shifting each per-edge burden by less than delta*C_S
(burdens held >= 0; admissibility and skeleton unchanged) preserves nestability.
The margin is a FINITE-capacity instrument: C_S in (0, inf). At C_S = inf the
criterion degenerates (companion section 6) and the margin is not computed here --
nestability_margin raises, while is_nestable applies the degenerate reading.

Because Phi_S is monotone non-decreasing under trajectory extension, the minimum
burden over all non-empty admissible trajectories is attained at a single admissible
edge (a one-edge motion is the cheapest non-empty motion, and the first edge of any
admissible trajectory is itself admissible). So the margin is computed from the
admissible single edges -- no full trajectory enumeration is needed.

This module reuses a MINIMAL finite-state substrate (states / oriented edges /
per-edge burden / capacity / stay-in-K admissibility). It does NOT prove Theorem 1
(that is the companion); it ENFORCES the margin's declared relation to nestability
and SUPPLIES the falsifiers of essay section 6.

DRIFT LAYER (Definition 2.9 / Proposition 2.10). A declared drift class fixes a
window rule and sealed bands (a, eps): every lower window's prefix-difference
increment is >= a*C_i and every image window's is <= eps*C_S. Membership FORCES
first crossing within ceil(1/a) windows at image burden <= k*eps*C_S; when
N*eps < 1 the image stays strictly subcritical and the Independent-Exhaustion
verdict is reached -- derived from the DECLARED bands, which is where the
declaration lives (a stream measured outside its bands falsifies the class
membership, not the arithmetic). Increments are prefix differences of the
monotone burden; additivity of Phi is NOT assumed.
"""
import math
from fractions import Fraction


def check(cond, msg="check failed"):
    """Unconditional verification (assert-equivalent that survives `python -O`)."""
    if not cond:
        raise AssertionError(msg)


class Sub:
    """Minimal finite-state substrate.

    states : iterable of hashable states X
    edges  : list of oriented (tail, head) pairs; an edge is referenced by its index
    phi    : dict {edge_index: burden >= 0} -- a per-edge burden for EVERY edge
    C      : capacity, a Fraction > 0, or None for +inf
    K      : admissible-state subset of X (stay-in-K predicate); default = all of X
    A trajectory is admissible iff every state it visits lies in K.
    """
    def __init__(self, states, edges, phi, C, K=None):
        self.X = list(states)
        self.E = [tuple(e) for e in edges]
        xs = set(self.X)
        check(len(xs) == len(self.X), "duplicate states")
        for (u, v) in self.E:
            check(u in xs and v in xs, "edge endpoint not a state: %r" % ((u, v),))
        check(len(phi) == len(self.E), "phi must give a burden for every edge")
        self.phi = {}
        for i in range(len(self.E)):
            check(i in phi, "missing burden for edge %d" % i)
            b = Fraction(phi[i])
            check(b >= 0, "burden must be >= 0 on edge %d" % i)
            self.phi[i] = b
        check(C is None or Fraction(C) > 0, "capacity must be > 0 (or None for +inf)")
        self.C = None if C is None else Fraction(C)
        self.K = set(self.X if K is None else K)
        check(self.K <= xs, "K must be a subset of states")

    def admissible_edges(self):
        """Edge indices whose BOTH endpoints lie in K (the admissible single-edge motions)."""
        return [i for i, (u, v) in enumerate(self.E) if u in self.K and v in self.K]

    def min_nonempty_burden(self):
        """min{ Phi_S(gamma) : gamma admissible, |gamma| >= 1 }, or None if there is no
        non-empty admissible motion. Equal to the min burden over admissible single
        edges (Phi monotone under extension)."""
        adm = self.admissible_edges()
        if not adm:
            return None
        return min(self.phi[i] for i in adm)


def nestability_margin(S):
    """mu_nest(S) = 1 - min{Phi_S(gamma)/C_S : |gamma| >= 1}. Requires finite capacity
    C_S in (0, inf). Raises if C_S = +inf (the criterion degenerates) or if S has no
    non-empty admissible motion (the margin is then undefined)."""
    check(S.C is not None, "nestability margin requires finite capacity C_S (C_S = +inf degenerates)")
    m = S.min_nonempty_burden()
    check(m is not None, "no non-empty admissible motion: margin undefined")
    return Fraction(1) - m / S.C


def is_nestable(S):
    """Theorem 1: nestable iff a subcritical admissible trajectory exists. A substrate
    with NO non-empty admissible motion is not nestable (returned False, not an error).
    At C_S = +inf (S.C is None) the criterion DEGENERATES to "some non-empty admissible
    motion has finite burden" (companion section 6) -- every Fraction burden is finite,
    so any non-empty admissible motion qualifies; the MARGIN stays finite-capacity-only
    (nestability_margin raises on C_S = +inf)."""
    if S.min_nonempty_burden() is None:
        return False
    if S.C is None:
        return True   # degenerate C_S = +inf reading: finite burden < inf = C_S
    return nestability_margin(S) > 0


def perturb(S, delta_phi):
    """Return a copy of S with per-edge burdens shifted by delta_phi (dict
    {edge_index: shift}); burdens are clamped at 0 (>= 0 invariant)."""
    new_phi = {}
    for i in range(len(S.E)):
        new_phi[i] = max(Fraction(0), S.phi[i] + Fraction(delta_phi.get(i, 0)))
    return Sub(S.X, S.E, new_phi, S.C, S.K)


# -- drift layer (Definition 2.9 / Proposition 2.10) ------------------------
def in_drift_class(low_inc, up_inc, a, eps, C_i, C_S):
    """Definition 2.9 membership on declared per-window prefix-difference increments:
    every lower window >= a*C_i AND every image window <= eps*C_S. The window rule
    and the bands (a, eps) are sealed for the class (the one-rule-for-the-class
    discipline of Definition 3.2). Negative increments are malformed data (prefix
    differences of a monotone burden cannot be negative)."""
    a, eps, C_i, C_S = Fraction(a), Fraction(eps), Fraction(C_i), Fraction(C_S)
    check(a > 0, "drift class requires a > 0")
    check(eps >= 0, "drift class requires eps >= 0")
    check(C_i > 0 and C_S > 0, "drift class requires positive finite capacities")
    check(len(low_inc) == len(up_inc) and len(low_inc) >= 1,
          "paired non-empty window lists required")
    lows = [Fraction(x) for x in low_inc]
    ups = [Fraction(x) for x in up_inc]
    check(all(x >= 0 for x in lows) and all(x >= 0 for x in ups),
          "prefix differences of a monotone burden cannot be negative (malformed)")
    return all(x >= a * C_i for x in lows) and all(x <= eps * C_S for x in ups)


def crossing_window(low_inc, C_i):
    """First window index k (1-based) at which the cumulative lower burden reaches
    C_i (first crossing), or None if the stream never crosses."""
    total = Fraction(0)
    for k, x in enumerate(low_inc, start=1):
        total += Fraction(x)
        if total >= Fraction(C_i):
            return k
    return None


def forced_crossing(low_inc, up_inc, a, eps, C_i, C_S):
    """Proposition 2.10 on a drift-class member: returns (N, k_cross, upper_cum, ie).
    N = ceil(1/a) is the derived horizon; the crossing arrives at window k <= N
    (clause (i), enforced); the image burden accumulated through the crossing is
    <= k*eps*C_S (clause (ii), enforced); ie reports whether the image stays
    strictly subcritical at the crossing -- guaranteed whenever N*eps < 1 (clause
    (iii)), otherwise reported honestly from the data with no claim made."""
    check(in_drift_class(low_inc, up_inc, a, eps, C_i, C_S),
          "forced_crossing requires drift-class membership (Definition 2.9)")
    N = math.ceil(Fraction(1) / Fraction(a))
    check(len(list(low_inc)) >= N,
          "Proposition 2.10 applies to streams extending over at least N windows")
    k = crossing_window(low_inc, C_i)
    check(k is not None and k <= N, "Proposition 2.10(i): crossing within N windows")
    upper_cum = sum(Fraction(x) for x in up_inc[:k])
    check(upper_cum <= Fraction(k) * Fraction(eps) * Fraction(C_S),
          "Proposition 2.10(ii): image burden bounded by k*eps*C_S")
    return N, k, upper_cum, upper_cum < Fraction(C_S)


# -- self-test ------------------------------------------------------------
def selftest():
    results = []
    F = Fraction

    # --- N1: sealed core -> mu_nest = 0, NOT nestable (Counter-example 2.2) ---
    sealed = Sub(["a", "b"], [("a", "b")], {0: 1}, C=1)   # only motion saturates
    check(nestability_margin(sealed) == 0, "N1: sealed core margin must be 0")
    check(not is_nestable(sealed), "N1: sealed core must be NOT nestable")
    results.append("N1 sealed core: mu_nest = 0, not nestable: OK")

    # --- N2: self-loop subcritical -> mu_nest > 0, nestable (Proposition 2.3) ---
    loop = Sub(["x"], [("x", "x")], {0: 2}, C=5)          # one state, one edge, burden 2 < 5
    check(nestability_margin(loop) == F(3, 5), "N2: margin must be 3/5")
    check(is_nestable(loop), "N2: subcritical self-loop must be nestable")
    results.append("N2 self-loop subcritical: mu_nest = 3/5, nestable (one state): OK")

    # --- N3: zero-cost genuine motion -> mu_nest = 1, nestable ------------
    zero = Sub(["a", "b"], [("a", "b")], {0: 0}, C=1)     # non-empty motion, zero burden
    check(nestability_margin(zero) == 1, "N3: zero-cost margin must be 1")
    check(is_nestable(zero), "N3: zero-cost motion must be nestable")
    results.append("N3 zero-cost motion: mu_nest = 1, nestable (distinct from zero-length): OK")

    # --- N4: robustness -- perturbation < delta*C_S preserves nestability --
    # loop has mu_nest = 3/5, so delta = 3/5, delta*C_S = 3.
    check(nestability_margin(loop) == F(3, 5) and loop.C == 5, "N4 setup")
    within = perturb(loop, {0: 2})        # +2 < delta*C = 3  -> burden 4 < 5
    check(is_nestable(within) and nestability_margin(within) == F(1, 5),
          "N4: perturbation < delta*C must preserve nestability")
    at_bound = perturb(loop, {0: 3})      # +3 = delta*C (not < )  -> burden 5 = C, margin 0
    check(not is_nestable(at_bound) and nestability_margin(at_bound) == 0,
          "N4 teeth: at the delta*C boundary nestability is exactly lost")
    results.append("N4 robustness: perturb < delta*C_S preserves; at delta*C_S it is lost: OK")

    # --- N5: infinite capacity -- margin REJECTED, is_nestable degenerates ---
    inf_cap = Sub(["a", "b"], [("a", "b")], {0: 1}, C=None)
    try:
        nestability_margin(inf_cap)
        raise RuntimeError("nestability_margin must reject C_S = +inf")
    except AssertionError:
        pass
    # is_nestable handles C_S = +inf via the degenerate reading (companion §6):
    check(is_nestable(inf_cap), "N5: C=+inf with a non-empty motion is nestable (degenerate)")
    inf_no_motion = Sub(["a", "b"], [("a", "b")], {0: 1}, C=None, K={"a"})
    check(not is_nestable(inf_no_motion), "N5: C=+inf with NO admissible motion is not nestable")
    results.append("N5 C_S = +inf: margin rejected; is_nestable degenerate-reading: OK")

    # --- N6: no admissible motion -> not nestable; margin undefined -------
    # edge (a,b) but b not in K, so no admissible edge exists.
    no_motion = Sub(["a", "b"], [("a", "b")], {0: 1}, C=2, K={"a"})
    check(not is_nestable(no_motion), "N6: no admissible motion => not nestable")
    try:
        nestability_margin(no_motion)
        raise RuntimeError("nestability_margin must reject a substrate with no admissible motion")
    except AssertionError:
        pass
    results.append("N6 no admissible motion: not nestable, margin undefined: OK")

    # --- N8: autonomy ladder -- the fabricated carrier bears NO witness class ---
    # Theorem 1's minimal construction takes the carrier of a SIMPLE subcritical
    # trajectory: a path graph, b1 = 0, so it cannot carry a witness-bearing
    # recurrence class (condition (iii) of autonomous nestability, Definition 2.5)
    # -- formally nestable, NOT autonomous. A declared CYCLIC lower (b1 = 1) can.
    import graph_hodge as _gh
    path_carrier = _gh.Graph(["s0", "s1"], [("s0", "s1")])       # carrier of a simple gamma
    check(path_carrier.b1() == 0, "N8: fabricated path carrier has b1 = 0 (no witness class)")
    cyclic_lower = _gh.Graph(["r0", "r1"], [("r0", "r1"), ("r1", "r0")])
    check(cyclic_lower.b1() == 1, "N8: a declared cyclic lower has b1 = 1 (witness-capable)")
    check(len(cyclic_lower.fundamental_cycles()) == 1
          and _gh.period({0: Fraction(1), 1: Fraction(1)}, cyclic_lower.fundamental_cycles()[0]) != 0,
          "N8: the cyclic lower carries a witness-bearing pairing")
    results.append("N8 autonomy ladder: fabricated path-carrier witness-free; cyclic lower witness-capable: OK")

    # --- N9: margin dominance (Prop 2.7) -- mu*C bounds every image slack ----
    # For ANY nested pair's IE witness, the image trajectory is a non-empty admissible
    # motion, so its upper slack tau_S = C_S - Phi_S(image) is <= C_S - min = mu*C.
    two9 = Sub(["a", "b", "c"], [("a", "b"), ("a", "c")], {0: 1, 1: 3}, C=5)
    muC = nestability_margin(two9) * two9.C
    check(muC == F(4), "N9 setup: mu*C = 5 - 1 = 4")
    tau_expensive = two9.C - two9.phi[1]      # image = the expensive edge
    tau_cheapest = two9.C - two9.phi[0]       # image = the cheapest edge
    check(tau_expensive == 2 < muC, "N9: expensive-image slack strictly below mu*C")
    check(tau_cheapest == 4 == muC, "N9: cheapest-image slack ATTAINS mu*C (bound tight)")
    results.append("N9 margin dominance: mu*C >= every image slack; tight on the cheapest edge: OK")

    # --- N7: margin tracks the CHEAPEST admissible edge (monotonicity) ----
    # two edges, burdens 4 and 1; the min (1) sets the margin, not the max.
    two = Sub(["a", "b", "c"], [("a", "b"), ("a", "c")], {0: 4, 1: 1}, C=5)
    check(nestability_margin(two) == F(4, 5) and is_nestable(two),
          "N7: margin uses the cheapest admissible edge (1/5 burden -> 4/5 margin)")
    # teeth: if the expensive edge alone existed, it would saturate and margin -> 0
    expensive = Sub(["a", "b"], [("a", "b")], {0: 5}, C=5)
    check(nestability_margin(expensive) == 0 and not is_nestable(expensive),
          "N7 teeth: a lone saturating edge gives margin 0")
    results.append("N7 margin = cheapest admissible edge (not the mean/max): OK")

    # --- N10: forced IE-crossing (Definition 2.9 / Proposition 2.10) -------
    # a = 1/3 (horizon N = 3), eps = 1/10, C_i = 6, C_S = 10: lower windows at the
    # band (a*C_i = 2 each), image windows at the band (eps*C_S = 1 each).
    lows, ups = [F(2), F(2), F(2)], [F(1), F(1), F(1)]
    check(in_drift_class(lows, ups, F(1, 3), F(1, 10), 6, 10),
          "N10: the band fixture is in the drift class")
    check(forced_crossing(lows, ups, F(1, 3), F(1, 10), 6, 10) == (3, 3, F(3), True),
          "N10: crossing at window 3 = N, image burden 3 < 10, IE reached")
    # steeper (non-constant) drift crosses BEFORE the horizon:
    N2, k2, _, ie2 = forced_crossing([F(4), F(4), F(2)], [F(1)] * 3, F(1, 3), F(1, 10), 6, 10)
    check(N2 == 3 and k2 == 2 and ie2, "N10: steeper drift crosses before the horizon")
    # tie to the budget machinery: the image's remaining slack is genuine budget room
    upper10 = Sub(["u0", "u1"], [("u0", "u1")], {0: 3}, C=10)
    check(is_nestable(upper10), "N10: the crossed image is a subcritical motion (Theorem 1 link)")
    results.append("N10 forced crossing: k <= ceil(1/a), image <= k*eps*C_S, IE reached: OK")

    # --- N11: the drift band is load-bearing --------------------------------
    check(not in_drift_class([F(2), F(2), F(1)], [F(1)] * 3, F(1, 3), F(1, 10), 6, 10),
          "N11: one lower window below a*C_i leaves the class")
    check(crossing_window([F(2), F(2), F(1)], 6) is None,
          "N11: without the band the stream can fail to cross by any horizon")
    try:
        in_drift_class([F(2), F(-1)], [F(1), F(1)], F(1, 3), F(1, 10), 6, 10)
        raise RuntimeError("negative increments must be rejected")
    except AssertionError:
        pass
    try:
        in_drift_class([F(2)], [F(1)], 0, F(1, 10), 6, 10)
        raise RuntimeError("a = 0 must be rejected")
    except AssertionError:
        pass
    try:
        forced_crossing([F(2), F(2)], [F(1), F(1)], F(1, 3), F(1, 10), 6, 10)
        raise RuntimeError("streams shorter than N windows are outside Prop 2.10's hypothesis")
    except AssertionError:
        pass
    results.append("N11 drift band load-bearing: sub-band exits the class; malformed rejected: OK")

    # --- N12: N*eps >= 1 -- clause (iii) honestly withheld ------------------
    # eps = 2/5 gives N*eps = 6/5 >= 1; image windows at the band accumulate
    # 12 >= C_S = 10 by the crossing -- subcriticality is NOT concluded.
    check(forced_crossing([F(2)] * 3, [F(4)] * 3, F(1, 3), F(2, 5), 6, 10)
          == (3, 3, F(12), False),
          "N12: at N*eps >= 1 the image can exhaust -- IE is not claimed")
    results.append("N12 boundary N*eps >= 1: subcriticality honestly withheld: OK")

    return results


if __name__ == "__main__":
    for line in selftest():
        print(line)
    print("nestability selftest: 12/12 OK")
