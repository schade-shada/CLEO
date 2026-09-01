
BYTES_PER_TYPE = {
    "int32": 4,
    "int64": 8,
    "float32": 4,
    "float64": 8,
    "pointer": 8,
}

NAIVE_FLOP_COST = {
    "+": 1,
    "-": 1,
    "*": 1,
    "/": 1,
    "fma": 2,
    "sqrt": 1,  # * Naive convention
    "exp": 1,  # * Naive convention
}