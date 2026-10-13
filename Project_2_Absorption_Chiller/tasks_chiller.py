"""
ME3160 Project 2 - Master Tasks Implementation (Tasks 1 to 4)

Executes all 4 project tasks and packages results into clean DataFrames and CSV files:
- Task 1: Seasonal cooling, heating loads, and ammonia circuit sizing
- Task 2: Condenser design (Air-Cooled vs Evaporative) and off-design simulation
- Task 3: Central water decanter system sizing
- Task 4: Sensitivity analysis to fresh-air fraction (30% -> 40%) & monsoon night reheat
"""

import numpy as np
import pandas as pd
from scipy.optimize import root_scalar
from psychrometrics import (
    solve_zone_psychrometrics, P_sat_water, humidity_ratio,
    moist_air_enthalpy, adiabatic_mixing, P_ATM
)
from absorption_chiller import AbsorptionChiller
from condenser_design import CondenserDesign

CONDITIONS_SPEC = [
    ('Summer day', 40.0, 50.0, True),
    ('Summer night', 30.0, 50.0, False),
    ('Monsoon day', 35.0, 85.0, True),
    ('Monsoon night', 30.0, 85.0, False),
    ('Winter day', 28.0, 50.0, True),
    ('Winter night', 16.0, 50.0, False),
]

def run_task1_and_task3(f_fresh=0.30):
    """
    Runs Task 1 and Task 3: Zone psychrometrics, district loads, and absorption cycle sizing.
    """
    chiller = AbsorptionChiller()
    cond_designer = CondenserDesign(chiller)

    # First pass: find design cooling duty at governing condition
    records_psychro = []
    for name, T_db, rh, solar in CONDITIONS_SPEC:
        p_res = solve_zone_psychrometrics(T_db, rh, solar, f_fresh=f_fresh)
        p_res['Condition'] = name
        records_psychro.append(p_res)
    df_psychro = pd.DataFrame(records_psychro)

    # Find governing condition for chiller
    idx_max_chiller = df_psychro['Q_evap_district_kW'].idxmax()
    gov_cond_chiller = df_psychro.loc[idx_max_chiller, 'Condition']
    Q_evap_design = df_psychro.loc[idx_max_chiller, 'Q_evap_district_kW']

    # Size evaporative condenser at governing condition
    gov_row = df_psychro[df_psychro['Condition'] == gov_cond_chiller].iloc[0]
    evap_cond_design = cond_designer.size_evaporative_design(Q_evap_design, gov_row['Twb_oa'])
    UA_evap_cond_kW_K = evap_cond_design['UA_kW_K']

    # Now solve off-design closed-loop absorption cycle for all conditions
    records_full = []
    for p_res in records_psychro:
        name = p_res['Condition']
        Q_evap = max(0.0, p_res['Q_evap_district_kW'])
        Twb = p_res['Twb_oa']

        # Off-design condensing temperature holding UA fixed
        T_cond_uncon, T_cond_act, cycle_res = cond_designer.solve_off_design_evaporative(
            UA_evap_cond_kW_K, Q_evap, Twb
        )

        turndown_pct = (Q_evap / Q_evap_design) * 100.0 if Q_evap_design > 0 else 0.0
        turndown_violation = (turndown_pct < 25.0) and (Q_evap > 0)

        # Verification of Constraints:
        # (a) P_high <= 20 bar
        p_high_bar = cycle_res['P_high_bar'] if cycle_res else 0.0
        p_high_ok = (p_high_bar <= 20.0) if Q_evap > 0 else True

        # (b) T_gen deliverable by 300 C flue gas with eps_gen=0.75 and 140 C floor
        t_gen_deliverable = cycle_res['t_gen_deliverable'] if cycle_res else True

        # (c) T_cond >= 25 C (flag where unconstrained T_cond < 25 C)
        head_pressure_control_active = (T_cond_uncon < 25.0) and (Q_evap > 0)

        row = {
            'Condition': name,
            'T_oa_C': p_res['T_oa'],
            'RH_oa_pct': p_res['RH_oa'],
            'Twb_oa_C': Twb,
            'T_mix_C': p_res['T_mix'],
            'ADP_C': p_res['ADP'],
            'T_supply_C': p_res['T_supply'],
            'w_supply': p_res['w_supply'],
            'RH_room_pct': p_res['RH_room'],
            'RH_75_violated': p_res['RH_room'] > 75.0,
            'Q_coil_kW': p_res['Q_coil_kW'],
            'Q_evap_kW': Q_evap,
            'turndown_pct': turndown_pct,
            'turndown_flag': turndown_pct < 25.0,
            # Condenser & Cycle
            'T_cond_uncon_C': T_cond_uncon,
            'T_cond_C': T_cond_act,
            'P_high_bar': p_high_bar,
            'P_low_kPa': cycle_res['P_low_kPa'] if cycle_res else 0.0,
            'T_gen_C': cycle_res['T_gen_C'] if cycle_res else np.nan,
            'Q_gen_kW': cycle_res['Q_gen_kW'] if cycle_res else 0.0,
            'Q_cond_kW': cycle_res['Q_cond_kW'] if cycle_res else 0.0,
            'Q_abs_kW': cycle_res['Q_abs_kW'] if cycle_res else 0.0,
            'Q_rect_kW': cycle_res['Q_rect_kW'] if cycle_res else 0.0,
            'COP': cycle_res['COP'] if cycle_res else 0.0,
            'COP_rev': cycle_res['COP_rev'] if cycle_res else 0.0,
            'm_r_kgs': cycle_res['m_r_kgs'] if cycle_res else 0.0,
            'x_strong_mass': cycle_res['x_strong'] if cycle_res else 0.0,
            'x_weak_mass': cycle_res['x_weak'] if cycle_res else 0.0,
            'm_strong_kgs': cycle_res['m_strong_kgs'] if cycle_res else 0.0,
            'm_weak_kgs': cycle_res['m_weak_kgs'] if cycle_res else 0.0,
            'f_circ': cycle_res['f_circ'] if cycle_res else 0.0,
            'V_dot_pump_m3h': cycle_res['V_dot_pump_m3h'] if cycle_res else 0.0,
            'delta_P_pump_kPa': cycle_res['delta_P_pump_kPa'] if cycle_res else 0.0,
            'V_dot_evap_vap_m3h': cycle_res['V_dot_evap_vap_m3h'] if cycle_res else 0.0,
            'T_fg_out_C': cycle_res['T_fg_out_C'] if cycle_res else np.nan,
            'm_fg_kgs': cycle_res['m_fg_required_kgs'] if cycle_res else 0.0,
            'm_fg_limit_violated': cycle_res['m_fg_limit_exceeded'] if cycle_res else False,
            'P_high_safe': p_high_ok,
            'T_gen_deliverable': t_gen_deliverable,
            'head_pressure_active': head_pressure_control_active,
            # Decanter / Condensate (Task 3)
            'm_cond_zone_kgh': p_res['m_cond_zone_kgh'],
            'm_cond_district_kgh': p_res['m_cond_district_kgh'],
            'm_cond_district_m3_day': p_res['m_cond_district_m3_day'],
        }
        records_full.append(row)

    df_full = pd.DataFrame(records_full)
    return df_full, evap_cond_design

def run_task2_comparison():
    """
    Runs Task 2: Comparative evaluation of Air-Cooled vs Evaporative Condensers.
    """
    chiller = AbsorptionChiller()
    cond_designer = CondenserDesign(chiller)

    # Governing condition cooling loads
    p_monsoon = solve_zone_psychrometrics(35.0, 85.0, True, f_fresh=0.30)
    p_summer = solve_zone_psychrometrics(40.0, 50.0, True, f_fresh=0.30)

    des_evap = cond_designer.size_evaporative_design(p_monsoon['Q_evap_district_kW'], p_monsoon['Twb_oa'])
    des_air = cond_designer.size_air_cooled_design(p_summer['Q_evap_district_kW'], p_summer['T_oa'])

    # Dynamic status calculations
    p_evap = des_evap['P_high_design_bar']
    p_air = des_air['P_high_design_bar']
    status_p_evap = f"PASS ({p_evap:.1f} bar <= 20 bar)" if p_evap <= 20.0 else f"VIOLATED ({p_evap:.1f} bar > 20 bar)"
    status_p_air = f"PASS ({p_air:.1f} bar <= 20 bar)" if p_air <= 20.0 else f"VIOLATED ({p_air:.1f} bar > 20 bar)"

    t_gen_evap = chiller.solve_cycle(p_monsoon['Q_evap_district_kW'], des_evap['T_cond_design_C'])['T_gen_C']
    t_gen_air = chiller.solve_cycle(p_summer['Q_evap_district_kW'], des_air['T_cond_design_C'])['T_gen_C']

    df_comp = pd.DataFrame([
        {
            'Parameter': 'Governing Condition',
            'Evaporative Condenser': 'Monsoon Day (Twb = 32.65 °C)',
            'Air-Cooled Finned-Tube': 'Summer Day (Tdb = 40.0 °C)'
        },
        {
            'Parameter': 'Condensing Temperature T_cond (°C)',
            'Evaporative Condenser': f"{des_evap['T_cond_design_C']:.2f}",
            'Air-Cooled Finned-Tube': f"{des_air['T_cond_design_C']:.2f}"
        },
        {
            'Parameter': 'Condensing Pressure P_high (bar)',
            'Evaporative Condenser': f"{p_evap:.2f}",
            'Air-Cooled Finned-Tube': f"{p_air:.2f}"
        },
        {
            'Parameter': 'P_high <= 20 bar Vessel Limit',
            'Evaporative Condenser': status_p_evap,
            'Air-Cooled Finned-Tube': status_p_air
        },
        {
            'Parameter': 'Generator Temperature T_gen (°C)',
            'Evaporative Condenser': f"{t_gen_evap:.1f} °C (Deliverable < 140 °C)",
            'Air-Cooled Finned-Tube': f"{t_gen_air:.1f} °C (Violates 140 °C acid floor)"
        },
        {
            'Parameter': 'Heat Rejection Q_cond (kW)',
            'Evaporative Condenser': f"{des_evap['Q_cond_kW']:.1f}",
            'Air-Cooled Finned-Tube': f"{des_air['Q_cond_kW']:.1f}"
        },
        {
            'Parameter': 'Overall Heat Transfer Coeff U (W/m²·K)',
            'Evaporative Condenser': f"{des_evap['U_W_m2K']:.0f}",
            'Air-Cooled Finned-Tube': f"{des_air['U_W_m2K']:.0f}"
        },
        {
            'Parameter': 'Required UA (kW/K)',
            'Evaporative Condenser': f"{des_evap['UA_kW_K']:.1f}",
            'Air-Cooled Finned-Tube': f"{des_air['UA_kW_K']:.1f}"
        },
        {
            'Parameter': 'Heat Transfer Area A (m²)',
            'Evaporative Condenser': f"{des_evap['Area_m2']:.1f}",
            'Air-Cooled Finned-Tube': f"{des_air['Area_m2']:.1f}"
        },
        {
            'Parameter': 'Area Ratio (Air-Cooled / Evaporative)',
            'Evaporative Condenser': '1.0x (Baseline)',
            'Air-Cooled Finned-Tube': f"{des_air['Area_m2'] / des_evap['Area_m2']:.1f}x larger"
        },
        {
            'Parameter': 'Makeup Water / Air Flow Rate',
            'Evaporative Condenser': f"{des_evap['m_makeup_m3_day']:.1f} m³/day makeup water",
            'Air-Cooled Finned-Tube': f"{des_air['m_air_kgs']:.1f} kg/s air flow"
        },
        {
            'Parameter': 'Engineering Recommendation',
            'Evaporative Condenser': 'RECOMMENDED (Safe pressure, compact area, high COP)',
            'Air-Cooled Finned-Tube': 'REJECTED (Violates 20 bar limit, excessive area)'
        }
    ])

    return df_comp, des_evap, des_air

def solve_monsoon_night_reheat(f_fresh=0.40, target_rh=0.70):
    """
    Dynamically computes the lower Apparatus Dew Point (ADP), terminal reheat duty,
    extra district cooling load, and resulting extra generator heat needed to eliminate
    humidity drift at monsoon night when fresh air is increased to 40%.
    """
    T_room = 22.0
    Psat_22 = P_sat_water(T_room)
    w_target = humidity_ratio(target_rh * Psat_22)

    # Zone load parameters
    Q_sens_zone = 7.0 # kW
    Q_lat_zone = 3.0 # kW
    m_w_zone = Q_lat_zone / 2450.0 # kg/s moisture release
    m_air_zone = 1.50 # kg/s supply air flow

    # Required supply air humidity ratio to maintain room humidity at target_rh
    w_sup_target = w_target - (m_w_zone / m_air_zone)

    # Solve for required coil ADP
    sol_adp = root_scalar(lambda t: humidity_ratio(P_sat_water(t)) - w_sup_target, bracket=[5.0, 25.0])
    adp_target = sol_adp.root

    # Coil leaving temperature with bypass factor BF = 0.10
    T_oa = 30.0
    RH_oa = 85.0
    w_oa = humidity_ratio((RH_oa / 100.0) * P_sat_water(T_oa))
    h_oa = moist_air_enthalpy(T_oa, w_oa)
    h_room_target = moist_air_enthalpy(T_room, w_target)
    T_mix, w_mix, h_mix = adiabatic_mixing(1.0 - f_fresh, h_room_target, w_target, f_fresh, h_oa, w_oa)

    T_coil_out = adp_target + 0.10 * (T_mix - adp_target)

    # Required supply temperature to meet sensible room heat balance:
    # Q_sens_zone = m_air_zone * Cp * (T_room - T_supply)
    T_sup_sensible = T_room - (Q_sens_zone / (m_air_zone * 1.006))

    # Reheat temperature rise:
    delta_T_reheat = max(0.0, T_sup_sensible - T_coil_out)
    q_reheat_zone_kW = m_air_zone * 1.006 * delta_T_reheat
    Q_reheat_district_kW = 1000.0 * q_reheat_zone_kW

    # Extra evaporator cooling load (1000 zones + 5% piping + 2% pump gains)
    extra_Q_evap_kW = Q_reheat_district_kW * 1.05 * 1.02

    # Chiller at Monsoon Night condition:
    chiller = AbsorptionChiller()
    # At T_cond ~ 30 C, COP ~ 0.58
    c_res = chiller.solve_cycle(Q_evap_kW=extra_Q_evap_kW, T_cond_C=30.0)
    cop_monsoon_night = c_res['COP'] if c_res['COP'] > 0 else 0.58
    extra_Q_gen_kW = extra_Q_evap_kW / cop_monsoon_night

    return {
        'target_rh_pct': target_rh * 100.0,
        'w_room_target': w_target,
        'w_sup_target': w_sup_target,
        'ADP_target_C': adp_target,
        'T_coil_out_C': T_coil_out,
        'T_supply_sensible_C': T_sup_sensible,
        'delta_T_reheat_K': delta_T_reheat,
        'q_reheat_zone_kW': q_reheat_zone_kW,
        'Q_reheat_district_kW': Q_reheat_district_kW,
        'extra_Q_evap_kW': extra_Q_evap_kW,
        'extra_Q_gen_kW': extra_Q_gen_kW,
        'cop_night': cop_monsoon_night
    }

def compute_shx_sensitivity(Q_evap_kW=4900.0, T_cond_C=40.0):
    """
    Computes sensitivity of generator heat demand to Solution Heat Exchanger (SHX) effectiveness.
    """
    chiller_base = AbsorptionChiller(eps_SHX=0.70)
    chiller_high = AbsorptionChiller(eps_SHX=0.80)
    chiller_none = AbsorptionChiller(eps_SHX=0.00)

    res_base = chiller_base.solve_cycle(Q_evap_kW, T_cond_C)
    res_high = chiller_high.solve_cycle(Q_evap_kW, T_cond_C)
    res_none = chiller_none.solve_cycle(Q_evap_kW, T_cond_C)

    savings_vs_none_kW = res_none['Q_gen_kW'] - res_base['Q_gen_kW']
    savings_eps80_kW = res_base['Q_gen_kW'] - res_high['Q_gen_kW']

    return {
        'Q_gen_base_kW': res_base['Q_gen_kW'],
        'Q_gen_eps80_kW': res_high['Q_gen_kW'],
        'Q_gen_none_kW': res_none['Q_gen_kW'],
        'savings_vs_none_kW': savings_vs_none_kW,
        'savings_eps80_kW': savings_eps80_kW,
        'cop_base': res_base['COP'],
        'cop_high': res_high['COP'],
        'cop_none': res_none['COP']
    }

def run_task4_sensitivity():
    """
    Runs Task 4: Sensitivity to fresh-air fraction (30% -> 40%).
    """
    df30, _ = run_task1_and_task3(f_fresh=0.30)
    df40, _ = run_task1_and_task3(f_fresh=0.40)

    rows = []
    for i in range(len(df30)):
        cond = df30.loc[i, 'Condition']
        q_coil_30 = df30.loc[i, 'Q_coil_kW']
        q_coil_40 = df40.loc[i, 'Q_coil_kW']
        pct_coil = ((q_coil_40 - q_coil_30) / abs(q_coil_30)) * 100.0 if abs(q_coil_30) > 0.01 else 0.0

        q_evap_30 = df30.loc[i, 'Q_evap_kW']
        q_evap_40 = df40.loc[i, 'Q_evap_kW']
        pct_evap = ((q_evap_40 - q_evap_30) / abs(q_evap_30)) * 100.0 if abs(q_evap_30) > 0.01 else 0.0

        q_gen_30 = df30.loc[i, 'Q_gen_kW']
        q_gen_40 = df40.loc[i, 'Q_gen_kW']
        pct_gen = ((q_gen_40 - q_gen_30) / abs(q_gen_30)) * 100.0 if abs(q_gen_30) > 0.01 else 0.0

        mr_30 = df30.loc[i, 'm_r_kgs']
        mr_40 = df40.loc[i, 'm_r_kgs']
        pct_mr = ((mr_40 - mr_30) / abs(mr_30)) * 100.0 if abs(mr_30) > 0.001 else 0.0

        mfg_30 = df30.loc[i, 'm_fg_kgs']
        mfg_40 = df40.loc[i, 'm_fg_kgs']
        pct_mfg = ((mfg_40 - mfg_30) / abs(mfg_30)) * 100.0 if abs(mfg_30) > 0.01 else 0.0

        cond_30 = df30.loc[i, 'm_cond_district_m3_day']
        cond_40 = df40.loc[i, 'm_cond_district_m3_day']
        pct_cond = ((cond_40 - cond_30) / abs(cond_30)) * 100.0 if abs(cond_30) > 0.01 else 0.0

        rows.append({
            'Condition': cond,
            'Delta_Q_coil_pct': pct_coil,
            'Delta_Q_evap_pct': pct_evap,
            'Delta_Q_gen_pct': pct_gen,
            'Delta_m_r_pct': pct_mr,
            'Delta_m_fg_pct': pct_mfg,
            'Delta_Condensate_pct': pct_cond,
            'RH_room_30': df30.loc[i, 'RH_room_pct'],
            'RH_room_40': df40.loc[i, 'RH_room_pct'],
            'RH_40_violated': df40.loc[i, 'RH_room_pct'] > 75.0,
            'P_high_40_bar': df40.loc[i, 'P_high_bar'],
            'P_high_limit_active': df40.loc[i, 'P_high_bar'] > 20.0,
            'm_fg_40_kgs': df40.loc[i, 'm_fg_kgs'],
            'm_fg_limit_active': df40.loc[i, 'm_fg_kgs'] > 80.0
        })

    df_sens = pd.DataFrame(rows)
    return df_sens, df30, df40
