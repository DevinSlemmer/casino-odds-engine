#include <catch2/catch_test_macros.hpp>
#include "core/rng.hpp"
#include "games/dice.hpp"

// Helper: roll `n` times and collect counts for faces [1..sides]
static std::vector<int> roll_counts(unsigned long long seed, int sides, int bet_on, int n) {
    core::RNG rng(seed);
    games::Dice dice({ sides, bet_on, /*payout*/5.0 }); // payout unused for roll distribution
    std::vector<int> cnt(sides + 1, 0);
    for (int i = 0; i < n; ++i) {
        auto res = dice.play(rng);
        REQUIRE(res.roll >= 1);
        REQUIRE(res.roll <= sides);
        cnt[res.roll] += 1;
    }
    return cnt;
}

TEST_CASE("Dice rolls are reproducible with the same seed", "[rng][dice]") {
    const int sides = 6;
    const int bet_on = 6; // irrelevant to the roll distribution
    const int N = 1000;

    auto a = roll_counts(/*seed*/123, sides, bet_on, N);
    auto b = roll_counts(/*seed*/123, sides, bet_on, N);
    auto c = roll_counts(/*seed*/42, sides, bet_on, N);

    // Same seed => identical counts
    REQUIRE(a == b);
    // Different seed => extremely likely different
    bool any_diff = false;
    for (int f = 1; f <= sides; ++f) {
        if (a[f] != c[f]) { any_diff = true; break; }
    }
    REQUIRE(any_diff);
}

TEST_CASE("Dice rolls are roughly uniform over faces", "[rng][dice]") {
    const int sides = 6;
    const int bet_on = 6; // irrelevant
    const int N = 60000;  // ~10k expected per face

    auto counts = roll_counts(/*seed*/2025, sides, bet_on, N);
    const double expected = static_cast<double>(N) / sides;
    const double tol = 0.05; // ±5%

    for (int face = 1; face <= sides; ++face) {
        REQUIRE(counts[face] > (1.0 - tol) * expected);
        REQUIRE(counts[face] < (1.0 + tol) * expected);
    }
}
