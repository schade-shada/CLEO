model run through

run_step()
│
└── sdm_microphysics()
    │
    ├── GBx 0
    │    │
    │    └── microphysics.run_step()
    │         │
    │         └── condensation.run_step()
    │              │
    │              ├── superdroplets_change()
    │              │   │
    │              │   ├── saturation_pressure()
    │              │   ├── supersaturation_ratio()
    │              │   ├── diffusion_factor()
    │              │   │
    │              │   └── for each SD
    │              │       │
    │              │       └── superdrop_mass_change()
    │              │           ├── condensate_mass
    │              │           ├── kohler_factors()
    │              │           ├── solve_condensation()
    │              │           ├── change_radius()
    │              │           ├── calculate_mass_change()
    │              │           └── multiplicity
    │              │
    │              └── effect_on_thermodynamic_state()
    │                  └── thermodynamic_state_change()
    │
    ├── GBx 1
    │    └── ...
    │
    └── GBx N
         └── ...

and every box in that tree is given the input

Workload
│
├── operations
│     ├── "+"
│     ├── "-"
│     ├── "*"
│     ├── "/"
│     ├── "fma"
│     ├── "sqrt"
│     └── "exp"
│
├── bytes_read
└── bytes_written

which outputs

workload.naive_FLOPs()
workload.naive_RW_bytes()
workload.arithmetic_intensity()

which helps you plot the roofline.