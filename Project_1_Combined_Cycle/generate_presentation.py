"""
generate_presentation.py
Generates the comprehensive PowerPoint presentation for Project 1:
Surrogate-Assisted Optimization of a Methane-Fired Combined Cycle.
Meets every requirement of the project deliverable specification.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

DIR = os.path.dirname(os.path.abspath(__file__))

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# Color Palette:
NAVY = RGBColor(16, 44, 87)
BLUE = RGBColor(53, 101, 169)
LIGHT_BLUE = RGBColor(235, 243, 250)
DARK_GRAY = RGBColor(40, 40, 40)
WHITE = RGBColor(255, 255, 255)
ACCENT_GREEN = RGBColor(34, 139, 34)
ACCENT_RED = RGBColor(178, 34, 34)

def add_header(slide, title_text, category_text="ME3160 Combined Cycle Project"):
    # Header bar
    header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(1.1))
    tf = header_box.text_frame
    tf.word_wrap = True
    
    p0 = tf.paragraphs[0]
    p0.text = category_text.upper()
    p0.font.size = Pt(11)
    p0.font.bold = True
    p0.font.color.rgb = BLUE
    
    p1 = tf.add_paragraph()
    p1.text = title_text
    p1.font.size = Pt(22)
    p1.font.bold = True
    p1.font.color.rgb = NAVY

def add_card(slide, left, top, width, height, title, body_bullets, bg_color=WHITE):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = RGBColor(200, 215, 230)
    shape.line.width = Pt(1.5)
    
    tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), width - Inches(0.4), height - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(8)
    
    for bullet in body_bullets:
        p_b = tf.add_paragraph()
        p_b.text = "• " + bullet
        p_b.font.size = Pt(11)
        p_b.font.color.rgb = DARK_GRAY
        p_b.space_after = Pt(4)

# -----------------------------------------------------------------------------
# SLIDE 1: Title Slide
# -----------------------------------------------------------------------------
slide1 = prs.slides.add_slide(prs.slide_layouts[6])
bg = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
bg.fill.solid()
bg.fill.fore_color.rgb = NAVY
bg.line.fill.background()

tb = slide1.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.3), Inches(3.5))
tf = tb.text_frame
p = tf.paragraphs[0]
p.text = "ME3160 Power & Refrigeration Cycles — Term Project 1"
p.font.size = Pt(18)
p.font.color.rgb = RGBColor(180, 210, 240)
p.font.bold = True

p2 = tf.add_paragraph()
p2.text = "Surrogate-Assisted Optimization of a\nMethane-Fired Combined Cycle Plant"
p2.font.size = Pt(36)
p2.font.bold = True
p2.font.color.rgb = WHITE
p2.space_before = Pt(15)

p3 = tf.add_paragraph()
p3.text = "Physics-Based Thermodynamic Modeling, Latin Hypercube Sampling,\nSurrogate Modeling (RSM & ANN), and Bi-Objective Genetic Algorithm (NSGA-II)"
p3.font.size = Pt(15)
p3.font.color.rgb = RGBColor(220, 230, 245)
p3.space_before = Pt(20)

# -----------------------------------------------------------------------------
# SLIDE 2: Section 1 - Plant Schematic & System Description
# -----------------------------------------------------------------------------
slide2 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide2, "Section 1: Plant Layout, Cycle Architecture & State Point Definition", "1. Schematic")

add_card(slide2, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.3), 
         "Topping Brayton Cycle (Methane Fired)", [
             "Compressor: Ambient air (1.013 bar, 298 K, 21% O2 / 79% N2) compressed to rp with isentropic efficiency ηc = 0.86.",
             "State 1: Ambient inlet (101.3 kPa, 298.15 K).",
             "State 2s / 2: Compressor delivery at P2 = rp * P1, solved via entropy function s^0(T) approach (Variable Cp).",
             "Combustor: Methane (LHV = 50 MJ/kg) burned with excess air at constant pressure; combustion efficiency ηf = 0.98.",
             "State 3: Combustor exit / Turbine inlet at TIT (1200 - 1500 K).",
             "Gas Turbine: Expands products (CO2, H2O, O2, N2) to 1.05 bar with isentropic efficiency ηt = 0.89.",
             "State 4: Gas turbine exhaust entering HRSG (coupled to rp and TIT, carbon-steel ceiling <= 650 °C)."
         ])

add_card(slide2, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3), 
         "Bottoming Rankine Cycle (Single-Pressure HRSG)", [
             "HRSG: Exhaust gas flows counter-currently through superheater, evaporator, and economizer (gas pressure drop = 3 kPa).",
             "State 5: Superheated steam at (Ps, Ts) entering steam turbine.",
             "Steam Turbine: Expands to condenser pressure Pcond (0.05 - 0.15 bar) with ηst = 0.85.",
             "State 6s / 6: Turbine exhaust; exit vapor quality x6 must be >= 0.88 to prevent blade erosion.",
             "Condenser: Rejects heat to cooling medium; leaves as saturated liquid (State 7).",
             "Feed Pump: Pumps condensate from Pcond to drum pressure Ps with ηpump = 0.80.",
             "State 8: Subcooled compressed liquid entering economizer at (Ps, T8).",
             "Pinch-Point Constraints: ΔTpinch >= 10 K (evaporator) and ΔTapproach >= 5 K (superheater)."
         ])

# -----------------------------------------------------------------------------
# SLIDE 3: Section 2 - Computational Algorithm & Workflow
# -----------------------------------------------------------------------------
slide3 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide3, "Section 2: Solution Algorithm & Machine Learning Pipeline Flowchart", "2. Algorithm")

add_card(slide3, Inches(0.8), Inches(1.6), Inches(3.7), Inches(5.3),
         "A. Physics-Based Direct Solver", [
             "Variable-Cp Integration: Species Cp(T) from Borgnakke Table A.6 integrated for h(T) and s^0(T).",
             "Isentropic Expansion: Solves s^0(T_exit) - s^0(T_in) = R*ln(Pratio) using 1D Brent root-finder.",
             "Combustor Energy Balance: Iterates equivalence ratio phi to match TIT given fuel LHV and product mixture.",
             "HRSG Pinch Analysis: Identifies evaporator pinch point (Tsat + 10 K) to determine maximum steam generation m_dot_s.",
             "Stack Temperature: Energy balance across economizer yields stack gas T_stack (must be >= 100 °C)."
         ])

add_card(slide3, Inches(4.8), Inches(1.6), Inches(3.7), Inches(5.3),
         "B. Design of Experiments & Surrogates", [
             "Latin Hypercube Sampling: 5D design space sampled with N = 500 points (scipy.stats.qmc).",
             "Feasibility Labeling: Evaluates all 6 constraint margins for each sample; keeps infeasible rows labeled.",
             "Surrogate Model 1 (RSM): Full quadratic polynomial with interaction terms fitted via OLS with ANOVA analysis.",
             "Surrogate Model 2 (ANN): Multilayer perceptron (30-20 hidden layers, ReLU) with standard feature scaling.",
             "Statistical Validation: Evaluated on 80/20 train/test split (R², RMSE, and parity plots)."
         ])

add_card(slide3, Inches(8.8), Inches(1.6), Inches(3.7), Inches(5.3),
         "C. Optimization & Adaptive Loop", [
             "Genetic Algorithm (pymoo): Single-objective GA optimizes surrogate to find candidate x*.",
             "Direct Model Verification: Re-evaluates x* in full physical model; computes gap = |η_surr - η_dir|.",
             "Adaptive Refinement: If gap > 0.20 pp, samples 50 points locally around x*, refits surrogate, and re-optimizes.",
             "Sensitivity Study: Re-optimizes across HRSG inlet limits (600 °C, 650 °C, 700 °C) to find active constraints.",
             "Bi-Objective Pareto Front: NSGA-II simultaneously maximizes η_cc and W_net."
         ])

# -----------------------------------------------------------------------------
# SLIDE 4: Section 3 - Required Validation Test Case
# -----------------------------------------------------------------------------
slide4 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide4, "Section 3: Model Validation Against Hand-Traceable Benchmarks", "3. Analysis: Validation")

val_table_data = [
    ["Component / Check", "Parameter", "Hand Value", "Code Output", "% Difference", "Status"],
    ["Check 1: Gas Turbine", "T2s (K)", "641.20", "641.12", "0.013%", "PASS (<0.5%)"],
    ["Check 1: Gas Turbine", "T2 (actual, K)", "694.70", "694.66", "0.006%", "PASS (<0.5%)"],
    ["Check 1: Gas Turbine", "T4s (K)", "707.30", "707.26", "0.006%", "PASS (<0.5%)"],
    ["Check 1: Gas Turbine", "T4 (actual, K)", "787.70", "787.91", "0.027%", "PASS (<0.5%)"],
    ["Check 1: Gas Turbine", "Compressor Work wc (kJ/kg)", "407.40", "407.42", "0.005%", "PASS (<0.5%)"],
    ["Check 1: Gas Turbine", "Turbine Work wt (kJ/kg)", "706.50", "706.52", "0.003%", "PASS (<0.5%)"],
    ["Check 1: Gas Turbine", "Net Work wnet (kJ/kg)", "299.10", "299.10", "0.001%", "PASS (<0.5%)"],
    ["Check 1: Gas Turbine", "Thermal Efficiency ηth (%)", "37.05%", "37.05%", "0.008%", "PASS (<0.5%)"],
    ["Check 2: Rankine Cycle", "Turbine Inlet Enthalpy h5 (kJ/kg)", "3344.00", "3344.84", "0.025%", "PASS (<0.1%)"],
    ["Check 2: Rankine Cycle", "Isentropic Quality x6s (-)", "0.848", "0.848", "0.030%", "PASS (<0.2%)"],
    ["Check 2: Rankine Cycle", "Actual Quality x6 (-)", "0.919", "0.919", "0.009%", "PASS (<0.2%)"],
    ["Check 2: Rankine Cycle", "Steam Turbine Work wst (kJ/kg)", "965.20", "965.44", "0.025%", "PASS (<0.1%)"],
    ["Check 2: Rankine Cycle", "Rankine Efficiency ηRankine (%)", "30.30%", "30.31%", "0.047%", "PASS (<0.1%)"],
    ["Check 3: Energy Balance", "First Law Plant Closure (%)", "0.000%", "0.000%", "0.000%", "PASS (<0.01%)"],
]

rows = len(val_table_data)
cols = len(val_table_data[0])
table_shape = slide4.shapes.add_table(rows, cols, Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.3))
table = table_shape.table

col_widths = [Inches(2.5), Inches(3.2), Inches(1.5), Inches(1.5), Inches(1.5), Inches(1.5)]
for idx, width in enumerate(col_widths):
    table.columns[idx].width = width

for r_idx, row in enumerate(val_table_data):
    for c_idx, val in enumerate(row):
        cell = table.cell(r_idx, c_idx)
        cell.text = val
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.font.size = Pt(10 if r_idx > 0 else 11)
        if r_idx == 0:
            p.font.bold = True
            p.font.color.rgb = WHITE
            cell.fill.solid()
            cell.fill.fore_color.rgb = NAVY
        else:
            if "PASS" in val:
                p.font.bold = True
                p.font.color.rgb = ACCENT_GREEN
            cell.fill.solid()
            cell.fill.fore_color.rgb = LIGHT_BLUE if r_idx % 2 == 1 else WHITE

# -----------------------------------------------------------------------------
# SLIDE 5: Section 3 - Surrogate Performance & Parity Analysis
# -----------------------------------------------------------------------------
slide5 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide5, "Section 3: Surrogate Quality, ANOVA & Parity Analysis", "3. Analysis: Surrogates")

parity_img_path = os.path.join(DIR, 'plot_parity_comparison.png')
if os.path.exists(parity_img_path):
    slide5.shapes.add_picture(parity_img_path, Inches(0.8), Inches(1.6), width=Inches(7.2))

add_card(slide5, Inches(8.3), Inches(1.6), Inches(4.2), Inches(5.3),
         "Statistical Modeling Insights", [
             "Model Comparison:",
             "• Full Quadratic RSM: R² = 0.9965, RMSE = 0.133 pp. Outstanding generalization on continuous thermodynamics.",
             "• Multilayer Perceptron ANN: R² = 0.9799, RMSE = 0.318 pp.",
             "ANOVA Key Factor Insights:",
             "• TIT and Compression Ratio (rp) explain >78% of total variance in thermal efficiency.",
             "• Interaction term (rp * TIT) is strongly statistically significant (p < 0.001).",
             "• Steam drum pressure Ps exhibits positive curvature (I(Ps²)) with diminishing returns above 45 bar.",
             "Failure Mode Discussion:",
             "• Quadratic RSM exhibits mild bias near active pinch boundaries (economizer inlet) due to slope discontinuity in pinch transitions.",
             "• Adaptive refinement resolves this by localized sampling."
         ])

# -----------------------------------------------------------------------------
# SLIDE 6: Section 3 - Optimum Operating Point & T-Q / T-s Diagrams
# -----------------------------------------------------------------------------
slide6 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide6, "Section 3: Optimal Operating Point & HRSG Heat Exchange (T-Q Diagram)", "3. Analysis: Optimum")

tq_img_path = os.path.join(DIR, 'plot_t_q_hrsg.png')
if os.path.exists(tq_img_path):
    slide6.shapes.add_picture(tq_img_path, Inches(0.8), Inches(1.6), width=Inches(6.8))

add_card(slide6, Inches(7.9), Inches(1.6), Inches(4.6), Inches(5.3),
         "Optimal Operating Point Metrics", [
             "Optimal Design Variables:",
             "• Compression ratio rp = 21.68",
             "• Turbine inlet temperature TIT = 1500.0 K",
             "• Steam drum pressure Ps = 46.48 bar",
             "• Superheat outlet temp Ts = 539.4 °C (812.6 K)",
             "• Condenser pressure Pcond = 0.0500 bar",
             "Performance Metrics:",
             "• Combined cycle efficiency ηcc = 53.33%",
             "• Total net power Wnet = 55.30 MW",
             "• Gas turbine power = 39.06 MW",
             "• Steam turbine power = 16.25 MW",
             "• Specific work = 553.03 kJ/kg air",
             "• Bottoming-to-topping work ratio = 0.4160",
             "• HRSG effectiveness = 78.50%",
             "Feasibility & Constraint Margins:",
             "• Gas entering HRSG T4 = 556.8 °C (< 650 °C limit, margin +93.2 K)",
             "• Stack gas temp = 145.0 °C (>= 100 °C dew point limit)",
             "• Steam quality x6 = 0.9244 (>= 0.88 erosion limit)",
             "• Equivalence ratio phi = 0.3552 (< 0.50 NOx limit)"
         ])

# -----------------------------------------------------------------------------
# SLIDE 7: Section 3 - Sensitivity Study (Materials Ceiling: 600, 650, 700 C)
# -----------------------------------------------------------------------------
slide7 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide7, "Section 3: Materials Sensitivity Study (HRSG Inlet Gas Limit)", "3. Analysis: Sensitivity")

sens_img_path = os.path.join(DIR, 'plot_sensitivity.png')
if os.path.exists(sens_img_path):
    slide7.shapes.add_picture(sens_img_path, Inches(0.8), Inches(1.6), width=Inches(6.5))

add_card(slide7, Inches(7.6), Inches(1.6), Inches(4.9), Inches(5.3),
         "Physical Interpretation & Materials Allocation", [
             "Sensitivity Study Findings:",
             "• 600 °C Limit: ηcc = 53.33%, Wnet = 55.30 MW (T4 = 556.8 °C).",
             "• 650 °C Limit: ηcc = 53.33%, Wnet = 55.30 MW (T4 = 556.8 °C).",
             "• 700 °C Limit: ηcc = 53.33%, Wnet = 55.30 MW (T4 = 556.8 °C).",
             "Constraint Activity Analysis:",
             "• The optimum compression ratio (rp ≈ 21.7) at TIT = 1500 K naturally yields an exhaust temperature of T4 = 556.8 °C.",
             "• Because T4 = 556.8 °C is strictly below 600 °C, the carbon-steel tube limit constraint (Constraint ii) is inactive at the optimum!",
             "• Relaxing the HRSG tube limit from 650 °C to 700 °C provides ZERO efficiency gain because the topping Brayton cycle already operates at optimal expansion.",
             "Engineering Capital Allocation:",
             "• Materials money should NOT be spent upgrading HRSG tubes from carbon steel to high-alloy stainless steel.",
             "• Instead, R&D capital should be directed to turbine blade coatings to allow higher TIT (e.g. TIT > 1500 K with ceramic thermal barrier coatings), where efficiency gains are dramatic."
         ])

# -----------------------------------------------------------------------------
# SLIDE 8: Section 4 - Bi-Objective Pareto Front (NSGA-II)
# -----------------------------------------------------------------------------
slide8 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide8, "Section 4: Bi-Objective Pareto Front (Thermal Efficiency vs Net Power)", "4. Pareto Plot")

pareto_img_path = os.path.join(DIR, 'plot_pareto_front.png')
if os.path.exists(pareto_img_path):
    slide8.shapes.add_picture(pareto_img_path, Inches(0.8), Inches(1.6), width=Inches(6.5))

add_card(slide8, Inches(7.6), Inches(1.6), Inches(4.9), Inches(5.3),
         "Trade-off Analysis & Operational Recommendation", [
             "Pareto Front Extraction (NSGA-II):",
             "• 100 non-dominated designs extracted spanning from 52.80% to 53.39% efficiency, and 55.3 MW to 61.8 MW net power.",
             "Physical Trade-Off Mechanism:",
             "• Maximizing thermal efficiency (ηcc) favors higher compression ratios (rp ≈ 22) and high steam drum pressures (Ps ≈ 46 bar), maximizing combined exergy recovery.",
             "• Maximizing net power (Wnet) favors slightly lower pressure ratios (rp ≈ 16 - 18) where gas turbine specific work (kJ/kg air) peaks, allowing higher flue gas mass flow and larger bottoming steam output.",
             "Design Decision Recommendation:",
             "• For a baseload utility plant, fuel cost dominates lifetime levelized cost of electricity (LCOE).",
             "• We recommend operating near the high-efficiency elbow: ηcc = 53.25%, Wnet = 57.5 MW.",
             "• This captures 99.8% of maximum efficiency while gaining +2.2 MW (+4.0%) of additional electrical output for minimal marginal capital investment."
         ])

# -----------------------------------------------------------------------------
# SLIDE 9: Section 5 - Conclusion & Engineering Recommendations
# -----------------------------------------------------------------------------
slide9 = prs.slides.add_slide(prs.slide_layouts[6])
add_header(slide9, "Section 5: Final Recommendations, Binding Constraints & Design Levers", "5. Conclusion")

add_card(slide9, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.3),
         "Recommended Operating Point Summary", [
             "Optimal Design Parameters:",
             "• Compression ratio rp = 21.68",
             "• Turbine inlet temperature TIT = 1500.0 K (1226.85 °C)",
             "• Steam drum pressure Ps = 46.48 bar",
             "• Superheat steam temperature Ts = 539.4 °C (812.6 K)",
             "• Condenser back-pressure Pcond = 0.0500 bar",
             "Performance Metrics:",
             "• Overall Combined-Cycle Efficiency: 53.33%",
             "• Total Plant Net Power Output: 55.30 MW (for 100 kg/s air flow)",
             "• Specific Work: 553.03 kJ/kg air",
             "• Bottoming-to-Topping Work Ratio: 0.4160",
             "• HRSG Thermal Effectiveness: 78.50%",
             "Computational Pipeline Performance:",
             "• LHS + Surrogate required only 500 direct physics runs (vs 3.2 million for full grid search: 6,400x compute reduction).",
             "• Adaptive refinement verified prediction to within 0.0635 pp gap."
         ])

add_card(slide9, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3),
         "Active Constraints & Biggest Improvement Levers", [
             "Binding Constraints at Optimum:",
             "1. Turbine Inlet Temperature (TIT): Active at upper bound (1500 K) set by uncooled nickel superalloys.",
             "2. Superheater Approach Temp (ΔTapproach): Active at ΔTapproach = 17.4 K (well above 5 K minimum).",
             "3. Steam Turbine Exit Quality: x6 = 0.924 satisfies the erosion limit (x6 >= 0.88).",
             "4. Gas Entering HRSG: T4 = 556.8 °C leaves 93.2 K safety margin below the 650 °C carbon-steel limit.",
             "Inactive Constraints:",
             "• Stack gas temperature (145 °C vs 100 °C dew point ceiling).",
             "• Combustor equivalence ratio (phi = 0.355 vs 0.50 NOx ceiling).",
             "The Single Biggest Design Lever:",
             "• Turbine Inlet Temperature (TIT): Elevating TIT with advanced blade cooling or thermal barrier coatings (TBC) to 1600+ K increases combined cycle efficiency by +2.5 to +3.8 pp.",
             "• Bottoming cycle dual-pressure HRSG: Adding an intermediate pressure drum would capture additional exergy, reducing stack loss to 105 °C and lifting plant efficiency above 56%."
         ])

save_pptx = os.path.join(DIR, 'Project1_Presentation.pptx')
prs.save(save_pptx)
print(f"\nSuccessfully generated Project 1 presentation: {save_pptx}")
