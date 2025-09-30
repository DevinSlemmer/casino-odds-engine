#include <catch2/catch_test_macros.hpp>
#include "core/rng.hpp"
#include "games/dice.hpp"
#include <cmath>

// Your model: payout = net profit multiple; stake is returned on wins.
// Fair d6: payout=5 => EV≈0.
static double simulate_ev(int trials, unsigned long long seed,
                          int sides, int bet_on, double payout, double wager) {
    core::RNG rng(seed);
    games::Dice dice({sides, bet_on, payout});

    long long hits = 0;
    for (int t = 0; t < trials; ++t) {
        auto res = dice.play(rng);        // we trust res.roll is uniform in [1..sides]
        if (res.roll == bet_on) ++hits;
    }

    const double total_bet = wager * trials;
    const double total_return = (payout + 1.0) * wager * hits; // stake + profit on wins
    const double net_profit = total_return - total_bet;
    return net_profit / trials;
}

TEST_CASE("EV converges to theory for fair d6", "[ev]") {
    const int sides = 6, bet_on = 6;
    const double payout = 5.0; // net profit multiple (fair)
    const double wager = 1.0;

    // theory EV = wager * (payout/6 - 5/6) = 0 for payout=5
    const double ev_theory = 0.0;

    // A few seeds; moderate trials so CI is narrow but tests are fast
    for (unsigned long long seed : {1ULL, 42ULL, 2025ULL}) {
        double ev = simulate_ev(200000, seed, sides, bet_on, payout, wager);
        // 95% CI width is ~O(1/sqrt(N)); allow ~±0.02 for 200k trials
        REQUIRE(std::abs(ev - ev_theory) < 0.02);
    }
}
