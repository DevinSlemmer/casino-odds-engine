#include <catch2/catch_all.hpp>
#include "db/sqlite.hpp"
#include <sqlite3.h>
#include <filesystem>

TEST_CASE("DB roundtrip: multiple rows + counts/aggregates") {
    const std::string path = "data/test_roundtrip.db";
    std::filesystem::create_directories("data");

    // fresh file
    std::error_code ec;
    std::filesystem::remove(path, ec);

    db::Sqlite db(path);

    // insert three different rows
    db.insert_game("dice", 1, 6, 6, 5.0, 1.0, 1000, 160, 0.16, 1000, 800, -200, -0.2, -0.2, 1.0, 0.01, -0.21, -0.19, 5);
    db.insert_game("dice", 2, 6, 6, 5.0, 1.0, 2000, 320, 0.16, 2000, 1600, -400, -0.2, -0.2, 1.0, 0.007, -0.21, -0.19, 5);
    db.insert_game("dice", 3, 6, 6, 5.0, 1.0, 3000, 480, 0.16, 3000, 2400, -600, -0.2, -0.2, 1.0, 0.005, -0.21, -0.19, 5);

    sqlite3* conn = nullptr;
    REQUIRE(sqlite3_open(path.c_str(), &conn) == SQLITE_OK);

    sqlite3_stmt* stmt = nullptr;

    // count rows
    REQUIRE(sqlite3_prepare_v2(conn, "SELECT COUNT(*) FROM games WHERE type='dice';", -1, &stmt, nullptr) == SQLITE_OK);
    REQUIRE(sqlite3_step(stmt) == SQLITE_ROW);
    REQUIRE(sqlite3_column_int(stmt, 0) == 3);
    sqlite3_finalize(stmt);

    // average EV ≈ -0.2
    REQUIRE(sqlite3_prepare_v2(conn, "SELECT ROUND(AVG(ev), 3) FROM games WHERE type='dice';", -1, &stmt, nullptr) == SQLITE_OK);
    REQUIRE(sqlite3_step(stmt) == SQLITE_ROW);
    REQUIRE(sqlite3_column_double(stmt, 0) == Catch::Approx(-0.2).margin(0.005));
    sqlite3_finalize(stmt);

    sqlite3_close(conn);
}
