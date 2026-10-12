"""
rankine_cycle.py
Bottoming Rankine cycle using CoolProp for all water/steam properties.
Single-pressure cycle: Economizer -> Evaporator -> Superheater -> Turbine -> Condenser -> Pump.
"""

import CoolProp.CoolProp as CP

def solve_rankine_cycle(Ps_bar, Ts_K, Pcond_bar, eta_st=0.85, eta_pump=0.80):
    """
    Solves single-pressure bottoming Rankine cycle:
    - Ps_bar: Steam drum pressure in bar (10 - 60 bar)
    - Ts_K: Superheat outlet temperature in K
    - Pcond_bar: Condenser pressure in bar (0.05 - 0.15 bar)
    - eta_st: Steam turbine isentropic efficiency (default 0.85)
    - eta_pump: Feed pump isentropic efficiency (default 0.80)
    
    Returns dict containing state points (5, 6s, 6, 7, 8, sat_liq, sat_vap),
    work outputs, heat additions, thermal efficiency, and exit quality.
    """
    Ps = Ps_bar * 1e5       # Pa
    Pcond = Pcond_bar * 1e5 # Pa
    
    # Saturation temperature at drum pressure:
    T_sat_drum = CP.PropsSI('T', 'P', Ps, 'Q', 0, 'Water') # K
    
    # Saturated liquid and vapor enthalpies at drum pressure:
    h_sat_liq = CP.PropsSI('H', 'P', Ps, 'Q', 0, 'Water') / 1e3 # kJ/kg
    h_sat_vap = CP.PropsSI('H', 'P', Ps, 'Q', 1, 'Water') / 1e3 # kJ/kg
    s_sat_liq = CP.PropsSI('S', 'P', Ps, 'Q', 0, 'Water') / 1e3 # kJ/kg-K
    
    # State 5: Superheated steam at (Ps, Ts)
    h5 = CP.PropsSI('H', 'P', Ps, 'T', Ts_K, 'Water') / 1e3 # kJ/kg
    s5 = CP.PropsSI('S', 'P', Ps, 'T', Ts_K, 'Water') / 1e3 # kJ/kg-K
    
    # State 6s: Isentropic turbine expansion to Pcond
    h6s = CP.PropsSI('H', 'P', Pcond, 'S', s5 * 1e3, 'Water') / 1e3 # kJ/kg
    x6s = CP.PropsSI('Q', 'P', Pcond, 'S', s5 * 1e3, 'Water')
    
    # State 6: Actual turbine exit
    h6 = h5 - eta_st * (h5 - h6s) # kJ/kg
    # Steam quality at actual turbine exit:
    h_f_cond = CP.PropsSI('H', 'P', Pcond, 'Q', 0, 'Water') / 1e3
    h_g_cond = CP.PropsSI('H', 'P', Pcond, 'Q', 1, 'Water') / 1e3
    x6 = (h6 - h_f_cond) / (h_g_cond - h_f_cond)
    T6 = CP.PropsSI('T', 'P', Pcond, 'Q', 0, 'Water') # Saturation temp at Pcond
    
    # State 7: Condenser exit (saturated liquid)
    T7 = T6
    h7 = h_f_cond # kJ/kg
    s7 = CP.PropsSI('S', 'P', Pcond, 'Q', 0, 'Water') / 1e3 # kJ/kg-K
    v7 = 1.0 / CP.PropsSI('D', 'P', Pcond, 'Q', 0, 'Water') # m3/kg
    
    # State 8s / 8: Feed pump exit
    # Pump work w_pump_isen = v7 * (Ps - Pcond)
    # or from isentropic enthalpy rise:
    h8s = CP.PropsSI('H', 'P', Ps, 'S', s7 * 1e3, 'Water') / 1e3 # kJ/kg
    w_pump_isen = h8s - h7
    w_pump = w_pump_isen / eta_pump # kJ/kg
    h8 = h7 + w_pump # kJ/kg
    T8 = CP.PropsSI('T', 'P', Ps, 'H', h8 * 1e3, 'Water') # K
    
    # Work and heat terms:
    w_st = h5 - h6           # kJ/kg steam
    w_net = w_st - w_pump    # kJ/kg steam
    q_H = h5 - h8            # kJ/kg steam
    q_cond = h6 - h7         # kJ/kg steam
    eta_rankine = w_net / q_H
    
    return {
        'Ps_bar': Ps_bar, 'Ts_K': Ts_K, 'Pcond_bar': Pcond_bar,
        'T_sat_drum': T_sat_drum, 'T_sat_drum_C': T_sat_drum - 273.15,
        'h_sat_liq': h_sat_liq, 'h_sat_vap': h_sat_vap,
        'State5': {'P': Ps, 'T': Ts_K, 'h': h5, 's': s5},
        'State6s': {'P': Pcond, 'h': h6s, 'x': x6s},
        'State6': {'P': Pcond, 'T': T6, 'h': h6, 'x': x6},
        'State7': {'P': Pcond, 'T': T7, 'h': h7, 's': s7, 'v': v7},
        'State8': {'P': Ps, 'T': T8, 'h': h8},
        'w_st': w_st,
        'w_pump': w_pump,
        'w_net': w_net,
        'q_H': q_H,
        'q_cond': q_cond,
        'eta_rankine': eta_rankine,
        'x6': x6,
        'x6s': x6s,
    }
