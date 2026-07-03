"""graph_hodge.py -- finite-state cohomology core for ONTO-Sigma XV harnesses.

Stdlib only (fractions.Fraction). -O-safe (uses check(), not assert).

Provides the induced-H^1-map machinery that Proposition 3.7 (Boundary-Witness
Compatibility), Proposition 4.3 (Witness Transport Kernel), and XV.3 (Core-Reduction)
depend on:

  - first Betti number b1 = |E| - |V| + components (union-find)
  - a cycle-space basis: fundamental cycles from a spanning forest
  - the period pairing <omega, z> = signed edge-sum of a 1-cochain around an
    oriented 1-cycle
  - the coboundary delta f of a vertex-function, and the built-in self-test
    <delta f, z> = 0 for every cycle z (discrete analogue of the period being a
    homology pairing -- companion Lemma 3.3, net-circulation mode)
  - the induced map phi^* on 1-cochains from a graph map (vertex map + edge ->
    edge-path), and phi_* on chains, which are mutual transposes under the
    pairing (companion Lemma 3.6): <phi^* alpha, z> = <alpha, phi_* z>.

This module ENFORCES the declared structural relations and SUPPLIES the falsifiers
of essay section 6; it does NOT prove XV.2 (a declared structural law). It checks
that declared relations are internally consistent and that wrong parameterisations
are detected.

Conventions
-----------
Vertices: any hashable. Edges: an ordered list of (tail, head) ORIENTED pairs;
an edge is referenced by its index in that list. A 1-cochain is a dict
{edge_index: Fraction}. A 1-chain / cycle is a dict {edge_index: int} of signed
multiplicities along the edge orientation (+1 forward, -1 backward). A graph map
G -> G' is (vmap, emap): vmap maps vertices, emap maps each edge_index of G to a
list of (edge_index_in_Gprime, sign) -- the oriented edge-path phi(e).
"""

from fractions import Fraction
from collections import deque
from collections.abc import Mapping


def check(cond, msg="check failed"):
    """Unconditional verification (assert-equivalent that survives `python -O`)."""
    if not cond:
        raise AssertionError(msg)


class Graph:
    def __init__(self, vertices, edges):
        self.V = list(vertices)
        self.E = [tuple(e) for e in edges]  # oriented (tail, head)
        vs = set(self.V)
        check(len(vs) == len(self.V), "duplicate vertices")
        for (u, v) in self.E:
            check(u in vs and v in vs, "edge endpoint not in V: %r" % ((u, v),))
        self._vi = {x: i for i, x in enumerate(self.V)}

    # -- connectivity -----------------------------------------------------
    def _uf(self):
        parent = list(range(len(self.V)))

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        for (u, v) in self.E:
            ra, rb = find(self._vi[u]), find(self._vi[v])
            if ra != rb:
                parent[ra] = rb
        return find

    def components(self):
        find = self._uf()
        return len({find(i) for i in range(len(self.V))})

    def b1(self):
        """First Betti number = cycle-space dimension = |E| - |V| + components."""
        return len(self.E) - len(self.V) + self.components()

    # -- cycle-space basis ------------------------------------------------
    def spanning_forest(self):
        """Return the set of edge-indices forming a spanning forest (tree per component)."""
        parent = list(range(len(self.V)))

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        forest = set()
        for i, (u, v) in enumerate(self.E):
            ru, rv = find(self._vi[u]), find(self._vi[v])
            if ru != rv:
                parent[ru] = rv
                forest.add(i)
        return forest

    def _tree_path(self, forest, src, dst):
        """Signed edge-index path in the forest from src to dst: list of (edge_index, sign)."""
        adj = {}
        for i in forest:
            (u, v) = self.E[i]
            adj.setdefault(u, []).append((v, i, +1))
            adj.setdefault(v, []).append((u, i, -1))
        prev = {src: None}
        q = deque([src])
        while q:
            x = q.popleft()
            if x == dst:
                break
            for (nbr, ei, sgn) in adj.get(x, []):
                if nbr not in prev:
                    prev[nbr] = (x, ei, sgn)
                    q.append(nbr)
        check(dst in prev, "tree path: dst unreachable (endpoints in different components)")
        path = []
        cur = dst
        while prev[cur] is not None:
            (p, ei, sgn) = prev[cur]
            path.append((ei, sgn))
            cur = p
        path.reverse()
        return path

    def fundamental_cycles(self):
        """A basis of H_1: one fundamental cycle per chord (chord + tree path back)."""
        forest = self.spanning_forest()
        cycles = []
        for i, (u, v) in enumerate(self.E):
            if i in forest:
                continue
            cyc = {i: +1}
            for (ei, sgn) in self._tree_path(forest, v, u):
                cyc[ei] = cyc.get(ei, 0) + sgn
            cyc = {k: c for k, c in cyc.items() if c != 0}
            cycles.append(cyc)
        return cycles

    def check_graph_map(self, gprime, vmap, emap):
        """Verify (vmap, emap): self -> gprime is a CONSISTENT graph map.

        vmap must be TOTAL on self.V (a dict is checked for totality; a callable is
        trusted on its domain) and land inside gprime.V. Each edge (t,h) of self must
        be EXPLICITLY present in emap -- a missing key is a declaration error, distinct
        from an explicit empty path -- and map to a contiguous oriented edge-path in
        gprime from vmap(t) to vmap(h); each step's sign is exactly +1 (forward
        tail->head) or -1 (backward head->tail). An explicit EMPTY path is allowed only
        when vmap(t) == vmap(h) (edge collapsed to a vertex).
        Raises AssertionError on any inconsistency; returns True on success.
        """
        is_map = isinstance(vmap, Mapping)
        vf = vmap.__getitem__ if is_map else vmap
        tgt = set(gprime.V)
        for v in self.V:
            check((not is_map) or (v in vmap),
                  "graph map: vmap not total on V (missing vertex %r)" % (v,))
            check(vf(v) in tgt,
                  "graph map: vmap image of %r is %r, not a vertex of the target" % (v, vf(v)))
        for i, (t, h) in enumerate(self.E):
            check(i in emap,
                  "graph map: edge %r (index %d) missing from emap (a missing key is a "
                  "declaration error; use an explicit [] for a deliberate collapse)" % ((t, h), i))
            path = emap[i]
            src, dst = vf(t), vf(h)
            if not path:
                check(src == dst,
                      "graph map: edge %r maps to empty path but endpoints differ (%r != %r)"
                      % ((t, h), src, dst))
                continue
            cur = src
            for (ep, sgn) in path:
                check(sgn in (1, -1),
                      "graph map: edge %r has step sign %r; must be exactly +1 or -1" % ((t, h), sgn))
                check(isinstance(ep, int) and 0 <= ep < len(gprime.E),
                      "graph map: edge %r path step targets edge index %r, not an edge of the target"
                      % ((t, h), ep))
                (a, b) = gprime.E[ep]
                start, end = (a, b) if sgn > 0 else (b, a)
                check(cur == start,
                      "graph map: non-contiguous path for edge %r (have %r, need %r)"
                      % ((t, h), cur, start))
                cur = end
            check(cur == dst,
                  "graph map: edge %r path ends at %r, expected vmap(head)=%r" % ((t, h), cur, dst))
        return True


# -- pairings and maps ----------------------------------------------------
def period(omega, cycle):
    """<omega, z> = sum_e omega(e) * z(e) -- signed edge-sum of the 1-cochain around z.

    Rejects float cochain values: the harness's verdicts are exact equalities over
    Fraction; a float value would silently degrade the pairing to binary floating
    point (0.1 + 0.2 != 0.3) and corrupt equality-based falsifiers."""
    total = Fraction(0)
    for ei, coeff in cycle.items():
        v = omega.get(ei, Fraction(0))
        check(not isinstance(v, float),
              "period: float cochain value on edge %r -- use Fraction (exact), not float" % (ei,))
        total += v * coeff
    return total


def cycle_norm(omega, cycle, weights=None):
    """The NORM functional along a cycle: sum_e |omega(e)| * |z(e)| * w(e) -- the
    local-channel magnitude reading (counting measure w = 1 by default; a declared
    edge-weight mapping otherwise). Unlike the period it is NOT a homology pairing:
    it is gauge-SENSITIVE (omega + delta f changes it) and cannot spuriously cancel."""
    total = Fraction(0)
    for ei, coeff in cycle.items():
        v = omega.get(ei, Fraction(0))
        check(not isinstance(v, float),
              "cycle_norm: float cochain value on edge %r -- use Fraction" % (ei,))
        w = Fraction(1) if weights is None else Fraction(weights[ei])
        total += abs(v) * abs(coeff) * w
    return total


def entrainment_floors(sigma, cycle, weights=None):
    """Proposition 3.14 (Minimal-Entrainment Bound): the two DERIVED floors on a
    declared locus (Gamma, w) for any realisation carrying net-circulation period sigma.

      l1_floor = (min_e w(e)) * |sigma|
          floor of the declared NORM reading (sum |omega~|*|z|*w along the cycle,
          i.e. cycle_norm), valid for arbitrary integer multiplicities z(e); attained
          by concentrating the period on a cheapest-measure edge, single-signed;
      l2_floor = sigma^2 / L,  L = sum_e z(e)^2 / w(e)
          weighted quadratic (energy) floor; attained UNIQUELY by the w-harmonic
          profile sigma * z / (w * L) -- the cycle reading of Proposition 3.13.

    Exact over Fraction. These are lower bounds every period-sigma realisation must
    meet (triangle inequality / Cauchy-Schwarz) -- a derived FLOOR beneath the declared
    Bridge Law, NOT a derivation of the law itself for general deployments."""
    check(not isinstance(sigma, float),
          "entrainment_floors: sigma must be Fraction/int (exact), not float")
    sigma = Fraction(sigma)
    c1 = None
    L = Fraction(0)
    for ei, coeff in cycle.items():
        if coeff == 0:
            continue
        w = Fraction(1) if weights is None else Fraction(weights[ei])
        check(w > 0, "entrainment_floors: weights must be > 0")
        c1 = w if c1 is None else min(c1, w)
        L += Fraction(coeff * coeff) / w
    check(c1 is not None, "entrainment_floors: cycle must traverse at least one edge")
    return (c1 * abs(sigma), sigma * sigma / L)


def coboundary(graph, f):
    """delta f: edge_index -> f(head) - f(tail). `f` is a Mapping {vertex: value} or a callable."""
    if isinstance(f, Mapping):
        fv = f.__getitem__
    elif callable(f):
        fv = f
    else:
        raise TypeError("coboundary: f must be a Mapping or a callable, got %r" % type(f))
    d = {}
    for i, (u, v) in enumerate(graph.E):
        d[i] = Fraction(fv(v)) - Fraction(fv(u))
    return d


def induced_pullback(emap, omega_prime):
    """phi^* omega' on G: (phi^* omega')(e) = <omega', emap(e)> (period along the edge-path)."""
    out = {}
    for e, signed_edges in emap.items():
        val = Fraction(0)
        for (ep, sgn) in signed_edges:
            val += omega_prime.get(ep, Fraction(0)) * sgn
        out[e] = val
    return out


def induced_pushforward(emap, cycle):
    """phi_* z: the image chain in G'."""
    out = {}
    for e, coeff in cycle.items():
        for (ep, sgn) in emap.get(e, []):
            out[ep] = out.get(ep, 0) + coeff * sgn
    return {k: c for k, c in out.items() if c != 0}


def rank_of_cycles(graph, chains):
    """Rank over Q of the given 1-cycles as classes in H_1(graph) -- the number of
    LINEARLY INDEPENDENT classes among them. This is the load-bearing quantity of the
    witness-capacity bound (companion Proposition 4.6): many chains can be non-zero
    yet all multiples of one generator (rank 1)."""
    vecs = []
    forest = graph.spanning_forest()
    chords = [i for i in range(len(graph.E)) if i not in forest]
    for ch in chains:
        coeffs = cycle_class_coeffs(graph, ch)
        vecs.append([Fraction(coeffs.get(j, 0)) for j in range(len(chords))])
    # Gaussian elimination over Fraction
    rank, ncols = 0, len(chords)
    rows = [v[:] for v in vecs]
    col = 0
    for col in range(ncols):
        piv = None
        for r in range(rank, len(rows)):
            if rows[r][col] != 0:
                piv = r
                break
        if piv is None:
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        pv = rows[rank][col]
        for r in range(len(rows)):
            if r != rank and rows[r][col] != 0:
                factor = rows[r][col] / pv
                rows[r] = [a - factor * b for a, b in zip(rows[r], rows[rank])]
        rank += 1
    return rank


def harmonic_representative(graph, omega, weights=None):
    """The discrete Hodge split on a graph: omega = delta f + h with h orthogonal to
    every coboundary under the (weighted) inner product <a,b>_w = sum_e w(e)a(e)b(e)
    -- equivalently the weighted divergence of h vanishes at every vertex. h is THE
    harmonic representative of [omega]: it has the same periods and, among all
    representatives omega + delta g, it UNIQUELY minimises the weighted L2-magnitude
    (companion Proposition 3.13). Exact over Fraction: solves the weighted graph-
    Laplacian normal equations, pinning one vertex per component (the constant kernel).
    Self-loops carry delta f = 0, so their omega-value passes to h unchanged."""
    n = len(graph.V)
    vi = graph._vi
    w = {}
    for i in range(len(graph.E)):
        w[i] = Fraction(1) if weights is None else Fraction(weights[i])
        check(w[i] > 0, "harmonic_representative: weights must be > 0")
    for i in range(len(graph.E)):
        v = omega.get(i, Fraction(0))
        check(not isinstance(v, float),
              "harmonic_representative: float cochain value on edge %d -- use Fraction" % i)
    # weighted Laplacian L and divergence rhs: L f = div(omega)
    L = [[Fraction(0)] * n for _ in range(n)]
    rhs = [Fraction(0)] * n
    for i, (u, v) in enumerate(graph.E):
        if u == v:
            continue                     # self-loop: no contribution to delta / div
        a, b = vi[u], vi[v]              # edge a -> b ; delta f(e) = f(b) - f(a)
        L[b][b] += w[i]; L[a][a] += w[i]
        L[b][a] -= w[i]; L[a][b] -= w[i]
        val = Fraction(omega.get(i, Fraction(0)))
        rhs[b] += w[i] * val             # <omega, delta 1_v>_w at head
        rhs[a] -= w[i] * val             # ... and tail
    # pin the first vertex of each component (kills the constant kernel)
    find = graph._uf()
    pinned = set()
    roots_seen = set()
    for idx in range(n):
        r = find(idx)
        if r not in roots_seen:
            roots_seen.add(r)
            pinned.add(idx)
    unknowns = [idx for idx in range(n) if idx not in pinned]
    m = len(unknowns)
    # dense solve of the reduced system over Fraction
    A = [[L[unknowns[r]][unknowns[c]] for c in range(m)] + [rhs[unknowns[r]]]
         for r in range(m)]
    for col in range(m):
        piv = None
        for r in range(col, m):
            if A[r][col] != 0:
                piv = r
                break
        check(piv is not None, "harmonic_representative: reduced Laplacian is singular")
        A[col], A[piv] = A[piv], A[col]
        pv = A[col][col]
        A[col] = [x / pv for x in A[col]]
        for r in range(m):
            if r != col and A[r][col] != 0:
                factor = A[r][col]
                A[r] = [x - factor * y for x, y in zip(A[r], A[col])]
    f = [Fraction(0)] * n
    for r in range(m):
        f[unknowns[r]] = A[r][m]
    h = {}
    for i, (u, v) in enumerate(graph.E):
        df = f[vi[v]] - f[vi[u]]
        h[i] = Fraction(omega.get(i, Fraction(0))) - df
    return h


def cycle_class_coeffs(gprime, chain):
    """Express a 1-cycle `chain` of G' in the fundamental-cycle basis (integer coeffs).

    Returns dict {basis_index: coeff}. Each fundamental cycle is the unique basis
    element carrying its own chord, so the coefficient equals the chain's value on
    that chord. VALIDATES that `chain` is genuinely in the cycle-space span by
    reconstructing sum_j coeff_j * C_j and checking it equals `chain`; a
    boundary-carrying / non-cycle chain is REJECTED (AssertionError). This closes
    the class-extraction-on-out-of-space-input gap.
    """
    basis = gprime.fundamental_cycles()
    forest = gprime.spanning_forest()
    chords = [i for i in range(len(gprime.E)) if i not in forest]
    coeffs = {j: chain.get(ch, 0) for j, ch in enumerate(chords)}
    recon = {}
    for j, c in coeffs.items():
        if c == 0:
            continue
        for ei, mult in basis[j].items():
            recon[ei] = recon.get(ei, 0) + c * mult
    recon = {k: v for k, v in recon.items() if v != 0}
    norm_chain = {k: v for k, v in chain.items() if v != 0}
    check(recon == norm_chain,
          "cycle_class_coeffs: input is not a 1-cycle in the fundamental-cycle span "
          "(reconstruction %r != chain %r)" % (recon, norm_chain))
    return coeffs


# -- self-test ------------------------------------------------------------
def _cycle_graph(n, offset=0, label=""):
    """C_n on vertices label+offset..: oriented edges (i -> i+1 mod n)."""
    V = ["%s%d" % (label, offset + i) for i in range(n)]
    E = [(V[i], V[(i + 1) % n]) for i in range(n)]
    return Graph(V, E), V


def selftest():
    results = []

    # --- P1: b1 correctness across shapes -------------------------------
    tree = Graph(["a", "b", "c"], [("a", "b"), ("b", "c")])
    check(tree.b1() == 0, "tree b1 must be 0")
    Ck, _ = _cycle_graph(4)
    check(Ck.b1() == 1, "cycle C4 b1 must be 1")
    # figure-eight: two loops sharing vertex x
    fig8 = Graph(["x", "p", "q"], [("x", "p"), ("p", "x"), ("x", "q"), ("q", "x")])
    check(fig8.b1() == 2, "figure-eight b1 must be 2")
    # two disjoint triangles: b1 = 2, components = 2
    tt = Graph(["a", "b", "c", "d", "e", "f"],
               [("a", "b"), ("b", "c"), ("c", "a"), ("d", "e"), ("e", "f"), ("f", "d")])
    check(tt.components() == 2 and tt.b1() == 2, "two triangles: comp=2, b1=2")
    results.append("P1 b1/components: OK")

    # --- P2: coboundary self-test <delta f, z> = 0 (period is a homology pairing) ---
    C6, Vc = _cycle_graph(6)
    f = {v: Fraction(3 * i - 1, 2) for i, v in enumerate(Vc)}  # arbitrary vertex-function
    df = coboundary(C6, f)
    for z in C6.fundamental_cycles():
        check(period(df, z) == 0, "coboundary must have zero period around every cycle")
    # and a non-closed cochain generally does NOT (teeth: the self-test is not vacuous)
    omega = {0: Fraction(1)}  # value 1 on one edge only -> not a coboundary
    nonzero = any(period(omega, z) != 0 for z in C6.fundamental_cycles())
    check(nonzero, "period self-test must be non-vacuous (a non-closed cochain has nonzero period)")
    results.append("P2 coboundary period=0 (Lemma 3.3) + non-vacuous: OK")

    # --- P3: Lemma 3.6 transpose-adjunction <phi^* a, z> = <a, phi_* z> ----
    # m-fold cover phi: C_{m k} -> C_k, total edge j -> base edge (j mod k).
    k, m = 3, 4
    base, _ = _cycle_graph(k, label="b")
    total, _ = _cycle_graph(m * k, label="t")
    emap = {j: [(j % k, +1)] for j in range(m * k)}
    # a cochain on the base, a cycle on the total:
    alpha = {e: Fraction(e + 1, 5) for e in range(k)}  # arbitrary base cochain
    z_total = total.fundamental_cycles()[0]  # the generator of H_1(C_{mk})
    lhs = period(induced_pullback(emap, alpha), z_total)
    rhs = period(alpha, induced_pushforward(emap, z_total))
    check(lhs == rhs, "Lemma 3.6 adjunction <phi^* a,z> = <a,phi_* z> must hold: %s vs %s" % (lhs, rhs))
    results.append("P3 Lemma-5 adjunction: OK")

    # --- P4: m-cover DEGREE is COMPUTED, not asserted (H-F2 teeth) -------
    # phi_*[gamma_total] must equal m * [gamma_base]; degree read from the cycle class.
    pushed = induced_pushforward(emap, z_total)          # chain in base
    cls = cycle_class_coeffs(base, pushed)               # coeff in H_1(base) basis
    deg = cls.get(0)
    check(deg == m, "m-fold cover degree must be COMPUTED as m=%d, got %r" % (m, deg))
    # teeth: a DIFFERENT m gives a different computed degree (not a literal)
    m2 = 2
    total2, _ = _cycle_graph(m2 * k, label="u")
    emap2 = {j: [(j % k, +1)] for j in range(m2 * k)}
    z2 = total2.fundamental_cycles()[0]
    deg2 = cycle_class_coeffs(base, induced_pushforward(emap2, z2)).get(0)
    check(deg2 == m2 and deg2 != deg, "degree tracks the actual cover (m2=%d) -- not hard-coded" % m2)
    results.append("P4 m-cover degree computed (m=%d, m2=%d): OK" % (m, m2))

    # --- P5: period of the pulled-back angular form = the base period ----
    # eta = angular 1-cochain on the base (each edge value 1) -> period = k (winding).
    eta = {e: Fraction(1) for e in range(k)}
    base_period = period(eta, base.fundamental_cycles()[0])
    check(base_period == k, "base winding period must be k=%d" % k)
    # pulled back to the total and paired with the total cycle -> m * base_period
    up_period = period(induced_pullback(emap, eta), z_total)
    check(up_period == m * base_period, "pullback period must be m*k = %d" % (m * k))
    results.append("P5 pullback period = m * base period: OK")

    # --- P6: SIGN teeth -- a REVERSED-orientation edge in an edge-path ----
    # base with a -1 in its fundamental cycle: a->b, c->b, chord a->c.
    Gs = Graph(["a", "b", "c"], [("a", "b"), ("c", "b"), ("a", "c")])
    fc = Gs.fundamental_cycles()
    check(len(fc) == 1 and fc[0].get(0) == -1 and fc[0].get(1) == 1 and fc[0].get(2) == 1,
          "fundamental cycle must carry a -1 tree-path coefficient: %r" % fc)
    # a graph map sending one edge to e0 traversed BACKWARD (sign -1):
    Gsmall = Graph(["p", "q"], [("p", "q")])
    vmap = {"p": "b", "q": "a"}
    emap_rev = {0: [(0, -1)]}                       # edge (p,q) -> e0=(a,b) reversed (b->a)
    Gsmall.check_graph_map(Gs, vmap, emap_rev)      # must validate
    alpha = {0: Fraction(7), 1: Fraction(2), 2: Fraction(5)}
    zsmall = {0: +1}
    lhs = period(induced_pullback(emap_rev, alpha), zsmall)
    rhs = period(alpha, induced_pushforward(emap_rev, zsmall))
    check(lhs == rhs == -alpha[0],
          "reversed-edge pullback must carry the -1 sign: lhs=%s rhs=%s expected=%s"
          % (lhs, rhs, -alpha[0]))
    results.append("P6 sign teeth (reversed edge-path) + adjunction: OK")

    # --- P7: graph-map validation + rejection teeth ---------------------
    bad_emap = {0: [(1, +1)]}                       # (p,q) -> e1=(c,b): starts at c != vmap(p)=b
    try:
        Gsmall.check_graph_map(Gs, vmap, bad_emap)
        raise RuntimeError("check_graph_map should have rejected an inconsistent emap")
    except AssertionError:
        pass
    try:
        cycle_class_coeffs(Gs, {0: 1})              # single tree edge: boundary-carrying, not a cycle
        raise RuntimeError("cycle_class_coeffs should have rejected a non-cycle")
    except AssertionError:
        pass
    results.append("P7 graph-map + non-cycle rejection teeth: OK")

    # --- P8: coverage -- self-loop, parallel edges, empty ---------------
    loop = Graph(["x"], [("x", "x")])
    check(loop.b1() == 1 and loop.fundamental_cycles() == [{0: 1}], "self-loop b1/cycle")
    par = Graph(["a", "b"], [("a", "b"), ("a", "b")])
    check(par.b1() == 1 and len(par.fundamental_cycles()) == 1, "parallel-edge b1=1, one cycle")
    empty = Graph([], [])
    check(empty.b1() == 0 and empty.components() == 0, "empty graph: b1=0, components=0 (convention)")
    results.append("P8 coverage self-loop/parallel/empty: OK")

    # --- P9: check_graph_map REJECTION teeth (malformed maps must raise) --
    Ga = Graph(["p", "q"], [("p", "q")])
    Gb = Graph(["a", "b"], [("a", "b")])
    # (a) ghost image: vmap sends endpoints outside target V (via empty-collapse)
    try:
        Ga.check_graph_map(Gb, {"p": "ghost", "q": "ghost"}, {0: []})
        raise RuntimeError("check_graph_map must reject a vmap image outside target V")
    except AssertionError:
        pass
    # (b) sign 0: a step sign must be exactly +/-1, not silently read as backward
    try:
        Ga.check_graph_map(Gb, {"p": "b", "q": "a"}, {0: [(0, 0)]})
        raise RuntimeError("check_graph_map must reject a step sign of 0")
    except AssertionError:
        pass
    # (c) non-total vmap: an isolated source vertex left unmapped
    Giso = Graph(["p", "q", "iso"], [("p", "q")])
    try:
        Giso.check_graph_map(Gb, {"p": "a", "q": "b"}, {0: [(0, +1)]})
        raise RuntimeError("check_graph_map must reject a vmap not total on V")
    except AssertionError:
        pass
    # (d) missing emap edge: a declared edge absent from emap is a declaration error
    try:
        Ga.check_graph_map(Gb, {"p": "a", "q": "b"}, {})
        raise RuntimeError("check_graph_map must reject an edge missing from emap")
    except AssertionError:
        pass
    # (e) out-of-range emap target: a path step naming a non-existent target edge
    try:
        Ga.check_graph_map(Gb, {"p": "a", "q": "b"}, {0: [(99, +1)]})
        raise RuntimeError("check_graph_map must reject an out-of-range emap target")
    except AssertionError:
        pass
    results.append("P9 check_graph_map rejection teeth (ghost/sign0/non-total/missing-emap/out-of-range): OK")

    # --- P10: float cochain REJECTED (exact-arithmetic discipline) --------
    try:
        period({0: 0.1, 1: 0.2}, {0: 1, 1: 1})
        raise RuntimeError("period must reject float cochain values")
    except AssertionError:
        pass
    check(period({0: Fraction(1, 10), 1: Fraction(1, 5)}, {0: 1, 1: 1}) == Fraction(3, 10),
          "P10: exact Fraction pairing must give exactly 3/10")
    results.append("P10 float cochain rejected; Fraction pairing exact: OK")

    # --- P11: gauge split -- period is gauge-INVARIANT, norm is gauge-SENSITIVE ---
    # omega + delta f: the homological (period) channel is unchanged (Lemma 3.3);
    # the local (norm) channel moves. The two channels genuinely read different data.
    C3g, Vg = _cycle_graph(3, label="g")
    zg = C3g.fundamental_cycles()[0]
    ang = {e: Fraction(1) for e in range(3)}
    fg = {v: Fraction(2 * i) for i, v in enumerate(Vg)}
    shifted = {e: ang[e] + coboundary(C3g, fg)[e] for e in range(3)}
    check(period(ang, zg) == period(shifted, zg) == 3,
          "P11: period must be gauge-invariant (3 == 3)")
    check(cycle_norm(ang, zg) == 3 and cycle_norm(shifted, zg) != 3,
          "P11: norm must be gauge-sensitive (local channel moves under +delta f)")
    check(cycle_norm(ang, zg, weights={0: 2, 1: 2, 2: 2}) == 6,
          "P11: declared edge-weights scale the norm (measure datum is load-bearing)")
    results.append("P11 gauge: period invariant, norm sensitive (two channels distinct): OK")

    # --- P12: channel inequality |period| <= norm; equality iff constant sign ---
    C4i, _ = _cycle_graph(4, label="i")
    zi = C4i.fundamental_cycles()[0]
    alt = {0: Fraction(1), 1: Fraction(-1), 2: Fraction(1), 3: Fraction(-1)}
    check(period(alt, zi) == 0 and cycle_norm(alt, zi) == 4,
          "P12: SAME-LOCUS converse witness -- alternating form: period 0, norm 4")
    mixed = {0: Fraction(3), 1: Fraction(-1), 2: Fraction(2), 3: Fraction(1)}
    check(abs(period(mixed, zi)) < cycle_norm(mixed, zi),
          "P12: mixed signs give STRICT |period| < norm")
    const = {e: Fraction(2) for e in range(4)}
    check(abs(period(const, zi)) == cycle_norm(const, zi) == 8,
          "P12: constant sign gives equality |period| = norm")
    # weighted clause (w >= 1): the inequality persists with a declared measure datum
    check(abs(period(mixed, zi)) <= cycle_norm(mixed, zi, weights={e: 2 for e in range(4)}),
          "P12: weighted (w >= 1) norm still dominates the period")
    results.append("P12 channel inequality: |period| <= norm; equality iff constant sign: OK")

    # --- P13: harmonic representative -- div 0, same periods, minimal L2 ---
    C3h, Vh = _cycle_graph(3, label="h")
    om = {0: Fraction(5), 1: Fraction(-1), 2: Fraction(2)}      # period = 6
    h = harmonic_representative(C3h, om)
    # (i) closed form on C_n: h is constant = period/n along the cycle
    check(all(h[e] == Fraction(2) for e in range(3)),
          "P13: C_3 harmonic must be constant period/3 = 2, got %r" % h)
    # (ii) same periods (same class)
    z3 = C3h.fundamental_cycles()[0]
    check(period(h, z3) == period(om, z3) == 6, "P13: harmonic keeps the period")
    # (iii) weighted divergence vanishes at every vertex (orthogonal to every coboundary)
    for x in Vh:
        ind = {v: Fraction(1) if v == x else Fraction(0) for v in Vh}
        d_ind = coboundary(C3h, ind)
        check(sum(h[e] * d_ind[e] for e in range(3)) == 0,
              "P13: harmonic must be orthogonal to every coboundary (div = 0)")
    # (iv) strict L2 minimality vs the non-harmonic input
    check(sum(v * v for v in h.values()) < sum(v * v for v in om.values()),
          "P13: harmonic strictly reduces the L2 magnitude of a non-harmonic input")
    # (v) figure-eight (b1 = 2, shared vertex): div 0 + both periods kept
    F8h = Graph(["x", "p", "q"], [("x", "p"), ("p", "x"), ("x", "q"), ("q", "x")])
    om8 = {0: Fraction(4), 1: Fraction(0), 2: Fraction(1), 3: Fraction(3)}
    h8 = harmonic_representative(F8h, om8)
    for z in F8h.fundamental_cycles():
        check(period(h8, z) == period(om8, z), "P13: figure-eight periods preserved")
    for x in ["x", "p", "q"]:
        ind = {v: Fraction(1) if v == x else Fraction(0) for v in ["x", "p", "q"]}
        d_ind = coboundary(F8h, ind)
        check(sum(h8[e] * d_ind[e] for e in range(4)) == 0, "P13: figure-eight div = 0")
    # WEIGHTED case: with w = (1,1,4) on C_3 the weighted-harmonic distributes as
    # h(e) proportional to 1/w(e): h = (8/3, 8/3, 2/3) for period 6 (exact, derived by
    # minimising sum w*h^2 at fixed period; weighted divergence w(in)h(in)-w(out)h(out)
    # is 8/3 - 8/3 = 0 at every vertex). Guards the weight handling end to end.
    w3 = {0: Fraction(1), 1: Fraction(1), 2: Fraction(4)}
    hw = harmonic_representative(C3h, om, weights=w3)
    check(hw == {0: Fraction(8, 3), 1: Fraction(8, 3), 2: Fraction(2, 3)},
          "P13w: weighted harmonic must be (8/3, 8/3, 2/3), got %r" % hw)
    check(period(hw, z3) == 6, "P13w: weighted harmonic keeps the period")
    for x in Vh:
        ind = {v: Fraction(1) if v == x else Fraction(0) for v in Vh}
        d_ind = coboundary(C3h, ind)
        check(sum(w3[e] * hw[e] * d_ind[e] for e in range(3)) == 0,
              "P13w: WEIGHTED divergence of the weighted harmonic must vanish")
    results.append("P13 harmonic representative: div 0, periods kept, strictly minimal L2 (+ weighted case): OK")

    # --- P14: rank_of_cycles -- image-independence is the real invariant ---
    rose = Graph(["x", "a", "b", "c"],
                 [("x", "a"), ("a", "x"), ("x", "b"), ("b", "x"), ("x", "c"), ("c", "x")])
    P1r, P2r, P3r = {0: 1, 1: 1}, {2: 1, 3: 1}, {4: 1, 5: 1}
    check(rose.b1() == 3 and rank_of_cycles(rose, [P1r, P2r, P3r]) == 3,
          "P14: the three petals are independent in H_1 (rank 3)")
    check(rank_of_cycles(rose, [P1r, P1r, {0: 2, 1: 2}]) == 1,
          "P14: multiples of one petal have rank 1 (non-zero is not independent)")
    results.append("P14 rank_of_cycles: petals rank 3; multiples rank 1: OK")

    # --- P15: minimal-entrainment floors (Prop 3.14) -- derived, attained, never undercut ---
    C4m, Vm = _cycle_graph(4, label="m")
    zm = C4m.fundamental_cycles()[0]                       # unit-multiplicity 4-cycle
    sig = Fraction(6)
    l1f, l2f = entrainment_floors(sig, zm)                 # counting measure
    check(l1f == 6 and l2f == 9, "P15: C4 floors must be |sigma| = 6 and sigma^2/4 = 9")
    harm = {e: Fraction(3, 2) * zm[e] for e in zm}         # constant (harmonic) profile
    conc = {e: sig * zm[e] for e in list(zm)[:1]}          # concentrated on one edge
    mixed = {}                                             # sign-mixed: 8 and -2 (period 6)
    e_a, e_b = sorted(zm)[0], sorted(zm)[1]
    mixed[e_a] = Fraction(8) * zm[e_a]
    mixed[e_b] = Fraction(-2) * zm[e_b]
    for om in (harm, conc, mixed):
        check(period(om, zm) == sig, "P15: fixture must carry period 6")
        check(cycle_norm(om, zm) >= l1f, "P15: l1 floor holds on every realisation")
        check(sum(v * v for v in om.values()) >= l2f, "P15: L2 floor holds on every realisation")
    check(cycle_norm(conc, zm) == l1f, "P15: concentration ATTAINS the l1 floor")
    check(cycle_norm(harm, zm) == l1f, "P15: single-signed harmonic attains l1 too (w = 1)")
    check(sum(v * v for v in harm.values()) == l2f, "P15: harmonic ATTAINS the L2 floor")
    check(sum(v * v for v in conc.values()) > l2f and sum(v * v for v in mixed.values()) > l2f,
          "P15: non-harmonic realisations sit STRICTLY above the L2 floor")
    # gauge shift: period unchanged, energy strictly above the floor (h orthogonal to delta f)
    fshift = {v: Fraction(2 * i - 3) for i, v in enumerate(Vm)}
    gauged = {e: harm.get(e, Fraction(0)) + coboundary(C4m, fshift)[e] for e in range(4)}
    check(period(gauged, zm) == sig and sum(v * v for v in gauged.values()) > l2f,
          "P15: gauge-shifted realisation keeps the period and sits above the L2 floor")
    # weighted case, tied to the P13w fixture: w = (1,1,4) on C_3, period 6
    C3m, _ = _cycle_graph(3, label="n")
    zn = C3m.fundamental_cycles()[0]
    w3m = {0: Fraction(1), 1: Fraction(1), 2: Fraction(4)}
    l1w, l2w = entrainment_floors(Fraction(6), zn, weights=w3m)
    check(l1w == 6 and l2w == 16, "P15w: weighted floors must be 6 and 36/(9/4) = 16")
    hw = {0: Fraction(8, 3), 1: Fraction(8, 3), 2: Fraction(2, 3)}   # the P13w harmonic
    check(sum(w3m[e] * hw[e] * hw[e] for e in range(3)) == l2w,
          "P15w: the weighted harmonic attains the weighted L2 floor exactly")
    concw = {0: Fraction(6)}                               # concentrate on a w = 1 edge
    check(period(concw, zn) == 6 and sum(w3m[e] * abs(v) for e, v in concw.items()) == l1w,
          "P15w: concentration on a cheapest-measure edge attains the weighted l1 floor")
    # mixed multiplicity: the DOUBLED cycle 2*z (integer chain). The norm reading carries
    # |z| = 2 per edge while the floor constant stays min w -- concentration still attains.
    zm2 = {e: 2 * zm[e] for e in zm}
    l1d, l2d = entrainment_floors(sig, zm2)
    check(l1d == 6 and l2d == Fraction(36, 16),
          "P15: doubled-cycle floors must be (min w)*|sigma| = 6 and sigma^2/(sum z^2/w) = 9/4")
    e0 = sorted(zm2)[0]
    conc2 = {e0: sig / zm2[e0]}                            # period sigma through |z| = 2
    check(period(conc2, zm2) == sig and cycle_norm(conc2, zm2) == l1d,
          "P15: concentration attains the norm floor on the doubled cycle too")
    harm2 = {e: sig * zm2[e] / Fraction(16) for e in zm2}  # sigma*z/(w*L), w = 1, L = 16
    check(period(harm2, zm2) == sig and sum(v * v for v in harm2.values()) == l2d,
          "P15: the harmonic profile attains the L2 floor on the doubled cycle")
    # sub-floor impossibility: shrinking the minimiser sheds period (no cheating the floor)
    shrunk = {e: Fraction(3, 4) * v for e, v in harm.items()}
    check(period(shrunk, zm) != sig, "P15: a shrunk minimiser no longer carries the period")
    # float sigma and empty cycle are declaration errors
    try:
        entrainment_floors(0.5, zm)
        raise RuntimeError("entrainment_floors must reject a float sigma")
    except AssertionError:
        pass
    try:
        entrainment_floors(Fraction(1), {})
        raise RuntimeError("entrainment_floors must reject an empty cycle")
    except AssertionError:
        pass
    results.append("P15 minimal-entrainment floors: derived + attained (l1 concentration, "
                   "L2 harmonic), never undercut, weighted case exact: OK")

    return results


if __name__ == "__main__":
    for line in selftest():
        print(line)
    print("graph_hodge selftest: 15/15 OK")
