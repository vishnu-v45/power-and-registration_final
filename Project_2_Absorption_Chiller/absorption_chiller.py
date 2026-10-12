"""
ME3160 Project 2 - Waste-Heat-Driven Ammonia-Water Absorption Chiller Model
Author: Pair Programming Assistant

Cycle components:
- Generator with Rectifier (y = 0.995 NH3 by mass)
- Condenser (T_cond, saturated liquid out)
- Refrigerant Expansion Valve (isenthalpic throttle)
- Evaporator (T_evap = 2.0 °C, supplying chilled water 7 °C / 12 °C return, saturated vapor out)
- Absorber (T_abs = T_cond, saturated liquid out)
- Solution Pump (eta_pump = 0.70)
- Solution Heat Exchanger (SHX) (eps_SHX = 0.70)
- Weak Solution Throttle Valve (isenthalpic)

Waste Heat Source:
- Flue gas: ideal gas, Cp = 1.10 kJ/kg-K, T_fg,in = 300 °C, max 80 kg/s
- eps_gen = 0.75, defined as (T_fg,in - T_fg,out) / (T_fg,in - T_gen)
- Floor: T_fg,out >= 140 °C
"""

import numpy as np
from ammonia_props import Psat_ammonia_lk, solve_volumes, h_saturated_ammonia, MW
from patek_klomfar import (
    solve_x_bubble, solve_y_dew, mole_to_mass, mass_to_mole,
    T_bubble, T_dew, h_liquid_solution, h_vapor_solution
)

class AbsorptionChiller:
    def __init__(self, T_evap_C=2.0, eta_pump=0.70, eps_SHX=0.70, eps_gen=0.75):
        self.T_evap_C = T_evap_C
        self.eta_pump = eta_pump
        self.eps_SHX = eps_SHX
        self.eps_gen = eps_gen
        self.T_fg_in_C = 300.0 # deg C
        self.Cp_fg = 1.10 # kJ/kg-K
        self.m_fg_max = 80.0 # kg/s
        self.T_fg_floor_C = 140.0 # deg C
        self.x_r = 0.995 # Refrigerant ammonia mass fraction leaving rectifier

    def solve_cycle(self, Q_evap_kW, T_cond_C, T_gen_C=130.0):
        """
        Solves the absorption cycle for a specified evaporator duty Q_evap_kW and condensing temperature T_cond_C.
        Returns full thermodynamic states dictionary and performance metrics.
        """
        T_abs_C = T_cond_C # Absorber and condenser cooled by same medium

        # 1. Pressures from pure ammonia saturation at T_evap and T_cond
        T_evap_K = self.T_evap_C + 273.15
        T_cond_K = T_cond_C + 273.15
        T_gen_K = T_gen_C + 273.15

        P_low_Pa = Psat_ammonia_lk(T_evap_K) # Pa
        P_high_Pa = Psat_ammonia_lk(T_cond_K) # Pa
        P_low_kPa = P_low_Pa / 1e3
        P_high_kPa = P_high_Pa / 1e3
        P_high_bar = P_high_Pa / 1e5

        # 2. Strong and weak solution equilibrium concentrations via Pátek & Klomfar
        # Strong solution at absorber exit (P_low, T_abs):
        x_s_mole = solve_x_bubble(P_low_Pa, T_abs_C + 273.15)
        x_strong = mole_to_mass(x_s_mole)

        # Weak solution at generator exit (P_high, T_gen):
        x_w_mole = solve_x_bubble(P_high_Pa, T_gen_K)
        x_weak = mole_to_mass(x_w_mole)

        # Circulation ratio f = m_strong / m_r = (x_r - x_weak) / (x_strong - x_weak)
        if x_strong <= x_weak:
            raise ValueError(f"Degenerate concentrations: x_strong={x_strong:.4f} <= x_weak={x_weak:.4f}")
        
        f_circ = (self.x_r - x_weak) / (x_strong - x_weak)

        # 3. Refrigerant enthalpies
        # State 10: Saturated vapor leaving evaporator (P_low, T_evap)
        nh3_evap = h_saturated_ammonia(self.T_evap_C)
        h10 = nh3_evap['h_g'] # kJ/kg
        v_vap_evap = nh3_evap['v_vap'] # m3/kg

        # State 8: Saturated liquid leaving condenser (P_high, T_cond)
        nh3_cond = h_saturated_ammonia(T_cond_C)
        h8 = nh3_cond['h_f'] # kJ/kg

        # State 9: Liquid leaving throttle valve (isenthalpic)
        h9 = h8

        # Refrigerating effect (kJ/kg)
        q_e = h10 - h9

        # Refrigerant mass flow rate
        if Q_evap_kW <= 0:
            m_r = 0.0
        else:
            m_r = Q_evap_kW / q_e # kg/s

        # Solution mass flows
        m_strong = m_r * f_circ
        m_weak = m_strong - m_r

        # State 7: Vapor leaving rectifier at T_dew(P_high, y_r)
        y_r_mole = mass_to_mole(self.x_r)
        T_rect_K = T_dew(P_high_Pa, y_r_mole)
        T_rect_C = T_rect_K - 273.15
        h7 = h_vapor_solution(T_rect_C, self.x_r)

        # 4. Solution circuit enthalpies
        # State 1: Strong solution leaving absorber (saturated liquid at T_abs, x_strong)
        h1 = h_liquid_solution(T_abs_C, x_strong)

        # State 2: Strong solution leaving pump
        rho_strong = 860.0 # kg/m3 approximate solution density
        delta_P_kPa = P_high_kPa - P_low_kPa
        W_pump_spec = (delta_P_kPa / rho_strong) / self.eta_pump # kJ/kg
        h2 = h1 + W_pump_spec
        W_pump_kW = m_strong * W_pump_spec

        # State 4: Weak solution leaving generator (saturated liquid at T_gen, x_weak)
        h4 = h_liquid_solution(T_gen_C, x_weak)

        # State 5: Weak solution leaving SHX
        # Maximum possible SHX heat transfer:
        h4_at_Tabs = h_liquid_solution(T_abs_C, x_weak)
        Q_SHX_max = m_weak * (h4 - h4_at_Tabs)
        Q_SHX = self.eps_SHX * Q_SHX_max
        
        if m_weak > 0:
            h5 = h4 - Q_SHX / m_weak
        else:
            h5 = h4

        # State 3: Strong solution entering generator after SHX
        if m_strong > 0:
            h3 = h2 + Q_SHX / m_strong
        else:
            h3 = h2

        # State 6: Weak solution after throttle valve (isenthalpic)
        h6 = h5

        # 5. Rectifier heat duty
        # Rectifier cools vapor from generator to high-purity ammonia vapor (y = 0.995)
        # Saturated vapor leaving generator is at T_gen:
        h_vap_gen = h_vapor_solution(T_gen_C, self.x_r)
        Q_rect = m_r * max(0.0, h_vap_gen - h7) * 0.85 # kW

        # 6. Generator heat duty (Heating load)
        # Energy balance on generator: Q_gen + m_strong*h3 = m_r*h7 + m_weak*h4 + Q_rect
        Q_gen = m_r * h7 + m_weak * h4 - m_strong * h3 + Q_rect # kW

        # 7. Condenser heat duty
        # Vapor enters condenser from rectifier (h7) and leaves as saturated liquid (h8)
        Q_cond = m_r * (h7 - h8) # kW

        # 8. Absorber heat duty
        # Vapor from evaporator (m_r*h10) + weak solution from throttle (m_weak*h6) -> strong solution (m_strong*h1)
        Q_abs = m_r * h10 + m_weak * h6 - m_strong * h1 # kW

        # 9. COP and Energy Balance Check
        # First Law closure:
        # Energy in: Q_gen + Q_evap + W_pump
        # Energy out: Q_cond + Q_abs + Q_rect
        E_in = Q_gen + Q_evap_kW + W_pump_kW
        E_out = Q_cond + Q_abs + Q_rect
        first_law_residual = abs(E_in - E_out)

        COP = Q_evap_kW / (Q_gen + W_pump_kW) if (Q_gen + W_pump_kW) > 0 else 0.0

        # Carnot / Reversible COP bound:
        # COP_rev = [T_evap / (T_cond - T_evap)] * [(T_gen - T_abs) / T_gen] in Kelvin
        COP_rev = (T_evap_K / (T_cond_K - T_evap_K)) * ((T_gen_K - (T_abs_C + 273.15)) / T_gen_K)

        # 10. Flue-Gas Requirements
        # eps_gen = (T_fg,in - T_fg,out) / (T_fg,in - T_gen)
        # T_fg,out = T_fg,in - eps_gen * (T_fg,in - T_gen)
        T_fg_out_C = self.T_fg_in_C - self.eps_gen * (self.T_fg_in_C - T_gen_C)
        q_fg_spec = self.Cp_fg * (self.T_fg_in_C - T_fg_out_C) # kJ/kg flue gas
        m_fg_required = Q_gen / q_fg_spec if q_fg_spec > 0 else 0.0 # kg/s

        # 11. Circuit sizing parameters
        # Solution pump volumetric flow (m3/h)
        V_dot_pump_m3h = (m_strong / rho_strong) * 3600.0 # m3/h
        # Evaporator vapor volumetric flow (m3/h and m3/s)
        V_dot_evap_vap_m3s = m_r * v_vap_evap # m3/s
        V_dot_evap_vap_m3h = V_dot_evap_vap_m3s * 3600.0 # m3/h

        return {
            'Q_evap_kW': Q_evap_kW,
            'Q_gen_kW': Q_gen,
            'Q_cond_kW': Q_cond,
            'Q_abs_kW': Q_abs,
            'Q_rect_kW': Q_rect,
            'W_pump_kW': W_pump_kW,
            'COP': COP,
            'COP_rev': COP_rev,
            'first_law_residual_kW': first_law_residual,
            'm_r_kgs': m_r,
            'm_strong_kgs': m_strong,
            'm_weak_kgs': m_weak,
            'x_strong': x_strong,
            'x_weak': x_weak,
            'f_circ': f_circ,
            'P_low_kPa': P_low_kPa,
            'P_high_kPa': P_high_kPa,
            'P_high_bar': P_high_bar,
            'T_cond_C': T_cond_C,
            'T_abs_C': T_abs_C,
            'T_gen_C': T_gen_C,
            'T_rect_C': T_rect_C,
            'T_fg_out_C': T_fg_out_C,
            'm_fg_required_kgs': m_fg_required,
            'm_fg_limit_exceeded': m_fg_required > self.m_fg_max,
            'V_dot_pump_m3h': V_dot_pump_m3h,
            'delta_P_pump_kPa': delta_P_kPa,
            'V_dot_evap_vap_m3s': V_dot_evap_vap_m3s,
            'V_dot_evap_vap_m3h': V_dot_evap_vap_m3h,
            'h1': h1, 'h2': h2, 'h3': h3, 'h4': h4, 'h5': h5, 'h6': h6,
            'h7': h7, 'h8': h8, 'h9': h9, 'h10': h10,
        }
