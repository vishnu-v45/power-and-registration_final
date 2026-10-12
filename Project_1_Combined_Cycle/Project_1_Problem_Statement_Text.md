# ME3160 Project 1: Surrogate-Assisted Optimization of a Methane-Fired Combined Cycle

--- PAGE 1 ---
ME3160 Power & Refrigeration Cycles 
End Semester Term Project 
Project – 1 Surrogate-Assisted Optimization of a Methane-Fired Combined Cycle 
1.1 Background 
A gas turbine burning natural gas (modelled as pure methane) rejects exhaust stream at 500–650 
°C. Rather than discarding this energy, a combined-cycle plant routes it through a heat recovery 
steam generator (HRSG) to raise steam for a bottoming Rankine cycle. Real plants are limited not 
by thermodynamics alone but by materials: turbine blades, HRSG tubes, and the stack all have 
temperature ceilings or floors that cap what the designer can do. Your task is to build a physics-
based model of such a plant, respect those limits, and use data-driven optimization to find the 
operating point that maximizes overall efficiency. 
1.2 System Description  
Methane Fired Open Brayton Cycle – Topping Cylce 
• Compressor: ambient air (1.013 bar, 298 K, 21% O₂ / 79% N₂ by mole) compressed to pressure 
ratio 𝑟𝑝, isentropic efficiency 𝜂𝑐= 0.86 
• Combustor: methane (LHV = 50.0 MJ/kg) burned with excess air at constant pressure. Assume 
complete combustion (products: CO₂, H₂O, O₂, N₂). Combustor efficiency (𝜂𝑓) is 0.98. The 
fuel–air ratio (
𝑓
𝐴) sets the turbine inlet temperature (TIT) 
• Turbine: expands products to 1.05 bar, isentropic efficiency 𝜂𝑡= 0.89 
• No blade cooling air is required as the TIT is below the material limit 
Ideal gas law with temperature-dependent specific heats for each species (use 𝐶𝑝(𝑇) 
polynomials in Borgnakke & Sonntag, Table A.6). Compute mixture enthalpy and entropy from 
mass-fraction-weighted species properties. Isentropic processes must be solved via the relative-
pressure/entropy-function approach (𝑠2 −𝑠1 = ((𝑠𝑇2
𝑜−𝑠𝑇1
𝑜) −𝑅ln (
𝑃2
𝑃1) , 𝑠𝑇
𝑜= ∫
𝐶𝑝
𝑇𝑑𝑇
𝑇
𝑇𝑜
), not 
with a constant 𝑘. Students who use constant 𝐶𝑝 will lose marks on the model-fidelity criterion. 
Single-pressure Low Pressure Rankine Cycle – Bottoming Cycle 
• HRSG: exhaust gas from gas turbine heats feedwater through economizer → evaporator → 
superheater. Gas-side pressure drop 3 kPa. Steam drum pressure is 𝑃𝑠 and superheat outlet 
temperature is 𝑇𝑠 
• Steam turbine: isentropic efficiency 𝜂𝑠𝑡= 0.85, exhausting to condenser at pressure 𝑃𝑐𝑜𝑛𝑑 
• Condenser: saturated liquid out 
• Feed pump: isentropic efficiency 0.80 
Steam side properties are to be estimated using CoolProp (CoolProp.CoolProp.PropsSI with fluid 
'Water'). No steam tables should be used 
 


--- PAGE 2 ---
1.3 Design Variables and Ranges 
Variable 
Symbol 
Range 
Compression ratio 
𝑟𝑝 
8 – 30  
Turbine inlet temperature 
TIT 
1200 – 1500 K 
Steam drum pressure 
𝑃𝑠 
10-60 bar 
Superheat temperature 
𝑇𝑠 
Saturation + 20 K -> HRSG limit 
Condenser pressure 
𝑃𝑐𝑜𝑛𝑑 
0.05 – 0.15 bar 
1.4 Practical Constraints 
Some of the hard constraints that cannot be violated are: 
i. 
Turbine inlet temperature (TIT) should be less than 1550 K, corresponding to uncooled 
nickel superalloy with TBC margin 
ii. 
Gas entering the HRSG should be less than 650 oC, corresponding to carbon-steel tube 
limit. This couples 𝑟𝑝 and TIT 
iii. 
Gas temperature leaving HRSG should be higher than 100 oC to stay about water dew point 
temperature 
iv. 
Δ𝑇𝑝𝑖𝑛𝑐ℎ≥10K at the evaporator and approached Δ𝑇≥5K at the superheater 
v. 
Steam turbine vapor quality is greater than 0.88 to prevent blade erosion 
vi. 
Equivalence ratio in the gas turbine combustor should be less than 0.5 for reduced NOx 
emission  
1.5 Objective 
Maximize the overall thermal efficiency for a plant sized to handle air mass flowrate (𝑚̇) of 100 
kg/s 
𝜂𝑐𝑐= 𝑊̇𝐺𝑇,𝑛𝑒𝑡+ 𝑊̇𝑆𝑇,𝑛𝑒𝑡
𝑚̇𝑓𝑄𝐿𝐻𝑉
 
Report specific work, bottoming-to-topping work ratio, and HRSG effectiveness at the optimum 
point 
1.6 Required Methodology 
Part A – Direct Model 
Write a Python code for the combined cycle that takes inputs as 𝑟𝑝, TIT, 𝑃𝑠, 𝑇𝑠, and 𝑃𝑐𝑜𝑛𝑑 and gives 
𝜂𝑐𝑐, 𝑊̇𝑛𝑒𝑡, feasibility with constraint margins. Validate it against the required baseline case as 
given in "Required Validation Test Case" below, and against a published textbook combined-cycle 
example. Plot 𝜂𝑐𝑐  vs 𝑟𝑝 at fixed TIT for the gas turbine alone and confirm the familiar maximum. 
Part B – Design of Experiments & Surrogates 
• Sample the 5-D design space with Latin Hypercube Sampling (≥ 300 points, scipy.stats.qmc). 
Record 𝜂𝑐𝑐 and each constraint margin; keep infeasible points, labelled. 
• Fit a surrogate models for 𝜂𝑐𝑐 and for the binding constraint margins: a full quadratic Response 
Surface (least squares, statsmodels or numpy.linalg.lstsq) with ANOVA to identify which terms 
matter, or an Artificial Neural Network (scikit-learn MLPRegressor or PyTorch, 2 hidden layers, 
tanh/ReLU) with an 80/20 train–test split and hyperparameter tuning. 
• Analyse R², RMSE, and parity plots on the held-out set. Discuss where the surrogate fails and 
why  


--- PAGE 3 ---
Part C – Optimization 
• Optimize the surrogate with a constrained method (using a genetic algorithm via pymoo or 
DEAP). 
• Re-evaluate the surrogate optimum with the direct model. Report the gap. If the gap exceeds 
0.2 percentage points of efficiency, perform at least one adaptive refinement (add samples 
near the predicted optimum, refit, re-optimize). 
• Sensitivity study: how does the optimum move if the gas entering the HRSG is relaxed to 700 
°C, or tightened to 600 °C? Which constraints are active at the optimum, and what does that 
tell you about where the materials money should be spent? 
• Bi-objective view: maximizing 𝜂𝑐𝑐 alone can drive down net specific work (smaller machinery 
does less work per unit mass flow, which matters for capital cost). Re-run the GA as a bi-
objective search: maximize 𝜂𝑐𝑐 and maximize 𝑊̇𝑛𝑒𝑡 simultaneously, subject to constraints 
given in section 1.4 and extract the Pareto front of non-dominated designs. This front is 
required in the report (see below) 
1.7 Required Validation Test Case 
Before any optimization work is accepted, each group must demonstrate that their code 
reproduces a fully worked, hand-traceable baseline. The numbers below are computed directly 
from the tables in Borgnakke & Sonntag (Tables A.7.1/A.7.2 for air, B.1.2/B.1.3 for steam) so they 
can be checked with no software at all. This is deliberately split into three independent checks, 
so a discrepancy can be traced to the specific routine at fault rather than lost in a single 
combined-cycle number. 
Check-1: Gas Turbine (air-standard) check 
Using pure air as the working fluid and given that 𝑇₁ = 300 K, 𝑃₁ = 100 kPa, 𝑟𝑝= 15, 𝑇₃ = 1400 
K, 𝜂𝑐= 0.86, 𝜂𝑡= 0.89, you should get  
State 
T (K) 
h (kJ/kg) 
𝑷𝒓 
Notes 
1 
300.0 
300.47 
1.1146 
Table A7.1/A7.2, exact 
2s 
≈641.2 
≈650.81 
16.72 
𝑃𝑟2 = 𝑃𝑟1𝑟𝑝 
2 (actual) 
≈694.7 
707.87 
— 
ℎ2 = ℎ1 + (ℎ2𝑠−ℎ1)/𝜂𝑐 
3 
1400.0 
1515.27 
361.62 
Table A7.1/A7.2, exact 
4s 
≈707.3 
≈721.47 
24.11 
𝑃𝑟4 = 𝑃𝑟3/𝑟𝑝 
4 (actual) 
≈787.7 
808.77 
— 
ℎ4 = ℎ3 −𝜂𝑡(ℎ3 −ℎ4𝑠) 
 
Your code should be able to match the above Brayton cycle state variables obtained using Tables 
A7.1 and A7.2. Based on these state variables, you should get: 
• 
𝑤𝑐= 407.4kJ/kg, 𝑤𝑡= 706.5kJ/kg and 𝑤𝑛𝑒𝑡= 299.1kJ/kg 
• 
𝑞ℎ= 807.4kJ/kg, 𝜂𝑡ℎ= 37.05% 
You should be able to match the temperatures at 𝑇2, 𝑇4 and 𝜂𝑡ℎ to establish that the code is able 
to solve the isentropic relation with variable 𝐶𝑝 for pure air 


--- PAGE 4 ---
Check-2: Rankine cycle v/s Steam Tables 
Given that 𝑃𝑠= 30 bar, 𝑇𝑠= 450 °𝐶, 𝑃𝑐𝑜𝑛𝑑= 7.5 𝑘𝑃𝑎, 𝜂𝑠𝑡= 0.85, 𝜂𝑝𝑢𝑚𝑝= 0.80 
State 
Description 
h (kJ/kg) 
s (kJ/kg·K) 
5 
Turbine inlet (3000 kPa, 450 °C) 
3344.00 
7.0833 
6s 
Isentropic to 7.5 kPa 
2208.4 
7.0833 
6 
Actual turbine exit 
2378.8 
— 
7 
Condenser exit, sat. liquid @ 7.5 kPa 
168.77 
0.5763 
8 
Pump exit (actual) 
172.54 
— 
  
Your code using CoolProp calls should recover the above state points of the Rankine cycle and 
should get the following results: 
• 
𝑥6𝑠= 0.848, actual exit quality 𝑥6 = 0.919 satisfies constraint C5 (≥ 0.88) 
• 
𝑤𝑠𝑡= 965.2 kJ/kg, 𝑤𝑝𝑢𝑚𝑝= 3.77 kJ/kg, 𝑤𝑛𝑒𝑡= 961.4 kJ/kg 
• 
𝑞_𝐻= 3171.5 kJ/kg → 𝜂𝑅𝑎𝑛𝑘𝑖𝑛𝑒= 30.3 % 
Check-3: Energy Balance 
The 1st law energy balance should be satisfied for all your runs: 
ṁ𝑓𝑢𝑒𝑙𝑄𝐿𝐻𝑉𝜂𝑐𝑜𝑚𝑏≈(𝑊̇𝐺𝑇,𝑛𝑒𝑡+ 𝑊̇𝑆𝑇,𝑛𝑒𝑡) + 𝑄̇𝑠𝑡𝑎𝑐𝑘+ 𝑄̇𝑐𝑜𝑛𝑑𝑒𝑛𝑠𝑒𝑟+ (𝑠𝑚𝑎𝑙𝑙 𝑙𝑜𝑠𝑠𝑒𝑠) 
Reporting Requirements 
Each report must include a Validation Table with columns Quantity | Hand value | Code output | 
% difference | Pass/Fail, covering every quantity in Checks 1–3, plus test_validation.py in the 
repository that asserts these tolerances automatically. Suggested tolerances: 0.5% for the gas-
side check (bounded by the hand-calculation's own interpolation error) and 0.1% for the steam-
side check (CoolProp vs. tables should agree tightly). A group that cannot meet these tolerances 
has an actual bug. 
1.8 Deliverables 
• 
Python repository with README, requirements, and a single reproducible driver script 
• 
A ppt giving the following: 
# 
Section 
Required content 
1 
Schematic 
A labelled block diagram of the full combined cycle — 
compressor, combustor, turbine, HRSG (economizer / evaporator 
/ superheater), steam turbine, condenser, feed pump — with 
state points numbered consistently with every equation and table 
used later in the report. 
2 
Algorithm 
A flowchart or structured pseudocode of the solver: how f/TIT is 
resolved from the combustor energy balance, how the isentropic 
relations are evaluated with variable cp, how the HRSG pinch 


--- PAGE 5 ---
# 
Section 
Required content 
point is located, and how the DOE, surrogate fitting, and 
optimization loop fit together. 
3 
Analysis 
Model validation against the Required Validation Test Case, T–s 
and T–Q diagrams at baseline and optimum, surrogate 
comparison 
(R², 
RMSE, 
parity 
plots), 
single-objective 
optimization results, constraint activity, and the HRSG 
relaxed/tightened sensitivity study. 
4 
Pareto plot 
The 𝜂𝑐𝑐  vs. 𝑊𝑛𝑒𝑡 Pareto front from the bi-objective GA run (Part C), 
with the single-objective optimum marked on it, and a short 
discussion of where the group would actually choose to operate 
and why. 
5 
Conclusion 
The recommended operating point, its efficiency and net specific 
work, the binding constraints at that point, and the single biggest 
lever (design variable or material limit) for improving the plant 
further. 
 
1.9 Rubric 
Criterion 
Weight 
Thermodynamic model fidelity (variable cp, correct mixture properties, correct 
pinch treatment) 
25 
Validation and error analysis (required test case, all 3 checks, within stated 
tolerances) 
20 
DOE and surrogate quality (both RSM and ANN, honest test-set metrics) 
10 
Optimization rigor (constraint handling, multi-start/GA, direct-model verification, 
refinement) 
10 
Physical interpretation and sensitivity study 
15 
Report and presentation 
20 
 
 


