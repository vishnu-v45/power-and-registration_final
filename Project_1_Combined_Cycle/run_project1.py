"""
run_project1.py
Master reproducible driver script for ME3160 Project 1:
Surrogate-Assisted Optimization of a Methane-Fired Combined Cycle.
Course: ME3160 Power & Refrigeration Cycles

Executes Parts A, B, and C end-to-end, generates all metrics, tables, and high-resolution plots:
1. plot_gt_alone.png: Gas Turbine Alone (eta_gt vs rp)
2. plot_parity_comparison.png: RSM and ANN Parity Plots with held-out metrics
3. plot_t_q_hrsg.png: T-Q Diagrams at Baseline and Optimum side-by-side
4. plot_t_s_diagram.png: Complete T-s Diagrams for Brayton and Rankine cycles
5. plot_sensitivity.png: Sensitivity to HRSG inlet temperature limit (honest scaling)
6. plot_pareto_front.png: Bi-Objective NSGA-II Pareto Front (eta_cc vs Wnet)
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import CoolProp.CoolProp as CP

from thermo_gas import solve_brayton_cycle, GasMixture
from combined_cycle import direct_model
from surrogate_pipeline import (
    run_lhs_doe, train_surrogates, optimize_surrogate_ga,
    adaptive_refinement, run_sensitivity_study, run_biobjective_pareto,
    x_to_vars, BOUNDS
)

plt.rcParams.update({
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.titlesize': 15,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'lines.linewidth': 2.0,
})

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

def plot_gt_alone():
    print("\n--- Part A: Gas Turbine Alone Analysis (eta_gt vs rp) ---")
    TIT_fixed = 1400.0  # K
    rp_values = np.linspace(4.0, 35.0, 32)
    eta_gt_list = []
    wnet_gt_list = []
    T4_list = []
    
    for rp in rp_values:
        gt = solve_brayton_cycle(rp=rp, TIT=TIT_fixed)
        eta_gt_list.append(gt['eta_gt'] * 100.0)
        wnet_gt_list.append(gt['w_gt_net'])
        T4_list.append(gt['T4'] - 273.15)
        
    eta_gt_arr = np.array(eta_gt_list)
    max_idx = np.argmax(eta_gt_arr)
    rp_opt = rp_values[max_idx]
    eta_max = eta_gt_arr[max_idx]
    
    fig, ax1 = plt.subplots(figsize=(8.5, 5.2))
    color = '#1A365D'
    ax1.set_xlabel('Compression Ratio ($r_p$)')
    ax1.set_ylabel('Thermal Efficiency $\\eta_{GT}$ (%)', color=color)
    ax1.plot(rp_values, eta_gt_list, color=color, lw=2.5, label='Gas Turbine $\\eta_{GT}$')
    ax1.plot(rp_opt, eta_max, 'ro', markersize=8, label=f'Peak $\\eta_{{GT}} = {eta_max:.2f}\\%$ at $r_p={rp_opt:.1f}$')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, linestyle='--', alpha=0.6)
    
    ax2 = ax1.twinx()
    color = '#C53030'
    ax2.set_ylabel('Exhaust Temperature $T_4$ (°C)', color=color)
    ax2.plot(rp_values, T4_list, color=color, linestyle='--', lw=2.0, label='Exhaust Temp $T_4$')
    ax2.tick_params(axis='y', labelcolor=color)
    
    plt.title(f'Gas Turbine Alone: Efficiency vs Compression Ratio ($TIT = {TIT_fixed:.0f}$ K)', pad=15)
    fig.tight_layout()
    save_path = os.path.join(OUTPUT_DIR, 'plot_gt_alone.png')
    plt.savefig(save_path)
    plt.close()
    print(f"  Saved: {save_path}")
    print(f"  Gas turbine alone peak efficiency: {eta_max:.2f}% at rp = {rp_opt:.1f}")


def plot_parity_and_residuals(surr_dict):
    y_test = surr_dict['y_test'] * 100.0
    y_pred_rsm = surr_dict['y_pred_rsm'] * 100.0
    y_pred_ann = surr_dict['y_pred_ann'] * 100.0
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    min_val = min(y_test.min(), y_pred_rsm.min()) - 1.0
    max_val = max(y_test.max(), y_pred_rsm.max()) + 1.0
    ax1.scatter(y_test, y_pred_rsm, alpha=0.7, color='steelblue', edgecolors='k', s=45)
    ax1.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='1:1 Parity Line')
    ax1.set_xlabel('True Combined Cycle Efficiency $\\eta_{cc}$ (%)')
    ax1.set_ylabel('RSM Predicted $\\eta_{cc}$ (%)')
    ax1.set_title(f'Quadratic Response Surface (RSM)\n$R^2 = {surr_dict["r2_rsm"]:.4f}$, RMSE = {surr_dict["rmse_rsm"]*100:.3f}%')
    ax1.set_xlim([min_val, max_val])
    ax1.set_ylim([min_val, max_val])
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.legend(loc='upper left')
    
    min_val2 = min(y_test.min(), y_pred_ann.min()) - 1.0
    max_val2 = max(y_test.max(), y_pred_ann.max()) + 1.0
    ax2.scatter(y_test, y_pred_ann, alpha=0.7, color='forestgreen', edgecolors='k', s=45)
    ax2.plot([min_val2, max_val2], [min_val2, max_val2], 'r--', lw=2, label='1:1 Parity Line')
    ax2.set_xlabel('True Combined Cycle Efficiency $\\eta_{cc}$ (%)')
    ax2.set_ylabel('ANN Predicted $\\eta_{cc}$ (%)')
    ax2.set_title(f'Artificial Neural Network (ANN - Tuned)\n$R^2 = {surr_dict["r2_ann"]:.4f}$, RMSE = {surr_dict["rmse_ann"]*100:.3f}%')
    ax2.set_xlim([min_val2, max_val2])
    ax2.set_ylim([min_val2, max_val2])
    ax2.grid(True, linestyle='--', alpha=0.6)
    ax2.legend(loc='upper left')
    
    fig.tight_layout()
    save_path = os.path.join(OUTPUT_DIR, 'plot_parity_comparison.png')
    plt.savefig(save_path)
    plt.close()
    print(f"  Saved: {save_path}")


def plot_hrsg_t_q_comparison(det_base, det_opt):
    """
    Plots T-Q diagrams for BOTH Baseline and Optimal designs side-by-side.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    for ax, det, title_tag in [
        (ax1, det_base, "Baseline ($r_p=16, TIT=1400$ K, $P_s=30$ bar)"),
        (ax2, det_opt, "Optimal ($r_p=21.7, TIT=1500$ K, $P_s=46.5$ bar)")
    ]:
        hrsg = det['hrsg']
        st = det['st']
        
        Q_econ = hrsg['Q_econ']
        Q_evap = hrsg['Q_evap']
        Q_sup = hrsg['Q_sup']
        Q_tot = hrsg['Q_hrsg']
        
        Q_steam = [0, Q_econ, Q_econ + Q_evap, Q_tot]
        T_steam = [
            st['State8']['T'] - 273.15,
            st['T_sat_drum_C'],
            st['T_sat_drum_C'],
            st['State5']['T'] - 273.15
        ]
        
        Q_gas = [0, Q_econ, Q_econ + Q_evap, Q_tot]
        T_gas = [
            hrsg['T_gas_stack_C'],
            hrsg['T_gas_pinch'] - 273.15,
            hrsg['T_gas_after_sup'] - 273.15,
            hrsg['T_gas_in'] - 273.15
        ]
        
        ax.plot(Q_gas, T_gas, 'r-o', lw=2.5, markersize=6, label='Exhaust Gas Stream')
        ax.plot(Q_steam, T_steam, 'b-s', lw=2.5, markersize=6, label='Water / Steam Stream')
        
        pinch_Q = Q_econ
        pinch_T_gas = hrsg['T_gas_pinch'] - 273.15
        pinch_T_steam = st['T_sat_drum_C']
        
        ax.annotate(f'Pinch Point\n$\\Delta T_{{pinch}} = {pinch_T_gas - pinch_T_steam:.1f}$ K',
                    xy=(pinch_Q, (pinch_T_gas + pinch_T_steam)/2),
                    xytext=(pinch_Q + Q_tot*0.06, pinch_T_steam - 45),
                    arrowprops=dict(facecolor='black', shrink=0.05, width=1.2, headwidth=6),
                    fontsize=9.5, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.6))
        
        app_dt = T_gas[-1] - T_steam[-1]
        ax.annotate(f'Approach\n$\\Delta T_{{app}} = {app_dt:.1f}$ K',
                    xy=(Q_tot, (T_gas[-1] + T_steam[-1])/2),
                    xytext=(Q_tot - Q_tot*0.35, T_gas[-1] - 35),
                    arrowprops=dict(facecolor='black', shrink=0.05, width=1.2, headwidth=6),
                    fontsize=9.5, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="#E2E8F0", alpha=0.7))
        
        ax.set_xlabel('Cumulative Heat Transferred $Q$ (kW)')
        ax.set_ylabel('Temperature (°C)')
        ax.set_title(f'HRSG $T–Q$ Diagram: {title_tag}', pad=12)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend(loc='upper left')
        ax.set_ylim([20, max(T_gas) + 40])
        
    fig.tight_layout()
    save_path = os.path.join(OUTPUT_DIR, 'plot_t_q_hrsg.png')
    plt.savefig(save_path)
    plt.close()
    print(f"  Saved: {save_path}")


def plot_t_s_diagram(det):
    """
    Generates the Temperature-Entropy (T-s) diagram for the combined cycle plant at the optimum.
    """
    gt = det['gt']
    st = det['st']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # ------------------ Subplot 1: Gas Turbine (Brayton) ------------------
    s1 = 0.0
    s2s = s1
    s2 = s1 + (gt['h2'] - gt['h2s']) / ((gt['T2'] + gt['T2s'])/2)
    s3 = s2 + (gt['h3'] - gt['h2']) / ((gt['TIT'] + gt['T2'])/2)
    s4s = s3
    s4 = s3 + (gt['h4'] - gt['h4s']) / ((gt['T4'] + gt['T4s'])/2)
    
    gt_s = [s1, s2, s3, s4, s1]
    gt_T = [gt['T1'] - 273.15, gt['T2'] - 273.15, gt['TIT'] - 273.15, gt['T4'] - 273.15, gt['T1'] - 273.15]
    
    ax1.plot(gt_s, gt_T, 'r-o', lw=2.5, markersize=8, label='Brayton Cycle')
    ax1.plot([s1, s2s], [gt['T1'] - 273.15, gt['T2s'] - 273.15], 'k--', lw=1.5, label='Isentropic 1-2s')
    ax1.plot([s3, s4s], [gt['TIT'] - 273.15, gt['T4s'] - 273.15], 'k--', lw=1.5, label='Isentropic 3-4s')
    
    for label, s_val, T_val in zip(['1', '2', '3', '4'], [s1, s2, s3, s4], gt_T[:4]):
        ax1.annotate(f'State {label}\n({T_val:.0f} °C)', (s_val, T_val),
                     textcoords="offset points", xytext=(10, -5 if label in ['2', '4'] else 5),
                     fontweight='bold', fontsize=9.5)
    
    rp_val = det.get('rp', 19.88)
    tit_val = det.get('TIT', 1500.0)
    ax1.set_title(f'Brayton Topping Cycle ($r_p = {rp_val:.1f}$, $TIT = {tit_val:.0f}$ K)\n$W_{{net,GT}} = {det["W_gt_net"]/1000:.1f}$ MW')
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.legend(loc='upper left')
    
    # ------------------ Subplot 2: Steam Rankine Cycle ------------------
    T_dome = np.linspace(25.0, 370.0, 80)
    s_liq_dome = [CP.PropsSI('S', 'T', T + 273.15, 'Q', 0, 'Water')/1e3 for T in T_dome]
    s_vap_dome = [CP.PropsSI('S', 'T', T + 273.15, 'Q', 1, 'Water')/1e3 for T in T_dome]
    
    ax2.plot(s_liq_dome + s_vap_dome[::-1], list(T_dome) + list(T_dome)[::-1], 'k-', lw=1.5, label='Water Saturation Dome')
    
    s5 = st['State5']['s']
    T5 = st['State5']['T'] - 273.15
    s6s = s5
    T6 = st['State6']['T'] - 273.15
    s6 = CP.PropsSI('S', 'P', st['State6']['P'], 'H', st['State6']['h']*1e3, 'Water')/1e3
    s7 = st['State7']['s']
    T7 = T6
    s8 = CP.PropsSI('S', 'P', st['State8']['P'], 'H', st['State8']['h']*1e3, 'Water')/1e3
    T8 = st['State8']['T'] - 273.15
    s_sat_l = CP.PropsSI('S', 'P', st['Ps_bar']*1e5, 'Q', 0, 'Water')/1e3
    s_sat_v = CP.PropsSI('S', 'P', st['Ps_bar']*1e5, 'Q', 1, 'Water')/1e3
    T_sat_Ps = st['T_sat_drum_C']
    
    st_s = [s8, s_sat_l, s_sat_v, s5, s6, s7, s8]
    st_T = [T8, T_sat_Ps, T_sat_Ps, T5, T6, T7, T8]
    
    ax2.plot(st_s, st_T, 'b-s', lw=2.5, markersize=7, label='Rankine Bottoming Cycle')
    ax2.plot([s5, s6s], [T5, T6], 'g--', lw=1.5, label='Isentropic 5-6s')
    
    for label, s_val, T_val in zip(['5', '6', '7', '8'], [s5, s6, s7, s8], [T5, T6, T7, T8]):
        ax2.annotate(f'State {label}\n({T_val:.0f} °C)', (s_val, T_val),
                     textcoords="offset points", xytext=(8, -5 if label in ['6', '7'] else 5),
                     fontweight='bold', fontsize=9.5)
    
    ax2.set_xlabel('Entropy $s$ (kJ/kg·K)')
    ax2.set_ylabel('Temperature (°C)')
    ax2.set_title(f'Rankine Bottoming Cycle ($P_s = {st["Ps_bar"]:.1f}$ bar, $T_s = {T5:.0f}$ °C)\n$W_{{net,ST}} = {det["W_st_net"]/1000:.1f}$ MW')
    ax2.grid(True, linestyle='--', alpha=0.6)
    ax2.legend(loc='upper left')
    
    fig.tight_layout()
    save_path = os.path.join(OUTPUT_DIR, 'plot_t_s_diagram.png')
    plt.savefig(save_path)
    plt.close()
    print(f"  Saved: {save_path}")


def plot_pareto_front(pareto_eta, pareto_wnet, single_opt_dict):
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(pareto_wnet, pareto_eta, 'b-o', markersize=5, lw=2, label='Pareto Front (NSGA-II Non-Dominated)')
    
    opt_wnet_MW = single_opt_dict['W_net_total'] / 1000.0
    opt_eta = single_opt_dict['eta_cc'] * 100.0
    ax.plot(opt_wnet_MW, opt_eta, 'r*', markersize=16, 
            label=f'Single-Objective Optimum ($\\eta_{{cc}}={opt_eta:.2f}\\%$, $\\dot{{W}}_{{net}}={opt_wnet_MW:.1f}$ MW)')
    
    ax.set_xlabel('Total Net Power Output $\\dot{W}_{net}$ (MW)')
    ax.set_ylabel('Combined Cycle Thermal Efficiency $\\eta_{cc}$ (%)')
    ax.set_title('Bi-Objective Pareto Front: Thermal Efficiency vs Net Power Output', pad=15)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(loc='lower left')
    
    fig.tight_layout()
    save_path = os.path.join(OUTPUT_DIR, 'plot_pareto_front.png')
    plt.savefig(save_path)
    plt.close()
    print(f"  Saved: {save_path}")


def plot_sensitivity_results(df_sens):
    """
    Plots sensitivity with proper absolute y-axis scaling to avoid misleading V distortion.
    """
    fig, ax1 = plt.subplots(figsize=(8.5, 5.2))
    color = '#1A365D'
    ax1.set_xlabel('HRSG Inlet Gas Temperature Limit (°C)')
    ax1.set_ylabel('Optimal Efficiency $\\eta_{cc}$ (%)', color=color)
    ax1.plot(df_sens['limit_C'], df_sens['eta_cc'], 'o-', color=color, lw=2.5, markersize=8, label='Efficiency $\\eta_{cc}$')
    ax1.set_ylim([50.0, 56.0])
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, linestyle='--', alpha=0.6)
    
    ax2 = ax1.twinx()
    color = '#276749'
    ax2.set_ylabel('Net Power Output $\\dot{W}_{net}$ (MW)', color=color)
    ax2.plot(df_sens['limit_C'], df_sens['Wnet_MW'], 's--', color=color, lw=2.5, markersize=8, label='Power Output $\\dot{W}_{net}$')
    ax2.set_ylim([40.0, 56.0])
    ax2.tick_params(axis='y', labelcolor=color)
    
    plt.title('Sensitivity Study: Effect of HRSG Inlet Temperature Limit\n(Tube Limit Non-Binding: Exhaust $T_4 \\approx 544$ °C stays below all limits)', pad=15)
    fig.tight_layout()
    save_path = os.path.join(OUTPUT_DIR, 'plot_sensitivity.png')
    plt.savefig(save_path)
    plt.close()
    print(f"  Saved: {save_path}")


def main():
    print("=" * 80)
    print("ME3160 - SURROGATE-ASSISTED OPTIMIZATION OF A METHANE-FIRED COMBINED CYCLE")
    print("=" * 80)
    
    # 1. Part A: Gas Turbine Alone Curve
    plot_gt_alone()
    
    # Baseline direct evaluation
    eta_base, Wnet_base, margins_base, feas_base, det_base = direct_model(
        rp=16.0, TIT=1400.0, Ps=30.0, Ts=450.0 + 273.15, Pcond=0.075
    )
    
    # 2. Part B: Latin Hypercube Sampling (N=500)
    doe_csv_path = os.path.join(OUTPUT_DIR, 'doe_samples.csv')
    if os.path.exists(doe_csv_path):
        print(f"\n[Step 1] Loading existing DOE samples from {doe_csv_path}...")
        df_doe = pd.read_csv(doe_csv_path)
        print(f"  Loaded {len(df_doe)} samples. Feasible: {df_doe['feasible'].sum()}")
    else:
        print(f"\n[Step 1] Running Latin Hypercube Sampling (N=500)...")
        df_doe = run_lhs_doe(n_samples=500, hrsg_limit_C=650.0)
        df_doe.to_csv(doe_csv_path, index=False)
        print(f"  Saved {len(df_doe)} samples to {doe_csv_path}. Feasible: {df_doe['feasible'].sum()}")
    
    # 3. Fit Surrogates & Evaluate
    surr_dict = train_surrogates(df_doe)
    plot_parity_and_residuals(surr_dict)
    
    # 4 & 5: Single-Objective GA & Verification
    best_x, surr_eta = optimize_surrogate_ga(surr_dict, hrsg_limit_C=650.0)
    final_x, eta_opt, Wnet_opt, margins_opt, det_opt, df_refined, surr_refined = adaptive_refinement(
        surr_dict, df_doe, best_x, hrsg_limit_C=650.0, max_refinements=2
    )
    
    rp_opt, TIT_opt, Ps_opt, Ts_opt, Pcond_opt = x_to_vars(final_x)
    
    print("\n" + "=" * 80)
    print("OPTIMAL COMBINED CYCLE OPERATING POINT")
    print("=" * 80)
    print(f"Compression Ratio (rp):               {rp_opt:.2f}")
    print(f"Turbine Inlet Temperature (TIT):      {TIT_opt:.1f} K")
    print(f"Steam Drum Pressure (Ps):             {Ps_opt:.2f} bar")
    print(f"Superheat Outlet Temperature (Ts):    {Ts_opt:.1f} K ({Ts_opt-273.15:.1f} °C)")
    print(f"Condenser Pressure (Pcond):           {Pcond_opt:.4f} bar")
    print("-" * 50)
    print(f"Combined Cycle Thermal Efficiency:    {eta_opt*100:.3f}%")
    print(f"Total Net Power Output (Wnet):        {Wnet_opt/1000.0:.2f} MW")
    print(f"Gas Turbine Net Power:                {det_opt['W_gt_net']/1000.0:.2f} MW")
    print(f"Steam Turbine Net Power:              {det_opt['W_st_net']/1000.0:.2f} MW")
    print(f"Specific Work (Wnet / m_air):         {det_opt['specific_work']:.2f} kJ/kg air")
    print(f"Bottoming-to-Topping Work Ratio:      {det_opt['bottoming_topping_ratio']:.4f}")
    print(f"HRSG Effectiveness:                   {det_opt['hrsg_effectiveness']*100:.2f}%")
    print(f"Gas Entering HRSG (T4):               {det_opt['T4_C']:.1f} °C (Limit: 650 °C)")
    print(f"Stack Gas Temperature:                {det_opt['T_stack_C']:.1f} °C (Limit: >= 100 °C)")
    print(f"Steam Turbine Exit Quality (x6):      {det_opt['x6']:.4f} (Limit: >= 0.88)")
    print(f"Combustor Equivalence Ratio (phi):    {det_opt['phi']:.4f} (Limit: <= 0.50)")
    print("=" * 80)
    
    # 6. Plot HRSG T-Q Diagrams (Baseline vs Optimum)
    plot_hrsg_t_q_comparison(det_base, det_opt)
    
    # 7. Plot T-s Diagram at Optimum
    plot_t_s_diagram(det_opt)
    
    # 8. Part C: Sensitivity Study (HRSG Inlet Limits)
    df_sens = run_sensitivity_study(surr_refined, df_refined)
    df_sens.to_csv(os.path.join(OUTPUT_DIR, 'sensitivity_hrsg_limit.csv'), index=False)
    print("\n--- SENSITIVITY STUDY RESULTS ---")
    print(df_sens.to_string(index=False))
    plot_sensitivity_results(df_sens)
    
    # 9. Part C: Bi-Objective Pareto Front (NSGA-II)
    pareto_eta, pareto_wnet, pareto_X = run_biobjective_pareto(surr_refined, hrsg_limit_C=650.0)
    plot_pareto_front(pareto_eta, pareto_wnet, det_opt)
    
    print("\n>>> PROJECT 1 MASTER WORKFLOW COMPLETED SUCCESSFULLY! <<<")

if __name__ == '__main__':
    main()
