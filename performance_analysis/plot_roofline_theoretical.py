# %%
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
plt.style.use("style.mplstyle")

def offset_axis(ax, offset_pts=8) -> None:
    """Format axis with no top/right spines, offset spines."""
    ax.spines["bottom"].set_position(("outward", offset_pts))
    ax.spines["left"].set_position(("outward", offset_pts))

def plot_roofline(
    machine,
    output_path=None,
    show=False,
):
    """
    Plot a generic Roofline model.

    Parameters
    ----------
    machine : dict
        Must contain:
            peak_memory_bandwidth : bytes/s
            peak_flops_dp         : FLOP/s

    output_path : str, optional
        Path to save the figure.

    show : bool
        Whether to display the figure.
    """

    # ================================================================
    # Machine characteristics
    # ================================================================

    peak_bw = machine["peak_memory_bandwidth"]
    peak_perf = machine["peak_flops_dp"]

    unit_scale = 1e9

    bw_gbs = peak_bw / unit_scale
    perf_gflops = peak_perf / unit_scale

    # ================================================================
    # Plot limits
    # ================================================================

    x_min = 1.0
    x_max = 100.0

    y_min = 1000.0
    y_max = 40000.0

    # Padding (log-space) so the roofline/shading never touches the axes
    axis_pad = 10.15
    x_lim_min = x_min / axis_pad
    x_lim_max = x_max * axis_pad
    y_lim_min = y_min / axis_pad
    y_lim_max = y_max * axis_pad

    # Arithmetic intensity range
    ai = np.logspace(
        np.log10(x_min),
        np.log10(x_max),
        500,
    )

    # ================================================================
    # Roofline
    # ================================================================

    roofline = np.minimum(
        peak_perf,
        ai * peak_bw,
    ) / unit_scale

    # Knee point
    knee_ai = peak_perf / peak_bw

    # ================================================================
    # Figure
    # ================================================================

    fig, ax = plt.subplots(
        figsize=(9, 6),
    )

    ax.set_facecolor("white")

    # ================================================================
    # Shaded regions
    # ================================================================

    # Memory-bound region
    memory_ai = ai[ai <= knee_ai]
    memory_roof = memory_ai * peak_bw / unit_scale

    ax.fill_between(
        memory_ai,
        y_min,
        memory_roof,
        color="#AB92D7",
        alpha=0.25,
        linewidth=0,
    )

    # Compute-bound region
    compute_ai = ai[ai >= knee_ai]

    ax.fill_between(
        compute_ai,
        y_min,
        peak_perf / unit_scale,
        color="#f4ef70",
        alpha=0.25,
        linewidth=0,
    )

    ax.scatter(
        knee_ai,
        peak_perf / unit_scale,
        color="black",
        zorder=5,
    )

    # ================================================================
    # Roofline
    # ================================================================

    ax.plot(
        ai,
        roofline,
        color="black",
    )

    # ================================================================
    # Axes
    # ================================================================

    ax.set_xscale("log")
    ax.set_yscale("log")

    offset_axis(ax, offset_pts=10)

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    ax.set_ylabel("GFLOP/s")


    ax.set_xlabel(
        "Arithmetic Intensity (FLOP/byte)",
    )



    # ================================================================
    # Ticks
    # ================================================================

    ax.set_xticks([1, 10, 100])
    ax.set_xticklabels(["1", "10", "100"])

    ax.set_yticks([1000, 10000])
    ax.set_yticklabels(["1000", "10000"])

    ax.grid(False)

    # ================================================================
    # Roofline annotations
    # ================================================================

    # ------------------------------------------------
    # Memory bandwidth label
    # ------------------------------------------------

    bw_label_x = 1.3
    bw_label_y =1.05* bw_label_x * peak_bw / unit_scale

    # Calculate the visual angle of the sloped roofline
    p1 = ax.transData.transform(
        (bw_label_x, bw_label_y)
    )

    p2 = ax.transData.transform(
        (
            bw_label_x * 1.5,
            bw_label_x * 1.5 * peak_bw / unit_scale,
        )
    )

    angle = 40.0

    ax.text(
        bw_label_x,
        bw_label_y,
        f"Peak Memory Bandwidth ({bw_gbs:.0f} GB/s)",
        rotation=angle,
        rotation_mode="anchor",
        ha="left",
        va="bottom",
    )

    # ------------------------------------------------
    # Peak performance label
    # ------------------------------------------------

    ax.text(
        knee_ai * 1.0,
        peak_perf / unit_scale * 1.03,
        f" FP64 Theoretical Peak Performance ({perf_gflops:.0f} GFLOP/s)",
        ha="left",
        va="bottom",
    )

    # ================================================================
    # Region labels
    # ================================================================

    # Memory-bound label
    ax.text(
        knee_ai / 3.0,
        y_min * 3.0,
        "Memory Bound",
        ha="center",
        va="center",
    )

    # Compute-bound label
    ax.text(
        np.sqrt(knee_ai * x_max),
        y_min * 6.0,
        "Compute Bound",
        ha="center",
        va="center",
    )


    # ================================================================
    # Final formatting
    # ================================================================

    plt.tight_layout()

    if output_path is not None:
        plt.savefig(
            output_path,
            bbox_inches="tight",
        )


    plt.show()

    # plt.close(fig)

    return output_path

# if __name__ == "__main__":


#%%
machine = {
    "peak_memory_bandwidth": 4000e9,  # bytes/s
    "peak_flops_dp": 34000e9,          # FLOP/s
}

plot_roofline(
    machine=machine,
    output_path="generic_roofline.png",
    show=True,
)
# %%
