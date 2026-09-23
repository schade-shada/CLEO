#!/bin/bash

#SBATCH --job-name=cleo_cpu
#SBATCH --partition=booster
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=288
#SBATCH --time=00:30:00
#SBATCH --account=xspies
#SBATCH --output=./cleo_cpu.%j.out
#SBATCH --error=./cleo_cpu.%j.out

set -e

# ============================================================
# Environment
# ============================================================

source /etc/profile

# Required if the .venv does not use the default environment.
module load Stages/2026 Python/3.13.5

export CLEO_PATH2CLEO="${SLURM_SUBMIT_DIR:-$(pwd)}"
export CLEO_PYTHON="${CLEO_PYTHON:-${CLEO_PATH2CLEO}/.venv/bin/python3}"
export CLEO_YACYAXTROOT="${CLEO_YACYAXTROOT:-${HOME}/yacyaxt/gcc}"

# ============================================================
# Configuration
# ============================================================

mode="${1:-run}"

experiment="constthermo2d"
buildtype="openmp"
compilername="gcc"

# ============================================================
# Validation
# ============================================================
source "${CLEO_PATH2CLEO}/scripts_2/common/check_inputs.sh"
check_args_not_empty "${CLEO_PATH2CLEO}" "${CLEO_PYTHON}" "${CLEO_YACYAXTROOT}"
# ============================================================
# Helper functions
# ============================================================
case "${mode}" in
    build)
        "${CLEO_PATH2CLEO}/scripts_2/jupiter/build_compile_run_plot_cleo.sh" \
            "${experiment}" "${buildtype}" "${compilername}" "${CLEO_PATH2CLEO}" \
            "${CLEO_PATH2BUILD}" "" "${CLEO_YACYAXTROOT}" false false 204800 build,compile
        ;;
    run)

        echo "=== Running ${experiment} (${buildtype}, ${compilername}) ==="
        "${CLEO_PATH2CLEO}/scripts_2/jupiter/build_compile_run_plot_cleo.sh" \
            "${experiment}" "${buildtype}" "${compilername}" "${CLEO_PATH2CLEO}" "${CLEO_PATH2BUILD}"
        ;;
    *)
        echo "Usage: $0 [build|run]"
        exit 1
        ;;
esac
