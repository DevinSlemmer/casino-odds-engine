# ---- SQLite static library (from the amalgamation you added) ----
add_library(sqlite3 STATIC
  ${CMAKE_SOURCE_DIR}/third_party/sqlite/sqlite3.c
)
target_include_directories(sqlite3 PUBLIC
  ${CMAKE_SOURCE_DIR}/third_party/sqlite
)

# ---- Your executable ----
add_executable(casino
  cli/main.cpp
  db/sqlite.cpp          # <-- add your DB wrapper source (we'll create this next)
)

# Public headers live here
target_include_directories(casino PUBLIC
  ${CMAKE_SOURCE_DIR}/include
  ${CMAKE_SOURCE_DIR}/third_party/sqlite   # so #include <sqlite3.h> works in your cpp
)

# Link the app to SQLite
target_link_libraries(casino PRIVATE sqlite3)
