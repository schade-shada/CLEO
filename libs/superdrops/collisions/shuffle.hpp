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
 * @brief Number of shuffle indices in team scratch memory for a gridbox with nsupers
 * super-droplets: nsupers for the permutation plus n = 4^h >= nsupers for the Feistel outputs
 * before compaction. Never smaller for a larger nsupers, so the size for the largest gridbox
 * fits every gridbox.
 */
KOKKOS_INLINE_FUNCTION size_t shuffle_scratch_size(const size_t nsupers) {
  return nsupers + (size_t{1} << (2 * feistel::half_bits(nsupers)));
}

/**
 * @brief Number of bytes of team scratch memory needed to shuffle a gridbox with
 * nsupers super-droplets.
 */
KOKKOS_INLINE_FUNCTION size_t shuffle_scratch_bytes(const size_t nsupers) {
  return viewd_shuffleidx::shmem_size(shuffle_scratch_size(nsupers));
}

/**
 * @brief Returns a view of shuffle_scratch_size(nsupers) shuffle indices in team scratch
 * memory. After shuffle_indices, its first nsupers entries are the shuffled order of the
 * super-droplets; the rest is workspace.
 *
 * Uses level 0 scratch if it was requested at launch (see sdmmethods.hpp), otherwise level 1.
 * Works on a copy of the team's scratch space so every call returns the same memory,
 * which is safe because the indices are only needed during one call of do_collisions.
 * Aborts if neither level has enough scratch memory.
 */
KOKKOS_INLINE_FUNCTION viewd_shuffleidx shuffle_idx_scratch(const TeamMember& team_member,
                                                            const size_t nsupers) {
  const auto size = shuffle_scratch_size(nsupers);
  const auto bytes = shuffle_scratch_bytes(nsupers);
  for (int level = 0; level < 2; ++level) {
    auto scratch = team_member.team_scratch(level);  // copy: does not use up the team's scratch
    void* ptr = scratch.get_shmem_aligned(bytes, alignof(shuffle_idx_t), level);
    if (ptr != nullptr) {
      return viewd_shuffleidx(static_cast<shuffle_idx_t*>(ptr), size);
    }
  }
  Kokkos::abort("not enough team scratch memory for the shuffle indices of a gridbox");
  return viewd_shuffleidx{};
}

/**
 * @brief Writes a random permutation of {0, ..., nsupers - 1} into idx, in parallel over the team.
 *
 * Pads nsupers to n = 4^h >= nsupers and evaluates the Feistel bijection b = f(i) for every
 * i < n into idx(nsupers + i). It then keeps the b < nsupers and compacts them into
 * idx(0 .. nsupers - 1), in order of i, with an exclusive prefix sum. The bijection is
 * evaluated in its own loop because a team parallel_scan calls its lambda twice per i.
 * When nsupers is a power of 4, no padding is needed and idx(i) = f(i) directly.
 *
 * @param team_member The Kokkos team member.
 * @param idx View of at least shuffle_scratch_size(nsupers) indices (e.g. from
 * shuffle_idx_scratch). On return its first nsupers entries are the permutation.
 * @param nsupers Number of super-droplets to shuffle.
 * @param base Random 64-bit number from which the Feistel round keys are made. It must be the
 * same for every thread in the team and new for every shuffle (e.g. drawn from a GenRandomPool
 * in a Kokkos::single, see DoCollisions::do_collisions).
 */
KOKKOS_FUNCTION void shuffle_indices(const TeamMember& team_member, const viewd_shuffleidx idx,
                                     const size_t nsupers, const uint64_t base);

#endif  // LIBS_SUPERDROPS_COLLISIONS_SHUFFLE_HPP_
