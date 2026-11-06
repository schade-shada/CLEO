/*
 * Copyright (c) 2024 MPI-M, Clara Bayley
 *
 * ----- CLEO -----
 * File: shuffle.cpp
 * Project: collisions
 * Created Date: Thursday 6th March 2025
 * Author: Clara Bayley (CB)
 * Additional Contributors: Harshada Balasubramanian
 * -----
 * License: BSD 3-Clause "New" or "Revised" License
 * https://opensource.org/licenses/BSD-3-Clause
 * -----
 * File Description:
 * Implementation of the parallel Feistel shuffle of super-droplet indices (see shuffle.hpp).
 */

#include "./shuffle.hpp"

KOKKOS_FUNCTION void shuffle_indices(const TeamMember& team_member, const viewd_shuffleidx idx,
                                     const size_t nsupers, const uint64_t base) {
  if (nsupers == 0) {
    return;
  }

  const auto h = feistel::half_bits(nsupers);
  const auto n = size_t{1} << (2 * h);  // padded domain, n = 4^h >= nsupers

  if (n == nsupers) {
    /* nsupers is a power of 4: every output is valid, so no compaction is needed */
    Kokkos::parallel_for(Kokkos::TeamThreadRange(team_member, n), [=](const size_t i) {
      idx(i) = static_cast<shuffle_idx_t>(feistel::bijection(i, base, h));
    });
  } else {
    /* flag = (b < nsupers); exclusive prefix sum of flag gives where each valid b goes */
    Kokkos::parallel_scan(Kokkos::TeamThreadRange(team_member, n),
                          [=](const size_t i, size_t& pos, const bool final) {
                            const auto b = feistel::bijection(i, base, h);
                            const auto flag = size_t{b < nsupers};
                            if (final && flag) {
                              idx(pos) = static_cast<shuffle_idx_t>(b);
                            }
                            pos += flag;
                          });
  }
  team_member.team_barrier();  // synchronise threads
}
