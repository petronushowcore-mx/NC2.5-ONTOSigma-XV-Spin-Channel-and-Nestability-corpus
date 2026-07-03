"""pilot_entrainment.py -- numerical demonstrator for the maintenance-circulation
reading (companion Open Problem 7.6; synthetic continuous world).

REGISTER (read first; this module is deliberately OUTSIDE the exact-rational
battery -- it uses floats, RK4 integration, and DECLARED tolerances, sealed in
PARAMS below before any run is scored).

What this pilot shows:
  * a measurement pipeline in which the field-side readings (circulation sigma,
    norm reading Lambda, energy reading) and the dynamics-side maintenance cost M
    come from two INDEPENDENT code paths -- sigma/Lambda are line-quadratures of
    the declared field over the declared cycle; M is integrated control effort
    along a genuinely simulated trajectory (P-controller, RK4), baseline-subtracted
    against a zero-field run of the same protocol;
  * the derived floor (companion Proposition 3.14) operating as a sanity gate on
    real measured readings, and its continuous mirror (norm >= |sigma|, energy >=
    sigma^2 / (2 pi R), the uniform field attaining both);
  * the sealed-c falsification discipline (companion Proposition 3.8) operating on
    genuinely simulated events -- calibration events, a frozen c, disjoint holdout
    events, and a corrupted-data negative control that the discipline catches;
  * the zero-spin and spurious-cancellation controls: a gradient world (maintenance
    without circulation) is correctly REJECTED by the norm-mode zero-spin clause,
    and a counter-rotating world shows net-circulation cancelling while the norm
    reading stays alive.

What this pilot does NOT show: the Bridge Law for any physical system. The linear
maintenance-vs-circulation mechanism in the vortex family is built into the synthetic
world by construction; the pilot validates the instruments, the independence of the
measurement code paths, and the falsification discipline -- not the law.

Stdlib only, deterministic (fixed parameters, no randomness), -O-safe.
"""
import math

from bridge_falsifier import floor_consistent, test_sealed_c_on_events, falsified_over_class


def check(cond, msg="check failed"):
    """Unconditional verification (assert-equivalent that survives `python -O`)."""
    if not cond:
        raise AssertionError(msg)


# -- sealed run parameters (declared BEFORE any event is scored) ------------
PARAMS = {
    "R": 1.0,          # declared cycle Gamma: circle of radius R about the origin
    "N_SEG": 720,      # quadrature segments along Gamma
    "N_STEP": 2000,    # RK4 steps per event (one revolution)
    "K_CTRL": 40.0,    # P-controller gain (station tracking)
    "TOL_REL": 0.05,   # declared relative tolerance for law-level comparisons
    "TOL_ABS": 0.02,   # declared absolute tolerance for zero-readings
}


# -- declared synthetic fields (u(x, y) -> (ux, uy)) ------------------------
def vortex(kappa):
    """Counterclockwise point vortex: tangential speed kappa/r; circulation 2*pi*kappa."""
    def u(x, y):
        r2 = x * x + y * y
        return (-kappa * y / r2, kappa * x / r2)
    return u


def gradient(a):
    """Potential (gradient) field grad(a*x): zero circulation on every closed cycle."""
    def u(x, y):
        return (a, 0.0)
    return u


def two_cell(kappa):
    """Counter-rotating cells: tangential profile kappa*cos(theta) on the circle --
    net circulation cancels; the norm reading does not."""
    def u(x, y):
        r = math.hypot(x, y)
        ct = x / r
        return (-kappa * ct * y / r, kappa * ct * x / r)
    return u


def concentrated(kappa):
    """Same total circulation as vortex(kappa), concentrated on a quarter arc --
    for the energy-floor demonstration (same sigma, strictly higher energy)."""
    def u(x, y):
        theta = math.atan2(y, x) % (2.0 * math.pi)
        r = math.hypot(x, y)
        amp = (4.0 * kappa / r) if theta < math.pi / 2.0 else 0.0
        return (-amp * y / r, amp * x / r)
    return u


# -- code path A: field-side readings (quadrature over the declared cycle) --
def field_readings(u, R=None, n=None):
    """(sigma, Lambda_norm, Lambda_energy) of the field along Gamma:
    sigma = closed line integral of the tangential component (net circulation),
    Lambda_norm = integral of |tangential component| (the norm reading),
    Lambda_energy = integral of the tangential component squared."""
    R = PARAMS["R"] if R is None else R
    n = PARAMS["N_SEG"] if n is None else n
    dl = 2.0 * math.pi * R / n
    sigma = lam = energy = 0.0
    for i in range(n):
        th = (i + 0.5) * 2.0 * math.pi / n
        x, y = R * math.cos(th), R * math.sin(th)
        tx, ty = -math.sin(th), math.cos(th)          # unit tangent, ccw orientation
        ux, uy = u(x, y)
        ut = ux * tx + uy * ty
        sigma += ut * dl
        lam += abs(ut) * dl
        energy += ut * ut * dl
    return sigma, lam, energy


# -- code path B: dynamics-side maintenance measurement ---------------------
def hold_station_work(u, n_steps=None):
    """Simulate one event: the station is driven once around Gamma AGAINST the
    counterclockwise field orientation (holding against the circulation); the tracer
    follows the station under drag dynamics xdot = u(x) + f with the P-controller
    f = k (s - x). Returns the integrated control effort  W = integral |f| dt  --
    measured from the TRAJECTORY the dynamics actually produces (RK4), not from
    any field formula. Maintenance is baseline-subtracted by the caller."""
    R = PARAMS["R"]
    n = PARAMS["N_STEP"] if n_steps is None else n_steps
    k = PARAMS["K_CTRL"]
    T = 1.0
    dt = T / n
    omega = -2.0 * math.pi / T                         # clockwise station drive

    def station(t):
        return (R * math.cos(omega * t), R * math.sin(omega * t))

    def rhs(t, x, y):
        sx, sy = station(t)
        ux, uy = u(x, y)
        return (ux + k * (sx - x), uy + k * (sy - y))

    x, y = station(0.0)
    work = 0.0
    t = 0.0
    for _ in range(n):
        sx, sy = station(t)
        fx, fy = k * (sx - x), k * (sy - y)
        work += math.hypot(fx, fy) * dt                # effort reading along the trajectory
        k1 = rhs(t, x, y)
        k2 = rhs(t + dt / 2, x + dt / 2 * k1[0], y + dt / 2 * k1[1])
        k3 = rhs(t + dt / 2, x + dt / 2 * k2[0], y + dt / 2 * k2[1])
        k4 = rhs(t + dt, x + dt * k3[0], y + dt * k3[1])
        x += dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        y += dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        t += dt
    return work


def maintenance(u):
    """Baseline-subtracted maintenance of one event: extra control effort caused by
    the field, relative to the identical zero-field protocol."""
    return hold_station_work(u) - hold_station_work(lambda x, y: (0.0, 0.0))


# -- self-test ---------------------------------------------------------------
def selftest():
    results = []
    R = PARAMS["R"]
    rel, ab = PARAMS["TOL_REL"], PARAMS["TOL_ABS"]

    # --- N1: determinism -- the whole pipeline reproduces itself exactly ----
    a1 = (field_readings(vortex(2.0)), maintenance(vortex(2.0)))
    a2 = (field_readings(vortex(2.0)), maintenance(vortex(2.0)))
    check(a1 == a2, "N1: two identical runs must agree bit-for-bit")
    results.append("N1 determinism (bit-for-bit reproduction): OK")

    # --- N2: numerics convergence gate (declared before scoring) ------------
    s_lo, l_lo, _ = field_readings(vortex(3.0), n=PARAMS["N_SEG"] // 2)
    s_hi, l_hi, _ = field_readings(vortex(3.0))
    check(abs(s_hi - s_lo) < ab and abs(l_hi - l_lo) < ab,
          "N2: halving the quadrature must not move sigma/Lambda beyond tolerance")
    m_lo = hold_station_work(vortex(3.0), n_steps=PARAMS["N_STEP"] // 2)
    m_hi = hold_station_work(vortex(3.0))
    check(abs(m_hi - m_lo) / m_hi < rel,
          "N2: halving the time step must not move the effort reading beyond tolerance")
    results.append("N2 convergence gate (quadrature + integrator): OK")

    # --- N3: field-side floors (continuous mirror of Proposition 3.14) ------
    # norm >= |sigma| on every config; energy >= sigma^2/(2 pi R), uniform attains.
    for name, cfg in (("vortex", vortex(2.0)), ("gradient", gradient(1.5)),
                      ("two-cell", two_cell(2.0)), ("concentrated", concentrated(2.0))):
        s, lam, en = field_readings(cfg)
        check(lam >= abs(s) - ab, "N3: norm floor violated on %s" % name)
        check(en >= s * s / (2 * math.pi * R) - ab, "N3: energy floor violated on %s" % name)
    s_u, _, en_u = field_readings(vortex(2.0))          # uniform tangential profile
    check(abs(en_u - s_u * s_u / (2 * math.pi * R)) / en_u < rel,
          "N3: the uniform field must ATTAIN the energy floor (within tolerance)")
    _, _, en_c = field_readings(concentrated(2.0))
    check(en_c > 2.0 * en_u,
          "N3: same circulation concentrated on an arc sits strictly above the floor")
    results.append("N3 field-side floors: held everywhere, attained by the uniform profile: OK")

    # --- N4: derived-floor gate on measured readings (shared falsifier code) --
    pairs = []
    for cfg in (vortex(1.0), vortex(3.0), two_cell(2.0), concentrated(2.0)):
        s, lam, _ = field_readings(cfg)
        pairs.append((lam, abs(s)))
    check(floor_consistent(pairs, 1, PARAMS["TOL_ABS"]),
          "N4: all real measured (Lambda, |sigma|) pairs must respect the derived floor")
    s, lam, _ = field_readings(vortex(3.0))
    check(not floor_consistent([(lam * 0.5, abs(s))], 1, PARAMS["TOL_ABS"]),
          "N4: a corrupted norm reading below the floor must FAIL the gate")
    results.append("N4 derived-floor gate on measured readings (+corruption caught): OK")

    # --- N5: sealed-c discipline on simulated events (the key demonstration) --
    # events: kappa sweep; M from dynamics, sigma from the field -- independent paths.
    events = {}
    for kappa in (1.0, 2.0, 3.0, 4.0, 5.0):
        s, _, _ = field_readings(vortex(kappa))
        events[kappa] = (maintenance(vortex(kappa)), abs(s))
    # calibrate on two events, freeze, holdout on the other three (disjoint)
    c_sealed = 0.5 * (events[1.0][0] / events[1.0][1] + events[2.0][0] / events[2.0][1])
    holdout = [events[k] for k in (3.0, 4.0, 5.0)]
    tol = rel * max(m for (m, _) in holdout)
    check(test_sealed_c_on_events(c_sealed, holdout, tol),
          "N5: the sealed c must fit all disjoint holdout events (mechanism built into "
          "this synthetic world by construction -- pipeline validation, not law proof)")
    corrupted = [holdout[0], (holdout[1][0] * 3.0, holdout[1][1]), holdout[2]]
    check(not test_sealed_c_on_events(c_sealed, corrupted, tol),
          "N5: a corrupted holdout event must break the sealed-c fit (discipline has teeth)")
    results.append("N5 sealed-c calibration/holdout on simulated events (+corruption caught): OK")

    # --- N6: zero-spin control -- maintenance without circulation is REJECTED --
    g = gradient(3.0)
    s_g, _, _ = field_readings(g)
    m_g = maintenance(g)
    check(abs(s_g) < ab, "N6: gradient field must read zero circulation")
    check(m_g > 10 * ab, "N6: holding against a drift still costs real effort")
    check(falsified_over_class([events[3.0], (m_g, abs(s_g))], tol),
          "N6: the norm-mode zero-spin clause must REJECT circulation-pricing of a "
          "world whose maintenance is not circulation-carried")
    results.append("N6 zero-spin control: gradient world correctly rejected: OK")

    # --- N7: spurious cancellation -- net-circulation blind, norm alive -------
    s_t, lam_t, _ = field_readings(two_cell(2.0))
    check(abs(s_t) < ab and lam_t > 10 * ab,
          "N7: counter-rotating cells: net circulation cancels, norm reading stays alive")
    results.append("N7 spurious-cancellation exhibit (net-circ 0, norm > 0): OK")

    return results


if __name__ == "__main__":
    for line in selftest():
        print(line)
    print("pilot_entrainment selftest: 7/7 OK")
