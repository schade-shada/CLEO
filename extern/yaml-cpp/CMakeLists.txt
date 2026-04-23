if(NOT DEFINED CMAKE_MINIMUM_REQUIRED_VERSION)
  cmake_minimum_required(VERSION 3.5)
endif()

include(FetchContent)
FetchContent_Declare(
  yaml-cpp
  DOWNLOAD_EXTRACT_TIMESTAMP TRUE
  URL https://github.com/jbeder/yaml-cpp/archive/refs/tags/yaml-cpp-0.9.0.tar.gz
  GIT_TAG f7320141120f720aecc4c32be25586e7da9eb978
)
FetchContent_MakeAvailable(yaml-cpp)

message(STATUS "yaml-cpp installation in: ${CMAKE_CURRENT_BINARY_DIR}")
