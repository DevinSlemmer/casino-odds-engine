# Root CMakeLists.txt
cmake_minimum_required(VERSION 3.20)
project(casino_odds_engine LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Fetch Catch2 (note the exact name "Catch2" so Catch2_SOURCE_DIR is defined)
include(FetchContent)
FetchContent_Declare(
  Catch2
  GIT_REPOSITORY https://github.com/catchorg/Catch2.git
  GIT_TAG v3.6.0
)
FetchContent_MakeAvailable(Catch2)

# Enable CTest at the top level
enable_testing()

# Subdirectories
add_subdirectory(src)
add_subdirectory(tests)
