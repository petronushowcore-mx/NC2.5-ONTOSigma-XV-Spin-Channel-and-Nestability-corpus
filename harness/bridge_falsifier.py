"""bridge_falsifier.py -- Proposition 3.8 (Multi-event c-consistency falsifier) harness.

Stdlib only (fractions.Fraction). -O-safe (uses check(), not assert).

The Bridge Law  M^cost = c * |sigma^(M)|  is a DECLARED structural law (companion
Theorem 2 / §3.2). This module enforces its EMPIRICAL-mode falsifier, NOT the law:

  - A SINGLE event never falsifies the law (c := M/|sigma| fits any one event).
  - Empirical content requires >= 2 events of one declared class. Two distinct
    tests: under a SEALED c the law fails iff some event misfits it (clause (a));
    the free-c CLASS falsifier declares FALSIFIED iff NO c > 0 fits every event
    within eps (clause (b)).
  - Discipline: c is sealed before the events it is scored against -- declared in
    advance (fully sealed), or fitted on calibration events, frozen, and holdout-tested
    on disjoint events (companion Prop 3.8's two admissible protocols); never fitted
    from the pair being scored.
  - Zero-spin control (norm mode): an event with |sigma| = 0 but M > eps falsifies
    (no c reaches it); with M <= eps it constrains nothing.

An `event` is a pair (M, abs_sigma) of non-negative Fractions: M the measured
maintenance cost -- scored net of the deployment's declared spin-independent
baseline, per the sealed baseline discipline of companion §3.2 / Proposition 3.8
-- abs_sigma = |sigma^(M)| measured under the declared boundary functional. This module does not measure anything; it decides consistency of a set
of declared measurements with a single proportionality constant.

The TWO-CHANNEL layer (companion Proposition 3.15) extends the discipline to the
jointly-declared law M = c_H*|sigma_H| + c_L*Lambda_loc of Remark 3.10: a
two-channel `event3` is a triple (M, abs_sigma_H, Lambda) of non-negative
Fractions; feasibility of a sealed pair (c_H, c_L) >= 0 is decided exactly over
Fraction by two-variable elimination with a self-verifying witness. Power
structure: two independent-reading events falsify only through positivity;
genuine overdetermination begins at three events; with Lambda == 0 the verdict
reduces to the single-channel discipline above (verdict-exact whenever some
M_j > eps -- Proposition 3.15(d)'s agreement condition).
"""
from fractions import Fraction


def check(cond, msg="check failed"):
    """Unconditional verification (assert-equivalent that survives `python -O`)."""
    if not cond:
        raise AssertionError(msg)


def _MS(event):
    M, s = Fraction(event[0]), Fraction(event[1])
    check(M >= 0 and s >= 0, "event (M, |sigma|) must be non-negative: %r" % (event,))
    return M, s


def _eps(eps):
    eps = Fraction(eps)
    check(eps >= 0, "tolerance eps must be >= 0 (Proposition 3.8)")
    return eps


def fits(event, c, eps):
    """|M - c*|sigma|| <= eps for one event under the constant c."""
    M, s = _MS(event)
    return abs(M - Fraction(c) * s) <= _eps(eps)


def consistent_with_sealed_c(events, c, eps):
    """Honest deployment test: with c SEALED BEFORE measurement (an input, not fitted),
    the law holds on `events` iff every event fits within eps. Returns True iff not
    falsified under this sealed c."""
    check(Fraction(c) > 0, "sealed c must be > 0")
    eps = _eps(eps)
    check(len(events) >= 1, "need at least one event")
    return all(fits(e, c, eps) for e in events)


def feasible_c_interval(events, eps):
    """The set of constants c > 0 fitting EVERY event within eps. Returns None iff
    that set is EMPTY (genuinely infeasible: a zero-|sigma| event with M > eps, or the
    per-event intervals over positive-|sigma| events intersect emptily in (0, inf)).
    Otherwise returns (lo, hi): the feasible set is {c > 0 : lo <= c <= hi}, with
    hi = None meaning UNBOUNDED above -- in particular (0, None) when no positive-
    |sigma| event constrains c at all (every c > 0 fits; such a set is 'not a test',
    but it is NOT falsified). A zero-|sigma| event with M <= eps imposes no constraint."""
    eps = _eps(eps)
    lo = Fraction(0)          # c must be > 0
    hi = None                 # unbounded above until a positive-|sigma| event bounds it
    for e in events:
        M, s = _MS(e)
        if s == 0:
            if M > Fraction(eps):
                return None   # c*0 = 0 cannot reach M > eps -> infeasible (zero-spin control)
            continue          # M <= eps: any c fits this event
        c_lo = (M - Fraction(eps)) / s
        c_hi = (M + Fraction(eps)) / s
        lo = max(lo, c_lo)
        hi = c_hi if hi is None else min(hi, c_hi)
    if hi is None:
        return (lo, None)     # no positive-|sigma| event: every c > 0 fits (unbounded,
        #                       'not a test' -- distinct from infeasible, which is None)
    if lo > hi or hi <= 0:
        return None
    return (lo, hi)


def falsified_over_class(events, eps):
    """Class-level falsifier: with a sealed-but-unknown c, is there ANY c > 0 fitting
    every event within eps? The law is FALSIFIED on the class iff NO such c exists.
    Requires >= 2 events (a single positive-|sigma| event is always fittable). An event
    set with no positive-|sigma| event (all zero-circulation within tolerance) does not
    constrain c and is NOT falsified ('not a test'). Returns True iff FALSIFIED."""
    check(len(events) >= 2, "multi-event falsifier requires >= 2 events (one event always fits)")
    # a single (M>0, |sigma|>0) event alone is trivially fittable; enforce the >=2 discipline
    return feasible_c_interval(events, eps) is None


def quantised_consistent(Ms, c, eps):
    """The M-ONLY lattice falsifier (companion Proposition 3.11 corollary): under the
    quantisation hypotheses (compatible subclass, net-circulation mode, integral
    primitive-normalized witness) every true cost is c*k for an integer k >= 1, so
    each measured M must lie within eps of the lattice {c, 2c, 3c, ...} -- no sigma
    measurement needed. Below-floor readings (M < c - eps) falsify outright.
    POWER: the lattice (integer-spacing) discrimination works only for eps < c/2 (at
    eps >= c/2 every reading above the floor is within eps of the lattice); the FLOOR
    clause alone retains power for any eps < c. This implementation rejects
    eps >= c/2 outright as a CONSERVATIVE design choice (full-power regime only)."""
    c = Fraction(c)
    check(c > 0, "quantum c must be > 0")
    eps = _eps(eps)
    check(eps < c / 2, "lattice test requires eps < c/2 (otherwise vacuous)")
    for M in Ms:
        M = Fraction(M)
        check(M >= 0, "measured M must be >= 0")
        k = round(M / c)
        if k < 1 or abs(M - c * k) > eps:
            return False          # off-lattice or below the floor: FALSIFIED
    return True


def floor_consistent(readings, c1, eps):
    """The DERIVED-floor sanity gate (companion Proposition 3.14 corollary). On a
    declared locus with l1 floor-constant c1 (= min_e w(e) for a unit-multiplicity
    cycle), EVERY realisation carrying period sigma has norm-channel reading
    Lambda >= c1 * |sigma| -- a theorem, not a declaration. A measured pair
    (Lambda, |sigma|) with Lambda < c1*|sigma| - eps is therefore IMPOSSIBLE for any
    realisation: it falsifies the measurement typing or the locus declaration itself,
    with no constant c, no lattice hypothesis, and no sealed law needed.
    `readings` is an iterable of (Lambda, abs_sigma) pairs of FIELD readings, both
    non-negative and both read off ONE realisation on ONE declared locus -- never an
    M^cost measurement in place of Lambda, and never Lambda of one realisation paired
    with sigma of another (cross-pairing voids the gate: the floor relates the two
    readings of a single field). Returns True iff every pair respects the floor
    within eps."""
    c1 = Fraction(c1)
    check(c1 > 0, "floor constant c1 must be > 0 (a declared-locus geometry datum)")
    eps = _eps(eps)
    for r in readings:
        lam, s = Fraction(r[0]), Fraction(r[1])
        check(lam >= 0 and s >= 0,
              "reading (Lambda, |sigma|) must be non-negative: %r" % (r,))
        if lam < c1 * s - eps:
            return False              # impossible reading: below the derived floor
    return True


def test_sealed_c_on_events(sealed_c, events, eps):
    """Score an already-frozen c on an event set. The HOLDOUT DISCIPLINE is the
    caller's: this function cannot see the calibration set, so disjointness (c never
    scored against the events that fitted it) is a protocol obligation, not machine-
    checked here -- named accordingly. The law survives iff the sealed c fits every
    supplied event within eps."""
    return consistent_with_sealed_c(events, sealed_c, eps)


# -- two-channel feasibility (Proposition 3.15) ----------------------------
def _MSL(event3):
    M, s, lam = Fraction(event3[0]), Fraction(event3[1]), Fraction(event3[2])
    check(M >= 0 and s >= 0 and lam >= 0,
          "two-channel event (M, |sigma_H|, Lambda) must be non-negative: %r" % (event3,))
    return M, s, lam


def _two_channel_constraints(events3, eps):
    """The half-plane system of the two-channel law: rows (a, b, c) meaning
    a*c_H + b*c_L <= c. Each event contributes its band's two edges; the closed
    non-negative quadrant contributes c_H >= 0 and c_L >= 0 (the degenerations
    c_L = 0 / c_H = 0 are the single-functional laws, so the quadrant is CLOSED)."""
    eps = _eps(eps)
    cons = []
    for (M, s, lam) in map(_MSL, events3):
        cons.append((s, lam, M + eps))
        cons.append((-s, -lam, -(M - eps)))
    cons.append((Fraction(-1), Fraction(0), Fraction(0)))
    cons.append((Fraction(0), Fraction(-1), Fraction(0)))
    return cons


def feasible_two_channel(events3, eps):
    """Proposition 3.15(b): the set of sealed pairs (c_H, c_L) >= 0 fitting EVERY
    event within eps -- the intersection of the event bands with the closed
    non-negative quadrant, a convex polygon. Decided EXACTLY over Fraction by
    two-variable (Fourier-Motzkin) elimination of c_L. Returns None iff the set is
    EMPTY; otherwise a WITNESS pair (c_H, c_L), substituted back into every
    constraint before being returned (self-verifying). Degeneration note (Prop
    3.15(d)): with Lambda == 0 throughout and some M_j > eps, the c_H-projection
    equals the single-channel feasible set of Proposition 3.8; at the degenerate
    corner (eps = 0 and every M_j = 0) it additionally contains the boundary point
    c_H = 0, which the single-channel reading's c > 0 excludes."""
    cons = _two_channel_constraints(events3, eps)
    upper = [(a, b, c) for (a, b, c) in cons if b > 0]   # c_L <= (c - a*c_H)/b
    lower = [(a, b, c) for (a, b, c) in cons if b < 0]   # c_L >= (c - a*c_H)/b
    oned = [(a, c) for (a, b, c) in cons if b == 0]
    # eliminate c_L: each (lower, upper) pairing projects to
    # (bu*al - bl*au) * c_H <= bu*cl - bl*cu   (bu > 0 > bl)
    for (au, bu, cu) in upper:
        for (al, bl, cl) in lower:
            oned.append((bu * al - bl * au, bu * cl - bl * cu))
    # NOTE: positivity lives ONLY in the constraint rows (single source of truth --
    # no hardcoded clamps here), so the teeth can genuinely break it.
    lo, hi = None, None
    for (a, c) in oned:
        if a > 0:
            hi = c / a if hi is None else min(hi, c / a)
        elif a < 0:
            lo = c / a if lo is None else max(lo, c / a)
        elif c < 0:
            return None                       # constraint 0 <= c violated
    if lo is not None and hi is not None and lo > hi:
        return None
    if lo is None and hi is None:
        cH = Fraction(0)
    elif lo is None:
        cH = hi
    elif hi is None:
        cH = lo
    else:
        cH = (lo + hi) / 2
    lo2, hi2 = None, None
    for (a, b, c) in cons:
        if b > 0:
            v = (c - a * cH) / b
            hi2 = v if hi2 is None else min(hi2, v)
        elif b < 0:
            v = (c - a * cH) / b
            lo2 = v if lo2 is None else max(lo2, v)
        elif a * cH > c:
            return None
    if lo2 is not None and hi2 is not None and lo2 > hi2:
        return None
    if lo2 is None and hi2 is None:
        cL = Fraction(0)
    elif lo2 is None:
        cL = hi2
    elif hi2 is None:
        cL = lo2
    else:
        cL = (lo2 + hi2) / 2
    for (a, b, c) in cons:                    # self-verify the witness
        check(a * cH + b * cL <= c,
              "two-channel witness failed a constraint (internal consistency)")
    return (cH, cL)


def consistent_with_sealed_pair(events3, c_H, c_L, eps):
    """Proposition 3.15(a): with the PAIR (c_H, c_L) sealed before measurement, the
    two-channel law M = c_H*|sigma_H| + c_L*Lambda holds on the set iff every event
    fits within eps."""
    c_H, c_L = Fraction(c_H), Fraction(c_L)
    check(c_H >= 0 and c_L >= 0, "sealed constants must be >= 0")
    eps = _eps(eps)
    check(len(events3) >= 1, "need at least one event")
    return all(abs(M - c_H * s - c_L * lam) <= eps
               for (M, s, lam) in map(_MSL, events3))


def falsified_two_channel(events3, eps):
    """Proposition 3.15(b)-(c): with a sealed-but-unknown pair, is there ANY
    (c_H, c_L) >= 0 fitting every event within eps? FALSIFIED for the class iff no
    such pair exists. Requires >= 2 events (mirror of Proposition 3.8's discipline).
    Power structure (clause (c)): two events with linearly INDEPENDENT reading
    vectors admit a unique exact solve -- non-negative solves are fittable exactly
    and never falsify, and such pairs falsify ONLY through positivity; a
    DEPENDENT-vector pair falsifies through band incompatibility instead (the
    single-channel reduction, verdict-exact under clause (d)'s agreement
    condition); genuine overdetermination begins at three events.
    Returns True iff FALSIFIED."""
    check(len(events3) >= 2, "two-channel falsifier requires >= 2 events")
    return feasible_two_channel(events3, eps) is None


# -- self-test ------------------------------------------------------------
def selftest():
    results = []
    F = Fraction
    eps = F(1, 10)

    # --- B1: single sealed c fits a 2-event class -> NOT falsified --------
    # c = 2 exactly: (M, |sigma|) = (2,1) and (6,3) both fit c=2.
    ev_ok = [(F(2), F(1)), (F(6), F(3))]
    check(consistent_with_sealed_c(ev_ok, F(2), eps), "B1: sealed c=2 must fit both events")
    check(not falsified_over_class(ev_ok, eps), "B1: a common c exists -> not falsified")
    results.append("B1 single sealed c fits multi-event class: NOT falsified: OK")

    # --- B2: no single c fits -> FALSIFIED -------------------------------
    # (2,1) wants c~2; (2,3) wants c~2/3; intervals disjoint at eps=0.1.
    ev_bad = [(F(2), F(1)), (F(2), F(3))]
    check(falsified_over_class(ev_bad, eps), "B2: no common c -> must be FALSIFIED")
    check(not consistent_with_sealed_c(ev_bad, F(2), eps), "B2: sealed c=2 fails the second event")
    results.append("B2 no single c across events: FALSIFIED: OK")

    # --- B3: zero-spin control -- |sigma|=0 with M>0 -> FALSIFIED ---------
    ev_zero = [(F(1), F(2)), (F(1), F(0))]   # second event: cost 1 with zero circulation
    check(falsified_over_class(ev_zero, eps), "B3: |sigma|=0 & M>0 must falsify")
    results.append("B3 zero-spin control (|sigma|=0, M>0): FALSIFIED: OK")

    # --- B4: single event is NOT a test (must require >= 2) ---------------
    try:
        falsified_over_class([(F(3), F(7))], eps)
        raise RuntimeError("a single event must not be accepted as a falsifier")
    except AssertionError:
        pass
    # and a single event is always fittable by c := M/|sigma|
    check(consistent_with_sealed_c([(F(3), F(7))], F(3) / F(7), eps),
          "B4: one event is always fit by c = M/|sigma|")
    results.append("B4 single event rejected as a test (always fittable): OK")

    # --- B5: holdout discipline -- c fitted on e1 need not fit e2 ----------
    # fit c on the calibration event (2,1) -> c=2; the DISJOINT holdout (2,3) fails.
    c_fitted = F(2) / F(1)                    # c := M/|sigma| from the calibration event
    check(test_sealed_c_on_events(c_fitted, [(F(2), F(1))], eps),
          "B5: c fits its own calibration event (circular)")
    check(not test_sealed_c_on_events(c_fitted, [(F(2), F(3))], eps),
          "B5: the c fitted on e1 FAILS on a disjoint holdout e2 -- why holdout matters")
    results.append("B5 holdout: c fitted on one event fails a disjoint holdout: OK")

    # --- B6: within-tolerance wobble still fits (eps is real slack) --------
    # c=2, but measured (2.05, 1) -> |2.05 - 2*1| = 0.05 <= eps=0.1 -> fits.
    ev_wobble = [(F(41, 20), F(1)), (F(6), F(3))]   # 41/20 = 2.05
    check(consistent_with_sealed_c(ev_wobble, F(2), eps), "B6: within-eps wobble must still fit")
    check(not falsified_over_class(ev_wobble, eps), "B6: within-eps wobble not falsified")
    # teeth: push it past eps -> (2.2,1): |2.2-2| = 0.2 > 0.1 with (6,3) pinning c near 2
    ev_past = [(F(11, 5), F(1)), (F(6), F(3))]      # 11/5 = 2.2
    check(falsified_over_class(ev_past, eps), "B6 teeth: past-eps divergence IS falsified")
    results.append("B6 tolerance eps is real slack (wobble fits, past-eps falsifies): OK")

    # --- B7: all-zero-sigma within tolerance -> NOT falsified ('not a test') ---
    # every c > 0 fits (|M - c*0| = M <= eps): unconstraining, must NOT read as falsified.
    ev_allzero = [(F(0), F(0)), (F(1, 20), F(0))]   # M = 0 and M = 0.05, both <= eps = 0.1
    check(not falsified_over_class(ev_allzero, eps),
          "B7: all-zero-sigma within tolerance must NOT be falsified (every c fits)")
    check(feasible_c_interval(ev_allzero, eps) == (F(0), None),
          "B7: feasible set must be unbounded (0, None), distinct from infeasible None")
    check(consistent_with_sealed_c(ev_allzero, F(1), eps),
          "B7: any sealed c fits an all-zero-sigma-within-tolerance set (module self-consistent)")
    results.append("B7 all-zero-sigma within tolerance: NOT falsified (unconstraining, not a test): OK")

    # --- B8: negative tolerance REJECTED (Proposition 3.8: eps >= 0) -------
    for fn in (lambda: fits((F(1), F(1)), F(1), F(-1)),
               lambda: consistent_with_sealed_c([(F(1), F(1))], F(1), F(-1)),
               lambda: feasible_c_interval([(F(1), F(1))], F(-1)),
               lambda: falsified_over_class([(F(1), F(1)), (F(2), F(2))], F(-1))):
        try:
            fn()
            raise RuntimeError("negative eps must be rejected")
        except AssertionError:
            pass
    results.append("B8 negative tolerance rejected across the public API: OK")

    # --- B9: M-only lattice falsifier (quantisation corollary) --------------
    c9, eps9 = F(2), F(1, 10)
    check(quantised_consistent([F(2), F(4), F(41, 20)], c9, eps9),
          "B9: on-lattice costs (2, 4, 2.05) pass at eps = 0.1")
    check(not quantised_consistent([F(2), F(3)], c9, eps9),
          "B9: off-lattice cost (3 = 1.5c) is FALSIFIED")
    check(not quantised_consistent([F(1)], c9, eps9),
          "B9: below-floor cost (1 < c - eps) is FALSIFIED (the positive floor)")
    check(not quantised_consistent([F(1, 20)], c9, eps9),
          "B9: a NEAR-ZERO cost (0.05, within eps of k=0) is FALSIFIED -- the floor "
          "k >= 1 is load-bearing, zero-maintenance is not on the lattice")
    try:
        quantised_consistent([F(2)], c9, F(1))          # eps = c/2: vacuous zone
        raise RuntimeError("lattice test must reject eps >= c/2 (vacuous)")
    except AssertionError:
        pass
    results.append("B9 lattice falsifier: on-lattice pass, off-lattice/below-floor falsified, eps<c/2 enforced: OK")

    # --- B10: derived-floor sanity gate (Prop 3.14 corollary) ---------------
    c1 = F(1)
    check(floor_consistent([(F(6), F(6)), (F(10), F(6))], c1, eps),
          "B10: on-floor (attained) and above-floor readings must pass")
    check(not floor_consistent([(F(5), F(6))], c1, eps),
          "B10: a norm reading BELOW c1*|sigma| is impossible for any realisation -> gate fails")
    check(floor_consistent([(F(0), F(0))], c1, eps),
          "B10: a zero-field reading (sigma = 0, Lambda = 0) respects the floor")
    check(not floor_consistent([(F(3), F(2))], F(2), eps),
          "B10: the floor scales with the declared c1 (c1 = 2: Lambda = 3 < 4 - eps fails)")
    try:
        floor_consistent([(F(1), F(1))], F(0), eps)
        raise RuntimeError("floor_consistent must reject c1 <= 0")
    except AssertionError:
        pass
    try:
        floor_consistent([(F(1), F(1))], c1, F(-1))
        raise RuntimeError("floor_consistent must reject a negative tolerance")
    except AssertionError:
        pass
    results.append("B10 derived-floor gate: attained/above pass, sub-floor impossible-reading fails, guards: OK")

    # --- B11: two-channel feasibility -- witness self-verified; incompatible set falsified ---
    ev2_ok = [(F(5), F(1), F(1)), (F(7), F(2), F(1)), (F(14), F(1), F(4))]  # exact (c_H, c_L) = (2, 3)
    w = feasible_two_channel(ev2_ok, F(1, 100))
    check(w is not None, "B11: consistent three-event two-channel set must be feasible")
    check(consistent_with_sealed_pair(ev2_ok, w[0], w[1], F(1, 100)),
          "B11: the returned witness must fit every event (sealed-pair cross-check)")
    ev2_bad = [(F(1), F(1), F(1)), (F(1), F(2), F(2)), (F(5), F(1), F(2))]
    check(falsified_two_channel(ev2_bad, F(1, 100)),
          "B11: incompatible event set must be FALSIFIED")
    # genuine three-event overdetermination (clause (c)): every 2-subset feasible,
    # the triple jointly infeasible -- the fixture the flagship claim rests on
    ev2_tri = [(F(1), F(1), F(0)), (F(1), F(0), F(1)), (F(4), F(1), F(1))]
    for i in range(3):
        pair = [ev2_tri[j] for j in range(3) if j != i]
        check(not falsified_two_channel(pair, F(1, 100)),
              "B11: every 2-subset of the overdetermination triple must be feasible")
    check(falsified_two_channel(ev2_tri, F(1, 100)),
          "B11: pairwise-feasible triple must be JOINTLY falsified (clause (c) overdetermination)")
    results.append("B11 two-channel feasibility: witness self-verified, incompatible set falsified, "
                   "pairwise-feasible triple jointly falsified: OK")

    # --- B12: Proposition 3.15(c) power structure, both directions ---------
    ev2_neg = [(F(1), F(1), F(1)), (F(3), F(1), F(2))]   # exact solve (-1, 2): outside the quadrant
    check(falsified_two_channel(ev2_neg, F(1, 100)),
          "B12: a negative exact solve at small eps must falsify THROUGH POSITIVITY")
    ev2_pos = [(F(5), F(1), F(1)), (F(8), F(1), F(2))]   # exact solve (2, 3)
    check(feasible_two_channel(ev2_pos, F(0)) == (F(2), F(3)),
          "B12: independent events with a non-negative exact solve fit EXACTLY even at eps = 0")
    results.append("B12 two-event power structure: positivity falsifies, non-negative solve always fits: OK")

    # --- B13: degeneration to the single-channel discipline + zero-control ---
    check(falsified_two_channel([(F(2), F(1), F(0)), (F(3), F(1), F(0))], F(1, 100))
          == (feasible_c_interval([(F(2), F(1)), (F(3), F(1))], F(1, 100)) is None),
          "B13: Lambda == 0 verdict must agree with the single-channel falsifier (generic M > eps)")
    w = feasible_two_channel([(F(2), F(1), F(0)), (F(4), F(2), F(0))], F(1, 100))
    iv = feasible_c_interval([(F(2), F(1)), (F(4), F(2))], F(1, 100))
    check(w is not None and iv is not None and iv[1] is not None
          and iv[0] <= w[0] <= iv[1] and w[1] == 0,
          "B13: Lambda == 0 witness c_H must lie in the single-channel feasible interval")
    check(falsified_two_channel([(F(1), F(0), F(0)), (F(1), F(1), F(1))], F(1, 100)),
          "B13: a zero-reading event (|sigma_H| = Lambda = 0) with M > eps must falsify outright")
    try:
        falsified_two_channel([(F(1), F(1), F(1))], F(1, 100))
        raise RuntimeError("a single event must not be accepted as a two-channel falsifier")
    except AssertionError:
        pass
    results.append("B13 degeneration: Lambda == 0 agrees with Prop 3.8, zero-control falsifies, >= 2 guard: OK")

    return results


if __name__ == "__main__":
    for line in selftest():
        print(line)
    print("bridge_falsifier selftest: 13/13 OK")
