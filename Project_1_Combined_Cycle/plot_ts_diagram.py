"""
plot_ts_diagram.py
Generates the Temperature-Entropy (T-s) diagram for the combined cycle plant at the optimum.
Shows Brayton topping cycle and Rankine bottoming cycle on aligned temperature scales.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import CoolProp.CoolProp as CP
from thermo_gas import GasMixture
from combined_cycle import direct_model

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Run at optimum operating point:
eta_cc, Wnet, margins, feasible, det = direct_model(
    rp=21.68, TIT=1500.0, Ps=46.48, Ts=812.6, Pcond=0.05
)

gt = det['gt']
st = det['st']
hrsg = det['hrsg']

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# ---------------------------------------------------------
# Subplot 1: Gas Turbine (Brayton Cycle) T-s Diagram
# ---------------------------------------------------------
air = GasMixture('Air')
prod = gt['prod_mix']

s1 = 0.0
s2s = s1
s2 = s1 + (gt['h2'] - gt['h2s']) / ((gt['T2'] + gt['T2s'])/2)
s3 = s2 + (gt['h3'] - gt['h2']) / ((gt['TIT'] + gt['T2'])/2)
s4s = s3
s4 = s3 + (gt['h4'] - gt['h4s']) / ((gt['T4'] + gt['T4s'])/2)

gt_s = [s1, s2, s3, s4, s1]
gt_T = [gt['T1'] - 273.15, gt['T2'] - 273.15, gt['TIT'] - 273.15, gt['T4'] - 273.15, gt['T1'] - 273.15]

ax1.plot(gt_s, gt_T, 'r-o', lw=2.5, markersize=8, label='Topping Brayton Cycle')
ax1.plot([s1, s2s], [gt['T1'] - 273.15, gt['T2s'] - 273.15], 'k--', lw=1.5, label='Isentropic 1-2s')
ax1.plot([s3, s4s], [gt['TIT'] - 273.15, gt['T4s'] - 273.15], 'k--', lw=1.5, label='Isentropic 3-4s')

for label, s_val, T_val in zip(['1', '2', '3', '4'], [s1, s2, s3, s4], gt_T[:4]):
    ax1.annotate(f'State {label}\n({T_val:.0f} °C)', (s_val, T_val),
                 textcoords="offset points", xytext=(10, -5 if label in ['2', '4'] else 5),
                 fontweight='bold', fontsize=10)

ax1.set_xlabel('Entropy $s - s_1$ (kJ/kg·K)')
ax1.set_ylabel('Temperature (°C)')
ax1.set_title(f'Brayton Topping Cycle ($r_p = 21.7$, $TIT = 1500$ K)\nNet Work = {det["W_gt_net"]/1000:.1f} MW')
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.legend(loc='upper left')

# ---------------------------------------------------------
# Subplot 2: Steam Turbine (Rankine Cycle) T-s Diagram
# ---------------------------------------------------------
P_crit = CP.PropsSI('PCRIT', 'Water')
T_crit = CP.PropsSI('TCRIT', 'Water') - 273.15
T_dome = np.linspace(25.0, T_crit - 0.5, 80)
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

ax2.plot(st_s, st_T, 'b-s', lw=2.5, markersize=7, label='Bottoming Rankine Cycle')
ax2.plot([s5, s6s], [T5, T6], 'g--', lw=1.5, label='Isentropic 5-6s')

for label, s_val, T_val in zip(['5', '6', '7', '8'], [s5, s6, s7, s8], [T5, T6, T7, T8]):
    ax2.annotate(f'State {label}\n({T_val:.0f} °C)', (s_val, T_val),
                 textcoords="offset points", xytext=(8, -5 if label in ['6', '7'] else 5),
                 fontweight='bold', fontsize=10)

ax2.set_xlabel('Entropy $s$ (kJ/kg·K)')
ax2.set_ylabel('Temperature (°C)')
ax2.set_title(f'Rankine Bottoming Cycle ($P_s = 46.5$ bar, $T_s = 539$ °C)\nNet Work = {det["W_st_net"]/1000:.1f} MW')
ax2.grid(True, linestyle='--', alpha=0.6)
ax2.legend(loc='upper left')

fig.tight_layout()
save_path = os.path.join(OUTPUT_DIR, 'plot_t_s_diagram.png')
plt.savefig(save_path)
plt.close()
print(f"Saved: {save_path}")
