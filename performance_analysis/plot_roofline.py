import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_roofline(
    machine,
    roofline,
    output_path=None,
    show=False,
    kernel_name="",
):
    """
    Plot a double-precision Roofline model for a single kernel.
    """

    # ================================================================
    # Machine characteristics
    # ================================================================

    peak_bw = machine["peak_memory_bandwidth"]
    peak_dp = machine["peak_flops_dp"]

    unit_scale = 1e9

    bw_gbs = peak_bw / unit_scale
    dp_gflops = peak_dp / unit_scale

    # ================================================================
    # Plot limits
    # ================================================================

    x_min = 0.7
    x_max = 100.0

    y_min = 700.0
    y_max = 13000.0

    ai = np.logspace(
        np.log10(x_min),
        np.log10(x_max),
        500,
    )

    # ================================================================
    # Double-precision Roofline
    # ================================================================

    roof_dp = np.minimum(
        peak_dp,
        ai * peak_bw,
    ) / unit_scale

    # Knee point
    knee_dp = peak_dp / peak_bw

    # ================================================================
    # Figure
    # ================================================================

    fig, ax = plt.subplots(
        figsize=(5.5, 5.5),
        dpi=120,
        facecolor="white",
    )

    ax.set_facecolor("white")

    # Roofline
    ax.plot(
        ai,
        roof_dp,
        color="black",
        linewidth=1.2,
    )

    # ================================================================
    # Achieved performance point
    # ================================================================

    achieved_ai = roofline["AI"]
    achieved_perf = roofline["performance"] / unit_scale

    ax.plot(
        achieved_ai,
        achieved_perf,
        marker="o",
        markersize=6,
        linestyle="None",
        color="#d62728",
    )

    # ================================================================
    # Axes
    # ================================================================

    ax.set_xscale("log")
    ax.set_yscale("log")

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    ax.set_xlabel(
        "Arithmetic Intensity (FLOP/byte)",
        fontsize=11,
    )

    ax.set_ylabel(
        "GFLOP/s",
        fontsize=11,
    )

    # ================================================================
    # Ticks
    # ================================================================

    ax.set_xticks([1, 10, 100])
    ax.set_xticklabels(["1", "10", "100"])

    ax.set_yticks([1000, 10000])
    ax.set_yticklabels(["1000", "10000"])

    ax.tick_params(
        axis="both",
        which="major",
        labelsize=9,
        length=4,
    )

    ax.tick_params(
        axis="both",
        which="minor",
        length=2,
    )

    ax.grid(False)

    # ================================================================
    # Roofline annotations
    # ================================================================

    # Memory bandwidth
    # Place it well below the achieved point so it doesn't collide
    # with the kernel annotation.
    # ================================================================
# Memory bandwidth annotation
# ================================================================

    # Position the label on the bandwidth-limited part of the roofline
    bw_label_x = 1.5
    bw_label_y = bw_label_x * peak_bw / unit_scale

    # Calculate the actual visual angle of the roofline in display space
    p1 = ax.transData.transform((
        bw_label_x,
        bw_label_y,
    ))

    p2 = ax.transData.transform((
        bw_label_x * 1.5,
        bw_label_x * 1.5 * peak_bw / unit_scale,
    ))

    angle = np.degrees(
        np.arctan2(
            p2[1] - p1[1],
            p2[0] - p1[0],
        )
    )

    ax.annotate(
        f"{bw_gbs:.2f} GB/s",
        xy=(bw_label_x, bw_label_y),
        xytext=(0, 5),
        textcoords="offset points",
        fontsize=9,
        rotation=angle,
        rotation_mode="anchor",
        ha="left",
        va="bottom",
    )

    # Peak FLOP/s
    ax.text(
        knee_dp * 1.25,
        dp_gflops * 1.03,
        f"Double ({dp_gflops:.1f} GFLOP/s)",
        fontsize=9,
        ha="left",
        va="bottom",
    )

    # ================================================================
    # Kernel annotation
    # ================================================================

    # Move the label above and to the right of the point.
    # The two lines are separated to avoid the previous overlap.
    label = (
        f"{kernel_name}\n"
        f"({achieved_ai:.2f}, {achieved_perf:.2f})"
    )

    ax.annotate(
        label,
        xy=(achieved_ai, achieved_perf),
        xytext=(15, 0),
        textcoords="offset points",
        fontsize=9,
        ha="left",
        va="top",
    )

    # ================================================================
    # Legend
    # ================================================================

    ax.legend(
        frameon=False,
        loc="upper left",
        fontsize=8,
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

    if show:
        plt.show()

    plt.close(fig)

    return output_path