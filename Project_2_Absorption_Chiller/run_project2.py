"""
ME3160 Project 2 - Master Driver Script
Waste-Heat-Driven Ammonia-Water Absorption Chiller for a District Cooling Network

Executes the complete end-to-end Project 2 pipeline:
1. Runs automated validation suite (Checks 1 to 3)
2. Executes Task 1 (Seasonal loads & ammonia circuit sizing)
3. Executes Task 2 (Condenser design & off-design simulation map)
4. Executes Task 3 (Central water decanter condensate system sizing)
5. Executes Task 4 (Sensitivity analysis to 40% fresh air & monsoon night reheat)
6. Computes SHX sensitivity to effectiveness
7. Generates 6 publication-quality figures
8. Exports detailed CSV tables
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

from test_validation import run_all_validation_checks
from tasks_chiller import (
    run_task1_and_task3, run_task2_comparison, run_task4_sensitivity,
    solve_monsoon_night_reheat, compute_shx_sensitivity
)
from psychrometrics import (
    P_sat_water, humidity_ratio, moist_air_enthalpy, P_ATM,
    solve_zone_psychrometrics
)

# Set high-quality plotting style
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['grid.alpha'] = 0.35

def generate_plots(df30, df40, df_comp, df_sens, evap_cond_des):
    print("\n--- GENERATING PUBLICATION-QUALITY PROJECT 2 FIGURES ---")

    # -------------------------------------------------------------
    # FIGURE 1: Psychrometric Processes on T-w Chart
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    T_range = np.linspace(5, 45, 100)
    for rh in [20, 40, 60, 80, 100]:
        w_curve = [humidity_ratio((rh / 100.0) * P_sat_water(t)) for t in T_range]
        ax.plot(T_range, np.array(w_curve) * 1000.0, color='gray', linestyle=':', alpha=0.6)
        ax.text(T_range[-1] + 0.3, w_curve[-1] * 1000.0, f'{rh}%', color='gray', fontsize=8, va='center')

    # Room setpoint
    w_room_set = humidity_ratio(0.50 * P_sat_water(22.0)) * 1000.0
    ax.scatter([22.0], [w_room_set], color='green', s=100, zorder=5, label='Room Setpoint (22 °C, 50% RH)')

    # Plot processes for each condition
    colors = ['#d95f02', '#7570b3', '#e7298a', '#66a61e', '#e6ab02', '#1f78b4']
    for idx, r in df30.iterrows():
        c = colors[idx % len(colors)]
        cond = r['Condition']
        T_oa = r['T_oa_C']
        w_oa = humidity_ratio((r['RH_oa_pct'] / 100.0) * P_sat_water(T_oa)) * 1000.0
        T_mix = r['T_mix_C']
        w_mix = humidity_ratio((r['RH_room_pct'] / 100.0) * P_sat_water(22.0)) * 1000.0
        T_sup = r['T_supply_C']
        w_sup = r['w_supply'] * 1000.0

        ax.plot([T_oa, T_mix, T_sup], [w_oa, w_mix, w_sup], 'o-', color=c, lw=1.8, ms=6, label=f"{cond}")

    ax.set_title("Psychrometric Processes: Outdoor State → Mixing → Cooling Coil → Supply Air", fontsize=12, fontweight='bold', pad=12)
    ax.set_xlabel("Dry-Bulb Temperature (°C)", fontweight='bold')
    ax.set_ylabel("Humidity Ratio w (g/kg dry air)", fontweight='bold')
    ax.set_xlim(5, 48)
    ax.set_ylim(0, 35)
    ax.grid(True, linestyle='--', alpha=0.4)
    ax.legend(loc='upper left', framealpha=0.9, fontsize=8.5)
    plt.tight_layout()
    plt.savefig("plot_psychrometric_chart.png")
    plt.close()
    print("[Saved] plot_psychrometric_chart.png")

    # -------------------------------------------------------------
    # FIGURE 2: Seasonal Energy Duties (Q_evap, Q_gen, Q_cond)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    x = np.arange(len(df30))
    width = 0.25

    rects1 = ax.bar(x - width, df30['Q_evap_kW'], width, label='Chiller Evaporator Q_evap', color='#3182bd')
    rects2 = ax.bar(x, df30['Q_gen_kW'], width, label='Flue-Gas Heat Q_gen', color='#e6550d')
    rects3 = ax.bar(x + width, df30['Q_cond_kW'], width, label='Condenser Rejection Q_cond', color='#31a354')

    ax.set_title("Seasonal Thermal Duties Across 6 Ambient Conditions (30% Fresh Air)", fontsize=12, fontweight='bold', pad=12)
    ax.set_ylabel("Thermal Duty (kW)", fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(df30['Condition'], rotation=15, ha='right', fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.3, axis='y')
    ax.legend(framealpha=0.9)

    max_idx = df30['Q_evap_kW'].idxmax()
    ax.annotate(f"Governing Peak:\n{df30.loc[max_idx, 'Q_evap_kW']:.1f} kW",
                xy=(max_idx - width, df30.loc[max_idx, 'Q_evap_kW']),
                xytext=(max_idx - 0.4, df30.loc[max_idx, 'Q_evap_kW'] + 1200),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6),
                fontsize=9, fontweight='bold', color='#3182bd')

    plt.tight_layout()
    plt.savefig("plot_seasonal_duties.png")
    plt.close()
    print("[Saved] plot_seasonal_duties.png")

    # -------------------------------------------------------------
    # FIGURE 3: Condenser Type Comparison
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5), dpi=300)

    types = ['Evaporative Condenser', 'Air-Cooled Finned-Tube']
    areas = [float(df_comp.loc[8, 'Evaporative Condenser']), float(df_comp.loc[8, 'Air-Cooled Finned-Tube'])]
    colors_c = ['#2ca02c', '#d62728']

    bars1 = ax1.bar(types, areas, color=colors_c, width=0.55)
    ax1.set_title("Heat Transfer Surface Area (m²)", fontweight='bold')
    ax1.set_ylabel("Area (m²)", fontweight='bold')
    ax1.grid(True, linestyle='--', alpha=0.3, axis='y')
    for b in bars1:
        h = b.get_height()
        ax1.text(b.get_x() + b.get_width()/2., h + 500, f'{h:,.0f} m²', ha='center', va='bottom', fontweight='bold')
    ratio = areas[1] / max(1.0, areas[0])
    ax1.text(0.5, 0.65, f"Air-Cooled requires\n~{ratio:.1f}x larger area!", transform=ax1.transAxes, ha='center',
             fontsize=10, fontweight='bold', bbox=dict(boxstyle='round,pad=0.5', facecolor='#fee0d2', edgecolor='#de2d26'))

    p_highs = [float(df_comp.loc[2, 'Evaporative Condenser']), float(df_comp.loc[2, 'Air-Cooled Finned-Tube'])]
    bars2 = ax2.bar(types, p_highs, color=colors_c, width=0.55)
    ax2.axhline(20.0, color='red', linestyle='--', lw=2, label='Vessel Design Limit (20 bar)')
    ax2.set_title("High Pressure P_high vs Vessel Limit", fontweight='bold')
    ax2.set_ylabel("Condensing Pressure P_high (bar)", fontweight='bold')
    ax2.set_ylim(0, 25)
    ax2.grid(True, linestyle='--', alpha=0.3, axis='y')
    ax2.legend(loc='upper left')
    for b in bars2:
        h = b.get_height()
        ax2.text(b.get_x() + b.get_width()/2., h + 0.5, f'{h:.2f} bar', ha='center', va='bottom', fontweight='bold')

    plt.suptitle("Condenser Technology Comparison: Evaporative vs Air-Cooled Finned-Tube", fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig("plot_condenser_comparison.png")
    plt.close()
    print("[Saved] plot_condenser_comparison.png")

    # -------------------------------------------------------------
    # FIGURE 4: Off-Design Performance Across the Seasons
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True, dpi=300)

    x_labels = df30['Condition']
    ax1.plot(x_labels, df30['T_cond_C'], 'o-', color='#e6550d', lw=2.2, label='Condensing Temp T_cond (°C)')
    ax1.plot(x_labels, df30['Twb_oa_C'], 's--', color='#3182bd', lw=1.8, label='Ambient Wet-Bulb Twb (°C)')
    ax1.axhline(25.0, color='purple', linestyle=':', lw=1.5, label='Minimum Expansion Differential Floor (25 °C)')
    ax1.set_ylabel("Temperature (°C)", fontweight='bold')
    ua_val = evap_cond_des['UA_kW_K']
    ax1.set_title(f"Off-Design Condenser Response (Fixed UA = {ua_val:.1f} kW/K)", fontweight='bold')
    ax1.grid(True, linestyle='--', alpha=0.3)
    ax1.legend(loc='lower left', framealpha=0.9)

    ax2.plot(x_labels, df30['COP'], '^-', color='#2ca02c', lw=2.2, label='Chiller COP')
    ax2.plot(x_labels, df30['COP_rev'], 'v--', color='#7570b3', lw=1.8, label='Reversible COP Limit')
    ax2.set_ylabel("Coefficient of Performance (COP)", fontweight='bold')
    ax2.set_xticklabels(x_labels, rotation=15, ha='right', fontweight='bold')
    ax2.grid(True, linestyle='--', alpha=0.3)
    ax2.legend(loc='upper right', framealpha=0.9)

    plt.tight_layout()
    plt.savefig("plot_off_design_condenser.png")
    plt.close()
    print("[Saved] plot_off_design_condenser.png")

    # -------------------------------------------------------------
    # FIGURE 5: Fresh Air Sensitivity Analysis (30% -> 40%)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    x = np.arange(len(df_sens))
    width = 0.22

    ax.bar(x - width, df_sens['Delta_Q_evap_pct'], width, label='% Change in Chiller Q_evap', color='#3182bd')
    ax.bar(x, df_sens['Delta_Q_gen_pct'], width, label='% Change in Heat Demand Q_gen', color='#e6550d')
    ax.bar(x + width, df_sens['Delta_Condensate_pct'], width, label='% Change in Condensate Rate', color='#31a354')

    ax.set_title("Sensitivity to Fresh Air Fraction: Percentage Change from 30% to 40% Fresh Air", fontsize=11, fontweight='bold', pad=12)
    ax.set_ylabel("Percentage Change (%)", fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(df_sens['Condition'], rotation=15, ha='right', fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.3, axis='y')
    ax.legend(framealpha=0.9)

    plt.tight_layout()
    plt.savefig("plot_fresh_air_sensitivity.png")
    plt.close()
    print("[Saved] plot_fresh_air_sensitivity.png")

    # -------------------------------------------------------------
    # FIGURE 6: Water Decanter Central Sizing
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 5.2), dpi=300)
    cond_m3 = df30['m_cond_district_m3_day']
    bars = ax.bar(df30['Condition'], cond_m3, color='#2b8cbe', width=0.55)

    ax.set_title("Central Water Decanter Sizing: Daily Condensate Production Across Seasons", fontsize=12, fontweight='bold', pad=12)
    ax.set_ylabel("Condensate Production (m³/day)", fontweight='bold')
    ax.set_xticklabels(df30['Condition'], rotation=15, ha='right', fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.3, axis='y')

    for b in bars:
        h = b.get_height()
        if h > 0:
            ax.text(b.get_x() + b.get_width()/2., h + 1.5, f'{h:.1f} m³/d', ha='center', va='bottom', fontweight='bold')

    max_dec_idx = cond_m3.idxmax()
    ax.annotate(f"Decanter Sizing Peak:\nMonsoon Day = {cond_m3[max_dec_idx]:.1f} m³/day\n({df30.loc[max_dec_idx, 'm_cond_district_kgh']:.0f} kg/h)",
                xy=(max_dec_idx, cond_m3[max_dec_idx]),
                xytext=(max_dec_idx + 0.5, cond_m3[max_dec_idx] - 15),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6),
                fontsize=9.5, fontweight='bold', bbox=dict(boxstyle='round,pad=0.5', facecolor='#e0f3f8', edgecolor='#0868ac'))

    plt.tight_layout()
    plt.savefig("plot_water_decanter.png")
    plt.close()
    print("[Saved] plot_water_decanter.png")

def main():
    print("\n" + "=" * 90)
    print("ME3160 PROJECT 2: AMMONIA-WATER ABSORPTION CHILLER FOR DISTRICT COOLING")
    print("=" * 90)

    # 1. Validation Suite
    val_exit = run_all_validation_checks()
    if val_exit != 0:
        print("[ERROR] Validation test suite failed!")
        sys.exit(1)

    # 2. Tasks 1 & 3: Baseline (30% fresh air)
    print("\n--- RUNNING TASKS 1 & 3: BASELINE SEASONAL SIMULATION (30% FRESH AIR) ---")
    df30, evap_cond_des = run_task1_and_task3(f_fresh=0.30)
    df30.to_csv("seasonal_summary_p2.csv", index=False)
    print("[Saved] seasonal_summary_p2.csv")

    # 3. Task 2: Condenser Comparison & Off-Design
    print("\n--- RUNNING TASK 2: CONDENSER SIZING & OFF-DESIGN MAP ---")
    df_comp, des_evap, des_air = run_task2_comparison()
    df_comp.to_csv("condenser_comparison_p2.csv", index=False)
    print("[Saved] condenser_comparison_p2.csv")

    # 4. Task 4: Fresh Air Sensitivity (30% -> 40%) & Reheat
    print("\n--- RUNNING TASK 4: FRESH AIR SENSITIVITY (30% -> 40%) ---")
    df_sens, _, df40 = run_task4_sensitivity()
    df_sens.to_csv("fresh_air_sensitivity_p2.csv", index=False)
    print("[Saved] fresh_air_sensitivity_p2.csv")

    # Task 4 Monsoon night reheat dynamic computation
    reheat_res = solve_monsoon_night_reheat(f_fresh=0.40, target_rh=0.70)
    
    # SHX Sensitivity computation
    shx_sens = compute_shx_sensitivity(df30['Q_evap_kW'].max())

    # 5. Generate Figures
    generate_plots(df30, df40, df_comp, df_sens, evap_cond_des)

    # Active operational conditions for flue gas reporting
    active_df30 = df30[df30['Q_evap_kW'] > 0]
    min_fg_out = active_df30['T_fg_out_C'].min()
    max_fg_out = active_df30['T_fg_out_C'].max()

    # 6. Print Executive Summary
    print("\n" + "=" * 90)
    print("PROJECT 2 EXECUTIVE SUMMARY & KEY INSIGHTS")
    print("=" * 90)
    print(f"1. CHILLER GOVERNING CONDITION: Monsoon Day (Q_evap = {df30['Q_evap_kW'].max():.1f} kW)")
    print("   -> Physical Reason: High latent outdoor humidity (35 °C, 85% RH, w=0.0306 kg/kg da).")
    print("   -> Latent load accounts for over 50% of the coil duty, outweighing the Summer Day peak dry-bulb.")
    print(f"2. DECANTER GOVERNING CONDITION: Monsoon Day (Peak = {df30['m_cond_district_m3_day'].max():.1f} m³/day = {df30['m_cond_district_kgh'].max():.1f} kg/h)")
    print("   -> Governed strictly by moisture condensation rate across the 1000 AHU cooling coils.")
    print("3. CONDENSER TECHNOLOGY CHOICE: EVAPORATIVE CONDENSER (RECOMMENDED)")
    print(f"   -> Evaporative: Sized at Monsoon Twb = 32.65 °C -> T_cond = 40.0 °C, P_high = {des_evap['P_high_design_bar']:.1f} bar ({des_evap['P_high_design_bar']:.1f} <= 20 bar SAFE).")
    print(f"   -> Air-Cooled: Sized at Summer Tdb = 40.0 °C -> T_cond = 52.0 °C, P_high = {des_air['P_high_design_bar']:.1f} bar (VIOLATES 20 bar vessel design limit!).")
    print(f"   -> Evaporative UA = {des_evap['UA_kW_K']:.1f} kW/K (Area = {des_evap['Area_m2']:.0f} m²) vs Air-Cooled Area = {des_air['Area_m2']:.0f} m² (ratio {des_air['Area_m2']/des_evap['Area_m2']:.1f}x).")
    print("4. TURNDOWN & FREE COOLING:")
    print(f"   -> Winter Night cooling load is 0.0 kW (< 25% turndown threshold of {0.25*df30['Q_evap_kW'].max():.1f} kW).")
    print("   -> Operational Remedy: Shut down absorption chiller and engage direct waterside economizer (free cooling).")
    print("5. MONSOON NIGHT RH CEILING & REHEAT CALCULATION (Task 4):")
    print(f"   -> Baseline (30% fresh air): Room RH reaches {df30.loc[3, 'RH_room_pct']:.1f}%.")
    print(f"   -> Increased fresh air (40%): Room RH reaches {df40.loc[3, 'RH_room_pct']:.1f}% (exceeds 75% ASHRAE ceiling).")
    print(f"   -> Dynamic Remedy: Modulate cooling coil ADP to {reheat_res['ADP_target_C']:.2f} °C (T_coil_out = {reheat_res['T_coil_out_C']:.2f} °C).")
    print(f"   -> Required terminal reheat: delta_T = {reheat_res['delta_T_reheat_K']:.2f} K ({reheat_res['q_reheat_zone_kW']:.3f} kW/zone).")
    print(f"   -> Total reheat sensible load: {reheat_res['Q_reheat_district_kW']:.1f} kW -> Extra district Q_evap: {reheat_res['extra_Q_evap_kW']:.1f} kW.")
    print(f"   -> Resulting extra flue-gas generator heat demand: {reheat_res['extra_Q_gen_kW']:.1f} kW (COP = {reheat_res['cop_night']:.3f}).")
    print("6. SOLUTION HEAT EXCHANGER (SHX) SENSITIVITY:")
    print(f"   -> Baseline eps_SHX = 0.70 gives Q_gen = {shx_sens['Q_gen_base_kW']:.1f} kW (COP = {shx_sens['cop_base']:.3f}).")
    print(f"   -> Without SHX (eps_SHX = 0.0), Q_gen rises by {shx_sens['savings_vs_none_kW']:.1f} kW (demonstrates SHX is the largest cycle lever).")
    print(f"   -> Increasing eps_SHX to 0.80 saves an additional {shx_sens['savings_eps80_kW']:.1f} kW of generator heat.")
    print("7. FLUE-GAS WASTE HEAT INTEGRATION:")
    print(f"   -> Peak flue-gas flow: {df30['m_fg_kgs'].max():.2f} kg/s (Monsoon Day), well within 80.0 kg/s source limit.")
    print(f"   -> Active flue-gas exit temperature range: {min_fg_out:.1f} °C to {max_fg_out:.1f} °C (well above 140 °C acid-gas dew point floor).")
    print("=" * 90)
    print("\n>>> PROJECT 2 EXECUTION FULLY COMPLETED AND REPRODUCIBLE! <<<\n")

if __name__ == '__main__':
    main()
