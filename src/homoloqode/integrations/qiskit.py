"""Ideal Qiskit syndrome-extraction circuits for binary CSS codes.

The circuits in this module are intended to validate the algebra-to-circuit
translation. They reuse one ancilla and assume ideal gates and measurements;
they are not fault-tolerant extraction schedules.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np
from numpy.typing import ArrayLike
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.providers.basic_provider import BasicSimulator

from homoloqode.algebra.gf2 import BinaryArray, as_binary_vector
from homoloqode.codes import CSSCode, CSSSyndrome


@dataclass(frozen=True, slots=True)
class QiskitSyndromeCircuits:
    """Ideal circuits ordered like the source code's X and Z check rows."""

    x_checks: QuantumCircuit
    z_checks: QuantumCircuit


@dataclass(frozen=True, slots=True)
class QiskitSyndromeResult:
    """Ideal result in the source code's X-check and Z-check row orders.

    Qiskit's displayed bitstrings remain available in ``x_check_counts`` and
    ``z_check_counts``. ``syndrome`` converts them to increasing matrix-row
    order.
    """

    circuits: QiskitSyndromeCircuits
    syndrome: CSSSyndrome
    x_check_counts: Mapping[str, int]
    z_check_counts: Mapping[str, int]


def _error_vector(
    values: ArrayLike | None, *, length: int, name: str
) -> BinaryArray:
    if values is None:
        vector = as_binary_vector(
            np.zeros(length, dtype=np.uint8),
            name=name,
        )
    else:
        vector = as_binary_vector(values, name=name)
    if vector.shape[0] != length:
        raise ValueError(f"{name} must have length n={length}.")
    return vector


def _apply_pauli_error(
    circuit: QuantumCircuit,
    data: QuantumRegister,
    x_error: BinaryArray,
    z_error: BinaryArray,
) -> None:
    for qubit, bit in enumerate(x_error):
        if bit:
            circuit.x(data[qubit])
    for qubit, bit in enumerate(z_error):
        if bit:
            circuit.z(data[qubit])


def _new_circuit(
    *, data_qubits: int, check_count: int, name: str
) -> tuple[QuantumCircuit, QuantumRegister, QuantumRegister, ClassicalRegister]:
    data = QuantumRegister(data_qubits, "data")
    ancilla = QuantumRegister(1, "ancilla")
    syndrome = ClassicalRegister(check_count, "syndrome")
    return QuantumCircuit(data, ancilla, syndrome, name=name), data, ancilla, syndrome


def _x_check_circuit(
    code: CSSCode,
    *,
    x_error: BinaryArray,
    z_error: BinaryArray,
) -> QuantumCircuit:
    circuit, data, ancilla, syndrome = _new_circuit(
        data_qubits=code.n,
        check_count=code.hx.shape[0],
        name="measure_x_checks",
    )

    circuit.h(data)
    _apply_pauli_error(circuit, data, x_error, z_error)
    circuit.barrier()

    for check_index, check in enumerate(code.hx):
        circuit.h(ancilla[0])
        for qubit, bit in enumerate(check):
            if bit:
                circuit.cx(ancilla[0], data[qubit])
        circuit.h(ancilla[0])
        circuit.measure(ancilla[0], syndrome[check_index])
        if check_index + 1 < code.hx.shape[0]:
            circuit.reset(ancilla[0])

    return circuit


def _z_check_circuit(
    code: CSSCode,
    *,
    x_error: BinaryArray,
    z_error: BinaryArray,
) -> QuantumCircuit:
    circuit, data, ancilla, syndrome = _new_circuit(
        data_qubits=code.n,
        check_count=code.hz.shape[0],
        name="measure_z_checks",
    )

    _apply_pauli_error(circuit, data, x_error, z_error)
    circuit.barrier()

    for check_index, check in enumerate(code.hz):
        for qubit, bit in enumerate(check):
            if bit:
                circuit.cx(data[qubit], ancilla[0])
        circuit.measure(ancilla[0], syndrome[check_index])
        if check_index + 1 < code.hz.shape[0]:
            circuit.reset(ancilla[0])

    return circuit


def build_syndrome_circuits(
    code: CSSCode,
    *,
    x_error: ArrayLike | None = None,
    z_error: ArrayLike | None = None,
) -> QiskitSyndromeCircuits:
    """Build ideal circuits measuring both CSS syndrome components.

    The X-check circuit prepares data in ``|+>^n`` and therefore has a known
    zero syndrome before applying the error. The Z-check circuit analogously
    starts in ``|0>^n``. This makes the circuit results directly comparable to
    ``H_X e_Z`` and ``H_Z e_X`` without requiring encoded-state preparation.
    Data-qubit indices follow ``code.qubit_labels``; classical-bit indices
    follow the corresponding check-row order.
    """

    x = _error_vector(x_error, length=code.n, name="X-error support")
    z = _error_vector(z_error, length=code.n, name="Z-error support")
    return QiskitSyndromeCircuits(
        x_checks=_x_check_circuit(code, x_error=x, z_error=z),
        z_checks=_z_check_circuit(code, x_error=x, z_error=z),
    )


def counts_to_syndrome(
    counts: Mapping[str, int],
    *,
    check_count: int,
) -> BinaryArray:
    """Convert the most frequent Qiskit bitstring to check-row order.

    Qiskit prints the highest-index classical bit first. ``CSSCode`` stores
    check rows in increasing index order, so the selected bitstring is reversed.
    """

    if check_count < 0:
        raise ValueError("check_count must be nonnegative.")
    if not counts:
        raise ValueError("Counts cannot be empty.")

    bitstring = max(counts.items(), key=lambda item: item[1])[0].replace(" ", "")
    if any(bit not in "01" for bit in bitstring):
        raise ValueError(f"Unsupported Qiskit count key {bitstring!r}.")
    if len(bitstring) != check_count:
        raise ValueError(
            f"Expected {check_count} syndrome bits; got {len(bitstring)}."
        )
    return as_binary_vector(
        [int(bit) for bit in reversed(bitstring)],
        name="Qiskit syndrome",
    )


def simulate_syndrome(
    code: CSSCode,
    *,
    x_error: ArrayLike | None = None,
    z_error: ArrayLike | None = None,
    shots: int = 128,
    seed: int = 12345,
) -> QiskitSyndromeResult:
    """Run ideal simulations and return syndrome vectors in check-row order."""

    if not isinstance(shots, int) or isinstance(shots, bool) or shots < 1:
        raise ValueError("shots must be a positive integer.")

    circuits = build_syndrome_circuits(
        code,
        x_error=x_error,
        z_error=z_error,
    )
    backend = BasicSimulator()
    job = backend.run(
        [circuits.x_checks, circuits.z_checks],
        shots=shots,
        seed_simulator=seed,
    )
    result = job.result()
    x_counts = result.get_counts(0)
    z_counts = result.get_counts(1)
    syndrome = CSSSyndrome(
        x_checks=counts_to_syndrome(
            x_counts,
            check_count=code.hx.shape[0],
        ),
        z_checks=counts_to_syndrome(
            z_counts,
            check_count=code.hz.shape[0],
        ),
    )
    return QiskitSyndromeResult(
        circuits=circuits,
        syndrome=syndrome,
        x_check_counts=x_counts,
        z_check_counts=z_counts,
    )
