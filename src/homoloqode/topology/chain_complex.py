"""Three-term chain complexes over the binary field."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike

from homoloqode.algebra.gf2 import (
    BinaryArray,
    as_binary_matrix,
    matmul,
    rank,
)


def _basis_labels(
    labels: tuple[str, ...] | None, *, size: int, prefix: str
) -> tuple[str, ...]:
    result = (
        tuple(f"{prefix}{index}" for index in range(size))
        if labels is None
        else tuple(labels)
    )
    if len(result) != size:
        raise ValueError(f"Expected {size} labels for {prefix}; got {len(result)}.")
    if len(result) != len(set(result)):
        raise ValueError(f"Basis labels for {prefix} must be unique.")
    if any(not isinstance(label, str) or not label for label in result):
        raise ValueError(f"Basis labels for {prefix} must be non-empty strings.")
    return result


@dataclass(frozen=True, slots=True)
class ChainComplex2D:
    """A binary chain complex ``C2 --d2--> C1 --d1--> C0``."""

    d1: ArrayLike
    d2: ArrayLike
    c0_labels: tuple[str, ...] | None = None
    c1_labels: tuple[str, ...] | None = None
    c2_labels: tuple[str, ...] | None = None

    def __post_init__(self) -> None:
        d1 = as_binary_matrix(self.d1, name="d1")
        d2 = as_binary_matrix(self.d2, name="d2")
        if d1.shape[1] != d2.shape[0]:
            raise ValueError(
                "Boundary dimensions are incompatible: "
                f"d1 has shape {d1.shape}, d2 has shape {d2.shape}."
            )

        composition = matmul(d1, d2)
        if np.any(composition):
            witnesses = np.argwhere(composition)
            first = tuple(int(value) for value in witnesses[0])
            raise ValueError(
                "The chain condition d1 @ d2 = 0 over F_2 is violated; "
                f"first nonzero entry is {first}."
            )

        object.__setattr__(self, "d1", d1)
        object.__setattr__(self, "d2", d2)
        object.__setattr__(
            self,
            "c0_labels",
            _basis_labels(self.c0_labels, size=d1.shape[0], prefix="v"),
        )
        object.__setattr__(
            self,
            "c1_labels",
            _basis_labels(self.c1_labels, size=d1.shape[1], prefix="e"),
        )
        object.__setattr__(
            self,
            "c2_labels",
            _basis_labels(self.c2_labels, size=d2.shape[1], prefix="f"),
        )

    @property
    def delta0(self) -> BinaryArray:
        """Coboundary ``C^0 -> C^1``, equal to ``d1.T``."""

        return as_binary_matrix(self.d1.T, name="delta0")

    @property
    def delta1(self) -> BinaryArray:
        """Coboundary ``C^1 -> C^2``, equal to ``d2.T``."""

        return as_binary_matrix(self.d2.T, name="delta1")

    @property
    def betti_1(self) -> int:
        """Dimension of ``H_1`` over the binary field."""

        return self.d1.shape[1] - rank(self.d1) - rank(self.d2)

    def to_css_code(self) -> "CSSCode":
        """Construct the homological CSS code with qubits on ``C1``."""

        from homoloqode.codes import CSSCode

        return CSSCode(
            hx=self.d1,
            hz=self.d2.T,
            qubit_labels=self.c1_labels,
            x_check_labels=self.c0_labels,
            z_check_labels=self.c2_labels,
        )

