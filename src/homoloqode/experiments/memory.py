"""Reproducible quantum-memory trials for small CSS codes.

This module connects the public noise, syndrome, decoder, and residual-
classification APIs. Decoder search failures are propagated to the caller;
they are not silently reclassified as logical failures
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np

from homoloqode.codes import CSSCode, CSSSyndrome
from homoloqode.decoders import (
    CSSDecodeResult,
    ResidualClass,
    classify_residual,
    decode_syndrome,
)
from homoloqode.noise import IndependentPauliNoise, PauliError

class CSSDecoder(Protocol):
    """Callable decoder boundary used by the memory-experiment engine."""

    def __call__(
        self, code: CSSCode, syndrome: CSSSyndrome, /
    ) -> CSSDecodeResult:
        """Return a correction for ``syndrome`` on ``code``."""

        ...


@dataclass(frozen=True, slots=True)
class MemoryTrialResult:
    """Complte result of one sample, syndrome, and correction cycle."""

    error: PauliError
    syndrome: CSSSyndrome
    decode_result: CSSDecodeResult
    residual_class: ResidualClass

    @property
    def succeeded(self) -> bool:
        """Whether the residual acts trivially on the encoded information"""

        return self.residual_class is ResidualClass.STABILIZER


@dataclass(frozen=True, slots=True)
class MemoryExperimentResult:
    """Aggregate outcomes from reproducible independent memory trials.

    Individual trial results are deliberately not retained, so memory usage
    does not grow with ``trials`` beyond the aggregate counters.
    """

    trials: int
    stabilizer_successes: int
    logical_failures: int
    invalid_failures: int
    seed: int

    def __post_init__(self) -> None:
        _positive_integer(self.trials, name="trials")
        _nonnegative_integer(self.stabilizer_successes, name="stabilizer_successes")
        _nonnegative_integer(self.logical_failures, name="logical_failures")
        _nonnegative_integer(self.invalid_failures, name="invalid_failures")
        _nonnegative_integer(self.seed, name="seed")

        counted = (
            self.stabilizer_successes
            + self.logical_failures
            + self.invalid_failures
        )
        if counted != self.trials:
            raise ValueError(
                "Experiment outcome counts must sum to trials, "
                f"got {counted} outcomes for {self.trials} trials"
            )

    @property
    def logical_failure_rate(self) -> float:
        """Fraction of trials ending in a nontrivial logical residual."""

        return self.logical_failures / self.trials

    @property
    def invalid_failure_rate(self) -> float:
        """Fraction of trials whose residual still has nonzero syndrome."""

        return self.invalid_failures / self.trials


def _positive_integer(value: object, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer, got {value!r}.")
    return value


def _nonnegative_integer(value: object, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer, got {value!r}")
    return value


def _validate_trial_inputs(
    code: CSSCode,
    noise: IndependentPauliNoise,
    rng: np.random.Generator,
    decoder: CSSDecoder,
) -> None:
    if not isinstance(code, CSSCode):
        raise TypeError("code must be a CSSCode.")
    if not isinstance(noise, IndependentPauliNoise):
        raise TypeError("noise must be an IndependentPauliNoise.")
    if not isinstance(rng, np.random.Generator):
        raise TypeError("rng must be a numpy.random.Generator.")
    if not callable(decoder):
        raise TypeError("decoder must be callable.")


def run_memory_trial(
    code: CSSCode,
    noise: IndependentPauliNoise,
    *,
    rng: np.random.Generator,
    decoder: CSSDecoder = decode_syndrome,
) -> MemoryTrialResult:
    """Run one physical-noise and decoding trial.

    The sampled error and decoder correction are combined componentwise by
    XOR. A zero-syndrome residual is a success only when it is a stabilizer;
    a nontrivial logical residual is counted as a logical failure. Exceptions
    raised by ``decoder``, including bounded exhaustive-search failures, are
    propagated unchanged.

    Args:
        code: CSS code whose physical qubits store the logical state.
        noise: Independent Pauli channel sampled once per physical qubit.
        rng: Explicit generator controlling the noise sample.
        decoder: Callable returning X and Z corrections for a syndrome.

    Returns:
        The sampled error, syndrome, correction, and residual classification.

    Raises:
        TypeError: If an input does not satisfy the public experiment contract.
        ValueError: If the decoder returns corrections with the wrong length.
        Exception: Any exception raised by the supplied decoder is propagated.
    """

    _validate_trial_inputs(code, noise, rng, decoder)
    error = noise.sample(code.n, rng=rng)
    syndrome = code.syndrome(x_error=error.x, z_error=error.z)
    decode_result = decoder(code, syndrome)
    if not isinstance(decode_result, CSSDecodeResult):
        raise TypeError("decoder must return a CSSDecodeResult.")

    x_correction = decode_result.x_correction.support
    z_correction = decode_result.z_correction.support
    if x_correction.shape != error.x.shape or z_correction.shape != error.z.shape:
        raise ValueError(f"Decoder corrections must have length n={code.n}.")

    residual_x = np.bitwise_xor(error.x, x_correction)
    residual_z = np.bitwise_xor(error.z, z_correction)
    residual_class = classify_residual(
        code,
        x_residual=residual_x,
        z_residual=residual_z,
    )
    return MemoryTrialResult(
        error=error,
        syndrome=syndrome,
        decode_result=decode_result,
        residual_class=residual_class,
    )


def run_memory_experiment(
    code: CSSCode,
    noise: IndependentPauliNoise,
    *,
    trials: int,
    seed: int,
    decoder: CSSDecoder = decode_syndrome,
) -> MemoryExperimentResult:
    """Run seeded memory trials and return mutually exclusive outcome counts.

    Exactly one ``numpy.random.Generator`` is created from the nonnegative
    integer ``seed`` and reused for every trial. Individual trial objects are
    not retained. Decoder exceptions propagate to the caller instead of being
    counted as logical or invalid failures.

    Args:
        code: CSS code whose physical qubits store the logical state.
        noise: Independent Pauli channel sampled once per physical qubit.
        trials: Positive number of trials to aggregate.
        seed: Nonnegative integer seed for NumPy's local generator.
        decoder: Callable returning X and Z corrections for a syndrome.

    Returns:
        Reproducible aggregate counts and failure rates.

    Raises:
        ValueError: If ``trials`` or ``seed`` is invalid.
        TypeError: If an input does not satisfy the public experiment contract.
        Exception: Any exception raised by the supplied decoder is propagated.
    """

    trial_count = _positive_integer(trials, name="trials")
    validated_seed = _nonnegative_integer(seed, name="seed")
    if not isinstance(code, CSSCode):
        raise TypeError("code must be a CSSCode.")
    if not isinstance(noise, IndependentPauliNoise):
        raise TypeError("noise must be an IndependentPauliNoise.")
    if not callable(decoder):
        raise TypeError("decoder must be callable.")

    rng = np.random.default_rng(validated_seed)
    stabilizer_successes = 0
    logical_failures = 0
    invalid_failures = 0

    for _ in range(trial_count):
        result = run_memory_trial(
            code,
            noise,
            rng=rng,
            decoder=decoder,
        )
        if result.residual_class is ResidualClass.STABILIZER:
            stabilizer_successes += 1
        elif result.residual_class is ResidualClass.LOGICAL:
            logical_failures += 1
        elif result.residual_class is ResidualClass.INVALID:
            invalid_failures += 1
        else:  # pragma: no cover - protected by the ResidualClass result type
            raise RuntimeError(
                f"Unsupported residual classification {result.residual_class!r}."
            )

    return MemoryExperimentResult(
        trials=trial_count,
        stabilizer_successes=stabilizer_successes,
        logical_failures=logical_failures,
        invalid_failures=invalid_failures,
        seed=validated_seed,
    )
