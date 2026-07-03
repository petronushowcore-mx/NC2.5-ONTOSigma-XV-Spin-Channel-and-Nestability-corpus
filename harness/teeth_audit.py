"""teeth_audit.py -- mechanical non-vacuity gate for the ONTO-Sigma XV harness.

Every selftest() check in the harness must have TEETH: breaking the underlying
computation must make some check RED. A check that passes regardless of the
property it claims to test is a VACUUM (the XIV failure class the checker C7 and
this audit exist to prevent).

Each REGISTRY row is (name, mutator, expected), where `expected` is "RED" (the
mutation breaks a real computation and must be caught) or "SURVIVE" (the mutation
PRESERVES the tested invariant and must NOT be caught -- included so the suite is
not merely 'everything reds', which is itself a kind of vacuum).

`run()` reimports the target module fresh, applies one mutation, runs its
selftest(), and records RED (raised) vs SURVIVE (passed). The audit FAILS if any
row's actual verdict differs from `expected` -- i.e. a genuine break went
uncaught, OR a teeth-check was weakened so an expected-RED mutation now survives.

Stdlib only, -O-safe. Scope: every harness module of the battery (graph_hodge,
nestability, core_reduction, boundary_witness, bridge_falsifier, pilot_entrainment,
tower_transport, funnel_channels, fano_channel) plus the corpus gate's own fixture teeth.
"""

import importlib


def check(cond, msg="check failed"):
    if not cond:
        raise AssertionError(msg)


def _run_one(module_name, patch):
    # Isolation: reload the shared dependencies FIRST (wipes any mutation a prior row
    # left on them), THEN reload the target so its `from <dep> import ...` names
    # re-bind to the fresh objects. The order is load-bearing. graph_hodge is imported
    # by most modules; bridge_falsifier is imported by pilot_entrainment.
    importlib.reload(importlib.import_module("graph_hodge"))
    for dep in ("nestability", "core_reduction", "boundary_witness",
                "bridge_falsifier", "pilot_entrainment"):
        if module_name != dep:
            importlib.reload(importlib.import_module(dep))
    mod = importlib.import_module(module_name)
    if module_name != "graph_hodge":
        importlib.reload(mod)
    patch(mod)
    try:
        mod.selftest()
    except AssertionError as e:
        return ("RED", str(e)[:70])
    except Exception as e:  # any raise = the break was caught
        return ("RED", "%s: %s" % (type(e).__name__, str(e)[:56]))
    return ("SURVIVE", "")


# ---- graph_hodge mutators ----------------------------------------------
def _gh_components(m):
    m.Graph.components = lambda self: 1

def _gh_pushforward_collapse(m):
    orig = m.induced_pushforward
    m.induced_pushforward = lambda em, cy: {k: (1 if v else 0) for k, v in orig(em, cy).items()}

def _gh_period_zero(m):
    m.period = lambda omega, cycle: m.Fraction(0)

def _gh_period_abs(m):
    m.period = lambda omega, cycle: sum((omega.get(ei, m.Fraction(0)) * abs(c)
                                         for ei, c in cycle.items()), m.Fraction(0))

def _gh_fundcycles_empty(m):
    m.Graph.fundamental_cycles = lambda self: []

def _gh_pullback_drop_sign(m):
    def bad(emap, omega_prime):
        return {e: sum((omega_prime.get(ep, m.Fraction(0)) for (ep, sgn) in se), m.Fraction(0))
                for e, se in emap.items()}
    m.induced_pullback = bad

def _gh_treepath_flip(m):
    orig = m.Graph._tree_path
    m.Graph._tree_path = lambda self, f, s, d: [(ei, -sg) for (ei, sg) in orig(self, f, s, d)]

def _gh_cgm_noop(m):
    m.Graph.check_graph_map = lambda self, gp, vm, em: True

def _gh_ccc_norecon(m):
    def bad(gp, chain):
        forest = gp.spanning_forest()
        chords = [i for i in range(len(gp.E)) if i not in forest]
        return {j: chain.get(ch, 0) for j, ch in enumerate(chords)}
    m.cycle_class_coeffs = bad

def _gh_coboundary_flip(m):
    orig = m.coboundary
    m.coboundary = lambda g, f: {k: -v for k, v in orig(g, f).items()}  # -df is still a coboundary

def _gh_rank_ignores_dependence(m):
    # rank pinned to the COUNT of chains (independence ignored). RED via P14/T11:
    # multiples of one petal must have rank 1, not 3.
    m.rank_of_cycles = lambda graph, chains: len(chains)

def _gh_harmonic_ignores_weights(m):
    # drop the measure datum (always counting measure). RED via the weighted P13 case:
    # the unweighted harmonic (2,2,2) fails the weighted-divergence check for w=(1,1,4).
    orig = m.harmonic_representative
    m.harmonic_representative = lambda graph, omega, weights=None: orig(graph, omega, None)

def _gh_harmonic_skip_projection(m):
    # skip the projection: return the input unchanged. RED via P13 (div != 0 on a
    # non-harmonic input / no strict L2 decrease).
    m.harmonic_representative = lambda graph, omega, weights=None: {
        i: m.Fraction(omega.get(i, m.Fraction(0))) for i in range(len(graph.E))}

def _gh_norm_as_period(m):
    # collapse the local channel into the homological one. RED via P11: the norm
    # must be gauge-SENSITIVE; the period is gauge-invariant.
    m.cycle_norm = lambda omega, cycle, weights=None: m.period(omega, cycle)


# ---- boundary_witness mutators (Proposition 3.7) -------------------------
def _bw_H_a_noop(m):
    m.check_H_a = lambda M, emap, Gamma, gamma_i: None

def _bw_H_b_noop(m):
    m.check_H_b = lambda U, emap, eta, ot: None

def _bw_cohomologous_true(m):
    m.cohomologous = lambda U, a, b: True

def _bw_noncontractible_true(m):
    m.is_noncontractible_cycle = lambda U, Gamma: True

def _bw_strict_H_b(m):
    # regress H-b from cohomological to POINTWISE equality. RED via Q6: the
    # coboundary-shifted realisation (cohomologous, not equal) must PASS -- strict
    # equality wrongly rejects it.
    def strict(U, emap, eta, ot):
        pulled = m.induced_pullback(emap, eta)
        m.check(ot == pulled, "H-b fails: strict equality")
    m.check_H_b = strict

def _bw_gamma_guard_removed(m):
    # remove the gamma_i non-zero + witness-bearing guard. RED via Q5: the zero
    # gamma_i / collapsed-rho declaration then passes H-a/H-b vacuously (0 = 0).
    def sig(M, U, rho_vmap, rho_emap, Gamma, gamma_i, eta, omega_tilde):
        U.check_graph_map(M, rho_vmap, rho_emap)
        m.check(m.is_noncontractible_cycle(U, Gamma), "not boundary-layer-admissible")
        m.check_H_a(M, rho_emap, Gamma, gamma_i)
        m.check_H_b(U, rho_emap, eta, omega_tilde)
        sigma = m.period(omega_tilde, Gamma)
        m.check(sigma == m.period(eta, gamma_i), "identity")
        return sigma
    m.boundary_witness_sigma = sig

def _bw_identity_removed(m):
    # Drop the final "sigma == transported witness period" assertion. This must
    # SURVIVE: Proposition 3.7 makes the identity a CONSEQUENCE of H-a + H-b + Lemma 3.6,
    # so on hypothesis-satisfying inputs it holds automatically -- the assertion is a
    # consistency belt, not independent teeth. (Its passing is evidence the theorem holds.)
    # NOTE: the gamma_i guard is KEPT -- this mutator removes ONLY the identity assert.
    def sig(M, U, rho_vmap, rho_emap, Gamma, gamma_i, eta, omega_tilde):
        U.check_graph_map(M, rho_vmap, rho_emap)
        m.check(m.is_noncontractible_cycle(U, Gamma), "not boundary-layer-admissible")
        cls_g = m.cycle_class_coeffs(M, gamma_i)
        m.check(any(c != 0 for c in cls_g.values()), "gamma_i must be a NON-ZERO class")
        m.check(m.period(eta, gamma_i) != 0, "gamma_i must be witness-bearing")
        m.check_H_a(M, rho_emap, Gamma, gamma_i)
        m.check_H_b(U, rho_emap, eta, omega_tilde)
        return m.period(omega_tilde, Gamma)          # identity assertion removed
    m.boundary_witness_sigma = sig


# ---- core_reduction mutators (Proposition 4.3) -------------------------
def _cr_survives_always(m):
    def bad(M, Mp, vmap, emap, recurrence, eta, eta_p):
        M.check_graph_map(Mp, vmap, emap)
        return ("PRESERVING", [True] * len(recurrence))
    m.transport_classify = bad

def _cr_h1flag_false(m):
    m.h1_trivial_target_annihilates = lambda Mp: False

def _cr_retention_always_full(m):
    # retention ratio pinned to 1 regardless of survival. RED via T9 (ANNIHILATING
    # must give 0, PARTIAL must give 1/2).
    def bad(M, Mp, vmap, emap, recurrence, eta, eta_p):
        v, s = m.transport_classify(M, Mp, vmap, emap, recurrence, eta, eta_p)
        return v, s, m.Fraction(1)
    m.witness_retention = bad

def _cr_precond_removed(m):
    # Remove ONLY the witness-bearing check, KEEP the cycle-validity check. RED via T6:
    # a non-witness-bearing GENUINE cycle now passes and the "must raise" tooth fails.
    def relaxed(M, Mp, vmap, emap, recurrence, eta, eta_p):
        M.check_graph_map(Mp, vmap, emap)
        m.check(len(recurrence) >= 1, "need cycle")
        survives = []
        for g in recurrence:
            m.gh.cycle_class_coeffs(M, g)                       # cycle-validity KEPT
            survives.append(m.period(eta_p, m.induced_pushforward(emap, g)) != 0)
        v = "PRESERVING" if all(survives) else ("ANNIHILATING" if not any(survives) else "PARTIAL")
        return v, survives
    m.transport_classify = relaxed

def _cr_cyclecheck_removed(m):
    # Remove ONLY the cycle-validity check, KEEP the witness-bearing check. RED via T5:
    # a NON-cycle (witness-bearing) now passes and the "must raise" tooth fails.
    def relaxed(M, Mp, vmap, emap, recurrence, eta, eta_p):
        M.check_graph_map(Mp, vmap, emap)
        m.check(len(recurrence) >= 1, "need cycle")
        survives = []
        for g in recurrence:
            m.check(m.period(eta, g) != 0, "witness-bearing")  # witness-check KEPT
            survives.append(m.period(eta_p, m.induced_pushforward(emap, g)) != 0)
        v = "PRESERVING" if all(survives) else ("ANNIHILATING" if not any(survives) else "PARTIAL")
        return v, survives
    m.transport_classify = relaxed


# ---- nestability mutators (Proposition 2.4) ----------------------------
def _nest_min_to_max(m):
    def bad(self):
        adm = self.admissible_edges()
        return None if not adm else max(self.phi[i] for i in adm)  # max, not min
    m.Sub.min_nonempty_burden = bad

def _nest_isnestable_true(m):
    m.is_nestable = lambda S: True

def _nest_edges_reversed(m):
    # reordering the admissible edges leaves the MIN unchanged -> must SURVIVE
    orig = m.Sub.admissible_edges
    m.Sub.admissible_edges = lambda self: list(reversed(orig(self)))

def _nest_drift_band_ignored(m):
    # drift-class membership stops checking the LOWER band: sub-band streams pass
    # as members. RED at N11 (the sub-band fixture then reads "in class"; the
    # malformed-rejection sub-checks also stop raising).
    from fractions import Fraction as _F
    def bad(low_inc, up_inc, a, eps, C_i, C_S):
        return all(_F(x) <= _F(eps) * _F(C_S) for x in up_inc)
    m.in_drift_class = bad

def _nest_windows_permuted(m):
    # consistent reversal of BOTH window lists: membership and the horizon bound
    # are order-invariant on the fixtures (telescoping sums; the N10 steeper
    # fixture is non-constant and its crossing index is unchanged) -> SURVIVE.
    orig_in, orig_fc = m.in_drift_class, m.forced_crossing
    def rev(xs):
        return list(reversed(list(xs)))
    m.in_drift_class = lambda l, u, a, e, ci, cs: orig_in(rev(l), rev(u), a, e, ci, cs)
    m.forced_crossing = lambda l, u, a, e, ci, cs: orig_fc(rev(l), rev(u), a, e, ci, cs)


# ---- tower_transport mutators (Defs 4.8/4.10, Lemma 4.9, Prop 4.11) ----
def _tw_derived_as_identity(m):
    # derived restriction pinned to the identity regardless of the upper map.
    # RED at W1 first (the non-image-preserving rejection tooth no longer raises);
    # W3's constant-map check would also red if execution reached it.
    m.derived_restriction = lambda phi_u, nu, nu_prime: {lo: lo for lo in nu}

def _tw_carrier_map_noop(m):
    # carrier-coherence check bypassed: identity carrier data regardless of phi_l.
    # RED via W3/W7: the collapse never reaches the carrier; the chord case no
    # longer raises.
    m.induced_carrier_map = lambda M, Mp, phi_l: (
        {v: v for v in M.V}, {i: [(i, 1)] for i in range(len(M.E))})

def _tw_reversed_iteration(m):
    # rebuild derived_restriction iterating keys in reverse -- the derived map is
    # a dict, order-free, so every fixture must SURVIVE (invariant-preserving).
    def rev(phi_u, nu, nu_prime):
        m.check(len(set(nu.values())) == len(nu), "nu must be injective")
        m.check(len(set(nu_prime.values())) == len(nu_prime), "nu' must be injective")
        inv = {up: lo for lo, up in nu_prime.items()}
        phi_l = {}
        for lo in reversed(list(nu)):
            target = phi_u[nu[lo]]
            m.check(target in inv, "not image-preserving at this level")
            phi_l[lo] = inv[target]
        return phi_l
    m.derived_restriction = rev


# ---- pilot_entrainment mutators (OP 7.6 demonstrator) ------------------
def _pilot_effort_zeroed(m):
    # dynamics-side measurement pinned to zero. RED via N5: the sealed constant
    # degenerates to 0 and the sealed-c scoring rejects it.
    m.hold_station_work = lambda u, n_steps=None: 0.0

def _pilot_sigma_zeroed(m):
    # field-side circulation pinned to zero while norm/energy stay live. RED via N3:
    # the uniform profile can no longer attain a zero energy floor.
    orig = m.field_readings
    def bad(u, R=None, n=None):
        _, lam, en = orig(u, R, n)
        return 0.0, lam, en
    m.field_readings = bad


# ---- bridge_falsifier mutators (Proposition 3.8) -----------------------
def _bf_drop_zerospin(m):
    def bad(events, eps):
        lo = m.Fraction(0); hi = None
        for e in events:
            M, s = m._MS(e)
            if s == 0:
                continue                      # DROPPED the zero-spin control
            c_lo = (M - m.Fraction(eps)) / s; c_hi = (M + m.Fraction(eps)) / s
            lo = max(lo, c_lo); hi = c_hi if hi is None else min(hi, c_hi)
        if hi is None or lo > hi or hi <= 0:
            return None
        return (lo, hi)
    m.feasible_c_interval = bad

def _bf_interval_union(m):
    def bad(events, eps):
        lo = None; hi = None
        for e in events:
            M, s = m._MS(e)
            if s == 0:
                if M > m.Fraction(eps): return None
                continue
            c_lo = (M - m.Fraction(eps)) / s; c_hi = (M + m.Fraction(eps)) / s
            lo = c_lo if lo is None else min(lo, c_lo)   # UNION (min of lo) not intersection (max)
            hi = c_hi if hi is None else max(hi, c_hi)   # UNION (max of hi) not intersection (min)
        if hi is None or lo > hi or hi <= 0:
            return None
        return (lo, hi)
    m.feasible_c_interval = bad

def _bf_drop_multievent_guard(m):
    m.falsified_over_class = lambda events, eps: m.feasible_c_interval(events, eps) is None

def _bf_events_reordered(m):
    # feasibility is order-independent -> must SURVIVE
    orig = m.falsified_over_class
    m.falsified_over_class = lambda events, eps: orig(list(reversed(events)), eps)

def _bf_eps_guard_removed(m):
    # remove the eps >= 0 guard. RED via B8: a negative tolerance must be rejected.
    m._eps = lambda eps: m.Fraction(eps)

def _bf_lattice_floor_dropped(m):
    # accept k = 0 on the lattice (drop the positive floor). RED via B9's NEAR-ZERO
    # tooth: M = 0.05, c = 2, eps = 0.1 -> k = 0, |0.05 - 0| <= eps, so the floorless
    # mutant wrongly PASSES a maintenance-free reading (M = 1 would NOT discriminate:
    # |1 - 0| > eps falsifies under both).
    def bad(Ms, c, eps):
        c = m.Fraction(c); eps = m._eps(eps)
        m.check(eps < c / 2, "vacuous")
        for M in Ms:
            M = m.Fraction(M)
            k = round(M / c)
            if abs(M - c * k) > eps:      # floor k >= 1 DROPPED
                return False
        return True
    m.quantised_consistent = bad

def _gh_floors_zeroed(m):
    # zero out the derived floors. RED via P15: the attainment checks (concentration
    # == l1 floor, harmonic == L2 floor) fail against a zeroed floor.
    m.entrainment_floors = lambda sigma, cycle, weights=None: (m.Fraction(0), m.Fraction(0))

def _gh_floor_divides_by_multiplicity(m):
    # regress the norm-floor constant to min(w/|z|) (the pre-fix bug). RED via P15's
    # doubled-cycle fixture: it under-floors to 3 while concentration reads 6.
    orig = m.entrainment_floors
    def bad(sigma, cycle, weights=None):
        _, l2 = orig(sigma, cycle, weights)
        sigma = m.Fraction(sigma)
        c1 = None
        for ei, coeff in cycle.items():
            if coeff == 0:
                continue
            w = m.Fraction(1) if weights is None else m.Fraction(weights[ei])
            cand = w / abs(coeff)
            c1 = cand if c1 is None else min(c1, cand)
        return (c1 * abs(sigma), l2)
    m.entrainment_floors = bad

def _bf_floor_gate_noop(m):
    # derived-floor gate pinned to True. RED via B10: the impossible sub-floor
    # reading (Lambda < c1*|sigma| - eps) must FAIL the gate, not pass it.
    m.floor_consistent = lambda readings, c1, eps: True

def _bf_unbounded_as_falsified(m):
    # regress the unbounded-branch bug: treat the 'not a test' branch (lo, None) as
    # infeasible None -> an all-zero-sigma set wrongly reads FALSIFIED. Must RED (B7).
    orig = m.feasible_c_interval
    def bad(events, eps):
        r = orig(events, eps)
        return None if (r is not None and r[1] is None) else r
    m.feasible_c_interval = bad


def _bf_2ch_positivity_dropped(m):
    # the quadrant constraints erased from the two-channel system: the negative-solve
    # fixture (B12) wrongly becomes feasible. RED.
    orig = m._two_channel_constraints
    m._two_channel_constraints = lambda ev3, eps: [
        (a, b, c) for (a, b, c) in orig(ev3, eps)
        if not ((a, b) == (m.Fraction(-1), m.Fraction(0))
                or (a, b) == (m.Fraction(0), m.Fraction(-1)))]

def _bf_2ch_bands_onesided(m):
    # each event's LOWER band edge dropped (only M <= M_j + eps kept; the two
    # quadrant rows are kept): the incompatible B11 set wrongly becomes feasible. RED.
    orig = m._two_channel_constraints
    POS = ((m.Fraction(-1), m.Fraction(0)), (m.Fraction(0), m.Fraction(-1)))
    m._two_channel_constraints = lambda ev3, eps: [
        (a, b, c) for (a, b, c) in orig(ev3, eps)
        if (a, b) in POS or a > 0 or b > 0]

def _bf_2ch_constraints_permuted(m):
    # constraint order reversed: elimination is order-independent -> must SURVIVE.
    orig = m._two_channel_constraints
    m._two_channel_constraints = lambda ev3, eps: list(reversed(orig(ev3, eps)))


# ---- funnel_channels mutators --------------------------------------------
def _fc_face_dropped(m):
    # a declared 2-cell silently lost: the Stokes consistency sum loses one face's
    # curl and the identity breaks on the non-closed cochain. Must RED (W1).
    orig = m.make_faces
    m.make_faces = lambda n: orig(n)[1:]

def _fc_tariff_flattened(m):
    # substrate-dependence of the tariff erased (one c for every mu): pooling then
    # WRONGLY fits a single constant and the pooled-class rejection goes dark. RED (W2).
    m.C_OF_MU = {mu: m.Fraction(1) for mu in m.C_OF_MU}

def _fc_death_witness_zeroed(m):
    # the pre-carrier witness silently zeroed: the live-period precondition of the
    # W-death fixture must catch it (and transport_classify's own witness-bearing
    # guard backs it up). RED (W3).
    orig = m.death_fixture
    def bad():
        pre, post, gamma, eta, vmap, emap, eta_post = orig()
        return pre, post, gamma, {k: m.Fraction(0) for k in eta}, vmap, emap, eta_post
    m.death_fixture = bad

def _fc_spokes_reoriented(m):
    # consistent reorientation of the radial spokes (edge directions flipped AND the
    # declared face multiplicities flipped with them): a pure orientation convention;
    # every reading is invariant -- must SURVIVE.
    orig_ann, orig_faces = m.make_annulus, m.make_faces
    def ann(n):
        g, z_in, z_out = orig_ann(n)
        edges = list(g.E)
        for k in range(2 * n, 3 * n):
            t, h = edges[k]
            edges[k] = (h, t)
        return m.Graph(g.V, edges), z_in, z_out
    def faces(n):
        return [{ei: (-c if ei >= 2 * n else c) for ei, c in f.items()}
                for f in orig_faces(n)]
    m.make_annulus = ann
    m.make_faces = faces


# ---- fano_channel mutators (Definition 5.3 / Proposition 5.4) ----
def _fa_log2_slack_dropped(m):
    # the floor's binary-entropy slack (log 2) is dropped: the "floor" then
    # OVERSHOOTS the exact MAP error on the useless channel -- FA2 must go red.
    def bad(prior, P):
        p, rows = m.validate_channel(prior, P)
        return ((m.entropy_prior(p) - m.mutual_information(p, rows))
                / m.math.log(len(p)))
    m.fano_floor = bad

def _fa_labels_permuted(m):
    # consistent relabelling of the source alphabet (prior and rows reversed
    # together): MAP error and mutual information are label-invariant -> SURVIVE.
    orig_me, orig_mi = m.map_error, m.mutual_information
    def perm(prior, P):
        p, rows = list(prior), list(P)
        if len(rows) != len(p):
            return p, rows      # malformed shape: hand through for the validator to reject
        idx = list(range(len(p)))[::-1]
        return [p[i] for i in idx], [rows[i] for i in idx]
    m.map_error = lambda prior, P: orig_me(*perm(prior, P))
    m.mutual_information = lambda prior, P: orig_mi(*perm(prior, P))


REGISTRY = [
    # (module, name, mutator, expected)
    ("graph_hodge", "components->1",                    _gh_components,           "RED"),
    ("graph_hodge", "pushforward collapse (lose m)",    _gh_pushforward_collapse, "RED"),
    ("graph_hodge", "period->0",                        _gh_period_zero,          "RED"),
    ("graph_hodge", "period->abs(cycle coeff)",         _gh_period_abs,           "RED"),
    ("graph_hodge", "fundamental_cycles->[]",           _gh_fundcycles_empty,     "RED"),
    ("graph_hodge", "pullback drop sign",               _gh_pullback_drop_sign,   "RED"),
    ("graph_hodge", "_tree_path flip sign",             _gh_treepath_flip,        "RED"),
    ("graph_hodge", "check_graph_map -> no-op",         _gh_cgm_noop,             "RED"),
    ("graph_hodge", "cycle_class_coeffs -> no reconstruct", _gh_ccc_norecon,      "RED"),
    ("graph_hodge", "rank ignores dependence",          _gh_rank_ignores_dependence, "RED"),
    ("graph_hodge", "harmonic skips projection",        _gh_harmonic_skip_projection, "RED"),
    ("graph_hodge", "harmonic ignores weights",         _gh_harmonic_ignores_weights, "RED"),
    ("graph_hodge", "norm collapsed into period",       _gh_norm_as_period,       "RED"),
    ("graph_hodge", "entrainment floors zeroed",        _gh_floors_zeroed,        "RED"),
    ("graph_hodge", "norm floor divides by |z|",        _gh_floor_divides_by_multiplicity, "RED"),
    ("graph_hodge", "coboundary sign flip (-df)",       _gh_coboundary_flip,      "SURVIVE"),
    ("boundary_witness", "check_H_a -> no-op",              _bw_H_a_noop,             "RED"),
    ("boundary_witness", "check_H_b -> no-op",              _bw_H_b_noop,             "RED"),
    ("boundary_witness", "cohomologous -> always True",     _bw_cohomologous_true,    "RED"),
    ("boundary_witness", "is_noncontractible -> always True", _bw_noncontractible_true, "RED"),
    ("boundary_witness", "H-b -> strict pointwise equality", _bw_strict_H_b,           "RED"),
    ("boundary_witness", "gamma_i guard removed",            _bw_gamma_guard_removed,  "RED"),
    ("boundary_witness", "Prop-3.7 identity check removed",  _bw_identity_removed,     "SURVIVE"),
    ("core_reduction", "transport always-survives",         _cr_survives_always,      "RED"),
    ("core_reduction", "h1-trivial-flag always False",      _cr_h1flag_false,         "RED"),
    ("core_reduction", "retention pinned to 1",             _cr_retention_always_full,"RED"),
    ("core_reduction", "cycle-validity check removed",      _cr_cyclecheck_removed,   "RED"),
    ("core_reduction", "witness-bearing precond removed",   _cr_precond_removed,      "RED"),
    ("nestability", "min-burden -> max-burden",             _nest_min_to_max,         "RED"),
    ("nestability", "is_nestable -> always True",           _nest_isnestable_true,    "RED"),
    ("nestability", "admissible-edges reversed",            _nest_edges_reversed,     "SURVIVE"),
    ("nestability", "drift lower band ignored",             _nest_drift_band_ignored, "RED"),
    ("nestability", "drift windows consistently reversed",  _nest_windows_permuted,   "SURVIVE"),
    ("bridge_falsifier", "zero-spin control dropped",       _bf_drop_zerospin,        "RED"),
    ("bridge_falsifier", "c-interval union not intersect",  _bf_interval_union,       "RED"),
    ("bridge_falsifier", "multi-event (>=2) guard dropped", _bf_drop_multievent_guard,"RED"),
    ("bridge_falsifier", "unbounded treated as falsified",  _bf_unbounded_as_falsified,"RED"),
    ("bridge_falsifier", "eps >= 0 guard removed",          _bf_eps_guard_removed,    "RED"),
    ("bridge_falsifier", "lattice floor (k>=1) dropped",    _bf_lattice_floor_dropped,"RED"),
    ("bridge_falsifier", "derived-floor gate -> no-op",     _bf_floor_gate_noop,      "RED"),
    ("bridge_falsifier", "events reordered",                _bf_events_reordered,     "SURVIVE"),
    ("bridge_falsifier", "2ch quadrant constraints dropped", _bf_2ch_positivity_dropped, "RED"),
    ("bridge_falsifier", "2ch lower band edges dropped",    _bf_2ch_bands_onesided,   "RED"),
    ("bridge_falsifier", "2ch constraint order reversed",   _bf_2ch_constraints_permuted, "SURVIVE"),
    ("pilot_entrainment", "dynamics effort pinned to 0",    _pilot_effort_zeroed,     "RED"),
    ("pilot_entrainment", "field circulation pinned to 0",  _pilot_sigma_zeroed,      "RED"),
    ("tower_transport", "derived restriction -> identity",  _tw_derived_as_identity,  "RED"),
    ("tower_transport", "carrier map -> unchecked no-op",   _tw_carrier_map_noop,     "RED"),
    ("tower_transport", "derived map built in reverse order", _tw_reversed_iteration, "SURVIVE"),
    ("funnel_channels", "declared face dropped from complex", _fc_face_dropped,      "RED"),
    ("funnel_channels", "tariff flattened across substrates", _fc_tariff_flattened,  "RED"),
    ("funnel_channels", "death witness zeroed (precondition)", _fc_death_witness_zeroed, "RED"),
    ("funnel_channels", "radial spokes consistently reoriented", _fc_spokes_reoriented, "SURVIVE"),
    ("fano_channel", "floor log-2 slack dropped",           _fa_log2_slack_dropped,   "RED"),
    ("fano_channel", "source labels consistently permuted", _fa_labels_permuted,      "SURVIVE"),
]


def run(verbose=True):
    """Run the audit. Returns list of (module, name, expected, actual, ok)."""
    rows = []
    for module, name, mut, expected in REGISTRY:
        actual, detail = _run_one(module, mut)
        ok = (actual == expected)
        rows.append((module, name, expected, actual, ok))
        if verbose:
            tag = "ok" if ok else "*** MISMATCH ***"
            print("  %-12s %-38s expect %-8s got %-8s %s  %s"
                  % (module, name, expected, actual, tag, detail))
    return rows


def selftest():
    # baseline: every target module's own selftest must pass unmutated
    for mod_name in ("graph_hodge", "boundary_witness", "core_reduction",
                     "nestability", "bridge_falsifier", "pilot_entrainment",
                     "tower_transport", "funnel_channels", "fano_channel"):
        importlib.reload(importlib.import_module("graph_hodge"))
        mod = importlib.import_module(mod_name)
        if mod_name != "graph_hodge":
            importlib.reload(mod)
        mod.selftest()
    rows = run(verbose=False)
    bad = [(mo, n, e, a) for (mo, n, e, a, ok) in rows if not ok]
    check(not bad, "teeth_audit: %d mutation(s) deviated from expected: %r" % (len(bad), bad))
    # corpus_gate carries its own synthetic-fixture teeth: fold them into the ONE gate
    # so `python teeth_audit.py` is the single mutation entry point for the bundle.
    import corpus_gate
    check(corpus_gate.run_teeth(verbose=False), "corpus_gate teeth FAILED")
    reds = sum(1 for r in rows if r[3] == "RED")
    survives = sum(1 for r in rows if r[3] == "SURVIVE")
    return ["teeth_audit: %d rows, %d RED (teeth) + %d SURVIVE (invariant-preserving), "
            "all as predicted; corpus_gate teeth folded in: PASS" % (len(rows), reds, survives)]


if __name__ == "__main__":
    print("baseline: target selftests pass unmutated")
    rows = run(verbose=True)
    bad = [r for r in rows if not r[4]]
    import corpus_gate
    ok_cg = corpus_gate.run_teeth(verbose=False)
    print("  corpus_gate    synthetic-fixture teeth (folded in)   %s" % ("PASS" if ok_cg else "FAIL"))
    print("\nteeth_audit: %s" % ("PASS (all as predicted)"
                                 if (not bad and ok_cg) else "FAIL: %d mismatch" % (len(bad) + (0 if ok_cg else 1))))
    check(not bad and ok_cg, "teeth_audit FAILED")
