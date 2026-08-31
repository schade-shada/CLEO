BYTES_PER_TYPE = {
    "int32": 4,
    "int64": 8,
    "float32": 4,
    "float64": 8,
    "pointer": 8,
}

SD_ATTR_MEMORY_FOOTPRINT = {
    "solute-properties": ("float64", 3),
    "multiplicity": ("int64", 1),
    "Attr": ("float64", 2), #radius and mass
}

SD_MEMORY_FOOTPRINT = {
    "sd-gbx-index": ("int64", 1),
    "spatial_coord": ("float64", 3),
    **SD_ATTR_MEMORY_FOOTPRINT,
}

GBX_INDEX_MEMORY_FOOTPRINT = {
    "index": ("int64", 1),
}

SUPERS_IN_GBX_MEMORY_FOOTPRINT = {
    "index": ("int64", 1),
    "references": ("pointer", 2),
}

STATE_MEMORY_FOOTPRINT = {
    "states": ("float64", 8), #volume, press, temp, qvap, qcond, wvel, uvel, vvel
}

GBX_MEMORY_FOOTPRINT = {
    **GBX_INDEX_MEMORY_FOOTPRINT,
    **SUPERS_IN_GBX_MEMORY_FOOTPRINT,
    **STATE_MEMORY_FOOTPRINT,
}

def memory_footprint(footprint, types=BYTES_PER_TYPE):
    return sum(
        count * BYTES_PER_TYPE[types.get(dtype, dtype)]
        for dtype, count in footprint.values()
    )

def max_sd_per_gbx(vram_bytes, n_gbx):
    """
    Calculate the maximum number of superdroplets per gridbox
    that can fit in the available VRAM.
    """
    sd_bytes = memory_footprint(SD_MEMORY_FOOTPRINT)
    gbx_bytes = memory_footprint(GBX_MEMORY_FOOTPRINT)

    gbx_memory = n_gbx * gbx_bytes

    if gbx_memory >= vram_bytes:
        raise ValueError("The gridbox memory footprint exceeds the available VRAM.")

    available_sd_memory = vram_bytes - gbx_memory

    return int(available_sd_memory / (sd_bytes * n_gbx))
