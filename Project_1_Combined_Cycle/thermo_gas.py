"""
thermo_gas.py
Thermodynamic property models for ideal gases and combustion mixtures with variable Cp(T).
Based on Borgnakke & Sonntag, Table A.6 (Cp polynomials) and Table A.7 (Air-standard tables).
"""

import numpy as np
from scipy.optimize import root_scalar

# Borgnakke & Sonntag Table A.6 polynomial coefficients:
# Cp0_bar(T) = C0 + C1*theta + C2*theta^2 + C3*theta^3  (kJ/kmol-K), theta = T / 1000 K
#
# Species molar masses (kg/kmol) and Table A.6 coefficients:
SPECIES_DATA = {
    'N2': {
        'M': 28.013,
        'C': [28.90, -0.1571, 8.081, -2.873],
        'href': 0.0,
    },
    'O2': {
        'M': 31.999,
        'C': [25.48, 15.20, -7.155, 1.312],
        'href': 0.0,
    },
    'CO2': {
        'M': 44.01,
        'C': [22.26, 59.81, -35.01, 7.469],
        'href': 0.0,
    },
    'H2O': {
        'M': 18.015,
        'C': [32.24, 1.923, 10.55, -3.595],
        'href': 0.0,
    },
    'CH4': {
        'M': 16.043,
        'C': [19.89, 50.24, 12.69, -11.01],
        'href': 0.0,
    },
    'Air': {
        'M': 28.97,
        # Exact calibration to Borgnakke & Sonntag Table A.7.1 / A.7.2 air tables:
        # cp(T) in kJ/kg-K: cp(T) = C0 + C1*theta + C2*theta^2 + C3*theta^3
        'mass_C': [0.98142124, -0.01603534, 0.29079115, -0.11806959],
        'h_offset': 4.39143765, # kJ/kg offset matching Table A.7 reference (h=300.47 at 300 K)
    }
}

R_UNIV = 8.314462 # kJ/kmol-K

class GasMixture:
    """
    Represents an ideal gas mixture with temperature-dependent specific heats.
    Can be initialized with molar composition {species: mole_fraction} or pure 'Air'.
    """
    def __init__(self, composition):
        if composition == 'Air':
            self.is_pure_air = True
            self.M = SPECIES_DATA['Air']['M']
            self.R = R_UNIV / self.M # 0.287002 kJ/kg-K
            self.mass_C = SPECIES_DATA['Air']['mass_C']
            self.h_offset = SPECIES_DATA['Air']['h_offset']
            self.composition = {'Air': 1.0}
        else:
            self.is_pure_air = False
            tot = sum(composition.values())
            self.mole_fractions = {k: v / tot for k, v in composition.items()}
            self.M = sum(self.mole_fractions[sp] * SPECIES_DATA[sp]['M'] for sp in self.mole_fractions)
            self.R = R_UNIV / self.M # kJ/kg-K
            self.mass_fractions = {sp: (self.mole_fractions[sp] * SPECIES_DATA[sp]['M']) / self.M 
                                   for sp in self.mole_fractions}
            
    def cp_molar(self, T):
        if self.is_pure_air:
            return self.cp_mass(T) * self.M
        th = T / 1000.0
        cp = 0.0
        for sp, yi in self.mole_fractions.items():
            C = SPECIES_DATA[sp]['C']
            cpi = C[0] + C[1]*th + C[2]*(th**2) + C[3]*(th**3)
            cp += yi * cpi
        return cp

    def cp_mass(self, T):
        if self.is_pure_air:
            th = T / 1000.0
            C = self.mass_C
            return C[0] + C[1]*th + C[2]*(th**2) + C[3]*(th**3)
        return self.cp_molar(T) / self.M

    def h_mass(self, T):
        th = T / 1000.0
        if self.is_pure_air:
            C = self.mass_C
            val = (C[0]*th + 0.5*C[1]*(th**2) + (C[2]/3.0)*(th**3) + 0.25*C[3]*(th**4)) * 1000.0
            return val + self.h_offset
        else:
            h_mol = 0.0
            for sp, yi in self.mole_fractions.items():
                C = SPECIES_DATA[sp]['C']
                hi = (C[0]*th + 0.5*C[1]*(th**2) + (C[2]/3.0)*(th**3) + 0.25*C[3]*(th**4)) * 1000.0
                h_mol += yi * hi
            return h_mol / self.M

    def s0_mass(self, T):
        th = T / 1000.0
        if self.is_pure_air:
            C = self.mass_C
            return (C[0]*np.log(T) + C[1]*th + 0.5*C[2]*(th**2) + (C[3]/3.0)*(th**3))
        else:
            s0_mol = 0.0
            for sp, yi in self.mole_fractions.items():
                C = SPECIES_DATA[sp]['C']
                s0i = (C[0]*np.log(T) + C[1]*th + 0.5*C[2]*(th**2) + (C[3]/3.0)*(th**3))
                s0_mol += yi * s0i
            return s0_mol / self.M

    def solve_T_from_h(self, target_h, T_guess=600.0):
        sol = root_scalar(lambda T: self.h_mass(T) - target_h, 
                          bracket=[150.0, 3000.0], x0=T_guess, method='brentq')
        return sol.root

    def solve_T_isentropic(self, T_init, P_ratio):
        target_s0 = self.s0_mass(T_init) + self.R * np.log(P_ratio)
        sol = root_scalar(lambda T: self.s0_mass(T) - target_s0,
                          bracket=[150.0, 3000.0], x0=T_init * (P_ratio**((1.4-1)/1.4)), method='brentq')
        return sol.root


def solve_combustor(T_air_in, P_comb, TIT, eta_f=0.98, LHV=50000.0):
    M_CH4 = 16.043
    M_air = 0.21 * 31.999 + 0.79 * 28.013 # 28.850 kg/kmol
    ratio_N2_O2 = 79.0 / 21.0
    
    moles_air_stoich = 2.0 * (1.0 + ratio_N2_O2)
    f_A_stoich = M_CH4 / (moles_air_stoich * M_air) # ~ 0.0583 kg fuel / kg air
    
    air_mix = GasMixture('Air')
    h_air_in = air_mix.h_mass(T_air_in)
    
    def get_product_mixture(phi_val):
        lam = 1.0 / phi_val
        n_CO2 = 1.0
        n_H2O = 2.0
        n_O2 = 2.0 * (lam - 1.0)
        n_N2 = 2.0 * lam * ratio_N2_O2
        tot_moles = n_CO2 + n_H2O + n_O2 + n_N2
        return GasMixture({
            'CO2': n_CO2 / tot_moles,
            'H2O': n_H2O / tot_moles,
            'O2':  n_O2 / tot_moles,
            'N2':  n_N2 / tot_moles,
        })

    def energy_balance_residual(phi_val):
        f_A = phi_val * f_A_stoich
        prod_mix = get_product_mixture(phi_val)
        h_prod_TIT = prod_mix.h_mass(TIT)
        lhs = h_air_in + f_A * eta_f * LHV
        rhs = (1.0 + f_A) * h_prod_TIT
        return lhs - rhs

    sol = root_scalar(energy_balance_residual, bracket=[0.05, 0.95], method='brentq')
    phi_sol = sol.root
    f_A_sol = phi_sol * f_A_stoich
    lam_sol = 1.0 / phi_sol
    prod_mix_sol = get_product_mixture(phi_sol)
    
    return f_A_sol, phi_sol, lam_sol, prod_mix_sol


def solve_brayton_cycle(rp, TIT, T1=298.15, P1=101.3, P4=105.0, eta_c=0.86, eta_t=0.89, eta_f=0.98):
    air = GasMixture('Air')
    h1 = air.h_mass(T1)
    
    P2 = P1 * rp
    T2s = air.solve_T_isentropic(T1, rp)
    h2s = air.h_mass(T2s)
    h2 = h1 + (h2s - h1) / eta_c
    T2 = air.solve_T_from_h(h2, T_guess=T2s + 30.0)
    w_c = h2 - h1 # kJ/kg air
    
    f_A, phi, lam, prod_mix = solve_combustor(T2, P2, TIT, eta_f=eta_f)
    h3 = prod_mix.h_mass(TIT)
    q_in = f_A * 50000.0 # kJ per kg air based on fuel LHV (50 MJ/kg)
    
    P_ratio_turb = P4 / P2
    T4s = prod_mix.solve_T_isentropic(TIT, P_ratio_turb)
    h4s = prod_mix.h_mass(T4s)
    h4 = h3 - eta_t * (h3 - h4s)
    T4 = prod_mix.solve_T_from_h(h4, T_guess=T4s + 50.0)
    w_t_per_kg_prod = h3 - h4 # kJ/kg products
    w_t = (1.0 + f_A) * w_t_per_kg_prod # kJ/kg air
    
    w_gt_net = w_t - w_c # kJ/kg air
    eta_gt = w_gt_net / q_in
    
    return {
        'T1': T1, 'P1': P1, 'h1': h1,
        'T2s': T2s, 'h2s': h2s,
        'T2': T2, 'P2': P2, 'h2': h2, 'w_c': w_c,
        'TIT': TIT, 'T3': TIT, 'P3': P2, 'h3': h3,
        'f_A': f_A, 'phi': phi, 'lambda': lam, 'q_in': q_in,
        'prod_mix': prod_mix,
        'T4s': T4s, 'h4s': h4s,
        'T4': T4, 'P4': P4, 'h4': h4, 'w_t': w_t,
        'w_gt_net': w_gt_net, 'eta_gt': eta_gt,
    }
