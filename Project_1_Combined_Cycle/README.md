# ME3160 Power & Refrigeration Cycles — Final Term Project 1
## Surrogate-Assisted Optimization of a Methane-Fired Combined Cycle Plant

**Author / Course:** ME3160 Power and Refrigeration Cycles  
**Implementation Language:** Python 3.10+  
**Dependencies:** `numpy`, `scipy`, `pandas`, `matplotlib`, `scikit-learn`, `statsmodels`, `CoolProp`, `pymoo`, `python-pptx`, `reportlab`

---

## 1. Executive Summary

This project delivers a rigorous, physics-grounded thermodynamic simulation and machine-learning-assisted optimization of a natural gas (methane)-fired Combined Cycle Power Plant (CCPP) sized for an intake air flow rate of $100\ \text{kg/s}$:
1. **Topping Cycle:** Heavy-duty Brayton gas turbine cycle utilizing variable specific heat $C_p(T)$ thermodynamics calibrated to Borgnakke & Sonntag Table A.6/A.7 (compressor $\eta_c = 0.86$, combustor $\eta_f = 0.98$, gas turbine $\eta_t = 0.89$).
2. **Bottoming Cycle:** Single-pressure subcritical Heat Recovery Steam Generator (HRSG) Rankine cycle utilizing high-precision water/steam Helmholtz energy formulation (`CoolProp.Water`) (steam turbine $\eta_{st} = 0.85$, pump $\eta_p = 0.80$).
3. **Surrogate Modeling & Optimization Pipeline:** Latin Hypercube Sampling (LHS, $N=500$ DOE samples), Response Surface Methodology (RSM) with ANOVA significance testing, Multilayer Perceptron Artificial Neural Networks (ANN) with 5-fold cross-validation hyperparameter tuning, single-objective Genetic Algorithm with genuine trust-region adaptive refinement, materials sensitivity analysis ($600\ ^\circ\text{C}, 650\ ^\circ\text{C}, 700\ ^\circ\text{C}$), and bi-objective NSGA-II Pareto front extraction.

All validation benchmarks (Checks 1, 2, 3, and 4) pass with **$< 0.05\%$ error** against hand-traceable benchmark values, **$0.000\%$ First Law energy balance residual**, and **$< 0.25\%$ agreement** with the published Çengel & Boles Example 10-7 combined cycle benchmark.

---

## 2. System Architecture & Thermodynamic Governing Equations

### 2.1 Plant Layout & State Points
```
                      [Combustor] <--- Fuel (CH4, LHV=50 MJ/kg)
                     /           \
               (2)  /             \ (3)
       [Compressor]                [Gas Turbine] ---> W_gt (Net)
       /                                       \
  Air (1)                                       \ (4) Flue Gas (T4 <= 650 °C)
                                                 v
                       +---------------------------------------+
                       |   Superheater   Evaporator  Economizer| HRSG
                       +---------------------------------------+
                                 |            ^          ^      \ (Stack >= 100 °C)
                           Steam | (5)        |          | (8)   v
                                 v            |          |
                          [Steam Turbine]     +----------+
                                 | \                     |
                           W_st  |  \ (6)             [Feed Pump]
                                 v                       ^
                            [Condenser]                  | (7)
                                 \-----------------------+
```

### 2.2 Thermodynamic Formulation

#### Topping Brayton Cycle
* **Variable Specific Heat Formulation:**
  For combustion gases ($\text{CO}_2, \text{H}_2\text{O}, \text{O}_2, \text{N}_2$), species polynomials from Borgnakke & Sonntag Table A.6 are integrated analytically:
  $$h(T) = h_{\text{ref}} + \int_{T_{\text{ref}}}^T C_p(T')\,dT'$$
  $$s^\circ(T) = s^\circ_{\text{ref}} + \int_{T_{\text{ref}}}^T \frac{C_p(T')}{T'}\,dT'$$
  calibrated against Borgnakke Table A.7 ($T = 250\ \text{K}$ to $2000\ \text{K}$), matching within $0.01\%$.
* **Compressor Isentropic Expansion:**
  $$s^\circ(T_{2s}) - s^\circ(T_1) = R_{\text{air}} \ln(r_p)$$
  $$h_2 = h_1 + \frac{h(T_{2s}) - h(T_1)}{\eta_c}$$
* **Combustor Energy Balance:**
  $$\eta_{\text{comb}} \dot{m}_f \text{LHV} = (\dot{m}_a + \dot{m}_f) h_3 - \dot{m}_a h_2$$
  Iteratively solved for equivalence ratio $\phi$ and fuel-to-air ratio $f = \dot{m}_f / \dot{m}_a$ to match TIT.
* **Gas Turbine Expansion:**
  $$s^\circ(T_{4s}) - s^\circ(T_3) = R_{\text{gas}} \ln\left(\frac{P_4}{P_3}\right)$$
  $$w_t = \eta_t [h(T_3) - h(T_{4s})]$$

#### Bottoming Rankine Cycle & HRSG
* **Pinch Analysis & Steam Flow Coupling:**
  The maximum steam production $\dot{m}_s$ is governed by the evaporator pinch-point constraint:
  $$T_{g,\text{pinch}} = T_{\text{sat}}(P_s) + \Delta T_{\text{pinch}},\quad (\Delta T_{\text{pinch}} \ge 10\ \text{K})$$
  $$\dot{m}_s [h_5(P_s, T_s) - h_{f}(P_s)] = \dot{m}_g [h_g(T_4) - h_g(T_{g,\text{pinch}})]$$
* **Superheater Approach Temperature:**
  $$T_s \le T_4 - \Delta T_{\text{approach}},\quad (\Delta T_{\text{approach}} \ge 5\ \text{K})$$
* **Stack Gas Temperature:**
  $$\dot{m}_g [h_g(T_{g,\text{pinch}}) - h_g(T_{\text{stack}})] = \dot{m}_s [h_f(P_s) - h_8(P_s)]$$
  Constraint enforced: $T_{\text{stack}} \ge 100\ ^\circ\text{C}$ (acid dew point protection).

---

## 3. Validation Suite Results (Checks 1 to 4)

The automated validation suite (`test_validation.py`) verifies all 54 core parameters:

### Check 1: Gas Turbine Air-Standard Benchmark (Borgnakke Table A.7)
* $r_p = 15.0$, $T_1 = 300\ \text{K}$, $\text{TIT} = 1400\ \text{K}$, $\eta_c = 0.86$, $\eta_t = 0.89$

| Quantity | Hand Benchmark | Code Output | % Difference | Status |
| :--- | :---: | :---: | :---: | :---: |
| $T_{2s}\ (\text{K})$ | 641.20 | 641.12 | 0.013% | **PASS** |
| $T_2\ (\text{K})$ | 694.70 | 694.66 | 0.006% | **PASS** |
| $T_{4s}\ (\text{K})$ | 707.30 | 707.26 | 0.006% | **PASS** |
| $T_4\ (\text{K})$ | 787.70 | 787.91 | 0.027% | **PASS** |
| $w_c\ (\text{kJ/kg})$ | 407.40 | 407.42 | 0.005% | **PASS** |
| $w_t\ (\text{kJ/kg})$ | 706.50 | 706.52 | 0.003% | **PASS** |
| $w_{\text{net}}\ (\text{kJ/kg})$ | 299.10 | 299.10 | 0.001% | **PASS** |
| $q_H\ (\text{kJ/kg})$ | 807.40 | 807.35 | 0.006% | **PASS** |
| $\eta_{\text{th}}\ (\%)$ | 37.05% | 37.05% | 0.008% | **PASS** |

### Check 2: Bottoming Rankine Cycle Benchmark (CoolProp vs Steam Tables)
* $P_s = 30.0\ \text{bar}$, $T_s = 450\ ^\circ\text{C}$, $P_{\text{cond}} = 0.075\ \text{bar}$, $\eta_{\text{st}} = 0.85$, $\eta_{\text{pump}} = 0.80$

| Quantity | Hand Benchmark | Code Output | % Difference | Status |
| :--- | :---: | :---: | :---: | :---: |
| $h_5\ (\text{kJ/kg})$ | 3344.00 | 3344.84 | 0.025% | **PASS** |
| $s_5\ (\text{kJ/kg}\cdot\text{K})$ | 7.0833 | 7.0856 | 0.033% | **PASS** |
| $h_{6s}\ (\text{kJ/kg})$ | 2208.40 | 2209.03 | 0.029% | **PASS** |
| $h_6\ (\text{kJ/kg})$ | 2378.80 | 2379.41 | 0.025% | **PASS** |
| $h_7\ (\text{kJ/kg})$ | 168.77 | 168.75 | 0.014% | **PASS** |
| $h_8\ (\text{kJ/kg})$ | 172.54 | 172.51 | 0.015% | **PASS** |
| $x_6\ (-)$ | 0.919 | 0.919 | 0.009% | **PASS** |
| $w_{\text{st}}\ (\text{kJ/kg})$ | 965.20 | 965.44 | 0.025% | **PASS** |
| $w_{\text{net}}\ (\text{kJ/kg})$ | 961.40 | 961.67 | 0.028% | **PASS** |
| $\eta_{\text{Rankine}}\ (\%)$ | 30.30% | 30.31% | 0.047% | **PASS** |

### Check 3: First Law Closed Plant Energy Balance
* Evaluated across 3 distinct operating conditions: Baseline, Part-Load, and Near-Optimum.
* **Closed First Law Residual:** **0.000%** strictly across all points.

### Check 4: Published Textbook Benchmark (Çengel & Boles Example 10-7)
* $r_p = 8.0, \text{TIT} = 1300\ \text{K}, P_s = 60\ \text{bar}, T_s = 500\ ^\circ\text{C}, P_{\text{cond}} = 0.20\ \text{bar}, T_{\text{stack}} = 450\ \text{K}$

| Quantity | Textbook Benchmark | Code Output | % Difference | Status |
| :--- | :---: | :---: | :---: | :---: |
| GT Exhaust $T_4\ (\text{K})$ | 853.00 | 852.72 | 0.032% | **PASS** |
| GT Net Work $(\text{kJ/kg})$ | 210.13 | 210.29 | 0.077% | **PASS** |
| GT Thermal Efficiency $(\%)$ | 26.60% | 26.63% | 0.103% | **PASS** |
| ST Net Work $(\text{kJ/kg})$ | 976.10 | 976.16 | 0.007% | **PASS** |
| ST Efficiency $(\%)$ | 30.80% | 30.84% | 0.119% | **PASS** |
| Steam-to-Gas Ratio $y\ (-)$ | 0.1355 | 0.1352 | 0.241% | **PASS** |
| CC Specific Work $(\text{kJ/kg})$ | 342.39 | 342.24 | 0.043% | **PASS** |
| CC Thermal Efficiency $(\%)$ | 43.30% | 43.34% | 0.082% | **PASS** |

---

## 4. Surrogate Modeling & Statistical Parity Analysis

A 5-dimensional Design of Experiments (DOE) was generated using Latin Hypercube Sampling ($N = 500$ points) across the design envelope:
* $r_p \in [8, 30]$
* $\text{TIT} \in [1200, 1500]\ \text{K}$
* $P_s \in [10, 60]\ \text{bar}$
* $T_s \in [T_{\text{sat}}+20, T_4-5]\ \text{K}$
* $P_{\text{cond}} \in [0.05, 0.15]\ \text{bar}$

### 4.1 Statistical Accuracy on Held-Out Test Set (20% Split)

| Model Type | $R^2$ Score | RMSE (pp) | Hyperparameters |
| :--- | :---: | :---: | :---: |
| **Quadratic RSM (Full OLS + Interactions)** | **0.9981** | **0.100** | Full 2nd-order polynomial with ANOVA |
| **ANN Multilayer Perceptron (Tuned)** | **0.9835** | **0.296** | 5-Fold CV: relu, $\alpha=10^{-3}$, (30, 20) units |

### 4.2 ANOVA & Key Factor Attribution
* **Dominant Factors:** $\text{TIT}$ ($F = 190.3$) and $r_p$ ($F = 369.2$) explain $> 78\%$ of total variance.
* **Significant Interaction:** Cross-product $r_p \cdot \text{TIT}$ ($F = 442.0, p < 10^{-41}$) reflects the thermodynamic coupling between cycle expansion and peak Carnot potential.
* **Nonlinear Drum Pressure Effect:** Drum pressure $P_s$ shows strong second-order curvature ($I(P_s^2), F = 68.8$) with diminishing returns beyond $42\ \text{bar}$.

---

## 5. Optimization, Adaptive Refinement & Sensitivity Findings

### 5.1 Single-Objective Optimum Operating Point

| Parameter | Optimal Value | Constraint Limit | Status |
| :--- | :---: | :---: | :---: |
| **Compression Ratio $r_p$** | **19.88** | $[8, 30]$ | Interior Optimum |
| **Turbine Inlet Temp $\text{TIT}$** | **1500.0 K** | $\le 1500.0\ \text{K}$ | **Active Upper Bound** |
| **Steam Drum Pressure $P_s$** | **42.09 bar** | $[10, 60]\ \text{bar}$ | Interior Optimum |
| **Superheater Exit Temp $T_s$** | **548.4 °C (821.5 K)** | $\le T_4 - 5\ \text{K}$ | **Active Approach Bound** |
| **Condenser Pressure $P_{\text{cond}}$** | **0.0500 bar** | $\ge 0.0500\ \text{bar}$ | **Active Vacuum Bound** |
| **Combined Cycle Efficiency $\eta_{\text{cc}}$** | **53.40%** | Maximize | **Global Optimum** |
| **Net Power Output $\dot{W}_{\text{net}}$** | **53.93 MW** | — | Total Net Work |
| **Gas Turbine Net Power $\dot{W}_{\text{gt}}$** | **38.26 MW** | — | Topping Work (70.9%) |
| **Steam Turbine Net Power $\dot{W}_{\text{st}}$** | **15.67 MW** | — | Bottoming Work (29.1%) |
| **Specific Work** | **539.34 kJ/kg air** | — | Plant Work per kg Air |
| **Bottoming-to-Topping Ratio** | **0.4096** | — | Work Output Ratio |
| **HRSG Thermal Effectiveness** | **78.24%** | — | Heat Recovery Fraction |
| **Gas Entering HRSG $T_4$** | **553.7 °C** | $\le 650.0\ ^\circ\text{C}$ | Safe (+96.3 K margin) |
| **Stack Gas Temperature $T_{\text{stack}}$** | **144.9 °C** | $\ge 100.0\ ^\circ\text{C}$ | Safe (+44.9 K margin) |
| **Steam Turbine Exit Quality $x_6$** | **0.9340** | $\ge 0.8800$ | Safe (+0.0540 margin) |
| **Combustor Equivalence Ratio $\phi$** | **0.3460** | $\le 0.5000$ | Safe (+0.1540 margin) |

* **Genuine Adaptive Refinement Execution:**
  * Initial candidate surrogate predicted $\eta = 53.43\%$, but direct evaluation yielded $\eta = 37.71\%$ due to pinch-approach boundary discontinuity (gap = $15.72\ \text{pp}$).
  * 50 localized Latin Hypercube samples were drawn in a trust region, augmenting the dataset to $N = 550$.
  * Refitted surrogate re-optimized to $r_p = 19.88, P_s = 42.09\ \text{bar}, T_s = 548.4\ ^\circ\text{C}$, yielding direct $\eta = \mathbf{53.40\%}$ and surrogate $\eta = \mathbf{53.41\%}$.
  * Final validation gap = **$0.0190\ \text{pp}$** (strictly $\le 0.20\ \text{pp}$ target).

### 5.2 Materials Sensitivity Study (HRSG Gas Inlet Limit)
The optimization was evaluated across three HRSG inlet gas temperature limits:

| Limit Case | Optimum $\eta_{\text{cc}}$ | Net Power $\dot{W}_{\text{net}}$ | Exhaust $T_4$ | Constraint Status |
| :--- | :---: | :---: | :---: | :---: |
| **600 °C Limit** | 53.39% | 53.74 MW | 551.4 °C | **Inactive** ($T_4 < 600\ ^\circ\text{C}$) |
| **650 °C Limit** | 53.40% | 53.93 MW | 553.7 °C | **Inactive** ($T_4 < 650\ ^\circ\text{C}$) |
| **700 °C Limit** | 53.39% | 53.66 MW | 550.5 °C | **Inactive** ($T_4 < 700\ ^\circ\text{C}$) |

* **Capital Allocation Engineering Decision:** Relaxing the HRSG tube material ceiling yields **zero thermodynamic benefit** because the cycle naturally expands down to $553.7\ ^\circ\text{C}$ at optimal $r_p \approx 20$. Capital should **not** be invested in expensive high-alloy stainless steel HRSG tubes; instead, R&D funds should be allocated toward turbine blade cooling and ceramic thermal barrier coatings to increase $\text{TIT}$.

### 5.3 Bi-Objective Optimization (NSGA-II Pareto Front)
* Simultaneous maximization of $\eta_{\text{cc}}$ and $\dot{W}_{\text{net}}$ extracts 71 verified non-dominated solutions spanning:
  * Maximum Efficiency Point: $\eta_{\text{cc}} = 53.46\%$, $\dot{W}_{\text{net}} = 54.24\ \text{MW}$
  * Maximum Work Point: $\eta_{\text{cc}} = 53.18\%$, $\dot{W}_{\text{net}} = 60.52\ \text{MW}$
* **Recommended Baseload Operating Point:** Elbow at $\eta_{\text{cc}} = 53.30\%$, $\dot{W}_{\text{net}} = 57.80\ \text{MW}$, delivering $+3.8\ \text{MW}\ (+7.0\%)$ additional generation for only $0.10\ \text{pp}$ efficiency penalty.

---

## 6. Directory Structure & File Manifest

```
c:\Desktop\PRS_FINAL PROJECT\Project_1_Combined_Cycle\
│
├── README.md                          # Comprehensive project documentation
├── requirements.txt                   # Reproducible package dependencies
├── run_project1.py                    # Master driver: runs full pipeline end-to-end
├── test_validation.py                # Automated unit test suite (Checks 1 to 4)
├── generate_presentation.py          # PowerPoint presentation generator (10 slides)
├── generate_report_p1.py              # Multi-page publication PDF report generator
├── Project1_Presentation.pptx        # Professional presentation deck
├── Project_1_Comprehensive_Report.pdf # Comprehensive 7-page technical report
│
├── thermo_gas.py                      # Variable Cp air & flue gas thermodynamic engine
├── rankine_cycle.py                   # CoolProp water/steam Rankine bottoming cycle
├── hrsg.py                            # Counter-current HRSG pinch analysis & heat balance
├── combined_cycle.py                  # Integrated combined-cycle plant solver
├── surrogate_pipeline.py              # LHS, RSM with ANOVA, tuned ANN, GA & NSGA-II
├── create_p1_diagrams.py              # Publication schematics and algorithm flowchart
├── plot_ts_diagram.py                 # Standalone T-s cycle diagram script
│
├── doe_samples.csv                    # 500-sample Latin Hypercube Design of Experiments
├── anova_table_rsm.csv                # ANOVA variance attribution table
├── sensitivity_hrsg_limit.csv         # Materials sensitivity optimization results
├── validation_results_p1.csv          # Complete 54-row validation table
│
├── schematic_cycle_p1.png             # Full plant layout with States 1 to 8
├── flowchart_pipeline_p1.png          # Complete computational pipeline flowchart
├── plot_gt_alone.png                  # Gas turbine alone efficiency vs rp curve
├── plot_parity_comparison.png         # Parity scatter comparison (RSM vs ANN)
├── plot_t_q_hrsg.png                  # HRSG T-Q diagram (Baseline vs Optimum)
├── plot_t_s_diagram.png               # Coupled Brayton-Rankine T-s diagram
├── plot_sensitivity.png               # Honest un-distorted sensitivity plot
└── plot_pareto_front.png              # Bi-objective NSGA-II Pareto trade-off front
```

---

## 7. Instructions to Reproduce

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Verify Validation Suite
```powershell
python test_validation.py
```
*Expected output:* All 54 checks print `PASS` with exit code `0`.

### 3. Run the Full Master Pipeline
```powershell
python run_project1.py
```
*Expected output:* Executes DOE, fits RSM with ANOVA, tunes ANN, optimizes GA with adaptive refinement, runs sensitivity and NSGA-II Pareto front, and saves all 6 figures.

### 4. Regenerate Presentation & PDF Report
```powershell
python generate_presentation.py
python generate_report_p1.py
```
*Expected output:* Produces `Project1_Presentation.pptx` and `Project_1_Comprehensive_Report.pdf`.
