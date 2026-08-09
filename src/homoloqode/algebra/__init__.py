"""Exact linear algebra over the binary field."""

from homoloqode.algebra.gf2 import (
    as_binary_matrix,
    as_binary_vector,
    inverse,
    matmul,
    null_space_basis,
    quotient_basis,
    rank,
    row_space_basis,
    rref,
)

__all__ = [
    "as_binary_matrix",
    "as_binary_vector",
    "inverse",
    "matmul",
    "null_space_basis",
    "quotient_basis",
    "rank",
    "row_space_basis",
    "rref",
]

