"""
ME3160 Project 2 - Condenser Design & Off-Design Performance

Covers Task 2:
- Comparison of Air-Cooled Finned-Tube (U = 30 W/m2-K) vs Evaporative (U = 600 W/m2-K)
- Design sizing at governing condition (Monsoon Day for Evaporative; Summer Day for Air-Cooled)
- Sizing of UA, heat transfer area A, LMTD, air flow, and evaporative water makeup (Cycles of Concentration = 4)
- Off-design solver holding UA fixed to determine T_cond, P_high, T_gen, COP across all 6 conditions
- Verification of 3 critical constraints:
  (a) P_high <= 20 bar (vessel design pressure)
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
        self.m_air_evap_design = 290.0 # kg/s cooling air
        self.cp_star_sat_air = 3.0 # kJ/kg-K effective heat capacity of saturated air

    def size_evaporative_design(self, Q_evap_design_kW, Twb_design_C=32.65):
        """
        Sizes the evaporative condenser at governing condition (Monsoon Day).
        """
        T_cond_design = Twb_design_C + self.design_approach_wb # 40.0 °C
        cycle_res = self.chiller.solve_cycle(Q_evap_design_kW, T_cond_design)
        Q_cond_kW = cycle_res['Q_cond_kW']

        # Water evaporation rate: h_fg ~ 2400 kJ/kg
        m_evap_water_kgs = Q_cond_kW / 2400.0 # kg/s

        # Air-side energy balance at design:
        # Design Delta Twb across condenser: ~6.0 K
        delta_Twb_design = 6.0 # K
        self.m_air_evap_design = Q_cond_kW / (self.cp_star_sat_air * delta_Twb_design)
        Twb_out = Twb_design_C + delta_Twb_design

        lmtd = calc_lmtd(T_cond_design, Twb_design_C, Twb_out)

        UA_design_kW_K = Q_cond_kW / lmtd # kW/K
        UA_design_W_K = UA_design_kW_K * 1e3 # W/K
        Area_m2 = UA_design_W_K / self.U_evaporative # m2

        # Makeup water with Cycles of Concentration = 4
        # Makeup = Evaporation * (CC / (CC - 1))
        CC = self.cycles_of_concentration
        m_makeup_water_kgs = m_evap_water_kgs * (CC / (CC - 1.0)) # kg/s
        m_makeup_m3_day = (m_makeup_water_kgs * 3600.0 * 24.0) / 1000.0 # m3/day

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
            'm_air_kgs': self.m_air_evap_design
        }

    def size_air_cooled_design(self, Q_evap_design_kW, Tdb_design_C=40.0):
        """
        Sizes air-cooled finned-tube condenser at Summer Day governing condition.
        """
        T_cond_design = Tdb_design_C + self.design_approach_db # 52.0 °C
        cycle_res = self.chiller.solve_cycle(Q_evap_design_kW, T_cond_design)
        Q_cond_kW = cycle_res['Q_cond_kW']

        # Air temperature rise: 10 K (enters at 40 C, leaves at 50 C)
        delta_T_air = 10.0
        T_air_out = Tdb_design_C + delta_T_air
        lmtd = calc_lmtd(T_cond_design, Tdb_design_C, T_air_out)

        UA_design_kW_K = Q_cond_kW / lmtd
        UA_design_W_K = UA_design_kW_K * 1e3
        Area_m2 = UA_design_W_K / self.U_air_cooled

        # Air mass flow rate: m_air = Q_cond / (Cp_air * delta_T_air)
        Cp_air = 1.006 # kJ/kg-K
        m_air_kgs = Q_cond_kW / (Cp_air * delta_T_air) # kg/s

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
        Holding UA fixed, solves for equilibrium condensing temperature T_cond
        by balancing condenser heat rejection Q_cond_cycle(T_cond) = UA * LMTD(T_cond, Twb_oa, Twb_out),
        where Twb_out is determined by an air-side energy balance:
        Twb_out = Twb_oa + Q_cond / (m_air * cp_star).
        """
        if Q_evap_kW <= 0:
            return 25.0, 25.0, None

        m_air = self.m_air_evap_design

        def residual(T_c):
            cycle = self.chiller.solve_cycle(Q_evap_kW, T_c)
            Q_c_cycle = cycle['Q_cond_kW']
            # Air-side energy balance:
            Twb_out = Twb_oa_C + (Q_c_cycle / (m_air * self.cp_star_sat_air))
            Twb_out_capped = min(T_c - 0.5, Twb_out)
            lmtd = calc_lmtd(T_c, Twb_oa_C, Twb_out_capped)
            Q_c_hex = UA_kW_K * lmtd
            return Q_c_cycle - Q_c_hex

        bracket = [Twb_oa_C + 1.5, Twb_oa_C + 25.0]
        try:
            sol = root_scalar(residual, bracket=bracket, method='brentq')
            T_cond_unconstrained = sol.root
        except Exception:
            grid = np.linspace(bracket[0], bracket[1], 100)
            res = [abs(residual(t)) for t in grid]
            T_cond_unconstrained = grid[np.argmin(res)]

        # Actual operating T_cond respects head pressure control minimum of 25 °C:
        T_cond_actual = max(25.0, T_cond_unconstrained)
        cycle_actual = self.chiller.solve_cycle(Q_evap_kW, T_cond_actual)

        return T_cond_unconstrained, T_cond_actual, cycle_actual
