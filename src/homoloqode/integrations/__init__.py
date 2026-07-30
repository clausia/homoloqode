"""Qiskit integration and future quantum-software ecosystem adapters."""

from homoloqode.integrations.qiskit import (
    QiskitSyndromeCircuits,
    QiskitSyndromeResult,
    build_syndrome_circuits,
    counts_to_syndrome,
    simulate_syndrome,
)

__all__ = [
    "QiskitSyndromeCircuits",
    "QiskitSyndromeResult",
    "build_syndrome_circuits",
    "counts_to_syndrome",
    "simulate_syndrome",
]
