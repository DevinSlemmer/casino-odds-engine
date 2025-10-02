#include <catch2/catch_all.hpp>
#include "core/rng.hpp"
#include "games/dice.hpp"

static double run_ev(unsigned long long seed, int trials, int sides, int bet_on, double payout) {
    core::RNG rng(seed);
    games::Dice dice({sides, bet_on, payout});
    int hits = 0;
    for (int t = 0; t < trials; ++t) {
        auto r = dice.play(rng);
        if (r.roll == bet_on) ++hits;
    }
    const double total_bet = trials * 1.0;
    const double total_return = hits * payout;
    const double net_profit = total_return - total_bet;
    return net_profit / trials; // $/play
}

TEST_CASE("EV approaches 0 for fair dice across several sides") {
    const int trials = 150000;
    const unsigned long long seed = 424242;

    for (int sides : {4, 6, 8, 10, 12}) {
        const int bet_on = sides;         // any face
        const double payout = sides - 1;  // fair
        const double ev = run_ev(seed, trials, sides, bet_on, payout);
        REQUIRE( ev == Catch::Approx(0.0).margin(0.01) );
    }
}
