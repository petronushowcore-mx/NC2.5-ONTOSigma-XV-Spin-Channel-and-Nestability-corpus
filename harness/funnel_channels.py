"""funnel_channels.py -- discrete mirrors for the table-top protocol companion
("Two Funnels, One Spin").

REGISTER. The companion document's depth laws (the +2 paraboloid, the -2 free-vortex
depression, the Rankine half-split) are DOCUMENT-LEVEL derivations of classical fluid
mechanics; this module does NOT verify that calculus. It verifies the protocol's
discrete graph mirrors and its sealed-constant discipline -- the parts that admit
exact finite verification:

  W1  the two-channel dichotomy on an annulus graph with DECLARED quad faces
      (glass-1-type cochain: face curls non-zero, ring periods differ;
       glass-2-type cochain: all face curls zero, ring periods equal and non-zero);
  W2  the substrate-tariff discipline (per-substrate sealed c passes with holdout;
      pooling substrates into one class is REJECTED as a mis-declaration; and a
      regime-dependent c within ONE substrate is a genuine Proposition 3.8(b)
      falsifier of the linear form);
  W3  the W-death reading: pre-carrier b1 = 1 with a live period, post-carrier
      H^1-trivial (the Theorem 3(ii) hypothesis, map-free), plus a declared
      collapse map whose transport verdict is ANNIHILATING while the source
      magnitude reading stays alive;
  W4  rejection controls on the fixture-local arithmetic.

HONEST TYPING OF THE FIXTURES.
- On the BARE annulus graph the two ring cycles are INDEPENDENT homology classes
  (b1 = n + 1); they become homologous only in the 2-complex whose quad faces are
  DECLARED here as fixture data. "Closed" below means: every declared face curl
  vanishes. The discrete Stokes identity (sum of face curls = inner-ring period
  minus outer-ring period) is a telescoping CONSISTENCY IDENTITY holding for every
  cochain -- the discriminating content is DIFFERENT-vs-EQUAL ring periods.
- The W3 collapse map is the finite-state STAND-IN for the physical event's map
  (the inclusion of the annular domain into the filled, simply connected domain):
  a graph cannot receive an inclusion into an H^1-trivial target that fills the
  hole -- that needs 2-cells -- so the stand-in collapses the cycle instead, and
  the map-free b1 comparison carries the Theorem 3(ii) hypothesis itself.

Stdlib only, -O-safe. Reuses graph_hodge, core_reduction, bridge_falsifier.
"""
from fractions import Fraction

from graph_hodge import Graph, check, period, cycle_norm
import core_reduction as cr
import bridge_falsifier as bf

F = Fraction


# ---- annulus fixture (declared 2-complex) --------------------------------
def make_annulus(n):
    """Annulus graph: inner ring i0..i{n-1}, outer ring o0..o{n-1}, radial spokes.
    Edge indexing: inner ring edges 0..n-1, outer ring edges n..2n-1, spokes
    (i_k, o_k) at 2n..3n-1. Returns (graph, z_inner, z_outer)."""
    check(n >= 3, "annulus needs n >= 3")
    verts = ["i%d" % k for k in range(n)] + ["o%d" % k for k in range(n)]
    edges = ([("i%d" % k, "i%d" % ((k + 1) % n)) for k in range(n)]
             + [("o%d" % k, "o%d" % ((k + 1) % n)) for k in range(n)]
             + [("i%d" % k, "o%d" % k) for k in range(n)])
    z_in = {k: 1 for k in range(n)}
    z_out = {n + k: 1 for k in range(n)}
    return Graph(verts, edges), z_in, z_out


def make_faces(n):
    """The DECLARED quad 2-cells of the annulus fixture, as 1-chains (their oriented
    boundaries): face k walks i_k -> i_{k+1} -> o_{k+1} -> o_k -> i_k, i.e.
    {inner_k: +1, spoke_{k+1}: +1, outer_k: -1, spoke_k: -1}. Summing over k the
    spokes telescope away and sum(faces) = z_inner - z_outer as chains -- the
    discrete Stokes identity used in W1. Fixture DATA, not graph structure: the
    bare graph has no 2-cells."""
    return [{k: 1, 2 * n + (k + 1) % n: 1, n + k: -1, 2 * n + k: -1}
            for k in range(n)]


def validate_faces(graph, faces):
    """Fixture-local guard: every declared face is a 1-chain over EXISTING edge
    indices with non-zero integer multiplicities (period() silently reads absent
    indices as 0, so an out-of-range face would corrupt the Stokes sum silently)."""
    ne = len(graph.E)
    for f in faces:
        check(len(f) > 0, "declared face must be a non-empty 1-chain")
        for ei, coeff in f.items():
            check(isinstance(ei, int) and 0 <= ei < ne,
                  "declared face references a non-existent edge index %r" % (ei,))
            check(isinstance(coeff, int) and coeff != 0,
                  "declared face multiplicity must be a non-zero integer")
    return True


def omega_solid(n):
    """Glass-1-type cochain (solid-body mirror): ring values grow outward
    (inner 1, outer 4 per edge), spokes 0 -- circulation grows with the loop, the
    loop-dependent reading of a non-closed field."""
    w = {k: F(1) for k in range(n)}
    w.update({n + k: F(4) for k in range(n)})
    return w


def omega_free(n, gamma):
    """Glass-2-type cochain (free-vortex mirror): the same period gamma on both
    rings (gamma/n per ring edge), spokes 0 -- loop-invariant, closed with respect
    to every declared face."""
    w = {k: F(gamma, n) for k in range(n)}
    w.update({n + k: F(gamma, n) for k in range(n)})
    return w


# ---- substrate-tariff fixture --------------------------------------------
# Three substrates (viscosity labels) with three different material tariffs c(mu):
# the same circulation costs differently on different substrates.
C_OF_MU = {1: F(1, 2), 3: F(3, 2), 10: F(5)}
CAL_SIGMAS = [F(2), F(3)]      # calibration events per substrate
HOLDOUT_SIGMA = F(5)           # disjoint holdout event per substrate
EPS = F(1, 100)


def tariff_events(mu, sigmas):
    """Events (M, |sigma|) generated by the substrate's own tariff: M = c(mu)*|sigma|."""
    c = C_OF_MU[mu]
    return [(c * s, s) for s in sigmas]


# Shear-thinning fixture: within ONE substrate the effective tariff drops with the
# reading (c(2) = 1, c(6) = 1/2) -- a regime-dependent c, the honest falsifier of
# the linear one-constant form (Proposition 3.8(b)).
SHEAR_EVENTS = [(F(2), F(2)), (F(3), F(6))]


# ---- W-death fixture ------------------------------------------------------
DEATH_GAMMA = F(4)


def death_fixture():
    """Pre-carrier: the ring C_4 (the annular domain's homotopy model) with a live
    witness; post-carrier: a tree (the filled domain's model, H^1-trivial); plus the
    declared collapse stand-in map (see module docstring). Returns
    (pre, post, gamma, eta, vmap, emap, eta_post)."""
    pre = Graph(["v0", "v1", "v2", "v3"],
                [("v0", "v1"), ("v1", "v2"), ("v2", "v3"), ("v3", "v0")])
    post = Graph(["a", "b"], [("a", "b")])
    gamma = {0: 1, 1: 1, 2: 1, 3: 1}
    eta = {k: F(DEATH_GAMMA, 4) for k in range(4)}   # period DEATH_GAMMA on the cycle
    vmap = {"v0": "a", "v1": "b", "v2": "a", "v3": "b"}
    emap = {0: [(0, 1)], 1: [(0, -1)], 2: [(0, 1)], 3: [(0, -1)]}
    eta_post = {0: F(1)}
    return pre, post, gamma, eta, vmap, emap, eta_post


# ---- selftest --------------------------------------------------------------
def selftest():
    results = []
    n = 6

    # --- W1: annulus two-channel dichotomy on the declared 2-complex -------
    g, z_in, z_out = make_annulus(n)
    faces = make_faces(n)
    validate_faces(g, faces)
    check(g.b1() == n + 1,
          "W1: bare annulus graph must have b1 = n+1 (rings independent WITHOUT faces)")
    for name, om in (("solid", omega_solid(n)), ("free", omega_free(n, DEATH_GAMMA))):
        stokes = sum(period(om, f) for f in faces)
        check(stokes == period(om, z_in) - period(om, z_out),
              "W1: discrete Stokes identity broken on %s cochain" % name)
    om1 = omega_solid(n)
    curls1 = [period(om1, f) for f in faces]
    check(any(c != 0 for c in curls1),
          "W1: glass-1 cochain must be NON-closed (some declared face curl != 0)")
    check(period(om1, z_in) != period(om1, z_out),
          "W1: glass-1 ring periods must DIFFER (loop-dependent reading)")
    om2 = omega_free(n, DEATH_GAMMA)
    curls2 = [period(om2, f) for f in faces]
    check(all(c == 0 for c in curls2),
          "W1: glass-2 cochain must be closed w.r.t. every declared face")
    p_in, p_out = period(om2, z_in), period(om2, z_out)
    check(p_in == p_out and p_in == DEATH_GAMMA and p_in != 0,
          "W1: glass-2 ring periods must be EQUAL and non-zero (witness alive)")
    results.append("W1 annulus dichotomy: non-closed differs, closed agrees (period %s): OK"
                   % p_in)

    # --- W2: substrate tariff -- per-substrate passes, pooling rejected ----
    for mu in sorted(C_OF_MU):
        cal = tariff_events(mu, CAL_SIGMAS)
        check(bf.consistent_with_sealed_c(cal, C_OF_MU[mu], EPS),
              "W2: substrate mu=%s must fit its own sealed tariff" % mu)
        check(bf.test_sealed_c_on_events(C_OF_MU[mu],
                                         tariff_events(mu, [HOLDOUT_SIGMA]), EPS),
              "W2: substrate mu=%s must pass its disjoint holdout" % mu)
    pooled = []
    for mu in sorted(C_OF_MU):
        pooled += tariff_events(mu, CAL_SIGMAS)
    check(bf.falsified_over_class(pooled, EPS),
          "W2: pooling three substrates into one class must be REJECTED "
          "(no single c fits -- a mis-declaration, not a law failure)")
    check(bf.falsified_over_class(SHEAR_EVENTS, EPS),
          "W2: regime-dependent c within one substrate must falsify the "
          "one-constant linear form (Proposition 3.8(b))")
    results.append("W2 substrate tariff: per-mu sealed+holdout pass, pooled class "
                   "rejected, shear-thinning drift falsifies: OK")

    # --- W3: W-death -- map-free 3(ii) hypothesis + declared stand-in ------
    pre, post, gamma, eta, vmap, emap, eta_post = death_fixture()
    check(pre.b1() == 1 and period(eta, gamma) == DEATH_GAMMA,
          "W3: pre-carrier must be b1=1 with a live period")
    check(cr.h1_trivial_target_annihilates(post),
          "W3: post-carrier must be H^1-trivial, b1 = 0 (the Theorem 3(ii) hypothesis)")
    verdict, survives = cr.transport_classify(pre, post, vmap, emap, [gamma],
                                              eta, eta_post)
    check(verdict == "ANNIHILATING" and survives == [False],
          "W3: declared collapse stand-in must be ANNIHILATING, got %s" % verdict)
    check(cycle_norm(eta, gamma) > 0,
          "W3: source magnitude reading must stay alive (norm > 0) while the "
          "period dies -- the magnitude-monitor blindness")
    results.append("W3 W-death: b1 1->0, H^1-trivial post, stand-in ANNIHILATING, "
                   "magnitude alive: OK")

    # --- W4: rejection controls on fixture-local arithmetic ----------------
    bad = dict(omega_free(n, DEATH_GAMMA))
    bad[0] = 0.5
    try:
        period(bad, z_in)
        raise RuntimeError("W4: float cochain value must be rejected")
    except AssertionError:
        pass
    try:
        validate_faces(g, [{99: 1}])
        raise RuntimeError("W4: out-of-range face index must be rejected")
    except AssertionError:
        pass
    try:
        validate_faces(g, [{0: 0}])
        raise RuntimeError("W4: zero face multiplicity must be rejected")
    except AssertionError:
        pass
    results.append("W4 rejection controls: float cochain, out-of-range face, "
                   "zero multiplicity all rejected: OK")

    return results


if __name__ == "__main__":
    for line in selftest():
        print(line)
    print("funnel_channels selftest: 4/4 OK")
