# Reading Notes

This file collects short reading notes for the **homoloQode** project.

The goal is not to produce complete paper summaries. Instead, each entry should identify the concepts, definitions, equations, and implementation ideas that are directly relevant to the project.

These notes are intended to be collaborative and preliminary. We can add, revise, or reorganize entries as our understanding of the project develops.

---

## Reading template

```markdown id="gic4yy"
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


