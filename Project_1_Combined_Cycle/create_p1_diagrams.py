"""
create_p1_diagrams.py
Generates publication-quality technical schematics and algorithm flowchart for Project 1:
1. schematic_cycle_p1.png: Combined Cycle Plant Layout with States 1-8
2. schematic_hrsg_p1.png: HRSG Counterflow Heat Exchanger Configuration
3. flowchart_pipeline_p1.png: Direct Model, Surrogate Pipeline, GA Optimization & Refinement
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

plt.rcParams.update({
    'font.size': 11,
    'font.family': 'sans-serif',
    'figure.dpi': 300,
    'savefig.dpi': 300,
})

def draw_combined_cycle_schematic():
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis('off')
    
    # Title
    ax.text(7, 8.6, "Methane-Fired Combined Cycle Plant Architecture (ME3160)",
            fontsize=15, fontweight='bold', ha='center', color='#1A365D')
    
    # ------------------ TOPPING BRAYTON CYCLE ------------------
    # Compressor
    c_box = patches.Polygon([[1.2, 5.0], [2.2, 5.4], [2.2, 6.6], [1.2, 7.0]],
                            closed=True, facecolor='#E2E8F0', edgecolor='#2B6CB0', lw=2)
    ax.add_patch(c_box)
    ax.text(1.7, 6.0, "Compressor\n($\\eta_c = 0.86$)", ha='center', va='center', fontweight='bold', fontsize=10)
    
    # Combustor
    comb = patches.FancyBboxPatch((3.5, 6.5), 1.8, 1.2, boxstyle="round,pad=0.1",
                                  facecolor='#FED7D7', edgecolor='#C53030', lw=2)
    ax.add_patch(comb)
    ax.text(4.4, 7.1, "Combustor\n($\\eta_{comb} = 0.98$)\n$CH_4$ LHV=50 MJ/kg", ha='center', va='center', fontweight='bold', fontsize=9)
    
    # Gas Turbine
    t_box = patches.Polygon([[6.5, 7.2], [7.7, 6.8], [7.7, 5.2], [6.5, 4.8]],
                            closed=True, facecolor='#E2E8F0', edgecolor='#2B6CB0', lw=2)
    ax.add_patch(t_box)
    ax.text(7.1, 6.0, "Gas Turbine\n($\\eta_t = 0.89$)", ha='center', va='center', fontweight='bold', fontsize=10)
    
    # Shaft connecting C & T
    ax.plot([2.2, 6.5], [6.0, 6.0], 'k-', lw=4, zorder=1)
    ax.text(4.35, 5.7, "Shaft Work ($W_{net,GT} = W_t - W_c$)", ha='center', fontsize=9, fontweight='bold', color='#4A5568')
    
    # ------------------ HRSG SECTION ------------------
    hrsg_box = patches.FancyBboxPatch((8.8, 2.0), 2.2, 5.5, boxstyle="round,pad=0.15",
                                      facecolor='#EDF2F7', edgecolor='#4A5568', lw=2.5, ls='--')
    ax.add_patch(hrsg_box)
    ax.text(9.9, 7.2, "HRSG ($P_{drop}=3$ kPa)", ha='center', fontweight='bold', fontsize=11, color='#2D3748')
    
    # Superheater, Evaporator, Economizer inside HRSG
    sh_box = patches.Rectangle((9.0, 5.8), 1.8, 0.9, facecolor='#FEB2B2', edgecolor='#E53E3E', lw=1.5)
    evap_box = patches.Rectangle((9.0, 4.2), 1.8, 1.1, facecolor='#FEEBC8', edgecolor='#DD6B20', lw=1.5)
    econ_box = patches.Rectangle((9.0, 2.6), 1.8, 0.9, facecolor='#BEE3F8', edgecolor='#3182CE', lw=1.5)
    ax.add_patch(sh_box)
    ax.add_patch(evap_box)
    ax.add_patch(econ_box)
    
    ax.text(9.9, 6.25, "Superheater\n$\\Delta T_{app} \\geq 5$ K", ha='center', va='center', fontsize=8.5, fontweight='bold')
    ax.text(9.9, 4.75, "Evaporator & Drum\n$\\Delta T_{pinch} \\geq 10$ K", ha='center', va='center', fontsize=8.5, fontweight='bold')
    ax.text(9.9, 3.05, "Economizer\n$T_{feed} \\to T_{sat}^-$", ha='center', va='center', fontsize=8.5, fontweight='bold')
    
    # ------------------ BOTTOMING RANKINE CYCLE ------------------
    # Steam Turbine
    st_box = patches.Polygon([[11.8, 6.8], [12.8, 6.3], [12.8, 4.7], [11.8, 4.2]],
                             closed=True, facecolor='#EBF8FF', edgecolor='#2B6CB0', lw=2)
    ax.add_patch(st_box)
    ax.text(12.3, 5.5, "Steam\nTurbine\n($\\eta_{st}=0.85$)", ha='center', va='center', fontweight='bold', fontsize=9.5)
    
    # Condenser
    cond_box = patches.FancyBboxPatch((11.6, 2.2), 1.4, 1.1, boxstyle="round,pad=0.1",
                                      facecolor='#E2E8F0', edgecolor='#4A5568', lw=1.8)
    ax.add_patch(cond_box)
    ax.text(12.3, 2.75, "Condenser\n$P_{cond}$ (0.05-0.15 bar)\nSat. Liquid", ha='center', va='center', fontsize=8.5, fontweight='bold')
    
    # Feed Pump
    pump_circle = patches.Circle((11.4, 1.0), 0.45, facecolor='#E2E8F0', edgecolor='#2B6CB0', lw=1.8)
    ax.add_patch(pump_circle)
    ax.text(11.4, 1.0, "Pump\n$\\eta_p=0.8$", ha='center', va='center', fontsize=8, fontweight='bold')
    
    # ------------------ FLOW LINES & STATE POINTS ------------------
    arrow = dict(arrowstyle="->", lw=2.0, color='#2B6CB0')
    gas_arrow = dict(arrowstyle="->", lw=2.2, color='#C53030')
    steam_arrow = dict(arrowstyle="->", lw=2.2, color='#2B6CB0')
    
    # State 1: Air in
    ax.annotate("", xy=(1.2, 6.0), xytext=(0.2, 6.0), arrowprops=arrow)
    ax.text(0.6, 6.3, "State 1\nAir: 1.013 bar\n298 K, 100 kg/s", ha='center', fontsize=9, fontweight='bold', color='#2B6CB0')
    
    # State 2: Compressed air to combustor
    ax.annotate("", xy=(3.5, 7.1), xytext=(2.2, 6.0),
                arrowprops=dict(arrowstyle="->", lw=2.0, color='#2B6CB0', connectionstyle="arc3,rad=-0.15"))
    ax.text(2.6, 7.3, "State 2 ($P_2=r_p P_1$, $T_2$)", fontsize=9, fontweight='bold', color='#2B6CB0')
    
    # Fuel in to combustor
    ax.annotate("", xy=(4.4, 7.7), xytext=(4.4, 8.4), arrowprops=dict(arrowstyle="->", lw=2.2, color='#C53030'))
    ax.text(4.4, 8.55, "Fuel: $\\dot{m}_f$ ($CH_4$), $\\phi \\leq 0.5$", ha='center', fontsize=9, fontweight='bold', color='#C53030')
    
    # State 3: Combustor to Turbine
    ax.annotate("", xy=(6.5, 6.5), xytext=(5.3, 7.1),
                arrowprops=dict(arrowstyle="->", lw=2.2, color='#C53030', connectionstyle="arc3,rad=-0.1"))
    ax.text(6.0, 7.3, "State 3 (TIT $\\leq 1500$ K)", fontsize=9, fontweight='bold', color='#C53030')
    
    # State 4: Turbine exhaust to HRSG
    ax.annotate("", xy=(8.8, 6.0), xytext=(7.7, 6.0), arrowprops=gas_arrow)
    ax.text(8.25, 6.35, "State 4\n$T_4 \\leq 650$ °C", ha='center', fontsize=9, fontweight='bold', color='#C53030')
    
    # Stack exhaust from HRSG
    ax.annotate("", xy=(8.8, 2.7), xytext=(7.8, 2.7), arrowprops=dict(arrowstyle="<-", lw=2.2, color='#718096'))
    ax.text(7.2, 2.7, "Stack Exhaust\n$T_{stack} \\geq 100$ °C", ha='center', va='center', fontsize=9, fontweight='bold', color='#718096')
    
    # State 5: Superheated steam to Steam Turbine
    ax.annotate("", xy=(11.8, 6.2), xytext=(10.8, 6.2), arrowprops=steam_arrow)
    ax.text(11.3, 6.5, "State 5 ($P_s, T_s$)", ha='center', fontsize=9, fontweight='bold', color='#2B6CB0')
    
    # State 6: Steam Turbine exhaust to Condenser
    ax.annotate("", xy=(12.3, 3.3), xytext=(12.3, 4.7), arrowprops=steam_arrow)
    ax.text(12.9, 4.0, "State 6 ($x_6 \\geq 0.88$)", ha='center', fontsize=9, fontweight='bold', color='#2B6CB0')
    
    # State 7: Condenser exit to Pump
    ax.plot([12.3, 12.3, 11.85], [2.2, 1.0, 1.0], 'b-', lw=2.0)
    ax.annotate("", xy=(11.85, 1.0), xytext=(12.0, 1.0), arrowprops=steam_arrow)
    ax.text(12.5, 1.3, "State 7\nSat. Liquid", ha='center', fontsize=8.5, fontweight='bold', color='#2B6CB0')
    
    # State 8: Pump discharge to HRSG Economizer
    ax.plot([10.95, 9.9, 9.9], [1.0, 1.0, 2.6], 'b-', lw=2.0)
    ax.annotate("", xy=(9.9, 2.6), xytext=(9.9, 2.3), arrowprops=steam_arrow)
    ax.text(10.5, 1.6, "State 8 ($P_s$, subcooled)", ha='center', fontsize=8.5, fontweight='bold', color='#2B6CB0')
    
    fig.tight_layout()
    save_path = os.path.join(OUTPUT_DIR, 'schematic_cycle_p1.png')
    plt.savefig(save_path)
    plt.close()
    print(f"Saved: {save_path}")


def draw_pipeline_flowchart():
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    ax.text(7, 9.6, "Project 1 Computational Architecture & Optimization Flowchart",
            fontsize=15, fontweight='bold', ha='center', color='#1A365D')
    
    box_blue = dict(boxstyle="round,pad=0.2", facecolor='#EBF8FF', edgecolor='#3182CE', lw=2)
    box_green = dict(boxstyle="round,pad=0.2", facecolor='#F0FFF4', edgecolor='#38A169', lw=2)
    box_gold = dict(boxstyle="round,pad=0.2", facecolor='#FEFCBF', edgecolor='#D69E2E', lw=2)
    box_red = dict(boxstyle="round,pad=0.2", facecolor='#FFF5F5', edgecolor='#E53E3E', lw=2)
    arrow = dict(arrowstyle="->", lw=2, color='#2D3748')
    
    # Step 1: Direct Physics Model
    p1 = patches.FancyBboxPatch((0.5, 6.0), 3.6, 2.8, **box_blue)
    ax.add_patch(p1)
    ax.text(2.3, 8.4, "PART A: DIRECT PHYSICS MODEL", fontweight='bold', ha='center', fontsize=10.5, color='#2B6CB0')
    ax.text(2.3, 7.2, "• Variable $C_p(T)$ air & combustion gas\n  (Borgnakke Table A.6 polynomials)\n• Newton-Raphson $f/A$ & TIT matching\n• Entropy integral isentropic solver\n• Counterflow HRSG pinch-point solver\n• Steam Rankine via CoolProp PropsSI",
            ha='center', va='center', fontsize=8.8)
    
    # Step 2: Latin Hypercube Sampling
    p2 = patches.FancyBboxPatch((5.0, 6.0), 3.8, 2.8, **box_blue)
    ax.add_patch(p2)
    ax.text(6.9, 8.4, "PART B: DESIGN OF EXPERIMENTS", fontweight='bold', ha='center', fontsize=10.5, color='#2B6CB0')
    ax.text(6.9, 7.2, "• 5-D Design Space:\n  $r_p \\in [8, 30]$, $TIT \\in [1200, 1500]$ K\n  $P_s \\in [10, 60]$ bar, $T_s \\in [T_{sat}+20, T_4-5]$ K\n  $P_{cond} \\in [0.05, 0.15]$ bar\n• N = 500 Latin Hypercube Samples\n• Record $\\eta_{cc}$, $W_{net}$, & 6 Constraint Margins",
            ha='center', va='center', fontsize=8.8)
    
    # Step 3: Surrogate Modeling
    p3 = patches.FancyBboxPatch((9.7, 6.0), 3.8, 2.8, **box_green)
    ax.add_patch(p3)
    ax.text(11.6, 8.4, "SURROGATE MODELING & ANOVA", fontweight='bold', ha='center', fontsize=10.5, color='#2F855A')
    ax.text(11.6, 7.2, "• 80/20 Train/Test Partition\n• Full Quadratic RSM + ANOVA Tables\n  (Significant linear, squared & cross terms)\n• ANN: MLPRegressor (2 hidden layers)\n  GridSearchCV Hyperparameter Tuning\n• Test-Set Parity & RMSE Verification",
            ha='center', va='center', fontsize=8.8)
    
    # Step 4: Optimization
    p4 = patches.FancyBboxPatch((9.7, 1.2), 3.8, 3.8, **box_gold)
    ax.add_patch(p4)
    ax.text(11.6, 4.6, "PART C: CONSTRAINED GA & NSGA-II", fontweight='bold', ha='center', fontsize=10.5, color='#B7791F')
    ax.text(11.6, 2.9, "• Single-Objective Genetic Algorithm:\n  Maximize $\\eta_{cc}$ subject to 6 constraints\n• Direct-Model Evaluation at Optimum:\n  Compute gap $|\\eta_{surr} - \\eta_{direct}|$\n• Adaptive Trust-Region Refinement:\n  If gap > 0.2%, inject localized LHS\n  samples, refit surrogates, & re-optimize\n• Bi-Objective NSGA-II:\n  Trade-off: Maximize $\\eta_{cc}$ & $\\dot{W}_{net}$",
            ha='center', va='center', fontsize=8.8)
    
    # Step 5: Verification & Sensitivity
    p5 = patches.FancyBboxPatch((5.0, 1.2), 3.8, 3.8, **box_blue)
    ax.add_patch(p5)
    ax.text(6.9, 4.6, "SENSITIVITY & MATERIAL ANALYSIS", fontweight='bold', ha='center', fontsize=10.5, color='#2B6CB0')
    ax.text(6.9, 2.9, "• HRSG Inlet Tube Limit Relaxation:\n  Tightened: 600 °C, Nominal: 650 °C,\n  Relaxed: 700 °C\n• Active Constraint Analysis:\n  Binding: TIT upper limit (1500 K),\n  $P_{cond}$ lower limit (0.05 bar),\n  $T_s$ approach ($T_4 - 5$ K)\n• Capital allocation recommendation",
            ha='center', va='center', fontsize=8.8)
    
    # Step 6: Validated Benchmark
    p6 = patches.FancyBboxPatch((0.5, 1.2), 3.6, 3.8, **box_green)
    ax.add_patch(p6)
    ax.text(2.3, 4.6, "RIGOROUS MODEL VALIDATION", fontweight='bold', ha='center', fontsize=10.5, color='#2F855A')
    ax.text(2.3, 2.9, "• Check 1: Borgnakke Table A.7 GT\n  Air-standard variable $C_p$ (<0.05% diff)\n• Check 2: Steam Tables via CoolProp\n  Subcooling, isentropic ST (<0.05% diff)\n• Check 3: Closed First Law Balance\n  Zero residual across 3 operating points\n• Check 4: Çengel Ex 10-7 Benchmark\n  Published Combined Cycle (<0.25% diff)",
            ha='center', va='center', fontsize=8.8)
    
    # Connecting Arrows
    ax.annotate("", xy=(5.0, 7.4), xytext=(4.1, 7.4), arrowprops=arrow)
    ax.annotate("", xy=(9.7, 7.4), xytext=(8.8, 7.4), arrowprops=arrow)
    ax.annotate("", xy=(11.6, 5.0), xytext=(11.6, 6.0), arrowprops=arrow)
    ax.annotate("", xy=(8.8, 3.1), xytext=(9.7, 3.1), arrowprops=arrow)
    ax.annotate("", xy=(4.1, 3.1), xytext=(5.0, 3.1), arrowprops=arrow)
    
    fig.tight_layout()
    save_path = os.path.join(OUTPUT_DIR, 'flowchart_pipeline_p1.png')
    plt.savefig(save_path)
    plt.close()
    print(f"Saved: {save_path}")

if __name__ == '__main__':
    draw_combined_cycle_schematic()
    draw_pipeline_flowchart()
