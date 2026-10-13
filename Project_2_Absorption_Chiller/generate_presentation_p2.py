"""
ME3160 Project 2 - Professional Presentation Generator
Waste-Heat-Driven Ammonia-Water Absorption Chiller for a District Cooling Network

Generates Project2_Presentation.pptx strictly complying with Section 2.5:
1. Schematic: (a) Graphical labelled absorption cycle with numbered state points 1-10;
              (b) Graphical labelled zone AHU diagram with numbered psychrometric points
2. Algorithm: Graphical flowchart of 3-tier computational solver loops
3. Analysis: Master validation table, psychrometric chart, seasonal duties,
             condenser comparison, off-design map, and 40% fresh air sensitivity
4. Conclusion: Governing conditions, condenser selection, flue gas envelope,
               and single biggest design lever (SHX)
"""

import os
import pandas as pd
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
        banner = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.05))
        banner.fill.solid()
        banner.fill.fore_color.rgb = C_NAVY_DARK
        banner.line.color.rgb = C_NAVY_DARK

        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.12), Inches(11.5), Inches(0.3))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = C_TEAL

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

    bar1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.2), Inches(1.8), Inches(0.15), Inches(3.6))
    bar1.fill.solid()
    bar1.fill.fore_color.rgb = C_TEAL
    bar1.line.color.rgb = C_TEAL

    tb1 = slide1.shapes.add_textbox(Inches(1.5), Inches(1.8), Inches(10.5), Inches(3.6))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "ME3160 — Power & Refrigeration Systems | Final Project 2"
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
    p3.text = "Comprehensive Thermodynamic Analysis: Zone Psychrometrics → District Cooling Demand → Ammonia Real-Gas EOS → Pátek & Klomfar (1995) Solution Cycle → Industrial Flue-Gas Waste Heat Integration"
    p3.font.size = Pt(14)
    p3.font.color.rgb = RGBColor(203, 213, 225)
    p3.space_before = Pt(14)

    card1 = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.5), Inches(5.6), Inches(10.5), Inches(1.1))
    card1.fill.solid()
    card1.fill.fore_color.rgb = RGBColor(26, 60, 105)
    card1.line.color.rgb = C_TEAL
    tf_card1 = card1.text_frame
    tf_card1.word_wrap = True
    p_c1 = tf_card1.paragraphs[0]
    p_c1.text = "Key Specifications: 1,000 Zones (40 m² each) | 2 °C Evaporator / 7–12 °C Chilled Water | 300 °C Flue Gas | Peng-Robinson Real-Gas Ammonia EOS | Pátek & Klomfar (1995) Binary Thermodynamics"
    p_c1.font.size = Pt(12)
    p_c1.font.color.rgb = C_WHITE
    p_c1.alignment = PP_ALIGN.CENTER

    # =========================================================================
    # SLIDE 2: Section 1 — Labelled System Schematics
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "System Architecture: Labelled Absorption Cycle & Zone AHU Schematics", "Section 1: System Schematics")

    if os.path.exists("schematic_cycle_p2.png"):
        slide2.shapes.add_picture("schematic_cycle_p2.png", Inches(0.8), Inches(1.2), width=Inches(5.7))
    if os.path.exists("schematic_ahu_p2.png"):
        slide2.shapes.add_picture("schematic_ahu_p2.png", Inches(6.8), Inches(1.2), width=Inches(5.7))

    card_s2 = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.1), Inches(11.733), Inches(1.05))
    card_s2.fill.solid()
    card_s2.fill.fore_color.rgb = C_CARD_BG
    card_s2.line.color.rgb = C_TEAL
    tf_s2 = card_s2.text_frame
    tf_s2.word_wrap = True
    p_s2 = tf_s2.paragraphs[0]
    p_s2.text = "Diagrammatic Key & Thermodynamic Interfaces:"
    p_s2.font.size = Pt(11)
    p_s2.font.bold = True
    p_s2.font.color.rgb = C_NAVY_DARK

    p_s2_b = tf_s2.add_paragraph()
    p_s2_b.text = "(a) Cycle: Numbered states 1 to 10 show strong/weak solution circulation, SHX recuperation (ε=0.70), rectifier reflux balance, and industrial flue-gas heating (300 °C in → 155–169 °C out). (b) AHU: Fresh outdoor air (30%) mixes with recirculated room air (70%), dehumidifies on cooling coil fins at ADP, and drains condensate to central decanter."
    p_s2_b.font.size = Pt(9.5)
    p_s2_b.font.color.rgb = C_DARK

    # =========================================================================
    # SLIDE 3: Section 2 — Algorithm & Flowchart
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "Computational Algorithm: Multi-Tiered Solver Architecture & Flowchart", "Section 2: Solution Methodology")

    if os.path.exists("flowchart_algorithm_p2.png"):
        slide3.shapes.add_picture("flowchart_algorithm_p2.png", Inches(0.8), Inches(1.2), width=Inches(7.2))

    c_b_card = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.2), Inches(1.2), Inches(4.333), Inches(5.95))
    c_b_card.fill.solid()
    c_b_card.fill.fore_color.rgb = C_CARD_BG
    c_b_card.line.color.rgb = C_NAVY_LIGHT
    tf_bc = c_b_card.text_frame
    tf_bc.word_wrap = True

    p = tf_bc.paragraphs[0]
    p.text = "Methodological Highlights:"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK

    algo_points = [
        "• Tier 1 Psychrometric Iteration: Rigorous moisture balance solves room humidity ratio w_room and coil ADP simultaneously; accounts for water-vapor condensate enthalpy removal.",
        "• Tier 2 Mixture Physics: Complete implementation of Pátek & Klomfar (1995) Table 1 (bubble point) and Table 2 (dew point), with unified 0 °C ideal-gas enthalpy scale matching Peng-Robinson EOS departures.",
        "• Tier 3 Closed-Loop Cycle: Fixed UA evaporative condenser balances heat rejection against ambient wet-bulb with air-side energy balance. Dynamic generator temperature T_gen tracks condensing pressure.",
        "• Rectifier Reflux Physics: Full mass and species balance on reflux column eliminates artificial fudge factors, yielding rigorous energy closure (<0.0001 kW residual)."
    ]
    for pt in algo_points:
        p_pt = tf_bc.add_paragraph()
        p_pt.text = pt
        p_pt.font.size = Pt(9.5)
        p_pt.font.color.rgb = C_DARK
        p_pt.space_before = Pt(6)

    # =========================================================================
    # SLIDE 4: Section 3 — Validation Table
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "Validation Suite: Automated Assertions Across Checks 1 to 3", "Section 3: Model Verification")

    val_data = [
        ("Check 1: Room Pv (kPa)", "1.984", "1.984", "0.00%", "PASS"),
        ("Check 1: Room w (kg/kg da)", "0.0124", "0.0124", "0.02%", "PASS"),
        ("Check 1: Room h (kJ/kg da)", "53.71", "53.71", "0.00%", "PASS"),
        ("Check 1: Mixed w (kg/kg da)", "0.0158", "0.0158", "0.02%", "PASS"),
        ("Check 1: Mixed h (kJ/kg da)", "67.84", "67.84", "0.01%", "PASS"),
        ("Check 1: Mixed T (°C)", "27.48", "27.48", "0.005 K", "PASS"),
        ("Check 1: Twb Summer Day (°C)", "30.30", "30.30", "0.005 K", "PASS"),
        ("Check 1: Twb Monsoon Day (°C)", "32.65", "32.65", "0.002 K", "PASS"),
        ("Check 2: Psat(0 °C) (kPa)", "429.6", "424.64", "-1.15%", "PASS"),
        ("Check 2: hfg(0 °C) (kJ/kg)", "1261.8", "1297.45", "+2.83%", "PASS"),
        ("Check 2: Psat(40 °C) (kPa)", "1554.9", "1564.00", "+0.58%", "PASS"),
        ("Check 2: hfg(40 °C) (kJ/kg)", "1098.8", "1144.95", "+4.20%", "PASS"),
        ("Check 2: qe Refrig Effect (kJ/kg)", "1075.0", "1098.64", "+2.20%", "PASS"),
        ("Check 2: m_r for 5000 kW (kg/s)", "4.70", "4.55", "-2.13%", "PASS"),
        ("Check 3: First Law Residual (kW)", "0.000", "0.000", "0.00000", "PASS"),
        ("Check 3: Species Mass Balance (kg/s)", "0.000", "0.000", "0.00000", "PASS"),
        ("Check 3: Carnot COP Bound", "1.349", "1.349", "0.01%", "PASS"),
        ("Check 3: Actual COP (0.45–0.65)", "0.550", "0.567", "0.567", "PASS"),
    ]

    t_box = slide4.shapes.add_table(len(val_data) + 1, 5, Inches(0.8), Inches(1.2), Inches(11.733), Inches(5.8))
    table = t_box.table
    table.columns[0].width = Inches(4.2)
    table.columns[1].width = Inches(1.8)
    table.columns[2].width = Inches(1.8)
    table.columns[3].width = Inches(2.0)
    table.columns[4].width = Inches(1.9)

    headers = ["Quantity / Verification Parameter", "Hand / Target", "Code Output", "Difference / Tolerance", "Status"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_NAVY_DARK
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(9.5)
            p.font.bold = True
            p.font.color.rgb = C_WHITE

    for i, row_data in enumerate(val_data):
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
    # SLIDE 5: Section 3 — Task 1 Seasonal Loads & Psychrometrics
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "Task 1: Seasonal Thermal Duties & Psychrometric State Trajectories", "Section 3: Seasonal Analysis")

    if os.path.exists("plot_psychrometric_chart.png"):
        slide5.shapes.add_picture("plot_psychrometric_chart.png", Inches(0.8), Inches(1.2), width=Inches(5.7))
    if os.path.exists("plot_seasonal_duties.png"):
        slide5.shapes.add_picture("plot_seasonal_duties.png", Inches(6.8), Inches(1.2), width=Inches(5.7))

    card_s5 = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.6), Inches(11.733), Inches(1.5))
    card_s5.fill.solid()
    card_s5.fill.fore_color.rgb = C_CARD_BG
    card_s5.line.color.rgb = C_NAVY_LIGHT
    tf_s5 = card_s5.text_frame
    tf_s5.word_wrap = True

    p = tf_s5.paragraphs[0]
    p.text = "Key Seasonal Thermodynamics Insights:"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK

    s5_bullets = [
        "• Governing Peak: Monsoon Day dictates peak district chiller capacity (Q_evap = 4,908.6 kW, Q_gen = 8,193.3 kW, m_r = 4.46 kg/s). It dominates over Summer Day (4,552.9 kW) because moisture ratio w_oa = 30.6 g/kg da requires massive latent dehumidification.",
        "• Latent vs Sensible: Latent load represents >50% of the total cooling duty at Monsoon Day, proving that moisture management governs commercial HVAC infrastructure in hot-humid climates.",
        "• Turndown & Free Cooling: Winter Night load drops to 0.0 kW (<25% turndown threshold = 1,227.1 kW). The absorption chiller is shut down, engaging direct waterside free cooling to eliminate boiler and pump energy consumption.",
        "• Flue-Gas Envelope: Peak flue-gas demand is 56.76 kg/s (safely below 80.0 kg/s limit). Stack exit temperature is 154.5–168.8 °C (well above 140 °C acid-gas dew point floor)."
    ]
    for b in s5_bullets:
        pb = tf_s5.add_paragraph()
        pb.text = b
        pb.font.size = Pt(9.0)
        pb.font.color.rgb = C_DARK
        pb.space_before = Pt(2)

    # =========================================================================
    # SLIDE 6: Section 3 — Task 2 Condenser Engineering & Off-Design Map
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, "Task 2: Condenser Selection, Off-Design Rating & Constraint Verification", "Section 3: Heat Rejection Sizing")

    if os.path.exists("plot_condenser_comparison.png"):
        slide6.shapes.add_picture("plot_condenser_comparison.png", Inches(0.8), Inches(1.2), width=Inches(5.7))
    if os.path.exists("plot_off_design_condenser.png"):
        slide6.shapes.add_picture("plot_off_design_condenser.png", Inches(6.8), Inches(1.2), width=Inches(5.7))

    card_s6 = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.6), Inches(11.733), Inches(1.5))
    card_s6.fill.solid()
    card_s6.fill.fore_color.rgb = C_CARD_BG
    card_s6.line.color.rgb = C_TEAL
    tf_s6 = card_s6.text_frame
    tf_s6.word_wrap = True

    p = tf_s6.paragraphs[0]
    p.text = "Condenser Selection Verdict & Constraint Audit:"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK

    cs_bullets = [
        "1. Evaporative Condenser (RECOMMENDED): Approaches wet-bulb (Twb = 32.65 °C governing), yielding T_cond = 40.0 °C and P_high = 15.64 bar. Safe under 20.0 bar vessel limit. High U = 600 W/m²·K requires 2,422 m² area (UA = 1,453.4 kW/K). Makeup water = 247.0 m³/day at CC=4.",
        "2. Air-Cooled Finned-Tube (REJECTED): Approaches dry-bulb (Tdb = 40.0 °C governing), resulting in T_cond = 52.0 °C and P_high = 21.54 bar — VIOLATES the 20 bar vessel design pressure limit! Furthermore, low U = 30 W/m²·K requires 28,604 m² (11.8x larger footprint).",
        "3. Three Hard Constraints: (a) P_high ≤ 20 bar: PASSED across all conditions; (b) T_gen deliverable by 300 °C flue gas: PASSED (T_gen = 125.0 °C, T_fg,out = 168.8 °C ≥ 140 °C); (c) T_cond ≥ 25 °C expansion valve floor: PASSED via spray-pump head pressure control at low ambient."
    ]
    for b in cs_bullets:
        pb = tf_s6.add_paragraph()
        pb.text = b
        pb.font.size = Pt(9.0)
        pb.font.color.rgb = C_DARK
        pb.space_before = Pt(2)

    # =========================================================================
    # SLIDE 7: Section 3 — Tasks 3 & 4 Decanter & Fresh Air Sensitivity
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    add_header(slide7, "Tasks 3 & 4: Water Decanter Sizing & 40% Fresh-Air Sensitivity", "Section 3: Auxiliary & Sensitivity")

    if os.path.exists("plot_water_decanter.png"):
        slide7.shapes.add_picture("plot_water_decanter.png", Inches(0.8), Inches(1.2), width=Inches(5.7))
    if os.path.exists("plot_fresh_air_sensitivity.png"):
        slide7.shapes.add_picture("plot_fresh_air_sensitivity.png", Inches(6.8), Inches(1.2), width=Inches(5.7))

    card_s7 = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.6), Inches(11.733), Inches(1.5))
    card_s7.fill.solid()
    card_s7.fill.fore_color.rgb = C_CARD_BG
    card_s7.line.color.rgb = C_NAVY_LIGHT
    tf_s7 = card_s7.text_frame
    tf_s7.word_wrap = True

    p = tf_s7.paragraphs[0]
    p.text = "Decanter Sizing & 40% Fresh Air Sensitivity Findings:"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK

    t34_bullets = [
        "• Task 3 Decanter Sizing: Monsoon Day governs central decanter holding capacity at 89.7 m³/day (3,738 kg/h district, 9.35 kg/h per zone). Sizing differs from the chiller because decanter load is purely latent moisture condensation, whereas chiller load includes sensible envelope and solar gains.",
        "• Task 4 Fresh Air Sensitivity (30% → 40%): Monsoon conditions exhibit extreme sensitivity (+22.2% coil load, +30.8% condensate rate) due to massive outdoor moisture influx. In contrast, Winter conditions exhibit negligible sensitivity (<4%) because outdoor air is cool and dry.",
        "• Humidity Limit Violation & Dynamic Reheat: At Monsoon night with 40% fresh air, room RH drifts to 76.6% (>75% ceiling). Remedy: Deep subcooling coil to ADP = 15.16 °C followed by terminal reheat of ΔT = 1.19 K (1.80 kW/zone), adding 1,929.0 kW district cooling and 2,998.8 kW extra generator heat.",
        "• Pressure & Flue Limits under 40% Fresh: P_high reaches 16.2 bar (≤20 bar PASS), and peak flue-gas flow reaches 71.4 kg/s (≤80 kg/s PASS)."
    ]
    for b in t34_bullets:
        pb = tf_s7.add_paragraph()
        pb.text = b
        pb.font.size = Pt(9.0)
        pb.font.color.rgb = C_DARK
        pb.space_before = Pt(2)

    # =========================================================================
    # SLIDE 8: Section 4 — Conclusions & Strategic Recommendations
    # =========================================================================
    slide8 = prs.slides.add_slide(blank_layout)
    add_header(slide8, "Executive Conclusions: Governing Envelopes & Single Biggest Design Lever", "Section 4: Engineering Conclusions")

    conclusions = [
        ("1. Component Governing Conditions",
         "• Chiller Evaporator: Monsoon Day governs peak capacity at Q_evap = 4,908.6 kW (refrigerant flow m_r = 4.46 kg/s).\n"
         "• Condenser Rejection: Monsoon Day governs evaporative heat rejection (Q_cond = 5,146.0 kW at Twb = 32.65 °C).\n"
         "• Water Decanter System: Monsoon Day governs central tank sizing (89.7 m³/day condensate drainage).\n"
         "• Physical Takeaway: High ambient humidity, not high ambient temperature, dictates HVAC & chiller infrastructure sizing."),
        ("2. Condenser Technology Selection",
         "• Evaporative Condenser is unconditionally recommended: U = 600 W/m²·K, Area = 2,422 m², P_high = 15.64 bar.\n"
         "• Air-Cooled Finned-Tube is unviable: P_high exceeds the 20 bar vessel design ceiling (21.54 bar), and requires 28,604 m².\n"
         "• Operational Control: Winter night turndown requires free-cooling staging; variable-speed fan maintains T_cond ≥ 25 °C."),
        ("3. Waste-Heat & Fresh-Air Resilience",
         "• Flue Gas Supply: Peak flow of 56.8 kg/s (30% fresh) and 71.4 kg/s (40% fresh) remains within 80.0 kg/s industrial availability.\n"
         "• Stack Integrity: Flue-gas exit temperature never drops below 154.5 °C, comfortably exceeding the 140 °C acid-gas floor.\n"
         "• Fresh Air Impact: Raising fresh air to 40% increases peak cooling by 22.2%; terminal reheat of 1.19 K is mandatory for monsoon night RH control."),
        ("4. Single Biggest Engineering Design Lever",
         "• THE SOLUTION HEAT EXCHANGER (SHX) EFFECTIVENESS (ε_SHX):\n"
         "  Because the ammonia-water circulation ratio f is ~3.7, sensible solution recirculation is 3.7× the refrigerant flow!\n"
         "  Eliminating the SHX increases generator heat demand by 3,460.5 kW (+42%), collapsing COP from 0.597 down to 0.442.\n"
         "  Increasing ε_SHX from 0.70 to 0.80 saves an additional 494.4 kW of generator heat. Investing in a high-effectiveness plate SHX yields the single highest thermodynamic and financial return in the plant.")
    ]

    for i, (c_title, c_text) in enumerate(conclusions):
        col = i % 2
        row = i // 2
        x_pos = Inches(0.8 + col * 5.95)
        y_pos = Inches(1.2 + row * 2.9)
        c_box = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x_pos, y_pos, Inches(5.75), Inches(2.75))
        c_box.fill.solid()
        c_box.fill.fore_color.rgb = C_CARD_BG
        c_box.line.color.rgb = C_NAVY_LIGHT if i < 3 else C_ACCENT_ORANGE
        tf_cb = c_box.text_frame
        tf_cb.word_wrap = True

        pcb = tf_cb.paragraphs[0]
        pcb.text = c_title
        pcb.font.size = Pt(12)
        pcb.font.bold = True
        pcb.font.color.rgb = C_NAVY_DARK if i < 3 else C_ACCENT_ORANGE

        p_desc = tf_cb.add_paragraph()
        p_desc.text = c_text
        p_desc.font.size = Pt(9.5)
        p_desc.font.color.rgb = C_DARK
        p_desc.space_before = Pt(3)

    output_pptx = "Project2_Presentation.pptx"
    prs.save(output_pptx)
    print(f"\n[OK] Presentation successfully generated and saved to '{output_pptx}'")

if __name__ == '__main__':
    create_deck()
