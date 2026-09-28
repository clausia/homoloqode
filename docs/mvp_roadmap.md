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
* exact X, Z, and overall distance searches for small CSS codes;
* reproducible independent Pauli noise sampling;
* exhaustive minimum-weight decoding for small CSS codes;
* stabilizer, logical, and invalid residual classification;
* reusable single-trial and aggregate memory-experiment APIs;
* ideal Qiskit X-check and Z-check measurement circuits;
* conversion between Qiskit classical-bit order and check-matrix row order;
* automated comparisons between algebraic and Qiskit syndromes;
* an introductory boundary-map notebook;
* an algebraic-versus-Qiskit syndrome notebook;
* a noise-and-decoding experiment notebook;
* periodic-lattice visualization with error, syndrome, and logical overlays;
* automated unit tests for the implemented layers;
* continuous integration on Windows and Ubuntu, including notebook execution.

This work is represented by [MVP-01] through [MVP-09].

## MVP work packages

The numbers identify issues; they do not imply that every issue must be
completed sequentially.

| Issue | Objective | Work state | Primary | Blocking dependencies |
|---|---|---|---|---|
| [MVP-01] | Ideal Qiskit syndrome-extraction adapter | Implemented | Claudia | Existing CSS core |
| [MVP-02] | Algebraic-versus-Qiskit syndrome notebook | Implemented | Claudia | MVP-01 |
| [MVP-03] | Exact X, Z, and overall distance for small CSS codes | Implemented | Amey | Existing GF(2) and logical-space core |
| [MVP-04] | Reproducible independent Pauli noise model | Implemented | Amey | Existing CSS error representation |
| [MVP-05] | Exhaustive minimum-weight CSS decoder | Implemented | Claudia | Existing GF(2) core |
| [MVP-06] | Reusable end-to-end memory-experiment API | Implemented | Claudia | MVP-04 and MVP-05 |
| [MVP-07] | Noise-and-decoding experiment notebook | Implemented | Amey | MVP-06 |
| [MVP-08] | Periodic-lattice, error, syndrome, and logical visualization | Implemented | Amey | Existing topology and CSS core |
| [MVP-09] | Continuous integration for tests and notebooks | Implemented | Claudia | Existing tests and notebooks |
| [MVP-10] | MVP integration, documentation, and release audit | Implemented | Claudia | MVP-01 through MVP-09 |

## Blocking relationships

The actual dependency structure is:

```text
MVP-01 Qiskit adapter ──> MVP-02 comparison notebook       [implemented]

MVP-04 noise [implemented] ────┐
                               ├──> MVP-06 experiment API [implemented]
MVP-05 decoder [implemented] ──┘                  │
                                                  v
                                      MVP-07 experiment notebook ──┐ [implemented]
                                                                   │
MVP-03 distance [implemented] ─────────────────────────────────────┤
MVP-08 visualization [implemented] ────────────────────────────────┼──> MVP-10 release [implemented]
MVP-09 CI [implemented] ───────────────────────────────────────────┘
```

Consequences:

* MVP-01 through MVP-10 are implemented.
* MVP-07 consumes the public experiment API from MVP-06 and the visualization
  API from MVP-08; it does not reimplement their algorithms.
* Version `0.1.0` records the completed MVP implementation and release audit.

## MVP release

Version `0.1.0` is the completed MVP release. It provides the reproducible
reference platform defined by the criteria below and establishes the baseline
for the post-MVP roadmap.

## MVP definition of done

The first MVP release satisfies the following criteria:

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

### Stage 1: Broaden the topological-code foundation

The first post-MVP stage extends the current toric-code assumptions:

* planar surface codes with physical boundaries;
* rough and smooth boundary metadata;
* relative homology;
* additional cellulations and code families;
* scalable or approximate distance tooling beyond exact small-code search;
* improved geometry and visualization APIs;
* scalable decoder adapters such as PyMatching;
* optional simulator/tool adapters such as Stim and Qiskit Aer;
* more realistic noise, measurement-error, and repeated-syndrome models.

This stage should preserve the separation among topology, chain complexes, CSS
codes, and external integrations.

### Stage 2A: Cup products and logical gates

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

### Stage 2B: Khovanov-related quantum codes

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

### Stage 2C: Homology-preserving transformations

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

### Stage 3: Comparative research and technical report

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

[MVP-01]: https://github.com/clausia/homoloqode/issues/1
[MVP-02]: https://github.com/clausia/homoloqode/issues/2
[MVP-03]: https://github.com/clausia/homoloqode/issues/3
[MVP-04]: https://github.com/clausia/homoloqode/issues/4
[MVP-05]: https://github.com/clausia/homoloqode/issues/5
[MVP-06]: https://github.com/clausia/homoloqode/issues/6
[MVP-07]: https://github.com/clausia/homoloqode/issues/7
[MVP-08]: https://github.com/clausia/homoloqode/issues/8
[MVP-09]: https://github.com/clausia/homoloqode/issues/9
[MVP-10]: https://github.com/clausia/homoloqode/issues/10
