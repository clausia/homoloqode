import numpy as np
import pytest

from homoloqode import CSSCode, toric_code
from homoloqode.algebra import matmul


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

