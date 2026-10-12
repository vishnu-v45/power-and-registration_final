# ME3160 Power & Refrigeration Cycles — Final Term Projects

This repository contains the complete, validated implementations of both end-semester term projects for **ME3160: Power & Refrigeration Cycles**.

---

## Repository Structure

```
├── Project_1_Combined_Cycle/
│   ├── README.md                            # Comprehensive technical documentation & governing equations
│   ├── Project_1_Comprehensive_Report.pdf   # Publication-quality technical PDF report
│   ├── Project1_Presentation.pptx           # 9-slide widescreen presentation deck
│   ├── run_project1.py                      # Master driver reproducing all figures and tables
│   ├── test_validation.py                   # Automated validation suite (Checks 1, 2, 3)
│   ├── thermo_gas.py                        # Variable Cp air & flue gas thermodynamic engine
│   ├── rankine_cycle.py                     # CoolProp water/steam Rankine bottoming cycle
│   ├── hrsg.py                              # HRSG pinch-point analysis & heat exchanger model
│   ├── combined_cycle.py                    # Integrated plant solver & constraint monitor
│   ├── surrogate_pipeline.py                # LHS (N=500), RSM/ANN surrogates, GA & NSGA-II
│   ├── doe_samples.csv                      # 500-sample LHS dataset with constraint margins
│   ├── sensitivity_hrsg_limit.csv           # HRSG gas limit sensitivity results
│   └── *.png                                # 6 publication figures (Pareto front, T-Q, T-s, etc.)
│
├── Project_2_Absorption_Chiller/
│   ├── README.md                            # Comprehensive technical documentation & governing equations
│   ├── Project_2_Comprehensive_Report.pdf   # Publication-quality technical PDF report
│   ├── Project2_Presentation.pptx           # 8-slide widescreen presentation deck
│   ├── run_project2.py                      # Master driver reproducing all figures and tables
│   ├── test_validation.py                   # Automated validation suite (22 benchmark quantities)
│   ├── psychrometrics.py                    # First-principles moist air, zone loads, & coil model
│   ├── ammonia_props.py                     # Peng-Robinson cubic real-gas EOS with departure functions
│   ├── patek_klomfar.py                     # Pátek & Klomfar (1995) NH3-H2O mixture thermodynamics
│   ├── absorption_chiller.py                # 11-state absorption chiller engine & First Law solver
│   ├── condenser_design.py                  # Evaporative vs air-cooled rating & off-design solver
│   ├── tasks_chiller.py                     # Implementation of Tasks 1, 2, 3, and 4
│   ├── seasonal_summary_p2.csv              # 6 seasonal operating conditions summary
│   ├── condenser_comparison_p2.csv          # Evaporative vs air-cooled condenser comparison
│   ├── fresh_air_sensitivity_p2.csv         # 10% to 50% fresh air sensitivity dataset
│   ├── validation_results_p2.csv            # Complete 22-parameter validation benchmark results
│   └── *.png                                # 6 publication figures (Psychrometric, seasonal duties, etc.)
│
├── ME3160_Term_Projects_Problem_Statement.pdf # Official 13-page problem statement
├── ME3160_Project_1_Support_Material.pdf       # 6-page optimization guide & pseudocode
└── ME3160_All_Problem_Statements_Extracted_Text.md # Searchable text of all problem statements
```

---

## Project 1: Surrogate-Assisted Optimization of a Methane-Fired Combined Cycle
* **Topping Brayton Cycle:** Variable specific heat $C_p(T)$ air model calibrated against Borgnakke Table A.6/A.7 ($<0.01\%$ error across $250\text{--}2000\text{ K}$). Solves isentropic expansion using standard entropy function $s^\circ(T)$ and relative pressure $P_r(T)$.
* **Bottoming Rankine Cycle:** Single-pressure subcritical HRSG with pinch analysis ($\Delta T_{pinch} \ge 10\text{ K}, \Delta T_{approach} \ge 5\text{ K}$) using `CoolProp.Water`.
* **Surrogate Pipeline:** 500-sample Latin Hypercube Sampling (LHS), Quadratic Response Surface Methodology (RSM, $R^2 = 0.9965$) with ANOVA, and Multilayer Perceptron Neural Network (ANN, $R^2 = 0.9799$).
* **Optimization:** Genetic Algorithm (`pymoo`) yields optimal $\eta_{cc} = 53.33\%$ ($\dot{W}_{net} = 55.30\text{ MW}$) at $r_p = 21.68$, $\text{TIT} = 1500\text{ K}$, $P_s = 46.48\text{ bar}$, $T_s = 539.4\ ^\circ\text{C}$, $P_{cond} = 0.050\text{ bar}$. Validation gap is $0.0635\text{ pp} \le 0.20\text{ pp}$.
* **Materials Sensitivity:** Carbon-steel tube limit ($650\ ^\circ\text{C}$) is inactive at optimal $r_p \approx 21.7$ ($T_4 = 556.8\ ^\circ\text{C}$). Recommends allocating R&D capital to turbine blade coatings rather than HRSG alloys.
* **Bi-Objective Pareto Front:** NSGA-II extracts 100 non-dominated points between max efficiency ($53.39\%$) and max power ($61.8\text{ MW}$).

---

## Project 2: Waste-Heat-Driven Ammonia–Water District Absorption Chiller
* **Zero Black-Box Physics:** Pure moist air ideal gas mixture relations; implicit adiabatic saturation $T_{wb}$ solver; Peng-Robinson cubic EOS for ammonia with Lee-Kesler / Pitzer generalized vapor pressure and departure functions; complete Pátek & Klomfar (1995) mixture model with calibrated Table 1 Row 13 exponent ($a_{13} = 4.895960\times 10^0$).
* **District Cooling (400 Zones):** Iterative room moisture balances matching $22\ ^\circ\text{C}, 50\%\text{ RH}$ across 6 Indian seasons with $1.07\times$ distribution losses.
* **Governing Chiller Capacity:** Governed by **Monsoon Day ($4,908.6\text{ kW}$)** rather than Summer Day ($4,552.9\text{ kW}$) due to massive fresh-air latent load ($w_{oa} = 30.6\text{ g/kg}$ vs $23.5\text{ g/kg}$).
* **Condenser Selection:** Evaporative Condenser ($1,198\text{ m}^2, 15.53\text{ bar}$) selected over Air-Cooled Finned-Tube ($22,400\text{ m}^2, 21.60\text{ bar}$), which violates the 20 bar ASME vessel pressure limit.
* **Decanter Tank & Water Recovery:** Sized at Monsoon Day ($89.7\text{ m}^3\text{/day}$ condensate), offsetting $24.0\%$ of evaporative cooling tower makeup water demand.
* **Monsoon Night Humidity Remedy:** Resolves $76.2\%$ room RH drift via deep subcooling ($ADP = 14.5\ ^\circ\text{C}$) and $2.8\text{ K}$ terminal reheat ($410\text{ kW}$) harvested from waste heat.
* **Single Biggest Design Lever:** Solution Heat Exchanger effectiveness ($\varepsilon_{SHX}$). Increasing $\varepsilon_{SHX}$ from 0.70 to 0.80 saves $890\text{ kW}$ generator heat, boosting COP by $+10.0\%$.

---

## Quick Start & Verification

Ensure dependencies are installed:
```bash
pip install numpy scipy pandas matplotlib scikit-learn CoolProp pymoo python-pptx reportlab
```

Run validation tests:
```bash
# Project 1 Validation
python Project_1_Combined_Cycle/test_validation.py

# Project 2 Validation
python Project_2_Absorption_Chiller/test_validation.py
```

Run end-to-end simulations:
```bash
# Project 1 Full Pipeline
python Project_1_Combined_Cycle/run_project1.py

# Project 2 Full Pipeline
python Project_2_Absorption_Chiller/run_project2.py
```
