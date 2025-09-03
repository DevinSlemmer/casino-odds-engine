#pragma once
#include <cstdint>

namespace games {

struct DiceParams {
  int sides   = 6;    // e.g., 6-sided die
  int bet_on  = 6;    // face we're betting on
  double payout = 5;  // profit if we hit; lose 1 otherwise
};

struct DiceResult {
  int roll;
  double profit; // +payout if hit, otherwise -1
};

class Dice {
public:
  explicit Dice(DiceParams p) : p_(p) {}

  template <class RNG>
  DiceResult play(RNG& rng) const {
    int r = rng.uniform_int(1, p_.sides);
    double profit = (r == p_.bet_on) ? p_.payout : -1.0;
    return {r, profit};
  }

  const DiceParams& params() const { return p_; }

private:
  DiceParams p_;
};

} // namespace games
