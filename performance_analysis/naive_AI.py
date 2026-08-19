from performance_analysis.memory_footprint import BYTES_PER_TYPE

NAIVE_FLOP_COST = {
    "+": 1,
    "-": 1,
    "*": 1,
    "/": 1,
    "fma": 2,
    "sqrt": 1,  # * Naive convention
    "exp": 1,  # * Naive convention
}


def naive_FLOPs(operations):
    """
    Calculate the naive FLOP count for a set of operations.
    """
    return sum(
        count * NAIVE_FLOP_COST[operation] for operation, count in operations.items()
    )


def naive_RW_bytes(reads, writes, dtype="float64"):
    """
    Calculate naive read/write memory traffic.

    Assumes every read and write transfers one value of `dtype`.
    """
    bytes_per_value = BYTES_PER_TYPE[dtype]

    return (reads + writes) * bytes_per_value


def naive_component_roofline(
    n_sd_per_gbx,
    n_gbx,
    operations,
    reads,
    writes,
    peak_flops,
    peak_memory_bandwidth,
    dtype="float64",
):
    """
    Calculate naive Roofline quantities for one CLEO component.
    """

    flops_per_sd = naive_FLOPs(operations)
    bytes_per_sd = naive_RW_bytes(reads, writes, dtype)

    ai = flops_per_sd / bytes_per_sd

    t_comp = n_sd_per_gbx * n_gbx * flops_per_sd / peak_flops

    t_mem = n_sd_per_gbx * n_gbx * bytes_per_sd / peak_memory_bandwidth

    t_total = max(t_comp, t_mem)

    return {
        "FLOPs_per_SD": flops_per_sd,
        "bytes_per_SD": bytes_per_sd,
        "AI": ai,
        "T_comp": t_comp,
        "T_mem": t_mem,
        "T_total": t_total,
    }
