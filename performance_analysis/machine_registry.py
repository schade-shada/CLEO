"""Machine registry and roofline helpers for performance analysis.

This module centralizes machine-specific peak performance data so the roofline
plot and timing estimates can be generated from a registry instead of hard-coded
constants in the workload script.
"""

from __future__ import annotations

MACHINE_REGISTRY = {
    "levante_a100": {
        "name": "NVIDIA A100 40GB PCIe",
        "peak_flops_dp": 9.7e12,
        "peak_flops_sp": 19.5e12,
        "peak_memory_bandwidth": 1.56e12,
        "memory_capacity": 40 * 1024**3,
    },
}


def get_machine(machine_name: str):
    """Return machine metadata from the registry."""
    if machine_name not in MACHINE_REGISTRY:
        raise KeyError(f"Unknown machine '{machine_name}'. Available: {sorted(MACHINE_REGISTRY)}")
    return MACHINE_REGISTRY[machine_name]


def build_roofline_curve(machine: dict):
    """Return roofline performance curve for a machine as a function of arithmetic intensity.

    The roofline is defined as:
        performance = min(peak_flops, AI * peak_memory_bandwidth)
    for AI > 0, with units FLOP/s.
    """
    ai = [10 ** x for x in [i / 50 for i in range(-40, 200)]]
    perf = []

    peak_flops = machine["peak_flops_dp"]
    peak_bw = machine["peak_memory_bandwidth"]

    for val in ai:
        perf.append(min(peak_flops, val * peak_bw))

    return ai, perf
