# tests/CMakeLists.txt

include(CTest)

add_executable(tests_basic tests_basic.cpp)
target_link_libraries(tests_basic PRIVATE Catch2::Catch2WithMain)
target_include_directories(tests_basic PRIVATE ${PROJECT_SOURCE_DIR}/include)
add_test(NAME tests_basic COMMAND tests_basic)

add_executable(test_dice test_dice.cpp)
target_link_libraries(test_dice PRIVATE Catch2::Catch2WithMain)
target_include_directories(test_dice PRIVATE ${PROJECT_SOURCE_DIR}/include)
add_test(NAME test_dice COMMAND test_dice)
