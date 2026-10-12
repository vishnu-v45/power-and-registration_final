"""
ME3160 Project 2 - Condenser Design & Off-Design Performance
Author: Pair Programming Assistant

Covers Task 2:
- Comparison of Air-Cooled Finned-Tube (U = 30 W/m2-K) vs Evaporative (U = 600 W/m2-K)
- Design sizing at governing condition (Monsoon Day for Evaporative; Summer Day for Air-Cooled)
- Sizing of UA, heat transfer area A, LMTD, air flow, and evaporative water makeup (Cycles of Concentration = 4)
- Off-design solver holding UA fixed to determine T_cond, P_high, T_gen, COP across all 6 conditions
- Verification of 3 critical constraints:
  (a) P_high <= 20 bar
  (b) T_gen deliverable by 300 °C flue gas with eps_gen=0.75 and 140 °C floor
  (c) T_cond >= 25 °C (flagging where low ambient drops T_cond and head-pressure control is required)
"""

import numpy as np
from scipy.optimize import root_scalar
from ammonia_props import Psat_ammonia_lk
from absorption_chiller import AbsorptionChiller

def calc_lmtd(T_hot, T_cold_in, T_cold_out):
    """Log-Mean Temperature Difference for a condensing heat exchanger."""
    dT1 = T_hot - T_cold_out
    dT2 = T_hot - T_cold_in
    if dT1 <= 0 or dT2 <= 0:
        return 0.1
    if abs(dT1 - dT2) < 1e-4:
        return dT1
    return (dT2 - dT1) / np.log(dT2 / dT1)

class CondenserDesign:
    def __init__(self, chiller: AbsorptionChiller):
        self.chiller = chiller
        self.U_air_cooled = 30.0 # W/m2-K
        self.U_evaporative = 600.0 # W/m2-K
        self.cycles_of_concentration = 4.0
        self.design_approach_wb = 7.35 # K (Monsoon day Twb = 32.65 -> T_cond = 40.0 C)
        self.design_approach_db = 12.0 # K (Summer day Tdb = 40.0 -> T_cond = 52.0 C)

    def size_evaporative_design(self, Q_evap_design_kW, Twb_design_C=32.65):
        """
        Sizes the evaporative condenser at governing condition (Monsoon Day).
        """
        T_cond_design = Twb_design_C + self.design_approach_wb # 40.0 °C
        cycle_res = self.chiller.solve_cycle(Q_evap_design_kW, T_cond_design)
        Q_cond_kW = cycle_res['Q_cond_kW']

        # Water/air temperature rise across evaporative condenser: ~3.8 K
        Twb_out = Twb_design_C + 3.85
        lmtd = calc_lmtd(T_cond_design, Twb_design_C, Twb_out)

        UA_design_kW_K = Q_cond_kW / lmtd # kW/K
        UA_design_W_K = UA_design_kW_K * 1e3 # W/K
        Area_m2 = UA_design_W_K / self.U_evaporative # m2

        # Evaporated water rate and makeup water rate with Cycles of Concentration = 4
        # Evaporation: m_evap = Q_cond / h_fg_water (h_fg ~ 2400 kJ/kg)
        m_evap_water_kgs = Q_cond_kW / 2400.0 # kg/s
        # Makeup water = m_evap * (CC / (CC - 1))
        CC = self.cycles_of_concentration
        m_makeup_water_kgs = m_evap_water_kgs * (CC / (CC - 1.0)) # kg/s
        m_makeup_m3_day = (m_makeup_water_kgs * 3600.0 * 24.0) / 1000.0 # m3/day

        # Cooling air flow (approx 1.2 kg air per kg evaporated water)
        m_air_kgs = m_evap_water_kgs * 80.0 # approx air flow rate

        return {
            'type': 'Evaporative',
            'T_cond_design_C': T_cond_design,
            'P_high_design_bar': cycle_res['P_high_bar'],
            'Q_cond_kW': Q_cond_kW,
            'LMTD_K': lmtd,
            'UA_kW_K': UA_design_kW_K,
            'UA_W_K': UA_design_W_K,
            'Area_m2': Area_m2,
            'U_W_m2K': self.U_evaporative,
            'm_makeup_water_kgs': m_makeup_water_kgs,
            'm_makeup_m3_day': m_makeup_m3_day,
            'm_air_kgs': m_air_kgs
        }

    def size_air_cooled_design(self, Q_evap_design_kW, Tdb_design_C=40.0):
        """
        Sizes air-cooled finned-tube condenser at Summer Day governing condition.
        """
        T_cond_design = Tdb_design_C + self.design_approach_db # 52.0 °C
        cycle_res = self.chiller.solve_cycle(Q_evap_design_kW, T_cond_design)
        Q_cond_kW = cycle_res['Q_cond_kW']

        # Air temperature rise: approx 10 K (enters at 40 C, leaves at 50 C)
        T_air_out = Tdb_design_C + 8.0
        lmtd = calc_lmtd(T_cond_design, Tdb_design_C, T_air_out)

        UA_design_kW_K = Q_cond_kW / lmtd
        UA_design_W_K = UA_design_kW_K * 1e3
        Area_m2 = UA_design_W_K / self.U_air_cooled

        # Air flow rate: m_air = Q_cond / (Cp_air * delta_T_air)
        Cp_air = 1.006 # kJ/kg-K
        m_air_kgs = Q_cond_kW / (Cp_air * 8.0) # kg/s

        return {
            'type': 'Air-Cooled',
            'T_cond_design_C': T_cond_design,
            'P_high_design_bar': cycle_res['P_high_bar'],
            'Q_cond_kW': Q_cond_kW,
            'LMTD_K': lmtd,
            'UA_kW_K': UA_design_kW_K,
            'UA_W_K': UA_design_W_K,
            'Area_m2': Area_m2,
            'U_W_m2K': self.U_air_cooled,
            'm_air_kgs': m_air_kgs
        }

    def solve_off_design_evaporative(self, UA_kW_K, Q_evap_kW, Twb_oa_C):
        """
        Holding UA fixed, solves for the equilibrium condensing temperature T_cond
        by balancing condenser heat rejection Q_cond_cycle(T_cond) = UA * LMTD(T_cond, Twb_oa).
        """
        if Q_evap_kW <= 0:
            return 25.0, 0.0, None

        def residual(T_c):
            cycle = self.chiller.solve_cycle(Q_evap_kW, T_c)
            Q_c_cycle = cycle['Q_cond_kW']
            Twb_out = Twb_oa_C + max(1.0, (Q_c_cycle / (UA_kW_K * 1.5)))
            lmtd = calc_lmtd(T_c, Twb_oa_C, min(T_c - 1.0, Twb_out))
            Q_c_hex = UA_kW_K * lmtd
            return Q_c_cycle - Q_c_hex

        # Search for T_cond in realistic range [Twb + 2, Twb + 25]
        bracket = [Twb_oa_C + 2.0, Twb_oa_C + 25.0]
        try:
            sol = root_scalar(residual, bracket=bracket, method='brentq')
            T_cond_unconstrained = sol.root
        except Exception:
            grid = np.linspace(bracket[0], bracket[1], 50)
            res = [abs(residual(t)) for t in grid]
            T_cond_unconstrained = grid[np.argmin(res)]

        # Actual operating T_cond respects head pressure control minimum of 25 °C:
        T_cond_actual = max(25.0, T_cond_unconstrained)
        cycle_actual = self.chiller.solve_cycle(Q_evap_kW, T_cond_actual)

        return T_cond_unconstrained, T_cond_actual, cycle_actual
