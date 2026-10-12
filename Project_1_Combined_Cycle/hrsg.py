"""
hrsg.py
Heat Recovery Steam Generator (HRSG) pinch analysis and heat exchanger model.
Solves heat transfer between gas turbine exhaust and bottoming Rankine cycle.
"""

def solve_hrsg(gas_mix, T_gas_in, m_dot_gas, rankine_results, 
               delta_T_pinch_min=10.0, delta_T_approach_min=5.0):
    """
    Performs pinch-point analysis for single-pressure HRSG:
    - gas_mix: GasMixture object of exhaust products
    - T_gas_in: Exhaust gas entering HRSG (K)
    - m_dot_gas: Exhaust gas mass flow rate (kg/s)
    - rankine_results: Output dict from solve_rankine_cycle()
    - delta_T_pinch_min: Minimum evaporator pinch temperature difference (default 10 K)
    - delta_T_approach_min: Minimum superheater approach temperature difference (default 5 K)
    
    Returns dict containing:
    - m_dot_steam: Steam mass flow rate (kg/s)
    - T_gas_stack: Stack gas temperature (K and C)
    - Q_hrsg: Total heat recovered in HRSG (kW)
    - Q_sup, Q_evap, Q_econ: Component duties (kW)
    - delta_T_pinch: Actual evaporator pinch DT (K)
    - delta_T_approach: Actual superheater approach DT (K)
    - delta_T_econ_pinch: Actual economizer inlet gas-water DT (K)
    - hrsg_effectiveness: Effectiveness of HRSG
    - feasible: Boolean feasibility flag
    """
    Ts = rankine_results['State5']['T']
    T_sat = rankine_results['T_sat_drum']
    T8 = rankine_results['State8']['T']
    
    h5 = rankine_results['State5']['h']
    h_sat_vap = rankine_results['h_sat_vap']
    h_sat_liq = rankine_results['h_sat_liq']
    h8 = rankine_results['State8']['h']
    
    # 1. Superheater approach check:
    delta_T_approach = T_gas_in - Ts
    
    # 2. Evaporator pinch:
    # Gas temperature at evaporator pinch point (gas leaving evaporator / entering economizer):
    T_gas_pinch = T_sat + delta_T_pinch_min
    
    # If gas entering is cooler than pinch temperature, impossible to raise steam:
    if T_gas_in <= T_gas_pinch or delta_T_approach < delta_T_approach_min:
        return {
            'feasible': False,
            'm_dot_steam': 0.0,
            'T_gas_stack': T_gas_in,
            'T_gas_stack_C': T_gas_in - 273.15,
            'Q_hrsg': 0.0,
            'delta_T_pinch': delta_T_approach,
            'delta_T_approach': delta_T_approach,
            'delta_T_econ_pinch': -999.0,
            'hrsg_effectiveness': 0.0,
            'margin_pinch': -10.0,
            'margin_approach': delta_T_approach - delta_T_approach_min,
            'margin_stack': -999.0,
        }
    
    h_gas_in = gas_mix.h_mass(T_gas_in)
    h_gas_pinch = gas_mix.h_mass(T_gas_pinch)
    
    # Heat released by exhaust gas between gas inlet and evaporator pinch:
    # Q_sup+evap = m_dot_gas * (h_gas_in - h_gas_pinch)
    # Steam side: m_dot_steam * (h5 - h_sat_liq)
    delta_h_steam_sup_evap = h5 - h_sat_liq # kJ/kg steam
    
    m_dot_steam = m_dot_gas * (h_gas_in - h_gas_pinch) / delta_h_steam_sup_evap # kg/s
    
    # Component duties:
    Q_sup = m_dot_steam * (h5 - h_sat_vap)       # kW
    Q_evap = m_dot_steam * (h_sat_vap - h_sat_liq) # kW
    Q_econ = m_dot_steam * (h_sat_liq - h8)       # kW
    Q_hrsg = Q_sup + Q_evap + Q_econ             # kW
    
    # Gas leaving economizer (Stack):
    h_gas_stack = h_gas_pinch - (Q_econ / m_dot_gas)
    try:
        T_gas_stack = gas_mix.solve_T_from_h(h_gas_stack, T_guess=T_gas_pinch - 50.0)
    except Exception:
        T_gas_stack = 200.0 # fallback if unphysical
    
    # Gas temperature entering evaporator (leaving superheater):
    h_gas_after_sup = h_gas_in - (Q_sup / m_dot_gas)
    try:
        T_gas_after_sup = gas_mix.solve_T_from_h(h_gas_after_sup, T_guess=T_gas_in - 50.0)
    except Exception:
        T_gas_after_sup = T_gas_in
        
    delta_T_econ_pinch = T_gas_stack - T8
    actual_delta_T_pinch = T_gas_pinch - T_sat
    
    # HRSG Effectiveness:
    # Maximum heat that could be transferred if exhaust cooled to ambient T0 = 298.15 K:
    h_gas_ambient = gas_mix.h_mass(298.15)
    Q_max_possible = m_dot_gas * (h_gas_in - h_gas_ambient)
    hrsg_effectiveness = Q_hrsg / Q_max_possible if Q_max_possible > 0 else 0.0
    
    # Feasibility checks:
    # 1) Stack gas >= 100 C (373.15 K)
    # 2) Gas-water temp diff at economizer inlet > 0
    # 3) delta_T_approach >= 5 K
    feasible = (T_gas_stack >= 373.15) and (delta_T_econ_pinch > 0.0) and (delta_T_approach >= delta_T_approach_min)
    
    return {
        'feasible': feasible,
        'm_dot_steam': m_dot_steam,
        'T_gas_in': T_gas_in,
        'T_gas_after_sup': T_gas_after_sup,
        'T_gas_pinch': T_gas_pinch,
        'T_gas_stack': T_gas_stack,
        'T_gas_stack_C': T_gas_stack - 273.15,
        'Q_sup': Q_sup,
        'Q_evap': Q_evap,
        'Q_econ': Q_econ,
        'Q_hrsg': Q_hrsg,
        'delta_T_pinch': actual_delta_T_pinch,
        'delta_T_approach': delta_T_approach,
        'delta_T_econ_pinch': delta_T_econ_pinch,
        'hrsg_effectiveness': hrsg_effectiveness,
        'margin_pinch': actual_delta_T_pinch - delta_T_pinch_min,
        'margin_approach': delta_T_approach - delta_T_approach_min,
        'margin_stack': T_gas_stack - 373.15, # K above 100 C
    }
