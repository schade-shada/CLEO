from condensation import Condensation
from workload import Workload

class Microphysics:

    def __init__(self, condensation):

        self.condensation = condensation

    def run_step(self, subt, n_sd_per_gbx):

        return self.condensation.run_step(
            n_sd_per_gbx
        )

def sdm_microphysics(
    n_gbx,
    n_sd_per_gbx,
    microphysics,
):

    total_workload = Workload()

    # Corresponds conceptually to:
    #
    # TeamPolicy(ngbxs, team_size)
    #
    # One team = one gridbox

    for _ in range(n_gbx):

        gbx_workload = microphysics.run_step(
            subt=0,
            n_sd_per_gbx=n_sd_per_gbx,
        )

        total_workload.add(gbx_workload)

    return total_workload

def run_step(
    t_mdl,
    t_mdl_next,
    n_gbx,
    n_sd_per_gbx,
    microphysics,
):

    total_workload = Workload()

    t_sdm = t_mdl

    while t_sdm < t_mdl_next:

        t_sdm_next = t_sdm + 1

        workload = sdm_microphysics(
            n_gbx=n_gbx,
            n_sd_per_gbx=n_sd_per_gbx,
            microphysics=microphysics,
        )

        total_workload.add(workload)

        t_sdm = t_sdm_next

    return total_workload