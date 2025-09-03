#include <catch2/catch_all.hpp>
#include "core/rng.hpp"
#include "games/dice.hpp"

TEST_CASE("Dice EV ~ 0 for fair payout") {
    core::RNG rng(7);
    games::Dice dice({6, 6, 5.0});
    int N = 120000;
    double sum = 0.0;
    for (int i = 0; i < N; ++i) sum += dice.play(rng).profit;
    double ev = sum / N;
    REQUIRE(std::abs(ev) < 0.05); // loose bound due to randomness
}
