"""core_reduction.py -- Proposition 4.3 (Witness Transport Kernel Criterion) harness.

Generalises XV.3 (Core-Reduction). A transport carrier-map phi: M -> M' induces
phi_*: H_1(M) -> H_1(M') on the recurrence cycles. The identity witness [eta]
(paired against a recurrence cycle [gamma] with <eta,gamma> != 0) is transported
according to whether phi_* KILLS the specific recurrence cycle -- NOT according to
the contractibility of the carrier:

  - PRESERVING   : every witness-bearing recurrence cycle survives -- <eta', phi_*[gamma]> != 0;
  - ANNIHILATING : every witness-bearing recurrence cycle is killed -- phi_*[gamma] pairs to 0;
  - PARTIAL      : some survive, some killed.

**XV.3 (Core-Reduction, companion Theorem 3(i)) is the COROLLARY**: if phi factors
through a contractible core K (H_1(K) = 0), then phi_* = 0 on H_1, so every cycle
is killed => ANNIHILATING. But contractibility is SUFFICIENT, not necessary: a
transport can land every witness-bearing cycle in the pairing kernel of eta' while
the pushed class itself SURVIVES (the T10 chain's middle stage: pairing dead, class alive) --
there a contractible factor is impossible, since one would force phi_* = 0. (The
degree-0 self-map of a NON-contractible carrier also annihilates -- killing every
class with non-contractible pre- and post-carriers -- though its winding-0 walk
does lift through a finite tree, i.e. it secretly IS a contractible-factor
instance; what it witnesses is that the POST-carrier need not be the core.) The
kernel criterion is the general statement; core-reduction is one way to land
phi_*[gamma] in the kernel.

Stdlib only, -O-safe. Reuses the hardened graph_hodge cohomology core.
"""
from fractions import Fraction
import graph_hodge as gh
from graph_hodge import Graph, period, induced_pushforward, check


def transport_classify(M, Mp, vmap, emap, recurrence, eta, eta_p):
    """Classify a transport phi: M -> M' on a set of witness-bearing recurrence
    cycles. Each `gamma` in `recurrence` must be a genuine 1-cycle of the SOURCE M
    (validated) with <eta, gamma> != 0 (a witness-bearing precondition, checked).
    Returns (verdict, survives) where verdict in {PRESERVING, ANNIHILATING, PARTIAL}
    and survives[i] is a bool."""
    M.check_graph_map(Mp, vmap, emap)
    check(len(recurrence) >= 1, "need at least one recurrence cycle")
    survives = []
    for gamma in recurrence:
        gh.cycle_class_coeffs(M, gamma)   # reject a non-cycle: gamma must be a 1-cycle of the SOURCE M
        check(period(eta, gamma) != 0, "recurrence cycle must be witness-bearing (<eta,gamma> != 0)")
        pushed = induced_pushforward(emap, gamma)             # phi_*[gamma], a chain in M'
        survives.append(period(eta_p, pushed) != 0)
    if all(survives):
        verdict = "PRESERVING"
    elif not any(survives):
        verdict = "ANNIHILATING"
    else:
        verdict = "PARTIAL"
    return verdict, survives


def witness_retention(M, Mp, vmap, emap, recurrence, eta, eta_p):
    """Quantitative refinement of the trichotomy (companion Remark 4.4): over the
    declared witness-bearing recurrence classes, the retention ratio
        R_phi = #survived / #declared
    refines the verdict -- PRESERVING is R = 1, ANNIHILATING is R = 0, PARTIAL is
    0 < R < 1. Returns (verdict, survives, ratio as a Fraction)."""
    verdict, survives = transport_classify(M, Mp, vmap, emap, recurrence, eta, eta_p)
    ratio = Fraction(sum(1 for s in survives if s), len(survives))
    return verdict, survives, ratio


def h1_trivial_target_annihilates(Mp):
    """The core-reduction corollary, mechanically: an H^1-trivial target (b1 = 0)
    forces phi_*[gamma] to pair to 0 for every cycle, so the witness is annihilated.
    NOTE b1 == 0 means H^1-TRIVIAL, which is WEAKER than contractible -- a disconnected
    forest is H^1-trivial but not contractible; H^1-triviality is the exact sufficient
    annihilation condition. Returns True iff Mp is H^1-trivial (b1 = 0)."""
    return Mp.b1() == 0


# ---- fixtures -----------------------------------------------------------
def _cycle(n, label):
    V = ["%s%d" % (label, i) for i in range(n)]
    E = [(V[i], V[(i + 1) % n]) for i in range(n)]
    return Graph(V, E)


def _figure_eight():
    """Two loops L1, L2 sharing vertex x. Edges 0,1 = L1 (x->a->x); 2,3 = L2 (x->b->x)."""
    V = ["x", "a", "b"]
    E = [("x", "a"), ("a", "x"), ("x", "b"), ("b", "x")]
    return Graph(V, E)


def selftest():
    results = []
    one = Fraction(1)

    M = _cycle(3, "c")                 # recurrence carrier C_3
    gamma = M.fundamental_cycles()[0]  # {0:1,1:1,2:1}
    eta = {0: one, 1: one, 2: one}     # <eta,gamma> = 3 != 0
    check(period(eta, gamma) == 3, "witness period must be 3")

    # --- T1: identity transport PRESERVES ------------------------------
    Mp = _cycle(3, "c")
    vmap_id = {"c%d" % i: "c%d" % i for i in range(3)}
    emap_id = {e: [(e, +1)] for e in range(3)}
    v, s = transport_classify(M, Mp, vmap_id, emap_id, [gamma], eta, eta)
    check(v == "PRESERVING" and s == [True], "T1: identity must preserve, got %s %s" % (v, s))
    results.append("T1 identity transport: PRESERVING: OK")

    # --- T2: contractible-core (tree target) ANNIHILATES (= XV.3) -------
    tree = Graph(["p", "q"], [("p", "q")])          # b1 = 0, contractible
    vmap_c = {"c0": "p", "c1": "p", "c2": "p"}
    emap_c = {0: [], 1: [], 2: []}                    # every edge collapses to the point p
    eta_tree = {0: one}
    v, s = transport_classify(M, tree, vmap_c, emap_c, [gamma], eta, eta_tree)
    check(v == "ANNIHILATING" and s == [False], "T2: contractible core must annihilate, got %s" % v)
    check(h1_trivial_target_annihilates(tree), "T2: tree target must be flagged H^1-trivial")
    results.append("T2 contractible core (XV.3 corollary): ANNIHILATING: OK")

    # --- T3: NON-contractible target, still ANNIHILATES (degree-0) ------
    # phi: C_3 -> C_3 collapsing everything to c0 -- target is NON-contractible (b1=1)
    Mp3 = _cycle(3, "c")
    vmap_0 = {"c0": "c0", "c1": "c0", "c2": "c0"}
    emap_0 = {0: [], 1: [], 2: []}
    v, s = transport_classify(M, Mp3, vmap_0, emap_0, [gamma], eta, eta)
    check(v == "ANNIHILATING", "T3: degree-0 map must annihilate, got %s" % v)
    check(Mp3.b1() == 1, "T3 teeth: target is NON-contractible (b1=1) yet witness is killed")
    results.append("T3 non-contractible target, degree-0: ANNIHILATING (contractibility not necessary): OK")

    # --- T4: PARTIAL -- one recurrence cycle survives, one killed -------
    F = _figure_eight()
    L1 = {0: +1, 1: +1}                # x->a->x
    L2 = {2: +1, 3: +1}                # x->b->x
    etaF = {0: one, 2: one}            # <etaF,L1>=1, <etaF,L2>=1 (both witness-bearing)
    C2 = _cycle(2, "d")
    vmapF = {"x": "d0", "a": "d1", "b": "d0"}
    emapF = {0: [(0, +1)], 1: [(1, +1)], 2: [], 3: []}   # L1 -> C_2 loop; L2 collapses
    etaC2 = {0: one}
    v, s = transport_classify(F, C2, vmapF, emapF, [L1, L2], etaF, etaC2)
    check(v == "PARTIAL" and s == [True, False], "T4: must be PARTIAL [True,False], got %s %s" % (v, s))
    results.append("T4 mixed transport: PARTIAL (L1 survives, L2 killed): OK")

    # --- T5: NON-CYCLE recurrence REJECTED (cycle-validity guard) --------
    # a single edge of C_3 is a 1-chain, not a 1-cycle; it is witness-bearing
    # (period != 0) so the cycle-check -- not the witness-check -- must fire.
    noncycle = {0: +1}
    eta_nc = {0: one}
    try:
        transport_classify(M, _cycle(3, "c"), vmap_id, emap_id, [noncycle], eta_nc, eta_nc)
        raise RuntimeError("non-cycle recurrence must be rejected (cycle-validity)")
    except AssertionError:
        pass
    results.append("T5 non-cycle recurrence rejected (cycle-validity): OK")

    # --- T6: non-witness-bearing GENUINE cycle REJECTED (witness precond) -
    # C_4 with an alternating cochain: <eta, gamma> = 1-1+1-1 = 0, but gamma is
    # a genuine 1-cycle, so the witness-check -- not the cycle-check -- must fire.
    C4 = _cycle(4, "e")
    g4 = C4.fundamental_cycles()[0]
    eta_perp = {0: one, 1: -one, 2: one, 3: -one}
    check(period(eta_perp, g4) == 0, "T6 setup: eta must be orthogonal to the cycle")
    vmap4 = {"e%d" % i: "e%d" % i for i in range(4)}
    emap4 = {e: [(e, +1)] for e in range(4)}
    try:
        transport_classify(C4, _cycle(4, "e"), vmap4, emap4, [g4], eta_perp, eta_perp)
        raise RuntimeError("non-witness-bearing recurrence must be rejected (witness precond)")
    except AssertionError:
        pass
    results.append("T6 non-witness-bearing cycle rejected (witness precond): OK")

    # --- T7: CARRIER-LEVEL channel split -- pairing dies, magnitude survives ---
    # Degree-0 transport (T3 data): the transported witness pairing is 0, yet the
    # field on the target carrier still has non-zero NORM. These are the CARRIER-side
    # analogues of the envelope channels (companion Remark 3.10, two-loci discipline
    # of Remark 3.3a): a magnitude-only monitor sees live structure while the witness
    # is already gone -- the Regime-W signature.
    v3, s3 = transport_classify(M, Mp3, vmap_0, emap_0, [gamma], eta, eta)
    check(v3 == "ANNIHILATING", "T7 setup: degree-0 must annihilate (transported pairing)")
    check(gh.cycle_norm(eta, Mp3.fundamental_cycles()[0]) == 3,
          "T7: the carrier-level magnitude reading is ALIVE (= 3) while the "
          "transported witness pairing is dead -- the two readings are distinct data")
    results.append("T7 carrier-level split: pairing dead, magnitude reading alive: OK")

    # --- T8: 2x3 axis independence as INDEPENDENT-AXIS DATA (companion Prop 5.1) ---
    # Budget axis {nestable, sealed} x witness axis {PRESERVING, ANNIHILATING, PARTIAL}.
    # The upper substrate's budget verdict and a carrier-transport's witness verdict
    # are independent data; on the nestable side they co-realise within one nested
    # instance, while a sealed core hosts no nested pair -- its rows pair verdicts of
    # independent objects, which is exactly Prop 5.1's point (neither axis constrains
    # the other), NOT an in-instance co-realisation.
    import nestability as ns
    uppers = {
        "nestable": ns.Sub(["x"], [("x", "x")], {0: 2}, C=5),        # mu = 3/5 > 0
        "sealed":   ns.Sub(["a", "b"], [("a", "b")], {0: 1}, C=1),   # mu = 0
    }
    F8 = _figure_eight()
    transports = {
        "PRESERVING":   (M, _cycle(3, "c"), vmap_id, emap_id, [gamma], eta, eta),
        "ANNIHILATING": (M, Mp3, vmap_0, emap_0, [gamma], eta, eta),
        "PARTIAL":      (F8, _cycle(2, "d"),
                         {"x": "d0", "a": "d1", "b": "d0"},
                         {0: [(0, +1)], 1: [(1, +1)], 2: [], 3: []},
                         [{0: +1, 1: +1}, {2: +1, 3: +1}], {0: one, 2: one}, {0: one}),
    }
    seen = []
    for uname, U8 in uppers.items():
        for tname, targs in transports.items():
            budget_verdict = ns.is_nestable(U8)
            witness_verdict, _ = transport_classify(*targs)
            check(witness_verdict == tname, "T8: transport verdict must be %s" % tname)
            seen.append((uname, budget_verdict, tname))
    check(len(seen) == 6 and {b for (_, b, _) in seen} == {True, False},
          "T8: all six budget x witness combinations realised independently")
    results.append("T8 axis independence: all 6 {nestable,sealed} x {P,A,Partial} combos realised: OK")

    # --- T9: retention ratio refines the trichotomy ------------------------
    vP, sP, rP = witness_retention(M, _cycle(3, "c"), vmap_id, emap_id, [gamma], eta, eta)
    check(rP == 1, "T9: PRESERVING retention must be 1, got %s" % rP)
    vA, sA, rA = witness_retention(M, Mp3, vmap_0, emap_0, [gamma], eta, eta)
    check(rA == 0, "T9: ANNIHILATING retention must be 0, got %s" % rA)
    vX, sX, rX = witness_retention(F8, _cycle(2, "d"),
                                   {"x": "d0", "a": "d1", "b": "d0"},
                                   {0: [(0, +1)], 1: [(1, +1)], 2: [], 3: []},
                                   [{0: +1, 1: +1}, {2: +1, 3: +1}], {0: one, 2: one}, {0: one})
    check(vX == "PARTIAL" and rX == Fraction(1, 2), "T9: PARTIAL retention must be 1/2, got %s" % rX)
    results.append("T9 retention ratio: PRESERVING 1, ANNIHILATING 0, PARTIAL 1/2: OK")

    # --- T10: composition -- class-kill propagates; pairing-kill does NOT ---
    # (companion Remark 4.5) Stage phi: C_3 -> figure-eight, image = loop L1.
    # Middle witness eta' reads ONLY L2: <eta', phi_* gamma> = 0 (pairing-annihilated),
    # BUT phi_* gamma = L1 != 0 in H_1. Stage psi: figure-eight -> C_2 collapsing L2;
    # final witness eta'' reads the C_2 loop: <eta'', psi_* phi_* gamma> = 2 != 0.
    # The chain PRESERVES the witness despite the pairing-dead middle reading --
    # pairing-annihilation is witness-relative and does not compose. Class-kill does:
    # any stage with phi_*[gamma] = 0 (e.g. T2/T3) makes every continuation dead.
    vmap_f = {"c0": "x", "c1": "a", "c2": "x"}
    emap_f = {0: [(0, +1)], 1: [(1, +1)], 2: []}
    M.check_graph_map(F8, vmap_f, emap_f)
    pushed_mid = induced_pushforward(emap_f, gamma)
    check(pushed_mid == {0: 1, 1: 1}, "T10: phi_* gamma must be the L1 loop (class-alive)")
    eta_mid = {2: one}                                  # reads only L2
    check(period(eta_mid, pushed_mid) == 0, "T10: middle pairing is DEAD (eta' reads L2 only)")
    vmap_g = {"x": "d0", "a": "d1", "b": "d0"}
    emap_g = {0: [(0, +1)], 1: [(1, +1)], 2: [], 3: []}
    F8.check_graph_map(_cycle(2, "d"), vmap_g, emap_g)
    pushed_end = induced_pushforward(emap_g, pushed_mid)
    eta_end = {0: one, 1: one}
    check(period(eta_end, pushed_end) == 2,
          "T10: the composed transport PRESERVES the witness (period 2) despite the "
          "pairing-dead middle reading -- pairing-annihilation does not compose")
    # and class-kill DOES propagate: after a degree-0 stage the image chain is empty,
    # so every continuation pairs to 0.
    check(induced_pushforward(emap_0, gamma) == {},
          "T10: a class-killing stage leaves nothing for any continuation to revive")
    results.append("T10 composition: class-kill propagates, pairing-kill is witness-relative: OK")

    # --- T11: witness capacity (Prop 4.6) -- image rank <= min b1; qualifier bites ---
    # rose (b1=3) -> figure-eight (b1=2): petals 1,2 -> loops L1,L2; petal 3 collapses.
    rose = Graph(["x", "a", "b", "c"],
                 [("x", "a"), ("a", "x"), ("x", "b"), ("b", "x"), ("x", "c"), ("c", "x")])
    F8t = _figure_eight()
    vmap_r = {"x": "x", "a": "a", "b": "b", "c": "x"}
    emap_r = {0: [(0, +1)], 1: [(1, +1)], 2: [(2, +1)], 3: [(3, +1)], 4: [], 5: []}
    rose.check_graph_map(F8t, vmap_r, emap_r)
    petals = [{0: 1, 1: 1}, {2: 1, 3: 1}, {4: 1, 5: 1}]
    imgs = [induced_pushforward(emap_r, p) for p in petals]
    live = [im for im in imgs if im]
    check(rose.b1() == 3 and F8t.b1() == 2, "T11 setup: b1 3 -> 2")
    check(gh.rank_of_cycles(F8t, live) == 2,
          "T11: image rank must attain the bottleneck bound min(b1) = 2")
    # the INDEPENDENCE qualifier bites: all petals onto ONE loop -> 3 nonzero images, rank 1
    emap_one = {0: [(0, +1)], 1: [(1, +1)], 2: [(0, +1)], 3: [(1, +1)], 4: [(0, +1)], 5: [(1, +1)]}
    rose.check_graph_map(F8t, {"x": "x", "a": "a", "b": "a", "c": "a"}, emap_one)
    imgs_one = [induced_pushforward(emap_one, p) for p in petals]
    check(all(im for im in imgs_one) and gh.rank_of_cycles(F8t, imgs_one) == 1,
          "T11: three NON-ZERO images can still have rank 1 -- image-independence is "
          "the invariant, not non-vanishing (the naive source-side count is refuted)")
    # INTERMEDIATE bottleneck: rose (b1=3) -> figure-eight (b1=2) -> rose' (b1=3);
    # only the MIDDLE carrier binds -- composite image rank <= 2 despite b1=3 at
    # both ends (Prop 4.6(iii): min over ALL carriers, including intermediate).
    rose2 = Graph(["y", "p", "q", "r"],
                  [("y", "p"), ("p", "y"), ("y", "q"), ("q", "y"), ("y", "r"), ("r", "y")])
    emap_2 = {0: [(0, +1)], 1: [(1, +1)], 2: [(2, +1)], 3: [(3, +1)]}   # L1->petal p, L2->petal q
    F8t.check_graph_map(rose2, {"x": "y", "a": "p", "b": "q"}, emap_2)
    composite = [induced_pushforward(emap_2, induced_pushforward(emap_r, p)) for p in petals]
    live_c = [im for im in composite if im]
    check(rose2.b1() == 3 and len(live_c) == 2 and gh.rank_of_cycles(rose2, live_c) == 2,
          "T11: composite rank bounded by the INTERMEDIATE b1 = 2, not the terminal b1 = 3")
    results.append("T11 witness capacity: bound attained (rank 2 = min b1); all-to-one rank 1; intermediate bottleneck binds: OK")

    # --- T12: class-retention monotone along a chain; survivor set shrinks ---
    # F8 -> C2 (T4 map: L1 alive, L2 killed) -> single-vertex loopless target (all killed).
    C2t = _cycle(2, "d")
    vmap_g2 = {"x": "d0", "a": "d1", "b": "d0"}
    emap_g2 = {0: [(0, +1)], 1: [(1, +1)], 2: [], 3: []}
    pt = Graph(["z"], [])
    vmap_pt = {"d0": "z", "d1": "z"}
    emap_pt = {0: [], 1: []}
    C2t.check_graph_map(pt, vmap_pt, emap_pt)
    W0 = [{0: +1, 1: +1}, {2: +1, 3: +1}]                     # L1, L2 on F8
    stage1 = [induced_pushforward(emap_g2, g) for g in W0]
    alive1 = [bool(im) for im in stage1]
    stage2 = [induced_pushforward(emap_pt, im) for im in stage1]
    alive2 = [bool(im) for im in stage2]
    check(alive1 == [True, False] and alive2 == [False, False],
          "T12: survivor sets 2 -> 1 -> 0 along the chain")
    check(all((not a1) <= (not a2) for a1, a2 in zip(alive1, alive2)) and
          all(a2 <= a1 for a1, a2 in zip(alive1, alive2)),
          "T12: composite survivors are a SUBSET of stage-one survivors (monotone)")
    results.append("T12 class-retention: monotone non-increasing along the chain (2->1->0): OK")

    return results


if __name__ == "__main__":
    for line in selftest():
        print(line)
    print("core_reduction selftest: 12/12 OK")
