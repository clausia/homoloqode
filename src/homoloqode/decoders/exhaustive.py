"""Deterministic exhaustive decoding for small CSS codes.

The decoder enumerates correction supports in increasing Hamming weight and
then in qubit-index lexicographic order.  It is a correctness reference for
small examples, not a scalable decoder.  A returned correction can differ
from the physical error because several errors may have the same syndrome.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from itertools import combinations

import numpy as np
from numpy.typing import ArrayLike

from homoloqode.algebra.gf2 import (
    BinaryArray,
    as_binary_vector,
    is_in_row_span,
    matmul,
)
from homoloqode.codes.css import CSSCode, CSSSyndrome


class DecodingFailure(RuntimeError):
    """Raised when no correction exists within the configured search bound."""


@dataclass(frozen=True, slots=True)
class BinaryCorrection:
    """An immutable binary correction support and its Hamming weight."""

    support: BinaryArray
    weight: int = field(init=False)

    def __post_init__(self) -> None:
        support = as_binary_vector(self.support, name="correction support")
        object.__setattr__(self, "support", support)
        object.__setattr__(self, "weight", int(np.count_nonzero(support)))


@dataclass(frozen=True, slots=True)
class CSSDecodeResult:
    """Minimum-weight X and Z corrections for a CSS syndrome.

    ``x_correction`` reproduces the Z-check syndrome through ``H_Z``;
    ``z_correction`` reproduces the X-check syndrome through ``H_X``.
    """

    x_correction: BinaryCorrection
    z_correction: BinaryCorrection


class ResidualClass(Enum):
    """Classification of a physical error plus its proposed correction."""

    STABILIZER = "stabilizer"
    LOGICAL = "logical"
    INVALID = "invalid"


def _positive_integer(value: object, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer; got {value!r}.")
    return value


def _find_correction(
    checks: BinaryArray,
    target: BinaryArray,
    *,
    n: int,
    max_weight: int,
    component: str,
) -> BinaryCorrection:
    zero = np.zeros(n, dtype=np.uint8)
    if not np.any(target):
        return BinaryCorrection(zero)

    for weight in range(1, min(max_weight, n) + 1):
        for qubits in combinations(range(n), weight):
            candidate = np.zeros(n, dtype=np.uint8)
            candidate[list(qubits)] = 1
            computed = matmul(checks, candidate.reshape(-1, 1)).reshape(-1)
            if np.array_equal(computed, target):
                return BinaryCorrection(candidate)

    raise DecodingFailure(
        f"No {component} correction reproduces the requested syndrome "
        f"within max_weight={max_weight}."
    )


def decode_syndrome(
    code: CSSCode,
    syndrome: CSSSyndrome,
    *,
    max_weight: int | None = None,
    max_qubits: int = 24,
) -> CSSDecodeResult:
    """Return deterministic minimum-weight corrections for ``syndrome``.

    X- and Z-error components are decoded independently over
    :math:`\\mathbb F_2`.  Exhaustive enumeration makes runtime exponential in
    ``code.n``; ``max_qubits`` and ``max_weight`` bound that work.  Degenerate
    equal-weight corrections are resolved by qubit-index lexicographic order.

    Raises:
        ValueError: If a bound or syndrome length is invalid.
        DecodingFailure: If no correction is found within ``max_weight``.
    """

    qubit_limit = _positive_integer(max_qubits, name="max_qubits")
    if code.n > qubit_limit:
        raise ValueError(
            f"code.n={code.n} exceeds the exponential-search guard "
            f"max_qubits={qubit_limit}."
        )
    weight_limit = (
        code.n
        if max_weight is None
        else _positive_integer(max_weight, name="max_weight")
    )

    if syndrome.x_checks.shape[0] != code.hx.shape[0]:
        raise ValueError(
            "X-check syndrome length must match the number of X checks; "
            f"got {syndrome.x_checks.shape[0]} and {code.hx.shape[0]}."
        )
    if syndrome.z_checks.shape[0] != code.hz.shape[0]:
        raise ValueError(
            "Z-check syndrome length must match the number of Z checks; "
            f"got {syndrome.z_checks.shape[0]} and {code.hz.shape[0]}."
        )

    x_correction = _find_correction(
        code.hz,
        syndrome.z_checks,
        n=code.n,
        max_weight=weight_limit,
        component="X",
    )
    z_correction = _find_correction(
        code.hx,
        syndrome.x_checks,
        n=code.n,
        max_weight=weight_limit,
        component="Z",
    )
    return CSSDecodeResult(
        x_correction=x_correction,
        z_correction=z_correction,
    )


def classify_residual(
    code: CSSCode,
    *,
    x_residual: ArrayLike,
    z_residual: ArrayLike,
) -> ResidualClass:
    """Classify a residual Pauli as stabilizer, logical, or invalid.

    A zero-syndrome residual is a stabilizer exactly when its X support belongs
    to ``row(H_X)`` and its Z support belongs to ``row(H_Z)``.  Otherwise it is
    a nontrivial logical Pauli.  A residual with nonzero syndrome is invalid.
    """

    x = as_binary_vector(x_residual, name="X residual support")
    z = as_binary_vector(z_residual, name="Z residual support")
    if x.shape[0] != code.n or z.shape[0] != code.n:
        raise ValueError(f"Residual supports must both have length n={code.n}.")

    syndrome = code.syndrome(x_error=x, z_error=z)
    if np.any(syndrome.x_checks) or np.any(syndrome.z_checks):
        return ResidualClass.INVALID
    if is_in_row_span(x, code.hx) and is_in_row_span(z, code.hz):
        return ResidualClass.STABILIZER
    return ResidualClass.LOGICAL
