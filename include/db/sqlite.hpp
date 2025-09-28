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

        // v3 insert: explicit params + financial + stats
        void insert_game(
            const std::string& type,
            unsigned long long seed,
            int sides, int bet_on, double payout, double wager,
            int trials, int hits, double hit_rate,
            double total_bet, double total_return, double net_profit,
            double ev, double roi,
            double variance, double std_err, double ci_lo, double ci_hi,
            long long runtime_ms
        );

    private:
        sqlite3* db_ = nullptr;
    };

} // namespace db
