"""
combined_cycle.py
Direct physical model of the methane-fired combined cycle plant.
Topping open Brayton cycle + HRSG pinch analysis + bottoming Rankine cycle.
"""

import numpy as np
from thermo_gas import solve_brayton_cycle, GasMixture
from rankine_cycle import solve_rankine_cycle
from hrsg import solve_hrsg

def direct_model(rp, TIT, Ps, Ts, Pcond, hrsg_limit_C=650.0, m_dot_air=100.0):
    """
    Direct combined cycle plant simulation.
    
    Inputs:
    - rp: Compression pressure ratio (8 - 30)
    - TIT: Turbine inlet temperature in K (1200 - 1500 K)
    - Ps: Steam drum pressure in bar (10 - 60 bar)
    - Ts: Superheat outlet temperature in K
    - Pcond: Condenser pressure in bar (0.05 - 0.15 bar)
    - hrsg_limit_C: Maximum gas temperature entering HRSG in deg C (default 650 C)
    - m_dot_air: Ambient air mass flow rate in kg/s (default 100 kg/s)
    
    Returns:
    (eta_cc, Wnet, margins, feasible, details)
    where:
    - eta_cc: Overall combined-cycle thermal efficiency (fraction)
    - Wnet: Total net electrical/shaft power (kW)
    - margins: dict of the 6 constraint margins
    - feasible: bool indicating feasibility
    - details: comprehensive dictionary of state points and component metrics
    """
    # 1. Solve Topping Brayton Cycle:
    gt = solve_brayton_cycle(rp=rp, TIT=TIT)
    
    m_dot_fuel = m_dot_air * gt['f_A']             # kg/s
    m_dot_gas = m_dot_air * (1.0 + gt['f_A'])       # kg/s
    W_gt_net = m_dot_air * gt['w_gt_net']          # kW
    Q_fuel_lhv = m_dot_fuel * 50000.0              # kW (LHV = 50 MJ/kg)
    
    T4 = gt['T4']                                  # K (gas entering HRSG)
    T4_C = T4 - 273.15                             # deg C
    
    # 2. Solve Bottoming Rankine Cycle:
    try:
        st = solve_rankine_cycle(Ps_bar=Ps, Ts_K=Ts, Pcond_bar=Pcond)
    except Exception as e:
        # If CoolProp fails on extreme inputs
        margins = {
            'c1_TIT': 1550.0 - TIT,
            'c2_HRSG_inlet': hrsg_limit_C - T4_C,
            'c3_stack_temp': -999.0,
            'c4_pinch_approach': -999.0,
            'c5_steam_quality': -1.0,
            'c6_equiv_ratio': 0.5 - gt['phi'],
        }
        return 0.0, 0.0, margins, False, {'error': str(e)}

    # 3. Solve HRSG Pinch Analysis:
    hrsg = solve_hrsg(
        gas_mix=gt['prod_mix'],
        T_gas_in=T4,
        m_dot_gas=m_dot_gas,
        rankine_results=st,
        delta_T_pinch_min=10.0,
        delta_T_approach_min=5.0
    )
    
    m_dot_steam = hrsg['m_dot_steam'] # kg/s
    W_st_net = m_dot_steam * st['w_net'] # kW
    
    # 4. Total Plant Performance:
    W_net_total = W_gt_net + W_st_net # kW
    eta_cc = W_net_total / Q_fuel_lhv if Q_fuel_lhv > 0 else 0.0
    
    specific_work = W_net_total / m_dot_air # kJ/kg air
    bottoming_topping_ratio = W_st_net / W_gt_net if W_gt_net > 0 else 0.0
    
    # 5. Evaluate the 6 Practical Constraints:
    # i. TIT <= 1550 K
    g1 = 1550.0 - TIT
    
    # ii. Gas entering HRSG <= hrsg_limit_C (default 650 C)
    g2 = hrsg_limit_C - T4_C
    
    # iii. Stack gas >= 100 C
    g3 = hrsg['T_gas_stack_C'] - 100.0
    
    # iv. Pinch >= 10 K and Approach >= 5 K
    g4 = min(hrsg['margin_pinch'], hrsg['margin_approach'])
    
    # v. Steam turbine vapor quality >= 0.88
    g5 = st['x6'] - 0.88
    
    # vi. Equivalence ratio phi <= 0.5
    g6 = 0.5 - gt['phi']
    
    margins = {
        'c1_TIT': g1,
        'c2_HRSG_inlet': g2,
        'c3_stack_temp': g3,
        'c4_pinch_approach': g4,
        'c5_steam_quality': g5,
        'c6_equiv_ratio': g6,
    }
    
    # Feasibility: all margins >= 0 AND HRSG valid
    feasible = (g1 >= -1e-6 and g2 >= -1e-6 and g3 >= -1e-6 and 
                g4 >= -1e-6 and g5 >= -1e-6 and g6 >= -1e-6 and 
                hrsg['feasible'] and m_dot_steam > 0)
    
    details = {
        'gt': gt,
        'st': st,
        'hrsg': hrsg,
        'm_dot_air': m_dot_air,
        'm_dot_fuel': m_dot_fuel,
        'm_dot_gas': m_dot_gas,
        'm_dot_steam': m_dot_steam,
        'W_gt_net': W_gt_net,
        'W_st_net': W_st_net,
        'W_net_total': W_net_total,
        'Q_fuel_lhv': Q_fuel_lhv,
        'eta_cc': eta_cc,
        'specific_work': specific_work,
        'bottoming_topping_ratio': bottoming_topping_ratio,
        'hrsg_effectiveness': hrsg['hrsg_effectiveness'],
        'T4_C': T4_C,
        'T_stack_C': hrsg['T_gas_stack_C'],
        'x6': st['x6'],
        'phi': gt['phi'],
    }
    
    return eta_cc, W_net_total, margins, feasible, details
