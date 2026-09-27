"""Reproducible independent single-qubit Pauli noise."""

from dataclasses import dataclass
import math

import numpy as np
from numpy.typing import ArrayLike

from homoloqode.algebra.gf2 import as_binary_vector


_PAULI_LETTERS = {
    (0, 0): "I",
    (1, 0): "X",
    (1, 1): "Y",
    (0, 1): "Z",
}
_TOLERANCE = 8 * math.ulp(1.0)


@dataclass(frozen=True, slots=True)
class PauliError:
    """An immutable binary Pauli error support on ``n`` qubits.

    ``x`` and ``z`` are equal-length, read-only binary vectors. Position
    ``i`` refers to qubit ``i`` in the consuming :class:`CSSCode` object's
    ``qubit_labels`` order. The symplectic convention is ``(0, 0)=I``,
    ``(1, 0)=X``, ``(1, 1)=Y``, and ``(0, 1)=Z``.
    """

    x: ArrayLike
    z: ArrayLike

    def __post_init__(self) -> None:
        x = as_binary_vector(self.x, name="X-error support")
        z = as_binary_vector(self.z, name="Z-error support")
        if x.shape[0] != z.shape[0]:
            raise ValueError(
                "X and Z error supports must have equal length; "
                f"got {x.shape[0]} and {z.shape[0]}."
            )
        object.__setattr__(self, "x", x)
        object.__setattr__(self, "z", z)

    @property
    def n(self) -> int:
        """Number of qubits represented by the error."""

        return self.x.shape[0]

    @property
    def weight(self) -> int:
        """Number of qubits carrying a nonidentity Pauli."""

        return int(np.count_nonzero((self.x == 1) | (self.z == 1)))

    def to_pauli_string(self) -> str:
        """Return a phase-free Pauli string in qubit-index order."""

        return "".join(
            _PAULI_LETTERS[(int(x_bit), int(z_bit))]
            for x_bit, z_bit in zip(self.x, self.z)
        )


@dataclass(frozen=True, slots=True)
class IndependentPauliNoise:
    """Independent per-qubit I/X/Y/Z Pauli channel.

    Each qubit receives X with probability ``p_x``, Y with probability
    ``p_y``, Z with probability ``p_z``, and I with the remaining probability.
    The channel can be reused across codes and trials because the qubit count
    and random generator are supplied to :meth:`sample`.

    Examples:
        >>> rng = np.random.default_rng(12345)
        >>> noise = IndependentPauliNoise(p_x=0.1, p_y=0.2, p_z=0.3)
        >>> error = noise.sample(5, rng=rng)
        >>> error.n
        5
    """

    p_x: float
    p_y: float
    p_z: float

    def __post_init__(self) -> None:
        for name, probability in (
            ("p_x", self.p_x),
            ("p_y", self.p_y),
            ("p_z", self.p_z),
        ):
            if isinstance(probability, bool):
                raise ValueError(f"{name} must be a real number, not a bool.")
            if not 0 <= probability <= 1:
                raise ValueError(
                    f"{name} must be in [0, 1]; got {probability}."
                )

        total = self.p_x + self.p_y + self.p_z
        if total > 1.0 and not math.isclose(
            total,
            1.0,
            rel_tol=0.0,
            abs_tol=_TOLERANCE,
        ):
            raise ValueError(
                "Sum of X, Y, and Z error probabilities must be at most 1; "
                f"got {total}."
            )

    @property
    def p_identity(self) -> float:
        """Probability of sampling the identity on one qubit."""

        return max(0.0, 1.0 - (self.p_x + self.p_y + self.p_z))

    def sample(self, n: int, *, rng: np.random.Generator) -> PauliError:
        """Draw one error on ``n`` ordered qubits using an explicit RNG.

        The returned vector positions are qubit-index order. The method never
        reads or mutates NumPy's global random state.
        """

        if isinstance(n, bool):
            raise ValueError(f"n must be an integer, not a bool; got {n}.")
        if not isinstance(n, int):
            raise ValueError(f"n must be an integer; got {type(n).__name__}.")
        if n <= 0:
            raise ValueError(f"n must be a positive integer; got {n}.")
        if not isinstance(rng, np.random.Generator):
            raise ValueError("rng must be a numpy.random.Generator.")

        boundary_x = self.p_identity
        boundary_y = boundary_x + self.p_x
        boundary_z = boundary_y + self.p_y
        draws = rng.random(n)

        past_x = draws >= boundary_x
        past_y = draws >= boundary_y
        past_z = draws >= boundary_z

        x_error = (past_x & ~past_z).astype(np.uint8)
        z_error = past_y.astype(np.uint8)
        return PauliError(x=x_error, z=z_error)
