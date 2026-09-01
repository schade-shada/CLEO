from common import BYTES_PER_TYPE

class memory:

    SD_ATTR_MEMORY_FOOTPRINT = {
        "solute-properties": ("float64", 3),
        "multiplicity": ("int64", 1),
        "Attr": ("float64", 2),
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
        "states": ("float64", 8),
    }

    GBX_MEMORY_FOOTPRINT = {
        **GBX_INDEX_MEMORY_FOOTPRINT,
        **SUPERS_IN_GBX_MEMORY_FOOTPRINT,
        **STATE_MEMORY_FOOTPRINT,
    }

    @classmethod
    def memory_footprint(cls, footprint):
        return sum(
            count * BYTES_PER_TYPE[dtype]
            for dtype, count in footprint.values()
        )

    @classmethod
    def max_sd_per_gbx(cls, vram_bytes, n_gbx):

        sd_bytes = cls.memory_footprint(cls.SD_MEMORY_FOOTPRINT)
        gbx_bytes = cls.memory_footprint(cls.GBX_MEMORY_FOOTPRINT)

        gbx_memory = n_gbx * gbx_bytes

        if gbx_memory >= vram_bytes:
            raise ValueError(
                "The gridbox memory footprint exceeds the available VRAM."
            )

        available_sd_memory = vram_bytes - gbx_memory

        return int(
            available_sd_memory / (sd_bytes * n_gbx)
        )