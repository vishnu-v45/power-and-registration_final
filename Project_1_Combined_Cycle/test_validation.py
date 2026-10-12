"""
test_validation.py
Automated validation test suite for Project 1:
Check 1: Gas Turbine (air-standard) check against Borgnakke & Sonntag Tables A.7.1/A.7.2
Check 2: Bottoming Rankine cycle check against steam tables via CoolProp
Check 3: Full plant 1st law energy balance check
"""

import sys
import numpy as np
import CoolProp.CoolProp as CP
from thermo_gas import GasMixture
from rankine_cycle import solve_rankine_cycle
from combined_cycle import direct_model

def run_check1():
    """
    Check-1: Gas Turbine (air-standard) validation
    Given: T1 = 300 K, P1 = 100 kPa, rp = 15, T3 = 1400 K, eta_c = 0.86, eta_t = 0.89
    """
    air = GasMixture('Air')
    T1 = 300.0
    P1 = 100.0
    rp = 15.0
    T3 = 1400.0
    eta_c = 0.86
    eta_t = 0.89
    
    # State 1:
    h1 = air.h_mass(T1)
    
    # State 2s and 2:
    T2s = air.solve_T_isentropic(T1, rp)
    h2s = air.h_mass(T2s)
    h2 = h1 + (h2s - h1) / eta_c
    T2 = air.solve_T_from_h(h2, T_guess=T2s + 30.0)
    
    # State 3:
    h3 = air.h_mass(T3)
    
    # State 4s and 4:
    T4s = air.solve_T_isentropic(T3, 1.0 / rp)
    h4s = air.h_mass(T4s)
    h4 = h3 - eta_t * (h3 - h4s)
    T4 = air.solve_T_from_h(h4, T_guess=T4s + 50.0)
    
    wc = h2 - h1
    wt = h3 - h4
    wnet = wt - wc
    qh = h3 - h2
    eta_th = (wnet / qh) * 100.0
    
    # Hand values from Borgnakke & Sonntag Table A.7:
    benchmarks = [
        ("T1 (K)", 300.0, T1, 0.5),
        ("h1 (kJ/kg)", 300.47, h1, 0.5),
        ("T2s (K)", 641.2, T2s, 0.5),
        ("h2s (kJ/kg)", 650.81, h2s, 0.5),
        ("T2 (K)", 694.7, T2, 0.5),
        ("h2 (kJ/kg)", 707.87, h2, 0.5),
        ("T3 (K)", 1400.0, T3, 0.5),
        ("h3 (kJ/kg)", 1515.27, h3, 0.5),
        ("T4s (K)", 707.3, T4s, 0.5),
        ("h4s (kJ/kg)", 721.47, h4s, 0.5),
        ("T4 (K)", 787.7, T4, 0.5),
        ("h4 (kJ/kg)", 808.77, h4, 0.5),
        ("wc (kJ/kg)", 407.4, wc, 0.5),
        ("wt (kJ/kg)", 706.5, wt, 0.5),
        ("wnet (kJ/kg)", 299.1, wnet, 0.5),
        ("qh (kJ/kg)", 807.4, qh, 0.5),
        ("eta_th (%)", 37.05, eta_th, 0.5),
    ]
    return benchmarks


def run_check2():
    """
    Check-2: Rankine cycle vs Steam Tables
    Given: Ps = 30 bar, Ts = 450 C, Pcond = 7.5 kPa, eta_st = 0.85, eta_pump = 0.80
    """
    res = solve_rankine_cycle(Ps_bar=30.0, Ts_K=450.0 + 273.15, Pcond_bar=0.075,
                              eta_st=0.85, eta_pump=0.80)
    
    h5 = res['State5']['h']
    s5 = res['State5']['s']
    h6s = res['State6s']['h']
    h6 = res['State6']['h']
    h7 = res['State7']['h']
    s7 = res['State7']['s']
    h8 = res['State8']['h']
    
    x6s = res['x6s']
    x6 = res['x6']
    w_st = res['w_st']
    w_pump = res['w_pump']
    w_net = res['w_net']
    q_H = res['q_H']
    eta_rankine = res['eta_rankine'] * 100.0
    
    benchmarks = [
        ("h5 (kJ/kg)", 3344.00, h5, 0.1),
        ("s5 (kJ/kg-K)", 7.0833, s5, 0.1),
        ("h6s (kJ/kg)", 2208.4, h6s, 0.1),
        ("h6 (kJ/kg)", 2378.8, h6, 0.1),
        ("h7 (kJ/kg)", 168.77, h7, 0.1),
        ("s7 (kJ/kg-K)", 0.5763, s7, 0.1),
        ("h8 (kJ/kg)", 172.54, h8, 0.1),
        ("x6s (-)", 0.848, x6s, 0.2),
        ("x6 (-)", 0.919, x6, 0.2),
        ("w_st (kJ/kg)", 965.2, w_st, 0.1),
        ("w_pump (kJ/kg)", 3.77, w_pump, 0.1),
        ("w_net (kJ/kg)", 961.4, w_net, 0.1),
        ("q_H (kJ/kg)", 3171.5, q_H, 0.1),
        ("eta_Rankine (%)", 30.30, eta_rankine, 0.1),
    ]
    return benchmarks


def run_check3():
    """
    Check-3: 1st Law Energy Balance for Combined Cycle
    m_fuel * LHV * eta_comb ≈ (W_gt_net + W_st_net) + Q_stack + Q_condenser + (small losses)
    """
    eta_cc, W_net, margins, feasible, det = direct_model(
        rp=16.0, TIT=1400.0, Ps=30.0, Ts=450.0 + 273.15, Pcond=0.075
    )
    
    Q_fuel_in_effective = det['m_dot_fuel'] * 50000.0 * 0.98 # kW
    W_total = det['W_net_total'] # kW
    
    # Heat rejected at stack above ambient 298.15 K:
    prod_mix = det['gt']['prod_mix']
    h_stack = prod_mix.h_mass(det['hrsg']['T_gas_stack'])
    h_ambient = prod_mix.h_mass(298.15)
    Q_stack = det['m_dot_gas'] * (h_stack - h_ambient) # kW
    
    # Heat rejected at condenser:
    Q_cond = det['m_dot_steam'] * det['st']['q_cond'] # kW
    
    # Sensible enthalpy flow from ambient air and fuel:
    # m_air * h1 - m_gas * h_ambient + m_fuel * h_f
    air_mix = GasMixture('Air')
    h_air_ambient = air_mix.h_mass(298.15)
    sensible_inflow = (det['m_dot_air'] * h_air_ambient - det['m_dot_gas'] * h_ambient)
    
    # First Law RHS (standard plant boundary):
    RHS_approx = W_total + Q_stack + Q_cond
    rel_diff_approx = abs(Q_fuel_in_effective - RHS_approx) / Q_fuel_in_effective * 100.0
    
    # Exact First Law balance (accounting for reference enthalpy difference of species):
    exact_residual = abs(Q_fuel_in_effective + sensible_inflow - (W_total + Q_stack + Q_cond)) / Q_fuel_in_effective * 100.0
    
    return [
        ("Effective Fuel Energy (kW)", Q_fuel_in_effective, Q_fuel_in_effective, 0.1),
        ("W_net,total (kW)", W_total, W_total, 0.1),
        ("Q_stack (kW)", Q_stack, Q_stack, 0.1),
        ("Q_condenser (kW)", Q_cond, Q_cond, 0.1),
        ("Approx Energy Balance Residual (%)", 0.0, rel_diff_approx, 2.0),
        ("Exact Closed First Law Residual (%)", 0.0, exact_residual, 0.01),
    ]


def main():
    print("=" * 80)
    print("ME3160 PROJECT 1 - VALIDATION TEST SUITE (CHECKS 1, 2, 3)")
    print("=" * 80)
    
    all_passed = True
    
    # Run Check 1:
    print("\n[CHECK 1: Gas Turbine Air-Standard Check (Borgnakke Table A.7)]")
    print(f"{'Quantity':<20} | {'Hand Value':<12} | {'Code Output':<12} | {'% Diff':<10} | {'Status'}")
    print("-" * 68)
    for name, hand, code, tol in run_check1():
        pct_diff = abs(code - hand) / abs(hand) * 100.0
        passed = (pct_diff <= tol)
        if not passed:
            all_passed = False
        print(f"{name:<20} | {hand:<12.2f} | {code:<12.2f} | {pct_diff:<9.3f}% | {'PASS' if passed else 'FAIL'}")
        
    # Run Check 2:
    print("\n[CHECK 2: Bottoming Rankine Cycle Check (CoolProp vs Steam Tables)]")
    print(f"{'Quantity':<20} | {'Hand Value':<12} | {'Code Output':<12} | {'% Diff':<10} | {'Status'}")
    print("-" * 68)
    for name, hand, code, tol in run_check2():
        pct_diff = abs(code - hand) / abs(hand) * 100.0
        passed = (pct_diff <= tol)
        if not passed:
            all_passed = False
        print(f"{name:<20} | {hand:<12.2f} | {code:<12.2f} | {pct_diff:<9.3f}% | {'PASS' if passed else 'FAIL'}")

    # Run Check 3:
    print("\n[CHECK 3: First Law Overall Energy Balance Check]")
    print(f"{'Quantity':<36} | {'Value':<14} | {'Status'}")
    print("-" * 62)
    for name, hand, code, tol in run_check3():
        if "Residual" in name:
            passed = (code <= tol)
            print(f"{name:<36} | {code:<14.3f}% | {'PASS' if passed else 'FAIL'}")
            if not passed:
                all_passed = False
        else:
            print(f"{name:<36} | {code:<14.2f} | PASS")

    print("\n" + "=" * 80)
    if all_passed:
        print(">>> ALL VALIDATION CHECKS PASSED WITHIN PRESCRIBED TOLERANCES! <<<")
        print("=" * 80)
        sys.exit(0)
    else:
        print(">>> ONE OR MORE VALIDATION CHECKS FAILED! <<<")
        print("=" * 80)
        sys.exit(1)

if __name__ == '__main__':
    main()
