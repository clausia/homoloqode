import numpy as np
import pytest

from homoloqode import CSSCode, exact_distance, toric_code
from homoloqode.algebra.gf2 import is_in_row_span

def test_size_two_toric_distance() -> None:
    result = exact_distance(toric_code(2))
    assert (result.d_x, result.d_z, result.d) == (2, 2, 2)

def test_size_three_toric_distance() -> None:
    result = exact_distance(toric_code(3))
    assert (result.d_x, result.d_z, result.d) == (3, 3, 3)

def test_k_zero_returns_all_none() -> None:
    code = CSSCode(hx=np.eye(3, dtype=int), hz=np.zeros((0, 3), dtype=int))
    assert code.k == 0

    result = exact_distance(code)
    assert (result.d_x, result.d_z, result.d) == (None, None, None)

def test_max_qubits_guard_rejects_large_codes() -> None:
    code = toric_code(3)
    with pytest.raises(ValueError, match="max_qubits"):
        exact_distance(code, max_qubits=10)

def test_max_weight_too_small_returns_none() -> None:
    result = exact_distance(toric_code(3), max_weight=1)
    assert result.d_x is None
    assert result.d_z is None
    assert result.d is None

def test_max_weight_large_enough_finds_distance() -> None:
    result = exact_distance(toric_code(2), max_weight=2)
    assert (result.d_x, result.d_z, result.d) == (2, 2, 2)

def test_stabilizer_row_is_excluded_via_row_span() -> None:
    code = toric_code(2)
    stabilizer_row = code.hx[0]

    assert is_in_row_span(stabilizer_row, code.hx)

def test_is_in_row_span_true_for_member() -> None:
    matrix = np.array([[1, 0, 0], [0, 1, 0]])
    vector = np.array([1, 1, 0])
    assert is_in_row_span(vector, matrix)

def test_is_in_row_span_false_for_nonmember() -> None:
    matrix = np.array([[1, 0, 0], [0, 1, 0]])
    vector = np.array([0, 0, 1])
    assert not is_in_row_span(vector, matrix)

def test_is_in_row_span_rejects_length_mismatch() -> None:
    matrix = np.array([[1, 0, 0], [0, 1, 0]])
    vector = np.array([1, 0])
    with pytest.raises(ValueError, match="length"):
        is_in_row_span(vector, matrix)

def test_nonbinary_check_matrix_rejected_by_csscode() -> None:
    with pytest.raises(ValueError, match="0 and 1"):
        CSSCode(hx=np.array([[2, 0, 0]]), hz=np.zeros((0, 3), dtype=int))