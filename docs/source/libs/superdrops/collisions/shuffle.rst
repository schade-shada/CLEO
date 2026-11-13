Parallel Superdroplet Shuffling Algorithm
=========================================

Header file: ``<libs/superdrops/collisions/shuffle.hpp>``
`[source] <https://github.com/yoctoyotta1024/CLEO/blob/main/libs/superdrops/collisions/shuffle.hpp>`_

The order of the superdroplets in a gridbox is shuffled in parallel with a Feistel network
bijection and compaction (Algorithm 1 of Mitchell et al., "Bandwidth-Optimal Random Shuffling
for GPUs"). The superdroplets are not moved; the shuffle writes an array of indices into
team scratch memory and pair ``jj`` of the collisions is ``supers(idx(2jj)), supers(idx(2jj+1))``.

.. doxygenfunction:: shuffle_indices
   :project: superdrops

.. doxygenfunction:: shuffle_idx_scratch
   :project: superdrops

.. doxygenfunction:: shuffle_scratch_size
   :project: superdrops

.. doxygenfunction:: shuffle_scratch_bytes
   :project: superdrops

Header file: ``<libs/superdrops/collisions/feistel.hpp>``
`[source] <https://github.com/yoctoyotta1024/CLEO/blob/main/libs/superdrops/collisions/feistel.hpp>`_

.. doxygentypedef:: feistel::RoundKeys
   :project: superdrops

.. doxygenfunction:: feistel::round_keys
   :project: superdrops

.. doxygenfunction:: feistel::bijection
   :project: superdrops

.. doxygenfunction:: feistel::mix
   :project: superdrops
