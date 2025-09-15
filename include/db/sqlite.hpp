#pragma once
#include <string>
#include <stdexcept>

struct sqlite3; // forward declaration

namespace db {

class Sqlite {
public:
  explicit Sqlite(const std::string& path);
  ~Sqlite();

  void exec(const std::string& sql);
  void insert_game(const std::string& game_type,
                   const std::string& params_json,
                   int trials, int hits,
                   double hit_rate, double ev);

private:
  sqlite3* db_ = nullptr;
};

} // namespace db
