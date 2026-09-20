import numpy as np
import pytest

from homoloqode import toric_code
from homoloqode.integrations import (
    build_syndrome_circuits,
    counts_to_syndrome,
    simulate_syndrome,
)


def test_counts_are_converted_to_check_row_order() -> None:
    syndrome = counts_to_syndrome({"1010": 16}, check_count=4)

    assert np.array_equal(syndrome, np.array([0, 1, 0, 1], dtype=np.uint8))


def test_syndrome_circuits_reuse_one_ancilla() -> None:
    code = toric_code(2)

    circuits = build_syndrome_circuits(code)

    assert circuits.x_checks.num_qubits == code.n + 1
    assert circuits.z_checks.num_qubits == code.n + 1
    assert circuits.x_checks.num_clbits == code.hx.shape[0]
    assert circuits.z_checks.num_clbits == code.hz.shape[0]


@pytest.mark.parametrize(
    ("x_indices", "z_indices"),
    [
        ((), ()),
        ((0,), (1,)),
        ((0, 3), (0, 5)),
    ],
)
def test_qiskit_and_algebraic_syndromes_agree(
    x_indices: tuple[int, ...],
    z_indices: tuple[int, ...],
) -> None:
    code = toric_code(2)
    x_error = np.zeros(code.n, dtype=np.uint8)
    z_error = np.zeros(code.n, dtype=np.uint8)
    x_error[list(x_indices)] = 1
    z_error[list(z_indices)] = 1

    algebraic = code.syndrome(x_error=x_error, z_error=z_error)
    qiskit_result = simulate_syndrome(
        code,
        x_error=x_error,
        z_error=z_error,
        shots=4,
    )

    assert np.array_equal(qiskit_result.syndrome.x_checks, algebraic.x_checks)
    assert np.array_equal(qiskit_result.syndrome.z_checks, algebraic.z_checks)


def test_invalid_counts_are_rejected() -> None:
    with pytest.raises(ValueError, match="nonnegative"):
        counts_to_syndrome({"0": 1}, check_count=-1)

    with pytest.raises(ValueError, match="cannot be empty"):
        counts_to_syndrome({}, check_count=0)

    with pytest.raises(ValueError, match="Expected 3 syndrome bits"):
        counts_to_syndrome({"00": 1}, check_count=3)

    with pytest.raises(ValueError, match="Unsupported Qiskit count key"):
        counts_to_syndrome({"0x1": 1}, check_count=3)


@pytest.mark.parametrize("shots", [0, -1, True, 1.5])
def test_invalid_error_length_and_shot_count_are_rejected(shots: object) -> None:
    code = toric_code(2)

    with pytest.raises(ValueError, match="must have length"):
        build_syndrome_circuits(code, x_error=[1, 0])

    with pytest.raises(ValueError, match="shots must be a positive integer"):
        simulate_syndrome(code, shots=shots)  # type: ignore[arg-type]


def test_count_keys_with_register_separators_are_supported() -> None:
    syndrome = counts_to_syndrome({"10 01": 4}, check_count=4)

    assert np.array_equal(syndrome, np.array([1, 0, 0, 1], dtype=np.uint8))
