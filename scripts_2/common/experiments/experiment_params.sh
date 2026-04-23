#!/bin/bash

### Central experiment parameter lookup.
### Set 'experiment' before sourcing this file, or pass the experiment name as $3.
### Positional args allow CLI overrides:
###   $1 = path2build  override (optional, leave empty to use default)
###   $2 = build_flags override (optional, leave empty to use default)
###   $3 = experiment  name     (optional, overrides the 'experiment' variable)
###

path2build_override=${2:-""}
build_flags_override=${3:-""}
experiment=${4:-${experiment}}

if [ "${path2CLEO}" == "" ]; then
  echo "Please provide path to CLEO source directory"
  exit 1
fi

if [[ -z "${experiment}" ]]; then
  echo "Error: 'experiment' must be set before sourcing experiment_params.sh (or passed as \$4)"
  exit 1
fi

case "${experiment}" in

  as2017)
    path2build="${path2CLEO}/build_as2017"
    build_flags="-DCLEO_COUPLED_DYNAMICS=cvode -DCLEO_DOMAIN=cartesian \
      -DCLEO_NO_ROUGHPAPER=true -DCLEO_NO_PYBINDINGS=true"
    executables="adia0d"
    ;;

  cuspbifurc)
    path2build="${path2CLEO}/build_cuspbifurc"
    build_flags="-DCLEO_COUPLED_DYNAMICS=cvode -DCLEO_DOMAIN=cartesian \
      -DCLEO_NO_ROUGHPAPER=true -DCLEO_NO_PYBINDINGS=true"
    executables="adia0d"
    ;;

  breakup)
    path2build="${path2CLEO}/build_breakup"
    build_flags="-DCLEO_COUPLED_DYNAMICS=null -DCLEO_DOMAIN=cartesian \
      -DCLEO_NO_ROUGHPAPER=true -DCLEO_NO_PYBINDINGS=true"
    executables="longcolls lowlistcolls szakallurbichcolls testikstraubcolls"
    ;;

  shima2009)
    path2build="${path2CLEO}/build_shima2009"
    build_flags="-DCLEO_COUPLED_DYNAMICS=null -DCLEO_DOMAIN=cartesian \
      -DCLEO_NO_ROUGHPAPER=true -DCLEO_NO_PYBINDINGS=true"
    executables="golcolls longcolls"
    ;;

  constthermo2d)
    path2build="${path2CLEO}/build_constthermo2d"
    build_flags="-DCLEO_COUPLED_DYNAMICS=fromfile -DCLEO_DOMAIN=cartesian \
      -DCLEO_NO_ROUGHPAPER=true -DCLEO_NO_PYBINDINGS=true"
    executables="const2d"
    ;;

  divfree2d)
    path2build="${path2CLEO}/build_divfree2d"
    build_flags="-DCLEO_COUPLED_DYNAMICS=fromfile -DCLEO_DOMAIN=cartesian \
      -DCLEO_NO_ROUGHPAPER=true -DCLEO_NO_PYBINDINGS=true"
    executables="divfree2d"
    ;;

  eurec4a1d)
    path2build="${path2CLEO}/build_eurec4a1d"
    build_flags="-DCLEO_COUPLED_DYNAMICS=fromfile -DCLEO_DOMAIN=cartesian \
      -DCLEO_NO_ROUGHPAPER=true -DCLEO_NO_PYBINDINGS=true"
    executables="eurec4a1d"
    ;;

  rainshaft1d)
    path2build="${path2CLEO}/build_rainshaft1d"
    build_flags="-DCLEO_COUPLED_DYNAMICS=fromfile -DCLEO_DOMAIN=cartesian \
      -DCLEO_NO_ROUGHPAPER=true -DCLEO_NO_PYBINDINGS=true"
    executables="rshaft1d"
    ;;

  python_bindings)
    path2build="${path2CLEO}/build_python_bindings"
    build_flags="-DCLEO_COUPLED_DYNAMICS=numpy -DCLEO_DOMAIN=cartesian \
      -DCLEO_NO_ROUGHPAPER=true -DCLEO_PYTHON=${CLEO_PYTHON}"
    executables="cleo_python_bindings"
    ;;

  kokkostools)
    path2build="${path2CLEO}/build_kokkostools"
    build_flags="-DCLEO_COUPLED_DYNAMICS=fromfile -DCLEO_DOMAIN=cartesian \
      -DCLEO_NO_ROUGHPAPER=true -DCLEO_NO_PYBINDINGS=true"
    executables="kokkostools"
    ;;

  fromfile)
    path2build="${path2CLEO}/build_fromfile"
    build_flags="-DCLEO_COUPLED_DYNAMICS=fromfile -DCLEO_DOMAIN=cartesian \
      -DCLEO_NO_ROUGHPAPER=true -DCLEO_NO_PYBINDINGS=true"
    executables="fromfile"
    ;;

  fromfile_irreg)
    path2build="${path2CLEO}/build_fromfile_irreg"
    build_flags="-DCLEO_COUPLED_DYNAMICS=fromfile -DCLEO_DOMAIN=cartesian \
      -DCLEO_NO_ROUGHPAPER=true -DCLEO_NO_PYBINDINGS=true"
    executables="fromfile_irreg"
    ;;

  bubble3d)
    path2build="${path2CLEO}/build_bubble3d"
    build_flags="-DCLEO_COUPLED_DYNAMICS=yac -DCLEO_DOMAIN=cartesian \
      -DCLEO_NO_ROUGHPAPER=true -DCLEO_NO_PYBINDINGS=true"
    executables="bubble3d"
    ;;

  *)
    echo "Error: unknown experiment '${experiment}'."
    echo "Available: as2017 cuspbifurc breakup shima2009 constthermo2d divfree2d"
    echo "           eurec4a1d rainshaft1d python_bindings kokkostools"
    echo "           fromfile fromfile_irreg bubble3d"
    exit 1
    ;;
esac

### Apply CLI overrides if provided (non-empty args take precedence over defaults)
[[ -n "${path2build_override}" ]]  && path2build="${path2build_override}"
[[ -n "${build_flags_override}" ]] && build_flags="${build_flags_override}"

export CLEO_PATH2BUILD=${path2build}
export CLEO_BUILD_FLAGS="${build_flags}"
