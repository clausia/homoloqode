"""Tests for homoloqode.noise: PauliError and IndependentPauliNoise."""

import math

import numpy as np
import pytest

from homoloqode.noise import IndependentPauliNoise, PauliError


def test_zero_probability_always_returns_identity() -> None:
    """With p_x = p_y = p_z = 0, every sampled qubit must be I."""
    noise = IndependentPauliNoise(p_x=0.0, p_y=0.0, p_z=0.0)
    rng = np.random.default_rng(0)

    error = noise.sample(50, rng=rng)

    assert not np.any(error.x)
    assert not np.any(error.z)
    assert error.weight == 0


def test_certain_x_always_returns_all_x() -> None:
    """With p_x = 1, every sampled qubit must be X."""
    noise = IndependentPauliNoise(p_x=1.0, p_y=0.0, p_z=0.0)
    rng = np.random.default_rng(1)

    error = noise.sample(50, rng=rng)

    assert np.all(error.x == 1)
    assert not np.any(error.z)


def test_certain_y_always_returns_all_y() -> None:
    """With p_y = 1, every sampled qubit must be Y (x=1 and z=1)."""
    noise = IndependentPauliNoise(p_x=0.0, p_y=1.0, p_z=0.0)
    rng = np.random.default_rng(2)

    error = noise.sample(50, rng=rng)

    assert np.all(error.x == 1)
    assert np.all(error.z == 1)


def test_certain_z_always_returns_all_z() -> None:
    """With p_z = 1, every sampled qubit must be Z."""
    noise = IndependentPauliNoise(p_x=0.0, p_y=0.0, p_z=1.0)
    rng = np.random.default_rng(3)

    error = noise.sample(50, rng=rng)

    assert not np.any(error.x)
    assert np.all(error.z == 1)


def test_equal_seeds_give_equal_arrays() -> None:
    """Two generators built from the same seed must sample identically."""
    noise = IndependentPauliNoise(p_x=0.1, p_y=0.2, p_z=0.3)

    first = noise.sample(200, rng=np.random.default_rng(42))
    second = noise.sample(200, rng=np.random.default_rng(42))

    assert np.array_equal(first.x, second.x)
    assert np.array_equal(first.z, second.z)


def test_continuing_generator_state_advances_normally() -> None:
    """Two draws from one continuing generator should differ from each other."""
    noise = IndependentPauliNoise(p_x=0.1, p_y=0.2, p_z=0.3)
    rng = np.random.default_rng(7)

    first = noise.sample(200, rng=rng)
    second = noise.sample(200, rng=rng)

    assert not (np.array_equal(first.x, second.x) and np.array_equal(first.z, second.z))


@pytest.mark.parametrize("kwargs", [
    {"p_x": -0.1, "p_y": 0.0, "p_z": 0.0},
    {"p_x": 0.0, "p_y": -0.1, "p_z": 0.0},
    {"p_x": 0.0, "p_y": 0.0, "p_z": -0.1},
])
def test_negative_probability_is_rejected(kwargs: dict[str, float]) -> None:
    """Any negative probability, in any of the three components, must raise."""
    with pytest.raises(ValueError):
        IndependentPauliNoise(**kwargs)


def test_nan_probability_is_rejected() -> None:
    """NaN is not a valid probability and must raise."""
    with pytest.raises(ValueError):
        IndependentPauliNoise(p_x=float("nan"), p_y=0.0, p_z=0.0)


def test_infinite_probability_is_rejected() -> None:
    """Infinity is not a valid probability and must raise."""
    with pytest.raises(ValueError):
        IndependentPauliNoise(p_x=float("inf"), p_y=0.0, p_z=0.0)


def test_probabilities_summing_above_one_are_rejected() -> None:
    """A genuine excess over 1 (not floating-point noise) must raise."""
    with pytest.raises(ValueError, match="must be at most 1"):
        IndependentPauliNoise(p_x=0.5, p_y=0.4, p_z=0.3)


def test_floating_point_rounding_noise_is_tolerated() -> None:
    """0.33 + 0.56 + 0.11 is not exactly representable in binary floating
    point and sums marginally above 1.0; this must still be accepted."""
    noise = IndependentPauliNoise(p_x=0.33, p_y=0.56, p_z=0.11)
    assert noise.p_identity == pytest.approx(0.0, abs=1e-9)


def test_genuine_excess_over_one_is_rejected() -> None:
    """A real excess of 5e-10, far larger than floating-point noise
    (~1e-16), must be rejected, not silently tolerated."""
    with pytest.raises(ValueError, match="must be at most 1"):
        IndependentPauliNoise(p_x=0.5, p_y=0.5, p_z=5e-10)


@pytest.mark.parametrize("bool_kwargs", [
    {"p_x": True, "p_y": 0.0, "p_z": 0.0},
    {"p_x": 0.0, "p_y": True, "p_z": 0.0},
    {"p_x": 0.0, "p_y": 0.0, "p_z": True},
])
def test_boolean_probability_is_rejected(bool_kwargs: dict[str, object]) -> None:
    """in python, bool is silently treated as 0/1; it must raise, for
    p_x, p_y, and p_z alike."""
    with pytest.raises(ValueError, match="bool"):
        IndependentPauliNoise(**bool_kwargs)


@pytest.mark.parametrize("n", [0, -1, -10])
def test_nonpositive_n_is_rejected(n: int) -> None:
    """n must be strictly positive."""
    noise = IndependentPauliNoise(p_x=0.1, p_y=0.1, p_z=0.1)
    with pytest.raises(ValueError, match="positive integer"):
        noise.sample(n, rng=np.random.default_rng(0))


def test_noninteger_n_is_rejected() -> None:
    """n must be an integer, not a random float."""
    noise = IndependentPauliNoise(p_x=0.1, p_y=0.1, p_z=0.1)
    with pytest.raises(ValueError, match="integer"):
        noise.sample(3.5, rng=np.random.default_rng(0))  # type: ignore[arg-type]


def test_boolean_n_is_rejected() -> None:
    """n=True must not be silently treated as n=1; it must raise."""
    noise = IndependentPauliNoise(p_x=0.1, p_y=0.1, p_z=0.1)
    with pytest.raises(ValueError, match="bool"):
        noise.sample(True, rng=np.random.default_rng(0))  # type: ignore[arg-type]


def test_missing_generator_is_rejected() -> None:
    """rng must be an actual numpy.random.Generator, not a bare seed."""
    noise = IndependentPauliNoise(p_x=0.1, p_y=0.1, p_z=0.1)
    with pytest.raises(ValueError, match="Generator"):
        noise.sample(5, rng=12345)  # type: ignore[arg-type]


def test_mismatched_x_z_lengths_are_rejected() -> None:
    """x and z supports of a PauliError must have equal length."""
    with pytest.raises(ValueError, match="equal length"):
        PauliError(x=[0, 1, 0], z=[0, 1])


def test_nonbinary_error_vector_is_rejected() -> None:
    """PauliError's x/z entries must be 0 or 1, nothing else."""
    with pytest.raises(ValueError, match="0 and 1"):
        PauliError(x=[0, 2, 0], z=[0, 0, 0])


def test_weight_counts_nonidentity_qubits() -> None:
    """weight must count qubits with any error (X, Y, or Z), not I."""
    error = PauliError(x=[0, 1, 1, 0, 0], z=[0, 0, 1, 1, 0])
    assert error.weight == 3


def test_to_pauli_string_matches_convention() -> None:
    """to_pauli_string must follow the (x,z) -> I/X/Y/Z convention."""
    error = PauliError(x=[0, 1, 1, 0], z=[0, 0, 1, 1])
    assert error.to_pauli_string() == "IXYZ"


def test_empirical_frequencies_are_close_to_configured_probabilities() -> None:
    """Over "many" samples, empirical I/X/Y/Z frequencies must match the
    configured probabilities within a loose, deterministic tolerance."""
    noise = IndependentPauliNoise(p_x=0.1, p_y=0.2, p_z=0.3)
    rng = np.random.default_rng(12345)

    error = noise.sample(100_000, rng=rng)

    empirical_x = float(np.mean((error.x == 1) & (error.z == 0)))
    empirical_y = float(np.mean((error.x == 1) & (error.z == 1)))
    empirical_z = float(np.mean((error.x == 0) & (error.z == 1)))
    empirical_i = float(np.mean((error.x == 0) & (error.z == 0)))

    tolerance = 0.01  # loose and deterministic: not a flaky hypothesis test
    assert empirical_x == pytest.approx(0.1, abs=tolerance)
    assert empirical_y == pytest.approx(0.2, abs=tolerance)
    assert empirical_z == pytest.approx(0.3, abs=tolerance)
    assert empirical_i == pytest.approx(0.4, abs=tolerance)


def test_sampled_error_works_directly_with_css_code_syndrome() -> None:
    """A sampled PauliError's x/z arrays must plug directly into
    CSSCode.syndrome without any conversion."""
    from homoloqode import toric_code

    code = toric_code(2)
    noise = IndependentPauliNoise(p_x=0.1, p_y=0.1, p_z=0.1)
    rng = np.random.default_rng(99)

    error = noise.sample(code.n, rng=rng)

    syndrome = code.syndrome(x_error=error.x, z_error=error.z)
    assert syndrome.x_checks.shape[0] == code.hx.shape[0]
    assert syndrome.z_checks.shape[0] == code.hz.shape[0]