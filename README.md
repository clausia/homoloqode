# homoloQode

[![Tests and notebooks](https://github.com/clausia/homoloqode/actions/workflows/tests.yml/badge.svg)](https://github.com/clausia/homoloqode/actions/workflows/tests.yml)

**homoloQode** is a research-software project for exploring the connection between topology, homology, and quantum error-correcting codes.

The goal is to build a Python-based toolkit that starts from simple combinatorial or topological data, such as cell complexes or surface-like graphs, and constructs the corresponding homological CSS/stabilizer quantum codes. The project aims to connect mathematical structure with reproducible software, examples, tests, and explanatory notebooks.

## Motivation

Topological and homological quantum codes provide a natural bridge between algebraic topology and quantum error correction. In these codes, geometric and combinatorial structures such as vertices, edges, faces, boundary maps, cycles, and homology classes can be translated into quantum-code data such as parity-check matrices, stabilizer generators, logical operators, and syndromes.

Many introductory quantum-computing projects implement a single known algorithm or a small code example. In contrast, **homoloQode** aims to develop a more structural and reusable framework for constructing and studying small homological quantum codes from their underlying mathematical data.

Version 0.1.0 is the first MVP release candidate. Its API remains experimental.

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
* Integrate the resulting codes and circuits with Qiskit
* Provide clear notebooks, tests, and documentation

## Initial scope

The first implemented example is a small toric code constructed from boundary
maps on a periodic square lattice, with physical qubits placed on edges. This
provides a clean starting point because it directly connects:

* a two-dimensional cell complex
* boundary maps
* homology classes
* CSS stabilizer checks
* logical operators
* syndromes
* and decoding intuition

Planned post-MVP directions include:

* planar surface codes with boundaries
* relative homology
* cup products and fault-tolerant logical-gate research
* Khovanov-related quantum codes and graded chain complexes
* homology-preserving transformations that change physical code parameters
* scalable decoder and simulator integrations such as PyMatching and Stim

## Repository structure

```text
homoloQode/
├── README.md
├── CHANGELOG.md
├── pyproject.toml
├── LICENSE
├── docs/
│   ├── architecture.md
│   ├── glossary.md
│   ├── mvp_roadmap.md
│   ├── release.md
│   └── reading_notes.md
├── references/
├── notebooks/
│   ├── 01_toric_code_from_boundary_maps.ipynb
│   ├── 02_algebraic_vs_qiskit_syndromes.ipynb
│   └── 03_noise_and_decoding.ipynb
├── src/homoloqode/
│   ├── algebra/
│   ├── codes/
│   ├── decoders/
│   ├── noise/
│   ├── experiments/
│   ├── topology/
│   ├── cohomology/
│   ├── khovanov/
│   ├── transformations/
│   ├── integrations/
│   └── visualization/
└── tests/
```

The core package separates combinatorial cell data, binary chain complexes, and
abstract CSS codes. The architectural decisions and extension boundaries are
documented in [`docs/architecture.md`](docs/architecture.md). The current MVP,
issue dependencies, parallel work plan, and post-MVP research directions are
described in [`docs/mvp_roadmap.md`](docs/mvp_roadmap.md).

## Quick start

### 1. Create an environment

Using an isolated environment is strongly recommended, but homoloQode does not
depend on a particular environment manager. Choose one of the following
options, or use another tool such as `uv`, Poetry, or virtualenv.

<details>
<summary><strong>Conda</strong></summary>

Create and activate a Conda environment with Python 3.12:

```bash
conda create --name homoloqode python=3.12
conda activate homoloqode
```

</details>

<details>
<summary><strong>Python venv: Windows PowerShell</strong></summary>

Create and activate an environment using Python's built-in `venv` module:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

</details>

<details>
<summary><strong>Python venv: macOS or Linux</strong></summary>

Create and activate an environment using Python's built-in `venv` module:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

</details>

If an environment is already active, or you intentionally do not want to use
one, continue directly with the installation step.

### 2. Install homoloQode

From the repository root (the directory containing `pyproject.toml`), install
the package and its runtime dependencies in editable mode:

```bash
python -m pip install -e .
```

For development, including tests, coverage measurement, and notebooks, install
the `dev` extra instead:

```bash
python -m pip install -e ".[dev]"
```

These commands are independent of how the Python environment was created.

The requirements are declared in `pyproject.toml`. Runtime dependencies are
Matplotlib 3.10, NumPy 2.5, and Qiskit 2.5 with visualization support. The
`dev` extra contains Coverage.py, IPython's Jupyter kernel, Jupyter, nbconvert,
and pytest. Qiskit is kept in a separate integration layer from the
mathematical core, but it is part of the required MVP.

### 3. Run a notebook

When using an IDE with notebook support, open the `.ipynb` file directly and
select the Python interpreter from the environment where homoloQode was
installed. No separate Jupyter command or kernel registration is normally
needed.

To use Jupyter outside an IDE, run the following command from the repository
root and open the desired file from the browser:

```bash
jupyter notebook
```

The introductory notebook is:

```text
notebooks/01_toric_code_from_boundary_maps.ipynb
```

<details>
<summary><strong>Optional: register the environment as a Jupyter kernel</strong></summary>

Most users do not need this step. Use it only if Jupyter is running outside an
IDE and does not show the environment where homoloQode is installed:

```bash
python -m ipykernel install --user --name homoloqode --display-name "Python (homoloqode)"
```

After registering it, select `Python (homoloqode)` from Jupyter's kernel menu.

</details>

### 4. Use homoloQode

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

### 5. Run an error-correction cycle

This deterministic example creates a toric code, specifies an X error,
computes its syndrome, decodes it, and classifies the residual:

```python
import numpy as np

from homoloqode import toric_code
from homoloqode.decoders import ResidualClass, classify_residual, decode_syndrome
from homoloqode.noise import PauliError

code = toric_code(2)
x_support = np.zeros(code.n, dtype=np.uint8)
x_support[0] = 1
error = PauliError(x=x_support, z=np.zeros(code.n, dtype=np.uint8))

syndrome = code.syndrome(x_error=error.x, z_error=error.z)
correction = decode_syndrome(code, syndrome)
residual = classify_residual(
    code,
    x_residual=error.x ^ correction.x_correction.support,
    z_residual=error.z ^ correction.z_correction.support,
)

print(residual.value)  # stabilizer
print(residual is ResidualClass.STABILIZER)  # True
```

The decoder's correction need not equal the physical error. Success means that
their residual is a stabilizer, so it acts trivially on encoded information.

### 6. Run the tests

After installing the `dev` extra, run the test suite and enforce complete line
and branch coverage with:

```bash
python -m coverage run -m pytest
python -m coverage report
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

The shared terminology is maintained in [`docs/glossary.md`](docs/glossary.md).

## Reading list

The initial reading list is maintained in [`references/reading_list.md`](references/reading_list.md).

It includes a small set of core references on stabilizer/CSS codes, topological quantum memories, surface codes, and homological quantum error correction.


## Development status

The MVP implementation includes:

* exact binary linear algebra over $\mathbb F_2$;
* finite two-dimensional cell complexes;
* three-term chain complexes and boundary validation;
* periodic square toric codes with qubits on edges;
* construction and validation of $H_X$ and $H_Z$;
* CSS syndromes and Pauli stabilizer strings;
* paired logical $X$ and $Z$ representatives;
* exact X, Z, and overall distance searches for small CSS codes;
* reproducible independent Pauli noise sampling;
* exhaustive minimum-weight decoding for small CSS codes;
* classification of residual stabilizer successes, logical failures, and
  invalid corrections;
* seeded single-trial and aggregate quantum-memory experiment APIs;
* automated tests for the size-two and size-three toric codes;
* an [explanatory notebook](notebooks/01_toric_code_from_boundary_maps.ipynb)
  deriving a toric code from boundary maps;
* ideal Qiskit syndrome-extraction circuits and a
  [comparison notebook](notebooks/02_algebraic_vs_qiskit_syndromes.ipynb);
* an [experiment notebook](notebooks/03_noise_and_decoding.ipynb) sweeping
  physical error probability against logical failure rate for the
  size-two and size-three toric codes;
* periodic-lattice visualizations with error, syndrome, and logical overlays;
* continuous integration on Windows and Ubuntu that enforces complete line and
  branch coverage and executes every committed notebook.

All MVP implementation work is present in the 0.1.0 release candidate. The
[MVP and project roadmap](docs/mvp_roadmap.md) describes post-MVP directions,
and [release.md](docs/release.md) records the release decisions and final
external checks. The API remains experimental.

## MVP limitations

Version 0.1.0 is a correctness-oriented reference implementation for small
codes. It intentionally does not provide:

* scalable distance search or decoding;
* threshold-scale simulation or statistical error bars;
* correlated, circuit-level, or measurement noise;
* repeated syndrome rounds or fault-tolerant extraction schedules;
* quantum-hardware execution;
* general surface-code boundaries, cup products, Khovanov-code construction,
  or certified homology-preserving transformations;
* API compatibility guarantees before a later stable release.

## Release

The release candidate version is `0.1.0`, supports Python 3.12, and is intended
to receive the Git tag `v0.1.0` after this PR is merged and CI is green. PyPI
publication is deferred; this release is distributed from the repository. See
[CHANGELOG.md](CHANGELOG.md) and [docs/release.md](docs/release.md).

## License

This project is released under the MIT License.

## Authors

* Claudia Zendejas-Morales
* Amey Joshi

## Citation

Version 0.1.0 has no DOI or `CITATION.cff`. Until an archived release exists,
cite the repository URL, authors, version `0.1.0`, and Git tag `v0.1.0` once the
tag is available. A formal citation file is deferred to a later research
release.

## Project vision

The long-term vision of **homoloQode** is to become a small but clear research-software toolkit for learning, constructing, and experimenting with homological quantum codes. The project is intended to be mathematically grounded, computationally reproducible, and useful both as a learning resource and as a foundation for small exploratory experiments in quantum error correction.
