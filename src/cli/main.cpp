#include <iostream>
#include <string>
#include <stdexcept>
#include <filesystem>
#include <chrono>
#include <cmath>

#include "core/rng.hpp"
#include "games/dice.hpp"
#include "db/sqlite.hpp"

struct Args {
    std::string game = "dice";
    int trials = 10000;
    unsigned long long seed = 42;
    int sides = 6;
    int bet_on = 6;
    double payout = 5.0;
    double wager = 1.0;           // NEW
    std::string db_path = "";
};

Args parse(int argc, char** argv) {
    Args a;
    auto need = [&](int i) { if (i + 1 >= argc) throw std::runtime_error("Missing value for " + std::string(argv[i])); };
    for (int i = 1; i < argc; ++i) {
        std::string s = argv[i];
        if (s == "--game") { need(i); a.game = argv[++i]; }
        else if (s == "--trials") { need(i); a.trials = std::stoi(argv[++i]); }
        else if (s == "--seed") { need(i); a.seed = std::stoull(argv[++i]); }
        else if (s == "--sides") { need(i); a.sides = std::stoi(argv[++i]); }
        else if (s == "--bet-on") { need(i); a.bet_on = std::stoi(argv[++i]); }
        else if (s == "--payout") { need(i); a.payout = std::stod(argv[++i]); }
        else if (s == "--wager") { need(i); a.wager = std::stod(argv[++i]); }  // NEW
        else if (s == "--db") { need(i); a.db_path = argv[++i]; }
        else if (s == "--help" || s == "-h") {
            std::cout << "Usage: casino --game dice "
                "[--trials N] [--seed S] [--sides K] [--bet-on F] [--payout P] [--wager $] [--db PATH]\n";
            std::exit(0);
        }
    }
    return a;
}

int main(int argc, char** argv) {
    try {
        Args args = parse(argc, argv);

        if (args.game != "dice") { std::cerr << "Only --game dice implemented.\n"; return 1; }
        if (args.sides < 2 || args.bet_on < 1 || args.bet_on > args.sides || args.trials <= 0 || args.wager <= 0.0) {
            std::cerr << "Invalid parameters.\n";
            return 2;
        }

        auto t0 = std::chrono::steady_clock::now();

        core::RNG rng(args.seed);
        games::Dice dice({ args.sides, args.bet_on, args.payout });

        long long hits = 0;
        double total_return = 0.0;

        // Welford for variance of per-play profit (in dollars)
        double mean = 0.0, M2 = 0.0;

        for (int t = 1; t <= args.trials; ++t) {
            auto res = dice.play(rng);

            double profit_t;
            if (res.roll == args.bet_on) {
                ++hits;
                double win = (args.payout + 1) * args.wager;     // winnings returned
                total_return += win;
                profit_t = win - args.wager;                // profit that play
            }
            else {
                total_return += 0.0;
                profit_t = -args.wager;
            }

            // Welford update
            double delta = profit_t - mean;
            mean += delta / t;
            M2 += delta * (profit_t - mean);
        }

        double hit_rate = static_cast<double>(hits) / args.trials;
        double total_bet = args.wager * args.trials;
        double net_profit = total_return - total_bet;

        double ev = net_profit / args.trials;            // $ per play
        double variance = (args.trials > 1) ? (M2 / (args.trials - 1)) : 0.0;  // sample variance of $/play
        double std_err = std::sqrt(variance / args.trials);
        double ci_lo = ev - 1.96 * std_err;
        double ci_hi = ev + 1.96 * std_err;
        double roi = (total_bet != 0.0) ? (net_profit / total_bet) : 0.0;

        auto t1 = std::chrono::steady_clock::now();
        long long runtime_ms = std::chrono::duration_cast<std::chrono::milliseconds>(t1 - t0).count();

        std::cout << "Game: dice\n"
            << "Trials: " << args.trials << "\n"
            << "Seed: " << args.seed << "\n"
            << "Sides: " << args.sides << ", Bet on: " << args.bet_on
            << ", Payout: " << args.payout << ", Wager: " << args.wager << "\n"
            << "Hit rate: " << hit_rate << "\n"
            << "EV ($/play): " << ev << "  95% CI: [" << ci_lo << ", " << ci_hi << "]\n"
            << "Total bet: " << total_bet << "  Total return: " << total_return
            << "  Net profit: " << net_profit << "  ROI: " << roi << "\n";

        if (!args.db_path.empty()) {
            std::filesystem::path p(args.db_path);
            if (p.has_parent_path()) {
                std::error_code ec;
                std::filesystem::create_directories(p.parent_path(), ec);
            }

            db::Sqlite db(args.db_path);
            db.insert_game(
                "dice",
                args.seed,
                args.sides, args.bet_on, args.payout, args.wager,
                args.trials, static_cast<int>(hits), hit_rate,
                total_bet, total_return, net_profit,
                ev, roi,
                variance, std_err, ci_lo, ci_hi,
                runtime_ms
            );
            std::cout << "Saved to " << std::filesystem::absolute(args.db_path).string() << "\n";
        }


        return 0;
    }
    catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        return 3;
    }
}

//Adding a comment to test if the commit actually worked
