/*
 * Copyright (c) 2024 MPI-M, Clara Bayley
 *
 * ----- CLEO -----
 * File: feistel.hpp
 * Project: collisions
 * Created Date: Thursday 5th November 2026
 * Author: Harshada Balasubramanian
 * Additional Contributors:
 * -----
 * License: BSD 3-Clause "New" or "Revised" License
 * https://opensource.org/licenses/BSD-3-Clause
 * -----
 * File Description:
 * Feistel network bijection on {0, ..., 4^h - 1} used for the parallel shuffle of
 * super-droplets (see Mitchell et al., "Bandwidth-Optimal Random Shuffling for GPUs").
 */

#ifndef LIBS_SUPERDROPS_COLLISIONS_FEISTEL_HPP_
#define LIBS_SUPERDROPS_COLLISIONS_FEISTEL_HPP_

#include <Kokkos_Core.hpp>
#include <cstdint>

namespace feistel {

/** number of Feistel rounds (16 passed the order, position, pair and step tests) */
constexpr unsigned int NROUNDS = 16;

/**
 * @brief Scrambles the bits of a 64-bit number (splitmix64 finaliser).
 */
KOKKOS_INLINE_FUNCTION uint64_t mix(uint64_t x) {
  x = (x ^ (x >> 30)) * uint64_t{0xBF58476D1CE4E5B9};
  x = (x ^ (x >> 27)) * uint64_t{0x94D049BB133111EB};
  return x ^ (x >> 31);
}

/**
 * @brief Number of bits in each half, h, so that the padded domain n = 4^h >= m (and h >= 1).
 */
KOKKOS_INLINE_FUNCTION unsigned int half_bits(const uint64_t m) {
  auto h = 1u;
  while ((uint64_t{1} << (2 * h)) < m) {
    ++h;
  }
  return h;
}

/** the NROUNDS round keys of one shuffle */
using RoundKeys = Kokkos::Array<uint64_t, NROUNDS>;

/**
 * @brief Makes the round keys k_r = mix(base + r) once, so that the bijection does not
 * recompute them for every index.
 *
 * @param base Random 64-bit number from which the round keys are made.
 * @return The NROUNDS round keys.
 */
KOKKOS_INLINE_FUNCTION RoundKeys round_keys(const uint64_t base) {
  auto keys = RoundKeys{};
  for (unsigned int r = 0; r < NROUNDS; ++r) {
    keys[r] = mix(base + r);
  }
  return keys;
}

/**
 * @brief Feistel bijection on {0, ..., 4^h - 1}.
 *
 * Splits i into left and right halves of h bits each and applies NROUNDS rounds of
 * (L, R) -> (R, L ^ F(R, k_r)) with round function F(R, k) = mix(R ^ k) & mask.
 *
 * @param i Input index, i < 4^h.
 * @param keys Round keys from round_keys(base).
 * @param h Number of bits in each half.
 * @return Output index, also < 4^h. Different i always give different outputs.
 */
KOKKOS_INLINE_FUNCTION uint64_t bijection(const uint64_t i, const RoundKeys& keys,
                                          const unsigned int h) {
  const auto mask = (uint64_t{1} << h) - 1;
  auto L = i >> h;
  auto R = i & mask;
  for (unsigned int r = 0; r < NROUNDS; ++r) {
    const auto newR = L ^ (mix(R ^ keys[r]) & mask);
    L = R;
    R = newR;
  }
  return (L << h) | R;
}

}  // namespace feistel

#endif  // LIBS_SUPERDROPS_COLLISIONS_FEISTEL_HPP_
