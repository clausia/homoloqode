"""Exact, exponential-time (on purpose) distance search for small CSS codes.

Enumerates candidate logical-operator supports in increasing Hamming weight,
using itertools.combinations, until one is found that commutes with the
opposite-type check matrix and is not itself a stabilizer. Intended only for
small examples (see max_qubits); not a scalable distance estimator.
"""

from dataclasses import dataclass
from itertools import combinations
import numpy as np
from homoloqode.codes.css import CSSCode
from homoloqode.algebra.gf2 import as_binary_vector, is_in_row_span, matmul


class IncompleteSearchError(ValueError):
    """Raised when a distance search did not find a logical operator within
    max_weight, and max_weight was set below code.n : so absence is not
    confirmed, only "not found within the searched range"."""


@dataclass(frozen=True, slots=True)
class CSSDistance:
    """Exact X, Z, and overall distance of a CSS code, or None where not
    determined (see exact_distance_x/exact_distance_z/exact_distance)."""

    d_x: int | None
    d_z: int | None
    d: int | None


def _validate_max_weight(max_weight: int | None) -> None:
    """Raise ValueError unless max_weight is None or a nonnegative int or a bool (true/false read as 0/1)."""
    if max_weight is not None and isinstance(max_weight, bool):
        raise ValueError("max_weight must be an integer, not a bool.")
    if max_weight is not None and not isinstance(max_weight, int):
        raise ValueError(f"max_weight must be an integer, got {type(max_weight).__name__}.")
    if max_weight is not None and max_weight < 0:
        raise ValueError(f"max_weight must be non-negative, got {max_weight}.")


def _validate_max_qubits(code: CSSCode, max_qubits: int) -> None:
    """Raise ValueError unless max_qubits is a nonnegative int and code.n
    does not exceed it."""
    if isinstance(max_qubits, bool):
        raise ValueError("max_qubits must be an integer, not a bool.")
    if not isinstance(max_qubits, int):
        raise ValueError(f"max_qubits must be an integer, got {type(max_qubits).__name__}.")
    if max_qubits < 0:
        raise ValueError(f"max_qubits must be non-negative, got {max_qubits}.")
    if code.n > max_qubits:
        raise ValueError(f"code.n={code.n} exceeds max_qubits={max_qubits}.")


def _search(code: CSSCode, *, check_matrix, span_matrix, max_weight: int | None) -> int | None:
    """Search increasing-weight candidate supports for the first one that
    commutes with check_matrix and is not in the row span of span_matrix.

    Returns the weight of the first match. Returns None only if max_weight
    was None (i.e. the search ran exhaustively to code.n) and nothing was
    found. Raises IncompleteSearchError if max_weight was explicitly below
    code.n and nothing was found within that bound.
    """
    search_limit = max_weight if max_weight is not None else code.n
    for weight in range(1, search_limit + 1):
        for qubits in combinations(range(code.n), weight):
            a = np.zeros(code.n, dtype=int)
            a[list(qubits)] = 1
            a = as_binary_vector(a)
            if np.all(matmul(check_matrix, a.reshape(-1, 1)) == 0) and not is_in_row_span(a, span_matrix):
                return weight
    if search_limit < code.n:
        raise IncompleteSearchError(
            f"No logical operator found within max_weight={search_limit}, but code.n={code.n}; "
            "absence is not confirmed. Increase max_weight, or omit it to search exhaustively."
        )
    return None


def exact_distance_x(code: CSSCode, *, max_weight: int | None = None, max_qubits: int = 24) -> int | None:
    """Search for d_x = min{|x| : x in ker(H_Z) \\ row(H_X)}.

    Returns None only if the search was exhaustive (max_weight left at its
    default, i.e. searched up to code.n) and no logical operator exists.
    If max_weight is explicitly restricted below code.n and nothing is found,
    raises IncompleteSearchError rather than returning None, since absence
    is not confirmed in that case.
    """

    _validate_max_weight(max_weight)
    _validate_max_qubits(code, max_qubits)
    return _search(code, check_matrix=code.hz, span_matrix=code.hx, max_weight=max_weight)


def exact_distance_z(code: CSSCode, *, max_weight: int | None = None, max_qubits: int = 24) -> int | None:
    """Search for d_z = min{|z| : z in ker(H_X) \\ row(H_Z)}.

    Same None-vs-IncompleteSearchError policy as exact_distance_x; see its
    docstring.
    """

    _validate_max_weight(max_weight)
    _validate_max_qubits(code, max_qubits)
    return _search(code, check_matrix=code.hx, span_matrix=code.hz, max_weight=max_weight)


def exact_distance(code: CSSCode, *, max_weight: int | None = None, max_qubits: int = 24) -> "CSSDistance":
    """Exact distance of a small CSS code: d = min(d_x, d_z).

     (d,d_x,d_z)==(0,0,0) when code.k == 0
    (no nontrivial logical operator can exist). Otherwise, see
    exact_distance_x/exact_distance_z for the None-vs-IncompleteSearchError
    policy when max_weight is explicitly restricted.
    """

    _validate_max_weight(max_weight)
    _validate_max_qubits(code, max_qubits)
    if code.k == 0:
        return CSSDistance(d_x=None, d_z=None, d=None)
    d_x = exact_distance_x(code, max_weight=max_weight, max_qubits=max_qubits)
    d_z = exact_distance_z(code, max_weight=max_weight, max_qubits=max_qubits)
    d = min(d_x, d_z) if d_x is not None and d_z is not None else None
    return CSSDistance(d_x=d_x, d_z=d_z, d=d)