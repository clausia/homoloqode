"""Tests for exact small-code CSS distance calculations."""

from dataclasses import FrozenInstanceError

import numpy as np
import pytest

import homoloqode
from homoloqode import CSSCode, exact_distance, toric_code, exact_distance_x, exact_distance_z, IncompleteSearchError
from homoloqode.algebra import is_in_row_span
from homoloqode.codes.distance import _search

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


def test_distance_result_is_immutable() -> None:
    result = exact_distance(toric_code(2))

    with pytest.raises(FrozenInstanceError):
        result.d = 3  # type: ignore[misc]


def test_max_qubits_guard_rejects_large_codes() -> None:
    """A code larger than max_qubits must be rejected before any search."""
    code = toric_code(3)
    with pytest.raises(ValueError, match="max_qubits"):
        exact_distance(code, max_qubits=10)


@pytest.mark.parametrize("max_qubits", [-1, True, 1.5])
def test_invalid_max_qubits_is_rejected(max_qubits: object) -> None:
    with pytest.raises(ValueError, match="max_qubits"):
        exact_distance(
            toric_code(2),
            max_qubits=max_qubits,  # type: ignore[arg-type]
        )

def test_max_weight_too_small_raises_incomplete_search_error() -> None:
    """If max_weight is too small to find the real distance, the search
    must raise IncompleteSearchError, not silently return None."""
    with pytest.raises(IncompleteSearchError):
        exact_distance(toric_code(3), max_weight=1)

def test_max_weight_large_enough_finds_distance() -> None:
    """A sufficient max_weight must still find the right distance."""
    result = exact_distance(toric_code(2), max_weight=2)
    assert (result.d_x, result.d_z, result.d) == (2, 2, 2)


@pytest.mark.parametrize("max_weight", [-1, True, 1.5])
def test_invalid_max_weight_is_rejected(max_weight: object) -> None:
    with pytest.raises(ValueError, match="max_weight"):
        exact_distance(
            toric_code(2),
            max_weight=max_weight,  # type: ignore[arg-type]
        )


def test_zero_max_weight_is_a_valid_but_incomplete_bound() -> None:
    with pytest.raises(IncompleteSearchError):
        exact_distance(toric_code(2), max_weight=0)


def test_exhaustive_search_returns_none_when_no_quotient_vector_exists() -> None:
    code = CSSCode(
        hx=np.eye(2, dtype=np.uint8),
        hz=np.zeros((0, 2), dtype=np.uint8),
    )

    result = _search(
        code,
        check_matrix=code.hz,
        span_matrix=code.hx,
        max_weight=None,
    )

    assert result is None


def test_stabilizer_row_is_excluded_via_row_span() -> None:
    """A genuine stabilizer row must be detected as lying in row(H_X)."""
    code = toric_code(2)
    stabilizer_row = code.hx[0]

    assert is_in_row_span(stabilizer_row, code.hx)

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

def test_all_entries_are_strings() -> None:
    """Every item in homoloqode.__all__ must be a string; a bare class
    object there raises TypeError on `from homoloqode import *`."""
    non_strings = [item for item in homoloqode.__all__ if not isinstance(item, str)]
    assert non_strings == []

def test_every_submodule_all_entries_are_strings() -> None:
    """The same must hold for every submodule's __all__, not just the
    top-level package, so the bug can't reappear one level down."""
    import importlib, pkgutil

    problems = []
    module_names = ["homoloqode"] + [
        m.name for m in pkgutil.walk_packages(homoloqode.__path__, "homoloqode.")
    ]
    for name in module_names:
        try:
            module = importlib.import_module(name)
        except Exception:
            continue
        for item in getattr(module, "__all__", []):
            if not isinstance(item, str):
                problems.append((name, item))
    assert problems == []

def test_star_import_works() -> None:
    """`from homoloqode import *` must not raise, and must expose the
    distance API including IncompleteSearchError."""
    namespace: dict[str, object] = {}
    exec("from homoloqode import *", namespace)
    for name in ("exact_distance", "exact_distance_x", "exact_distance_z",
                 "CSSDistance", "IncompleteSearchError"):
        assert name in namespace

def test_all_entries_are_actually_importable() -> None:
    """Every name listed in homoloqode.__all__ must really exist on the
    package, so __all__ can't drift out of sync with the real exports."""
    for name in homoloqode.__all__:
        assert hasattr(homoloqode, name), f"{name} is in __all__ but not importable"
