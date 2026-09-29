# homoloQode roadmap

## Where we are

Release `v0.1.0` provides a tested reference implementation for small
homological CSS codes. The next versions build on that foundation and move the
project toward broader code families and original research questions.

The order matters because each version prepares ideas and tools needed by the
next one:

$$
\text{boundaries and relative homology}
\longrightarrow
\text{scalable experiments}
\longrightarrow
\text{complex transformations}
\longrightarrow
\text{cohomological gates}
\longrightarrow
\text{graded and Khovanov complexes}
$$

The version numbers describe goals, not fixed deadlines. A version can be
split if the mathematics or implementation turns out to need more work than
expected.

## What every version should include

- Clear mathematical definitions and conventions
- Stable ordering for bases, qubits, checks, syndromes, and logical operators
- A clean separation between topology, algebra, codes, decoders, experiments,
  and external integrations
- Small examples whose answers can be checked independently
- References for mathematical constructions and a clear distinction between
  reproduced results and new observations
- Tests for mathematical identities as well as software behavior
- Clear complexity limits and a distinction between exact and heuristic results
- Seeded randomness and enough metadata to reproduce experiments
- An executable notebook for the main workflow
- Updated API documentation, glossary, architecture notes, and changelog
- Documented migrations when a public API or convention changes
- A complete test and notebook run in CI
- Carefully stated claims about scalability, thresholds, locality, and fault
  tolerance

Mathematical research, software design, implementation, documentation, and
review are shared parts of the project. Work ownership can be decided when the
issues for each version are created.

---

## v0.2.0 - Surface codes and relative homology

### Goal

Extend the current periodic toric-code model to planar surface codes with
physical boundaries. A user should be able to see how boundary types and
relative homology determine checks, logical strings, and distance.

### Mathematical work

This version needs a consistent convention for:

- A cell complex with distinguished boundary subcomplexes
- Rough and smooth boundary components
- Relative chain groups

  $$
  C_p(K,A)=C_p(K)/C_p(A)
  $$

- Relative boundary maps satisfying

  $$
  \partial_{p-1}^{\mathrm{rel}}\partial_p^{\mathrm{rel}}=0
  $$

- Primal and dual relative cycles representing logical operators
- The cells that carry physical qubits
- The checks retained or removed at each type of boundary
- The pairing between logical X and Z representatives
- The relation between code distance and the shortest nontrivial relative and
  dual cycles

These conventions should be written down before they are encoded in a
surface-code generator. If the literature uses competing boundary names or
labeling conventions, the chosen convention should be stated explicitly.

### Expected software

- Boundary metadata that works with the existing cell-complex model
- Exact relative-homology operations over $\mathbb F_2$
- At least one public family of planar surface codes
- Stable labels for data qubits, checks, and boundary components
- Construction of $H_X$ and $H_Z$ from the relative-chain model
- Logical-basis and exact-distance support for small planar examples
- Reuse of the existing noise, exhaustive decoder, residual classifier, and
  memory-experiment APIs
- Visualization of rough and smooth boundaries, errors, syndromes, and
  logical strings
- A notebook that derives and exercises a planar code from beginning to end
- A short technical note that presents the `v0.1.0` foundation and explains
  the extension to planar boundaries and relative homology

The toric-code API and examples should continue to work unless a documented
API improvement makes a change necessary.

### Validation

- A documented planar family encoding one logical qubit
- Two or more small sizes with independently known $[[n,k,d]]$ parameters
- Verification of the relative boundary-of-boundary identity
- Verification of CSS commutation
- Logical X and Z representatives with the expected pairing
- Errors that terminate at an allowed boundary and produce the expected
  syndrome
- Errors that cannot terminate at the opposite boundary
- Exact distance matching the geometry for sizes within the search limit
- Deterministic decoding and residual-classification examples
- Regression tests confirming that toric-code conventions have not changed

### Complete when

A new user can construct a planar surface code, trace its checks and logicals
back to relative homology, run the existing error-correction workflow, and
reproduce the reference parameters and visualization from a clean install.

### Not included yet

- Repeated noisy syndrome rounds
- Circuit-level noise
- Scalable decoding
- Threshold estimates
- Lattice surgery, code deformation, twists, or punctures
- Fault-tolerant logical-gate claims

---

## v0.3.0 - Scalable decoding and noisy syndrome experiments

### Goal

Move beyond exhaustive small-code demonstrations. This version adds optional
adapters for scalable decoding and stabilizer-circuit simulation while keeping
the algebraic core independent of those tools.

### Mathematical and experimental work

- Separate phenomenological and circuit-level noise models
- Represent data errors, measurement errors, detectors, and logical
  observables explicitly
- Convert repeated noisy syndrome rounds into detector events
- Define an explicit repeated syndrome-extraction schedule for at least one
  supported code family
- Relate circuit measurements, detector events, and logical observables to the
  algebraic conventions
- Define spatial and temporal boundary conventions
- Define decoder input and output ordering
- Classify residual logical failures after repeated rounds
- Report logical failure rates with trial counts and uncertainty intervals
- Distinguish a finite-size crossing experiment from a defensible threshold
  estimate

### Expected software

- A decoder protocol that supports syndrome histories
- A PyMatching adapter or an equivalent documented scalable decoder
- A Stim adapter for supported memory circuits and detector models
- Repeated syndrome-extraction circuits for at least one supported code family
- Optional dependency groups that keep the mathematical core lightweight
- Seeded batch experiments with machine-readable result records
- Confidence intervals and explicit trial counts
- Parameter sweeps across code sizes and physical error rates
- A notebook comparing the exact small-code path with the scalable path
- Basic runtime and memory benchmarks with the hardware context recorded

### Validation

- Agreement between scalable and exhaustive decoding on small shared cases
- Noiseless experiments and simple single-error cases
- Agreement between noiseless circuit measurements and algebraic syndromes in
  every round
- Tests for detector ordering and round boundaries
- Deterministic output for fixed seeds
- Aggregate experiments whose retained memory does not grow with the number of
  trials unless samples are explicitly requested
- Examples larger than the exhaustive-decoder guard allows
- Careful interpretation of finite-size results without unsupported threshold
  claims

### Complete when

The same documented code family can be run through both the exact workflow and
an optional scalable workflow with consistent conventions and reproducible
logical-failure statistics.

### Not included yet

- Quantum-hardware execution
- A universal circuit compiler
- Production-scale distributed simulation
- A hardware-validated noise model
- Threshold claims without enough sizes and statistics

---

## v0.4.0 - Homology-preserving transformations

### Goal

Study transformations that preserve homology while changing the chain complex
and possibly the physical CSS code. This is the first version centered on an
original comparative research question rather than only adding another code
family.

### Mathematical work

Start with a restricted set of transformations such as:

- Elementary expansions and collapses
- Addition or removal of cancellable generator pairs
- Controlled subdivision or refinement
- Addition of redundant cells or checks
- Explicit chain maps between original and transformed complexes
- Chain-homotopy certificates when available

For every transformation, distinguish:

- Preservation of the chain condition
- Preservation of homology dimensions
- Preservation of identified homology classes
- Equivalence or nonequivalence of the resulting physical CSS codes
- Changes to geometry, locality, and check weights
- Changes to logical-operator support and any available logical-gate
  construction

Preserving homology alone does not prove that distance, decoder behavior, or
fault-tolerance properties are preserved.

### Expected software

- A result object containing the transformed complex and its provenance
- Explicit maps or certificates that can be checked automatically
- Validation that transformed boundary maps still compose to zero
- Comparisons of $n$, $k$, check counts, ranks, check weights, qubit
  participation, $d_X$, $d_Z$, and overall distance where computable
- Transport or comparison of selected homology and logical representatives
- Comparison of logical support geometry and known gate constructions when
  relevant
- Geometry-aware before-and-after visualization
- Decoder and memory-experiment comparisons for tractable examples
- A notebook presenting at least one nontrivial transformation

### Validation

At least one reversible or independently checkable transformation should:

- Preserve the relevant homology
- Change at least one physical-code property
- Provide a machine-checkable map or certificate
- Work on more than one input size
- Reject an invalid transformation in a negative test
- Record whether distance is preserved, improved, reduced, or unknown because
  of computational limits

### Complete when

homoloQode can apply a documented transformation, verify its homological
claim, and produce a reproducible comparison showing how the associated CSS
realization changed.

### Not included yet

- Arbitrary topology simplification
- An optimizer guaranteed to improve code distance
- A classification of every homology-preserving transformation
- Automatic claims of local-unitary or fault-tolerant equivalence

---

## v0.5.0 - Cohomology operations and logical gates

### Goal

Add the cochain-level structure needed to construct and verify logical
operations from cup products and related cohomology operations. The main task
is to connect a mathematical invariant to its logical action and then to a
concrete physical circuit for a restricted example.

### Mathematical work

- Ordered cochain complexes

  $$
  C^0\xrightarrow{\delta^0}C^1\xrightarrow{\delta^1}C^2
  $$

- The dual relationship between boundary and coboundary maps
- The extra combinatorial data required by the chosen product, such as an
  ordering, cellular diagonal approximation, or preorientation
- A cup product for an explicit class of simplicial or cubical complexes
- The cochain-level Leibniz rule and any integrated form used
- Evaluation or integration of top-degree cochains
- Conditions that make an integrated product depend only on cohomology classes
- The resulting phase function on encoded basis states
- The expected Clifford-hierarchy level of each construction

Possible extensions include preorientations, higher cup products, Steenrod
squares, Bockstein homomorphisms, and operations from recent papers. Each
operation needs its own domain and hypotheses. It should not be treated as
interchangeable with the ordinary cup product.

A cup product must not be inferred from boundary matrices or CSS check
matrices alone. Its required combinatorial structure should be part of the
input and preserved explicitly.

### Expected software

- A cochain representation compatible with existing ordered chain data
- A validated cup product for at least one supported class of complexes
- Tests that integrated products are invariant under changes of cohomology
  representatives
- A two-copy toric-code CZ construction as the main reference example
- A Qiskit circuit or circuit description for the corresponding physical
  operation
- Independent verification of the logical action
- A structured way to register and compare other cohomology operations
- At least one comparison with a different product, operation, or topological
  example
- A notebook deriving the mathematics and checking the circuit action

### Claims that must remain separate

- Preservation of the code space
- Implementation of the intended logical unitary
- Constant circuit depth
- Geometric locality
- Bounded error propagation
- Fault tolerance under a stated noise and correction model

Proving one of these does not automatically prove the others.

### Complete when

At least one nontrivial cohomological phase construction has been derived,
implemented, and verified from its cochain definition through its logical
action and physical circuit, with assumptions and limitations stated clearly.

### Not included yet

- A universal fault-tolerant gate set
- Arbitrary cup products on every `CellComplex2D`
- Unsupported fault-tolerance claims
- Every operation identified in the literature
- Khovanov-specific operations

---

## v0.6.0 - Graded complexes and Khovanov-related codes

### Goal

Generalize the algebraic layer beyond three-term, ungraded cell complexes and
use the new representation to reproduce and study small quantum codes derived
from Khovanov-type chain complexes.

This work belongs in `v0.6.0` because it depends on ideas developed in earlier
versions: explicit ordering, code adapters, comparison tools, logical-map
analysis, and a clear separation between a chain complex and its associated
physical code.

### Mathematical work

- Finite chain complexes with an arbitrary consecutive degree range
- Graded or bigraded basis elements
- Degree-indexed differentials whose consecutive compositions vanish
- Homology computed degree by degree
- An exact relationship between a selected complex window and a CSS code
- Grading shifts and sign conventions for the chosen Khovanov construction
- A clear account of what is lost over $\mathbb F_2$ when signs or torsion
  matter

`ChainComplex2D` should remain focused on the original pipeline. A separate
graded-complex abstraction should represent the more general mathematics.

### Expected software

- An ordered `GradedChainComplex` or equivalent public abstraction
- Degree-aware and grading-aware basis labels and differentials
- Validation and homology computations across all represented degrees
- An explicit adapter from a documented three-term window or published
  construction to `CSSCode`
- A small and reproducible Khovanov-related reference example
- Comparisons of $n$, $k$, checks, ranks, logical representatives, and exact
  distance when feasible
- Provenance connecting generated matrices to the original graded basis
- An investigation of natural maps or operations that may induce logical maps
- A notebook connecting the source construction to the resulting quantum code

### Validation

The main example should:

- Reproduce published or independently checkable chain and code data
- Verify every consecutive differential composition
- Preserve grading metadata through the code adapter
- State what information is discarded when selecting a CSS window
- Distinguish properties of the full Khovanov complex from properties of the
  resulting CSS code
- Remain small enough to check ranks, homology, logicals, and distance
  independently

### Complete when

homoloQode can represent a documented graded complex, verify its algebra,
derive a small Khovanov-related CSS code through an explicit construction, and
reproduce its claimed parameters and logical structure.

### Not included yet

- A scalable general-purpose Khovanov-homology engine
- Arbitrary knot or link parsing
- Every coefficient ring or torsion phenomenon
- A claim that Khovanov-derived codes outperform established code families
- A claim that every Khovanov operation produces a useful logical gate

---

## Beyond v0.6.0

After these milestones, the project can compare the code families,
transformations, decoders, and logical operations using reproducible
benchmarks. That evidence can support a larger technical report or research
publication focused on questions such as:

- Which quantities are genuine topological or homological invariants
- Which properties depend on the chosen chain-level realization
- When transformations improve or degrade physical code parameters
- How geometric and cohomological constructions of logical operations relate
- Whether new examples justify broader abstractions or optimized tooling

A future `v1.0.0` should wait until the project has a stable public API and a
clear supported scope. Finishing the research milestones does not by itself
require declaring API stability.

## Keeping the roadmap current

When planning a version:

1. Confirm that the mathematical prerequisites are ready
2. Split the work into bounded GitHub issues with acceptance criteria
3. Record dependencies and decide ownership with the collaborators
4. Separate required release outcomes from exploratory questions
5. Split a version when evidence shows that a question needs its own release
6. Keep implementation details in issues rather than duplicating them here
