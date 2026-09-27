"""Small, exact linear-algebra routines over :math:`\\mathbb F_2`."""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray

BinaryArray = NDArray[np.uint8]


def _validated_array(values: ArrayLike, *, ndim: int, name: str) -> BinaryArray:
    array = np.asarray(values)
    if array.ndim != ndim:
        raise ValueError(f"{name} must be {ndim}-dimensional; got shape {array.shape}.")
    if not np.all((array == 0) | (array == 1)):
        raise ValueError(f"{name} must contain only 0 and 1.")
    return np.array(array, dtype=np.uint8, copy=True)


def _freeze(array: BinaryArray) -> BinaryArray:
    array.setflags(write=False)
    return array


def as_binary_matrix(values: ArrayLike, *, name: str = "matrix") -> BinaryArray:
    """Return a validated, read-only binary matrix."""

    return _freeze(_validated_array(values, ndim=2, name=name))


def as_binary_vector(values: ArrayLike, *, name: str = "vector") -> BinaryArray:
    """Return a validated, read-only binary vector."""

    return _freeze(_validated_array(values, ndim=1, name=name))


def matmul(left: ArrayLike, right: ArrayLike) -> BinaryArray:
    """Multiply two matrices over :math:`\\mathbb F_2`."""

    a = _validated_array(left, ndim=2, name="left matrix")
    b = _validated_array(right, ndim=2, name="right matrix")
    if a.shape[1] != b.shape[0]:
        raise ValueError(
            "Incompatible binary matrix dimensions: "
            f"{a.shape} cannot be multiplied by {b.shape}."
        )
    return _freeze(np.asarray((a @ b) & 1, dtype=np.uint8))


def rref(matrix: ArrayLike) -> tuple[BinaryArray, tuple[int, ...]]:
    """Return reduced row-echelon form and pivot columns over the binary field."""

    reduced = _validated_array(matrix, ndim=2, name="matrix")
    row_count, column_count = reduced.shape
    pivot_row = 0
    pivots: list[int] = []

    for column in range(column_count):
        candidates = np.flatnonzero(reduced[pivot_row:, column])
        if candidates.size == 0:
            continue

        selected = pivot_row + int(candidates[0])
        if selected != pivot_row:
            reduced[[pivot_row, selected]] = reduced[[selected, pivot_row]]

        for row in range(row_count):
            if row != pivot_row and reduced[row, column]:
                reduced[row] ^= reduced[pivot_row]

        pivots.append(column)
        pivot_row += 1
        if pivot_row == row_count:
            break

    return _freeze(reduced), tuple(pivots)


def rank(matrix: ArrayLike) -> int:
    """Compute matrix rank over :math:`\\mathbb F_2`."""

    _, pivots = rref(matrix)
    return len(pivots)


def row_space_basis(matrix: ArrayLike) -> BinaryArray:
    """Return independent rows spanning the input row space."""

    reduced, _ = rref(matrix)
    nonzero = np.any(reduced, axis=1)
    return as_binary_matrix(reduced[nonzero], name="row-space basis")


def null_space_basis(matrix: ArrayLike) -> BinaryArray:
    """Return row vectors forming a basis of the right null space."""

    reduced, pivots = rref(matrix)
    column_count = reduced.shape[1]
    pivot_set = set(pivots)
    free_columns = [column for column in range(column_count) if column not in pivot_set]
    basis = np.zeros((len(free_columns), column_count), dtype=np.uint8)

    for basis_row, free_column in enumerate(free_columns):
        basis[basis_row, free_column] = 1
        for pivot_row, pivot_column in enumerate(pivots):
            basis[basis_row, pivot_column] = reduced[pivot_row, free_column]

    return as_binary_matrix(basis, name="null-space basis")


def quotient_basis(space_basis: ArrayLike, subspace_basis: ArrayLike) -> BinaryArray:
    """Choose representatives for ``space / subspace``.

    Both inputs contain basis candidates as rows. The subspace must be contained
    in the larger space.
    """

    space = _validated_array(space_basis, ndim=2, name="space basis")
    subspace = _validated_array(subspace_basis, ndim=2, name="subspace basis")
    if space.shape[1] != subspace.shape[1]:
        raise ValueError("Space and subspace vectors must have the same length.")

    current = row_space_basis(subspace)
    current_rank = current.shape[0]

    combined = np.vstack((current, space))
    if rank(combined) != rank(space):
        raise ValueError("The supplied subspace is not contained in the space.")

    representatives: list[BinaryArray] = []
    for vector in space:
        candidate = np.vstack((current, vector))
        candidate_rank = rank(candidate)
        if candidate_rank > current_rank:
            representatives.append(vector.copy())
            current = candidate
            current_rank = candidate_rank

    if representatives:
        result = np.vstack(representatives)
    else:
        result = np.zeros((0, space.shape[1]), dtype=np.uint8)
    return as_binary_matrix(result, name="quotient basis")


def inverse(matrix: ArrayLike) -> BinaryArray:
    """Return the inverse of a square binary matrix."""

    square = _validated_array(matrix, ndim=2, name="matrix")
    row_count, column_count = square.shape
    if row_count != column_count:
        raise ValueError(f"Matrix must be square; got shape {square.shape}.")

    augmented = np.hstack((square, np.eye(row_count, dtype=np.uint8)))
    pivot_row = 0
    for column in range(column_count):
        candidates = np.flatnonzero(augmented[pivot_row:, column])
        if candidates.size == 0:
            raise ValueError("Matrix is singular over F_2.")

        selected = pivot_row + int(candidates[0])
        if selected != pivot_row:
            augmented[[pivot_row, selected]] = augmented[[selected, pivot_row]]

        for row in range(row_count):
            if row != pivot_row and augmented[row, column]:
                augmented[row] ^= augmented[pivot_row]
        pivot_row += 1

    return as_binary_matrix(augmented[:, column_count:], name="inverse")


def is_in_row_span(vector: ArrayLike, matrix: ArrayLike) -> bool:
    """Return whether a binary vector belongs to a matrix's row space."""

    candidate = as_binary_vector(vector, name="vector")
    rows = as_binary_matrix(matrix, name="matrix")
    if candidate.shape[0] != rows.shape[1]:
        raise ValueError(
            "Vector length must match matrix column count; "
            f"got {candidate.shape[0]} and {rows.shape[1]}."
        )
    return rank(np.vstack((rows, candidate))) == rank(rows)
