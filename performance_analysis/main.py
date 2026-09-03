from condensation import Condensation
from machine_registry import get_machine
from microphysics import Microphysics, run_step
from plot_roofline import plot_roofline
from roofline import compute_roofline


def main():

    # --------------------------------------------------------
    # Simple CLEO configuration (mimics exp_config.yaml)
    # --------------------------------------------------------

    machine_name = "levante_a100"

    n_gbx = 10
    # nsupers_pergbx = 134217726
    nsupers_pergbx = 13

    # timesteps, matching CLEO config.yaml semantics
    CONDTSTEP = 1  # time between SD condensation [s]
    T_END = 240  # total simulation time [s]

    t_mdl = 0
    t_mdl_next = T_END

    maxniters_newton_raphson = 50 # maximum no. iterations of Newton Raphson Method

    # --------------------------------------------------------
    # Create microphysics model
    # --------------------------------------------------------

    condensation = Condensation()
    microphysics = Microphysics(condensation=condensation)

    # --------------------------------------------------------
    # Run CLEO
    # --------------------------------------------------------

    workload = run_step(
        t_mdl=t_mdl,
        t_mdl_next=t_mdl_next,
        n_gbx=n_gbx,
        n_sd_per_gbx=nsupers_pergbx,
        microphysics=microphysics,
        condtstep=CONDTSTEP,
        maxniters_newton_raphson=maxniters_newton_raphson,
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
    # Roofline calculation from registry machine data
    # --------------------------------------------------------

    machine = get_machine(machine_name)
    roofline = compute_roofline(workload, machine)

    print("=== CLEO Condensation Roofline ===")
    print(f"Total FLOPs:          {roofline['FLOPs_total']:.0f}")
    print(f"Total bytes:          {roofline['bytes_total']:.0f}")
    print(f"Arithmetic Intensity: {roofline['AI']:.4f} FLOPs/byte")
    print(f"Compute time:         {roofline['T_comp']:.6e} s")
    print(f"Memory time:          {roofline['T_mem']:.6e} s")
    print(f"Total time:           {roofline['T_total']:.6e} s")
    print(f"Performance:          {roofline['performance']:.3e} FLOP/s")

    output_path = plot_roofline(
        machine=machine,
        roofline=roofline,
        output_path=f"{machine_name}_roofline.png",
        show=False,
        kernel_name="condensation",
    )
    print(f"\nSaved roofline plot to: {output_path}")


if __name__ == "__main__":
    main()