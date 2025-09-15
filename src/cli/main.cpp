#include <iostream>
#include <string>
#include <stdexcept>
#include "core/rng.hpp"
#include "games/dice.hpp"
#include <sstream>
#include "db/sqlite.hpp"
#include <filesystem>

struct Args {
    std::string game = "dice";
    int trials = 10000;
    unsigned long long seed = 42;
    int sides = 6;
    int bet_on = 6;
    double payout = 5.0;
    std::string db_path = "";   // NEW: path to SQLite database (optional)
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
        else if (s == "--db") { need(i); a.db_path = argv[++i]; }
        else if (s == "--help" || s == "-h") {
            std::cout <<
                "Usage: casino --game dice [--trials N] [--seed S] [--sides K] [--bet-on F] [--payout P]\n";
            std::exit(0);
        }
    }
    return a;
}

int main(int argc, char** argv) {
    try {
        Args args = parse(argc, argv);

        if (args.game != "dice") {
            std::cerr << "Only --game dice is implemented in Step 2.\n";
            return 1;
        }
        if (args.sides < 2 || args.bet_on < 1 || args.bet_on > args.sides || args.trials <= 0) {
            std::cerr << "Invalid parameters. Try: --sides >= 2, 1 <= --bet-on <= --sides, --trials > 0\n";
            return 2;
        }

        core::RNG rng(args.seed);
        games::Dice dice({ args.sides, args.bet_on, args.payout });

        long long hits = 0;
        double profit_sum = 0.0;

        for (int t = 0; t < args.trials; ++t) {
            auto res = dice.play(rng);
            if (res.roll == args.bet_on) ++hits;
            profit_sum += res.profit;
        }

        double hit_rate = static_cast<double>(hits) / args.trials;
        double ev = profit_sum / args.trials;

        std::cout << "Game: dice\n"
            << "Trials: " << args.trials << "\n"
            << "Seed: " << args.seed << "\n"
            << "Sides: " << args.sides << ", Bet on: " << args.bet_on
            << ", Payout: " << args.payout << "\n"
            << "Hit rate: " << hit_rate << "\n"
            << "EV per play: " << ev << "\n";


        if (!args.db_path.empty()) {
            // Ensure parent directory exists
            std::filesystem::path p(args.db_path);
            if (p.has_parent_path()) {
                std::error_code ec;
                std::filesystem::create_directories(p.parent_path(), ec); // no throw if fails
            }

            // Build params string
            std::ostringstream params;
            params << "sides=" << args.sides
                << ",bet_on=" << args.bet_on
                << ",payout=" << args.payout
                << ",seed=" << args.seed;

            // Insert into DB
            db::Sqlite db(args.db_path);
            db.insert_game("dice", params.str(), args.trials, (int)hits, hit_rate, ev);

            std::cout << "Saved results to " << std::filesystem::absolute(args.db_path).string() << "\n";
        }


        // For a fair-odds setup (payout = sides-1 when betting one face), EV 0
        return 0;

    }
    catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        return 3;
    }
}
