# homoloQode

**homoloQode** is a research-software project for exploring the connection between topology, homology, and quantum error-correcting codes.

The goal is to build a Python-based toolkit that starts from simple combinatorial or topological data, such as cell complexes or surface-like graphs, and constructs the corresponding homological CSS/stabilizer quantum codes. The project aims to connect mathematical structure with reproducible software, examples, tests, and explanatory notebooks.

## Motivation

Topological and homological quantum codes provide a natural bridge between algebraic topology and quantum error correction. In these codes, geometric and combinatorial structures such as vertices, edges, faces, boundary maps, cycles, and homology classes can be translated into quantum-code data such as parity-check matrices, stabilizer generators, logical operators, and syndromes.

Many introductory quantum-computing projects implement a single known algorithm or a small code example. In contrast, **homoloQode** aims to develop a more structural and reusable framework for constructing and studying small homological quantum codes from their underlying mathematical data.

The project is currently in a preparation and prototyping phase.

## Project goals

The initial goals of **homoloQode** are:

* Represent simple cell complexes or surface-like graphs using combinatorial data
* Construct boundary maps over $\mathbb{F}_2$
* Verify the chain-complex condition $\partial_1 \partial_2 = 0$
* Translate boundary maps into CSS check matrices $H_X$ and $H_Z$
* Verify the CSS commutation condition $H_X H_Z^T = 0 \pmod 2$
* Identify candidate logical operators through cycles, boundaries, and homology classes
* Simulate simple Pauli errors and compute syndromes
* Implement small decoding experiments for selected examples
* Provide clear notebooks, tests, and documentation

## Initial scope

The first target example will likely be a small toric code constructed from boundary maps. This provides a clean starting point because it directly connects:

* a two-dimensional cell complex
* boundary maps
* homology classes
* CSS stabilizer checks
* logical operators
* syndromes
* and decoding intuition

Possible later extensions include:

* planar surface codes with boundaries
* relative homology
* visualization of lattices and logical operators
* simple noise and decoding experiments
* integration with Qiskit, Stim, or PyMatching

## Repository structure

```text
homoloQode/
├── README.md
├── pyproject.toml
├── LICENSE
├── docs/
│   ├── architecture.md
│   ├── glossary.md
│   └── reading_notes.md
├── references/
├── notebooks/
├── src/homoloqode/
│   ├── algebra/
│   ├── codes/
│   ├── topology/
│   ├── cohomology/
│   ├── khovanov/
│   ├── transformations/
│   └── integrations/
└── tests/
```

The core package separates combinatorial cell data, binary chain complexes, and
abstract CSS codes. The architectural decisions and extension boundaries are
documented in [`docs/architecture.md`](docs/architecture.md).

## Quick start

Create an environment and install the package in editable mode:

```bash
python -m pip install -e ".[test]"
```

Construct a periodic square toric code:

```python
from homoloqode import square_toric_complex

cell_complex = square_toric_complex(size=3)
chain_complex = cell_complex.to_chain_complex()
code = chain_complex.to_css_code()

assert code.n == 18
assert code.k == 2
assert chain_complex.betti_1 == 2
```

Run the test suite with:

```bash
python -m pytest
```

## Core concepts

The project is organized around the following concepts:

* **Stabilizer codes**
* **CSS codes**
* **Pauli errors**
* **Syndromes**
* **Logical operators**
* **Code distance**
* **Cell complexes**
* **Chain complexes**
* **Boundary maps**
* **Cycles and boundaries**
* **Homology classes**
* **Toric and surface codes**

A shared glossary will be developed in [`docs/glossary.md`](docs/glossary.md).

## Reading list

The initial reading list is maintained in [`references/reading_list.md`](references/reading_list.md).

It includes a small set of core references on stabilizer/CSS codes, topological quantum memories, surface codes, and homological quantum error correction.


## Development status

The first implementation scaffold is now available. It includes exact binary
linear algebra, finite two-dimensional cell complexes, three-term chain
complexes, CSS-code construction, paired logical representatives, syndromes,
and periodic square toric-code examples.

The API remains experimental. The next MVP tasks are optional Qiskit adapters,
small-code distance calculations, explanatory notebooks, and simple decoding
experiments.

## License

This project is released under the MIT License.

## Authors

* Claudia Zendejas-Morales
* Amey Joshi

## Citation

A formal citation file may be added later if the project develops into a more complete research-software artifact.

## Project vision

The long-term vision of **homoloQode** is to become a small but clear research-software toolkit for learning, constructing, and experimenting with homological quantum codes. The project is intended to be mathematically grounded, computationally reproducible, and useful both as a learning resource and as a foundation for small exploratory experiments in quantum error correction.
