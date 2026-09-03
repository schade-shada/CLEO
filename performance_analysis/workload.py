from dataclasses import dataclass, field
from common import NAIVE_FLOP_COST

@dataclass
class Workload:
    operations: dict = field(default_factory=dict)
    bytes_read: int = 0
    bytes_written: int = 0

    def add_operation(self, operation, count=1):
        self.operations[operation] = (
            self.operations.get(operation, 0) + count
        )

    def add(self, other):
        for operation, count in other.operations.items():
            self.add_operation(operation, count)

        self.bytes_read += other.bytes_read
        self.bytes_written += other.bytes_written

    def scale(self, factor):
        """
        Return a new Workload scaled by an integer factor.

        Useful for representing many identical parallel units (e.g. gridboxes)
        without looping, since the roofline model only needs total FLOPs/bytes.
        """
        scaled = Workload()

        for operation, count in self.operations.items():
            scaled.add_operation(operation, count * factor)

        scaled.bytes_read = self.bytes_read * factor
        scaled.bytes_written = self.bytes_written * factor

        return scaled

    def naive_FLOPs(self):
        """
        Calculate the naive FLOP count for this workload.
        """
        return sum(
            count * NAIVE_FLOP_COST[operation]
            for operation, count in self.operations.items()
        )

    def naive_RW_bytes(self, dtype="float64"):
        """
        Calculate naive read/write memory traffic.

        Assumes every read and write transfers one value of dtype.
        """
        bytes_per_value = 8

        return (self.bytes_read + self.bytes_written) * bytes_per_value

    def roofline(
        self,
        peak_flops,
        peak_memory_bandwidth,
        n_sd_per_gbx=None,
        n_gbx=None,
        dtype="float64",
    ):
        """
        Calculate naive Roofline quantities for this workload.

        If the Workload object represents a total aggregated workload for the full
        model step, pass only peak_flops and peak_memory_bandwidth. If instead it
        represents a per-gridbox/per-superdroplet workload, you may optionally
        provide n_sd_per_gbx and n_gbx to scale the totals up to system size.
        """

        total_flops = self.naive_FLOPs()
        total_bytes = self.naive_RW_bytes(dtype)

        if n_sd_per_gbx is not None and n_gbx is not None:
            total_flops *= n_sd_per_gbx * n_gbx
            total_bytes *= n_sd_per_gbx * n_gbx

        ai = total_flops / total_bytes if total_bytes else 0.0

        t_comp = total_flops / peak_flops
        t_mem = total_bytes / peak_memory_bandwidth
        t_total = max(t_comp, t_mem)

        return {
            "FLOPs_total": total_flops,
            "bytes_total": total_bytes,
            "FLOPs_per_SD": self.naive_FLOPs(),
            "bytes_per_SD": self.naive_RW_bytes(dtype),
            "AI": ai,
            "T_comp": t_comp,
            "T_mem": t_mem,
            "T_total": t_total,
            "performance": total_flops / t_total if t_total else 0.0,
        }

## EXAMPLE CALL
# Workload(
#     operations={
#         "+": 3,
#         "*": 2,
#         "/": 1,
#     },
#     bytes_read=24,
#     bytes_written=8,
# )