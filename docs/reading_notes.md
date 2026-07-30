# Reading Notes

This file collects short reading notes for the **homoloQode** project.

The goal is not to produce complete paper summaries. Instead, each entry should identify the concepts, definitions, equations, and implementation ideas that are directly relevant to the project.

These notes are intended to be collaborative and preliminary. We can add, revise, or reorganize entries as our understanding of the project develops.

---

## Reading template

```markdown
## Reference title

**Citation:**  
Author(s), *Title*, year. Link: ...

**Read by:**  
Name(s), date.

### Main concepts

- ...

### Definitions to add to the glossary

- ...

### Equations or constructions relevant to the project

- ...

### Possible implementation ideas for later

- ...

### Open questions

- ...
```

---

## 1. Gottesman -- Stabilizer Codes and Quantum Error Correction

**Citation:**
Daniel Gottesman, *Stabilizer Codes and Quantum Error Correction*, 1997.
Link: https://arxiv.org/abs/quant-ph/9705052

**Read by:**
TBD

### Main concepts

* Stabilizer formalism
* Pauli group
* Stabilizer generators
* Syndrome measurement
* Logical operators
* Code distance

### Definitions to add to the glossary

* Stabilizer code
* Pauli group
* Syndrome
* Logical operator
* Code distance

### Equations or constructions relevant to the project

* A stabilizer code is defined as the simultaneous $+1$ eigenspace of an abelian subgroup of the Pauli group.
* Errors are detected through their commutation or anti-commutation with stabilizer generators.

### Possible implementation ideas for later

* Represent Pauli operators in binary or symplectic form
* Compute syndromes from commutation relations
* Check whether a proposed stabilizer set is mutually commuting

### Open questions

* Which stabilizer representation should we use in the first prototype: explicit Pauli strings, binary matrices, or both?
* How much of the general stabilizer formalism do we need before specializing to CSS codes?

---

## 2. Dennis-Kitaev-Landahl-Preskill -- Topological Quantum Memory

**Citation:**
Eric Dennis, Alexei Kitaev, Andrew Landahl, and John Preskill, *Topological Quantum Memory*, 2001/2002.
Link: https://arxiv.org/abs/quant-ph/0110143

**Read by:**
TBD

### Main concepts

* Toric code
* Surface code
* Local stabilizer checks
* Error chains
* Logical operators as nontrivial cycles
* Decoding as a geometric matching problem

### Definitions to add to the glossary

* Toric code
* Surface code
* Error chain
* Nontrivial cycle
* Decoder

### Equations or constructions relevant to the project

* Qubits can be placed on edges of a lattice
* $X$-type checks are associated with vertices
* $Z$-type checks are associated with faces
* Logical operators correspond to topologically nontrivial cycles

### Possible implementation ideas for later

* Build a small periodic square lattice
* Generate vertex-edge and face-edge incidence matrices
* Use incidence matrices to construct $H_X$ and $H_Z$
* Visualize error chains and syndromes on the lattice

### Open questions

* Should the first prototype use a toric code with periodic boundary conditions?
* What is the smallest example that still shows nontrivial logical operators?
* When should we introduce decoding: immediately with brute force, or later?

---

## 3. Breuckmann-Davydova-Eberhardt-Tantivasadakarn -- Cups and Gates I

**Citation:**
Nikolas P. Breuckmann, Margarita Davydova, Jens N. Eberhardt, and Nathanan Tantivasadakarn, *Cups and Gates I: Cohomology invariants and logical quantum operations*, 2025.
Link: https://arxiv.org/abs/2410.16250

**Read by:**
Claudia Zendejas-Morales, July 2026.

### Main concepts

* CSS codes as cochain complexes
* Cohomology invariants as logical phase functions
* Cup products and integrated cup products
* Copy-cup logical gates
* Constant-depth logical circuits
* qLDPC codes and the Clifford hierarchy
* Preorientations and the integrated Leibniz rule

### Definitions to add to the glossary

* Cochain complex
* Cohomology class
* Cup product
* qLDPC code
* Clifford hierarchy
* Constant-depth circuit
* Preorientation

### Equations or constructions relevant to the project

* A CSS code can be represented by a cochain complex
  $$
  C^0 \xrightarrow{\delta^0} C^1 \xrightarrow{\delta^1} C^2,
  $$
  with physical qubits associated with a basis of $C^1$ and logical information represented by
  $$
  H^1=\ker(\delta^1)/\operatorname{im}(\delta^0).
  $$
* An integrated $\Lambda$-fold cup product defines a phase function
  $$
  \Psi_{\cup,\Lambda}(c_1,\ldots,c_\Lambda)
  =
  \int c_1\cup\cdots\cup c_\Lambda.
  $$
* When this function depends only on cohomology classes, it defines the diagonal logical operation
  $$
  |c_1,\ldots,c_\Lambda\rangle
  \longmapsto
  (-1)^{\int c_1\cup\cdots\cup c_\Lambda}
  |c_1,\ldots,c_\Lambda\rangle.
  $$
* For suitable codes, the physical circuit is composed of controlled-$Z$-type gates, has bounded depth, and induces an operation at level $\Lambda$ of the Clifford hierarchy.

### Possible implementation ideas for later

* Add a cochain-complex view of the same data used by the homological CSS construction
* Implement cup products first on a small simplicial or cubical complex
* Verify computationally that an integrated cup product is unchanged after adding a coboundary
* Derive the physical $CZ$ pattern for two copies of a small two-dimensional toric code
* Represent a candidate preorientation and test the integrated Leibniz condition
* Keep this functionality separate from the first toric-code MVP until the basic chain-complex and CSS interfaces are stable

### Open questions

* Which class of complexes should provide the first concrete cup-product implementation?
* Can the project expose cup products without committing to a full differential graded algebra API?
* How should multiple copies of a code and the induced logical action be represented?
* Which conditions can be verified algorithmically for a finite input code?
* Is the two-copy toric-code $CZ$ example small enough to become the first advanced notebook?

---

## 4. Bravyi-Konig -- Classification of Topologically Protected Gates

**Citation:**
Sergey Bravyi and Robert König, *Classification of topologically protected gates for local stabilizer codes*, 2013.
Link: https://arxiv.org/abs/1206.1609

**Read by:**
Claudia Zendejas-Morales, July 2026.

### Main concepts

* Topological stabilizer codes
* Geometrically local constant-depth circuits
* Topologically protected logical gates
* Clifford hierarchy
* Cleaning lemma
* Union lemma
* Correctable regions and light cones

### Definitions to add to the glossary

* Geometric locality
* Topologically protected gate
* Correctable region
* Cleaning lemma
* Circuit light cone

### Equations or constructions relevant to the project

* The Clifford hierarchy is defined recursively by
  $$
  \mathcal P_1=\text{Pauli operators},
  \qquad
  \mathcal P_j=
  \left\{
  U:U\mathcal P_1U^\dagger\subseteq\mathcal P_{j-1}
  \right\}.
  $$
* The Bravyi-König result bounds a logical gate implemented by a geometrically local constant-depth circuit in a $D$-dimensional topological stabilizer code:
  $$
  U_{\mathrm{logical}}\in\mathcal P_D.
  $$
* In two dimensions, protected logical gates are therefore restricted to Clifford operations.
* The proof uses cleaned logical representatives and nested commutators whose support is progressively confined to correctable regions.

### Possible implementation ideas for later

* Store geometric support information for cells, checks, and gates when a code has an embedding
* Compute the support expansion produced by a finite-depth local circuit
* Illustrate the two-dimensional restriction using logical loops of a toric code
* Classify implemented logical actions as Pauli, Clifford, or a higher-level operation in small examples
* Use this result as a consistency check for gates constructed from cup products

### Open questions

* How much geometric information should be part of the core data model rather than a visualization layer?
* What operational definition of locality should homoloQode use for non-Euclidean or non-geometric qLDPC codes?
* Can small computational checks distinguish a genuinely protected logical gate from a logical operation that merely preserves the code space?
* How should the project communicate that the Bravyi-König bound depends on geometric locality, whereas LDPC locality alone is different?

