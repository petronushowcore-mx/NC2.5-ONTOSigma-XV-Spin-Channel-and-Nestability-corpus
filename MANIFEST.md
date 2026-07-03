# MANIFEST — ONTOΣ XV bundle

Inventory of every source document and runnable harness module in this repository. The declared check counts below are tied to the code by `harness/check_bundle.py` (a stale count here fails that gate).

## Documents

| File | Role |
|---|---|
| `ONTOSigma-XV-Spin-Channel-and-Nestability.md` | main essay — XV.1 (Nestability Criterion), XV.2 (Spin as Maintenance Geometry, a declared structural law), XV.3 (Core-Reduction Annihilates Witness); falsification surface §6; cross-reference matrix §10.1 |
| `Spin-Channel Bridge and Core-Reduction — A Categorical Foundation.md` | formal companion — imported apparatus §1; Theorem 1 + margin / autonomy ladder §2; the Bridge Law, compatible subclass, falsifiers and refinements §3; transport kernel criterion and calculus §4; two-axis symmetry §5; scope §6; open problems §7; glossary §9 |
| `Two Funnels, One Spin — A Table-Top Protocol Companion.md` | table-top protocol companion — Illustration-register physical readings (two-glasses channel dichotomy §1–§3, Rankine composite §4, substrate tariff §5, shape-monitor / W-death comparison §6, engineering-register instance §7), the proposed four-run protocol §8, honesty notes §9; no run performed |
| `README.md` | orientation, status register, run instructions |
| `MANIFEST.md` | this inventory |

## Harness

Stdlib-only Python 3, deterministic; exact rational arithmetic (`fractions.Fraction`) throughout, except the explicitly declared numerical demonstrators — `pilot_entrainment.py` and the entropy side of `fano_channel.py` — which run floats against sealed tolerances. Every module exits non-zero on any failing check, in both normal and `-O` interpreter modes.

| Module | Backs | Count |
|---|---|---|
| `graph_hodge.py` | cohomology core: cycle space and Betti number, periods, coboundary, induced maps, cycle-class coefficients, rank of transported families, harmonic representative (weighted Laplacian over ℚ), minimal-entrainment floors (Proposition 3.14) | 15 checks |
| `nestability.py` | Theorem 1 + Proposition 2.4 margin (sealed core, subcritical self-loop, zero-cost motion, robustness clause, margin dominance) + the drift layer (Definition 2.9 / Proposition 2.10: forced Independent-Exhaustion under declared window bands, band-violation and malformed-data rejection, and the honest withholding of subcriticality at N·ε ≥ 1) | 12 checks |
| `core_reduction.py` | Theorem 3 + Proposition 4.3 kernel criterion (preserving / annihilating / partial), retention, composition counterexample, capacity and bottleneck bounds, class-retention monotonicity | 12 checks |
| `boundary_witness.py` | Definition 3.5 / Lemma 3.6 / Proposition 3.7 compatibility checks: transported witness period, degree-m and collapsed-cycle rejection, cohomological (not pointwise) H-b, integrality and the quantisation floor | 7 checks |
| `bridge_falsifier.py` | Proposition 3.8 multi-event sealed-c discipline + Proposition 3.11 lattice falsifier + Proposition 3.14 derived-floor gate + Proposition 3.15 two-channel feasibility falsifier: feasible-interval intersection, zero-spin control, not-a-test degeneracy, tolerance guard, quantised lattice and floor, sub-floor impossible-reading rejection, exact two-variable elimination with a self-verifying witness, the two-event positivity power structure, and the single-channel degeneration cross-check | 13 checks |
| `tower_transport.py` | tower layer (companion §4): image-preservation typing, the derived lower restriction (rejecting non-preserving and non-injective declarations), automatic-vs-declared carrier-coherence boundary, all four level-verdict combinations realised by single transports, the pinch criterion, additive floors across loci, and the period ladder (parallel per-pair; composed only under a declared witness-alignment) | 7 checks |
| `pilot_entrainment.py` | Open Problem 7.6 synthetic demonstrator: field-side circulation/norm readings and dynamics-side maintenance measured through independent code paths, the derived-floor gate on measured readings, sealed-c calibration/holdout with corruption controls, zero-spin and cancellation controls (floats with declared tolerances — deliberately outside the exact-rational battery; instrument-and-discipline validation, not a law proof) | 7 checks |
| `funnel_channels.py` | discrete mirrors of the table-top protocol companion: the annulus two-channel dichotomy over declared quad 2-cells (non-closed cochain: ring periods differ; closed: equal and non-zero, with the discrete Stokes consistency identity), the substrate-tariff discipline (per-substrate sealed constant with holdout; wrongly-pooled-class rejection; regime-dependent constant as a genuine Proposition 3.8(b) falsifier), the W-death reading (H¹-trivial post-carrier hypothesis map-free plus a declared collapse stand-in, magnitude reading alive), and rejection controls (the document's depth laws are document-level derivations, not verified here) | 4 checks |
| `fano_channel.py` | Proposition 5.4 source-localisation floor: exact MAP error over ℚ (identity, useless, symmetric-noise and asymmetric channels; uniform and skew priors), the floor checked against the best estimator across the family, the degradation bite (mutual information falls, the floor rises toward its useless-channel value), and rejection controls (entropy terms in floats against a sealed tolerance — the estimator side stays exact-rational) | 4 checks |
| `teeth_audit.py` | mutation self-audit over the nine modules above plus the corpus gate: each listed weakening of a verified property must turn its check red; deliberate survivors are documented discriminators | all listed mutations behave as predicted |
| `corpus_gate.py` | cross-document invariants over the corpus documents (open-problem mirror, XV.k presence, no duplicate declarations, quote-punctuation, process-vocabulary and serial hygiene) + the regenerable cross-reference map (`--map`) | invariant gate + fixture self-audit |
| `check_bundle.py` | bundle gate: C1 smoke (every module, both interpreter modes), C2 count tie-out against this manifest, C3 packaging-document hygiene | gate + fixture self-audit |

## Running

From the repository root:

```bash
for m in graph_hodge nestability core_reduction boundary_witness bridge_falsifier tower_transport pilot_entrainment funnel_channels fano_channel teeth_audit corpus_gate check_bundle; do python "harness/$m.py" || break; done
```

or run `python harness/check_bundle.py`, which smoke-runs the whole battery in both interpreter modes and ties the counts above to the code.

**Layout requirement.** The corpus documents are read relative to the repository layout (the corpus `.md` files at the root, scripts inside `harness/`). A flattened copy is rejected with an explanatory message.
