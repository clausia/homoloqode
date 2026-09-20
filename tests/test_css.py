from dataclasses import FrozenInstanceError

import numpy as np
import pytest

import homoloqode.codes.css as css_module
from homoloqode import CSSCode, toric_code
from homoloqode.algebra import matmul
from homoloqode.codes import LogicalBasis


@pytest.mark.parametrize(
    ("size", "n", "check_rank"),
    [
        (2, 8, 3),
        (3, 18, 8),
    ],
)
def test_toric_code_parameters(size: int, n: int, check_rank: int) -> None:
    code = toric_code(size)

    assert code.n == n
    assert code.k == 2
    assert code.rank_x == check_rank
    assert code.rank_z == check_rank
    assert code.hx.shape == (size * size, n)
    assert code.hz.shape == (size * size, n)
    assert not np.any(matmul(code.hx, code.hz.T))


@pytest.mark.parametrize("size", [2, 3])
def test_logical_basis_is_paired_and_commutes_with_checks(size: int) -> None:
    code = toric_code(size)

    logicals = code.logical_basis()

    assert logicals.x.shape == (2, code.n)
    assert logicals.z.shape == (2, code.n)
    assert np.array_equal(
        matmul(logicals.x, logicals.z.T),
        np.eye(2, dtype=np.uint8),
    )
    assert not np.any(matmul(code.hz, logicals.x.T))
    assert not np.any(matmul(code.hx, logicals.z.T))


def test_single_qubit_errors_have_two_defects_on_size_three_torus() -> None:
    code = toric_code(3)
    error = np.zeros(code.n, dtype=np.uint8)
    error[0] = 1

    z_error_syndrome = code.syndrome(z_error=error)
    x_error_syndrome = code.syndrome(x_error=error)

    assert int(z_error_syndrome.x_checks.sum()) == 2
    assert not np.any(z_error_syndrome.z_checks)
    assert int(x_error_syndrome.z_checks.sum()) == 2
    assert not np.any(x_error_syndrome.x_checks)


def test_geometric_check_rows_are_retained_even_when_dependent() -> None:
    code = toric_code(3)

    assert code.hx.shape[0] == 9
    assert code.rank_x == 8
    assert code.hz.shape[0] == 9
    assert code.rank_z == 8


def test_noncommuting_css_checks_are_rejected() -> None:
    with pytest.raises(ValueError, match="CSS commutation"):
        CSSCode(hx=np.array([[1]], dtype=np.uint8), hz=np.array([[1]], dtype=np.uint8))


def test_css_check_matrices_must_have_equal_widths() -> None:
    with pytest.raises(ValueError, match="same number of columns"):
        CSSCode(
            hx=np.zeros((1, 2), dtype=np.uint8),
            hz=np.zeros((1, 3), dtype=np.uint8),
        )


@pytest.mark.parametrize(
    ("labels", "message"),
    [
        (("q0",), "Expected 2 q labels"),
        (("q", "q"), "q labels must be unique"),
        (("q", ""), "q labels must be non-empty strings"),
        (("q", 1), "q labels must be non-empty strings"),
    ],
)
def test_css_labels_are_validated(labels: tuple[object, ...], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        CSSCode(
            hx=np.zeros((0, 2), dtype=np.uint8),
            hz=np.zeros((0, 2), dtype=np.uint8),
            qubit_labels=labels,  # type: ignore[arg-type]
        )


def test_logical_basis_validates_shape_and_pairing() -> None:
    with pytest.raises(ValueError, match="equal shapes"):
        LogicalBasis(x=[[1, 0]], z=[[1, 0], [0, 1]])

    with pytest.raises(ValueError, match="X @ Z.T = I"):
        LogicalBasis(x=[[1, 0]], z=[[0, 1]])


def test_logical_basis_count_and_immutability() -> None:
    logicals = toric_code(2).logical_basis()

    assert logicals.count == 2
    with pytest.raises(FrozenInstanceError):
        logicals.x = np.zeros_like(logicals.x)  # type: ignore[misc]
    with pytest.raises(ValueError, match="read-only"):
        logicals.x[0, 0] ^= 1


def test_syndrome_rejects_wrong_error_length() -> None:
    with pytest.raises(ValueError, match="length n=8"):
        toric_code(2).syndrome(x_error=[1, 0])


def test_stabilizer_strings_follow_check_row_order() -> None:
    code = CSSCode(
        hx=[[1, 0, 1]],
        hz=[[0, 1, 0]],
        qubit_labels=("a", "b", "c"),
    )

    assert code.x_stabilizer_strings() == ("XIX",)
    assert code.z_stabilizer_strings() == ("IZI",)


def test_logical_basis_detects_an_internal_dimension_mismatch(monkeypatch) -> None:
    code = toric_code(2)
    real_quotient_basis = css_module.quotient_basis
    calls = 0

    def wrong_quotient_basis(space_basis, subspace_basis):
        nonlocal calls
        calls += 1
        if calls == 1:
            return np.zeros((0, code.n), dtype=np.uint8)
        return real_quotient_basis(space_basis, subspace_basis)

    monkeypatch.setattr(css_module, "quotient_basis", wrong_quotient_basis)
    with pytest.raises(RuntimeError, match="dimensions do not match"):
        code.logical_basis()
