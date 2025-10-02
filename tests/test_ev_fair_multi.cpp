#include <catch2/catch_all.hpp>
#include "core/rng.hpp"
#include "games/dice.hpp"
#include <cmath>

static double run_ev(unsigned long long seed, int trials, int sides, int bet_on, double payout) {
    core::RNG rng(seed);
    games::Dice dice({ sides, bet_on, payout });
    int hits = 0;
    for (int t = 0; t < trials; ++t) {
        auto r = dice.play(rng);
        if (r.roll == bet_on) ++hits;
    }
    const double wager = 1.0;
    const double total_bet = trials * wager;
    const double total_return = hits * payout * wager;   // gross return
    const double net_profit = total_return - total_bet;
    return net_profit / trials;                          // $/play
}

// Theoretical variance for one play (wager=1), mean=0 at payout=sides:
//   X = +(s-1) with prob 1/s,  X = -1 with prob (s-1)/s
//   Var(X) = E[X^2] = (1/s)*(s-1)^2 + (1 - 1/s)*1^2
static double per_play_variance(int sides) {
    const double s = static_cast<double>(sides);
    return (1.0 / s) * (s - 1) * (s - 1) + (1.0 - 1.0 / s) * 1.0;
}

TEST_CASE("EV approaches 0 for fair dice across several sides") {
    const int trials = 150000;                 // keep this fast for CI
    const double k_sigma = 3.0;                // 3×SE ~99.7% band
    const unsigned long long seed = 424242;

    for (int sides : {4, 6, 8, 10, 12}) {
        const int bet_on = sides;              // any face
        const double payout = static_cast<double>(sides); // FAIR under our model

        const double ev = run_ev(seed, trials, sides, bet_on, payout);

        const double var = per_play_variance(sides);
        const double se = std::sqrt(var / trials);

        // Require EV to lie within ±k_sigma * SE
        REQUIRE(std::fabs(ev) <= k_sigma * se);
    }
}
