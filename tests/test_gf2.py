import numpy as np
import pytest

from homoloqode.algebra import (
    as_binary_matrix,
    as_binary_vector,
    inverse,
    is_in_row_span,
    matmul,
    null_space_basis,
    quotient_basis,
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


@pytest.mark.parametrize(
    ("converter", "values", "dimension"),
    [
        (as_binary_matrix, [0, 1], 2),
        (as_binary_vector, [[0, 1]], 1),
    ],
)
def test_binary_converters_reject_wrong_dimensions(
    converter, values: list, dimension: int
) -> None:
    with pytest.raises(ValueError, match=rf"must be {dimension}-dimensional"):
        converter(values)


def test_matmul_rejects_incompatible_dimensions() -> None:
    with pytest.raises(ValueError, match="cannot be multiplied"):
        matmul(np.zeros((2, 3), dtype=np.uint8), np.zeros((2, 1), dtype=np.uint8))


def test_quotient_basis_validates_spaces_and_handles_zero_quotient() -> None:
    with pytest.raises(ValueError, match="same length"):
        quotient_basis([[1, 0]], [[1, 0, 0]])

    with pytest.raises(ValueError, match="not contained"):
        quotient_basis([[1, 0]], [[0, 1]])

    quotient = quotient_basis([[1, 0], [0, 1]], [[1, 0], [0, 1]])
    assert quotient.shape == (0, 2)


def test_inverse_rejects_nonsquare_and_singular_matrices() -> None:
    with pytest.raises(ValueError, match="must be square"):
        inverse([[1, 0, 1], [0, 1, 0]])

    with pytest.raises(ValueError, match="singular"):
        inverse([[1, 1], [1, 1]])


def test_inverse_handles_a_required_row_swap() -> None:
    matrix = np.array([[0, 1], [1, 0]], dtype=np.uint8)

    assert np.array_equal(inverse(matrix), matrix)


def test_row_span_membership_handles_dependent_rows() -> None:
    matrix = np.array(
        [
            [1, 0, 1],
            [0, 1, 1],
            [1, 1, 0],
        ],
        dtype=np.uint8,
    )

    assert is_in_row_span([1, 1, 0], matrix)
    assert not is_in_row_span([0, 0, 1], matrix)


def test_row_span_membership_handles_empty_basis() -> None:
    matrix = np.zeros((0, 3), dtype=np.uint8)

    assert is_in_row_span([0, 0, 0], matrix)
    assert not is_in_row_span([1, 0, 0], matrix)


def test_row_span_membership_rejects_length_mismatch() -> None:
    with pytest.raises(ValueError, match="got 2 and 3"):
        is_in_row_span([1, 0], np.zeros((0, 3), dtype=np.uint8))


@pytest.mark.parametrize(
    ("vector", "matrix"),
    [
        ([2, 0], [[1, 0]]),
        ([1, 0], [[1, 2]]),
    ],
)
def test_row_span_membership_rejects_nonbinary_input(
    vector: list[int], matrix: list[list[int]]
) -> None:
    with pytest.raises(ValueError, match="only 0 and 1"):
        is_in_row_span(vector, matrix)
