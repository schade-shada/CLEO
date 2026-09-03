from condensation import Condensation
from workload import Workload

class Microphysics:

    def __init__(self, condensation):

        self.condensation = condensation

    def run_step(self, subt, n_sd_per_gbx, maxniters_newton_raphson):

        return self.condensation.run_step(
            n_sd_per_gbx,
            maxniters_newton_raphson=maxniters_newton_raphson,
        )

def sdm_microphysics(
    n_gbx,
    n_sd_per_gbx,
    microphysics,
    maxniters_newton_raphson,
):

    total_workload = Workload()

    # Corresponds conceptually to:
    #
    # TeamPolicy(ngbxs, team_size)
    #
    # One team = one gridbox, all executed in parallel on real hardware.
    # Every gridbox does identical work here, so instead of looping n_gbx
    # times we compute one gridbox's workload and scale it, which is what
    # the roofline model needs (total FLOPs/bytes, independent of ordering).

    gbx_workload = microphysics.run_step(
        subt=0,
        n_sd_per_gbx=n_sd_per_gbx,
        maxniters_newton_raphson=maxniters_newton_raphson,
    )

    total_workload.add(gbx_workload.scale(n_gbx))

    return total_workload

def run_step(
    t_mdl,
    t_mdl_next,
    n_gbx,
    n_sd_per_gbx,
    microphysics,
    condtstep,
    maxniters_newton_raphson,
):

    total_workload = Workload()

    # Every SDM step does identical work, so instead of looping and adding
    # per-step, compute the number of steps and scale one step's workload.
    n_steps = -(-(t_mdl_next - t_mdl) // condtstep)  # ceil division

    workload = sdm_microphysics(
        n_gbx=n_gbx,
        n_sd_per_gbx=n_sd_per_gbx,
        microphysics=microphysics,
        maxniters_newton_raphson=maxniters_newton_raphson,
    )

    total_workload.add(workload.scale(n_steps))

    return total_workload