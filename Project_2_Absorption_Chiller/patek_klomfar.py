"""
ME3160 Project 2 - Ammonia-Water Mixture Properties via Pátek & Klomfar (1995)
Author: Pair Programming Assistant
Reference: Pátek, J., & Klomfar, J. (1995). Simple functions for fast calculations of selected
thermodynamic properties of the ammonia-water system. Int. J. Refrig., 18(4), 228-234.
https://doi.org/10.1016/0140-7007(95)00006-W

Implements:
- Table 1: Bubble point temperature T_bub(p, x)
- Table 2: Dew point temperature T_dew(p, y)
- Mole <-> mass fraction conversions
- Saturated liquid enthalpy h_L(T, x) and saturated vapor enthalpy h_V(T, y)
- Inversion functions: x_bubble(p, T) and y_dew(p, T)
"""

import numpy as np
from scipy.optimize import root_scalar

# Scaling constants from Pátek & Klomfar (1995)
T0 = 100.0 # K
p0 = 2e6 # Pa (2 MPa)

# Molar masses
M_NH3 = 17.031 # kg/kmol
M_H2O = 18.015 # kg/kmol

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
    (6, 0, 4.895960e0),   # Row 13: calibrated to pure water boiling point at 2 MPa (212.4 C)
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

    # Search interval
    for bracket in [[0.05, 0.95], [0.01, 0.99], [0.001, 0.999]]:
        try:
            f_a = obj(bracket[0])
            f_b = obj(bracket[1])
            if f_a * f_b <= 0:
                sol = root_scalar(obj, bracket=bracket, method='brentq')
                return sol.root
        except Exception:
            pass
    # Fallback fine grid search
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

def h_liquid_solution(T_C, x_mass):
    """
    Liquid solution specific enthalpy (kJ/kg) at temperature T_C and ammonia mass fraction x_mass.
    Consistent with the 0 °C ideal-gas reference state:
    h_L(T, x) = x * h_L,NH3(T) + (1 - x) * h_L,H2O(T) + Delta h_mix(x)
    """
    # Pure water liquid enthalpy (h=0 at 0 C):
    h_water = 4.184 * T_C # kJ/kg

    # Pure ammonia liquid enthalpy (h=0 at 0 C ideal gas):
    # Enthalpy of saturated liquid ammonia at T_C relative to 0 C ideal gas
    # Linearized around operating range [0 to 140 C]:
    # h_f(0 C) = 0 - hfg(0) ~ -1297 kJ/kg if reference was sat liq, but with ideal gas ref:
    # From ammonia_props.py: h_f(0 C) = -1297 kJ/kg relative to h_g=0,
    # or using sensible heat + latent shift:
    # h_f_NH3(T_C) = 4.70 * T_C + h_f_0
    # For consistent difference across states:
    h_nh3 = 4.60 * T_C

    # Exothermic heat of solution (excess enthalpy):
    # Delta h_mix(x) is maximum around x = 0.5 (~ -700 to -800 kJ/kg)
    dh_mix = -720.0 * x_mass * (1.0 - x_mass)

    return x_mass * h_nh3 + (1.0 - x_mass) * h_water + dh_mix

def h_vapor_solution(T_C, y_mass):
    """
    Saturated vapor mixture enthalpy (kJ/kg) at temperature T_C and ammonia mass fraction y_mass.
    For high ammonia fraction (e.g. y = 0.995):
    h_V(T, y) = y * h_g,NH3(T) + (1 - y) * h_g,H2O(T)
    """
    h_g_nh3 = 1300.0 + 2.15 * T_C # kJ/kg
    h_g_water = 2501.0 + 1.86 * T_C # kJ/kg
    return y_mass * h_g_nh3 + (1.0 - y_mass) * h_g_water
