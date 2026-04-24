#!/bin/bash

set -e

### ============================================================ ###
###                      Vanilla script                          ###
### ============================================================ ###
###
### Usage:
###   ./build_compile_run_plot.sh [experiment] [buildtype] [compilername] \
###                               [path2CLEO] [path2build] [build_flags] \
###                               [executables] [pythonscript] [script_args] \
###                               [enabledebug] [make_clean]
###
### Arguments:
###   $1  do_build       true | false                    (default: true)
###   $2  buildtype      serial | threads | openmp       (default: serial)
###   $3  compilername   gcc                             (default: gcc)
###   $4  path2CLEO      Absolute path to CLEO source    (default: $CLEO_PATH2CLEO)
###   $5  path2build     Absolute path for build dir     (default: $CLEO_PATH2BUILD)
###   $6  build_flags    Extra CMake flags               (default: "")
###   $7  executables    Space-separated list of targets (default: "")
###   $8  pythonscript   Absolute path to Python script  (default: "")
###   $9  script_args    Extra args passed to pythonscript (default: "")
###   $10 enabledebug    true | false                    (default: false)
###   $11 make_clean     true | false                    (default: false)
### ============================================================ ###

export CLEO_MACHINE="vanilla"

do_build=${1:-true}
buildtype=${2:-"serial"}
compilername=${3:-"gcc"}
path2CLEO=${4:-${CLEO_PATH2CLEO}}

if [ -z "${path2CLEO}" ]; then
  echo "Error: path to CLEO source directory is not set."
  exit 1
fi

path2build=${5:-${CLEO_PATH2BUILD}}
build_flags=${6:-""}
executables=${7:-""}
pythonscript=${8:-""}
script_args=${9:-""}
enabledebug=${10:-false}
make_clean=${11:-false}

python=${CLEO_PYTHON}
yacyaxtroot=${CLEO_YACYAXTROOT}

### -------------------- print inputs ------------------ ###
echo "----- Running Example -----"
echo "do_build      = ${do_build}"
echo "buildtype     = ${buildtype}"
echo "compilername  = ${compilername}"
echo "path2CLEO     = ${path2CLEO}"
echo "path2build    = ${path2build}"
echo "build_flags   = ${build_flags}"
echo "executables   = ${executables}"
echo "pythonscript  = ${pythonscript}"
echo "script_args   = ${script_args}"
echo "enabledebug   = ${enabledebug}"
echo "make_clean    = ${make_clean}"
echo "---------------------------"
### ---------------------------------------------------- ###

### --------------- build and compile CLEO ------------- ###
if [ "${do_build}" == "true" ]; then
  buildcmd="${path2CLEO}/scripts_2/vanilla/build_run_cleo.sh"
  if [ ! -f "${buildcmd}" ]; then
    echo "Error: build script not found at ${buildcmd}"
    exit 1
  fi
  "${buildcmd}" "" "${buildtype}" "${compilername}" "${path2CLEO}" \
    "${path2build}" "${build_flags}" "${yacyaxtroot}" "${enabledebug}" "${make_clean}"
fi
### ---------------------------------------------------- ###

### ----------- run Python plot/analysis script -------- ###
if [ -z "${pythonscript}" ]; then
  echo "Error: no Python script provided."
  exit 1
fi
if [ ! -f "${pythonscript}" ]; then
  echo "Error: Python script not found at ${pythonscript}"
  exit 1
fi
if [ -z "${python}" ]; then
  echo "Error: CLEO_PYTHON is not set."
  exit 1
fi

echo "Running: ${python} ${pythonscript} ${path2CLEO} ${path2build} ${script_args}"
${python} "${pythonscript}" "${path2CLEO}" "${path2build}" ${script_args}
### ---------------------------------------------------- ###
