// tests/test_dice_math.cpp
#include <catch2/catch_test_macros.hpp>
#include "core/rng.hpp"
#include "games/dice.hpp"
#include <cmath>

TEST_CASE("Closed-form EV for fair d6 payout=5, wager=1 is -1/6") {
    // Profit per play: +4 on hit, -1 otherwise
    // EV = (1/6)*4 + (5/6)*(-1) = -1/6
    double ev = (1.0/6.0)*4.0 + (5.0/6.0)*(-1.0);
    REQUIRE(std::abs(ev + 1.0/6.0) < 1e-12);
}

TEST_CASE("Monte-Carlo EV for fair d6 converges near theory") {
    core::RNG rng(424242);
    games::Dice d({6, 6, 5.0}); // sides=6, bet_on=6, payout=5
    const int N = 200000;
    double sum = 0.0;
    for (int i = 0; i < N; ++i) {
        auto r = d.play(rng);
        double profit = (r.roll == 6) ? 4.0 : -1.0;
        sum += profit;
    }
    double ev_mc = sum / N;
    double ev_theory = -1.0/6.0;
    // 200k trials -> tight tolerance
    REQUIRE(std::abs(ev_mc - ev_theory) < 0.01);
}
