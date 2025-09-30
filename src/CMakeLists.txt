# src/CMakeLists.txt

# ---- SQLite amalgamation (static lib) ----
add_library(sqlite3 STATIC
    ${PROJECT_SOURCE_DIR}/third_party/sqlite/sqlite3.c
)
target_include_directories(sqlite3 PUBLIC
    ${PROJECT_SOURCE_DIR}/third_party/sqlite
)
# PIC helps on Linux when linking into other targets
set_property(TARGET sqlite3 PROPERTY POSITION_INDEPENDENT_CODE ON)

# ---- Reusable engine code (DB wrapper, future game impls) ----
add_library(casino_engine STATIC
    db/sqlite.cpp
    # add more .cpp here later if you create them (e.g., games/dice.cpp)
)
target_include_directories(casino_engine PUBLIC
    ${PROJECT_SOURCE_DIR}/include
    ${PROJECT_SOURCE_DIR}/src
)
target_link_libraries(casino_engine PUBLIC sqlite3)

# Optional: warnings
if (MSVC)
  target_compile_options(casino_engine PRIVATE /W4)
else()
  target_compile_options(casino_engine PRIVATE -Wall -Wextra -Wpedantic)
endif()

# ---- CLI executable ----
add_executable(casino
    cli/main.cpp
)
target_include_directories(casino PRIVATE
    ${PROJECT_SOURCE_DIR}/include
    ${PROJECT_SOURCE_DIR}/src
)
target_link_libraries(casino PRIVATE casino_engine)

if (MSVC)
  target_compile_options(casino PRIVATE /W4)
else()
  target_compile_options(casino PRIVATE -Wall -Wextra -Wpedantic)
endif()
