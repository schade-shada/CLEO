from workload import Workload

class Condensation:

    def run_step(self, n_sd_per_gbx):
        """
        Workload corresponding to one condensation call
        for one gridbox.
        """

        workload = Workload()

        workload.add(
            self.superdroplets_change(n_sd_per_gbx)
        )

        workload.add(
            self.effect_on_thermodynamic_state()
        )

        return workload

    def superdroplets_change(self, n_sd_per_gbx):

        workload = Workload()

        # ----------------------------------------------------
        # These are calculated once per gridbox
        # ----------------------------------------------------

        workload.add(
            self.saturation_pressure()
        )

        workload.add(
            self.supersaturation_ratio()
        )

        workload.add(
            self.diffusion_factor()
        )

        # ----------------------------------------------------
        # This is executed once per superdroplet
        # ----------------------------------------------------

        for _ in range(n_sd_per_gbx):

            workload.add(
                self.superdrop_mass_change()
            )

        return workload

    def saturation_pressure(self):

        workload = Workload()

        # psat = PREF * exp(A * (T - TREF) / (T - B)) / P0
        # Roughly: one temperature scaling, two subtractions, one division,
        # one exponential, and a couple of multiplications/divisions for the
        # prefactor and normalisation.
        workload.add_operation("*", 3)
        workload.add_operation("-", 2)
        workload.add_operation("/", 2)
        workload.add_operation("exp", 1)

        # temperature read
        workload.bytes_read += 8

        return workload

    def supersaturation_ratio(self):

        workload = Workload()

        # s_ratio = (press * qvap) / ((Mr_ratio + qvap) * psat)
        workload.add_operation("*", 2)
        workload.add_operation("+", 1)
        workload.add_operation("/", 1)

        # temperature and pressure read
        workload.bytes_read += 16

        return workload

    def diffusion_factor(self):

        workload = Workload()

        # This is the largest per-gridbox term. It includes:
        # - temperature/pressure scaling
        # - polynomial-like terms in T and P
        # - two diffusion-factor contributions
        # - a final combination into fkl + fdl
        workload.add_operation("*", 8)
        workload.add_operation("+", 5)
        workload.add_operation("-", 2)
        workload.add_operation("/", 5)

        # temperature and pressure read
        workload.bytes_read += 16

        return workload

    def superdrop_mass_change(self):

        workload = Workload()

        # old_m_cond = drop.condensate_mass()
        workload.add(
            self.read_condensate_mass()
        )

        # kohler_factors(drop, temp)
        workload.add(
            self.kohler_factors()
        )

        # impe.solve_condensation(...)
        workload.add(
            self.solve_condensation()
        )

        # drop.change_radius(newr)
        workload.add(
            self.change_radius()
        )

        # drop.condensate_mass() - old_m_cond
        workload.add(
            self.calculate_mass_change()
        )

        # * drop.get_xi()
        workload.add(
            self.apply_multiplicity()
        )

        return workload

    def kohler_factors(self):

        workload = Workload()

        # akoh = akoh_constant / temp
        # bkoh = bkoh_constant * msol * ionic / mr_sol
        workload.add_operation("*", 4)
        workload.add_operation("/", 1)

        # radius + solute properties + temperature
        workload.bytes_read += (
            8 +       # radius
            3 * 8 +   # solute properties
            8         # temperature
        )

        return workload

    def solve_condensation(self):

        workload = Workload()
        n_iterations = 10  # Default number of iterations

        for _ in range(n_iterations):

            # Based on the Newton-Raphson-style root finding used in the
            # implicit Euler solver, each iteration performs a small set of
            # arithmetic updates.
            workload.add_operation("*", 5)
            workload.add_operation("+", 4)
            workload.add_operation("-", 1)
            workload.add_operation("/", 1)

        # s_ratio, Kohler factors, diffusion factor, radius
        workload.bytes_read += 4 * 8

        return workload

    def change_radius(self):

        workload = Workload()

        # Conceptually:
        # drop.change_radius(newr)
        # No arithmetic in the modelled update itself; just a stored value.

        workload.bytes_read += 8
        workload.bytes_written += 8

        return workload

    def calculate_mass_change(self):

        workload = Workload()

        # mass_condensed = (drop.condensate_mass() - old_m_cond) * drop.get_xi()
        workload.add_operation("-", 1)
        workload.add_operation("*", 1)

        workload.bytes_read += 8
        workload.bytes_written += 8

        return workload

    def apply_multiplicity(self):

        workload = Workload()

        # This is the multiplicity weighting applied to the condensed mass.
        workload.add_operation("*", 1)

        workload.bytes_read += 8
        workload.bytes_written += 8

        return workload

    def read_condensate_mass(self):

        workload = Workload()

        workload.bytes_read += 8

        return workload

    def effect_on_thermodynamic_state(self):

        workload = Workload()

        workload.add(
            self.thermodynamic_state_change()
        )

        return workload

    def thermodynamic_state_change(self):

        workload = Workload()

        # rho_dry = press / ((Rgas_dry + Rgas_v * qvap) * temp)
        workload.add_operation("*", 2)
        workload.add_operation("+", 1)
        workload.add_operation("/", 1)

        # delta_qcond = totrho_condensed / rho_dry
        workload.add_operation("/", 1)

        # qvap -= delta_qcond
        workload.add_operation("-", 1)

        # qcond += delta_qcond
        workload.add_operation("+", 1)

        # moist_specifc_heat = Cp_dry + Cp_v * qvap + C_l * qcond
        # delta_temp = (Latent_v / moist_specifc_heat) * delta_qcond
        workload.add_operation("*", 2)
        workload.add_operation("+", 2)
        workload.add_operation("/", 1)
        workload.add_operation("*", 1)

        # temp += delta_temp
        workload.add_operation("+", 1)

        # State:
        # press, temp, qvap, qcond, ...
        workload.bytes_read += 8 * 4
        workload.bytes_written += 8 * 3

        return workload