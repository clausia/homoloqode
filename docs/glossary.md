# Glossary

This glossary collects working definitions for the main mathematical and quantum-information concepts used in **homoloQode**. The goal is not to write exhaustive textbook entries, but to agree on precise, project-specific definitions that can be refined as the project develops.

Unless stated otherwise, chain groups, vector spaces, and matrices in the project are defined over the binary field $\mathbb F_2$. The notation for $X$- and $Z$-type checks follows the convention described in the **Homological CSS code** entry.

## Contents

- [Entry template](#entry-template)
- [API and data model](#api-and-data-model)
- [Automated test and mathematical invariant](#automated-test-and-mathematical-invariant)
- [Binary field](#binary-field)
- [Binary symplectic representation](#binary-symplectic-representation)
- [Boundary](#boundary)
- [Boundary map](#boundary-map)
- [Cell complex](#cell-complex)
- [Chain complex](#chain-complex)
- [Clifford hierarchy](#clifford-hierarchy)
- [Cochain complex and coboundary map](#cochain-complex-and-coboundary-map)
- [Code parameters and code distance](#code-parameters-and-code-distance)
- [Cohomology group and cohomology class](#cohomology-group-and-cohomology-class)
- [Constant-depth circuit](#constant-depth-circuit)
- [Copy-cup gate](#copy-cup-gate)
- [Correctable region and cleaning lemma](#correctable-region-and-cleaning-lemma)
- [CSS code](#css-code)
- [Cup product](#cup-product)
- [Cycle](#cycle)
- [Decoder](#decoder)
- [Fault-tolerant logical gate](#fault-tolerant-logical-gate)
- [Geometric locality and circuit light cone](#geometric-locality-and-circuit-light-cone)
- [Homological CSS code](#homological-css-code)
- [Homology group and homology class](#homology-group-and-homology-class)
- [Incidence matrix](#incidence-matrix)
- [Logical operator and logical qubit](#logical-operator-and-logical-qubit)
- [Noise model and Pauli error](#noise-model-and-pauli-error)
- [Parity-check matrix](#parity-check-matrix)
- [Pauli operator and Pauli group](#pauli-operator-and-pauli-group)
- [Preorientation and integrated Leibniz rule](#preorientation-and-integrated-leibniz-rule)
- [qLDPC code](#qldpc-code)
- [Quantum circuit](#quantum-circuit)
- [Reproducibility and dependency](#reproducibility-and-dependency)
- [Stabilizer code](#stabilizer-code)
- [Surface code and relative homology](#surface-code-and-relative-homology)
- [Syndrome](#syndrome)
- [Topologically protected gate](#topologically-protected-gate)
- [Toric code](#toric-code)

---

## Entry template

```markdown
## Term

A **term** is ...

**Project role:** Explain how this concept appears in homoloQode.

**Related concepts:** Optional list of related glossary entries.
```
---

## API and data model

An **application programming interface (API)** is the documented set of classes, functions, inputs, outputs, and errors through which other code uses a software library. A **data model** specifies how domain objects and their relationships are represented in memory.

For example, a cell-complex data model must decide how cells are identified, ordered, validated, and converted into matrices. A stable API can hide those internal choices from users.

**Project role:** homoloQode needs a clear separation between the input complex, its boundary matrices, the resulting CSS code, and the required Qiskit integration layer.

**Related concepts:** Cell complex, incidence matrix, quantum circuit.

## Automated test and mathematical invariant

An **automated test** is executable code that checks whether a small, specified behavior remains correct. A **unit test** focuses on one function or class, while an **integration test** checks that several components work together.

A **mathematical invariant** is a property that must remain unchanged under specified transformations. Algebraic identities and known code parameters make particularly strong test oracles because their expected values do not depend on implementation details.

**Project role:** Tests should verify identities such as $\partial_1\partial_2=0$ and $H_XH_Z^T=0$, as well as expected ranks, syndromes, logical operators, and $[[n,k,d]]$ parameters for reference examples.

**Related concepts:** Boundary map, CSS code, code parameters, reproducibility.

## Binary field

The **binary field**, denoted $\mathbb F_2$, contains two elements, $0$ and $1$, with addition and multiplication performed modulo $2$. In particular,

$$
1+1=0.
$$

Working over $\mathbb F_2$ removes orientation signs from boundary calculations and makes binary vectors a natural representation of subsets of cells and supports of Pauli operators.

**Project role:** Boundary matrices, CSS check matrices, error vectors, syndromes, and most linear-algebra computations in homoloQode use $\mathbb F_2$.

**Related concepts:** Boundary map, parity-check matrix, binary symplectic representation.

## Binary symplectic representation

The **binary symplectic representation** encodes an $n$-qubit Pauli operator, up to an overall phase, by two binary vectors:

$$
(\mathbf x\mid\mathbf z)\in\mathbb F_2^{2n}.
$$

At qubit $i$, $(x_i,z_i)=(1,0)$ represents $X$, $(0,1)$ represents $Z$, and $(1,1)$ represents $Y$. Two Pauli operators commute exactly when their symplectic inner product is zero:

$$
\mathbf x\cdot\mathbf z' + \mathbf z\cdot\mathbf x' = 0\pmod 2.
$$

**Project role:** This representation provides an efficient implementation of commutation tests, general stabilizers, errors, and logical operators.

**Related concepts:** Pauli group, stabilizer code, syndrome.

## Boundary

A **$p$-boundary** is a chain that is itself the boundary of a higher-dimensional chain. The vector space of $p$-boundaries is

$$
B_p=\operatorname{im}(\partial_{p+1}).
$$

Every boundary is a cycle because $\partial_p\partial_{p+1}=0$, so $B_p\subseteq Z_p$.

**Project role:** Cycles that differ by a boundary represent the same homology class and, in the code, the same logical action up to stabilizers.

**Related concepts:** Cycle, homology class, stabilizer.

## Boundary map

A **boundary map**

$$
\partial_p:C_p\longrightarrow C_{p-1}
$$

sends each $p$-dimensional cell to the formal sum of the cells in its boundary. Consecutive boundary maps must satisfy

$$
\partial_{p-1}\partial_p=0,
$$

which expresses the principle that a boundary has no boundary.

**Project role:** homoloQode validates $\partial_1\partial_2=0$ when constructing
a chain complex. The same identity guarantees commutation of the associated CSS
checks.

**Related concepts:** Chain complex, cycle, boundary, homological CSS code.

## Cell complex

A **cell complex** is a space assembled from cells of different dimensions, such as vertices ($0$-cells), edges ($1$-cells), and faces ($2$-cells), together with rules describing how the boundary of each cell is attached to lower-dimensional cells.

A finite two-dimensional cell complex supplies chain groups

$$
C_2,\quad C_1,\quad C_0
$$

generated by its faces, edges, and vertices. Its incidence data determines the boundary maps between these groups.

**Project role:** Small combinatorial cell complexes are homoloQode's primary
topological inputs. The MVP provides periodic square cellulations of the torus.

**Related concepts:** Chain complex, incidence matrix, boundary map, toric code.

## Chain complex

A **chain complex** is a sequence of vector spaces or modules connected by boundary maps,

$$
\cdots \longrightarrow C_2 \xrightarrow{\partial_2} C_1 \xrightarrow{\partial_1} C_0 \longrightarrow 0,
$$

such that applying two consecutive boundary maps gives zero:

$$
\partial_1 \partial_2 = 0.
$$

In this project, we will mainly consider finite chain complexes over $\mathbb{F}_2$. For a two-dimensional cell complex, $C_0$, $C_1$, and $C_2$ can be interpreted as the vector spaces generated by vertices, edges, and faces, respectively.

**Project role:** Chain complexes provide the algebraic structure from which we construct homological CSS quantum codes.

**Related concepts:** Boundary map, cycle, boundary, homology, homological CSS code.

## Clifford hierarchy

The **Clifford hierarchy** is defined recursively by

$$
\mathcal P_1=\text{Pauli operators},
$$

and

$$
\mathcal P_j
=
\left\{
U:U\mathcal P_1U^\dagger\subseteq\mathcal P_{j-1}
\right\}.
$$

The second level is the Clifford group. Higher levels contain important non-Clifford operations; for example, $T$ and $CCZ$ lie in the third level. Levels above the second are generally not groups.

**Project role:** The hierarchy measures the algebraic complexity of logical gates constructed from cup products and is the target of dimensional restrictions on protected gates.

**Related concepts:** Copy-cup gate, topologically protected gate, Pauli group.

## Cochain complex and coboundary map

The **cochain group** $C^p$ is the dual space of $C_p$. A **coboundary map**

$$
\delta^p:C^p\longrightarrow C^{p+1}
$$

is dual to a boundary map and satisfies

$$
\delta^{p+1}\delta^p=0.
$$

With fixed bases and the usual column-vector convention, coboundary matrices are transposes of the corresponding boundary matrices.

**Project role:** The cochain viewpoint is natural for describing $X$-type logical operators, cohomology invariants, and the cup-product constructions studied in *Cups and Gates I*.

**Related concepts:** Chain complex, cohomology class, cup product.

## Code parameters and code distance

The notation

$$
[[n,k,d]]
$$

describes a quantum code with $n$ physical qubits, $k$ logical qubits, and **distance** $d$. For a CSS code with valid check matrices,

$$
k
=
n-\operatorname{rank}(H_X)-\operatorname{rank}(H_Z).
$$

The distance is the minimum weight, or number of affected physical qubits, of any nontrivial logical Pauli operator. For a CSS code, the separate distances are

$$
d_X=\min\{|x|:x\in\ker(H_Z)\setminus\operatorname{row}(H_X)\},
\qquad
d_Z=\min\{|z|:z\in\ker(H_X)\setminus\operatorname{row}(H_Z)\},
$$

with $d=\min(d_X,d_Z)$.

**Project role:** These parameters summarize how the topology and cellulation affect storage overhead and error-detecting capability. homoloQode computes them exactly by exhaustive search for small codes only.

**Related concepts:** Logical operator, stabilizer code, decoder.

## Cohomology group and cohomology class

The **$p$-th cohomology group** is

$$
H^p
=
\ker(\delta^p)/\operatorname{im}(\delta^{p-1}).
$$

A **cohomology class** is an equivalence class of cocycles, where two cocycles are equivalent if they differ by a coboundary. Cohomology is dual to homology over a field, but it also carries additional operations, such as the cup product.

**Project role:** A phase function that depends only on a cohomology class acts on logical information rather than on a particular physical representative.

**Related concepts:** Cochain complex, cup product, logical operator.

## Constant-depth circuit

A family of circuits has **constant depth** when the number of sequential gate layers is bounded independently of the code size. Many gates may occur in parallel within a layer, provided they act on disjoint sets of qubits.

Constant depth alone does not imply geometric locality: a layer could still contain gates between arbitrarily distant qubits.

**Project role:** Cup-product constructions aim to produce bounded-depth logical circuits, while topological-protection results additionally require an appropriate locality condition.

**Related concepts:** Geometric locality, copy-cup gate, topologically protected gate.

## Copy-cup gate

A **copy-cup gate** is a diagonal logical gate constructed from an integrated cup product on multiple copies of the same CSS code:

$$
|c_1,\ldots,c_\Lambda\rangle
\longmapsto
(-1)^{\int c_1\cup\cdots\cup c_\Lambda}
|c_1,\ldots,c_\Lambda\rangle.
$$

When the integrated product is well defined and nontrivial on cohomology, it produces a logical operation that can reach level $\Lambda$ of the Clifford hierarchy.

**Project role:** This is a concrete advanced target after the base chain-complex and CSS functionality is implemented.

**Related concepts:** Cup product, Clifford hierarchy, constant-depth circuit.

## Correctable region and cleaning lemma

A region is **correctable** if erasure of all qubits in that region can, in principle, be corrected. Equivalently, the region supports no nontrivial logical operator.

The **cleaning lemma** states that a logical Pauli representative can be multiplied by stabilizers so that its support is removed from a correctable region.

**Project role:** These ideas explain how equivalent logical representatives can be deformed and are central to the proof of restrictions on topologically protected gates.

**Related concepts:** Logical operator, code distance, topologically protected gate.

## CSS code

A **CSS code** is a stabilizer quantum error-correcting code whose stabilizer generators can be separated into $X$-type and $Z$-type checks. It can be described by two binary parity-check matrices,

$$
H_X \quad \text{and} \quad H_Z,
$$

satisfying the commutation condition

$$
H_X H_Z^T = 0 \pmod 2.
$$

This condition ensures that all $X$-type and $Z$-type stabilizer generators commute.

**Project role:** In homological quantum codes, the CSS check matrices are constructed from boundary maps of an underlying chain complex.

**Related concepts:** Stabilizer code, parity-check matrix, homological CSS code, syndrome.

---

## Cup product

The **cup product** is a bilinear operation on cochains,

$$
\cup:C^p\times C^q\longrightarrow C^{p+q},
$$

which descends, under suitable conditions, to a product on cohomology. It combines lower-degree cohomological information into a higher-degree invariant.

The exact cochain-level formula depends on the type of complex and on ordering or orientation conventions. It is therefore additional structure, not something determined by arbitrary check matrices alone.

**Project role:** Integrated cup products are a proposed mechanism for generating diagonal logical gates from cohomology invariants.

**Related concepts:** Cohomology class, copy-cup gate, Clifford hierarchy, preorientation.

## Cycle

A **$p$-cycle** is a chain with zero boundary. The vector space of $p$-cycles is

$$
Z_p=\ker(\partial_p).
$$

For a surface, a $1$-cycle can be represented by a collection of edges in which every vertex has even incidence.

**Project role:** Nontrivial cycles provide candidates for logical operators in homological codes.

**Related concepts:** Boundary, homology class, logical operator.

## Decoder

A **decoder** is an algorithm that uses a measured syndrome and a noise model to choose a correction. It need not reconstruct the exact physical error; it succeeds when the combined error and correction differ from the identity only by a stabilizer.

Different errors can have the same syndrome, and some such differences are logical operators. Decoding is therefore an inference problem, not simply matrix inversion.

**Project role:** The MVP uses deterministic exhaustive search as a correctness reference for small codes. More scalable extensions could use matching-based or specialized qLDPC decoders.

**Related concepts:** Syndrome, logical operator, code distance, noise model.

## Fault-tolerant logical gate

A **fault-tolerant logical gate** implements an operation on encoded information while preventing a small number of physical faults from spreading into an uncorrectable error.

Transversal gates and geometrically local constant-depth circuits are important mechanisms, but fault tolerance is a property of the complete implementation and error model, not merely of the abstract logical unitary.

**Project role:** Advanced phases of homoloQode aim to relate cohomological constructions to explicit physical circuits and to evaluate their error-propagation properties.

**Related concepts:** Logical operator, constant-depth circuit, topologically protected gate.

## Geometric locality and circuit light cone

A circuit is **geometrically local** when its gates act only on qubits that are close in a specified spatial geometry. The **light cone** of a set of qubits is the region to which its influence can propagate through the circuit.

For bounded-range gates and constant depth, a local error has a light cone of bounded size, independent of the total code size.

**Project role:** Geometric support and light-cone growth are necessary to state and test whether a logical circuit has topological protection in the sense used by Bravyi and König.

**Related concepts:** Constant-depth circuit, topologically protected gate, qLDPC code.

## Homological CSS code

A **homological CSS code** is a CSS code obtained from a chain complex. For a two-dimensional complex

$$
C_2\xrightarrow{\partial_2}C_1\xrightarrow{\partial_1}C_0
$$

with physical qubits associated with a basis of $C_1$, homoloQode uses the convention

$$
H_X=\partial_1,
\qquad
H_Z=\partial_2^T.
$$

Consequently,

$$
H_XH_Z^T
=
\partial_1\partial_2
=0.
$$

Rows of $H_X$ define $X$-type checks and rows of $H_Z$ define $Z$-type checks.

**Project role:** This is the central translation implemented by the project: topology becomes a valid CSS stabilizer code through boundary matrices.

**Related concepts:** Chain complex, CSS code, parity-check matrix, logical operator.

## Homology group and homology class

The **$p$-th homology group** is the quotient

$$
H_p=Z_p/B_p
=
\ker(\partial_p)/\operatorname{im}(\partial_{p+1}).
$$

A **homology class** groups together cycles that differ by a boundary. A nonzero class represents a cycle that cannot be filled using the higher-dimensional cells available in the complex.

Over $\mathbb F_2$, these groups are vector spaces, despite retaining the traditional name “group.”

**Project role:** For qubits placed on edges, first homology describes one family of logical degrees of freedom. Its dimension contributes to the number of encoded qubits.

**Related concepts:** Cycle, boundary, logical qubit, cohomology.

## Incidence matrix

An **incidence matrix** records which cells are incident to which lower-dimensional cells. Over $\mathbb F_2$, an entry is $1$ when a lower-dimensional cell occurs in the boundary of a higher-dimensional cell and $0$ otherwise.

For example, with vertices indexing rows and edges indexing columns, the vertex-edge incidence matrix represents

$$
\partial_1:C_1\longrightarrow C_0.
$$

**Project role:** Incidence matrices are the concrete data structures from which
homoloQode builds boundary maps and CSS check matrices.

**Related concepts:** Cell complex, boundary map, parity-check matrix.

## Logical operator and logical qubit

A **logical operator** preserves the code space but acts nontrivially on the encoded information. A logical Pauli commutes with every stabilizer but is not itself a stabilizer.

For the CSS convention used here, binary representatives satisfy

$$
Z_{\mathrm{logical}}
\in
\ker(H_X)/\operatorname{row}(H_Z),
$$

and

$$
X_{\mathrm{logical}}
\in
\ker(H_Z)/\operatorname{row}(H_X).
$$

A **logical qubit** is one encoded two-dimensional degree of freedom on which a corresponding pair of anticommuting logical $X$ and $Z$ operators acts.

**Project role:** Finding explicit logical representatives and relating them to nontrivial cycles and cocycles is a core goal of homoloQode.

**Related concepts:** Homology class, cohomology class, stabilizer code, code distance.

## Noise model and Pauli error

A **noise model** is a mathematical or computational description of how faults occur, including their probabilities, correlations, and locations in time or space. A **Pauli error model** approximates faults using random $X$, $Y$, and $Z$ operators.

Code distance is independent of a particular probability distribution, whereas decoder performance depends strongly on the chosen noise model.

**Project role:** `IndependentPauliNoise` supplies reproducible per-qubit I/X/Y/Z sampling for the MVP experiments. It excludes correlated and measurement errors.

**Related concepts:** Pauli group, syndrome, decoder, code distance.

## Parity-check matrix

A **parity-check matrix** is a binary matrix whose rows encode linear constraints. In a CSS code, $H_X$ and $H_Z$ encode the supports of $X$- and $Z$-type stabilizer generators.

The equation

$$
H_XH_Z^T=0
$$

states that every $X$-type generator overlaps every $Z$-type generator on an even number of qubits, which makes the corresponding Pauli operators commute.

**Project role:** Check matrices are the main algebraic output of the first planned API and the bridge to syndrome calculation.

**Related concepts:** CSS code, incidence matrix, syndrome.

## Pauli operator and Pauli group

The single-qubit **Pauli operators** are $I$, $X$, $Y$, and $Z$. Tensor products of these operators, together with phase factors, form the **$n$-qubit Pauli group**.

Two Pauli operators either commute or anticommute. This binary commutation relation is what allows stabilizer checks to detect Pauli errors.

**Project role:** Physical errors, stabilizer generators, and logical Pauli operators are all represented as elements of the Pauli group or as equivalent binary vectors.

**Related concepts:** Binary symplectic representation, stabilizer code, syndrome.

## Preorientation and integrated Leibniz rule

In *Cups and Gates I*, a **preorientation** partitions the bits incident to a check into incoming, outgoing, and free subsets. This combinatorial structure is used to define cup-product-like operations for codes that do not arise directly from a simplicial complex.

The **integrated Leibniz rule** is a weakened form of the usual product rule for a differential. It requires the sum of terms obtained by applying the coboundary in each input position to vanish after integration. This ensures that the resulting integrated product depends only on cohomology classes.

**Project role:** Preorientations may provide a finite, testable data structure for extending cup-product gates beyond explicitly topological complexes.

**Related concepts:** Cup product, cohomology class, qLDPC code.

## qLDPC code

A **quantum low-density parity-check code**, or **qLDPC code**, is a family of quantum codes whose check operators have bounded weight and in which each physical qubit participates in a bounded number of checks as the code grows.

LDPC locality is combinatorial: it does not by itself imply that interacting qubits are near one another in a fixed-dimensional geometric embedding.

**Project role:** The cup-product framework motivates possible later experiments with homological qLDPC constructions. The distinction between LDPC and geometric locality is essential when interpreting fault-tolerance results.

**Related concepts:** Geometric locality, constant-depth circuit, cup product.

## Quantum circuit

A **quantum circuit** is an ordered collection of quantum gates, state preparations, measurements, and classical control operations acting on qubits. Gates that do not depend on one another and act on disjoint qubits may be placed in the same parallel layer.

An abstract code definition does not automatically provide a complete circuit. For example, check matrices specify stabilizers, but syndrome extraction additionally requires ancilla qubits, a gate schedule, and measurements.

**Project role:** The core constructs abstract CSS codes. The Qiskit integration
layer generates ideal syndrome-extraction circuits from those code objects.

**Related concepts:** Constant-depth circuit, syndrome, fault-tolerant logical gate.

## Reproducibility and dependency

A computational result is **reproducible** when another person can recreate it from the repository using documented inputs, software versions, and commands. A **dependency** is an external package on which the project relies.

Reproducibility normally requires declared dependencies, a supported Python version, deterministic examples where possible, and instructions for running tests and notebooks.

**Project role:** The package declares its runtime dependencies and supported
Python version in `pyproject.toml`. Continuous integration installs from that
metadata and executes the tests and notebooks on Windows and Ubuntu.

**Related concepts:** API, automated test, quantum circuit.

## Stabilizer code

A **stabilizer code** is the simultaneous $+1$ eigenspace of an abelian subgroup of the Pauli group that does not contain $-I$. The subgroup is normally specified by a set of independent commuting generators called **stabilizer generators**.

If there are $n$ physical qubits and $r$ independent stabilizer generators, the code space has dimension $2^{n-r}$ and encodes

$$
k=n-r
$$

logical qubits.

**Project role:** homoloQode converts topological incidence data into stabilizer generators and verifies that they commute.

**Related concepts:** CSS code, logical qubit, syndrome, code parameters.

## Surface code and relative homology

A **surface code** is a topological CSS code constructed from a surface or planar cellulation, often with boundaries. Different boundary types determine which error strings may terminate without creating a syndrome.

**Relative homology** modifies the usual cycle and boundary relations by treating a chosen subspace, such as part of the physical boundary, as trivial. This is the natural language for many planar surface-code logical operators.

**Project role:** Planar surface codes are a planned extension after the periodic toric-code MVP. Supporting them will require boundary metadata and relative-homology conventions.

**Related concepts:** Toric code, homology class, logical operator.

## Syndrome

An error **syndrome** records which stabilizer checks anticommute with an error. For binary CSS errors, a $Z$-error vector $\mathbf e_Z$ produces the $X$-check syndrome

$$
\mathbf s_X=H_X\mathbf e_Z^T,
$$

and an $X$-error vector $\mathbf e_X$ produces

$$
\mathbf s_Z=H_Z\mathbf e_X^T.
$$

All arithmetic is over $\mathbb F_2$.

**Project role:** Syndrome computation connects the static CSS construction to error sampling, exhaustive decoding, and memory experiments.

**Related concepts:** Pauli error, stabilizer code, decoder.

## Topologically protected gate

In the setting of local topological stabilizer codes, a **topologically protected gate** is a logical operation implemented by a geometrically local circuit whose depth and interaction range remain bounded as the code grows.

The Bravyi-König theorem states that such a logical gate in spatial dimension $D$ cannot lie above level $D$ of the Clifford hierarchy. In particular, two-dimensional codes are restricted to protected Clifford gates.

**Project role:** This concept supplies a precise limitation against which proposed logical-gate constructions should be checked.

**Related concepts:** Geometric locality, constant-depth circuit, Clifford hierarchy.

## Toric code

The **toric code** is a topological CSS code defined on a cellulation with periodic boundary conditions, topologically equivalent to a torus. In the standard construction, qubits lie on edges, $X$ checks are associated with vertices, and $Z$ checks with faces.

Its logical operators are represented by noncontractible cycles and dual cycles wrapping around the torus.

**Project role:** A small periodic square-lattice toric code is the first target example because it exhibits nontrivial logical operators without introducing physical boundaries.

**Related concepts:** Cell complex, homological CSS code, surface code.
