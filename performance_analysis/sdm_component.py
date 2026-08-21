from performance_analysis.naive_AI import naive_component_roofline

SDM_MOVEMENT_COMPONENTS = {
    "coord_upt": {},
    "gbx_upt": {},
    "sort": {},
    "boundary_conditions": {},
}


def calculate_component(
    component,
    component_data,
    n_sd_per_gbx,
    n_gbx,
    peak_flops,
    peak_memory_bandwidth,
    dtype="float64",
):
    if component not in SDM_MOVEMENT_COMPONENTS:
        raise ValueError(
            f"Unknown SDM movement component: {component!r}. "
            f"Expected one of: {list(SDM_MOVEMENT_COMPONENTS)}"
        )

    return naive_component_roofline(
        n_sd_per_gbx=n_sd_per_gbx,
        n_gbx=n_gbx,
        operations=component_data["operations"],
        reads=component_data["reads"],
        writes=component_data["writes"],
        peak_flops=peak_flops,
        peak_memory_bandwidth=peak_memory_bandwidth,
        dtype=dtype,
    )
