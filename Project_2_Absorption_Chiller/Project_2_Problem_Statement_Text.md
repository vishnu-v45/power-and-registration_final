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
 


