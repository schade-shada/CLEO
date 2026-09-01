from condensation import Condensation
from microphysics import Microphysics, run_step
from workload import Workload

def main():

    # --------------------------------------------------------
    # Simple CLEO configuration
    # --------------------------------------------------------

    n_gbx = 2
    n_sd_per_gbx = 3

    t_mdl = 0
    t_mdl_next = 1


    # --------------------------------------------------------
    # Create microphysics model
    # --------------------------------------------------------

    condensation = Condensation()

    microphysics = Microphysics(
        condensation=condensation
    )


    # --------------------------------------------------------
    # Run CLEO
    # --------------------------------------------------------

    workload = run_step(
        t_mdl=t_mdl,
        t_mdl_next=t_mdl_next,
        n_gbx=n_gbx,
        n_sd_per_gbx=n_sd_per_gbx,
        microphysics=microphysics,
    )


    # --------------------------------------------------------
    # Print workload
    # --------------------------------------------------------

    print("=== CLEO Condensation Workload ===")

    print("\nOperations:")
    for operation, count in workload.operations.items():
        print(f"  {operation:5s}: {count}")

    print(f"\nBytes read:    {workload.bytes_read}")
    print(f"Bytes written: {workload.bytes_written}")
    print(f"Total bytes:   {workload.naive_RW_bytes()}")

    # --------------------------------------------------------
    # Roofline calculation
    # --------------------------------------------------------

    roofline = workload.roofline(
        n_sd_per_gbx=n_sd_per_gbx,
        n_gbx=n_gbx,
        peak_flops=19.5e12,
        peak_memory_bandwidth=1.5e12,
    )

    print("=== CLEO Condensation Roofline ===")

    print(f"FLOPs per SD:       {roofline['FLOPs_per_SD']}")
    print(f"Bytes per SD:       {roofline['bytes_per_SD']}")
    print(f"Arithmetic Intensity: {roofline['AI']:.4f} FLOPs/byte")
    print(f"Compute time:        {roofline['T_comp']:.6e} s")
    print(f"Memory time:         {roofline['T_mem']:.6e} s")
    print(f"Total time:          {roofline['T_total']:.6e} s")


if __name__ == "__main__":
    main()