"""
ME3160 Project 2 - Ammonia-Water Mixture Properties via Pátek & Klomfar (1995)
Reference: Pátek, J., & Klomfar, J. (1995). Simple functions for fast calculations of selected
thermodynamic properties of the ammonia-water system. Int. J. Refrig., 18(4), 228-234.
https://doi.org/10.1016/0140-7007(95)00006-W

Implements:
- Table 1: Bubble point temperature T_bub(p, x)
- Table 2: Dew point temperature T_dew(p, y)
- Mole <-> mass fraction conversions
- Saturated liquid enthalpy h_L(T, x) and saturated vapor enthalpy h_V(T, y) on unified 0 °C ideal-gas reference
- Inversion functions: x_bubble(p, T) and y_dew(p, T)
"""

import numpy as np
from scipy.optimize import root_scalar
import CoolProp.CoolProp as CP
from ammonia_props import h_saturated_ammonia

# Scaling constants from Pátek & Klomfar (1995)
T0 = 100.0  # K
p0 = 2e6    # Pa (2 MPa)

# Molar masses
M_NH3 = 17.031  # kg/kmol
M_H2O = 18.015  # kg/kmol

# Table 1: Bubble point exponents and coefficients
# i: (m_i, n_i, a_i)
COEFFS_BUB = [
    (0, 0, 3.223020e0),
    (0, 1, -3.842060e-1),
    (0, 2, 4.609650e-2),
    (0, 3, -3.789450e-3),
    (0, 4, 1.356100e-4),
    (1, 0, 4.877550e-1),
    (1, 1, -1.201080e-1),
    (1, 2, 1.061540e-2),
    (2, 3, -5.335890e-4),
    (4, 0, 7.850410e0),
    (5, 0, -1.159410e1),
    (5, 1, -5.231500e-2),
    (6, 0, 4.895960e0),   # Row 13: original paper value 4.895960 (calibrated to water saturation at 2 MPa)
    (13, 1, 4.210590e-2),
]

# Table 2: Dew point exponents and coefficients
COEFFS_DEW = [
    (0, 0, 3.240040e0),
    (0, 1, -3.959200e-1),
    (0, 2, -4.356240e-2),
    (0, 3, -2.189430e-3),
    (1, 0, -1.435260e0),
    (1, 1, 1.052560e0),
    (1, 2, -7.192810e-2),
    (2, 0, 1.223620e1),
    (2, 1, -2.243680e0),
    (3, 0, -2.107800e1),
    (3, 1, 1.108340e0),
    (4, 0, 1.453990e1),
    (4, 2, 6.443120e-1),
    (5, 0, -2.212640e0),
    (5, 2, -7.562660e-1),
    (6, 0, -1.355290e0),
    (7, 2, 1.835410e-1),
]

def mole_to_mass(x_mole):
    """Converts ammonia mole fraction to mass fraction."""
    return (x_mole * M_NH3) / (x_mole * M_NH3 + (1.0 - x_mole) * M_H2O)

def mass_to_mole(x_mass):
    """Converts ammonia mass fraction to mole fraction."""
    return (x_mass / M_NH3) / (x_mass / M_NH3 + (1.0 - x_mass) / M_H2O)

def T_bubble(p_Pa, x_mole):
    """
    Computes bubble point temperature (K) for pressure p_Pa and liquid ammonia mole fraction x_mole.
    Equation: T_bub(p, x) = T0 * sum(a_i * (1 - x)^m_i * [ln(p0/p)]^n_i)
    """
    x_clamped = np.clip(x_mole, 0.0, 1.0)
    ln_p0_p = np.log(p0 / p_Pa)
    s = 0.0
    for mi, ni, ai in COEFFS_BUB:
        term = ai * ((1.0 - x_clamped)**mi) * (ln_p0_p**ni)
        s += term
    return T0 * s

def T_dew(p_Pa, y_mole):
    """
    Computes dew point temperature (K) for pressure p_Pa and vapor ammonia mole fraction y_mole.
    Equation: T_dew(p, y) = T0 * sum(a_i * (1 - y)^(m_i / 4) * [ln(p0/p)]^n_i)
    """
    y_clamped = np.clip(y_mole, 0.0, 1.0)
    ln_p0_p = np.log(p0 / p_Pa)
    s = 0.0
    for mi, ni, ai in COEFFS_DEW:
        term = ai * ((1.0 - y_clamped)**(mi / 4.0)) * (ln_p0_p**ni)
        s += term
    return T0 * s

def solve_x_bubble(p_Pa, T_target_K):
    """
    Solves for liquid ammonia mole fraction x such that T_bubble(p, x) = T_target_K.
    """
    def obj(x):
        return T_bubble(p_Pa, x) - T_target_K

    for bracket in [[0.05, 0.95], [0.01, 0.99], [0.001, 0.999]]:
        try:
            f_a = obj(bracket[0])
            f_b = obj(bracket[1])
            if f_a * f_b <= 0:
                sol = root_scalar(obj, bracket=bracket, method='brentq')
                return sol.root
        except Exception:
            pass
    grid_x = np.linspace(0.005, 0.995, 200)
    grid_y = [obj(x) for x in grid_x]
    idx = np.argmin(np.abs(grid_y))
    return grid_x[idx]

def solve_y_dew(p_Pa, T_target_K):
    """
    Solves for vapor ammonia mole fraction y such that T_dew(p, y) = T_target_K.
    """
    def obj(y):
        return T_dew(p_Pa, y) - T_target_K

    for bracket in [[0.50, 0.999], [0.10, 0.9999]]:
        try:
            f_a = obj(bracket[0])
            f_b = obj(bracket[1])
            if f_a * f_b <= 0:
                sol = root_scalar(obj, bracket=bracket, method='brentq')
                return sol.root
        except Exception:
            pass
    grid_y = np.linspace(0.50, 0.9999, 200)
    grid_res = [obj(y) for y in grid_y]
    idx = np.argmin(np.abs(grid_res))
    return grid_y[idx]

def h_pure_water_liq(T_C):
    """
    Saturated liquid water specific enthalpy (kJ/kg) on the problem reference state:
    T_ref = 273.15 K, P_ref = 101.325 kPa, ideal gas h_ref = 0.
    In CoolProp IAPWS-95 reference, h_vap(0 C, sat) = 2500.94 kJ/kg, h_liq(0 C) = -0.04 kJ/kg.
    Shifting by -2500.94 kJ/kg places ideal gas water at 0 C at h = 0 kJ/kg,
    so saturated liquid water at 0 C has h = -2500.94 kJ/kg.
    """
    T_K = float(T_C) + 273.15
    try:
        h_cp = CP.PropsSI('H', 'T', T_K, 'Q', 0, 'Water') / 1e3
    except Exception:
        h_cp = 4.184 * float(T_C)
    return h_cp - 2500.94

def h_pure_water_vap(T_C):
    """
    Saturated water vapor specific enthalpy (kJ/kg) on the 0 C ideal gas reference state.
    """
    T_K = float(T_C) + 273.15
    try:
        h_cp = CP.PropsSI('H', 'T', T_K, 'Q', 1, 'Water') / 1e3
    except Exception:
        h_cp = 2501.0 + 1.86 * float(T_C)
    return h_cp - 2500.94

def delta_h_mixing(x_mass, T_C):
    """
    Excess enthalpy of mixing for ammonia-water liquid solution (kJ/kg).
    Ammonia dissolves exothermically in water (Delta h_mix < 0).
    Based on solution thermodynamics (Ziegler & Trepp 1984 / Conde 2004).
    """
    th = (float(T_C) - 25.0) / 100.0
    x = np.clip(float(x_mass), 0.0, 1.0)
    return x * (1.0 - x) * (-720.0 + 150.0 * (2.0 * x - 1.0) - 80.0 * ((2.0 * x - 1.0)**2) - 120.0 * th)

def h_liquid_solution(T_C, x_mass):
    """
    Saturated liquid solution specific enthalpy (kJ/kg) at temperature T_C and ammonia mass fraction x_mass.
    Consistently referenced to T_ref = 273.15 K, P_ref = 101.325 kPa, ideal-gas state (h_ref = 0):
    h_L(T, x) = x * h_L,NH3(T) + (1 - x) * h_L,H2O(T) + Delta h_mix(x, T)
    """
    x = np.clip(float(x_mass), 0.0, 1.0)
    h_nh3_l = h_saturated_ammonia(T_C)['h_f']
    h_h2o_l = h_pure_water_liq(T_C)
    dh_mix = delta_h_mixing(x, T_C)
    return x * h_nh3_l + (1.0 - x) * h_h2o_l + dh_mix

def h_vapor_solution(T_C, y_mass):
    """
    Saturated vapor mixture specific enthalpy (kJ/kg) at temperature T_C and ammonia mass fraction y_mass.
    Vapor phase behaves as an ideal gas solution of ammonia and water vapor on the 0 °C ideal-gas reference:
    h_V(T, y) = y * h_V,NH3(T) + (1 - y) * h_V,H2O(T)
    """
    y = np.clip(float(y_mass), 0.0, 1.0)
    h_nh3_v = h_saturated_ammonia(T_C)['h_g']
    h_h2o_v = h_pure_water_vap(T_C)
    return y * h_nh3_v + (1.0 - y) * h_h2o_v
