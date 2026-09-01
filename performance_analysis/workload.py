from dataclasses import dataclass, field
from common import BYTES_PER_TYPE, NAIVE_FLOP_COST

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
        bytes_per_value = BYTES_PER_TYPE[dtype]

        return (self.bytes_read + self.bytes_written) * bytes_per_value

    def roofline(
        self,
        n_sd_per_gbx,
        n_gbx,
        peak_flops,
        peak_memory_bandwidth,
        dtype="float64",
    ):
        """
        Calculate naive Roofline quantities for this workload.
        """

        flops_per_sd = self.naive_FLOPs()
        bytes_per_sd = self.naive_RW_bytes(dtype)

        ai = flops_per_sd / bytes_per_sd

        t_comp = (
            n_sd_per_gbx
            * n_gbx
            * flops_per_sd
            / peak_flops
        )

        t_mem = (
            n_sd_per_gbx
            * n_gbx
            * bytes_per_sd
            / peak_memory_bandwidth
        )

        t_total = max(t_comp, t_mem)

        return {
            "FLOPs_per_SD": flops_per_sd,
            "bytes_per_SD": bytes_per_sd,
            "AI": ai,
            "T_comp": t_comp,
            "T_mem": t_mem,
            "T_total": t_total,
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