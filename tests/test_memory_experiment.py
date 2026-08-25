from dataclasses import FrozenInstanceError, fields
from functools import partial

import numpy as np
import pytest

from homoloqode import CSSCode, toric_code
from homoloqode.codes import CSSSyndrome
from homoloqode.decoders import (
    BinaryCorrection,
    CSSDecodeResult,
    DecodingFailure,
    ResidualClass,
    decode_syndrome,
)
from homoloqode.experiments import (
    MemoryExperimentResult,
    MemoryTrialResult,
    run_memory_experiment,
    run_memory_trial,
)
from homoloqode.noise import IndependentPauliNoise


def _logical_decoder(code: CSSCode, syndrome: CSSSyndrome) -> CSSDecodeResult:
    del syndrome
    logical_x = code.logical_basis().x[0]
    return CSSDecodeResult(
        x_correction=BinaryCorrection(logical_x),
        z_correction=BinaryCorrection(np.zeros(code.n, dtype=np.uint8)),
    )


def _invalid_decoder(code: CSSCode, syndrome: CSSSyndrome) -> CSSDecodeResult:
    del syndrome
    x_correction = np.zeros(code.n, dtype=np.uint8)
    x_correction[0] = 1
    return CSSDecodeResult(
        x_correction=BinaryCorrection(x_correction),
        z_correction=BinaryCorrection(np.zeros(code.n, dtype=np.uint8)),
    )


def _wrong_length_decoder(
    code: CSSCode, syndrome: CSSSyndrome
) -> CSSDecodeResult:
    del code, syndrome
    return CSSDecodeResult(
        x_correction=BinaryCorrection([0]),
        z_correction=BinaryCorrection([0]),
    )


def test_one_trial_returns_complete_immutable_result() -> None:
    code = toric_code(2)
    noise = IndependentPauliNoise(p_x=0.0, p_y=0.0, p_z=0.0)

    result = run_memory_trial(code, noise, rng=np.random.default_rng(123))

    assert isinstance(result, MemoryTrialResult)
    assert result.error.n == code.n
    assert result.syndrome.x_checks.shape == (code.hx.shape[0],)
    assert result.syndrome.z_checks.shape == (code.hz.shape[0],)
    assert result.decode_result.x_correction.support.shape == (code.n,)
    assert result.decode_result.z_correction.support.shape == (code.n,)
    assert result.residual_class is ResidualClass.STABILIZER
    assert result.succeeded
    with pytest.raises(FrozenInstanceError):
        result.residual_class = ResidualClass.LOGICAL  # type: ignore[misc]


def test_zero_noise_gives_only_stabilizer_successes() -> None:
    result = run_memory_experiment(
        toric_code(2),
        IndependentPauliNoise(p_x=0.0, p_y=0.0, p_z=0.0),
        trials=8,
        seed=17,
    )

    assert result == MemoryExperimentResult(
        trials=8,
        stabilizer_successes=8,
        logical_failures=0,
        invalid_failures=0,
        seed=17,
    )
    assert result.logical_failure_rate == 0.0
    assert result.invalid_failure_rate == 0.0
    with pytest.raises(FrozenInstanceError):
        result.trials = 9  # type: ignore[misc]


def test_equal_seeds_give_identical_aggregate_results() -> None:
    code = toric_code(2)
    noise = IndependentPauliNoise(p_x=0.15, p_y=0.1, p_z=0.2)

    first = run_memory_experiment(code, noise, trials=20, seed=31415)
    second = run_memory_experiment(code, noise, trials=20, seed=31415)

    assert first == second


def test_experiment_does_not_use_numpy_global_random_state() -> None:
    original_state = np.random.get_state()
    try:
        np.random.seed(2026)
        state_before = np.random.get_state()
        run_memory_experiment(
            toric_code(2),
            IndependentPauliNoise(p_x=0.1, p_y=0.1, p_z=0.1),
            trials=5,
            seed=9,
        )
        state_after = np.random.get_state()
    finally:
        np.random.set_state(original_state)

    assert state_before[0] == state_after[0]
    assert np.array_equal(state_before[1], state_after[1])
    assert state_before[2:] == state_after[2:]


def test_aggregate_counts_are_mutually_exclusive_and_exhaustive() -> None:
    result = run_memory_experiment(
        toric_code(2),
        IndependentPauliNoise(p_x=0.2, p_y=0.2, p_z=0.2),
        trials=15,
        seed=42,
    )

    counted = (
        result.stabilizer_successes
        + result.logical_failures
        + result.invalid_failures
    )
    assert counted == result.trials
    assert result.logical_failure_rate == result.logical_failures / result.trials
    assert result.invalid_failure_rate == result.invalid_failures / result.trials


def test_fixed_logical_residual_increments_logical_failures() -> None:
    result = run_memory_experiment(
        toric_code(2),
        IndependentPauliNoise(p_x=0.0, p_y=0.0, p_z=0.0),
        trials=4,
        seed=0,
        decoder=_logical_decoder,
    )

    assert result.stabilizer_successes == 0
    assert result.logical_failures == 4
    assert result.invalid_failures == 0
    assert result.logical_failure_rate == 1.0


def test_fixed_nonzero_syndrome_residual_increments_invalid_failures() -> None:
    result = run_memory_experiment(
        toric_code(2),
        IndependentPauliNoise(p_x=0.0, p_y=0.0, p_z=0.0),
        trials=3,
        seed=0,
        decoder=_invalid_decoder,
    )

    assert result.stabilizer_successes == 0
    assert result.logical_failures == 0
    assert result.invalid_failures == 3
    assert result.invalid_failure_rate == 1.0


@pytest.mark.parametrize(
    ("code", "noise"),
    [
        (
            CSSCode(
                hx=np.zeros((0, 2), dtype=np.uint8),
                hz=np.array([[1, 1]], dtype=np.uint8),
            ),
            IndependentPauliNoise(p_x=1.0, p_y=0.0, p_z=0.0),
        ),
        (
            CSSCode(
                hx=np.array([[1, 1]], dtype=np.uint8),
                hz=np.zeros((0, 2), dtype=np.uint8),
            ),
            IndependentPauliNoise(p_x=0.0, p_y=0.0, p_z=1.0),
        ),
    ],
)
def test_deterministic_all_pauli_channel_has_expected_logical_residual(
    code: CSSCode, noise: IndependentPauliNoise
) -> None:
    result = run_memory_trial(code, noise, rng=np.random.default_rng(1))

    assert result.error.weight == code.n
    assert result.residual_class is ResidualClass.LOGICAL
    assert not result.succeeded


@pytest.mark.parametrize("trials", [0, -1, 1.5, True])
def test_invalid_trial_count_is_rejected(trials: object) -> None:
    with pytest.raises(ValueError, match="trials must be a positive integer"):
        run_memory_experiment(
            toric_code(2),
            IndependentPauliNoise(p_x=0.0, p_y=0.0, p_z=0.0),
            trials=trials,  # type: ignore[arg-type]
            seed=0,
        )


@pytest.mark.parametrize("seed", [-1, 1.5, True])
def test_invalid_seed_is_rejected(seed: object) -> None:
    with pytest.raises(ValueError, match="seed must be a nonnegative integer"):
        run_memory_experiment(
            toric_code(2),
            IndependentPauliNoise(p_x=0.0, p_y=0.0, p_z=0.0),
            trials=1,
            seed=seed,  # type: ignore[arg-type]
        )


def test_decoder_failure_is_propagated() -> None:
    code = CSSCode(
        hx=np.zeros((0, 3), dtype=np.uint8),
        hz=np.eye(3, dtype=np.uint8),
    )
    bounded_decoder = partial(decode_syndrome, max_weight=1)

    with pytest.raises(DecodingFailure, match="max_weight=1"):
        run_memory_experiment(
            code,
            IndependentPauliNoise(p_x=1.0, p_y=0.0, p_z=0.0),
            trials=2,
            seed=0,
            decoder=bounded_decoder,
        )


def test_decoder_must_return_decode_result() -> None:
    def wrong_decoder(code: CSSCode, syndrome: CSSSyndrome) -> object:
        del code, syndrome
        return object()

    with pytest.raises(TypeError, match="CSSDecodeResult"):
        run_memory_trial(
            toric_code(2),
            IndependentPauliNoise(p_x=0.0, p_y=0.0, p_z=0.0),
            rng=np.random.default_rng(0),
            decoder=wrong_decoder,  # type: ignore[arg-type]
        )


def test_decoder_corrections_must_match_code_length() -> None:
    with pytest.raises(ValueError, match="length n=8"):
        run_memory_trial(
            toric_code(2),
            IndependentPauliNoise(p_x=0.0, p_y=0.0, p_z=0.0),
            rng=np.random.default_rng(0),
            decoder=_wrong_length_decoder,
        )


def test_code_noise_and_decoder_are_validated() -> None:
    code = toric_code(2)
    noise = IndependentPauliNoise(p_x=0.0, p_y=0.0, p_z=0.0)
    rng = np.random.default_rng(0)

    with pytest.raises(TypeError, match="code must be a CSSCode"):
        run_memory_trial(object(), noise, rng=rng)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="noise must be"):
        run_memory_trial(code, object(), rng=rng)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="rng must be"):
        run_memory_trial(code, noise, rng=object())  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="decoder must be callable"):
        run_memory_trial(code, noise, rng=rng, decoder=None)  # type: ignore[arg-type]


def test_code_and_noise_are_not_mutated() -> None:
    code = toric_code(2)
    noise = IndependentPauliNoise(p_x=0.1, p_y=0.2, p_z=0.3)
    hx_before = code.hx.copy()
    hz_before = code.hz.copy()
    probabilities_before = (noise.p_x, noise.p_y, noise.p_z)

    run_memory_experiment(code, noise, trials=5, seed=11)

    assert np.array_equal(code.hx, hx_before)
    assert np.array_equal(code.hz, hz_before)
    assert (noise.p_x, noise.p_y, noise.p_z) == probabilities_before


def test_aggregate_result_validates_counts_and_does_not_retain_trials() -> None:
    with pytest.raises(ValueError, match="must sum to trials"):
        MemoryExperimentResult(
            trials=3,
            stabilizer_successes=1,
            logical_failures=1,
            invalid_failures=0,
            seed=0,
        )

    names = {field.name for field in fields(MemoryExperimentResult)}
    assert names == {
        "trials",
        "stabilizer_successes",
        "logical_failures",
        "invalid_failures",
        "seed",
    }
