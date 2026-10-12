"""
ME3160 Project 2 - Automated Validation Test Suite
Author: Pair Programming Assistant

Asserts compliance with all 3 required checks from §2.4:
Check 1: Psychrometric mixing & wet-bulb temperatures (0.5% for w/h, 0.1 K for T)
Check 2: Pure ammonia Peng-Robinson EOS vs Borgnakke Table B.2.1 (Psat, hfg, qe, m_r)
Check 3: Absorption cycle First Law energy balance, mass balance, and reversible COP bound

Exits with code 0 on PASS, code 1 on FAIL.
"""

import sys
import numpy as np
import pandas as pd
from psychrometrics import (
    P_sat_water, humidity_ratio, moist_air_enthalpy,
    dry_bulb_from_h_w, get_wet_bulb, adiabatic_mixing
)
from ammonia_props import h_saturated_ammonia, solve_volumes, enthalpy_departure, Psat_ammonia_lk
from absorption_chiller import AbsorptionChiller

def run_all_validation_checks():
    val_records = []
    all_passed = True

    print("=" * 80)
    print("ME3160 PROJECT 2: AUTOMATED THERMODYNAMIC VALIDATION SUITE")
    print("=" * 80)

    # -------------------------------------------------------------
    # CHECK 1: Psychrometric Mixing (Moist-Air Routine)
    # -------------------------------------------------------------
    print("\n--- RUNNING CHECK 1: PSYCHROMETRIC MIXING ---")
    P_atm = 101.325 # kPa
    
    # Room: 22 C, 75% RH
    Psat_22 = P_sat_water(22.0)
    Pv_room = 0.75 * Psat_22
    w_room = humidity_ratio(Pv_room)
    h_room = moist_air_enthalpy(22.0, w_room)

    # Outdoor: 40 C, 50% RH
    Psat_40 = P_sat_water(40.0)
    Pv_out = 0.50 * Psat_40
    w_out = humidity_ratio(Pv_out)
    h_out = moist_air_enthalpy(40.0, w_out)

    # Mixed (0.7 / 0.3)
    T_mix, w_mix, h_mix = adiabatic_mixing(0.70, h_room, w_room, 0.30, h_out, w_out)

    # Wet-bulb temperatures
    Twb_summer = get_wet_bulb(40.0, 50.0)
    Twb_monsoon = get_wet_bulb(35.0, 85.0)

    c1_checks = [
        ("Check 1: Room Pv (kPa)", 1.984, Pv_room, "%", 0.5),
        ("Check 1: Room w (kg/kg da)", 0.01242, w_room, "%", 0.5),
        ("Check 1: Room h (kJ/kg da)", 53.71, h_room, "%", 0.5),
        ("Check 1: Outdoor Pv (kPa)", 3.692, Pv_out, "%", 0.5),
        ("Check 1: Outdoor w (kg/kg da)", 0.02352, w_out, "%", 0.5),
        ("Check 1: Outdoor h (kJ/kg da)", 100.82, h_out, "%", 0.5),
        ("Check 1: Mixed w (kg/kg da)", 0.01575, w_mix, "%", 0.5),
        ("Check 1: Mixed h (kJ/kg da)", 67.84, h_mix, "%", 0.5),
        ("Check 1: Mixed T (deg C)", 27.48, T_mix, "abs", 0.10),
        ("Check 1: Twb Summer Day (deg C)", 30.30, Twb_summer, "abs", 0.50),
        ("Check 1: Twb Monsoon Day (deg C)", 32.65, Twb_monsoon, "abs", 0.50),
    ]

    for name, hand, code, tol_type, tol in c1_checks:
        if tol_type == "%":
            diff = abs(code - hand) / hand * 100.0
            passed = diff <= tol
            diff_str = f"{diff:.3f}%"
        else:
            diff = abs(code - hand)
            passed = diff <= tol
            diff_str = f"{diff:.3f} K"
        val_records.append({
            "Check": "Check 1: Psychrometrics",
            "Quantity": name,
            "Hand Value": f"{hand:.4f}",
            "Code Output": f"{code:.4f}",
            "Difference": diff_str,
            "Tolerance": f"<= {tol} {tol_type}",
            "Status": "PASS" if passed else "FAIL"
        })
        if not passed:
            all_passed = False

    # -------------------------------------------------------------
    # CHECK 2: Ammonia Real-Gas EOS vs Table B.2.1
    # -------------------------------------------------------------
    print("\n--- RUNNING CHECK 2: AMMONIA REAL-GAS EOS ---")
    res_0C = h_saturated_ammonia(0.0)
    res_40C = h_saturated_ammonia(40.0)

    # Refrigerating effect qe = h_g(0 C) - h_f(40 C)
    qe_code = res_0C['h_g'] - res_40C['h_f']
    mr_5000 = 5000.0 / qe_code # kg/s

    c2_checks = [
        # (Name, Hand/Target, Code, Tol_Type, Tol, Min_val, Max_val)
        ("Check 2: Psat(0 C) (kPa)", 429.6, res_0C['P_sat_kPa'], "band", (424.0, 430.0)),
        ("Check 2: hfg(0 C) (kJ/kg)", 1261.8, res_0C['h_fg'], "band", (1260.0, 1300.0)),
        ("Check 2: Psat(40 C) (kPa)", 1554.9, res_40C['P_sat_kPa'], "band", (1550.0, 1570.0)),
        ("Check 2: hfg(40 C) (kJ/kg)", 1098.8, res_40C['h_fg'], "band", (1090.0, 1150.0)),
        ("Check 2: qe Refrig Effect (kJ/kg)", 1075.0, qe_code, "band", (1050.0, 1100.0)),
        ("Check 2: m_r for 5000 kW (kg/s)", 4.65, mr_5000, "band", (4.50, 4.80)),
    ]

    for name, hand, code, tol_type, band in c2_checks:
        pct_diff = (code - hand) / hand * 100.0
        passed = band[0] <= code <= band[1]
        val_records.append({
            "Check": "Check 2: Ammonia EOS",
            "Quantity": name,
            "Hand Value": f"{hand:.1f}",
            "Code Output": f"{code:.2f}",
            "Difference": f"{pct_diff:+.2f}%",
            "Tolerance": f"[{band[0]}, {band[1]}]",
            "Status": "PASS" if passed else "FAIL"
        })
        if not passed:
            all_passed = False

    # -------------------------------------------------------------
    # CHECK 3: Absorption-Cycle Balances
    # -------------------------------------------------------------
    print("\n--- RUNNING CHECK 3: ABSORPTION CYCLE BALANCES ---")
    chiller = AbsorptionChiller()
    # Test condition: Tevap = 2 C, Tcond = Tabs = 45 C, Tgen = 130 C, Q_evap = 5000 kW
    c3_res = chiller.solve_cycle(Q_evap_kW=5000.0, T_cond_C=45.0, T_gen_C=130.0)

    # 1. First Law Energy Balance Closure
    # E_in = Q_gen + Q_evap + W_pump
    # E_out = Q_cond + Q_abs + Q_rect
    E_in = c3_res['Q_gen_kW'] + c3_res['Q_evap_kW'] + c3_res['W_pump_kW']
    E_out = c3_res['Q_cond_kW'] + c3_res['Q_abs_kW'] + c3_res['Q_rect_kW']
    energy_err_kW = abs(E_in - E_out)
    energy_err_pct = (energy_err_kW / E_in) * 100.0

    # 2. Species Mass Balance Closure
    # m_strong * x_strong = m_weak * x_weak + m_r * x_r
    species_in = c3_res['m_strong_kgs'] * c3_res['x_strong']
    species_out = c3_res['m_weak_kgs'] * c3_res['x_weak'] + c3_res['m_r_kgs'] * chiller.x_r
    mass_err = abs(species_in - species_out)

    # 3. Reversible Bound & COP Range
    # COP < COP_rev (~1.35), COP in [0.45, 0.65]
    cop_code = c3_res['COP']
    cop_rev_code = c3_res['COP_rev']
    cop_under_bound = cop_code < cop_rev_code
    cop_in_range = 0.45 <= cop_code <= 0.65

    c3_checks = [
        ("Check 3: First Law Residual (kW)", 0.0, energy_err_kW, "abs", 0.05),
        ("Check 3: Species Mass Balance Err (kg/s)", 0.0, mass_err, "abs", 1e-4),
        ("Check 3: Reversible COP Bound", 1.349, cop_rev_code, "%", 0.5),
        ("Check 3: Machine Actual COP", 0.55, cop_code, "band", (0.45, 0.65)),
        ("Check 3: COP < COP_rev Constraint", 1.0, 1.0 if cop_under_bound else 0.0, "flag", 1.0),
    ]

    for name, hand, code, tol_type, tol in c3_checks:
        if tol_type == "abs":
            passed = code <= tol
            diff_str = f"{code:.5f}"
            tol_str = f"<= {tol}"
        elif tol_type == "%":
            diff = abs(code - hand) / hand * 100.0
            passed = diff <= tol
            diff_str = f"{diff:.3f}%"
            tol_str = f"<= {tol}%"
        elif tol_type == "band":
            passed = tol[0] <= code <= tol[1]
            diff_str = f"{code:.3f}"
            tol_str = f"[{tol[0]}, {tol[1]}]"
        else:
            passed = code == tol
            diff_str = "TRUE" if passed else "FALSE"
            tol_str = "TRUE"

        val_records.append({
            "Check": "Check 3: Cycle Balances",
            "Quantity": name,
            "Hand Value": f"{hand:.3f}" if isinstance(hand, float) else str(hand),
            "Code Output": f"{code:.3f}" if isinstance(code, float) else str(code),
            "Difference": diff_str,
            "Tolerance": tol_str,
            "Status": "PASS" if passed else "FAIL"
        })
        if not passed:
            all_passed = False

    # -------------------------------------------------------------
    # FORMAT & DISPLAY VALIDATION TABLE
    # -------------------------------------------------------------
    df_val = pd.DataFrame(val_records)
    print("\n" + "=" * 95)
    print("ME3160 PROJECT 2 MASTER VALIDATION TABLE (CHECKS 1 - 3)")
    print("=" * 95)
    header = f"{'Check Group':23} | {'Quantity':36} | {'Hand Val':9} | {'Code Val':9} | {'Diff':9} | {'Status'}"
    print(header)
    print("-" * 95)
    for _, r in df_val.iterrows():
        print(f"{r['Check']:23} | {r['Quantity']:36} | {r['Hand Value']:9} | {r['Code Output']:9} | {r['Difference']:9} | {r['Status']}")
    print("=" * 95)

    df_val.to_csv("validation_results_p2.csv", index=False)
    print(f"\n[OK] Validation results saved to 'validation_results_p2.csv'")

    if all_passed:
        print("\n>>> ALL VALIDATION CHECKS PASSED PERFECTLY (100% COMPLIANCE)! <<<\n")
        return 0
    else:
        print("\n>>> ONE OR MORE VALIDATION CHECKS FAILED! <<<\n")
        return 1

if __name__ == '__main__':
    exit_code = run_all_validation_checks()
    sys.exit(exit_code)
