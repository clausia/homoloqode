# homoloQode MVP and project roadmap

This document describes the shared implementation plan for homoloQode. It
summarizes:

* what the minimum viable product (MVP) is intended to demonstrate;
* what has already been implemented;
* which GitHub issues complete the MVP;
* which issues block other work;
* which tasks can proceed in parallel;
* what research and software directions follow the MVP.

GitHub issues are the authoritative source for detailed requirements and
acceptance criteria. This document intentionally stays at the roadmap level and
does not reproduce the full issue descriptions.

> **Issue links:** Exact GitHub issue numbers will be inserted when they are
> available. Until then, the `MVP-XX` links below open the repository's issue
> tracker. The link definitions are centralized at the end of this file.

## Mathematical foundation

The initial code family is constructed from a finite binary chain complex

$$
C_2
\xrightarrow{\partial_2}
C_1
\xrightarrow{\partial_1}
C_0,
$$

with physical qubits associated with the basis elements of $C_1$. homoloQode
uses the convention

$$
H_X=\partial_1,
\qquad
H_Z=\partial_2^T.
$$

The chain-complex identity

$$
\partial_1\partial_2=0
$$

therefore becomes the CSS commutation identity

$$
H_XH_Z^T=0.
$$

The reference example is a square cellulation of a torus with periodic
boundary conditions and qubits placed on edges.

## What the MVP must demonstrate

The MVP is complete when homoloQode provides one reproducible end-to-end path:

```text
periodic square cellulation
    -> binary boundary matrices
    -> validated CSS code
    -> stabilizers and paired logical operators
    -> physical Pauli error
    -> algebraic and Qiskit syndrome extraction
    -> decoding correction
    -> stabilizer success or logical failure
    -> documented small-code experiment
```

The MVP prioritizes correctness, explicit mathematical conventions, automated
tests, and understandable examples. Algorithms such as exact distance search
and exhaustive decoding are intentionally restricted to small codes. They
provide reference implementations, not scalable production decoders.

The MVP does not claim:

* fault-tolerant syndrome extraction;
* threshold-scale simulation;
* scalable decoding;
* hardware execution;
* a general cup-product implementation;
* support for arbitrary Khovanov complexes.

These limitations define the first delivery boundary; they do not remove those
directions from the project roadmap.

## Already implemented

The current codebase includes:

* exact binary linear algebra over $\mathbb F_2$;
* explicit vertices, oriented edges, faces, and attaching walks;
* finite three-term chain complexes;
* validation of $\partial_1\partial_2=0$;
* periodic square toric complexes for configurable lattice size;
* construction and validation of $H_X$ and $H_Z$;
* code parameters $n$ and $k$ from binary ranks;
* CSS stabilizer strings and syndrome calculations;
* paired logical X and Z representatives;
* ideal Qiskit X-check and Z-check measurement circuits;
* conversion between Qiskit classical-bit order and check-matrix row order;
* automated comparisons between algebraic and Qiskit syndromes;
* an introductory boundary-map notebook;
* an algebraic-versus-Qiskit syndrome notebook;
* automated unit tests for the implemented layers.

This work is represented by [MVP-01] and [MVP-02].

## MVP work packages

The numbers identify issues; they do not imply that every issue must be
completed sequentially.

| Issue | Objective | Work state | Primary | Blocking dependencies |
|---|---|---|---|---|
| [MVP-01] | Ideal Qiskit syndrome-extraction adapter | Implemented | Claudia | Existing CSS core |
| [MVP-02] | Algebraic-versus-Qiskit syndrome notebook | Implemented | Claudia | MVP-01 |
| [MVP-03] | Exact X, Z, and overall distance for small CSS codes | Not started — can begin now | Amey | Existing GF(2) and logical-space core |
| [MVP-04] | Reproducible independent Pauli noise model | Not started — can begin now | Amey | Existing CSS error representation |
| [MVP-05] | Exhaustive minimum-weight CSS decoder | Not started — can begin now | Claudia / pair | Existing GF(2) core |
| [MVP-06] | Reusable end-to-end memory-experiment API | Not started — blocked | Claudia | MVP-04 and MVP-05 |
| [MVP-07] | Noise-and-decoding experiment notebook | Not started — blocked | Amey | MVP-06 |
| [MVP-08] | Periodic-lattice, error, syndrome, and logical visualization | Not started — can begin now | Amey | Existing topology and CSS core |
| [MVP-09] | Continuous integration for tests and notebooks | Not started — can begin now | Claudia | Existing tests and notebooks |
| [MVP-10] | MVP integration, documentation, and release audit | Not started — blocked | Claudia | MVP-03 through MVP-09 |

## Blocking relationships

The actual dependency structure is:

```text
MVP-01 Qiskit adapter ──> MVP-02 comparison notebook       [implemented]

MVP-04 noise ─────┐
                  ├──> MVP-06 experiment API ──> MVP-07 experiment notebook ────┐
MVP-05 decoder ───┘                                                             │
                                                                                ├──> MVP-10 release
MVP-03 distance ────────────────────────────────────────────────────────────────┤
MVP-08 visualization ───────────────────────────────────────────────────────────┤
MVP-09 CI ──────────────────────────────────────────────────────────────────────┘
```

Consequences:

* MVP-03, MVP-04, MVP-05, MVP-08, and MVP-09 can begin immediately.
* MVP-06 cannot be completed until the noise and decoder APIs from MVP-04 and
  MVP-05 are available.
* MVP-07 must use the public API produced by MVP-06; experiment logic should not
  be reimplemented in notebook cells.
* MVP-08 is independent, although MVP-07 may use its visualizations if it is
  completed in time.
* MVP-09 can start with the current tests and two notebooks and expand as other
  issues are merged.
* MVP-10 is the final integration gate and begins only after the preceding MVP
  feature and infrastructure issues are complete.

MVP-03 is useful when interpreting experimental results, but it does not block
the initial implementation of the experiment engine.

## Parallel development plan

The project is designed so both collaborators can make progress without
waiting on one another.

### First parallel cycle

* **Amey:** [MVP-04], independent Pauli noise.
* **Claudia:** [MVP-05], exhaustive decoder, or [MVP-09], initial CI.

### Second parallel cycle

After MVP-04 review:

* **Amey:** [MVP-03], exact distance.
* **Claudia:** continue [MVP-05] and/or [MVP-09].

### Work during review periods

* **Amey:** [MVP-08], topology-aware visualization.
* **Claudia:** review mathematical conventions and keep CI synchronized with
  newly merged tests.

### Integration cycle

1. Claudia implements [MVP-06] after MVP-04 and MVP-05 are merged.
2. Amey implements [MVP-07] using the public experiment API.
3. Both review results, mathematical explanations, runtime, and limitations.
4. Claudia coordinates [MVP-10], with Amey reviewing the final mathematical
   narrative.

## MVP definition of done

The MVP is ready for its first release when:

* toric codes of sizes two and three are reproducibly constructed;
* $[[n,k,d]]$ is verified for both reference examples;
* Pauli errors can be sampled reproducibly;
* algebraic and ideal Qiskit syndrome results agree;
* the exhaustive decoder corrects the documented small-code cases;
* residual stabilizers and logical failures are distinguished;
* the end-to-end experiment is reproducible;
* topology, errors, syndromes, and logicals can be visualized;
* all unit tests pass;
* all MVP notebooks execute from a clean installation;
* CI verifies supported environments;
* README, architecture, glossary, and notebooks use consistent conventions;
* limitations and post-MVP directions are documented explicitly.

## Roadmap after the MVP

Completing the MVP establishes a tested reference platform. The following work
is deliberately postponed until that platform is stable.

### Stage 1 — Broaden the topological-code foundation

The first post-MVP stage extends the current toric-code assumptions:

* planar surface codes with physical boundaries;
* rough and smooth boundary metadata;
* relative homology;
* additional cellulations and code families;
* separate X and Z distance behavior;
* improved geometry and visualization APIs;
* scalable decoder adapters such as PyMatching;
* optional simulator/tool adapters such as Stim and Qiskit Aer;
* more realistic noise, measurement-error, and repeated-syndrome models.

This stage should preserve the separation among topology, chain complexes, CSS
codes, and external integrations.

### Stage 2A — Cup products and logical gates

This research track develops the cochain-level structure needed for
cohomological logical operations:

1. define ordered simplicial or cubical input with the extra data required by a
   cup product;
2. expose the cochain complex

   $$
   C^0\xrightarrow{\delta^0}C^1\xrightarrow{\delta^1}C^2;
   $$

3. implement a cup product for a restricted, explicit class of complexes;
4. verify computationally that integrated products depend only on cohomology
   classes;
5. construct the two-copy toric-code CZ example;
6. derive the corresponding Qiskit physical circuit;
7. distinguish code-space preservation, constant depth, locality, and fault
   tolerance as separate properties;
8. later investigate preorientations and integrated Leibniz conditions for
   more general qLDPC codes.

Possible later operations include Steenrod squares, Bockstein homomorphisms,
and related cohomology operations.

### Stage 2B — Khovanov-related quantum codes

This track requires a representation more general than the MVP's three-term
complex:

1. introduce a graded or bigraded chain-complex representation;
2. record basis labels, gradings, and differentials explicitly;
3. validate consecutive differential compositions;
4. define an explicit adapter from a chosen three-term window or related
   construction to a CSS code;
5. reproduce a small published Khovanov-code example;
6. compare physical qubits, logical qubits, check structure, and distance;
7. investigate which Khovanov operations induce meaningful logical maps.

The existing `ChainComplex2D` should remain a clear MVP abstraction rather than
being stretched into a premature general Khovanov model.

### Stage 2C — Homology-preserving transformations

This track studies modifications of a complex that preserve homology while
changing the physical realization of the code:

* elementary expansions and collapses;
* inverse-cancellation-like moves;
* addition of redundant cells or generators;
* chain maps and chain-homotopy certificates;
* automated verification that homology dimensions are preserved.

For every transformation, experiments should compare:

* physical qubit count $n$;
* logical qubit count $k$;
* X and Z check counts;
* check ranks and weights;
* qubit participation in checks;
* X, Z, and overall distance;
* decoder behavior;
* geometry and possible logical-gate structure.

Preserving homology does not imply preserving the physical CSS code. Measuring
those differences is the purpose of this research direction.

### Stage 3 — Comparative research and technical report

After the post-MVP tracks have concrete examples:

* compare code families and transformations with reproducible benchmarks;
* study which properties are topological invariants and which depend on the
  chosen complex;
* compare logical operations obtained from geometry and cohomology;
* identify results strong enough for a technical report or publication;
* extend the existing project note with methods, experiments, limitations, and
  open questions.

The cup-product, Khovanov, and transformation tracks may proceed in parallel
once their shared algebraic interfaces are stable.

## Roadmap overview

```text
MVP
 ├─ exact distance
 ├─ Pauli noise
 ├─ exhaustive decoder
 ├─ end-to-end experiment
 ├─ visualization
 └─ CI and reproducible release
        |
        v
Stage 1: broader topological-code foundation
 ├─ planar boundaries and relative homology
 ├─ scalable decoder/simulator adapters
 └─ richer noise and syndrome models
        |
        +--------------------+-----------------------+
        v                    v                       v
Stage 2A                Stage 2B                 Stage 2C
Cup products            Khovanov codes           Homology-preserving
and logical gates       and graded complexes     transformations
        \                    |                       /
         +-------------------+----------------------+
                             v
Stage 3: comparative experiments, technical report, and research results
```

## Keeping this roadmap current

When a GitHub issue is created, closed, split, or renumbered:

1. update the corresponding link definition below;
2. update the work-state table if the high-level status changed;
3. update the dependency graph if a blocking relationship changed;
4. keep implementation details in GitHub rather than duplicating them here;
5. update the README only when the public project status changes materially.

[MVP-01]: https://github.com/clausia/homoloqode/issues
[MVP-02]: https://github.com/clausia/homoloqode/issues
[MVP-03]: https://github.com/clausia/homoloqode/issues
[MVP-04]: https://github.com/clausia/homoloqode/issues
[MVP-05]: https://github.com/clausia/homoloqode/issues
[MVP-06]: https://github.com/clausia/homoloqode/issues
[MVP-07]: https://github.com/clausia/homoloqode/issues
[MVP-08]: https://github.com/clausia/homoloqode/issues
[MVP-09]: https://github.com/clausia/homoloqode/issues
[MVP-10]: https://github.com/clausia/homoloqode/issues
