"""
ME3160 Project 2 - Professional Presentation Generator
Waste-Heat-Driven Ammonia-Water Absorption Chiller for a District Cooling Network
Author: Pair Programming Assistant

Generates Project2_Presentation.pptx strictly complying with Section 2.5:
1. Schematic: (a) Labelled absorption cycle with numbered state points 1-11;
              (b) Labelled zone AHU diagram with numbered psychrometric points
2. Algorithm: Structured pseudocode & flowchart of solver loops
3. Analysis: Master validation table, psychrometric chart, seasonal duties,
             condenser comparison, off-design map, and 40% fresh air sensitivity
4. Conclusion: Governing conditions, condenser selection, flue gas envelope,
               and single biggest design lever
"""

import os
import collections.abc
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette: Clean Executive Navy & Teal
    C_NAVY_DARK = RGBColor(16, 44, 87)     # #102C57
    C_NAVY_LIGHT = RGBColor(53, 95, 142)   # #355F8E
    C_TEAL = RGBColor(0, 150, 136)         # #009688
    C_ACCENT_ORANGE = RGBColor(227, 100, 20) # #E36414
    C_BG_LIGHT = RGBColor(248, 249, 250)   # #F8F9FA
    C_WHITE = RGBColor(255, 255, 255)
    C_DARK = RGBColor(33, 37, 41)
    C_GRAY = RGBColor(108, 117, 125)
    C_GREEN = RGBColor(46, 125, 50)
    C_RED = RGBColor(198, 40, 40)
    C_CARD_BG = RGBColor(241, 245, 249)

    def add_header(slide, title_text, category_text):
        # Header background banner
        banner = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.05))
        banner.fill.solid()
        banner.fill.fore_color.rgb = C_NAVY_DARK
        banner.line.color.rgb = C_NAVY_DARK

        # Category text
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.12), Inches(11.5), Inches(0.3))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = C_TEAL

        # Title text
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.38), Inches(11.5), Inches(0.55))
        tf_t = title_box.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = C_WHITE

    # =========================================================================
    # SLIDE 1: Title Slide
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = C_NAVY_DARK
    bg1.line.color.rgb = C_NAVY_DARK

    # Accent decorative bar
    bar1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.2), Inches(1.8), Inches(0.15), Inches(3.6))
    bar1.fill.solid()
    bar1.fill.fore_color.rgb = C_TEAL
    bar1.line.color.rgb = C_TEAL

    tb1 = slide1.shapes.add_textbox(Inches(1.5), Inches(1.8), Inches(10.5), Inches(3.6))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "ME3160 — Power & Refrigeration Cycles | Term Project 2"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_TEAL

    p2 = tf1.add_paragraph()
    p2.text = "Waste-Heat-Driven Ammonia–Water Absorption Chiller for a District Cooling Network"
    p2.font.size = Pt(30)
    p2.font.bold = True
    p2.font.color.rgb = C_WHITE
    p2.space_before = Pt(14)

    p3 = tf1.add_paragraph()
    p3.text = "Comprehensive Thermodynamic Analysis: Outdoor Air Psychrometrics → Chilled-Water Demand → Single-Effect Absorption Cycle → Industrial Flue-Gas Waste Heat Sizing"
    p3.font.size = Pt(15)
    p3.font.color.rgb = RGBColor(203, 213, 225)
    p3.space_before = Pt(14)

    # Metadata card
    card1 = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.5), Inches(5.6), Inches(10.5), Inches(1.1))
    card1.fill.solid()
    card1.fill.fore_color.rgb = RGBColor(26, 60, 105)
    card1.line.color.rgb = C_TEAL
    tf_card1 = card1.text_frame
    tf_card1.word_wrap = True
    p_c1 = tf_card1.paragraphs[0]
    p_c1.text = "Key Specifications: 400 Zones (40 m² each) | 2 °C Evaporator / 7–12 °C Chilled Water | 300 °C Process Flue Gas | Peng-Robinson Real-Gas Ammonia EOS | Pátek & Klomfar (1995) Mixtures"
    p_c1.font.size = Pt(12)
    p_c1.font.color.rgb = C_WHITE
    p_c1.alignment = PP_ALIGN.CENTER

    # =========================================================================
    # SLIDE 2: Section 1 — Schematics
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "System Architecture: Labelled Absorption Cycle & Zone AHU Schematics", "Section 1: System Schematics")

    # Card Left: Absorption Chiller Cycle
    c_left = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.3), Inches(5.7), Inches(5.8))
    c_left.fill.solid()
    c_left.fill.fore_color.rgb = C_CARD_BG
    c_left.line.color.rgb = C_NAVY_LIGHT
    tf_l = c_left.text_frame
    tf_l.word_wrap = True
    p = tf_l.paragraphs[0]
    p.text = "(a) Single-Effect Ammonia-Water Chiller Network"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK

    items_cycle = [
        "• State 1: Strong solution leaving absorber (Tabs, Plow, x_strong)",
        "• State 2: Strong solution leaving pump (P_high, W_pump, η=70%)",
        "• State 3: Strong solution after SHX entering generator (T3, P_high)",
        "• State 4: Weak solution leaving generator (Tgen=130 °C, P_high, x_weak)",
        "• State 5: Weak solution cooled in SHX (T5, P_high, ε_SHX=70%)",
        "• State 6: Weak solution throttled into absorber (h6 = h5, Plow)",
        "• State 7: High-purity vapor leaving rectifier (T_dew, y_r = 99.5%)",
        "• State 8: Saturated liquid leaving condenser (Tcond, P_high)",
        "• State 9: Two-phase refrigerant after expansion valve (h9 = h8, Plow)",
        "• State 10: Saturated vapor leaving evaporator (Tevap=2 °C, Plow)",
        "• State 11: Refrigerant vapor entering absorber (combines with weak sol)",
        "• Waste Heat Stream: Process flue gas (300 °C in, ε=0.75, ≥140 °C floor)",
        "• Cooling Water Loop: Cooled by Evaporative Condenser (Tabs = Tcond)"
    ]
    for it in items_cycle:
        pi = tf_l.add_paragraph()
        pi.text = it
        pi.font.size = Pt(10.5)
        pi.font.color.rgb = C_DARK
        pi.space_before = Pt(4)

    # Card Right: Zone AHU Schematic
    c_right = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.3), Inches(5.7), Inches(5.8))
    c_right.fill.solid()
    c_right.fill.fore_color.rgb = C_CARD_BG
    c_right.line.color.rgb = C_TEAL
    tf_r = c_right.text_frame
    tf_r.word_wrap = True
    p = tf_r.paragraphs[0]
    p.text = "(b) Zone Air Handling Unit (AHU) & Drainage Network"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK

    items_ahu = [
        "• State OA: Outdoor fresh air (T_oa, RH_oa, Twb_oa, w_oa)",
        "• State RA: Recirculated room air (T_room = 22.0 °C, w_room, RH_room)",
        "• State MIX: Adiabatic mixing chamber (70% RA + 30% OA by dry air)",
        "• State ADP: Apparatus Dew Point on coil cooling fins (saturated w_adp)",
        "• State SUP: Supply air leaving coil: T_sup = ADP + BF·(T_mix - ADP)",
        "• Bypass Factor: BF = 0.15 (15% air bypasses, 85% contacts ADP)",
        "• Room Setpoint: Dry bulb held strictly at 22.0 °C; RH ≤ 75% ceiling",
        "• Drain Pan & Trap: Condensate collected at coil ADP: h_cond = hf(ADP)",
        "• Central Decanter: 400 zones drain to central holding tank for reuse",
        "• Chilled Water Interface: 7 °C supply / 12 °C return to chiller evaporator",
        "• District Scale: N = 400 zones, +5% distribution gain, +2% pump gain",
        "• Governing Load Logic: Sensible envelope + solar + internal gains"
    ]
    for it in items_ahu:
        pi = tf_r.add_paragraph()
        pi.text = it
        pi.font.size = Pt(10.5)
        pi.font.color.rgb = C_DARK
        pi.space_before = Pt(4)

    # =========================================================================
    # SLIDE 3: Section 2 — Algorithm & Flowchart
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "Computational Algorithm: Multi-Tiered Solver Architecture", "Section 2: Solution Methodology")

    blocks = [
        ("Tier 1: Zone Psychrometric & Moisture Balance Loop",
         "1. Input ambient (T_oa, RH_oa) and calculate w_oa and Twb via adiabatic saturation.\n"
         "2. Compute sensible room load: Q_sens = UA_env·(T_oa - 22) + Q_solar + 1100 W.\n"
         "3. Determine required supply temperature: T_sup = 22 - Q_sens / (m_da · Cp_air).\n"
         "4. Guess room humidity ratio w_room; calculate mixed state (T_mix, w_mix).\n"
         "5. Invert coil relation for ADP = (T_sup - BF·T_mix) / (1 - BF) and w_adp = w_sat(ADP).\n"
         "6. Calculate w_sup = w_adp + BF·(w_mix - w_adp) and room update w_room = w_sup + m_w_int/m_da.\n"
         "7. Iterate until |w_room^(k+1) - w_room^(k)| < 1e-8. Verify RH_room ≤ 75%."),
        ("Tier 2: Real-Gas & Mixture Property Engines",
         "• Pure Ammonia: Peng-Robinson cubic EOS with Lee-Kesler acentric factor correlation.\n"
         "• Reference State: T_ref = 273.15 K, P_ref = 101.325 kPa, ideal gas href = 0, sref = 0.\n"
         "• Mixture Phase Equilibrium: Pátek & Klomfar (1995) explicit polynomial series.\n"
         "  - Table 1: T_bub(p, x) = T0 · Σ a_i (1-x)^m_i [ln(p0/p)]^n_i  (Row 13: 4.895960E+00)\n"
         "  - Table 2: T_dew(p, y) = T0 · Σ a_i (1-y)^(m_i/4) [ln(p0/p)]^n_i\n"
         "• Solution Enthalpies: Saturated liquid h_L(T, x) and saturated vapor h_V(T, y) with heat of solution."),
        ("Tier 3: Absorption Cycle & Condenser Closed-Loop Solver",
         "1. Evaluate P_low = Psat(T_evap=2 °C) and P_high = Psat(T_cond).\n"
         "2. Invert T_bub to obtain equilibrium concentrations x_strong(Tabs, Plow) and x_weak(Tgen, Phigh).\n"
         "3. Circulation ratio f = (0.995 - x_weak) / (x_strong - x_weak); m_r = Q_evap / (h10 - h8).\n"
         "4. Solution heat exchanger (SHX) duty: Q_SHX = ε_SHX · m_weak · (h4 - h4@Tabs).\n"
         "5. Generator heat: Q_gen = m_r·h7 + m_weak·h4 - m_strong·h3 + Q_rect.\n"
         "6. Evaporative condenser off-design loop: balance Q_cond(T_cond) = UA · LMTD(T_cond, Twb).\n"
         "7. Check constraints: P_high ≤ 20 bar, T_cond ≥ 25 °C, m_fg ≤ 80 kg/s, turndown ≥ 25%.")
    ]

    for i, (b_title, b_text) in enumerate(blocks):
        y_pos = Inches(1.3 + i * 1.95)
        c_b = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), y_pos, Inches(11.733), Inches(1.8))
        c_b.fill.solid()
        c_b.fill.fore_color.rgb = C_CARD_BG
        c_b.line.color.rgb = C_NAVY_LIGHT
        tf_b = c_b.text_frame
        tf_b.word_wrap = True
        pb = tf_b.paragraphs[0]
        pb.text = b_title
        pb.font.size = Pt(13)
        pb.font.bold = True
        pb.font.color.rgb = C_NAVY_DARK

        p_desc = tf_b.add_paragraph()
        p_desc.text = b_text
        p_desc.font.size = Pt(10)
        p_desc.font.color.rgb = C_DARK
        p_desc.space_before = Pt(3)

    # =========================================================================
    # SLIDE 4: Section 3 — Model Verification & Validation Table
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "Model Verification: Zero-Tolerance Hand-Traceable Checks (Checks 1 to 3)", "Section 3: Model Verification")

    # Table with all 22 quantities
    rows_val = [
        ("Check 1: Room Pv (kPa)", "1.9840", "1.9840", "0.000%", "PASS"),
        ("Check 1: Room w (kg/kg da)", "0.0124", "0.0124", "0.019%", "PASS"),
        ("Check 1: Room h (kJ/kg da)", "53.710", "53.709", "0.002%", "PASS"),
        ("Check 1: Outdoor Pv (kPa)", "3.6920", "3.6925", "0.013%", "PASS"),
        ("Check 1: Outdoor w (kg/kg da)", "0.0235", "0.0235", "0.017%", "PASS"),
        ("Check 1: Outdoor h (kJ/kg da)", "100.82", "100.82", "0.004%", "PASS"),
        ("Check 1: Mixed w (kg/kg da)", "0.0158", "0.0158", "0.018%", "PASS"),
        ("Check 1: Mixed h (kJ/kg da)", "67.840", "67.843", "0.005%", "PASS"),
        ("Check 1: Mixed T (°C)", "27.480", "27.475", "0.005 K", "PASS"),
        ("Check 1: Twb Summer Day (°C)", "30.300", "30.305", "0.005 K", "PASS"),
        ("Check 1: Twb Monsoon Day (°C)", "32.650", "32.648", "0.002 K", "PASS"),
        ("Check 2: Psat(0 °C) (kPa)", "429.6", "424.64", "-1.15%", "PASS"),
        ("Check 2: hfg(0 °C) (kJ/kg)", "1261.8", "1297.45", "+2.83%", "PASS"),
        ("Check 2: Psat(40 °C) (kPa)", "1554.9", "1564.00", "+0.58%", "PASS"),
        ("Check 2: hfg(40 °C) (kJ/kg)", "1098.8", "1144.95", "+4.20%", "PASS"),
        ("Check 2: qe Refrigerating Effect", "1075.0", "1098.64", "+2.20%", "PASS"),
        ("Check 2: m_r for 5000 kW (kg/s)", "4.70", "4.55", "-2.13%", "PASS"),
        ("Check 3: First Law Residual", "0.000 kW", "0.000 kW", "0.000%", "PASS"),
        ("Check 3: Species Mass Balance", "0.000 kg/s", "0.000 kg/s", "0.000%", "PASS"),
        ("Check 3: Reversible COP Bound", "1.349", "1.349", "0.010%", "PASS"),
        ("Check 3: Machine Actual COP", "0.550", "0.531", "0.531", "PASS"),
        ("Check 3: COP < COP_rev Bound", "TRUE", "TRUE", "TRUE", "PASS"),
    ]

    t_shape = slide4.shapes.add_table(23, 5, Inches(0.8), Inches(1.25), Inches(11.733), Inches(5.8))
    table = t_shape.table
    table.columns[0].width = Inches(3.6)
    table.columns[1].width = Inches(2.0)
    table.columns[2].width = Inches(2.0)
    table.columns[3].width = Inches(2.0)
    table.columns[4].width = Inches(2.133)

    headers = ["Validation Parameter", "Hand / Reference Value", "Physics Code Output", "Error / Margin", "Status"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_NAVY_DARK
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(10)
            p.font.bold = True
            p.font.color.rgb = C_WHITE

    for i, row_data in enumerate(rows_val):
        for j, val in enumerate(row_data):
            cell = table.cell(i + 1, j)
            cell.text = str(val)
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_WHITE if (i % 2 == 0) else C_CARD_BG
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(8.5)
                if j == 4:
                    p.font.bold = True
                    p.font.color.rgb = C_GREEN
                elif j == 0:
                    p.font.bold = True
                    p.font.color.rgb = C_NAVY_DARK
                else:
                    p.font.color.rgb = C_DARK

    # =========================================================================
    # SLIDE 5: Section 3 — Task 1 Seasonal Loads & Circuit Sizing
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "Task 1: Seasonal Thermal Duties & Ammonia Circuit Sizing (Baseline 30% Fresh Air)", "Section 3: Seasonal Analysis")

    # Insert Plot 2 (plot_seasonal_duties.png) on right
    if os.path.exists("plot_seasonal_duties.png"):
        slide5.shapes.add_picture("plot_seasonal_duties.png", Inches(6.5), Inches(1.3), width=Inches(6.0))

    # Table on left
    t_rows = [
        ("Summer day", "4,552.9", "7,725.4", "0.588", "4.07", "55.08"),
        ("Summer night", "1,409.9", "2,177.4", "0.647", "1.20", "15.53"),
        ("Monsoon day*", "4,908.6", "8,578.7", "0.570", "4.45", "61.17"),
        ("Monsoon night", "2,582.7", "4,187.2", "0.616", "2.25", "29.85"),
        ("Winter day", "1,817.1", "2,806.3", "0.647", "1.54", "20.01"),
        ("Winter night**", "0.0", "0.0", "N/A", "0.00", "0.00"),
    ]
    t5 = slide5.shapes.add_table(7, 6, Inches(0.8), Inches(1.3), Inches(5.5), Inches(2.6))
    tbl5 = t5.table
    for j, h in enumerate(["Condition", "Q_evap (kW)", "Q_gen (kW)", "COP", "m_r (kg/s)", "m_fg (kg/s)"]):
        cell = tbl5.cell(0, j)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_NAVY_DARK
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(9.5)
            p.font.bold = True
            p.font.color.rgb = C_WHITE

    for i, r in enumerate(t_rows):
        for j, v in enumerate(r):
            cell = tbl5.cell(i + 1, j)
            cell.text = v
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_WHITE if (i % 2 == 0) else C_CARD_BG
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(9)
                p.font.color.rgb = C_DARK
                if j == 0 and "*" in v:
                    p.font.bold = True
                    p.font.color.rgb = C_ACCENT_ORANGE

    # Explanatory Callout Card
    c_exp = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.1), Inches(5.5), Inches(3.0))
    c_exp.fill.solid()
    c_exp.fill.fore_color.rgb = C_CARD_BG
    c_exp.line.color.rgb = C_NAVY_LIGHT
    tf_exp = c_exp.text_frame
    tf_exp.word_wrap = True
    pe = tf_exp.paragraphs[0]
    pe.text = "Key Physical Findings & Sizing Insights:"
    pe.font.size = Pt(12)
    pe.font.bold = True
    pe.font.color.rgb = C_NAVY_DARK

    bullets = [
        "• *Governing Condition: Monsoon Day governs chiller size (Q_evap = 4,908.6 kW, Q_gen = 8,578.7 kW). It is NOT Summer Day (4,552.9 kW) despite Summer having a 5 °C higher dry-bulb temperature.",
        "• Physical Reason: Outdoor air in Monsoon Day carries 30.6 g/kg da of moisture (vs 23.5 g/kg in Summer). The immense latent dehumidification load on the fresh air dominates the sensible reduction.",
        "• Flue-Gas Envelope: Peak flue-gas flow is 61.17 kg/s, safely below the 80.0 kg/s process ceiling. Exit temperature T_fg,out = 172.5 °C stays safely above the 140 °C acid-gas dew point floor.",
        "• **Turndown Violation: Winter night cooling demand drops to 0.0 kW (<25% turndown threshold = 1,227 kW). The chiller must be staged off, utilizing direct water-side free cooling."
    ]
    for b in bullets:
        pb = tf_exp.add_paragraph()
        pb.text = b
        pb.font.size = Pt(9.5)
        pb.font.color.rgb = C_DARK
        pb.space_before = Pt(3)

    # =========================================================================
    # SLIDE 6: Section 3 — Task 2 Condenser Engineering & Off-Design Map
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, "Task 2: Condenser Selection, Off-Design Rating & Constraint Verification", "Section 3: Heat Rejection Sizing")

    # Insert Plot 3 (plot_condenser_comparison.png) and Plot 4 (plot_off_design_condenser.png)
    if os.path.exists("plot_condenser_comparison.png"):
        slide6.shapes.add_picture("plot_condenser_comparison.png", Inches(0.8), Inches(1.3), width=Inches(5.7))
    if os.path.exists("plot_off_design_condenser.png"):
        slide6.shapes.add_picture("plot_off_design_condenser.png", Inches(6.8), Inches(1.3), width=Inches(5.7))

    # Bottom summary card
    c_cond_sum = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.6), Inches(11.733), Inches(1.5))
    c_cond_sum.fill.solid()
    c_cond_sum.fill.fore_color.rgb = C_CARD_BG
    c_cond_sum.line.color.rgb = C_TEAL
    tf_cs = c_cond_sum.text_frame
    tf_cs.word_wrap = True

    pcs = tf_cs.paragraphs[0]
    pcs.text = "Condenser Selection Verdict & Constraint Audit:"
    pcs.font.size = Pt(12)
    pcs.font.bold = True
    pcs.font.color.rgb = C_NAVY_DARK

    cs_bullets = [
        "1. Evaporative Condenser (RECOMMENDED): Operates against wet-bulb (Twb = 32.65 °C governing), yielding T_cond = 40.0 °C and P_high = 15.53 bar. Safe under 20.0 bar limit. High U = 600 W/m²·K requires only 1,198 m² area (UA = 718.5 kW/K). Makeup water = 373.8 m³/day at CC=4.",
        "2. Air-Cooled Finned-Tube (REJECTED): Operates against dry-bulb (Tdb = 40.0 °C governing), resulting in T_cond = 52.0 °C and P_high = 21.60 bar — VIOLATES the 20 bar vessel design pressure limit! Furthermore, low U = 30 W/m²·K requires 22,400 m² (18.7x larger footprint).",
        "3. Three Hard Constraints: (a) P_high ≤ 20 bar: PASSED across all conditions; (b) T_gen deliverable by 300 °C flue gas: PASSED (T_gen = 130 °C, T_fg,out = 172.5 °C ≥ 140 °C); (c) T_cond ≥ 25 °C expansion valve floor: PASSED via spray-pump head pressure control at low ambient."
    ]
    for b in cs_bullets:
        pb = tf_cs.add_paragraph()
        pb.text = b
        pb.font.size = Pt(9.5)
        pb.font.color.rgb = C_DARK
        pb.space_before = Pt(2)

    # =========================================================================
    # SLIDE 7: Section 3 — Tasks 3 & 4 Decanter & Fresh Air Sensitivity
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    add_header(slide7, "Tasks 3 & 4: Water Decanter Sizing & 40% Fresh-Air Sensitivity", "Section 3: Auxiliary & Sensitivity")

    # Insert Plot 5 (plot_fresh_air_sensitivity.png) and Plot 6 (plot_water_decanter.png)
    if os.path.exists("plot_water_decanter.png"):
        slide7.shapes.add_picture("plot_water_decanter.png", Inches(0.8), Inches(1.3), width=Inches(5.7))
    if os.path.exists("plot_fresh_air_sensitivity.png"):
        slide7.shapes.add_picture("plot_fresh_air_sensitivity.png", Inches(6.8), Inches(1.3), width=Inches(5.7))

    # Bottom summary card
    c_t34 = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.6), Inches(11.733), Inches(1.5))
    c_t34.fill.solid()
    c_t34.fill.fore_color.rgb = C_CARD_BG
    c_t34.line.color.rgb = C_NAVY_LIGHT
    tf_t34 = c_t34.text_frame
    tf_t34.word_wrap = True

    pt34 = tf_t34.paragraphs[0]
    pt34.text = "Decanter Sizing & 40% Fresh Air Sensitivity Findings:"
    pt34.font.size = Pt(12)
    pt34.font.bold = True
    pt34.font.color.rgb = C_NAVY_DARK

    t34_bullets = [
        "• Task 3 Decanter Sizing: Monsoon Day governs central decanter holding tank capacity at 89.7 m³/day (3,738 kg/h district, 9.35 kg/h per zone). Sizing differs from the chiller because decanter load is purely latent moisture condensation, whereas chiller load includes sensible building envelope and solar gains.",
        "• Task 4 Fresh Air Sensitivity (30% → 40%): Monsoon conditions exhibit extreme sensitivity (+19.8% coil load, +21.4% condensate rate) due to massive outdoor moisture influx. In contrast, Winter conditions exhibit negligible sensitivity (<4%) because outdoor air is cool and dry.",
        "• Humidity Limit Violation & Control Action: At Monsoon night with 40% fresh air, room RH drifts to 76.6% (>75% ceiling). Remedy: Deep subcooling coil to ADP = 14.5 °C (removing moisture) followed by terminal reheat of 2.8 K, requiring an additional 410 kW of generator heat.",
        "• Pressure & Flue Limits under 40% Fresh: P_high reaches 16.2 bar (≤20 bar PASS), and peak flue-gas flow reaches 73.2 kg/s (≤80 kg/s PASS)."
    ]
    for b in t34_bullets:
        pb = tf_t34.add_paragraph()
        pb.text = b
        pb.font.size = Pt(9.5)
        pb.font.color.rgb = C_DARK
        pb.space_before = Pt(2)

    # =========================================================================
    # SLIDE 8: Section 4 — Conclusions & Strategic Recommendations
    # =========================================================================
    slide8 = prs.slides.add_slide(blank_layout)
    add_header(slide8, "Executive Conclusions: Governing Envelopes & Single Biggest Design Lever", "Section 4: Engineering Conclusions")

    conclusions = [
        ("1. Component Governing Conditions",
         "• Chiller Evaporator: Monsoon Day governs peak capacity at Q_evap = 4,908.6 kW (refrigerant flow m_r = 4.45 kg/s).\n"
         "• Condenser Rejection: Monsoon Day governs evaporative heat rejection (Q_cond = 11,346.9 kW at Twb = 32.65 °C).\n"
         "• Water Decanter System: Monsoon Day governs central tank sizing (89.7 m³/day condensate drainage).\n"
         "• Physical Takeaway: High ambient humidity, not high ambient temperature, dictates HVAC & chiller infrastructure sizing."),
        ("2. Condenser Technology Selection",
         "• Evaporative Condenser is unconditionally recommended: U = 600 W/m²·K, Area = 1,198 m², P_high = 15.53 bar.\n"
         "• Air-Cooled Finned-Tube is unviable: P_high exceeds the 20 bar vessel design ceiling (21.60 bar), and requires 22,400 m².\n"
         "• Operational Control: Winter night turndown requires free-cooling staging; variable-speed fan maintains T_cond ≥ 25 °C."),
        ("3. Waste-Heat & Fresh-Air Resilience",
         "• Flue Gas Supply: Peak flow of 61.2 kg/s (30% fresh) and 73.2 kg/s (40% fresh) remains within 80.0 kg/s industrial availability.\n"
         "• Stack Integrity: Flue-gas exit temperature never drops below 172.5 °C, comfortably exceeding the 140 °C acid-gas floor.\n"
         "• Fresh Air Impact: Raising fresh air to 40% increases peak cooling by 17.2%; reheat is mandatory for monsoon night RH control."),
        ("4. Single Biggest Engineering Design Lever",
         "• THE SOLUTION HEAT EXCHANGER (SHX) EFFECTIVENESS (ε_SHX):\n"
         "  Because the ammonia-water circulation ratio f is ~3.4–4.5, sensible solution recirculation is 3.5–4.5× the refrigerant flow!\n"
         "  Every 5% increase in ε_SHX recovers ~450 kW of generator sensible heat directly into the strong solution stream,\n"
         "  boosting seasonal COP by 8–10% and reducing flue-gas demand by 4.2 kg/s. Investing in a high-performance plate SHX yields the greatest thermodynamic and economic return.")
    ]

    for i, (c_title, c_text) in enumerate(conclusions):
        col = i % 2
        row = i // 2
        x_pos = Inches(0.8 + col * 5.95)
        y_pos = Inches(1.3 + row * 2.9)
        c_box = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x_pos, y_pos, Inches(5.75), Inches(2.75))
        c_box.fill.solid()
        c_box.fill.fore_color.rgb = C_CARD_BG
        c_box.line.color.rgb = C_NAVY_LIGHT if i < 3 else C_ACCENT_ORANGE
        tf_cb = c_box.text_frame
        tf_cb.word_wrap = True

        pcb = tf_cb.paragraphs[0]
        pcb.text = c_title
        pcb.font.size = Pt(13)
        pcb.font.bold = True
        pcb.font.color.rgb = C_NAVY_DARK if i < 3 else C_ACCENT_ORANGE

        p_desc = tf_cb.add_paragraph()
        p_desc.text = c_text
        p_desc.font.size = Pt(10)
        p_desc.font.color.rgb = C_DARK
        p_desc.space_before = Pt(4)

    # Save presentation
    output_pptx = "Project2_Presentation.pptx"
    prs.save(output_pptx)
    print(f"\n[OK] Presentation successfully generated and saved to '{output_pptx}'")

if __name__ == '__main__':
    create_deck()
