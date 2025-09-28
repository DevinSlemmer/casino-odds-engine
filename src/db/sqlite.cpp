#include "db/sqlite.hpp"
#include <sqlite3.h>
#include <stdexcept>
#include <string>

namespace db {

    static void throwIf(int rc, sqlite3* db) {
        if (rc != SQLITE_OK && rc != SQLITE_DONE && rc != SQLITE_ROW)
            throw std::runtime_error(sqlite3_errmsg(db));
    }

    Sqlite::Sqlite(const std::string& path) {
        if (sqlite3_open(path.c_str(), &db_) != SQLITE_OK) {
            throw std::runtime_error("Failed to open DB: " + path);
        }

        exec(
            "CREATE TABLE IF NOT EXISTS games ("
            "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "  created_at TEXT DEFAULT CURRENT_TIMESTAMP,"
            "  type TEXT NOT NULL,"
            "  seed INTEGER NOT NULL,"
            "  sides INTEGER NOT NULL,"
            "  bet_on INTEGER NOT NULL,"
            "  payout REAL NOT NULL,"
            "  wager REAL NOT NULL,"
            "  trials INTEGER NOT NULL,"
            "  hits INTEGER NOT NULL,"
            "  hit_rate REAL NOT NULL,"
            "  total_bet REAL NOT NULL,"
            "  total_return REAL NOT NULL,"
            "  net_profit REAL NOT NULL,"
            "  ev REAL NOT NULL,"
            "  roi REAL NOT NULL,"
            "  variance REAL NOT NULL,"
            "  std_err REAL NOT NULL,"
            "  ci_lo REAL NOT NULL,"
            "  ci_hi REAL NOT NULL,"
            "  runtime_ms INTEGER NOT NULL"
            ");"
        );
    }

    Sqlite::~Sqlite() {
        if (db_) sqlite3_close(db_);
    }

    void Sqlite::exec(const std::string& sql) {
        char* err = nullptr;
        int rc = sqlite3_exec(db_, sql.c_str(), nullptr, nullptr, &err);
        if (rc != SQLITE_OK) {
            std::string msg = err ? err : "unknown sqlite error";
            sqlite3_free(err);
            throw std::runtime_error(msg);
        }
    }

    void Sqlite::insert_game(
        const std::string& type,
        unsigned long long seed,
        int sides, int bet_on, double payout, double wager,
        int trials, int hits, double hit_rate,
        double total_bet, double total_return, double net_profit,
        double ev, double roi,
        double variance, double std_err, double ci_lo, double ci_hi,
        long long runtime_ms
    ) {
        const char* sql =
            "INSERT INTO games("
            " type, seed, sides, bet_on, payout, wager,"
            " trials, hits, hit_rate,"
            " total_bet, total_return, net_profit,"
            " ev, roi,"
            " variance, std_err, ci_lo, ci_hi,"
            " runtime_ms"
            ") VALUES (?,?,?,?,?, ?, ?,?,?, ?, ?,?, ?, ?, ?,?,?,?, ?);";

        sqlite3_stmt* st = nullptr;
        throwIf(sqlite3_prepare_v2(db_, sql, -1, &st, nullptr), db_);

        int i = 1;
        throwIf(sqlite3_bind_text(st, i++, type.c_str(), -1, SQLITE_TRANSIENT), db_);
        throwIf(sqlite3_bind_int64(st, i++, static_cast<sqlite3_int64>(seed)), db_);
        throwIf(sqlite3_bind_int(st, i++, sides), db_);
        throwIf(sqlite3_bind_int(st, i++, bet_on), db_);
        throwIf(sqlite3_bind_double(st, i++, payout), db_);
        throwIf(sqlite3_bind_double(st, i++, wager), db_);

        throwIf(sqlite3_bind_int(st, i++, trials), db_);
        throwIf(sqlite3_bind_int(st, i++, hits), db_);
        throwIf(sqlite3_bind_double(st, i++, hit_rate), db_);

        throwIf(sqlite3_bind_double(st, i++, total_bet), db_);
        throwIf(sqlite3_bind_double(st, i++, total_return), db_);
        throwIf(sqlite3_bind_double(st, i++, net_profit), db_);

        throwIf(sqlite3_bind_double(st, i++, ev), db_);
        throwIf(sqlite3_bind_double(st, i++, roi), db_);

        throwIf(sqlite3_bind_double(st, i++, variance), db_);
        throwIf(sqlite3_bind_double(st, i++, std_err), db_);
        throwIf(sqlite3_bind_double(st, i++, ci_lo), db_);
        throwIf(sqlite3_bind_double(st, i++, ci_hi), db_);

        throwIf(sqlite3_bind_int64(st, i++, static_cast<sqlite3_int64>(runtime_ms)), db_);

        throwIf(sqlite3_step(st), db_);
        sqlite3_finalize(st);
    }

} // namespace db
