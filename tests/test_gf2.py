import numpy as np
import pytest

from homoloqode.algebra import (
    inverse,
    matmul,
    null_space_basis,
    rank,
    row_space_basis,
)


def test_rank_is_computed_over_binary_field() -> None:
    matrix = np.array(
        [
            [1, 1, 0],
            [1, 0, 1],
            [0, 1, 1],
        ],
        dtype=np.uint8,
    )

    assert np.linalg.matrix_rank(matrix) == 3
    assert rank(matrix) == 2


def test_null_space_basis_satisfies_matrix_equations() -> None:
    matrix = np.array(
        [
            [1, 1, 0, 0],
            [0, 1, 1, 0],
        ],
        dtype=np.uint8,
    )

    kernel = null_space_basis(matrix)

    assert kernel.shape == (2, 4)
    assert not np.any(matmul(matrix, kernel.T))


def test_row_space_basis_discards_dependent_rows() -> None:
    matrix = np.array(
        [
            [1, 0, 1],
            [0, 1, 1],
            [1, 1, 0],
        ],
        dtype=np.uint8,
    )

    basis = row_space_basis(matrix)

    assert basis.shape == (2, 3)
    assert rank(basis) == 2


def test_inverse_is_exact_over_binary_field() -> None:
    matrix = np.array([[1, 1], [1, 0]], dtype=np.uint8)

    result = inverse(matrix)

    assert np.array_equal(matmul(matrix, result), np.eye(2, dtype=np.uint8))


def test_nonbinary_input_is_rejected() -> None:
    with pytest.raises(ValueError, match="only 0 and 1"):
        rank([[1, 2]])
