from workload import Workload


class Condensation:
    """Naive but formula-grounded condensation workload model.

    These counts aim to reflect the dominant algebraic structure in the C++
    condensation solver without claiming exact instruction counts for any specific
    compiler or hardware pipeline.
    """

    def run_step(self, n_sd_per_gbx, maxniters_newton_raphson=50):
        """Workload corresponding to one condensation call for one gridbox."""

        workload = Workload()

        workload.add(
            self.superdroplets_change(n_sd_per_gbx, maxniters_newton_raphson)
        )

        workload.add(
            self.effect_on_thermodynamic_state()
        )

        return workload

    def superdroplets_change(self, n_sd_per_gbx, maxniters_newton_raphson=50):

        workload = Workload()

        # These are calculated once per gridbox.
        workload.add(self.saturation_pressure())
        workload.add(self.supersaturation_ratio())
        workload.add(self.diffusion_factor())

        # Each superdroplet performs the same condensation update, so scale one
        # representative superdroplet workload by n_sd_per_gbx.
        workload.add(
            self.superdrop_mass_change(maxniters_newton_raphson).scale(n_sd_per_gbx)
        )

        return workload

    def saturation_pressure(self):

        workload = Workload()

        # psat = PREF * exp(A * (T - TREF) / (T - B)) / P0
        # Scalar expression with conversion, subtraction, division, and exp.
        workload.add_operation("*", 3)
        workload.add_operation("-", 2)
        workload.add_operation("/", 2)
        workload.add_operation("exp", 1)

        workload.bytes_read += 8
        workload.bytes_written += 8

        return workload

    def supersaturation_ratio(self):

        workload = Workload()

        # s_ratio = (press * qvap) / ((Mr_ratio + qvap) * psat)
        workload.add_operation("*", 2)
        workload.add_operation("+", 1)
        workload.add_operation("/", 1)

        workload.bytes_read += 3 * 8
        workload.bytes_written += 8

        return workload

    def diffusion_factor(self):

        workload = Workload()

        # diffusion_factor() in thermodynamic_equations.cpp is a dominant
        # gridbox-level term, containing powers, divisions, and a product-plus-sum
        # structure. This is a formula-grounded estimate rather than exact ISA-level
        # accounting.
        workload.add_operation("*", 9)
        workload.add_operation("fma", 1)
        workload.add_operation("+", 1)
        workload.add_operation("-", 1)
        workload.add_operation("/", 6)
        workload.add_operation("pow", 2)

        workload.bytes_read += 3 * 8
        workload.bytes_written += 8

        return workload

    def superdrop_mass_change(self, maxniters_newton_raphson=50):

        workload = Workload()

        workload.add(self.condensate_mass())
        workload.add(self.kohler_factors())
        workload.add(self.solve_condensation(maxniters_newton_raphson))
        workload.add(self.change_radius())
        workload.add(self.calculate_mass_change())
        workload.add(self.apply_multiplicity())
        workload.add(self.accumulate_mass_condensed())

        return workload

    def condensate_mass(self):

        workload = Workload()

        # mass() = msol * density_factor + massconst * rcubed(); then subtract
        # msol and clamp with fmax(0.0, ...). This is an algebraic proxy of the
        # actual droplet mass calculation.
        workload.add_operation("*", 3)
        workload.add_operation("fma", 1)
        workload.add_operation("-", 1)
        workload.add_operation("max", 1)

        workload.bytes_read += 3 * 8
        workload.bytes_written += 8

        return workload

    def kohler_factors(self):

        workload = Workload()

        # akoh = akoh_constant / temp
        # bkoh = bkoh_constant * msol * ionic / mr_sol
        workload.add_operation("*", 3)
        workload.add_operation("/", 3)

        workload.bytes_read += 8 + 3 * 8 + 8
        workload.bytes_written += 2 * 8

        return workload

    def solve_condensation(self, maxniters_newton_raphson=50):

        workload = Workload()

        # Worst-case path: this is the most expensive kernel in the condensation
        # step. In the actual implicit Euler solver, each Newton update evaluates
        # g(z) and g'(z) multiple times, applies a clamp with fmax, repeats until
        # convergence, and may also hit the adaptive sub-timestepping branch. We
        # therefore model a conservative upper-bound cost for the full solver.
        for _ in range(maxniters_newton_raphson):
            # One worst-case NR iteration is dominated by:
            #   - 2 g(z) evaluations: sqrt + pow + multiple multiplies/divides/adds
            #   - 1 g'(z) evaluation: sqrt + pow + multiply/divide chain
            #   - 1 update step: ziter * (1 - num/denom)
            #   - 1 clamp: fmax(ziter, 1e-8)
            #   - 1 convergence check
            workload.add_operation("*", 12)
            workload.add_operation("+", 8)
            workload.add_operation("-", 8)
            workload.add_operation("/", 8)
            workload.add_operation("pow", 4)
            workload.add_operation("sqrt", 2)
            workload.add_operation("max", 1)

        workload.bytes_read += 5 * 8
        workload.bytes_written += 8

        return workload

    def change_radius(self):

        workload = Workload()

        # radius = max(newr, dryr); return radius - oldradius.
        workload.add_operation("max", 1)
        workload.add_operation("-", 1)

        workload.bytes_read += 2 * 8
        workload.bytes_written += 8

        return workload

    def calculate_mass_change(self):

        workload = Workload()

        # mass_condensed = (drop.condensate_mass() - old_m_cond) * drop.get_xi()
        workload.add_operation("-", 1)
        workload.add_operation("*", 1)

        workload.bytes_read += 3 * 8
        workload.bytes_written += 8

        return workload

    def apply_multiplicity(self):

        workload = Workload()

        # multiplicity scaling: deltamass * xi
        workload.add_operation("*", 1)

        workload.bytes_read += 2 * 8
        workload.bytes_written += 8

        return workload

    def accumulate_mass_condensed(self):

        workload = Workload()

        # mass_condensed += deltamass; the reduction value is kept live in a
        # register rather than re-read from memory each time.
        workload.add_operation("+", 1)

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

        # qvap -= delta_qcond and qcond += delta_qcond
        workload.add_operation("-", 1)
        workload.add_operation("+", 1)

        # moist_specific_heat = Cp_dry + Cp_v * qvap + C_l * qcond
        # delta_temp = (Latent_v / moist_specific_heat) * delta_qcond
        workload.add_operation("*", 2)
        workload.add_operation("+", 2)
        workload.add_operation("/", 1)
        workload.add_operation("*", 1)

        # temp += delta_temp
        workload.add_operation("+", 1)

        workload.bytes_read += 5 * 8
        workload.bytes_written += 3 * 8

        return workload
