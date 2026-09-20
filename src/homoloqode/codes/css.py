"""Binary CSS codes, syndromes, stabilizers, and logical Pauli bases."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike

from homoloqode.algebra.gf2 import (
    BinaryArray,
    as_binary_matrix,
    as_binary_vector,
    inverse,
    matmul,
    null_space_basis,
    quotient_basis,
    rank,
    row_space_basis,
)


def _labels(
    supplied: tuple[str, ...] | None, *, size: int, prefix: str
) -> tuple[str, ...]:
    result = (
        tuple(f"{prefix}{index}" for index in range(size))
        if supplied is None
        else tuple(supplied)
    )
    if len(result) != size:
        raise ValueError(f"Expected {size} {prefix} labels; got {len(result)}.")
    if len(result) != len(set(result)):
        raise ValueError(f"{prefix} labels must be unique.")
    if any(not isinstance(label, str) or not label for label in result):
        raise ValueError(f"{prefix} labels must be non-empty strings.")
    return result


@dataclass(frozen=True, slots=True)
class CSSSyndrome:
    """Immutable syndrome vectors in the code's check-row order.

    ``x_checks[i]`` is the outcome for ``CSSCode.hx[i]`` and detects the Z
    component of an error. ``z_checks[i]`` is the outcome for
    ``CSSCode.hz[i]`` and detects the X component.
    """

    x_checks: ArrayLike
    z_checks: ArrayLike

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "x_checks",
            as_binary_vector(self.x_checks, name="X-check syndrome"),
        )
        object.__setattr__(
            self,
            "z_checks",
            as_binary_vector(self.z_checks, name="Z-check syndrome"),
        )


@dataclass(frozen=True, slots=True)
class LogicalBasis:
    """Paired logical operators represented by binary ``(k, n)`` matrices.

    Columns use the parent code's qubit order. Row ``i`` of ``x`` is paired
    with row ``i`` of ``z`` so that ``x @ z.T`` is the identity over
    :math:`\\mathbb F_2`.
    """

    x: ArrayLike
    z: ArrayLike

    def __post_init__(self) -> None:
        x = as_binary_matrix(self.x, name="logical X basis")
        z = as_binary_matrix(self.z, name="logical Z basis")
        if x.shape != z.shape:
            raise ValueError(
                f"Logical X and Z bases must have equal shapes; got {x.shape} "
                f"and {z.shape}."
            )
        pairing = matmul(x, z.T)
        expected = np.eye(x.shape[0], dtype=np.uint8)
        if not np.array_equal(pairing, expected):
            raise ValueError("Logical bases must satisfy X @ Z.T = I over F_2.")
        object.__setattr__(self, "x", x)
        object.__setattr__(self, "z", z)

    @property
    def count(self) -> int:
        return self.x.shape[0]


@dataclass(frozen=True, slots=True)
class CSSCode:
    """An immutable CSS code with explicit qubit and check ordering.

    Columns of ``hx`` and ``hz`` follow ``qubit_labels``. Rows of ``hx``
    follow ``x_check_labels`` and rows of ``hz`` follow ``z_check_labels``.
    All stored arrays are validated binary, read-only copies.
    """

    hx: ArrayLike
    hz: ArrayLike
    qubit_labels: tuple[str, ...] | None = None
    x_check_labels: tuple[str, ...] | None = None
    z_check_labels: tuple[str, ...] | None = None

    def __post_init__(self) -> None:
        hx = as_binary_matrix(self.hx, name="H_X")
        hz = as_binary_matrix(self.hz, name="H_Z")
        if hx.shape[1] != hz.shape[1]:
            raise ValueError(
                "H_X and H_Z must have the same number of columns; "
                f"got {hx.shape} and {hz.shape}."
            )

        commutator = matmul(hx, hz.T)
        if np.any(commutator):
            first = tuple(int(value) for value in np.argwhere(commutator)[0])
            raise ValueError(
                "CSS commutation H_X @ H_Z.T = 0 is violated; "
                f"first nonzero entry is {first}."
            )

        object.__setattr__(self, "hx", hx)
        object.__setattr__(self, "hz", hz)
        object.__setattr__(
            self,
            "qubit_labels",
            _labels(self.qubit_labels, size=hx.shape[1], prefix="q"),
        )
        object.__setattr__(
            self,
            "x_check_labels",
            _labels(self.x_check_labels, size=hx.shape[0], prefix="x"),
        )
        object.__setattr__(
            self,
            "z_check_labels",
            _labels(self.z_check_labels, size=hz.shape[0], prefix="z"),
        )

    @property
    def n(self) -> int:
        return self.hx.shape[1]

    @property
    def rank_x(self) -> int:
        return rank(self.hx)

    @property
    def rank_z(self) -> int:
        return rank(self.hz)

    @property
    def k(self) -> int:
        return self.n - self.rank_x - self.rank_z

    def syndrome(
        self,
        *,
        x_error: ArrayLike | None = None,
        z_error: ArrayLike | None = None,
    ) -> CSSSyndrome:
        """Compute syndrome vectors in X-check and Z-check row order.

        A Z error anticommutes with X checks, while an X error anticommutes with
        Z checks. Error-vector positions follow ``qubit_labels``.
        """

        x = (
            np.zeros(self.n, dtype=np.uint8)
            if x_error is None
            else as_binary_vector(x_error, name="X-error support")
        )
        z = (
            np.zeros(self.n, dtype=np.uint8)
            if z_error is None
            else as_binary_vector(z_error, name="Z-error support")
        )
        if x.shape[0] != self.n or z.shape[0] != self.n:
            raise ValueError(f"Error supports must have length n={self.n}.")

        x_syndrome = np.asarray((self.hx @ z) & 1, dtype=np.uint8)
        z_syndrome = np.asarray((self.hz @ x) & 1, dtype=np.uint8)
        return CSSSyndrome(x_checks=x_syndrome, z_checks=z_syndrome)

    def x_stabilizer_strings(self) -> tuple[str, ...]:
        """Return X-type generators as phase-free Pauli strings."""

        return tuple(
            "".join("X" if bit else "I" for bit in row) for row in self.hx
        )

    def z_stabilizer_strings(self) -> tuple[str, ...]:
        """Return Z-type generators as phase-free Pauli strings."""

        return tuple(
            "".join("Z" if bit else "I" for bit in row) for row in self.hz
        )

    def logical_basis(self) -> LogicalBasis:
        """Compute paired logical representatives in ``qubit_labels`` order."""

        z_space = null_space_basis(self.hx)
        z_stabilizers = row_space_basis(self.hz)
        z_logicals = quotient_basis(z_space, z_stabilizers)

        x_space = null_space_basis(self.hz)
        x_stabilizers = row_space_basis(self.hx)
        x_logicals = quotient_basis(x_space, x_stabilizers)

        if x_logicals.shape[0] != self.k or z_logicals.shape[0] != self.k:
            raise RuntimeError("Logical quotient dimensions do not match code k.")

        pairing = matmul(x_logicals, z_logicals.T)
        paired_x = matmul(inverse(pairing), x_logicals)
        return LogicalBasis(x=paired_x, z=z_logicals)
