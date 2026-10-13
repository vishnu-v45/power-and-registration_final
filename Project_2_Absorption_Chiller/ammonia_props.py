"""
ME3160 Project 2 - Pure Ammonia Thermodynamic Properties via Real-Gas EOS
Reference state: T_ref = 273.15 K, P_ref = 101.325 kPa, ideal-gas state: h_ref = 0, s_ref = 0.
Equation of State: Peng-Robinson Cubic EOS with Lee-Kesler / Pitzer generalized vapor pressure.
Ideal gas Cp from Borgnakke & Sonntag (Table A.6).
"""

import numpy as np

# Ammonia molecular and critical constants
MW = 17.031 # kg/kmol
R_univ = 8314.462 # J/(kmol-K)
R_sp = R_univ / MW # J/(kg-K) = 488.19576 J/(kg-K)
Tc = 405.56 # K
Pc = 11.333e6 # Pa (11.333 MPa)
omega = 0.256 # Acentric factor

# PR EOS parameters
a_c = 0.45724 * (R_sp**2) * (Tc**2) / Pc
b = 0.07780 * R_sp * Tc / Pc
m_factor = 0.37464 + 1.54226 * omega - 0.26992 * (omega**2)

# Borgnakke & Sonntag Table A.6 polynomial for NH3 ideal gas Cp0:
# Cp0_bar(T) = 27.31 + 23.83*theta + 17.07*theta^2 - 11.85*theta^3 (kJ/kmol-K), theta = T / 1000
c_molar = [27.31, 23.83, 17.07, -11.85]
c_mass = [coeff / MW for coeff in c_molar] # kJ/(kg-K)

def Psat_ammonia_lk(T_K):
    """
    Lee-Kesler / Pitzer vapor pressure correlation for ammonia:
    ln(Pr) = f0(Tr) + omega * f1(Tr)
    Returns Psat in Pa.
    """
    Tr = T_K / Tc
    f0 = 5.92714 - 6.09648 / Tr - 1.28862 * np.log(Tr) + 0.169347 * (Tr**6)
    f1 = 15.2518 - 15.6875 / Tr - 13.4721 * np.log(Tr) + 0.43577 * (Tr**6)
    ln_Pr = f0 + omega * f1
    Pr = np.exp(ln_Pr)
    return Pr * Pc

def pr_params(T_K):
    """Peng-Robinson parameters a(T) and da/dT at temperature T_K."""
    Tr = T_K / Tc
    sqrt_Tr = np.sqrt(Tr)
    alpha = (1.0 + m_factor * (1.0 - sqrt_Tr))**2
    a = a_c * alpha
    da_dT = a_c * 2.0 * (1.0 + m_factor * (1.0 - sqrt_Tr)) * (-m_factor / (2.0 * sqrt_Tr * Tc))
    return a, da_dT

def solve_volumes(T_K, P_Pa):
    """
    Solves cubic PR EOS for compressibility factors Z_liq and Z_vap.
    Z^3 - (1 - B)*Z^2 + (A - 3B^2 - 2B)*Z - (AB - B^2 - B^3) = 0
    Returns: Z_liq, Z_vap, v_liq, v_vap (m3/kg)
    """
    a, da_dT = pr_params(T_K)
    RT = R_sp * T_K
    A = a * P_Pa / (RT**2)
    B = b * P_Pa / RT

    c3 = 1.0
    c2 = -(1.0 - B)
    c1 = A - 3.0 * (B**2) - 2.0 * B
    c0 = -(A * B - B**2 - B**3)

    roots = np.roots([c3, c2, c1, c0])
    real_roots = [r.real for r in roots if np.isreal(r) and r.real > B]
    if not real_roots:
        real_roots = [r.real for r in roots if np.isreal(r)]
    
    Z_liq = min(real_roots)
    Z_vap = max(real_roots)
    v_liq = Z_liq * RT / P_Pa
    v_vap = Z_vap * RT / P_Pa
    return Z_liq, Z_vap, v_liq, v_vap

def enthalpy_departure(T_K, P_Pa, Z):
    """
    Enthalpy departure (h - h_ig) in J/kg from PR EOS.
    (h - h_ig) = RT*(Z - 1) + [(T*da/dT - a)/(2*sqrt(2)*b)] * ln((Z + (1+sqrt(2))*B)/(Z + (1-sqrt(2))*B))
    """
    a, da_dT = pr_params(T_K)
    RT = R_sp * T_K
    B = b * P_Pa / RT
    term1 = RT * (Z - 1.0)
    sqrt2 = np.sqrt(2.0)
    numerator = Z + (1.0 + sqrt2) * B
    denominator = max(1e-12, Z + (1.0 - sqrt2) * B)
    term2 = ((T_K * da_dT - a) / (2.0 * sqrt2 * b)) * np.log(numerator / denominator)
    return term1 + term2 # J/kg

def h_ideal_gas(T_K):
    """
    Integral of Cp0 from T_ref = 273.15 K to T_K.
    Returns h_ig in kJ/kg with h_ig(273.15 K) = 0.
    """
    T_ref = 273.15
    th = T_K / 1000.0
    th_ref = T_ref / 1000.0
    val = (c_mass[0] * (th - th_ref) +
           0.5 * c_mass[1] * (th**2 - th_ref**2) +
           (c_mass[2] / 3.0) * (th**3 - th_ref**3) +
           0.25 * c_mass[3] * (th**4 - th_ref**4))
    return 1000.0 * val # kJ/kg

def h_saturated_ammonia(T_C):
    """
    Computes saturated liquid and vapor enthalpies (kJ/kg) and saturation pressure (kPa)
    for pure ammonia at temperature T_C in deg C.
    Both h_f and h_g share the 273.15 K / 101.325 kPa ideal gas reference (h_ref = 0).
    """
    T_K = T_C + 273.15
    P_sat_Pa = Psat_ammonia_lk(T_K)
    Z_liq, Z_vap, v_liq, v_vap = solve_volumes(T_K, P_sat_Pa)
    
    h_ig_val = h_ideal_gas(T_K)
    dh_dep_liq = enthalpy_departure(T_K, P_sat_Pa, Z_liq) / 1e3 # kJ/kg
    dh_dep_vap = enthalpy_departure(T_K, P_sat_Pa, Z_vap) / 1e3 # kJ/kg

    h_f = h_ig_val + dh_dep_liq
    h_g = h_ig_val + dh_dep_vap
    h_fg = h_g - h_f

    return {
        'T_C': T_C,
        'P_sat_kPa': P_sat_Pa / 1e3,
        'P_sat_bar': P_sat_Pa / 1e5,
        'h_f': h_f,
        'h_g': h_g,
        'h_fg': h_fg,
        'v_liq': v_liq,
        'v_vap': v_vap,
        'Z_liq': Z_liq,
        'Z_vap': Z_vap
    }
