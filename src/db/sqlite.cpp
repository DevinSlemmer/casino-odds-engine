#include "db/sqlite.hpp"
#include <sqlite3.h>
#include <stdexcept>

namespace db {

static void throwIf(int rc, sqlite3* db) {
  if (rc != SQLITE_OK && rc != SQLITE_DONE && rc != SQLITE_ROW) {
    throw std::runtime_error(sqlite3_errmsg(db));
  }
}

Sqlite::Sqlite(const std::string& path) {
  if (sqlite3_open(path.c_str(), &db_) != SQLITE_OK) {
    throw std::runtime_error("Failed to open DB: " + path);
  }
  exec("CREATE TABLE IF NOT EXISTS games ("
       "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
       "  created_at TEXT DEFAULT CURRENT_TIMESTAMP,"
       "  type TEXT NOT NULL,"
       "  params_json TEXT NOT NULL,"
       "  trials INTEGER NOT NULL,"
       "  hits INTEGER NOT NULL,"
       "  hit_rate REAL NOT NULL,"
       "  ev REAL NOT NULL"
       ");");
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

void Sqlite::insert_game(const std::string& game_type,
                         const std::string& params_json,
                         int trials, int hits,
                         double hit_rate, double ev) {
  const char* sql =
    "INSERT INTO games(type, params_json, trials, hits, hit_rate, ev) "
    "VALUES(?,?,?,?,?,?);";

  sqlite3_stmt* stmt = nullptr;
  throwIf(sqlite3_prepare_v2(db_, sql, -1, &stmt, nullptr), db_);
  throwIf(sqlite3_bind_text (stmt, 1, game_type.c_str(), -1, SQLITE_TRANSIENT), db_);
  throwIf(sqlite3_bind_text (stmt, 2, params_json.c_str(), -1, SQLITE_TRANSIENT), db_);
  throwIf(sqlite3_bind_int  (stmt, 3, trials), db_);
  throwIf(sqlite3_bind_int  (stmt, 4, hits), db_);
  throwIf(sqlite3_bind_double(stmt, 5, hit_rate), db_);
  throwIf(sqlite3_bind_double(stmt, 6, ev), db_);
  throwIf(sqlite3_step(stmt), db_);
  sqlite3_finalize(stmt);
}

} // namespace db
