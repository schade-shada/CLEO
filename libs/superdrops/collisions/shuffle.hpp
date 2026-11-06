/*
 * Copyright (c) 2024 MPI-M, Clara Bayley
 *
 * ----- CLEO -----
 * File: shuffle.hpp
 * Project: collisions
 * Created Date: Thursday 6th March 2025
 * Author: Clara Bayley (CB)
 * Additional Contributors: Harshada Balasubramanian
 * -----
 * License: BSD 3-Clause "New" or "Revised" License
 * https://opensource.org/licenses/BSD-3-Clause
 * -----
 * File Description:
 * Parallel random shuffle of the order of super-droplets in a gridbox using a Feistel
 * network bijection with compaction (Algorithm 1 of Mitchell et al., "Bandwidth-Optimal
 * Random Shuffling for GPUs"). The super-droplets themselves are not moved: the shuffle
 * writes an array of indices into the gridbox's view of super-droplets.
 */

#ifndef LIBS_SUPERDROPS_COLLISIONS_SHUFFLE_HPP_
#define LIBS_SUPERDROPS_COLLISIONS_SHUFFLE_HPP_

#include <Kokkos_Core.hpp>
#include <cstdint>

#include "../kokkosaliases_sd.hpp"
#include "./feistel.hpp"

/**
 * @brief Number of bytes of team scratch memory needed to shuffle a gridbox with
 * nsupers super-droplets.
 */
KOKKOS_INLINE_FUNCTION size_t shuffle_scratch_bytes(const size_t nsupers) {
  return viewd_shuffleidx::shmem_size(nsupers);
}

/**
 * @brief Returns a view of nsupers shuffle indices in team scratch memory.
 *
 * Uses level 0 scratch if it was requested at launch (see sdmmethods.hpp), otherwise level 1.
 * Works on a copy of the team's scratch space so every call returns the same memory,
 * which is safe because the indices are only needed during one call of do_collisions.
 * Aborts if neither level has enough scratch memory.
 */
KOKKOS_INLINE_FUNCTION viewd_shuffleidx shuffle_idx_scratch(const TeamMember& team_member,
                                                            const size_t nsupers) {
  const auto bytes = shuffle_scratch_bytes(nsupers);
  for (int level = 0; level < 2; ++level) {
    auto scratch = team_member.team_scratch(level);  // copy: does not use up the team's scratch
    void* ptr = scratch.get_shmem_aligned(bytes, alignof(shuffle_idx_t), level);
    if (ptr != nullptr) {
      return viewd_shuffleidx(static_cast<shuffle_idx_t*>(ptr), nsupers);
    }
  }
  Kokkos::abort("not enough team scratch memory for the shuffle indices of a gridbox");
  return viewd_shuffleidx{};
}

/**
 * @brief Writes a random permutation of {0, ..., nsupers - 1} into idx, in parallel over the team.
 *
 * Pads nsupers to n = 4^h >= nsupers, evaluates the Feistel bijection b = f(i) for every
 * i < n, keeps the b < nsupers and compacts them in order of i with an exclusive prefix
 * sum. When nsupers is a power of 4, no padding is needed and the scan is skipped.
 *
 * @param team_member The Kokkos team member.
 * @param idx View of at least nsupers indices (e.g. from shuffle_idx_scratch).
 * @param nsupers Number of super-droplets to shuffle.
 * @param base Random 64-bit number from which the Feistel round keys are made. It must be the
 * same for every thread in the team and new for every shuffle (e.g. drawn from a GenRandomPool
 * in a Kokkos::single, see DoCollisions::do_collisions).
 */
KOKKOS_FUNCTION void shuffle_indices(const TeamMember& team_member, const viewd_shuffleidx idx,
                                     const size_t nsupers, const uint64_t base);

#endif  // LIBS_SUPERDROPS_COLLISIONS_SHUFFLE_HPP_
