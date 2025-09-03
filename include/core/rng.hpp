#pragma once
#include <cstdint>
#include <random>

namespace core {

// Simple, reproducible RNG wrapper (mt19937_64)
class RNG {
public:
  explicit RNG(std::uint64_t seed = 42) : eng_(seed) {}

  // Uniform int in [lo, hi]
  int uniform_int(int lo, int hi) {
    std::uniform_int_distribution<int> dist(lo, hi);
    return dist(eng_);
  }

  // Uniform double in [0,1)
  double uniform01() {
    std::uniform_real_distribution<double> dist(0.0, 1.0);
    return dist(eng_);
  }

private:
  std::mt19937_64 eng_;
};

} // namespace core
