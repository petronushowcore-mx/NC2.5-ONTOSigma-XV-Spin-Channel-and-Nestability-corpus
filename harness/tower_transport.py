"""tower_transport.py -- inter-level transport typing for towers (companion Defs
4.8/4.10, Lemma 4.9, Proposition 4.11, Remark 4.12, Proposition 4.13).

Stdlib only (fractions.Fraction). -O-safe (uses check(), not assert).

The typing, in code form:

  * a TOWER level pair is (upper states, lower states, nu) with nu an INJECTIVE
    embedding of lower states into upper states (the corpus's nesting morphism,
    state level);
  * a transport at the upper level is a state map phi_u; it is IMAGE-PRESERVING
    at the lower level iff phi_u maps the embedded image nu(X_lower) into the
    post-tower embedded image nu'(X'_lower);
  * under image-preservation the lower transport is DERIVED, not declared:
    phi_l = (nu')^{-1} o phi_u o nu -- total and unique because nu' is injective
    (Lemma 4.9); `derived_restriction` computes it and REJECTS non-image-
    preserving maps;
  * CARRIER-COHERENCE: the derived phi_l acts on lower STATES; the companion's
    AUTOMATIC case is the AdmDyn edge-to-edge one. `induced_carrier_map` is a
    derive-or-refuse convenience covering a SUPERSET of that case -- direct-edge,
    reversed-edge, and collapse images (preferring an existing self-loop over a
    collapse) -- and REJECTS anything else; whatever it refuses is exactly the
    territory the companion says must be DECLARED;
  * verdicts per level are then Proposition 4.3 through the derived data
    (core_reduction.transport_classify, reused).

What the fixtures prove (Proposition 4.11): all FOUR combinations of the
per-level verdicts (upper preserved/annihilated x lower preserved/annihilated)
are realisable, each by a single image-preserving, carrier-coherent transport:
level death propagates in neither direction by itself, and a lower level dies
when its witness-bearing cycles are pinched -- the pinch criterion, a sufficient
and downward condition (Proposition 4.3 read through the derived restriction). The upper's recurrence cycle and the embedded
lower image are DISJOINT in these fixtures (nothing in the corpus requires the
embedded image to be upper-recurrent); when they intersect, verdicts can couple
-- realisability, not non-correlation, is the claim.

This module does not prove the Bridge Law and does not add any tower claim beyond
the typed statements above; the composite period ladder is exercised ONLY in its
honest layers (parallel equalities per level; composition under an explicitly
declared witness-alignment).
"""
from fractions import Fraction

import graph_hodge as gh
from graph_hodge import Graph, period, check, entrainment_floors
from core_reduction import transport_classify
from boundary_witness import boundary_witness_sigma


# -- typing ------------------------------------------------------------------
def derived_restriction(phi_u, nu, nu_prime):
    """Lemma 4.9: the lower transport derived from an image-preserving upper map.

    phi_u : dict upper-state -> post-upper-state
    nu    : dict lower-state -> upper-state (injective)
    nu'   : dict post-lower-state -> post-upper-state (injective)

    Returns phi_l : dict lower-state -> post-lower-state, total and unique.
    Raises AssertionError if nu / nu' are not injective or phi_u is NOT
    image-preserving (the transported embedded image must land inside the
    post-tower embedded image)."""
    check(len(set(nu.values())) == len(nu), "nu must be injective (nesting morphism)")
    check(len(set(nu_prime.values())) == len(nu_prime), "nu' must be injective")
    inv = {up: lo for lo, up in nu_prime.items()}
    phi_l = {}
    for lo, up in nu.items():
        target = phi_u[up]
        check(target in inv,
              "not image-preserving at this level: phi_u maps embedded state %r to %r, "
              "outside the post-tower embedded image" % (lo, target))
        phi_l[lo] = inv[target]
    return phi_l


def induced_carrier_map(M, M_prime, phi_l):
    """Derive-or-refuse carrier data (vmap, emap) for the derived phi_l on the
    lower recurrence carrier. Covers a SUPERSET of the companion's automatic
    (AdmDyn edge-to-edge) case: a carrier edge may map to a direct edge of the
    post-carrier, to a reversed edge (sign -1), or collapse to a vertex (equal
    endpoints -> empty path) -- an existing self-loop at that vertex is PREFERRED
    over a collapse, since the two differ on pushforwards. Anything else is
    rejected: in the companion's terms, carrier-coherence is then a declared
    condition this helper refuses to invent."""
    vmap = {v: phi_l[v] for v in M.V}
    edge_index = {}
    for j, (a, b) in enumerate(M_prime.E):
        edge_index.setdefault((a, b), j)
    emap = {}
    for i, (a, b) in enumerate(M.E):
        ia, ib = vmap[a], vmap[b]
        if (ia, ib) in edge_index:                        # direct edge (incl. self-loop)
            emap[i] = [(edge_index[(ia, ib)], +1)]
        elif (ib, ia) in edge_index:
            emap[i] = [(edge_index[(ib, ia)], -1)]
        elif ia == ib:
            emap[i] = []                                  # collapse (no self-loop present)
        else:
            raise AssertionError(
                "carrier-coherence not automatic: carrier edge %r maps to %r, which is "
                "neither an edge of the post-carrier nor a collapse; a coherent carrier "
                "map must be DECLARED for this transport" % ((a, b), (ia, ib)))
    M.check_graph_map(M_prime, vmap, emap)
    return vmap, emap


def level_verdict(M, M_prime, phi_l, recurrence, eta, eta_prime):
    """Proposition 4.3 through the derived restriction: classify the lower level."""
    vmap, emap = induced_carrier_map(M, M_prime, phi_l)
    return transport_classify(M, M_prime, vmap, emap, recurrence, eta, eta_prime)


# -- fixtures ------------------------------------------------------------------
def _triangle(prefix):
    V = ["%s%d" % (prefix, i) for i in range(3)]
    return Graph(V, [(V[0], V[1]), (V[1], V[2]), (V[2], V[0])]), V


def _pre_tower():
    """Upper states: a-triangle (the UPPER's own recurrence carrier) + b-states
    (the embedded image of the lower; NOT upper-recurrent). Lower: its own
    u-triangle carrier in its own state space."""
    Mu, A = _triangle("a")
    Ml, U = _triangle("u")
    nu = {"u0": "b0", "u1": "b1", "u2": "b2"}
    eta = {0: Fraction(1), 1: Fraction(1), 2: Fraction(1)}   # unit witness on each carrier
    gam = {0: 1, 1: 1, 2: 1}                                  # the triangle cycle
    return Mu, Ml, nu, eta, gam


def selftest():
    results = []
    Mu, Ml, nu, eta, gam = _pre_tower()
    upper_states = ["a0", "a1", "a2", "b0", "b1", "b2"]
    point = Graph(["pt"], [])       # collapsed UPPER carrier
    point_l = Graph(["l*"], [])     # collapsed POST-LOWER carrier (on post-lower states)
    eta0 = {}

    # --- W1: typing -- derived restriction computed; non-preserving REJECTED ---
    phi_id = {s: s for s in upper_states}
    check(derived_restriction(phi_id, nu, dict(nu)) == {"u0": "u0", "u1": "u1", "u2": "u2"},
          "W1: identity transport must derive the identity restriction")
    bad = dict(phi_id)
    bad["b1"] = "a0"                     # embedded state thrown outside the post-image
    try:
        derived_restriction(bad, nu, dict(nu))
        raise RuntimeError("W1: a non-image-preserving map must be rejected")
    except AssertionError:
        pass
    try:
        derived_restriction(phi_id, nu, {"u0": "b0", "u1": "b0", "u2": "b2"})
        raise RuntimeError("W1: a non-injective nu' must be rejected")
    except AssertionError:
        pass
    results.append("W1 typing: derived restriction total+unique; non-preserving and "
                   "non-injective declarations rejected: OK")

    # --- W2: upper dies, lower lives (one transport) -----------------------
    # upper a-triangle collapsed to a point; embedded b-states fixed.
    phi = {"a0": "pt", "a1": "pt", "a2": "pt",
           "b0": "b0", "b1": "b1", "b2": "b2"}
    up_v, up_s = transport_classify(Mu, point, {"a0": "pt", "a1": "pt", "a2": "pt"},
                                    {0: [], 1: [], 2: []}, [gam], eta, eta0)
    check(up_v == "ANNIHILATING", "W2: collapsed upper carrier must be ANNIHILATING")
    phi_l = derived_restriction(phi, nu, dict(nu))
    lo_v, lo_s = level_verdict(Ml, Ml, phi_l, [gam], eta, eta)
    check(lo_v == "PRESERVING", "W2: the untouched lower must be PRESERVING")
    results.append("W2 upper dies, lower lives -- death does NOT propagate down: OK")

    # --- W3: upper lives, lower dies (one transport; the pinch) -------------
    # identity on the a-triangle; embedded b-states pinched to one post-state.
    nu_p = {"l*": "b*"}
    phi = {"a0": "a0", "a1": "a1", "a2": "a2",
           "b0": "b*", "b1": "b*", "b2": "b*"}
    up_v, _ = transport_classify(Mu, Mu, {v: v for v in Mu.V},
                                 {0: [(0, 1)], 1: [(1, 1)], 2: [(2, 1)]}, [gam], eta, eta)
    check(up_v == "PRESERVING", "W3: the untouched upper must be PRESERVING")
    phi_l = derived_restriction(phi, nu, nu_p)
    check(set(phi_l.values()) == {"l*"}, "W3: derived restriction must be the constant map")
    lo_v, _ = level_verdict(Ml, point_l, phi_l, [gam], eta, eta0)
    check(lo_v == "ANNIHILATING",
          "W3: the pinched lower must be ANNIHILATING (pinch criterion, Prop 4.3 "
          "through the derived restriction) -- upper survival does not save it")
    results.append("W3 upper lives, lower dies -- the pinch kills the passenger only: OK")

    # --- W4: the remaining two combinations (both live / both die) ----------
    lo_v, _ = level_verdict(Ml, Ml, {"u0": "u0", "u1": "u1", "u2": "u2"}, [gam], eta, eta)
    check(lo_v == "PRESERVING", "W4: identity tower transport preserves the lower")
    phi_all = {s: "pt" for s in upper_states}
    up_v, _ = transport_classify(Mu, point, {"a0": "pt", "a1": "pt", "a2": "pt"},
                                 {0: [], 1: [], 2: []}, [gam], eta, eta0)
    phi_l = derived_restriction(phi_all, nu, {"l*": "pt"})
    lo_v, _ = level_verdict(Ml, point_l, phi_l, [gam], eta, eta0)
    check(up_v == "ANNIHILATING" and lo_v == "ANNIHILATING",
          "W4: the full collapse annihilates both levels")
    results.append("W4 all four verdict combinations realised by single transports "
                   "(Prop 4.11(a) realisability): OK")

    # --- W5: additive tower floors (Remark 4.12) -- distinct loci, exact sum ---
    C4, _ = gh._cycle_graph(4, label="t")
    z1 = C4.fundamental_cycles()[0]
    C3, _ = gh._cycle_graph(3, label="s")
    z2 = C3.fundamental_cycles()[0]
    w2 = {0: Fraction(1), 1: Fraction(1), 2: Fraction(4)}
    f1 = entrainment_floors(Fraction(6), z1)                 # level-1 locus
    f2 = entrainment_floors(Fraction(6), z2, weights=w2)     # level-2 locus
    check(f1[0] + f2[0] == 12 and f1[1] + f2[1] == 9 + 16,
          "W5: the tower floor is the exact sum of per-level floors (independent loci)")
    results.append("W5 additive floors across levels (sum of independent per-level "
                   "bounds, no cross-level content): OK")

    # --- W6: period ladder -- (i) PARALLEL equalities, (ii) composition ONLY ---
    # under an explicitly declared witness-alignment.
    # Pair A (level 1<-0): prism-style compatible pair, sigma_A = lower witness period.
    MlA, UA = _triangle("p")
    etaA = {0: Fraction(1), 1: Fraction(1), 2: Fraction(1)}
    gamA = {0: 1, 1: 1, 2: 1}
    U_env, VE = _triangle("e")
    rho_vmap = {"e0": "p0", "e1": "p1", "e2": "p2"}
    rho_emap = {0: [(0, 1)], 1: [(1, 1)], 2: [(2, 1)]}
    GammaA = {0: 1, 1: 1, 2: 1}
    otA = gh.induced_pullback(rho_emap, etaA)                 # H-b as pullback
    sigA = boundary_witness_sigma(MlA, U_env, rho_vmap, rho_emap, GammaA, gamA, etaA, otA)
    check(sigA == period(etaA, gamA) == 3,
          "W6(i): pair-A maintenance circulation equals its own lower witness period")
    # Pair B (level 2<-1): DIFFERENT numbers -- parallel, not composed.
    etaB = {0: Fraction(2), 1: Fraction(2), 2: Fraction(2)}
    U2, _ = _triangle("f")
    otB = gh.induced_pullback(rho_emap, etaB)
    sigB = boundary_witness_sigma(MlA, U2,
                                  {"f0": "p0", "f1": "p1", "f2": "p2"}, rho_emap,
                                  GammaA, gamA, etaB, otB)
    check(sigB == 6 and sigB != sigA,
          "W6(i): the equalities are PARALLEL per pair -- independent numbers, no chain")
    # (ii) composition under the DECLARED witness-alignment, stated at PERIOD level:
    # level 1 gets its OWN carrier M1 (distinct from pair-A's envelope) and its own
    # witness eta1; the alignment is the declared EQUALITY OF TWO INDEPENDENTLY
    # COMPUTED PERIODS, <eta1, gam1> = sigma_A -- nothing class-level, no conflated
    # locus. The top pair's envelope has b1 = 2 (a figure-eight), so the fixture is
    # not degenerate in the b1 = 1 sense where period and class equality coincide.
    M1, _ = _triangle("q")
    eta1 = {0: Fraction(1), 1: Fraction(1), 2: Fraction(1)}
    gam1 = {0: 1, 1: 1, 2: 1}
    check(period(eta1, gam1) == sigA,
          "W6(ii): the declared period-level alignment (level-1 witness period = sigma_A)")
    U_top = Graph(["x", "p", "q"], [("x", "p"), ("p", "x"), ("x", "q"), ("q", "x")])
    Gamma_top = {0: 1, 1: 1}
    rho_vm = {"x": "q0", "p": "q1", "q": "q0"}
    rho_em = {0: [(0, 1)], 1: [(1, 1), (2, 1)], 2: [], 3: []}
    ot_top = gh.induced_pullback(rho_em, eta1)
    sig_top = boundary_witness_sigma(M1, U_top, rho_vm, rho_em,
                                     Gamma_top, gam1, eta1, ot_top)
    check(sig_top == sigA == 3,
          "W6(ii): under the declared period-level alignment the top reading equals "
          "the bottom witness period (composition is declaration-conditional)")
    results.append("W6 period ladder: parallel per-pair equalities (no free composition); "
                   "composed reading only under a declared witness-alignment: OK")

    # --- W7: carrier-coherence rejection (the declared-case boundary) --------
    # a derived state map sending a carrier edge to a NON-edge, non-collapse pair
    # is not automatically coherent and must be rejected, not silently accepted.
    Msq = Graph(["x0", "x1", "x2", "x3"],
                [("x0", "x1"), ("x1", "x2"), ("x2", "x3"), ("x3", "x0")])
    phi_bad = {"u0": "x0", "u1": "x2", "u2": "x1"}            # (u0,u1) -> (x0,x2): a chord
    try:
        induced_carrier_map(Ml, Msq, phi_bad)
        raise RuntimeError("W7: a non-edge, non-collapse image must be rejected")
    except AssertionError:
        pass
    results.append("W7 carrier-coherence boundary: non-automatic case rejected "
                   "(declared-condition territory): OK")

    return results


if __name__ == "__main__":
    for line in selftest():
        print(line)
    print("tower_transport selftest: 7/7 OK")
