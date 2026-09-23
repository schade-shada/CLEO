#!/bin/bash

# Slurm resources for the single-GPU CLEO job.
#SBATCH --job-name=cleo_gpu_4000mib
#SBATCH --partition=booster
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=72
#SBATCH --gpus-per-node=1
#SBATCH --time=01:20:00
#SBATCH --account=xspies
#SBATCH --output=./cleo_gpu_4000mib.%j.out
#SBATCH --error=./cleo_gpu_4000mib.%j.out

set -e

# Load the site environment and the Python runtime used by the helper script.
source /etc/profile
module load Stages/2026 Python/3.13.5

# Resolve paths from the submission directory while allowing site-specific overrides.
export CLEO_PATH2CLEO="${SLURM_SUBMIT_DIR:-$(pwd)}"
export CLEO_PYTHON="${CLEO_PYTHON:-${CLEO_PATH2CLEO}/.venv/bin/python3}"
export CLEO_YACYAXTROOT="${CLEO_YACYAXTROOT:-${HOME}/yacyaxt/gcc}"
export CLEO_PATH2BUILD="${CLEO_PATH2BUILD:-/e/scratch/xspies/cleo/builds/4000mib_dm/}"

# Use run mode unless the caller explicitly requests a build.
mode="${1:-run}"
experiment="constthermo2d"
buildtype="cuda"
compilername="gcc"

source "${CLEO_PATH2CLEO}/scripts_2/common/check_inputs.sh"
check_args_not_empty "${CLEO_PATH2CLEO}" "${CLEO_PYTHON}" "${CLEO_YACYAXTROOT}"

# The build mode performs only the build and compile stages.
# The run mode omits the stages argument, so the helper defaults to all:
# build, compile, run, and plot.
case "${mode}" in
    build)
        "${CLEO_PATH2CLEO}/scripts_2/jupiter/build_compile_run_plot_cleo.sh" \
            "${experiment}" "${buildtype}" "${compilername}" "${CLEO_PATH2CLEO}" \
            "${CLEO_PATH2BUILD}" "" "${CLEO_YACYAXTROOT}" false false 204800 build,compile
        ;;
    run)

        roofline_output="/e/scratch/xspies/cleo/nsys_output"
        mkdir -p "${roofline_output}"

        export KOKKOS_TOOLS_LIBS="/e/home/jusers/balasubramanian2/jupiter/kokkos-tools/install/lib64/libkp_nvtx_connector.so"

        METRICS="sm__inst_executed_pipe_xu.avg.pct_of_peak_sustained_active,sm__inst_executed_pipe_fma.avg.pct_of_peak_sustained_active,sm__inst_executed_pipe_fp64.avg.pct_of_peak_sustained_active,sm__cycles_elapsed.avg,sm__cycles_elapsed.avg.per_second,sm__sass_thread_inst_executed_op_dadd_pred_on.sum,sm__sass_thread_inst_executed_op_dfma_pred_on.sum,sm__sass_thread_inst_executed_op_dmul_pred_on.sum,sm__sass_thread_inst_executed_op_fadd_pred_on.sum,sm__sass_thread_inst_executed_op_ffma_pred_on.sum,sm__sass_thread_inst_executed_op_fmul_pred_on.sum,dram__bytes.sum,dram__bytes.sum.per_second"

        export NSYS_PREFIX="ncu \
        --verbose \
        --nvtx \
        --nvtx-include timestep_sdm_movement/ \
        --replay-mode kernel \
        -c 30 \
        --kill yes \
        --cache-control none \
        --set roofline \
        --metrics $METRICS \
        --target-processes all \
        -o ${roofline_output}/constthermo2d_drop_motion_4000mib"

        echo "=== Running ${experiment} (${buildtype}, ${compilername}) ==="
        "${CLEO_PATH2CLEO}/scripts_2/jupiter/build_compile_run_plot_cleo.sh" \
            "${experiment}" "${buildtype}" "${compilername}" "${CLEO_PATH2CLEO}" "${CLEO_PATH2BUILD}"
        ;;
    *)
        echo "Usage: $0 [build|run]"
        exit 1
        ;;
esac
