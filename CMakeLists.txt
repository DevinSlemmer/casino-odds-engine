cmake_minimum_required(VERSION 3.20)
project(casino_odds_engine LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Add the source folder
add_subdirectory(src)