cmake_minimum_required(VERSION 3.20)
project(casino_odds_engine LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

include(FetchContent)

# ---- Catch2 (name it exactly Catch2 so Catch2_SOURCE_DIR is defined) ----
FetchContent_Declare(
  Catch2
  GIT_REPOSITORY https://github.com/catchorg/Catch2.git
  GIT_TAG v3.6.0
)
FetchContent_MakeAvailable(Catch2)

# ---- IMPORTANT: turn on CTest at the top level ----
enable_testing()

add_subdirectory(src)
add_subdirectory(tests)
