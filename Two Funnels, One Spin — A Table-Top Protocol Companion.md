# Two Funnels, One Spin: Injection Locus, Channel Occupancy, and the Price of Identity

## A Table-Top Protocol Companion to ONTOΣ XV

**Maksim Barziankou (MxBv)**  
July 2026 · Poznań  
Contact: research@petronus.eu  
LinkedIn: https://www.linkedin.com/in/maxbarzenkov  
License: CC BY-NC-ND 4.0  
This work DOI: 10.17605/OSF.IO/EAUD5 (deposited with the ONTOΣ XV bundle)  
Axiomatic core anchor: **NC2.5 v2.1**, DOI 10.17605/OSF.IO/NHTC5  
Website: https://petronus.eu  

*Companion to: ONTOΣ XV — Spin-Channel and Nestability, and its formal companion. This document proposes physical instances and a table-top protocol; it derives no new mathematics and reports no measurements. One work in the 130+ work corpus of Navigational Cybernetics 2.5.*

---

> *"The figure is the channel's; the form is the substrate's; the price is the substrate's; the period is nobody's but topology's"*.
> — MxBv, July 2026

---

## 0. Position and Register

Everything in this document is one of three things, and nothing in it is a fourth: **(a)** classical fluid mechanics, read through the vocabulary of ONTOΣ XV — every formula below is textbook material, cited as such, deriving nothing new; **(b)** a *proposed*, unexecuted table-top protocol (§8) whose readings, once performed, would populate the falsification surface of XV essay §6 and the calibration programme of Open Problems 7.2 and 7.6; **(c)** one engineering-register instance (§7) of the structural slot the Bridge Law names. In the deployment-status taxonomy the corpus imports from the XIV companion (§6.7 / §11.3), every instance here is **Illustration-level**: no measurement has been performed, nothing is deployment-witnessed, and no physically-confirmed cross-layer result is claimed. The companion harness module (`harness/funnel_channels.py`) verifies the *discrete graph mirrors* and the *sealed-constant discipline* of this document — the depth laws themselves (+2, −2, the Rankine split) are document-level derivations of classical results, not machine-verified claims.

The honest limits of every identification made below are collected in §9 and repeated at the claims they qualify. The two most load-bearing: the punctured-domain reading of §2 holds in the two-dimensional axisymmetric section, or in three dimensions only when the air core spans the full water column (§9, note 5); and the transition of §6 is viscosity-mediated — in the inviscid idealization circulation on material loops is conserved (Kelvin), so the W-death reading compares two steady states quasi-statically rather than describing an inviscid event (§9, note 6).

## 1. Glass One — the Boundary Injects: the Local Channel

Spin a platform carrying a glass of water and wait for the steady state. The water settles into solid-body rotation, $v_\theta = \omega r$ — Newton's bucket. Read through the corpus's spin apparatus (*Operational Spin*, DOI 10.17605/OSF.IO/94GWQ):

- The spin one-form is $\omega_S = v^\flat = \omega r^2\, d\theta$ — **not closed**: $d\omega_S = 2\omega \cdot (\text{area form})$, a vorticity of $2\omega$ distributed uniformly through the bulk.
- The circulation around a centred circle of radius $r$ is $\oint \omega_S = 2\pi \omega r^2$ — it grows with the enclosed area (Stokes: it is *collected from* the interior vorticity), and is therefore **loop-dependent**: no invariant of any homology class.
- The carrier is the full disk section — simply connected, $H^1 = 0$. There is no closed component with a non-zero period; the identity witness of the corpus's two-channel reading is **zero**. This is the plane-rotation example of *Operational Spin* ($[\eta_S] = 0$, $d\omega_S \neq 0$) standing in glassware.
- The free surface is an equipotential of the effective potential in the rotating frame, $\Phi_{\mathrm{eff}} = gz - \omega^2 r^2 / 2$, giving $z(r) = z_0 + \omega^2 r^2 / (2g)$: a **paraboloid**, profile exponent $+2$. The funnel is nature graphing the potential.
- The spin enters **through the boundary**: shear at the walls and floor, communicated inward by the boundary-layer (Ekman) circulation. The vessel entrains its contents through the envelope — the walker-and-swarm picture of XV essay §3, with the envelope doing the carrying.

In XV's channel vocabulary this is the **local channel occupied alone**: field magnitude everywhere, homological reading zero. Note the typing consequence: with $H^1 = 0$ the section admits no homologically non-trivial cycle at all, so this configuration sits **outside the boundary-layer-admissible class** of companion Definition 3.2 — it enters the protocol of §8 as the *non-admissible negative control*, not as a Bridge-Law instance with $\sigma^{(M)} = 0$.

## 2. Glass Two — the Core Injects: the Homological Channel

Keep the platform still and drive the water from inside with a magnetic stir bar. Outside the stirred core the steady flow is the free (irrotational) vortex, $v_\theta = \Gamma / (2\pi r)$:

- The spin one-form is $\omega_S = (\Gamma / 2\pi)\, d\theta$ — **closed** on the region excluding the axis ($d\omega_S = 0$ there); the vorticity is concentrated at the core.
- The circulation around the core is $\oint \omega_S = \Gamma$ on *every* surrounding loop — a genuine period, $[\omega_S] = (\Gamma/2\pi)[d\theta] \in H^1_{\mathrm{dR}}$, **loop-invariant**. The witness is $\Gamma \neq 0$.
- At strong swirl the surface depression reaches the stirrer and an **air core** forms: in the two-dimensional axisymmetric section (and in three dimensions when the core spans the full column — §9, note 5) the water domain becomes an annulus, $H^1 \neq 0$. The puncture is *manufactured*: the worked example $S = \partial_\theta$ on $S^1 \times \mathbb{R}$ of *Operational Spin*, assembled in a kitchen.
- Bernoulli along the free surface gives $z(r) = z_\infty - \Gamma^2 / (8\pi^2 g\, r^2)$: profile exponent $-2$, two branches falling to the axis — visually, "two folded hyperbola halves" (an exponent signature, not a conic — §9, note 1).
- The spin enters **at the core**: the drive is applied to an internal actuator (the magnetically coupled bar), and the water receives it mechanically at the core boundary — an interior moving boundary, not a shear handed through the outer envelope.

Classical hydrodynamics has always carried this object under a paradoxical name — the *irrotational vortex with circulation*: a vortex with no vorticity but non-zero circulation. The paradox is exactly $H^1$: the form is locally potential ($\Gamma\theta/2\pi$, multivalued) and globally not. The corpus gives the slot its name: the **homological channel** — the channel that carries the identity witness.

## 3. The Duality, and the Funnel as a Free Readout

| | Glass 1 — platform | Glass 2 — stir bar |
|---|---|---|
| Injection locus | boundary (outer envelope) | core (internal actuator) |
| Velocity profile | $v \propto r^{+1}$ | $v \propto r^{-1}$ |
| $\omega_S$ | $\omega r^2 d\theta$, **not closed** | $(\Gamma/2\pi) d\theta$, **closed** |
| $d\omega_S$ | $2\omega$ everywhere | $0$ (concentrated at the core) |
| Circulation | $\propto$ area, loop-dependent | $\Gamma$, loop-invariant |
| Carrier ($2$D section) | disk, $H^1 = 0$ | annulus, $H^1 \neq 0$ |
| Identity witness | none ($[\eta_S] = 0$) | $\Gamma \neq 0$ |
| Surface profile | $z \propto +r^2$ | $z \propto -r^{-2}$ |
| XV class | outside boundary-layer-admissible (negative control) | topological prerequisite of the class supplied (candidate; nothing sealed) |

The profile exponents $+2$ and $-2$ are mirror signatures, and they cost nothing to read: a photograph of the free surface and a one-parameter fit. The exponent is a **radius-local readout between the two idealized pure states** — it discriminates the solid-body and free-vortex laws where each holds; it is not a general-purpose channel meter (arbitrary $v(r)$ profiles produce other exponents, and §4's composite shows both signatures in one glass, zone by zone).

## 4. One Glass, Both Channels: the Rankine Composite

A real stirred vortex is approximately a **Rankine vortex**: a solid-body core, $v = \Omega r$ for $r < a$, matched to irrotational wings, $v = \Omega a^2 / r$ for $r > a$. The free surface is correspondingly composite — a parabolic cup ($z = z_c + \Omega^2 r^2/2g$) inside radius $a$, hyperbolic-type wings ($z = z_\infty - \Omega^2 a^4 / (2 g r^2)$) outside — and the classical bookkeeping splits the total depression exactly in half: $\Omega^2 a^2 / 2g$ accumulated inside the core, $\Omega^2 a^2 / 2g$ across the wings.

Read through the corpus: the two zones are the two channels side by side in one funnel — the non-closed, vorticity-bearing reading inside $a$, the closed, period-carrying reading outside. Where the parabola hands over to the wings is where the local channel hands over to the homological one; the crossover radius $a$ is a **material scale** (it grows as viscosity spreads the core — the Lamb–Oseen widening $\propto \sqrt{4\nu t}$ after the drive stops), while the split itself is the channel structure. This is an illustration of the two-channel decomposition, not a computation of it: the zonal split is a property of the velocity law, and the corpus's Hodge-decomposition claims stay where the formal companion makes them.

## 5. The Substrate Sets the Price: Why $c$ Is Declared

Repeat glass two with syrup, then with a starch gel. Across the **Newtonian rungs** the classes do not move: the steady driven wing profile $v \propto 1/r$ is viscosity-independent (a steady free-vortex-regime statement — §9, note 2), so the closed form, the period $\Gamma$ for the same imposed circulation, and the exponent signatures all stand — and the *carrier topology* does not know the viscosity on any rung. What moves on the Newtonian rungs is the **form** (depth, steepness, core radius $a$, spin-up and decay times — the Ekman time $\tau \approx H/\sqrt{\nu\Omega}$, the Lamb–Oseen spreading) and the **price**: to *hold* the same $\Gamma$ against dissipation the stirrer must continuously supply power of order $\mu \int |\nabla v|^2\, dV$. The same period costs orders of magnitude more in syrup than in water. The gel rung is different in kind, and honestly so (§9, note 4): a shear-thinning medium bends the steady driven *profile* itself — with a power-law stress the azimuthal balance $r^2 \tau_{r\theta} = \text{const}$ gives $v \propto r^{1-2/n}$ rather than $1/r$ — so on that rung the wing one-form is not closed, the circulation is loop-dependent, and the $-2$ signature is not expected; the gel tests the *discipline*, not the profile.

This is the structural content of the Bridge Law's constant read physically: in $M^{\mathrm{cost}} = c \cdot |\sigma^{(M)}|$ the circulation reading $\sigma^{(M)}$ is topological — identical across the Newtonian substrates at the same imposed period — and, with the period and readout fixed in the idealized Newtonian wing reading, **the substrate enters the one-parameter Bridge-Law scoring exactly through $c$** — its remaining effects are the form and regime moves already named above, matters of calibration and regime typing rather than of the homological period. The material degree of freedom is the one thing the topology cannot fix; that is *why* the corpus types $c$ as deployment-declared rather than derived, and why its calibration (Open Problem 7.2) is a per-substrate measurement: calibrating $c$ is weighing one's own gel. A shear-thinning substrate sharpens the point rather than spoiling it: there the effective tariff varies with the regime, a *single* sealed $c$ fails the multi-event consistency test of companion Proposition 3.8 within that one substrate, and the linear one-constant form is honestly falsified — the protocol of §8 uses this as a falsifier resource, not a defect. (At the far end of the substrate axis the picture hands over to XV.1: a medium rigid enough that no genuine motion stays below the working budget hosts no vortex at all — an Illustration-register echo of the sealed core, recorded here and pressed no further.)

## 6. The Shape Monitor, and W-Death in Glassware

Now run both drives at once — platform spinning *and* stir bar running — and then switch the stir bar off, leaving the platform on. Quasi-statically (§9, note 6): the initial steady state carries the composite funnel with its $-2$ wings and, in the idealized section, a punctured carrier with period $\Gamma \neq 0$; the final steady state is glass one — solid-body rotation, paraboloid, air core closed, carrier simply connected, period gone.

Compare the two steady states through the corpus's monitor taxonomy. A **magnitude monitor** — is there rotation? is there a funnel? is the field non-zero? — reports continuity: rotation persists, a funnel persists, the local channel stays loudly alive. The **witness is nonetheless dead**: the closed, period-carrying component has no home once the carrier is simply connected. Under the named idealizations — the two-dimensional axisymmetric section, a full-span air core, the quasi-static comparison, and the declared transport being the inclusion of the annular domain into the filled one — this pair of states **is read as the Theorem 3(ii) pattern** of the formal companion: the post-event carrier is contractible, and the witness class is annihilated in it, while every magnitude reading survives. That is Regime W's signature (XIV companion Theorem 10) staged on a countertop; the identification of the physical event with a transport morphism is itself an Illustration-level reading, made here with its idealizations listed, not a formalized deployment.

What makes the staging worth having is the **shape monitor**. The funnel's profile exponent flips from $-2$ wings to a clean $+2$ as the period dies — an observable that is *not* magnitude-only, read from a photograph. In the idealized steady axisymmetric setting, between the two endpoint states of this comparison — full-span core present, then closed — the $-2$ tail is present exactly when the closed, period-carrying component is present, so there the exponent tracks the witness where magnitude monitors are provably blind. Outside the idealizations, or away from the endpoints, the readout is honest but weaker: a partial-depth air core leaves the three-dimensional domain simply connected, and a stirred state whose depression never reaches the stirrer shows the same already in the section (§4's composite below the core-reach threshold), the $-2$ wings still showing (§9, note 5) — there the exponent is reporting the *velocity law*, a live local-channel reading with trivial topology, which is itself the two-channel lesson: a live signal is not yet a live witness.

## 7. An Engineering-Register Instance: the Alignment-Charge Control Law

One engineering-register instance of the Bridge Law's slot exists in the corpus. *Alignment Charge: A New Control Primitive for Friction and Adhesion in Navigational Cybernetics 2.5* (dated 2025-12-20; published 2026-02-27 — months before the ONTOΣ XV formalism, the correspondence being noticed after the fact) defines a control variable with a rotational penalty term:

$$Q_A(t) = \varphi(\tilde{z}(t)) - \gamma \cdot \tau(t), \qquad \gamma \ge 0,$$

where $\tau(t)$ is a rotational-component signal — a torsional mismatch between system and contact medium, extracted from raw interaction features — and $\gamma$ is a non-negative calibration constant. In XV's vocabulary the correspondence is one qualitative paragraph, and the interpretive step in it is named: reading a *penalty inside a control variable* as a *cost line in a maintenance ledger* is a reading, not an equality. Under that reading, $\gamma \cdot \tau$ is a linear price on a rotational reading at the contact boundary with a deployment-declared constant — the shape of the **local channel term** $c_L \cdot \Lambda_{\mathrm{loc}}$ of the two-channel declared law (companion Remark 3.10): $\tau$ is a magnitude-type torsional signal, not a period, and the February work carries no topological channel at all — no witness, no $H^1$, exactly the blindness the corpus assigns to magnitude instruments. The work's energy accounting ("the trade-off is between mechanical energy — pressing harder — and electrical/thermal energy — modulating the contact regime") separates the ledger the way the X+M discipline of *Why the Ocean Has No Chance* §III does: normal force on the energetic line, regime-holding actuation on the maintenance line. And its stance — "spin does not destabilize — it provides the signal that triggers stabilization" — is the entrainment reading of XV.2 in engineering prose: the rotational reading is what the controller pays against to hold the regime.

What the instance contributes is concrete: the ultrasonic contact rig it describes (piezoelectric actuation, contact impedance, microvibration spectra) is a candidate **calibration domain for Open Problem 7.2** — instrument $\tau$ from the interaction features, meter the actuation power holding the contact regime as the maintenance reading (net of the declared spin-independent baseline), seal one constant, and run the multi-event discipline of companion Proposition 3.8 across surface and load changes with a disjoint holdout. Alongside the glassware of §8 it is a second candidate for Open Problem 7.6's physical-domain pilot. Its status here is the same as everything else's: an Illustration-level instance until a sealed deployment performs the measurements.

## 8. The Protocol

Four runs, each cheap, each reproducible with a phone camera and a profile-tracking fit. All declarations (substrate, drive, tolerance, constants, the spin-independent maintenance baseline) are sealed before scoring, per XIV companion Definition 2.6. What the four runs test is channel discrimination, the sealed-constant discipline, and the shape monitor — not the Bridge Law as a physical law: that requires the full sealed-deployment discipline — the complete Definition 2.6 declaration set with its evidence package — and performed measurements. Executed under that discipline, runs 2 and 4 would constitute the companion's empirical mode within each substrate; nothing here reports such an execution (Open Problem 7.2).

1. **Channel discrimination.** One glass, one water. Drive by platform; fit the surface-profile exponent. Drive by stir bar; fit again. Expected: $+2$ against $-2$ zones, the radius-local readout of §3, with the Rankine crossover visible in the stirred case.
2. **Substrate ladder.** Water → sugar syrup (stepped concentrations) → starch gel. Expected: class invariance across the Newtonian rungs (same exponent signatures; the gel rung is expected to bend the profile as well as the tariff — §9, note 4), form drift (core radius, depths, times), and a monotone tariff curve $c(\mu)$ on the Newtonian rungs — the power required to hold a fixed $\Gamma$ as a function of viscosity. This is the calibration curve Open Problem 7.2 asks for, one substrate at a time; pooling the substrates into a single class must *fail* the shared-constant test, and that failure is the point (§5).
3. **Kill the core.** Combined drive, then stir bar off, platform on. Record the relaxation of the wings, $-2 \to +2$. Expected: the magnitude readings continuous, the shape reading flipping — the §6 comparison staged.
4. **Sealed-constant discipline.** Within each substrate: seal $c$ on calibration events, score on a disjoint holdout (the calibration-sealed protocol of companion Proposition 3.8); for the gel, test whether one constant survives regime changes — a shear-thinning substrate is expected to falsify the one-constant form honestly, exercising clause (b).

The discrete mirrors of runs 1 and 3 — the annulus dichotomy over declared 2-cells and the W-death carrier comparison — and the sealed-constant discipline of runs 2 and 4 are executable now and ship in `harness/funnel_channels.py`; the physical runs remain open.

## 9. Honesty Notes

1. $z \propto -1/r^2$ is not a conic hyperbola; "two folded hyperbola halves" is a visual signature. The rigorous dichotomy is the pair of profile exponents $+2 / -2$ and closed / non-closed one-forms, and only that is claimed.
2. The stirred flow is three-dimensional in reality (Ekman pumping at the floor, secondary circulation); the free vortex and the Rankine composite are regime approximations, claimed as such.
3. Surface tension distorts the profile at small radius, near the core.
4. A starch gel is non-Newtonian (shear-thinning): its effective tariff is regime-dependent, so a single sealed $c$ is expected to fail there — disclosed and used as a falsifier resource (§5, §8 run 4), not hidden as a defect. The same rheology bends the steady driven *profile*: $r^2 \tau_{r\theta} = \text{const}$ with a power-law stress gives $v \propto r^{1-2/n}$ rather than $1/r$, so on the gel rung the wing one-form is not closed, the circulation is loop-dependent, and the $-2$ signature is not expected. The class-invariance statement of §5 is a *Newtonian-rung* statement.
5. **Full-span-core caveat (load-bearing).** The punctured-domain identification of §2 and the topological half of §6's reading hold in the two-dimensional axisymmetric section, or in three dimensions only when the air core reaches the stirrer through the full water column. A partial-depth core leaves the three-dimensional domain simply connected — loops slip under the core tip — while the $-2$ profile still shows; the exponent then reports a live local channel over trivial topology. The shape readout is exact in the idealization and channel-honest outside it.
6. **Kelvin caveat (load-bearing).** In the inviscid idealization circulation on material loops is conserved; the §6 transition is viscosity-mediated, on the spin-down timescale. The W-death reading is a quasi-static comparison of two steady states, not a claim about an inviscid event.
7. Every instance in this document is Illustration-level per the XIV deployment-status taxonomy; no run of §8 has been performed; nothing here is deployment-witnessed, and the Bridge Law's status (a declared structural law) is unchanged by anything in this document.

## 10. References

- **ONTOΣ XV — Spin-Channel and Nestability**, and *Spin-Channel Bridge and Core-Reduction: A Categorical Foundation* (this bundle).
- **ONTOΣ XIV** corpus bundle (deployment-status taxonomy §6.7 / §11.3; Theorem 10; sealed declarations §2.6). DOI 10.17605/OSF.IO/KAGMH.
- **Structural Spin as a Forgetful Separation over Dissipative Dynamics** ("Operational Spin"): the spin one-form, the identity witness, the two-channel reading, the folding example. DOI 10.17605/OSF.IO/94GWQ.
- **Why the Ocean Has No Chance** §III: the X+M two-ledger discipline. DOI 10.17605/OSF.IO/769YV.
- **NC2.5 v2.1** (axiomatic core). DOI 10.17605/OSF.IO/NHTC5.
- **Alignment Charge: A New Control Primitive for Friction and Adhesion in Navigational Cybernetics 2.5.** Published 2026-02-27, petronus.eu (petronus.eu/blog/alignment-charge). No DOI; the published markdown source is pinned by SHA-256 `34e4f6e8075ace029fa4ca81f7beb772014780edee2cb027fc42bf41b5500abb`.
- Classical results used as textbook material: Newton's bucket / rotating-frame equipotential; the free (irrotational) vortex and its Bernoulli surface; the Rankine vortex and its equal-split depression; Kelvin's circulation theorem; Ekman spin-up; the Lamb–Oseen vortex.

---

**Maksim Barziankou (MxBv)**  
*Table-top protocol companion to ONTOΣ XV — Spin-Channel and Nestability*
*Axiomatic core: NC2.5 v2.1, DOI 10.17605/OSF.IO/NHTC5*
