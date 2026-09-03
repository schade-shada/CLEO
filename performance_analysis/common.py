NAIVE_FLOP_COST = {
    "+": 1,
    "-": 1,
    "*": 1,
    "/": 30,
    "fma": 1,
    "sqrt": 1,  # * Naive convention
    "exp": 1,  # * Naive convention
    "pow": 1,  # * Naive convention
    "max": 1,  # * Naive convention (e.g. Kokkos::fmax)
}