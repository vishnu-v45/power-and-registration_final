"""
run_project1.py
Master reproducible driver script for ME3160 Project 1:
Surrogate-Assisted Optimization of a Methane-Fired Combined Cycle.
Executes Parts A, B, and C end-to-end, generates all metrics, tables, and high-resolution plots.
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
    'font.size': 12,
    'axes.labelsize': 13,
    'axes.titlesize': 14,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11,
    'figure.titlesize': 16,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'lines.linewidth': 2.0,
})

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

def plot_gt_alone():
    print("\n--- Part A: Gas Turbine Alone Analysis (eta_gt vs rp) ---")
    TIT_fixed = 1400.0 # K
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
    
    fig, ax1 = plt.subplots(figsize=(8, 5))
    color = 'tab:blue'
    ax1.set_xlabel('Compression Ratio ($r_p$)')
    ax1.set_ylabel('Thermal Efficiency $\\eta_{GT}$ (%)', color=color)
    ax1.plot(rp_values, eta_gt_list, color=color, lw=2.5, label='Gas Turbine $\\eta_{GT}$')
    ax1.plot(rp_opt, eta_max, 'ro', markersize=8, label=f'Peak $\\eta_{{GT}} = {eta_max:.2f}\\%$ at $r_p={rp_opt:.1f}$')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, linestyle='--', alpha=0.6)
    
    ax2 = ax1.twinx()
    color = 'tab:red'
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
    ax2.set_title(f'Artificial Neural Network (ANN)\n$R^2 = {surr_dict["r2_ann"]:.4f}$, RMSE = {surr_dict["rmse_ann"]*100:.3f}%')
    ax2.set_xlim([min_val2, max_val2])
    ax2.set_ylim([min_val2, max_val2])
    ax2.grid(True, linestyle='--', alpha=0.6)
    ax2.legend(loc='upper left')
    
    fig.tight_layout()
    save_path = os.path.join(OUTPUT_DIR, 'plot_parity_comparison.png')
    plt.savefig(save_path)
    plt.close()
    print(f"  Saved: {save_path}")


def plot_hrsg_t_q_diagram(det):
    hrsg = det['hrsg']
    st = det['st']
    
    Q_econ = hrsg['Q_econ']
    Q_evap = hrsg['Q_evap']
    Q_sup = hrsg['Q_sup']
    Q_tot = hrsg['Q_hrsg']
    
    Q_points_steam = [0, Q_econ, Q_econ + Q_evap, Q_tot]
    T_points_steam = [
        st['State8']['T'] - 273.15,
        st['T_sat_drum_C'],
        st['T_sat_drum_C'],
        st['State5']['T'] - 273.15
    ]
    
    Q_points_gas = [0, Q_econ, Q_econ + Q_evap, Q_tot]
    T_points_gas = [
        hrsg['T_gas_stack_C'],
        hrsg['T_gas_pinch'] - 273.15,
        hrsg['T_gas_after_sup'] - 273.15,
        hrsg['T_gas_in'] - 273.15
    ]
    
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(Q_points_gas, T_points_gas, 'r-o', lw=2.5, markersize=7, label='Exhaust Gas Stream')
    ax.plot(Q_points_steam, T_points_steam, 'b-s', lw=2.5, markersize=7, label='Water / Steam Stream')
    
    pinch_Q = Q_econ
    pinch_T_gas = hrsg['T_gas_pinch'] - 273.15
    pinch_T_steam = st['T_sat_drum_C']
    ax.annotate(f'Evaporator Pinch Point\n$\\Delta T_{{pinch}} = {pinch_T_gas - pinch_T_steam:.1f}$ K',
                xy=(pinch_Q, (pinch_T_gas + pinch_T_steam)/2),
                xytext=(pinch_Q + Q_tot*0.08, pinch_T_steam - 40),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8),
                fontsize=11, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.5))
    
    ax.annotate(f'Superheater Approach\n$\\Delta T_{{approach}} = {T_points_gas[-1] - T_points_steam[-1]:.1f}$ K',
                xy=(Q_tot, (T_points_gas[-1] + T_points_steam[-1])/2),
                xytext=(Q_tot - Q_tot*0.35, T_points_gas[-1] - 30),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8),
                fontsize=11, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.5))
    
    ax.set_xlabel('Heat Transferred $Q$ (kW)')
    ax.set_ylabel('Temperature (°C)')
    ax.set_title('HRSG Temperature–Heat Duty ($T–Q$) Diagram at Optimum', pad=15)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(loc='upper left')
    
    fig.tight_layout()
    save_path = os.path.join(OUTPUT_DIR, 'plot_t_q_hrsg.png')
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
    fig, ax1 = plt.subplots(figsize=(8, 5))
    color = 'tab:blue'
    ax1.set_xlabel('HRSG Inlet Gas Temperature Limit (°C)')
    ax1.set_ylabel('Optimal Efficiency $\\eta_{cc}$ (%)', color=color)
    ax1.plot(df_sens['limit_C'], df_sens['eta_cc'], 'o-', color=color, lw=2.5, markersize=8)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, linestyle='--', alpha=0.6)
    
    ax2 = ax1.twinx()
    color = 'tab:green'
    ax2.set_ylabel('Net Power Output $\\dot{W}_{net}$ (MW)', color=color)
    ax2.plot(df_sens['limit_C'], df_sens['Wnet_MW'], 's--', color=color, lw=2.5, markersize=8)
    ax2.tick_params(axis='y', labelcolor=color)
    
    plt.title('Sensitivity Study: Effect of HRSG Inlet Temperature Limit', pad=15)
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
    
    # 2. Part B: Latin Hypercube Sampling (N=500)
    doe_csv_path = os.path.join(OUTPUT_DIR, 'doe_samples.csv')
    if os.path.exists(doe_csv_path):
        print(f"\n[Step 1] Loading existing DOE samples from {doe_csv_path}...")
        df_doe = pd.read_csv(doe_csv_path)
        print(f"  Loaded {len(df_doe)} samples. Feasible: {df_doe['feasible'].sum()}")
    else:
        df_doe = run_lhs_doe(n_samples=500, hrsg_limit_C=650.0)
        df_doe.to_csv(doe_csv_path, index=False)
    
    # 3. Fit Surrogates & Evaluate
    surr_dict = train_surrogates(df_doe)
    plot_parity_and_residuals(surr_dict)
    
    # 4 & 5: Single-Objective GA & Verification
    best_x, surr_eta = optimize_surrogate_ga(surr_dict, hrsg_limit_C=650.0)
    final_x, eta_opt, Wnet_opt, margins_opt, det_opt = adaptive_refinement(
        surr_dict, best_x, hrsg_limit_C=650.0, max_refinements=2
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
    
    # 6. Plot HRSG T-Q Diagram at Optimum
    plot_hrsg_t_q_diagram(det_opt)
    
    # 7. Part C: Sensitivity Study (HRSG Inlet Limits)
    df_sens = run_sensitivity_study(surr_dict)
    df_sens.to_csv(os.path.join(OUTPUT_DIR, 'sensitivity_hrsg_limit.csv'), index=False)
    print("\n--- SENSITIVITY STUDY RESULTS ---")
    print(df_sens.to_string(index=False))
    plot_sensitivity_results(df_sens)
    
    # 8. Part C: Bi-Objective Pareto Front (NSGA-II)
    pareto_eta, pareto_wnet, pareto_X = run_biobjective_pareto(surr_dict, det_opt, hrsg_limit_C=650.0)
    plot_pareto_front(pareto_eta, pareto_wnet, det_opt)
    
    print("\n>>> PROJECT 1 MASTER WORKFLOW COMPLETED SUCCESSFULLY! <<<")

if __name__ == '__main__':
    main()
