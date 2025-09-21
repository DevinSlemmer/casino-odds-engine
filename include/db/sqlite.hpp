// include/db/sqlite.hpp
#pragma once
#include <string>
#include <stdexcept>

struct sqlite3;

namespace db {

    class Sqlite {
    public:
        explicit Sqlite(const std::string& path);
        ~Sqlite();

        void exec(const std::string& sql);

        // NEW: explicit columns for run parameters
        void insert_game(const std::string& game_type,
            unsigned long long seed,
            int sides, int bet_on, double payout,
            int trials, int hits,
            double hit_rate, double ev);

    private:
        sqlite3* db_ = nullptr;
    };

} // namespace db
