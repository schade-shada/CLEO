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
  const auto keys = feistel::round_keys(base);  // made once, not once per index

  if (n == nsupers) {
    /* nsupers is a power of 4: every output is valid, so no compaction is needed */
    Kokkos::parallel_for(Kokkos::TeamThreadRange(team_member, n), [=](const size_t i) {
      idx(i) = static_cast<shuffle_idx_t>(feistel::bijection(i, keys, h));
    });
  } else {
    /* 1. b = f(i) for every i < n, stored after the first nsupers entries of idx.
    In its own loop so that each b is computed once (parallel_scan calls its lambda twice) */
    const auto outputs = viewd_shuffleidx(idx.data() + nsupers, n);  // b < n fits shuffle_idx_t
    // because max(shuffle_idx_t) + 1 is a power of 4 and nsupers <= it (see sdmmethods.hpp)
    Kokkos::parallel_for(Kokkos::TeamThreadRange(team_member, n), [=](const size_t i) {
      outputs(i) = static_cast<shuffle_idx_t>(feistel::bijection(i, keys, h));
    });
    team_member.team_barrier();

    /* 2. flag = (b < nsupers); exclusive prefix sum of flag gives where each valid b goes */
    Kokkos::parallel_scan(Kokkos::TeamThreadRange(team_member, n),
                          [=](const size_t i, size_t& pos, const bool final) {
                            const auto b = outputs(i);
                            const auto flag = size_t{b < nsupers};
                            if (final && flag) {
                              idx(pos) = b;
                            }
                            pos += flag;
                          });
  }
  team_member.team_barrier();  // synchronise threads
}
