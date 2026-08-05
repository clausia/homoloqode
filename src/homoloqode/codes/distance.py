from dataclasses import dataclass
from itertools import combinations
import numpy as np
from homoloqode.codes.css import CSSCode
from homoloqode.algebra.gf2 import as_binary_vector, is_in_row_span, matmul


@dataclass(frozen=True, slots=True)
class CSSDistance:
    d_x: int | None
    d_z: int | None
    d: int | None


def exact_distance_x(code: CSSCode, *, max_weight: int | None = None) -> int | None:
    max_weight = max_weight or code.n
    for weight in range(1, max_weight + 1):
        for qubits in combinations(range(code.n), weight):
            a = np.zeros(code.n, dtype=int)
            a[list(qubits)] = 1
            a = as_binary_vector(a)
            if np.all(matmul(code.hz, a.reshape(-1, 1)) == 0) and not is_in_row_span(a, code.hx):
                return weight
    return None


def exact_distance_z(code: CSSCode, *, max_weight: int | None = None) -> int | None:
    max_weight = max_weight or code.n
    for weight in range(1, max_weight + 1):
        for qubits in combinations(range(code.n), weight):
            a = np.zeros(code.n, dtype=int)
            a[list(qubits)] = 1
            a = as_binary_vector(a)
            if np.all(matmul(code.hx, a.reshape(-1, 1)) == 0) and not is_in_row_span(a, code.hz):
                return weight
    return None


def exact_distance(code: CSSCode, *, max_weight: int | None = None, max_qubits: int = 24) -> "CSSDistance":
    if code.n > max_qubits:
        raise ValueError(f"code.n={code.n} exceeds max_qubits={max_qubits}.")
    if code.k == 0:
        return CSSDistance(d_x=None, d_z=None, d=None)
    d_x = exact_distance_x(code, max_weight=max_weight)
    d_z = exact_distance_z(code, max_weight=max_weight)
    d = min(d_x, d_z) if d_x is not None and d_z is not None else None
    return CSSDistance(d_x=d_x, d_z=d_z, d=d)