import numpy as np
import pytest

from homoloqode import CSSCode, toric_code
from homoloqode.codes import CSSSyndrome
from homoloqode.decoders import (
    DecodingFailure,
    ResidualClass,
    classify_residual,
    decode_syndrome,
)


def _xor(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return np.asarray(left ^ right, dtype=np.uint8)


def test_zero_syndrome_returns_zero_corrections() -> None:
    code = toric_code(3)
    result = decode_syndrome(code, code.syndrome())

    assert result.x_correction.weight == 0
    assert result.z_correction.weight == 0
    assert not np.any(result.x_correction.support)
    assert not np.any(result.z_correction.support)


def test_correction_result_is_immutable_and_owns_its_weight() -> None:
    code = toric_code(2)
    x_error = np.zeros(code.n, dtype=np.uint8)
    x_error[0] = 1
    result = decode_syndrome(code, code.syndrome(x_error=x_error))

    assert result.x_correction.weight == 1
    assert not result.x_correction.support.flags.writeable
    with pytest.raises(ValueError, match="read-only"):
        result.x_correction.support[0] = 0


@pytest.mark.parametrize("pauli", ["X", "Y", "Z"])
def test_every_single_qubit_error_on_size_three_torus_succeeds(pauli: str) -> None:
    code = toric_code(3)

    for qubit in range(code.n):
        x_error = np.zeros(code.n, dtype=np.uint8)
        z_error = np.zeros(code.n, dtype=np.uint8)
        if pauli in {"X", "Y"}:
            x_error[qubit] = 1
        if pauli in {"Y", "Z"}:
            z_error[qubit] = 1

        syndrome = code.syndrome(x_error=x_error, z_error=z_error)
        result = decode_syndrome(code, syndrome)

        reproduced = code.syndrome(
            x_error=result.x_correction.support,
            z_error=result.z_correction.support,
        )
        assert np.array_equal(reproduced.x_checks, syndrome.x_checks)
        assert np.array_equal(reproduced.z_checks, syndrome.z_checks)
        assert (
            classify_residual(
                code,
                x_residual=_xor(x_error, result.x_correction.support),
                z_residual=_xor(z_error, result.z_correction.support),
            )
            is ResidualClass.STABILIZER
        )


def test_equal_weight_tie_uses_qubit_index_order() -> None:
    code = CSSCode(
        hx=np.zeros((0, 2), dtype=np.uint8),
        hz=np.array([[1, 1]], dtype=np.uint8),
    )
    syndrome = CSSSyndrome(x_checks=[], z_checks=[1])

    result = decode_syndrome(code, syndrome)

    assert np.array_equal(result.x_correction.support, [1, 0])


def test_dependent_syndrome_bits_are_accepted() -> None:
    code = CSSCode(
        hx=np.array([[1, 0], [1, 0]], dtype=np.uint8),
        hz=np.zeros((0, 2), dtype=np.uint8),
    )
    result = decode_syndrome(
        code,
        CSSSyndrome(x_checks=[1, 1], z_checks=[]),
    )

    assert np.array_equal(result.z_correction.support, [1, 0])


def test_identity_residual_is_a_stabilizer() -> None:
    code = toric_code(3)
    zero = np.zeros(code.n, dtype=np.uint8)

    assert (
        classify_residual(code, x_residual=zero, z_residual=zero)
        is ResidualClass.STABILIZER
    )


@pytest.mark.parametrize("component", ["x", "z"])
def test_nonzero_stabilizer_residual_is_a_success(component: str) -> None:
    code = toric_code(3)
    zero = np.zeros(code.n, dtype=np.uint8)
    x_residual = code.hx[0] if component == "x" else zero
    z_residual = code.hz[0] if component == "z" else zero

    assert (
        classify_residual(
            code,
            x_residual=x_residual,
            z_residual=z_residual,
        )
        is ResidualClass.STABILIZER
    )


@pytest.mark.parametrize("component", ["x", "z"])
def test_noncontractible_logical_residual_is_logical(component: str) -> None:
    code = toric_code(3)
    logicals = code.logical_basis()
    zero = np.zeros(code.n, dtype=np.uint8)
    x_residual = logicals.x[0] if component == "x" else zero
    z_residual = logicals.z[0] if component == "z" else zero

    assert (
        classify_residual(
            code,
            x_residual=x_residual,
            z_residual=z_residual,
        )
        is ResidualClass.LOGICAL
    )


def test_nonzero_syndrome_residual_is_invalid() -> None:
    code = toric_code(3)
    x_residual = np.zeros(code.n, dtype=np.uint8)
    x_residual[0] = 1

    assert (
        classify_residual(
            code,
            x_residual=x_residual,
            z_residual=np.zeros(code.n, dtype=np.uint8),
        )
        is ResidualClass.INVALID
    )


@pytest.mark.parametrize("family", ["x", "z"])
def test_incorrect_syndrome_length_is_rejected(family: str) -> None:
    code = toric_code(2)
    x_checks = [0] * code.hx.shape[0]
    z_checks = [0] * code.hz.shape[0]
    if family == "x":
        x_checks.pop()
    else:
        z_checks.pop()

    with pytest.raises(ValueError, match=f"{family.upper()}-check syndrome length"):
        decode_syndrome(code, CSSSyndrome(x_checks=x_checks, z_checks=z_checks))


@pytest.mark.parametrize("max_weight", [0, -1, True, 1.5])
def test_invalid_max_weight_is_rejected(max_weight: object) -> None:
    code = toric_code(2)
    with pytest.raises(ValueError, match="max_weight must be a positive integer"):
        decode_syndrome(
            code,
            code.syndrome(),
            max_weight=max_weight,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("max_qubits", [0, -1, True, 1.5])
def test_invalid_max_qubits_is_rejected(max_qubits: object) -> None:
    code = toric_code(2)
    with pytest.raises(ValueError, match="max_qubits must be a positive integer"):
        decode_syndrome(
            code,
            code.syndrome(),
            max_qubits=max_qubits,  # type: ignore[arg-type]
        )


def test_code_larger_than_max_qubits_is_rejected() -> None:
    code = toric_code(3)
    with pytest.raises(ValueError, match="exponential-search guard"):
        decode_syndrome(code, code.syndrome(), max_qubits=17)


def test_search_bound_too_small_raises_decoding_failure() -> None:
    code = CSSCode(
        hx=np.eye(2, dtype=np.uint8),
        hz=np.zeros((0, 2), dtype=np.uint8),
    )
    syndrome = CSSSyndrome(x_checks=[1, 1], z_checks=[])

    with pytest.raises(DecodingFailure, match="max_weight=1"):
        decode_syndrome(code, syndrome, max_weight=1)


def test_unreachable_dependent_syndrome_raises_decoding_failure() -> None:
    code = CSSCode(
        hx=np.array([[1, 0], [1, 0]], dtype=np.uint8),
        hz=np.zeros((0, 2), dtype=np.uint8),
    )

    with pytest.raises(DecodingFailure, match="requested syndrome"):
        decode_syndrome(
            code,
            CSSSyndrome(x_checks=[1, 0], z_checks=[]),
        )


def test_residual_support_validation() -> None:
    code = toric_code(2)
    with pytest.raises(ValueError, match="length n=8"):
        classify_residual(code, x_residual=[0], z_residual=[0] * code.n)
    with pytest.raises(ValueError, match="only 0 and 1"):
        classify_residual(
            code,
            x_residual=[2] * code.n,
            z_residual=[0] * code.n,
        )
