"""
ME3160 Project 2 - Moist Air Psychrometrics & District Cooling Load Routine
Reference state: 0 °C (273.15 K) ideal-gas reference, h_ref = 0.
Atmospheric pressure: P_atm = 101.325 kPa.
CoolProp permitted only for pure water/steam saturation pressure and condensate enthalpy.
"""

import numpy as np
import CoolProp.CoolProp as CP
from scipy.optimize import root_scalar

P_ATM = 101.325 # kPa

def P_sat_water(T_C):
    """Saturated water vapor pressure (kPa) using CoolProp (matches Table B.1.1)."""
    return CP.PropsSI('P', 'T', T_C + 273.15, 'Q', 0, 'Water') / 1e3

def humidity_ratio(Pv_kPa):
    """Humidity ratio w (kg H2O / kg dry air) from water vapor partial pressure (kPa)."""
    Pv_clamped = min(Pv_kPa, P_ATM - 0.01)
    return 0.622 * Pv_clamped / (P_ATM - Pv_clamped)

def vapor_pressure(w):
    """Water vapor partial pressure Pv (kPa) from humidity ratio w."""
    return w * P_ATM / (0.622 + w)

def moist_air_enthalpy(T_C, w):
    """
    Specific enthalpy of moist air (kJ/kg dry air):
    h = 1.006 * T + w * (2501.0 + 1.86 * T)
    """
    return 1.006 * T_C + w * (2501.0 + 1.86 * T_C)

def dry_bulb_from_h_w(h, w):
    """Recovers dry bulb temperature T_C from enthalpy h (kJ/kg da) and humidity ratio w."""
    return (h - 2501.0 * w) / (1.006 + 1.86 * w)

def get_wet_bulb(T_db, RH_percent):
    """
    Calculates thermodynamic wet bulb temperature Twb (deg C) via the adiabatic saturation energy balance:
    h(T_db, w) + (w_sat(Twb) - w) * h_f(Twb) = h_sat(Twb, w_sat(Twb))
    """
    Psat_db = P_sat_water(T_db)
    Pv = (RH_percent / 100.0) * Psat_db
    w = humidity_ratio(Pv)
    h_in = moist_air_enthalpy(T_db, w)

    def energy_residual(Twb):
        Psat_wb = P_sat_water(Twb)
        w_sat_wb = humidity_ratio(Psat_wb)
        # Saturated liquid water enthalpy h_f from CoolProp at Twb
        h_f = CP.PropsSI('H', 'T', Twb + 273.15, 'Q', 0, 'Water') / 1e3 # kJ/kg
        h_sat = moist_air_enthalpy(Twb, w_sat_wb)
        # Adiabatic saturation balance:
        return h_in + (w_sat_wb - w) * h_f - h_sat

    sol = root_scalar(energy_residual, bracket=[-10.0, T_db], method='brentq')
    return sol.root

def adiabatic_mixing(m_da1, h1, w1, m_da2, h2, w2):
    """Adiabatic mixing of two moist air streams."""
    m_tot = m_da1 + m_da2
    w_mix = (m_da1 * w1 + m_da2 * w2) / m_tot
    h_mix = (m_da1 * h1 + m_da2 * h2) / m_tot
    T_mix = dry_bulb_from_h_w(h_mix, w_mix)
    return T_mix, w_mix, h_mix

def solve_zone_psychrometrics(T_oa, RH_oa, solar_on=True, f_fresh=0.30):
    """
    Solves zone envelope thermal and moisture balances for one zone,
    iterating room moisture balance to convergence to maintain T_room = 22.0 °C.
    Returns dictionary with all psychrometric state points, coil duties, and condensate flow.
    """
    # Zone design parameters
    UA_env = 80.0 # W/K
    Q_solar = 1200.0 if solar_on else 0.0 # W
    q_sens_occ = 4.0 * 75.0 # 300 W
    q_lat_occ = 4.0 * 55.0 # 220 W
    q_light_equip = 20.0 * 40.0 # 800 W sensible
    q_sens_int = q_sens_occ + q_light_equip # 1100 W total sensible
    
    # Moisture generation rate from occupants (kg/s)
    # Using h_fg = 2501 kJ/kg:
    m_w_int = q_lat_occ / (2501.0 * 1e3) # 8.7965e-5 kg/s = 0.31667 kg/h
    
    m_da = 0.40 # kg/s supply dry air per zone
    BF = 0.15 # Bypass factor
    T_room = 22.0 # Setpoint deg C

    # Outdoor state
    Pv_oa = (RH_oa / 100.0) * P_sat_water(T_oa)
    w_oa = humidity_ratio(Pv_oa)
    h_oa = moist_air_enthalpy(T_oa, w_oa)
    Twb_oa = get_wet_bulb(T_oa, RH_oa)

    # Sensible room balance:
    # Q_sens_room = UA_env*(T_oa - T_room) + Q_solar + q_sens_int
    Q_sens_env = UA_env * (T_oa - T_room) # W
    Q_sens_room = Q_sens_env + Q_solar + q_sens_int # W

    # Iterate room humidity ratio w_room
    w_room = 0.010 # Initial estimate
    for _ in range(100):
        # Specific heat of moist air in room
        Cp_air = 1.006 + 1.86 * w_room # kJ/kg-K
        # Required supply temperature to absorb room sensible load
        T_supply = T_room - (Q_sens_room / 1000.0) / (m_da * Cp_air)

        # Mixing of recirculated room air and fresh outdoor air
        h_room = moist_air_enthalpy(T_room, w_room)
        T_mix, w_mix, h_mix = adiabatic_mixing(
            (1.0 - f_fresh) * m_da, h_room, w_room,
            f_fresh * m_da, h_oa, w_oa
        )

        # Coil Apparatus Dew Point (ADP):
        # T_supply = ADP + BF * (T_mix - ADP) -> ADP = (T_supply - BF * T_mix) / (1 - BF)
        ADP = (T_supply - BF * T_mix) / (1.0 - BF)
        Pv_adp = P_sat_water(ADP)
        w_adp = humidity_ratio(Pv_adp)

        # Supply humidity ratio
        if w_mix > w_adp:
            # Dehumidifying coil process
            w_supply = w_adp + BF * (w_mix - w_adp)
        else:
            # Sensible cooling only
            w_supply = w_mix

        # Moisture balance in the room: m_da * (w_room - w_supply) = m_w_int
        w_room_new = w_supply + m_w_int / m_da
        if abs(w_room_new - w_room) < 1e-8:
            w_room = w_room_new
            break
        w_room = w_room_new

    # Room relative humidity
    Pv_room = vapor_pressure(w_room)
    Psat_room = P_sat_water(T_room)
    RH_room = (Pv_room / Psat_room) * 100.0

    # Condensate removal rate
    m_cond_zone = m_da * max(0.0, w_mix - w_supply) # kg/s

    # Supply state enthalpy
    h_supply = moist_air_enthalpy(T_supply, w_supply)

    # Condensate enthalpy evaluated at ADP (from CoolProp)
    h_cond = CP.PropsSI('H', 'T', ADP + 273.15, 'Q', 0, 'Water') / 1e3 # kJ/kg

    # Coil load per zone including condensate removal enthalpy term:
    # Q_coil = m_da * (h_mix - h_supply) - m_cond * h_cond
    Q_coil = m_da * (h_mix - h_supply) - m_cond_zone * h_cond # kW

    # Sensible and latent load split on coil
    Q_coil_sens = m_da * (1.006 + 1.86 * w_mix) * (T_mix - T_supply) # kW
    Q_coil_lat = Q_coil - Q_coil_sens # kW

    # District scale (400 zones, 5% distribution gain, 2% pump gain)
    N_ZONES = 400
    DISTRIBUTION_GAIN = 0.05
    PUMP_GAIN = 0.02
    district_factor = 1.0 + DISTRIBUTION_GAIN + PUMP_GAIN # 1.07
    Q_evap_district = N_ZONES * Q_coil * district_factor # kW

    # Condensate generation
    m_cond_zone_kgh = m_cond_zone * 3600.0 # kg/h per zone
    m_cond_district_kgh = N_ZONES * m_cond_zone_kgh # kg/h
    m_cond_district_m3_day = (m_cond_district_kgh * 24.0) / 1000.0 # m3/day

    return {
        'T_oa': T_oa, 'RH_oa': RH_oa, 'Twb_oa': Twb_oa, 'w_oa': w_oa, 'h_oa': h_oa,
        'T_mix': T_mix, 'w_mix': w_mix, 'h_mix': h_mix,
        'T_supply': T_supply, 'w_supply': w_supply, 'h_supply': h_supply,
        'ADP': ADP, 'w_adp': w_adp,
        'T_room': T_room, 'w_room': w_room, 'RH_room': RH_room, 'Pv_room': Pv_room,
        'Q_sens_room_W': Q_sens_room,
        'Q_coil_kW': Q_coil,
        'Q_coil_sens_kW': Q_coil_sens,
        'Q_coil_lat_kW': Q_coil_lat,
        'Q_evap_district_kW': Q_evap_district,
        'm_cond_zone_kgh': m_cond_zone_kgh,
        'm_cond_district_kgh': m_cond_district_kgh,
        'm_cond_district_m3_day': m_cond_district_m3_day,
        'rh_violated': RH_room > 75.0
    }
