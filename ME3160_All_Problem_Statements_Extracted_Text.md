# ME3160 Term Projects - Complete Problem Statements & Support Materials

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
 
 




# ME3160 Project 2: Waste-Heat-Driven Ammonia-Water Absorption Chiller

--- PAGE 6 ---
Project – 2 Waste-Heat-Driven Ammonia–Water Absorption Chiller for a District Cooling 
Network 
2.1 Background  
Industrial sites reject large quantities of medium-grade heat in the form of flue gas at 250–350 °C 
which is too cool for power generation but ideal for driving a thermally activated chiller. A 
ammonia–water absorption refrigeration unit converts that heat into chilled water, which a 
district cooling network distributes to air handling units (AHUs) in the surrounding buildings. 
Unlike a vapour-compression plant, its capacity and heat demand are strongly coupled to the 
ambient condition through the condenser and absorber, so the same machine behaves very 
differently across an Indian summer, monsoon, and winter. Your task is to model the full chain: 
outdoor air → AHU psychrometrics → chilled-water load → absorption cycle → waste-heat demand 
and size the components that must survive the whole year. 
2.2 System Description 
A. Waste heat source 
• Process flue gas, treated as an ideal gas with constant C𝑝= 1.10 kJ/kg·K, available at 300 °C, 
up to a maximum of 80 kg/s. 
• Flue gas must leave the generator heat exchanger at ≥ 140 °C. 
• Generator heat exchanger effectiveness 𝜀𝑔𝑒𝑛= 0.75, defined on the flue-gas side: 𝜀𝑔𝑒𝑛=
(𝑇𝑓𝑔,𝑖𝑛−𝑇𝑓𝑔,𝑜𝑢𝑡)/(𝑇𝑓𝑔,𝑖𝑛−𝑇𝑔𝑒𝑛), where 𝑇𝑔𝑒𝑛 is the solution temperature leaving the generator. 
The "heating load" asked for in Task 1 is the generator heat duty 𝑄𝑔𝑒𝑛; the flue-gas mass flow that 
supplies it follows from the effectiveness and the 140 °C floor. 
B. Ammonia-water chiller unit 
• Components: generator with rectifier (vapour leaving at 99.5 % NH₃ by mass), condenser, 
expansion valve, evaporator, absorber, solution pump (𝜂𝑝𝑢𝑚𝑝= 0.70), solution heat 
exchanger (𝜀𝑆𝐻𝑋= 0.70), weak-solution throttle. A refrigerant precooler is optional (state 
clearly if used). 
• Evaporator: 𝑇𝑒𝑣𝑎𝑝= 2 °C, supplying chilled water at 7 °C with 12 °C return. 
• Condenser and absorber are cooled by the same medium; assume 𝑇𝑎𝑏𝑠= 𝑇𝑐𝑜𝑛𝑑. 
• Generator outlet (weak solution), absorber outlet (strong solution), condenser outlet 
(saturated liquid), and evaporator outlet (saturated vapour) are all saturated states at their 
respective pressures. 
• Pressure drops in vessels and piping are neglected; 𝑃ℎ𝑖𝑔ℎ= 𝑃𝑠𝑎𝑡,𝑁𝐻3(𝑇𝑐𝑜𝑛𝑑), 𝑃𝑙𝑜𝑤=
𝑃𝑠𝑎𝑡,𝑁𝐻3(𝑇𝑒𝑣𝑎𝑝). 
• Minimum stable turndown of the chiller: 25 % of design capacity 
Property models: No black-box property libraries for ammonia or moist air. CoolProp is permitted 
only for pure water/steam (condensate, chilled water, any steam-side calculation, and the 
saturation pressure of water used inside the psychrometric relations below). Ammonia and moist 
air must be evaluated using thermodynamic relations as discussed in class lectures with a real-
gas equation of state used wherever the fluid's compressibility departs materially from unity.  


--- PAGE 7 ---
• Reference state (for enthalpy and entropy estimation): 𝑇𝑟𝑒𝑓= 273.15 K, 𝑃𝑟𝑒𝑓= 101.325 kPa 
(standard pressure and temperature), ideal-gas state, ℎ𝑟𝑒𝑓= 0, 𝑠𝑟𝑒𝑓= 0. State this explicitly 
in the report and carry it through consistently. 
• Ammonia–water 
solution: 
Pátek 
& 
Klomfar 
(1995) 
(https://doi.org/10.1016/0140-
7007(95)00006-W) correlations for bubble/dew temperature and liquid/vapour enthalpy as 
functions of (P, x). Implement these yourself; do not use a pre-packaged absorption-cycle 
library. 
Pátek & Klomfar Model 
Bubble point (saturated liquid at pressure p, liquid mole fraction x) 
𝑇𝑏𝑢𝑏(𝑝, 𝑥) = 𝑇0 ∑𝑎𝑖(1 −𝑥)𝑚𝑖[ln (𝑝𝑜
𝑝)]
𝑛𝑖
𝑖
 
Table 1: Exponents and coefficients 
i 
𝒎𝒊 
𝒏𝒊 
𝒂𝒊 
1 
0 
0 
3.223020E+00 
2 
0 
1 
-3.842060E-01 
3 
0 
2 
4.609650E-02 
4 
0 
3 
-3.789450E-03 
5 
0 
4 
1.356100E-04 
6 
1 
0 
4.877550E-01 
7 
1 
1 
-1.201080E-01 
8 
1 
2 
1.061540E-02 
9 
2 
3 
-5.335890E-04 
10 
4 
0 
7.850410E+00 
11 
5 
0 
-1.159410E+01 
12 
5 
1 
-5.231500E-02 
13 
6 
0 
4.895960E-02 
14 
13 
1 
4.210590E-02 
𝑇𝑜= 100𝐾 and 𝑝𝑜= 2𝑀𝑃𝑎 
Dew point (saturated vapor at pressure p, vapor mole fraction y) 
𝑇𝑑𝑒𝑤(𝑝, 𝑦) = 𝑇0 ∑𝑎𝑖(1 −𝑦)
𝑚𝑖
4 [ln (𝑝𝑜
𝑝)]
𝑛𝑖
𝑖
 
Table 2: Exponents and coefficients 
i 
𝒎𝒊 
𝒏𝒊 
𝒂𝒊 
1 
0 
0 
3.240040E+00 
2 
0 
1 
-3.959200E-01 
3 
0 
2 
-4.356240E-02 
4 
0 
3 
-2.189430E-03 
5 
1 
0 
-1.435260E+00 
6 
1 
1 
1.052560E+00 
7 
1 
2 
-7.192810E-02 
8 
2 
0 
1.223620E+01 
9 
2 
1 
-2.243680E+00 


--- PAGE 8 ---
10 
3 
0 
-2.107800E+01 
11 
3 
1 
1.108340E+00 
12 
4 
0 
1.453990E+01 
13 
4 
2 
6.443120E-01 
14 
5 
0 
-2.212640E+00 
15 
5 
2 
-7.562660E-01 
16 
6 
0 
-1.355290E+00 
17 
7 
2 
1.835410E-01 
𝑇𝑜= 100𝐾 and 𝑝𝑜= 2𝑀𝑃𝑎 
• Pure ammonia (refrigerant side): a cubic real-gas equation of state: Peng–Robinson or 
Redlich–Kwong–Soave using 𝑇𝑐= 405.56 K, 𝑃𝑐= 11.333 MPa, 𝜔= 0.256, 𝑀𝑊 = 17.031 
kg/kmol. Compute ℎ(𝑇, 𝑃) and 𝑠(𝑇, 𝑃) as an ideal-gas contribution (integrate the 𝐶𝑝0 
polynomial in Table A.6 from 𝑇𝑟𝑒𝑓 ) plus the EOS departure function at the actual (T, P); the 
saturation pressure 𝑃𝑠𝑎𝑡(𝑇) is not read off a table but obtained from a generalized vapour-
pressure correlation (e.g. the Lee–Kesler/Pitzer acentric-factor correlation, using the same 
𝑇𝑐, 𝑃𝑐, 𝜔). State clearly why a real-gas EOS is appropriate here: at generator/condenser 
pressures (1–2 MPa, close to saturation) the compressibility factor of ammonia vapour departs 
several percent from 1, and the liquid phase is not ideal-gas at all. 
Lee-Kesler equation of state for simple fluids 
𝑍= 𝑃𝑟𝑣𝑟
𝑇𝑟
= 𝑎+ 𝐵
𝑣𝑟
+ 𝐶
𝑣𝑟2 + 𝐷
𝑣𝑟
5 +
𝑐4
𝑇𝑟3𝑣𝑟2 (𝛽+ 𝛾
𝑣𝑟2) exp (−𝛾
𝑣𝑟2) 
𝐵= 𝑏1 −𝑐2
𝑇𝑟
−𝑏3
𝑇𝑟2 −𝑏4
𝑇𝑟3 
𝐶= 𝑐1 −𝑐2
𝑇𝑟
+ 𝑐3
𝑇𝑟3 
𝐷= 𝑑1 + 𝑑2
𝑇𝑟
 
Where 
𝑇𝑟= 𝑇
𝑇𝑐, 𝑃𝑟= 𝑃
𝑃𝑐
, 𝑣𝑟=
𝑣
𝑅𝑇𝑐
𝑃𝑐
 
Constant 
Simple Fluids 
Constant 
Simple Fluids 
𝑏1 
0.1181193 
𝑐3 
0.0 
𝑏2 
0.265728 
𝑐4 
0.042724 
𝑏3 
0.154790 
𝑑1 × 104 
0.155488 
𝑏4 
0.030323 
𝑑2 × 104 
0.623689 
𝑐1 
0.0236744 
𝛽 
0.65392 
𝑐2 
0.0186984 
𝛾 
0.060167 
• Moist air: dry air and water vapour treated with the ideal-gas mixture relations (𝑤=
0.622𝑃𝑣/(𝑃−𝑃𝑣), ℎ= 𝐶𝑝,𝑑𝑎𝑇+ 𝑤ℎ𝑣(𝑇)), because at the pressures and temperatures of this 
problem (≈101 kPa, −5 to 45 °C) both dry air and water vapour have Z ≈ 0.999. The one place a 
real fluid correlation is required is the water-vapour saturation pressure 𝑃𝑠𝑎𝑡,𝐻2𝑂(𝑇), which will 
come from Antoine’s equation. The vapour enthalpy ℎ𝑣(𝑇) at 1 atm may be taken as ℎ𝑔 of 
saturated water vapour at that 𝑇 from CoolProp, consistent with the same 0 °C reference. 


--- PAGE 9 ---
C. District cooling network and zones 
• 400 identical zones, each 40 m² floor × 3 m height, served by chilled water at 7 °C supply / 12 
°C return. Distribution heat gain = 5 % of delivered cooling; chilled-water pump heat = 2 %. 
• Zone envelope: overall 𝑈𝐴𝑒𝑛𝑣= 80 W/K (walls, roof, glazing combined). Solar gain 1200 W 
during the day, 0 at night. 
• Internal gains: 4 occupants (75 W sensible + 55 W latent each) and 20 W/m² lighting + 
equipment (sensible). 
• AHU: supply air 𝑚̇𝑑𝑎= 0.40 kg/s dry air per zone, made up of 70 % recirculated room air and 
30 % fresh outdoor air (by dry-air mass). Cooling coil bypass factor BF = 0.15. Fan heat 
neglected. 
• Room set-point: dry-bulb held exactly at 22 °C by modulating the coil. Relative humidity must 
not exceed 75 %; the actual room humidity ratio is a result of the moisture balance, not an 
input, and must be iterated to convergence. 
• Condensate from every coil falls into a drain pan, passes through a trap, drains by gravity to a 
building riser (20 zones per riser), and is collected in a central decanter/holding tank for reuse 
D. Ambient Conditions 
Condition 
𝑻𝒅𝒃 (°C) 
RH (%) 
Solar 
Summer day 
40 
50 
on 
Summer night 
30 
50 
off 
Monsoon day 
35 
85 
on 
Monsoon night 
30 
85 
off 
Winter day 
28 
50 
on 
Winter night 
16 
50 
off 
For annual quantities assume each season lasts four months, with 12 h day / 12 h night. 
Atmospheric pressure 101.325 kPa 
2.3 Tasks 
Task – 1 Cooling and heating loads; and ammonia circuit size across the seasons 
• For each of the six conditions, solve the zone psychrometrics: outdoor state → adiabatic mixing 
(70/30) → coil (ADP and bypass factor) → supply state → room sensible and latent balances. The 
coil must deliver exactly the supply temperature required to hold 22 °C; the supply humidity 
ratio follows from the coil process; the room humidity ratio is then found by iterating the 
moisture balance until it converges. Report 𝑇𝑚𝑖𝑥, ADP, 𝑤𝑠𝑢𝑝𝑝𝑙𝑦, the resulting room RH, and flag 
any condition where the 75 % ceiling is violated and state what control action fixes it. 
ADP (Apparatus Dew Point) is the temperature a cooling coil would drive the air to if the coil had infinite 
contact area, i.e., if every bit of air actually touched the cold fins/tubes long enough to reach the coil's surface 
temperature. At that point the air would be saturated (100% RH) at the coil's effective surface temperature. 
It's called a "dew point" because it's the temperature at which the air's moisture just starts condensing out on 
the coil. 
Bypass Factor (BF) accounts for the fact that a real coil doesn't have infinite area — some fraction of the air 
slips through the coil without ever touching a cold surface, "bypassing" it. So the air leaving the coil is really a 
mix of: 
○ 
air that fully contacted the coil and left at the ADP (saturated), and 
○ 
air that bypassed the coil entirely and left unchanged at the entering (mixed) condition. 
If BF = 0.15, that means 15% of the air effectively bypasses the coil untouched, and 85% is brought all the way 
to the ADP 


--- PAGE 10 ---
BF = 𝑇𝑠𝑢𝑝𝑝𝑙𝑦−𝐴𝐷𝑃
𝑇𝑚𝑖𝑥−𝐴𝐷𝑃 
𝑤𝑠𝑢𝑝𝑝𝑙𝑦= 𝑤𝐴𝐷𝑃+ 𝐵𝐹(𝑤𝑚𝑖𝑥−𝑤𝐴𝐷𝑃) 
𝑇𝑠𝑢𝑝𝑝𝑙𝑦= 𝐴𝐷𝑃+ 𝐵𝐹(𝑇𝑚𝑖𝑥−𝐴𝐷𝑃) 
• Compute the coil load per zone (with the condensate enthalpy term), scale to the district with 
distribution and pump gains, and obtain the chiller evaporator duty 𝑄𝑒𝑣𝑎𝑝 for each condition. 
Identify the governing condition and explain why it is not the one with the highest dry-bulb 
temperature. 
• Solve the absorption cycle at each condition with 𝑇𝑐𝑜𝑛𝑑 from your Task 2 condenser (first pass: 
𝑇𝑐𝑜𝑛𝑑= 𝑇𝑑𝑏+ 12 K, then close the loop). Report 𝑄𝑔𝑒𝑛 (the heating load), COP, refrigerant mass 
flow ṁ𝑟, strong- and weak-solution concentrations and flows, circulation ratio, solution-pump 
volumetric flow, and the required flue-gas mass flow. Check that the flue-gas flow never 
exceeds 80 kg/s and that the chiller never falls below 25 % turndown; flag it where it does, 
propose possible remedy (thermal storage, chiller staging, or free cooling). 
• "Ammonia circuit size" means: ṁ𝑟, the solution pump duty (m³/h and kPa head generation), 
and the vapour volumetric flow leaving the evaporator must be estimated 
Task – 2 Condenser design for the full ambient spectrum 
• Compare two condenser types: (i) air-cooled finned-tube (approach to dry-bulb; 𝑈𝑜𝑣𝑒𝑟𝑎𝑙𝑙= 30 
W/m²·K on the finned-side area) and (ii) evaporative (approach to wet-bulb; 𝑈𝑜𝑣𝑒𝑟𝑎𝑙𝑙= 600 
W/m²·K on wetted tube area, cycles of concentration 4). Compute the wet-bulb temperature 
of each condition from your own ideal-gas psychrometric relations (iterate the adiabatic-
saturation energy balance to 𝑇𝑤𝑏 using CoolProp only for 𝑃𝑠𝑎𝑡,𝐻2𝑂 and ℎ𝑔,𝐻2𝑂) and identify 
which condition governs each type. 
• For your chosen type, fix the design point at the governing condition with a stated approach 
(e.g., 12 K to dry-bulb or 8 K to wet-bulb), compute 𝑄𝑐𝑜𝑛𝑑 from the cycle, the LMTD, the required 
UA, the heat-transfer area, and the air or water flow. 
• Off-design: holding UA fixed, solve for the condensing temperature at the other five conditions 
by iterating between the cycle model and the condenser energy balance. Show the resulting 
𝑇𝑐𝑜𝑛𝑑, 𝑃ℎ𝑖𝑔ℎ, generator temperature and COP for all six conditions. 
• Verify at every condition that (a) 𝑃ℎ𝑖𝑔ℎ≤20 bar (vessel design pressure), (b) 𝑇𝑔𝑒𝑛 required at 
that P_high is deliverable by 300 °C flue gas with 𝜀𝑔𝑒𝑛= 0.75 and the 140 °C floor, and (c) 
𝑇𝑐𝑜𝑛𝑑≥25 °C so the expansion valve retains adequate pressure differential. Flag where (c) 
fails at low ambient 
Task – 3 Water decanter (condensate) system 
Condensate rate per zone and for the district at every condition (kg/h and m³/day). Identify the 
governing condition for the decanter and explain why it differs from the chiller's governing 
condition. 
Task – 4 Sensitivity to fresh-air fraction: 30 % → 40 % 
• Re-run Tasks 1 and 3 with 40 % fresh air. Tabulate, for each condition, the percentage change 
in coil load, 𝑄̇𝑒𝑣𝑎𝑝, 𝑄̇𝑔𝑒𝑛 , ṁ𝑟, flue-gas flow and condensate rate. 
• Explain physically why the monsoon conditions are the most sensitive, and why the winter-
night change is small. 
• Check whether the 75 % RH ceiling still holds at monsoon night with 40 % fresh air. If it does 
not, quantify the lower ADP (and any reheat) needed and the resulting extra generator heat. 


--- PAGE 11 ---
• State whether the 80 kg/s flue-gas limit or the 20 bar vessel limit becomes active anywhere 
with 40 % fresh air 
2.4 Required Validation Test Case 
Before any design results are accepted, each group must show that their code reproduces the 
following hand-traceable checks. The three checks are independent so that a discrepancy points 
to an error in the solver. 
Check – 1 Psychrometric mixing (moist-air routine) 
Given: 70 % room air at 22 °C, 75 % RH mixed adiabatically with 30 % outdoor air at 40 °C, 50 % 
RH, 𝑃= 101.325 kPa. Hand values use 𝑃𝑠𝑎𝑡,𝐻2𝑂 from CoolProp (matches Table B.1.1 to 4 figures: 
40 °C exact; 22 °C ≈ 2.645 kPa), 𝑤 = 0.622𝑃𝑣/(𝑃−𝑃𝑣) and ℎ= 1.006𝑇+ 𝑤(2501 + 1.86𝑇), 
consistent with the 0 °C ideal-gas reference. 
State 
𝑷𝒗 (kPa) 
w (kg/kg da) 
h (kJ/kg da) 
T (oC) 
Room, 22 oC/75% RH 
1.984 
0.01242 
53.71 
22 
Outdoor, 40 oC/50% RH 
3.692 
0.02352 
100.82 
40 
Mixed (0.7/0.3) 
 
0.01575 
67.84 
27.48 
Match these to within 0.5 % for 𝑤 and ℎ and 0.1 K for 𝑇. The tolerance is tight because ideal-gas 
mixing at this pressure should have no model error; a larger gap is a units or root-finding bug, not 
"real-gas correction." Also report 𝑇𝑤𝑏 for the summer-day and monsoon-day outdoor states 
(expected around 30.3 °C and 32.6 °C from the adiabatic-saturation iteration). 
Check – 2 Ammonia real-gas EOS vs. Table B.2.1 
Given: saturated ammonia at 0 °C and 40 °C (chosen to land on tabulated rows). Compute 𝑃𝑠𝑎𝑡(𝑇) 
from your generalized vapour-pressure correlation and ℎ𝑓𝑔(𝑇) from the EOS departure functions. 
𝑃𝑠𝑎𝑡 and ℎ𝑓𝑔 are reference-independent, so they can be checked directly against the table; ℎ𝑓 and 
ℎ𝑔 depend on the 0 °C/101.325 kPa ideal-gas reference that was given in Section B and are not 
expected to equal the table's own (different) reference. 
Quantity 
0 °C 
40 °C 
Table B.2.1 
𝑃𝑠𝑎𝑡 (kPa) 
424–430 
1550–1570 
429.6 / 1554.9 
ℎ𝑓𝑔 (kJ/kg) 
1260–1300 
1090–1150 
1261.8 / 1098.8 
A Peng–Robinson EOS with the Lee–Kesler/Pitzer vapour-pressure correlation and the critical 
constants above reproduces 𝑃𝑠𝑎𝑡 to within about 1.2 % and ℎ𝑓𝑔 to within about 3–4 % of the table.  
This is the genuine, expected accuracy of a cubic EOS with generalized correlations for a polar, 
hydrogen-bonding fluid like ammonia, not numerical error. Report your own percentage deviation 
and discuss it: it is a legitimate finding, not a bug, provided it falls within roughly ±5 % on 𝑃𝑠𝑎𝑡 and 
±8 % on ℎ𝑓𝑔. A deviation far outside that band (wrong sign, order of magnitude, or a value that 
doesn't decrease appropriately with T) does indicate an implementation error. 
• Refrigerating effect: 𝑞𝑒= ℎ𝑔(0 °𝐶,𝑒𝑣𝑎𝑝) −ℎ𝑓(40 °𝐶,𝑐𝑜𝑛𝑑). Because both terms share the same 
reference, the difference 𝑞𝑒 must still match ℎ𝑓𝑔-based expectations: 𝑞𝑒≈1050 −1100 
kJ/kg. 
• For 𝑄𝑒𝑣𝑎𝑝= 5000 kW: expected ṁ𝑟≈4.5 −4.8 kg/s. Report your own value and compare. 
Check – 3 Absorption-cycle balances (no external tables needed) 
At any operating point the code produces, the following must hold: 


--- PAGE 12 ---
𝑄𝑔𝑒𝑛+ 𝑄𝑒𝑣𝑎𝑝+ 𝑊𝑝𝑢𝑚𝑝= 𝑄𝑐𝑜𝑛𝑑+ 𝑄𝑎𝑏𝑠+ 𝑄𝑟𝑒𝑐𝑡  
ṁ𝑠𝑡𝑟𝑜𝑛𝑔𝑥𝑠𝑡𝑟𝑜𝑛𝑔= ṁ𝑤𝑒𝑎𝑘𝑥𝑤𝑒𝑎𝑘+ ṁ𝑟𝑥𝑟 
𝐶𝑂𝑃< 𝐶𝑂𝑃𝑟𝑒𝑣= [
𝑇𝑒𝑣𝑎𝑝
𝑇𝑐𝑜𝑛𝑑−𝑇𝑒𝑣𝑎𝑝
][𝑇𝑔𝑒𝑛−𝑇𝑎𝑏𝑠
𝑇𝑔𝑒𝑛
] 
For 𝑇𝑒𝑣𝑎𝑝= 2 °C, 𝑇𝑐𝑜𝑛𝑑= 𝑇𝑎𝑏𝑠= 45 °C, 𝑇𝑔𝑒𝑛= 130 °C the reversible bound is ≈ 1.35; the actual 
COP of a single-effect NH₃–H₂O machine is expected to be range between 0.45–0.65. A COP 
outside this band, or one that rises with condensing temperature, indicates a sign or property-
reference error. 
Reporting requirement 
Each report must include a Validation Table with columns Quantity | Hand value | Code output | 
% difference | Pass/Fail covering every quantity in Checks 1–3, plus a test_validation.py in the 
repository that asserts the same tolerances automatically. 
2.5 Deliverables 
Python repository with README of all the codes, requirements, the Pátek–Klomfar 
implementation as a separate tested module, and a single reproducible driver script. 
A ppt giving the following: 
# 
Section 
Required content 
1 
Schematic 
Two labelled diagrams: (a) the absorption cycle with all state 
points numbered — generator, rectifier, condenser, valve, 
evaporator, absorber, pump, SHX, weak-solution throttle — and 
the flue-gas and cooling-medium streams; (b) one zone AHU 
showing return, fresh-air, mixing, coil, drain pan/trap and supply, 
with the psychrometric state points numbered. Both numbering 
schemes must be used consistently in every equation and table 
that follows. 
2 
Algorithm 
Flowchart or structured pseudocode: the room-humidity 
iteration, the coil ADP/bypass solution, the Pátek–Klomfar 
property calls, the cycle solution sequence. 
3 
Analysis 
Validation table; psychrometric chart with all six mixing/coil 
processes drawn; seasonal tables for Tasks 1–3; condenser type 
comparison and off-design map; the 40 % fresh-air sensitivity 
(Task 4). 
4 
Conclusion 
One page: the governing condition for each component (chiller, 
condenser, decanter), the recommended condenser type and 
size, the flue-gas demand envelope over the year, the response to 
40 % fresh air, and the single biggest design lever. 
 


--- PAGE 13 ---
2.6 Grading Rubric 
Criterion 
Weight 
Psychrometric and cycle model fidelity (own ideal-gas moist-air relations, own 
ammonia real-gas EOS, own Pátek–Klomfar, correct room-humidity iteration, 
correct condensate enthalpy term) 
25 
Validation (all 3 checks within tolerance, reference-state shift shown) 
20 
Seasonal 
load/heating-load/circuit-size 
results 
and 
governing-condition 
reasoning (Task 1) 
15 
Condenser design and off-design map with all three feasibility checks (Task 2) 
10 
Decanter sizing and fresh-air sensitivity (Tasks 3–4) 
10 
Report and presentation 
20 
 




# ME3160 Project 1: Support Material

--- PAGE 1 ---
ME3160 — Power & Refrigeration Cycles 
Project 1 Support Material 
Surrogate-Assisted Optimization of a Methane-Fired Combined Cycle 
1. What Are You Doing? 
You are building a physics model of a combined-cycle plant (Brayton topping cycle + HRSG + Rankine bottoming 
cycle), then finding the setting of five design variables — rp, TIT, Ps, Ts, Pcond — that maximizes overall 
efficiency without violating any of the six constraints in §1.4. The physics itself is fully specified in the problem 
statement; this document focuses on the optimization/ML pipeline layered on top of it (Parts B and C). 
2. Why Are You Doing It This Way? 
Your physics model (Part A) is expensive: every call solves a full variable-Cp Brayton cycle, an HRSG pinch 
analysis, and a CoolProp-based Rankine cycle. A brute-force grid search over all 5 design variables makes that 
cost explode. 
Grid search: 20 points per variable, 5 variables → 20⁵ = 3,200,000 evaluations. 
This pipeline: Latin Hypercube Sampling → 300–500 evaluations total — roughly 6,000× fewer. 
Illustration only (not required in your report): if one physics evaluation takes ~0.3 s, a full grid search is ~11 
days of continuous compute. LHS + surrogates finishes the same job in under 3 minutes of expensive-model 
time. 
That's the whole point of Parts B and C: sample the expensive model a few hundred times, fit a cheap stand-in 
(surrogate) to those samples, search the cheap surrogate as much as you like, and only go back to the expensive 
model to double-check the final answer. 
3. Pipeline at a Glance 
Part A — Build and validate the physics model. 
Variable-Cp, validated against the three hand-calculable checks in §1.7. Everything below treats this as a 
finished, trustworthy black box. 
Part B — Turn the expensive model into a cheap one. 
Sample the design space (LHS), then fit ONE surrogate — your choice of a quadratic Response Surface (RSM) or a 
small Neural Network (ANN), not both — and analyse it on held-out data. 
Part C — Optimize the cheap model, then verify. 
Optimize your surrogate with a Genetic Algorithm (pymoo/DEAP), re-check the winner against the real physics 
model, refine if it disagrees, run a sensitivity study, and produce a Pareto front (ηcc vs. net power) instead of a 
single answer. 
 
 


--- PAGE 2 ---
4. Pipeline Flow Chart 
Follow it top to bottom; the two loops (fail-validation, and adaptive refinement) are the only places you circle 
back. 
 
 
 


--- PAGE 3 ---
5. Step-by-Step Pseudocode 
This is structural pseudocode — it shows what goes into each stage and what comes out, not working 
thermodynamics. Every block assumes you already have the validated Part A model. 
Physical Model — treated as a black box 
You already built and validated this in Part A. Nothing below re-derives it — every later step just calls it. 
direct_model(rp, TIT, Ps, Ts, Pcond)  →  eta_cc, Wnet, margins, feasible 
Internally: variable-Cp Brayton cycle → HRSG pinch analysis → CoolProp Rankine cycle. You know this part 
— it's Part A. 
Step 1 — Design of Experiments — Latin Hypercube Sampling (Part B) 
INPUTS  →  bounds for the 5 design variables; the direct_model() black box; number of samples N (≥300, 500 
recommended). 
from scipy.stats import qmc 
  
sampler = qmc.LatinHypercube(d=5, seed=SEED) 
unit_samples = sampler.random(n=500) 
X = qmc.scale(unit_samples, l_bounds, u_bounds)   # scale to real engineering units 
  
records = [] 
for x in X: 
    eta_cc, Wnet, margins, feasible = direct_model(*x) 
    records.append({'x': x, 'eta_cc': eta_cc, 'Wnet': Wnet, 
                     'margins': margins, 'feasible': feasible}) 
df = to_dataframe(records)   # KEEP infeasible rows -- label them, do not drop 
OUTPUT  →  df — one row per sampled design, with ηcc, Ẇnet, all 6 constraint margins, and a feasible flag (infeasible rows 
kept and labelled). 
Step 2 — Fit YOUR surrogate — choose RSM or ANN, not both 
INPUTS  →  df from Step 1 — the design-variable columns (X) and the eta_cc column (plus the binding constraint-margin 
columns). 
Implement ONE of these two options. Both are shown here only so you can pick whichever fits your group's background — 
the project asks for a single surrogate. 
Option A — Response Surface (RSM) + ANOVA 
import statsmodels.api as sm 
from statsmodels.formula.api import ols 
  
formula = 'eta_cc ~ (rp + TIT + Ps + Ts + Pcond)**2 + ' \ 
          'I(rp**2) + I(TIT**2) + I(Ps**2) + I(Ts**2) + I(Pcond**2)' 
rsm_model = ols(formula, data=df_feasible).fit() 
anova_table = sm.stats.anova_lm(rsm_model, typ=2) 
  
rsm_margin_models = {c: ols(f'{c} ~ ...same formula...', data=df).fit() 
                     for c in binding_constraints} 


--- PAGE 4 ---
Option B — Neural Network (ANN) 
from sklearn.neural_network import MLPRegressor 
from sklearn.preprocessing import StandardScaler 
from sklearn.model_selection import train_test_split, GridSearchCV 
  
X_train, X_test, y_train, y_test = train_test_split(X, eta_cc, test_size=0.2, 
random_state=SEED) 
scaler = StandardScaler().fit(X_train) 
Xs_train, Xs_test = scaler.transform(X_train), scaler.transform(X_test) 
  
param_grid = {'hidden_layer_sizes': [(10,10), (20,10), (20,20)], 
              'activation': ['tanh', 'relu'], 'alpha': [1e-4, 1e-3, 1e-2]} 
search = GridSearchCV(MLPRegressor(max_iter=5000, random_state=SEED), 
                       param_grid, cv=5, scoring='r2') 
search.fit(Xs_train, y_train) 
ann_model = search.best_estimator_ 
OUTPUT  →  surrogate_model — your fitted RSM or ANN, callable to predict ηcc (and the binding constraint margins) at any 
x. 
Step 3 — Analyse your surrogate on held-out data 
INPUTS  →  surrogate_model from Step 2, and the held-out X_test / y_test (for ANN, your 20% split; for RSM, a held-out 
subset you set aside the same way). 
from sklearn.metrics import r2_score, mean_squared_error 
  
y_pred = surrogate_predict(X_test) 
r2   = r2_score(y_test, y_pred) 
rmse = mean_squared_error(y_test, y_pred, squared=False) 
plot_parity(y_test, y_pred, title=f'R2={r2:.3f}, RMSE={rmse:.4f}') 
# look specifically near the HRSG-inlet / pinch boundary -- a quadratic RSM 
# should show visible bias there; discuss why, whichever surrogate you used 
OUTPUT  →  R², RMSE, and a parity plot — feeds directly into your report's surrogate-quality discussion (where and why it 
fails). 
Step 4 — Optimize the surrogate with a Genetic Algorithm (Part C) 
INPUTS  →  surrogate_model as a callable prediction function, plus the bounds and constraint-margin functions from Step 1. 
from pymoo.algorithms.soo.nonconvex.ga import GA 
from pymoo.optimize import minimize as pymoo_minimize 
  
problem = CombinedCycleProblem(surrogate_predict, surrogate_margin_fn, bounds) 
res = pymoo_minimize(problem, GA(pop_size=100), ('n_gen', 200), seed=SEED) 
  
best_candidate = CandidateResult(x=res.X, eta=-res.F[0])   # pymoo minimizes, 
                                                            # so negate eta_cc 
OUTPUT  →  best_candidate — the GA's best feasible design (x*, surrogate-predicted ηcc). 
Step 5 — Direct-model verification & adaptive refinement 
INPUTS  →  best_candidate.x from Step 4, and the direct_model() black box. 


--- PAGE 5 ---
eta_direct, Wnet_direct, margins, feasible = direct_model(*best_candidate.x) 
gap = best_candidate.eta - eta_direct 
  
iteration = 0 
while abs(gap) > 0.002 and iteration < MAX_REFINEMENTS:     # 0.2 percentage points 
    new_points = latin_hypercube_around(best_candidate.x, radius=trust_region, n=50) 
    new_records = [direct_model(*pt) for pt in new_points] 
    df = df.append(new_records) 
    refit_surrogate()      # refit your RSM or ANN on the augmented df 
    best_candidate = re_optimize_with_ga() 
    eta_direct, Wnet_direct, margins, feasible = direct_model(*best_candidate.x) 
    gap = best_candidate.eta - eta_direct 
    iteration += 1 
OUTPUT  →  final_design — a design whose surrogate-predicted ηcc has been confirmed against the real physics model to 
within 0.2 pp. 
Step 6 — Sensitivity study 
INPUTS  →  the full Steps 1–5 pipeline, re-run once per HRSG-inlet limit. 
for hrsg_limit_C in [600, 650, 700]: 
    set_constraint_ii_limit(hrsg_limit_C) 
    result = repeat_optimization_pipeline() 
    record(hrsg_limit_C, result.x_star, result.eta_cc, result.active_constraints) 
  
# which constraints are active at each limit? where would loosening a material 
# limit buy the most efficiency? -> that's where materials R&D $ should go 
OUTPUT  →  a table of (limit, x*, ηcc, active constraints) used to argue where materials investment matters most. 
Step 7 — Bi-objective Pareto front (ηcc vs. net power) 
INPUTS  →  bounds, constraint-margin function, and ηcc / Ẇnet predictions (surrogate or direct — state which you use). 
from pymoo.algorithms.moo.nsga2 import NSGA2 
  
class BiObjectiveProblem(Problem): 
    def _evaluate(self, X, out): 
        eta = np.array([eta_fn(x) for x in X]) 
        Wnet = np.array([wnet_fn(x) for x in X]) 
        out['F'] = np.column_stack([-eta, -Wnet])       # maximize both -> minimize 
negatives 
        out['G'] = np.array([constraint_margins_vec(x) for x in X]) * -1  # pymoo: G<=0 
feasible 
  
res = pymoo_minimize(BiObjectiveProblem(), NSGA2(pop_size=100), ('n_gen', 200), seed=SEED) 
pareto_front = res.F, res.X 
plot_pareto(pareto_front, mark_point=final_design) 
OUTPUT  →  pareto_front — the set of non-dominated designs to plot, with the single-objective optimum marked on it. 
 
 


--- PAGE 6 ---
6. Resources — Surrogate Modelling & Optimization 
Videos build intuition; the documentation is what you actually code against. 
Topic 
YouTube video 
Documentation 
Latin 
Hypercube 
Sampling 
(DOE) 
Random Sampling Tutorial 4 — 
Latin Hypercube Sampling 
youtube.com/watch?v=H0RZ1uez
uuw 
scipy.stats.qmc.LatinHypercube 
docs.scipy.org/doc/scipy/reference/generated/scipy.stats.qmc.LatinHyper
cube.html 
Response 
Surface 
Methodolo
gy + 
ANOVA 
RSM: Introduction to Response 
Surface Methodology 
youtube.com/watch?v=ERSWvYy
bOrk 
statsmodels anova_lm 
statsmodels.org/devel/generated/statsmodels.stats.anova.anova_lm.html 
Neural 
network 
intuition 
But what is a neural network? — 
3Blue1Brown 
youtube.com/watch?v=aircAruvn
Kk 
scikit-learn MLPRegressor guide scikit-
learn.org/stable/modules/neural_networks_supervised.html 
Genetic 
Algorithms 
The Knapsack Problem & Genetic 
Algorithms — Computerphile 
youtube.com/watch?v=MacVqujS
XWE 
pymoo documentation & tutorials pymoo.org 
Pareto 
fronts / bi-
objective 
optimizatio
n 
Multiobjective optimization & the 
Pareto front 
youtube.com/watch?v=act0oZoV
3RA 
pymoo — Multi-Objective Optimization (NSGA-II) pymoo.org 
Steam 
properties 
(Rankine 
side) 
— 
CoolProp High-Level Interface (PropsSI) 
coolprop.org/coolprop/HighLevelAPI.html 
Note: RSM and GA tutorials online skew toward manufacturing/Minitab examples rather than Python. Use them for the 
concept, and use Section 5 to bridge to actual scipy/statsmodels/scikit-learn/pymoo code. 


