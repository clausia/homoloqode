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

Release `v0.1.0` establishes the tested reference platform. Subsequent minor
versions broaden the mathematical scope before building more experimental
research layers:

* **`v0.2.0` — Surface codes and relative homology.** Add physical boundaries,
  planar surface-code families, relative cycles, and boundary-aware logicals
  and visualization.
* **`v0.3.0` — Scalable decoding and noisy syndrome experiments.** Add decoder
  and simulator adapters, repeated syndrome rounds, measurement noise, and
  statistically meaningful experiments beyond exhaustive search.
* **`v0.4.0` — Homology-preserving transformations.** Implement certified
  changes to chain complexes and measure how they alter the physical CSS code.
* **`v0.5.0` — Cohomology operations and logical gates.** Add restricted cup
  products and related operations, with a two-copy 2D toric CZ construction
  as the required Clifford reference case and explicit logical-action
  validation.
* **`v0.6.0` — Graded complexes and Khovanov-related codes.** Generalize the
  algebraic representation and reproduce small published Khovanov-code
  constructions.

The detailed version goals, mathematical questions, deliverables, validation
criteria, and non-goals are maintained in the
[project roadmap](roadmap.md).

## Roadmap overview

The diagram shows the planned development and publication order. Each version
is a milestone containing several issues, as `v0.1.0` did. Complete, validate,
and release each milestone before starting research, prototypes, or
implementation for the next one. This includes individual issues for
`v0.2.0`, `v0.3.0`, and `v0.4.0`, even when they are technically independent.
See the [project roadmap](roadmap.md#milestones-and-sequential-development)
for the sequential development policy and patch-release handling.

```text
v0.1.0  MVP reference platform
   |
   v
v0.2.0  Surface codes and relative homology
   |
   v
v0.3.0  Scalable decoding and noisy syndrome experiments
   |
   v
v0.4.0  Homology-preserving transformations
   |
   v
v0.5.0  Cohomology operations and logical gates (toric CZ reference)
   |
   v
v0.6.0  Graded complexes and Khovanov-related codes
```

## Keeping this roadmap current

When a GitHub issue is created, closed, split, or renumbered:

1. update the corresponding link definition below;
2. update the work-state table if the high-level status changed;
3. update the dependency graph if a blocking relationship changed;
4. keep later version details in `docs/roadmap.md`;
5. keep implementation details in GitHub rather than duplicating them here;
6. update the README only when the public project status changes materially.

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
