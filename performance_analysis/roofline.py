import numpy as np


def build_roofline_curve(machine):
    """Return the roofline curve for a machine as a function of arithmetic intensity."""
    ai = np.geomspace(1e-4, 1e4, 400)
    peak_flops = machine["peak_flops_dp"]
    peak_bw = machine["peak_memory_bandwidth"]
    performance = np.minimum(peak_flops, ai * peak_bw)
    return ai, performance


def compute_roofline(workload, machine, dtype="float64", n_sd_per_gbx=None, n_gbx=None):
    """Compute naive roofline metrics for a workload using machine peak limits."""
    return workload.roofline(
        peak_flops=machine["peak_flops_dp"],
        peak_memory_bandwidth=machine["peak_memory_bandwidth"],
        n_sd_per_gbx=n_sd_per_gbx,
        n_gbx=n_gbx,
        dtype=dtype,
    )
