#include <catch2/catch_all.hpp>
#include "core/rng.hpp"
#include "games/dice.hpp"

static double run_ev(unsigned long long seed, int trials, int sides, int bet_on, double payout, double wager) {
    core::RNG rng(seed);
    games::Dice dice({sides, bet_on, payout});

    double total_return = 0.0;
    for (int t = 0; t < trials; ++t) {
        auto r = dice.play(rng);
        if (r.roll == bet_on) total_return += payout * wager;
        else total_return += 0.0;
    }
    const double total_bet = wager * trials;
    const double net_profit = total_return - total_bet;
    return net_profit / trials; // $/play
}

TEST_CASE("EV scales linearly with wager; ROI constant") {
    const int trials = 100000;
    const int sides = 6;
    const int bet_on = 6;
    const double payout = 4.8; // slightly negative game

    const auto seed = 777ull;

    const double ev1 = run_ev(seed, trials, sides, bet_on, payout, 1.0);
    const double ev5 = run_ev(seed, trials, sides, bet_on, payout, 5.0);

    // EV ($/play) should scale ~5x; tolerate sampling noise
    REQUIRE( ev5 / 5.0 == Catch::Approx(ev1).margin(0.01) );

    // ROI = net_profit / total_bet → same RNG path & probabilities → near equal
    const double roi1 = ev1 / 1.0;  // EV $/play divided by wager
    const double roi5 = ev5 / 5.0;
    REQUIRE( roi5 == Catch::Approx(roi1).margin(0.01) );
}
