"""fano_channel.py -- Proposition 5.4 (Source-localisation floor) harness.

Stdlib only. Deterministic. -O-safe (uses check(), not assert).

HYBRID PRECISION REGISTER (read first): the channel data (prior, transition
matrix) and the MAP estimator's error probability are EXACT rationals
(fractions.Fraction -- the probabilities of a declared finite channel are
rational data). The entropy terms of the floor involve logarithms and are
irrational for generic rational inputs; they are computed in floats against the
DECLARED tolerance TOL below, sealed before any fixture is scored -- the same
discipline as the bundle's synthetic demonstrator (pilot_entrainment.py). The
module is deliberately outside the exact-rational battery on its entropy side
and inside it on the estimator side.

What this module shows:
  * the exact MAP (maximum a posteriori) error of a declared finite channel
    (Z, p, P(w|z)) -- the best achievable localisation error, over Fraction;
  * the source-localisation floor (companion Proposition 5.4): for ANY estimator,
        P_e >= (H(Z) - I(Z; W) - log 2) / log |Z|,
    checked against the exact MAP error (the best estimator) across a fixture
    family -- identity, useless, symmetric-noise and asymmetric channels,
    uniform and skew priors;
  * the degradation bite: as the channel degrades toward useless, the mutual
    information falls and the floor rises toward (log|Z| - log 2)/log|Z|;
  * rejection controls: malformed declarations (non-stochastic rows, negative
    entries, mis-sized priors, |Z| < 2) are refused, not silently scored.

What it does NOT show: anything about which physical channel a deployment has.
The channel matrix is a DECLARED sealed datum (companion Definition 5.3); this
module enforces the floor's arithmetic, not the declaration's fidelity.
"""
import math
from fractions import Fraction

TOL = 1e-9   # sealed numeric tolerance for the float entropy side


def check(cond, msg="check failed"):
    """Unconditional verification (assert-equivalent that survives `python -O`)."""
    if not cond:
        raise AssertionError(msg)


def validate_channel(prior, P):
    """Declared finite source-localisation channel (companion Definition 5.3):
    a prior over Z (entries > 0 summing to 1, |Z| >= 2) and a row-stochastic
    matrix P[z][w] >= 0 with unit row sums, all rows one length |W| >= 1."""
    p = [Fraction(x) for x in prior]
    check(len(p) >= 2, "source alphabet needs |Z| >= 2")
    check(all(x > 0 for x in p), "prior entries must be > 0")
    check(sum(p) == 1, "prior must sum to 1")
    rows = [[Fraction(x) for x in row] for row in P]
    check(len(rows) == len(p), "one channel row per source letter")
    w = len(rows[0])
    check(w >= 1 and all(len(r) == w for r in rows), "rows must share one |W| >= 1")
    for r in rows:
        check(all(x >= 0 for x in r), "channel entries must be >= 0")
        check(sum(r) == 1, "channel rows must sum to 1")
    return p, rows


def map_error(prior, P):
    """Exact MAP error: P_e = 1 - sum_w max_z p(z) P(w|z), over Fraction. The MAP
    estimator is the best possible; every estimator's error is >= this value."""
    p, rows = validate_channel(prior, P)
    return Fraction(1) - sum(max(p[z] * rows[z][j] for z in range(len(p)))
                             for j in range(len(rows[0])))


def _xlogx(x):
    return 0.0 if x == 0 else float(x) * math.log(float(x))


def entropy_prior(prior):
    """H(Z) in nats (float)."""
    return -sum(_xlogx(Fraction(x)) for x in prior)


def mutual_information(prior, P):
    """I(Z; W) in nats (float): H(W) - H(W|Z) over the declared joint."""
    p, rows = validate_channel(prior, P)
    w = len(rows[0])
    pw = [sum(p[z] * rows[z][j] for z in range(len(p))) for j in range(w)]
    h_w = -sum(_xlogx(x) for x in pw)
    h_w_given_z = -sum(float(p[z]) * sum(_xlogx(rows[z][j]) for j in range(w))
                       for z in range(len(p)))
    return h_w - h_w_given_z


def fano_floor(prior, P):
    """Proposition 5.4: (H(Z) - I(Z; W) - log 2) / log |Z| -- a floor under the
    error of EVERY estimator of Z from W (in particular under the MAP error).
    Float, scored against the sealed tolerance TOL. For a uniform prior the
    numerator reads log|Z| - I - log 2."""
    p, rows = validate_channel(prior, P)
    return ((entropy_prior(p) - mutual_information(p, rows) - math.log(2))
            / math.log(len(p)))


def _symmetric(n, delta):
    """Symmetric noisy channel on n letters: correct with 1 - delta, the
    remaining delta spread evenly over the n - 1 wrong letters."""
    d = Fraction(delta)
    off = d / (n - 1)
    return [[(Fraction(1) - d) if i == j else off for j in range(n)]
            for i in range(n)]


# -- self-test ------------------------------------------------------------
def selftest():
    results = []
    F = Fraction
    third = [F(1, 3)] * 3
    uni4 = [F(1, 4)] * 4
    skew = [F(1, 2), F(1, 4), F(1, 4)]

    # --- FA1: exact MAP error at the extremes ------------------------------
    ident = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    check(map_error(third, ident) == 0, "FA1: identity channel localises exactly")
    useless = [[F(1, 2), F(1, 2)]] * 3
    check(map_error(third, useless) == F(2, 3),
          "FA1: useless channel leaves MAP error 1 - max p = 2/3")
    check(map_error(skew, useless) == F(1, 2),
          "FA1: useless channel, skew prior: MAP error = 1 - 1/2")
    results.append("FA1 exact MAP error (identity 0; useless 1 - max p; skew prior): OK")

    # --- FA2: the floor holds against the BEST estimator -------------------
    family = [
        (third, ident),
        (third, useless),
        (third, _symmetric(3, F(1, 10))),
        (third, _symmetric(3, F(1, 4))),
        (uni4, _symmetric(4, F(2, 5))),
        (skew, [[F(9, 10), F(1, 20), F(1, 20)],
                [F(1, 10), F(4, 5), F(1, 10)],
                [F(1, 5), F(1, 5), F(3, 5)]]),
    ]
    for prior, P in family:
        check(float(map_error(prior, P)) >= fano_floor(prior, P) - TOL,
              "FA2: the exact MAP error must sit on or above the floor")
    results.append("FA2 floor <= exact MAP error across the family (uniform + skew priors): OK")

    # --- FA3: degradation bite ----------------------------------------------
    deltas = [F(0), F(1, 10), F(1, 4), F(2, 5), F(1, 2), F(2, 3)]
    mis = [mutual_information(third, _symmetric(3, d)) for d in deltas]
    floors = [fano_floor(third, _symmetric(3, d)) for d in deltas]
    check(all(mis[i] > mis[i + 1] + TOL for i in range(len(mis) - 1)),
          "FA3: mutual information falls as the channel degrades")
    check(all(floors[i] < floors[i + 1] - TOL for i in range(len(floors) - 1)),
          "FA3: the localisation floor rises as the channel degrades")
    check(floors[-1] > 0.36
          and float(map_error(third, _symmetric(3, F(2, 3)))) >= floors[-1] - TOL,
          "FA3: at the useless end the floor is non-trivial and still honoured")
    results.append("FA3 degradation bite: I falls, floor rises to (log|Z| - log 2)/log|Z|: OK")

    # --- FA4: rejection controls --------------------------------------------
    for bad_call in (
        lambda: map_error([F(1, 2), F(1, 2)], [[F(1, 2), F(1, 4)], [F(1, 2), F(1, 2)]]),
        lambda: map_error([F(1, 2), F(1, 2)], [[F(3, 2), F(-1, 2)], [F(1, 2), F(1, 2)]]),
        lambda: map_error([F(2, 3), F(1, 2)], [[1, 0], [0, 1]]),
        lambda: map_error([1], [[1]]),
        lambda: map_error([F(1, 2), F(1, 2)], [[1, 0]]),
    ):
        try:
            bad_call()
            raise RuntimeError("malformed channel must be rejected")
        except AssertionError:
            pass
    results.append("FA4 rejection controls: non-stochastic / mis-sized declarations refused: OK")

    return results


if __name__ == "__main__":
    for line in selftest():
        print(line)
    print("fano_channel selftest: 4/4 OK")
