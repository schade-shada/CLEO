#!/bin/bash
#SBATCH --job-name=cleo_gpu
#SBATCH --partition=gpu
#SBATCH --constraint=a100_40
#SBATCH --nodes=1
#SBATCH --gpus=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=150G
#SBATCH --time=02:00:00
#SBATCH --mail-user=harshada.balasubramanian@mpimet.mpg.de
#SBATCH --mail-type=FAIL
#SBATCH --account=bk1341
#SBATCH --output=./cleo_gpu.%j.out
#SBATCH --error=./cleo_gpu.%j.out

export CLEO_PATH2CLEO="${SLURM_SUBMIT_DIR:-$(pwd)}"
export CLEO_PYTHON="${CLEO_PATH2CLEO}/.venv/bin/python3"

export KOKKOS_TOOLS_LIBS=/home/m/m301159/CLEO_profiling/kokkos-tools/profiling/nvtx-connector/kp_nvtx_connector.so

source "${CLEO_PATH2CLEO}/scripts_2/common/check_inputs.sh"
check_args_not_empty "${CLEO_PYTHON}" "${CLEO_YACYAXTROOT}"

nsys_output="${SLURM_SUBMIT_DIR:-$(pwd)}/nsys_output"
# export CLEO_PYTHON="nsys profile \
#   -t cuda,mpi,nvtx,osrt,cublas \
#   --gpu-metrics-device=all \
#   --cuda-memory-usage=true \
#   --stats=true \
#   -o ${nsys_output} \
#   ${CLEO_PYTHON}"

export NSYS_PREFIX="nsys profile -t cuda,mpi,nvtx,osrt,cublas --gpu-metrics-device=all --cuda-memory-usage=true --stats=true -o ${nsys_output}"


"${CLEO_PATH2CLEO}/scripts_2/levante/build_compile_run_plot_cleo.sh" constthermo2d cuda gcc "${CLEO_PATH2CLEO}"
