# Changelog

All notable changes to homoloQode are recorded here.

## 0.1.0 - 2026-09-28

First minimum viable product release.

### Added

- Exact binary linear algebra over $\mathbb F_2$.
- Ordered two-dimensional cell and chain-complex representations.
- Periodic square toric complexes and homological CSS-code construction.
- Stabilizers, syndromes, paired logical representatives, and exact distance
  search for small CSS codes.
- Reproducible independent Pauli noise and deterministic exhaustive decoding.
- Residual classification and reusable seeded memory experiments.
- Ideal local Qiskit syndrome-extraction circuits.
- Periodic-lattice visualization with error, syndrome, and logical overlays.
- Three executable notebooks covering construction, circuit comparison, and
  noise/decoding experiments.
- Windows and Ubuntu CI for tests, complete line/branch coverage, and notebook
  execution.

### Limitations

- Distance search and decoding are exponential reference implementations.
- Noise is independent per-qubit Pauli noise; measurement and correlated
  errors are excluded.
- Qiskit circuits are ideal validation circuits, not fault-tolerant schedules.
- Threshold studies, hardware execution, package-index publication, and API
  stability guarantees are deferred.
