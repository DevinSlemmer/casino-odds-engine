# Build a simple executable from main.cpp
add_executable(casino cli/main.cpp)

# Let the target see headers in /include
target_include_directories(casino PUBLIC ${CMAKE_SOURCE_DIR}/include)
