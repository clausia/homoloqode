# Architecture

This document records the initial software boundaries for **homoloQode**. The
architecture is intentionally small enough for the toric-code MVP while keeping
later research directions separate from the stable mathematical core.

## Core pipeline

The first supported pipeline is

$$
\texttt{CellComplex2D}
\longrightarrow
\texttt{ChainComplex2D}
\longrightarrow
\texttt{CSSCode}.
$$

For a finite two-dimensional cell complex,

$$
C_2 \xrightarrow{\partial_2} C_1 \xrightarrow{\partial_1} C_0,
$$

the project uses column vectors and matrices with shapes

$$
\partial_1\in\mathbb F_2^{|C_0|\times|C_1|},
\qquad
\partial_2\in\mathbb F_2^{|C_1|\times|C_2|}.
$$

Physical qubits are the basis elements of $C_1$, and

$$
H_X=\partial_1,
\qquad
H_Z=\partial_2^T.
$$

Consequently,

$$
H_XH_Z^T=\partial_1\partial_2=0.
$$

The three core layers have distinct responsibilities:

* `homoloqode.topology` stores cells, attaching data, boundary maps, and
  reference cellulations.
* `homoloqode.algebra` implements exact binary linear algebra. NumPy's
  real-valued rank and solver functions are not used for these calculations.
* `homoloqode.codes` stores abstract CSS codes and derives syndromes,
  stabilizers, and paired logical operators.

Qiskit objects do not appear in these layers.

## Cell representation

Cells have stable string identifiers and an explicit tuple order. An edge is
identified independently of its endpoints, so loops and parallel edges are
valid. A face boundary is an ordered closed walk of oriented edge references.
Orientations are retained even though signs disappear after reduction over
$\mathbb F_2$.

Boundary matrices are derived by accumulating incidences modulo two. They are
not constructed from sets: repeated incidences must cancel, particularly in
small periodic cellulations.

## Package layout

```text
src/homoloqode/
├── algebra/          exact linear algebra over F_2
├── topology/         cells, chain complexes, and cellulation factories
├── codes/            CSS code objects and logical operators
├── cohomology/       future cup products and cohomology operations
├── khovanov/         future graded/Khovanov chain-complex adapters
├── transformations/ future homology-preserving transformations
└── integrations/     required Qiskit layer and future external adapters
```

## Extension boundaries

### Cup products and logical gates

A cup product requires more information than arbitrary boundary or check
matrices. Future implementations belong in `homoloqode.cohomology` and should
declare the extra structure they require, such as an ordered simplicial or
cubical complex, a cellular diagonal approximation, or a preorientation.

The intended future pipeline is

$$
\text{structured cochain complex}
\longrightarrow
\text{integrated cohomology operation}
\longrightarrow
\text{logical action}
\longrightarrow
\text{Qiskit physical circuit}.
$$

Logical-gate circuits belong in an integration layer and must distinguish
code-space preservation, constant depth, and fault tolerance as separate
claims.

### Khovanov-related codes

Khovanov complexes are graded and are not naturally restricted to three chain
groups. A future `GradedChainComplex` should therefore live in
`homoloqode.khovanov`, with an explicit adapter that selects a three-term window
or otherwise constructs a CSS code. The MVP's `ChainComplex2D` should not be
stretched into a premature general-purpose Khovanov representation.

### Homology-preserving transformations

Transformations belong in `homoloqode.transformations`. A transformation should
return a new complex together with enough data to verify the claimed relation,
such as chain maps, a chain homotopy, or a sequence of elementary
expansion/collapse certificates.

Experiments should compare at least:

* homology dimensions;
* physical qubit count $n$;
* check counts, ranks, and weights;
* logical-qubit count $k$;
* distance, when an exact or bounded computation is available.

Preserving homology alone does not imply preservation of the physical CSS code.

## Initial milestones

1. Construct and validate a periodic square cellulation.
2. Produce $\partial_1$, $\partial_2$, $H_X$, and $H_Z$.
3. Verify toric-code check ranks and $[[n,k]]$ parameters for sizes two and
   three.
4. Compute syndromes and paired logical representatives over $\mathbb F_2$.
5. Add Qiskit export and ideal syndrome-extraction circuits.
6. Add small-code distance calculations and decoding experiments.
