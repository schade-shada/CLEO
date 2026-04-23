#!/bin/bash

set -e


COMMON_BASH_SRC="${CLEO_PATH2CLEO}/scripts_2/common/bash/src"
MACHINE_BASH_SRC="${CLEO_PATH2CLEO}/scripts_2/${CLEO_MACHINE}/bash/src"

cleo_yac_module_path="${CLEO_PATH2CLEO}/libs/coupldyn_yac/cmake"

### -------------------- check inputs ------------------ ###
source ${COMMON_BASH_SRC}/check_inputs.sh
check_args_not_empty "${CLEO_PATH2CLEO}" "${CLEO_YACYAXTROOT}" "${CLEO_FYAMLLIB}"
### ---------------------------------------------------- ###

### ------------------ choose YAC build ---------------- ###
export CLEO_YAC_FLAGS="-DCLEO_YAC_MODULE_PATH="${cleo_yac_module_path}" \
  -DCLEO_FYAMLLIB=${CLEO_FYAMLLIB} \
  -DCLEO_YAXT_ROOT=${CLEO_YACYAXTROOT}/yaxt \
  -DCLEO_YAC_ROOT=${CLEO_YACYAXTROOT}/yac"
### ---------------------------------------------------- ###
