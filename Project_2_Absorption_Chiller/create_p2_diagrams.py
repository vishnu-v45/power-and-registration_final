"""
ME3160 Project 2 - Diagram Generator for Schematics and Flowcharts
Generates publication-quality schematic diagrams:
1. schematic_cycle_p2.png (Labelled absorption cycle with numbered state points 1-10)
2. schematic_ahu_p2.png (Zone AHU psychrometric process, coil, fan, room, and decanter drain)
3. flowchart_algorithm_p2.png (Multi-tier computational algorithm flowchart)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib
matplotlib.use('Agg')

plt.rcParams['font.family'] = 'DejaVu Sans'

def create_absorption_cycle_schematic():
    fig, ax = plt.subplots(figsize=(10, 7), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Color palette
    c_gen = '#e6550d'    # Orange/Red for Generator/Rectifier
    c_cond = '#31a354'   # Green for Condenser
    c_evap = '#3182bd'   # Blue for Evaporator
    c_abs = '#756bb1'    # Purple for Absorber
    c_shx = '#636363'    # Gray for SHX
    c_bg = '#f7f7f7'

    # Background title
    ax.text(5.0, 7.6, "Single-Effect Ammonia–Water Absorption Chiller Network", 
            ha='center', va='center', fontsize=14, fontweight='bold', color='#102C57')

    # 1. Generator Box (top left)
    rect_gen = patches.FancyBboxPatch((0.8, 4.5), 2.2, 2.2, boxstyle="round,pad=0.1", 
                                      fc='#fee6ce', ec=c_gen, lw=2.5)
    ax.add_patch(rect_gen)
    ax.text(1.9, 6.2, "GENERATOR\n(Desorber)", ha='center', va='center', fontsize=11, fontweight='bold', color=c_gen)
    ax.text(1.9, 5.0, "T_gen = T_bub(P_high, x_w)\nP_high = 10–16 bar", ha='center', va='center', fontsize=8.5, color='#7f2704')

    # Flue gas heat input arrow
    ax.annotate("Flue Gas Heat Q_gen\n(300 °C in → ≥140 °C out)", xy=(0.8, 5.6), xytext=(-0.5, 5.6),
                arrowprops=dict(facecolor='#d94801', edgecolor='#7f2704', width=2.5, headwidth=8),
                fontsize=8.5, fontweight='bold', color='#d94801', va='center', ha='right')

    # Rectifier on top of generator
    rect_rect = patches.FancyBboxPatch((1.2, 6.7), 1.4, 0.7, boxstyle="round,pad=0.05",
                                       fc='#fdd0a2', ec='#d94801', lw=1.8)
    ax.add_patch(rect_rect)
    ax.text(1.9, 7.05, "RECTIFIER\n(y_r = 99.5%)", ha='center', va='center', fontsize=8, fontweight='bold', color='#a63603')
    ax.annotate("Q_rect", xy=(2.6, 7.05), xytext=(3.3, 7.05),
                arrowprops=dict(facecolor='#d94801', arrowstyle="->", lw=1.5),
                fontsize=8, fontweight='bold', color='#d94801', va='center')

    # 2. Condenser Box (top right)
    rect_cond = patches.FancyBboxPatch((7.0, 5.0), 2.2, 1.8, boxstyle="round,pad=0.1",
                                       fc='#e5f5e0', ec=c_cond, lw=2.5)
    ax.add_patch(rect_cond)
    ax.text(8.1, 6.2, "CONDENSER", ha='center', va='center', fontsize=11, fontweight='bold', color=c_cond)
    ax.text(8.1, 5.4, "Evaporative Cooling\nT_cond = Twb + 7.4 K\nP_high ≤ 20 bar", ha='center', va='center', fontsize=8.5, color='#006d2c')
    ax.annotate("Heat Rejection Q_cond\nto ambient wet-bulb", xy=(9.2, 5.9), xytext=(10.5, 5.9),
                arrowprops=dict(facecolor='#2ca02c', edgecolor='#006d2c', width=2.5, headwidth=8),
                fontsize=8.5, fontweight='bold', color='#2ca02c', va='center', ha='left')

    # 3. Evaporator Box (bottom right)
    rect_evap = patches.FancyBboxPatch((7.0, 0.8), 2.2, 1.8, boxstyle="round,pad=0.1",
                                       fc='#deebf7', ec=c_evap, lw=2.5)
    ax.add_patch(rect_evap)
    ax.text(8.1, 2.0, "EVAPORATOR", ha='center', va='center', fontsize=11, fontweight='bold', color=c_evap)
    ax.text(8.1, 1.2, "T_evap = 2.0 °C\nP_low ≈ 4.58 bar\nSaturated Vapor", ha='center', va='center', fontsize=8.5, color='#08519c')
    ax.annotate("District Cooling Q_evap\nChilled Water: 7 °C / 12 °C", xy=(9.2, 1.7), xytext=(10.5, 1.7),
                arrowprops=dict(facecolor='#08519c', edgecolor='#08306b', width=2.5, headwidth=8),
                fontsize=8.5, fontweight='bold', color='#08519c', va='center', ha='left')

    # 4. Absorber Box (bottom left)
    rect_abs = patches.FancyBboxPatch((0.8, 0.8), 2.2, 1.8, boxstyle="round,pad=0.1",
                                      fc='#efedf5', ec=c_abs, lw=2.5)
    ax.add_patch(rect_abs)
    ax.text(1.9, 2.0, "ABSORBER", ha='center', va='center', fontsize=11, fontweight='bold', color=c_abs)
    ax.text(1.9, 1.2, "T_abs = T_cond\nP_low = 4.58 bar\nStrong Sol Out (x_s)", ha='center', va='center', fontsize=8.5, color='#54278f')
    ax.annotate("Absorber Duty Q_abs\nCooled by evaporative loop", xy=(0.8, 1.4), xytext=(-0.5, 1.4),
                arrowprops=dict(facecolor='#756bb1', edgecolor='#54278f', width=2.5, headwidth=8),
                fontsize=8.5, fontweight='bold', color='#756bb1', va='center', ha='right')

    # 5. SHX Box (center)
    rect_shx = patches.FancyBboxPatch((3.8, 2.7), 2.4, 1.6, boxstyle="round,pad=0.1",
                                      fc='#f0f0f0', ec=c_shx, lw=2.0)
    ax.add_patch(rect_shx)
    ax.text(5.0, 3.8, "SOLUTION HEAT\nEXCHANGER (SHX)", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#252525')
    ax.text(5.0, 3.1, "ε_SHX = 0.70\nSaves >3400 kW heat!", ha='center', va='center', fontsize=8, color='#525252')

    # 6. Solution Pump (bottom middle-left)
    pump_circle = patches.Circle((2.5, 3.3), 0.35, fc='#bcbddc', ec='#54278f', lw=2.0)
    ax.add_patch(pump_circle)
    ax.text(2.5, 3.3, "P", ha='center', va='center', fontsize=11, fontweight='bold', color='#3f007d')
    ax.text(2.5, 2.75, "Pump (η=70%)", ha='center', va='center', fontsize=7.5, color='#54278f')

    # 7. Expansion Valves
    # Refrigerant TXV (right)
    txv = patches.Polygon([[8.1, 4.3], [7.8, 3.8], [8.4, 3.8]], closed=True, fc='#fdae6b', ec='#e6550d', lw=1.5)
    ax.add_patch(txv)
    ax.text(8.65, 4.0, "TXV\n(h9 = h8)", ha='left', va='center', fontsize=7.5, fontweight='bold', color='#d94801')

    # Weak Solution Throttle (center-left)
    throttle = patches.Polygon([[3.4, 2.3], [3.2, 1.9], [3.6, 1.9]], closed=True, fc='#dadaeb', ec='#6a51a3', lw=1.5)
    ax.add_patch(throttle)
    ax.text(3.7, 2.1, "Throttle\n(h6 = h5)", ha='left', va='center', fontsize=7.5, fontweight='bold', color='#54278f')

    # PIPING / STREAMS & LABELS
    # State 7: Rectifier to Condenser
    ax.annotate("", xy=(7.0, 6.7), xytext=(2.6, 7.05),
                arrowprops=dict(arrowstyle="->", color='#e6550d', lw=2.2))
    ax.text(4.8, 7.15, "State 7: NH3 Vapor (y=0.995, T_dew, P_high)", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#e6550d')

    # State 8: Condenser to TXV
    ax.annotate("", xy=(8.1, 4.3), xytext=(8.1, 5.0),
                arrowprops=dict(arrowstyle="->", color='#31a354', lw=2.2))
    ax.text(8.25, 4.7, "8: Sat. Liq (h8, P_high)", ha='left', va='center', fontsize=8, fontweight='bold', color='#238b45')

    # State 9: TXV to Evaporator
    ax.annotate("", xy=(8.1, 2.6), xytext=(8.1, 3.8),
                arrowprops=dict(arrowstyle="->", color='#3182bd', lw=2.2))
    ax.text(8.25, 3.2, "9: 2-Phase (P_low)", ha='left', va='center', fontsize=8, fontweight='bold', color='#2171b5')

    # State 10: Evaporator to Absorber
    ax.annotate("", xy=(3.0, 1.0), xytext=(7.0, 1.0),
                arrowprops=dict(arrowstyle="->", color='#3182bd', lw=2.2))
    ax.text(5.0, 0.7, "State 10: Saturated Vapor NH3 (T_evap = 2 °C, P_low)", ha='center', va='top', fontsize=8.5, fontweight='bold', color='#08519c')

    # State 1: Absorber to Pump
    ax.annotate("", xy=(2.5, 2.95), xytext=(2.0, 2.6),
                arrowprops=dict(arrowstyle="->", color='#756bb1', lw=2.0))
    ax.text(1.5, 2.9, "1: Strong Sol\n(Tabs, Plow, x_s)", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#54278f')

    # State 2: Pump to SHX
    ax.annotate("", xy=(3.8, 3.5), xytext=(2.85, 3.3),
                arrowprops=dict(arrowstyle="->", color='#756bb1', lw=2.0))
    ax.text(3.3, 3.65, "2: P_high", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#54278f')

    # State 3: SHX to Generator
    ax.annotate("", xy=(2.5, 4.5), xytext=(4.0, 4.3),
                arrowprops=dict(arrowstyle="->", color='#756bb1', lw=2.0))
    ax.text(3.4, 4.7, "3: Preheated\nStrong Sol (T3)", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#54278f')

    # State 4: Generator to SHX (weak solution)
    ax.annotate("", xy=(5.8, 4.3), xytext=(3.0, 4.7),
                arrowprops=dict(arrowstyle="->", color='#e6550d', lw=2.0, linestyle='--'))
    ax.text(4.7, 5.0, "4: Weak Sol Out (T_gen, x_w)", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#a63603')

    # State 5: SHX to Throttle
    ax.annotate("", xy=(3.4, 2.3), xytext=(4.2, 2.7),
                arrowprops=dict(arrowstyle="->", color='#756bb1', lw=2.0, linestyle='--'))
    ax.text(4.1, 2.3, "5: Cooled Weak Sol", ha='left', va='center', fontsize=7.5, fontweight='bold', color='#54278f')

    # State 6: Throttle to Absorber
    ax.annotate("", xy=(2.8, 2.2), xytext=(3.3, 1.9),
                arrowprops=dict(arrowstyle="->", color='#756bb1', lw=2.0, linestyle='--'))
    ax.text(2.5, 1.7, "6: Weak Sol (P_low)", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#54278f')

    plt.tight_layout()
    plt.savefig("schematic_cycle_p2.png")
    plt.close()
    print("[Saved] schematic_cycle_p2.png")

def create_ahu_schematic():
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis('off')

    ax.text(5.0, 6.7, "Zone Air Handling Unit (AHU) & Central Decanter Drainage", 
            ha='center', va='center', fontsize=14, fontweight='bold', color='#102C57')

    # Outdoor Air stream
    ax.annotate("Outdoor Air (OA)\n30% Fresh Air (40% test)\n(T_oa, RH_oa, w_oa)", xy=(1.5, 5.0), xytext=(0.2, 5.0),
                arrowprops=dict(facecolor='#d95f02', edgecolor='#a63603', width=2.5, headwidth=7),
                fontsize=8.5, fontweight='bold', color='#d95f02', va='center')

    # Return Air stream
    ax.annotate("Return Air (RA)\n70% Recirculated\n(22 °C, w_room)", xy=(1.5, 3.6), xytext=(0.2, 3.6),
                arrowprops=dict(facecolor='#7570b3', edgecolor='#54278f', width=2.5, headwidth=7),
                fontsize=8.5, fontweight='bold', color='#7570b3', va='center')

    # Mixing Plenum
    mix_box = patches.FancyBboxPatch((1.6, 3.2), 1.2, 2.4, boxstyle="round,pad=0.08",
                                     fc='#f0f0f0', ec='#636363', lw=2.0)
    ax.add_patch(mix_box)
    ax.text(2.2, 4.4, "MIXING\nPLENUM\n(T_mix, w_mix)", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#252525')

    # Arrow to Coil
    ax.annotate("", xy=(3.6, 4.4), xytext=(2.8, 4.4), arrowprops=dict(arrowstyle="->", lw=2.5, color='#252525'))

    # Cooling Coil
    coil_box = patches.FancyBboxPatch((3.6, 3.2), 1.6, 2.4, boxstyle="round,pad=0.08",
                                      fc='#deebf7', ec='#2171b5', lw=2.5)
    ax.add_patch(coil_box)
    ax.text(4.4, 4.7, "COOLING\nCOIL", ha='center', va='center', fontsize=11, fontweight='bold', color='#08519c')
    ax.text(4.4, 3.8, "Fin ADP State\nBF = 0.10\n(w_adp sat)", ha='center', va='center', fontsize=8.5, color='#2171b5')

    # Chilled water lines
    ax.annotate("Chilled Water In (7 °C)", xy=(4.4, 5.6), xytext=(4.4, 6.2),
                arrowprops=dict(facecolor='#08519c', arrowstyle="->", lw=2.0),
                fontsize=8, fontweight='bold', color='#08519c', ha='center')
    ax.annotate("Chilled Water Return (12 °C)", xy=(4.4, 3.2), xytext=(4.4, 2.6),
                arrowprops=dict(facecolor='#08519c', arrowstyle="<-", lw=2.0),
                fontsize=8, fontweight='bold', color='#08519c', ha='center')

    # Drain Pan & Central Decanter (bottom)
    drain_pan = patches.Rectangle((3.6, 2.95), 1.6, 0.2, fc='#9ecae1', ec='#08519c', lw=1.5)
    ax.add_patch(drain_pan)
    ax.annotate("", xy=(4.4, 1.8), xytext=(4.4, 2.95), arrowprops=dict(arrowstyle="->", lw=2.0, color='#08519c'))
    ax.text(4.55, 2.3, "Condensate Trap\nm_cond = m_da·(w_mix - w_sup)", ha='left', va='center', fontsize=7.5, color='#08519c')

    # Central Decanter Box
    decanter = patches.FancyBboxPatch((3.2, 0.6), 2.4, 1.1, boxstyle="round,pad=0.08",
                                     fc='#c6dbef', ec='#08519c', lw=2.0)
    ax.add_patch(decanter)
    ax.text(4.4, 1.25, "CENTRAL WATER DECANTER", ha='center', va='center', fontsize=9, fontweight='bold', color='#08306b')
    ax.text(4.4, 0.85, "1000 Zones Network Sizing:\nPeak Monsoon Day = 89.7 m³/day (3738 kg/h)", ha='center', va='center', fontsize=7.5, color='#08519c')

    # Arrow from Coil to Fan
    ax.annotate("", xy=(5.8, 4.4), xytext=(5.2, 4.4), arrowprops=dict(arrowstyle="->", lw=2.5, color='#252525'))

    # Supply Fan
    fan = patches.Circle((6.2, 4.4), 0.4, fc='#fee8c8', ec='#e6550d', lw=2.0)
    ax.add_patch(fan)
    ax.text(6.2, 4.4, "FAN", ha='center', va='center', fontsize=9, fontweight='bold', color='#d94801')
    ax.text(6.2, 3.8, "+2% Fan/Pump\nHeat Gain", ha='center', va='center', fontsize=7.5, color='#7f2704')

    # Terminal Reheat Coil (Task 4)
    reheat_box = patches.FancyBboxPatch((7.0, 3.6), 0.8, 1.6, boxstyle="round,pad=0.05",
                                       fc='#fee0d2', ec='#de2d26', lw=1.8)
    ax.add_patch(reheat_box)
    ax.text(7.4, 4.4, "REHEAT\nCOIL\n(Task 4)", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#a50f15')

    # Arrow to Room
    ax.annotate("", xy=(8.4, 4.4), xytext=(7.8, 4.4), arrowprops=dict(arrowstyle="->", lw=2.5, color='#252525'))
    ax.text(8.05, 4.7, "Supply Air\n(T_sup, w_sup)", ha='center', va='bottom', fontsize=8, fontweight='bold')

    # Zone Room Box
    room_box = patches.FancyBboxPatch((8.4, 2.8), 1.5, 3.2, boxstyle="round,pad=0.08",
                                     fc='#e5f5e0', ec='#2ca02c', lw=2.5)
    ax.add_patch(room_box)
    ax.text(9.15, 5.4, "ZONE ROOM\n(40 m²)", ha='center', va='center', fontsize=10, fontweight='bold', color='#006d2c')
    ax.text(9.15, 4.3, "T_room = 22.0 °C\nRH_room ≤ 75%\nQ_sens = 7.0 kW\nQ_lat = 3.0 kW\nInternal: 1100 W", ha='center', va='center', fontsize=8, color='#00441b')

    # Return air duct back to plenum
    ax.annotate("", xy=(2.2, 3.2), xytext=(8.4, 3.2),
                arrowprops=dict(arrowstyle="->", lw=1.8, color='#7570b3', linestyle='--'))
    ax.text(5.5, 3.0, "Recirculated Room Air Duct (RA = 70%)", ha='center', va='top', fontsize=8, color='#54278f', fontweight='bold')

    plt.tight_layout()
    plt.savefig("schematic_ahu_p2.png")
    plt.close()
    print("[Saved] schematic_ahu_p2.png")

def create_algorithm_flowchart():
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis('off')

    ax.text(5.0, 6.7, "Multi-Tiered Computational Solver Architecture", 
            ha='center', va='center', fontsize=14, fontweight='bold', color='#102C57')

    # Box 1: Input Ambient
    b1 = patches.FancyBboxPatch((0.5, 5.2), 2.4, 1.1, boxstyle="round,pad=0.08", fc='#edf8fb', ec='#006d2c', lw=2.0)
    ax.add_patch(b1)
    ax.text(1.7, 5.75, "INPUTS:\nAmbient (T_oa, RH_oa)\nFresh Air Fraction f_oa", ha='center', va='center', fontsize=8.5, fontweight='bold')

    # Arrow 1->2
    ax.annotate("", xy=(3.5, 5.75), xytext=(2.9, 5.75), arrowprops=dict(arrowstyle="->", lw=2.2))

    # Box 2: Tier 1 Psychrometrics
    b2 = patches.FancyBboxPatch((3.5, 4.8), 2.8, 1.9, boxstyle="round,pad=0.08", fc='#e0f3f8', ec='#0868ac', lw=2.0)
    ax.add_patch(b2)
    ax.text(4.9, 6.35, "TIER 1: PSYCHROMETRIC SOLVER", ha='center', va='center', fontsize=9, fontweight='bold', color='#084081')
    ax.text(4.9, 5.45, "• Adiabatic saturation → Twb_oa\n• Sensible heat → T_supply\n• Room humidity loop (w_room)\n• Invert coil ADP & condensate\n• District scaling (+5% dist, +2% pump)", ha='center', va='center', fontsize=7.5)

    # Arrow 2->3
    ax.annotate("", xy=(6.9, 5.75), xytext=(6.3, 5.75), arrowprops=dict(arrowstyle="->", lw=2.2))

    # Box 3: Output Chiller Duty
    b3 = patches.FancyBboxPatch((6.9, 5.2), 2.6, 1.1, boxstyle="round,pad=0.08", fc='#fee8c8', ec='#e6550d', lw=2.0)
    ax.add_patch(b3)
    ax.text(8.2, 5.75, "OUTPUT:\nDistrict Q_evap (kW)\nCondensate (m³/day)", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#7f2704')

    # Arrow down to Tier 2 & 3
    ax.annotate("", xy=(8.2, 4.1), xytext=(8.2, 5.2), arrowprops=dict(arrowstyle="->", lw=2.2))

    # Box 4: Tier 2 Real-Gas Engine
    b4 = patches.FancyBboxPatch((0.5, 2.5), 3.4, 1.6, boxstyle="round,pad=0.08", fc='#f7fcf5', ec='#238b45', lw=2.0)
    ax.add_patch(b4)
    ax.text(2.2, 3.75, "TIER 2: THERMODYNAMICS ENGINE", ha='center', va='center', fontsize=9, fontweight='bold', color='#005a32')
    ax.text(2.2, 2.95, "• Peng-Robinson EOS + Lee-Kesler (NH3)\n• Pátek & Klomfar (1995) Tables 1 & 2\n• Bubble T_bub(P, x) & Dew T_dew(P, y)\n• Liquid & Vapor Enthalpies (0 °C Ref)", ha='center', va='center', fontsize=7.5)

    # Arrow 4->5
    ax.annotate("", xy=(4.5, 3.3), xytext=(3.9, 3.3), arrowprops=dict(arrowstyle="->", lw=2.2))

    # Box 5: Tier 3 Cycle Solver
    b5 = patches.FancyBboxPatch((4.5, 2.3), 5.0, 2.0, boxstyle="round,pad=0.08", fc='#fff7bc', ec='#d95f0e', lw=2.0)
    ax.add_patch(b5)
    ax.text(7.0, 3.95, "TIER 3: ABSORPTION CYCLE & OFF-DESIGN MAP", ha='center', va='center', fontsize=9, fontweight='bold', color='#993404')
    ax.text(7.0, 3.0, "• Fixed UA Evaporative Condenser Energy Balance:\n  Solve Q_cond(T_cond) = UA · LMTD(T_cond, Twb, Twb_out)\n• Dynamic T_gen = T_bub(P_high, x_w), tracking condensing pressure\n• Solution mass & species balance; SHX recuperation (ε=0.70)\n• Rigorous Rectifier Reflux balance (no fudge factors)", ha='center', va='center', fontsize=7.5)

    # Arrow down to Verification
    ax.annotate("", xy=(7.0, 1.4), xytext=(7.0, 2.3), arrowprops=dict(arrowstyle="->", lw=2.2))

    # Box 6: Constraint Checks & Remedies
    b6 = patches.FancyBboxPatch((1.5, 0.2), 7.0, 1.2, boxstyle="round,pad=0.08", fc='#fee0d2', ec='#de2d26', lw=2.0)
    ax.add_patch(b6)
    ax.text(5.0, 1.05, "CRITICAL CONSTRAINTS & REMEDIES VERIFICATION", ha='center', va='center', fontsize=9, fontweight='bold', color='#99000d')
    ax.text(5.0, 0.55, "✓ (a) P_high ≤ 20 bar vessel design limit  |  ✓ (b) T_gen deliverable by 300 °C flue gas with ≥140 °C floor\n✓ (c) Head pressure floor (T_cond ≥ 25 °C)  |  ✓ Turndown ≥ 25% (Winter Night free cooling trigger)\n✓ Task 4: Modulated ADP (15.16 °C) + 1.19 K reheat eliminates Monsoon Night RH drift", ha='center', va='center', fontsize=7.5)

    plt.tight_layout()
    plt.savefig("flowchart_algorithm_p2.png")
    plt.close()
    print("[Saved] flowchart_algorithm_p2.png")

if __name__ == '__main__':
    create_absorption_cycle_schematic()
    create_ahu_schematic()
    create_algorithm_flowchart()
