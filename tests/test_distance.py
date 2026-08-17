"""Tests fr homoloqode.codes.distance: exact_distance """

import numpy as np
import pytest

from homoloqode import CSSCode, exact_distance, toric_code, exact_distance_x, exact_distance_z, IncompleteSearchError
from homoloqode.algebra.gf2 import is_in_row_span

def test_size_two_toric_distance() -> None:
    """toric_code(2) is [[8,2,2]]: d_x = d_z = d = 2."""
    result = exact_distance(toric_code(2))
    assert (result.d_x, result.d_z, result.d) == (2, 2, 2)

def test_size_three_toric_distance() -> None:
    """toric_code(3) is [18,2,3]: so we want to see d_x = d_z = d = 3."""
    result = exact_distance(toric_code(3))
    assert (result.d_x, result.d_z, result.d) == (3, 3, 3)

def test_k_zero_returns_all_none() -> None:
    """A code with k=0 has no nontrivial logical operator; exact_distance
    must give CSSDistance(None, None, None) without searching."""
    code = CSSCode(hx=np.eye(3, dtype=int), hz=np.zeros((0, 3), dtype=int))
    assert code.k == 0

    result = exact_distance(code)
    assert (result.d_x, result.d_z, result.d) == (None, None, None)

def test_max_qubits_guard_rejects_large_codes() -> None:
    """A code larger than max_qubits must be rejected before any search."""
    code = toric_code(3)
    with pytest.raises(ValueError, match="max_qubits"):
        exact_distance(code, max_qubits=10)

def test_max_weight_too_small_raises_incomplete_search_error() -> None:
    """If max_weight is too small to find the real distance, the search
    must raise IncompleteSearchError, not silently return None."""
    with pytest.raises(IncompleteSearchError):
        exact_distance(toric_code(3), max_weight=1)

def test_max_weight_large_enough_finds_distance() -> None:
    """A sufficient max_weight must still find the right distance."""
    result = exact_distance(toric_code(2), max_weight=2)
    assert (result.d_x, result.d_z, result.d) == (2, 2, 2)

def test_stabilizer_row_is_excluded_via_row_span() -> None:
    """A genuine stabilizer row must be detected as lying in row(H_X)."""
    code = toric_code(2)
    stabilizer_row = code.hx[0]

    assert is_in_row_span(stabilizer_row, code.hx)

def test_is_in_row_span_true_for_member() -> None:
    """A vector equal to the sum of matrix rows must be reported as a member."""
    matrix = np.array([[1, 0, 0], [0, 1, 0]])
    vector = np.array([1, 1, 0])
    assert is_in_row_span(vector, matrix)

def test_is_in_row_span_false_for_nonmember() -> None:
    """A vector outside the row span must be reported as not a member."""
    matrix = np.array([[1, 0, 0], [0, 1, 0]])
    vector = np.array([0, 0, 1])
    assert not is_in_row_span(vector, matrix)

def test_is_in_row_span_rejects_length_mismatch() -> None:
    """A vector whose length doesn't match the matrix column count, must raise."""
    matrix = np.array([[1, 0, 0], [0, 1, 0]])
    vector = np.array([1, 0])
    with pytest.raises(ValueError, match="length"):
        is_in_row_span(vector, matrix)

def test_nonbinary_check_matrix_rejected_by_csscode() -> None:
    """CSSCode itself must reject a non-binary check matrix; distance code
    never has to defend against non-binary input directly."""
    with pytest.raises(ValueError, match="0 and 1"):
        CSSCode(hx=np.array([[2, 0, 0]]), hz=np.zeros((0, 3), dtype=int))
# test for assymetric distance since for toric code we tested dx=dz
def test_asymmetric_distance() -> None:
    """A hand-built code with genuinely different d_x and d_z, confirming
    the search doesn't rely on symmetry the toric fixtures happen to have."""
    hx = np.array([[1, 0, 1, 1, 0], [1, 1, 0, 0, 1]])
    hz = np.array([[1, 1, 0, 1, 0]])
    code = CSSCode(hx=hx, hz=hz)

    result = exact_distance(code)

    assert result.d_x != result.d_z
    assert (result.d_x, result.d_z, result.d) == (1, 2, 1)

def test_search_excludes_stabilizers_not_just_helper() -> None:
    """The actual search (not just is_in_row_span in isolation) must not
    mistake a known stabilizer for the answer."""
    code = toric_code(2)
    stabilizer_row = code.hx[0]

    result = exact_distance_x(code)

    # the stabilizer itself shd notbe  reported as the answer
    assert result != int(stabilizer_row.sum())
    # and the actual search result must match the correct distance
    assert result == 2
def test_search_excludes_stabilizers_z() -> None:
    """Same check as above, mirrored for exact_distance_z / H_Z."""
    code = toric_code(2)
    stabilizer_row = code.hz[0]

    result = exact_distance_z(code)

    assert result != int(stabilizer_row.sum())
    assert result == 2