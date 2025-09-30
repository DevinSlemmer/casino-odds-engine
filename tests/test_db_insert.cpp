// tests/test_db_insert.cpp
#include <catch2/catch_all.hpp>
#include <filesystem>
#include <sqlite3.h>

#include "db/sqlite.hpp"

TEST_CASE("DB insert creates schema and row") {
    // Ensure ./data exists inside the build dir
    std::filesystem::path dbp = std::filesystem::path("data") / "test_ci.db";
    std::filesystem::create_directories(dbp.parent_path());

    // Remove any previous DB
    if (std::filesystem::exists(dbp)) {
        std::filesystem::remove(dbp);
    }

    // Create/open DB and insert a test run
    db::Sqlite db(dbp.string());
    db.insert_game(
        "dice",
        /*seed*/ 123,
        /*sides*/ 6,
        /*bet_on*/ 6,
        /*payout*/ 5.0,
        /*wager*/ 1.0,
        /*trials*/ 1000,
        /*hits*/ 167,
        /*hit_rate*/ 0.167,
        /*total_bet*/ 1000.0,
        /*total_return*/ 835.0,
        /*net_profit*/ -165.0,
        /*ev*/ -0.165,
        /*roi*/ -0.165,
        /*variance*/ 1.0,
        /*std_err*/ 0.03,
        /*ci_lo*/ -0.22,
        /*ci_hi*/ -0.11,
        /*runtime_ms*/ 5
    );

    // Verify with raw sqlite3
    sqlite3* conn = nullptr;
    REQUIRE(sqlite3_open(dbp.string().c_str(), &conn) == SQLITE_OK);

    // Table exists?
    const char* schema_q =
        "SELECT name FROM sqlite_master WHERE type='table' AND name='games';";
    sqlite3_stmt* stmt = nullptr;
    REQUIRE(sqlite3_prepare_v2(conn, schema_q, -1, &stmt, nullptr) == SQLITE_OK);
    int rc = sqlite3_step(stmt);
    REQUIRE(rc == SQLITE_ROW);
    sqlite3_finalize(stmt);

    // Row exists?
    const char* count_q = "SELECT COUNT(*) FROM games;";
    REQUIRE(sqlite3_prepare_v2(conn, count_q, -1, &stmt, nullptr) == SQLITE_OK);
    rc = sqlite3_step(stmt);
    REQUIRE(rc == SQLITE_ROW);
    int count = sqlite3_column_int(stmt, 0);
    REQUIRE(count == 1);
    sqlite3_finalize(stmt);

    sqlite3_close(conn);
}
