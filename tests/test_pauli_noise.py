import numpy as np
import pytest

from homoloqode.noise import IndependentPauliNoise, PauliError

# ---------------------------------------------------------------------------
# Exact deterministic cases
# ---------------------------------------------------------------------------


def test_zero_probability_always_returns_identity() -> None:
    noise = IndependentPauliNoise(p_x=0.0, p_y=0.0, p_z=0.0)
    rng = np.random.default_rng(0)

    error = noise.sample(50, rng=rng)

    assert not np.any(error.x)
    assert not np.any(error.z)
    assert error.weight == 0


def test_certain_x_always_returns_all_x() -> None:
    noise = IndependentPauliNoise(p_x=1.0, p_y=0.0, p_z=0.0)
    rng = np.random.default_rng(1)

    error = noise.sample(50, rng=rng)

    assert np.all(error.x == 1)
    assert not np.any(error.z)


def test_certain_y_always_returns_all_y() -> None:
    noise = IndependentPauliNoise(p_x=0.0, p_y=1.0, p_z=0.0)
    rng = np.random.default_rng(2)

    error = noise.sample(50, rng=rng)

    assert np.all(error.x == 1)
    assert np.all(error.z == 1)


def test_certain_z_always_returns_all_z() -> None:
    noise = IndependentPauliNoise(p_x=0.0, p_y=0.0, p_z=1.0)
    rng = np.random.default_rng(3)

    error = noise.sample(50, rng=rng)

    assert not np.any(error.x)
    assert np.all(error.z == 1)


def test_equal_seeds_give_equal_arrays() -> None:
    noise = IndependentPauliNoise(p_x=0.1, p_y=0.2, p_z=0.3)

    first = noise.sample(200, rng=np.random.default_rng(42))
    second = noise.sample(200, rng=np.random.default_rng(42))

    assert np.array_equal(first.x, second.x)
    assert np.array_equal(first.z, second.z)


def test_continuing_generator_state_advances_normally() -> None:
    noise = IndependentPauliNoise(p_x=0.1, p_y=0.2, p_z=0.3)
    rng = np.random.default_rng(7)

    first = noise.sample(200, rng=rng)
    second = noise.sample(200, rng=rng)

    assert not (np.array_equal(first.x, second.x) and np.array_equal(first.z, second.z))


# ---------------------------------------------------------------------------
# Validation: IndependentPauliNoise construction
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("kwargs", [
    {"p_x": -0.1, "p_y": 0.0, "p_z": 0.0},
    {"p_x": 0.0, "p_y": -0.1, "p_z": 0.0},
    {"p_x": 0.0, "p_y": 0.0, "p_z": -0.1},
])
def test_negative_probability_is_rejected(kwargs: dict[str, float]) -> None:
    with pytest.raises(ValueError):
        IndependentPauliNoise(**kwargs)


def test_nan_probability_is_rejected() -> None:
    with pytest.raises(ValueError):
        IndependentPauliNoise(p_x=float("nan"), p_y=0.0, p_z=0.0)


def test_infinite_probability_is_rejected() -> None:
    with pytest.raises(ValueError):
        IndependentPauliNoise(p_x=float("inf"), p_y=0.0, p_z=0.0)


def test_probabilities_summing_above_one_are_rejected() -> None:
    with pytest.raises(ValueError, match="must be at most 1"):
        IndependentPauliNoise(p_x=0.5, p_y=0.4, p_z=0.3)


def test_floating_point_rounding_noise_is_tolerated() -> None:
    # 0.33 + 0.56 + 0.11 is not exactly representable in binary floating
    # point and sums marginally above 1.0; this must still be accepted.
    noise = IndependentPauliNoise(p_x=0.33, p_y=0.56, p_z=0.11)
    assert noise.p_identity == pytest.approx(0.0, abs=1e-9)


def test_x_boolean_probability_is_rejected() -> None:
    with pytest.raises(ValueError, match="bool"):
        IndependentPauliNoise(p_x=True, p_y=0.0, p_z=0.0)


def test_y_boolean_probability_is_rejected() -> None:
    with pytest.raises(ValueError, match="bool"):
        IndependentPauliNoise(p_x=0.0, p_y=True, p_z=0.0)


def test_z_boolean_probability_is_rejected() -> None:
    with pytest.raises(ValueError, match="bool"):
        IndependentPauliNoise(p_x=0.0, p_y=0.0, p_z=True)


# ---------------------------------------------------------------------------
# Validation: sample() arguments
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("n", [0, -1, -10])
def test_nonpositive_n_is_rejected(n: int) -> None:
    noise = IndependentPauliNoise(p_x=0.1, p_y=0.1, p_z=0.1)
    with pytest.raises(ValueError, match="positive integer"):
        noise.sample(n, rng=np.random.default_rng(0))


def test_boolean_n_is_rejected() -> None:
    noise = IndependentPauliNoise(p_x=0.1, p_y=0.1, p_z=0.1)
    with pytest.raises(ValueError, match="bool"):
        noise.sample(True, rng=np.random.default_rng(0))


def test_noninteger_n_is_rejected() -> None:
    noise = IndependentPauliNoise(p_x=0.1, p_y=0.1, p_z=0.1)
    with pytest.raises(ValueError, match="integer"):
        noise.sample(3.5, rng=np.random.default_rng(0))  # type: ignore[arg-type]


def test_missing_generator_is_rejected() -> None:
    noise = IndependentPauliNoise(p_x=0.1, p_y=0.1, p_z=0.1)
    with pytest.raises(ValueError, match="Generator"):
        noise.sample(5, rng=12345)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Validation: PauliError construction
# ---------------------------------------------------------------------------


def test_mismatched_x_z_lengths_are_rejected() -> None:
    with pytest.raises(ValueError, match="equal length"):
        PauliError(x=[0, 1, 0], z=[0, 1])


def test_nonbinary_error_vector_is_rejected() -> None:
    with pytest.raises(ValueError, match="0 and 1"):
        PauliError(x=[0, 2, 0], z=[0, 0, 0])


# ---------------------------------------------------------------------------
# weight and to_pauli_string
# ---------------------------------------------------------------------------


def test_weight_counts_nonidentity_qubits() -> None:
    error = PauliError(x=[0, 1, 1, 0, 0], z=[0, 0, 1, 1, 0])
    assert error.weight == 3


def test_to_pauli_string_matches_convention() -> None:
    error = PauliError(x=[0, 1, 1, 0], z=[0, 0, 1, 1])
    assert error.to_pauli_string() == "IXYZ"


# ---------------------------------------------------------------------------
# Statistical smoke test (loose, deterministic tolerance -- not flaky)
# ---------------------------------------------------------------------------


def test_empirical_frequencies_are_close_to_configured_probabilities() -> None:
    noise = IndependentPauliNoise(p_x=0.1, p_y=0.2, p_z=0.3)
    rng = np.random.default_rng(12345)

    error = noise.sample(100_000, rng=rng)

    empirical_x = float(np.mean((error.x == 1) & (error.z == 0)))
    empirical_y = float(np.mean((error.x == 1) & (error.z == 1)))
    empirical_z = float(np.mean((error.x == 0) & (error.z == 1)))
    empirical_i = float(np.mean((error.x == 0) & (error.z == 0)))

    tolerance = 0.01
    assert empirical_x == pytest.approx(0.1, abs=tolerance)
    assert empirical_y == pytest.approx(0.2, abs=tolerance)
    assert empirical_z == pytest.approx(0.3, abs=tolerance)
    assert empirical_i == pytest.approx(0.4, abs=tolerance)


# ---------------------------------------------------------------------------
# Integration with CSSCode.syndrome
# ---------------------------------------------------------------------------


def test_sampled_error_works_directly_with_css_code_syndrome() -> None:
    from homoloqode import toric_code

    code = toric_code(2)
    noise = IndependentPauliNoise(p_x=0.1, p_y=0.1, p_z=0.1)
    rng = np.random.default_rng(99)

    error = noise.sample(code.n, rng=rng)

    syndrome = code.syndrome(x_error=error.x, z_error=error.z)
    assert syndrome.x_checks.shape[0] == code.hx.shape[0]
    assert syndrome.z_checks.shape[0] == code.hz.shape[0]