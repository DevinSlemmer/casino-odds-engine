# tests/CMakeLists.txt
enable_testing()
include(CTest)

# Find Catch2's CMake helpers
list(APPEND CMAKE_MODULE_PATH ${Catch2_SOURCE_DIR}/extras)
include(Catch)

# ---- tests_basic (RNG + distribution sanity) ----
add_executable(tests_basic tests_basic.cpp)
target_link_libraries(tests_basic PRIVATE Catch2::Catch2WithMain casino_engine)
target_include_directories(tests_basic PRIVATE
    ${PROJECT_SOURCE_DIR}/include
    ${PROJECT_SOURCE_DIR}/src
)
catch_discover_tests(tests_basic)

# ---- test_ev_convergence (Dice EV → theory) ----
add_executable(test_ev_convergence test_ev_convergence.cpp)
target_link_libraries(test_ev_convergence PRIVATE Catch2::Catch2WithMain casino_engine)
target_include_directories(test_ev_convergence PRIVATE
    ${PROJECT_SOURCE_DIR}/include
    ${PROJECT_SOURCE_DIR}/src
)
catch_discover_tests(test_ev_convergence)

# ---- test_dice_math ----
add_executable(test_dice_math test_dice_math.cpp)
target_link_libraries(test_dice_math PRIVATE Catch2::Catch2WithMain casino_engine)
target_include_directories(test_dice_math PRIVATE
    ${PROJECT_SOURCE_DIR}/include
    ${PROJECT_SOURCE_DIR}/src
)
catch_discover_tests(test_dice_math)


# ---- test_db_insert (schema + insert works) ----
add_executable(test_db_insert test_db_insert.cpp)
target_link_libraries(test_db_insert PRIVATE Catch2::Catch2WithMain casino_engine sqlite3)
target_include_directories(test_db_insert PRIVATE
    ${PROJECT_SOURCE_DIR}/include
    ${PROJECT_SOURCE_DIR}/third_party/sqlite
    ${PROJECT_SOURCE_DIR}/src
)
catch_discover_tests(test_db_insert)

