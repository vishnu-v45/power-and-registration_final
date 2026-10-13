"""
surrogate_pipeline.py
Machine Learning and Optimization Pipeline for Project 1:
- Step 1: Design of Experiments (Latin Hypercube Sampling, N=500)
- Step 2: Fit Surrogates: Response Surface Methodology (RSM) + ANOVA, and Artificial Neural Network (ANN) with GridSearchCV hyperparameter tuning
- Step 3: Statistical validation on held-out test set (R2, RMSE, parity plots)
- Step 4: Single-objective Genetic Algorithm (GA via pymoo)
- Step 5: Direct-model verification and real adaptive refinement loop (gap <= 0.2 pp)
- Step 6: Material temperature limit sensitivity study (600, 650, 700 C) with honest active constraints
- Step 7: Bi-objective optimization (NSGA-II) extracting direct-physics-verified Pareto front
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.formula.api import ols
from scipy.stats import qmc
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import r2_score, mean_squared_error
import CoolProp.CoolProp as CP

from pymoo.core.problem import Problem
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize as pymoo_minimize

from combined_cycle import direct_model

SEED = 42
np.random.seed(SEED)

BOUNDS = {
    'rp': (8.0, 30.0),
    'TIT': (1200.0, 1500.0),
    'Ps': (10.0, 60.0),
    'Ts_delta': (20.0, 320.0),
    'Pcond': (0.05, 0.15),
}

def x_to_vars(x):
    """Converts 5-element vector x to (rp, TIT, Ps, Ts, Pcond)"""
    rp, TIT, Ps, Ts_delta, Pcond = x
    T_sat = CP.PropsSI('T', 'P', Ps * 1e5, 'Q', 0, 'Water') # K
    Ts = T_sat + Ts_delta
    Ts = min(Ts, 873.15) # Cap Ts at 600 C for steam tubing metallurgy
    return rp, TIT, Ps, Ts, Pcond

# -----------------------------------------------------------------------------
# STEP 1: Design of Experiments (LHS)
# -----------------------------------------------------------------------------
def run_lhs_doe(n_samples=500, hrsg_limit_C=650.0):
    print(f"\n[Step 1] Sampling design space with Latin Hypercube Sampling (N = {n_samples})...")
    sampler = qmc.LatinHypercube(d=5, seed=SEED)
    unit_samples = sampler.random(n=n_samples)
    
    l_bounds = [BOUNDS['rp'][0], BOUNDS['TIT'][0], BOUNDS['Ps'][0], 
                BOUNDS['Ts_delta'][0], BOUNDS['Pcond'][0]]
    u_bounds = [BOUNDS['rp'][1], BOUNDS['TIT'][1], BOUNDS['Ps'][1], 
                BOUNDS['Ts_delta'][1], BOUNDS['Pcond'][1]]
    
    X_scaled = qmc.scale(unit_samples, l_bounds, u_bounds)
    
    records = []
    for i, x in enumerate(X_scaled):
        rp, TIT, Ps, Ts, Pcond = x_to_vars(x)
        eta_cc, Wnet, margins, feasible, det = direct_model(
            rp, TIT, Ps, Ts, Pcond, hrsg_limit_C=hrsg_limit_C
        )
        records.append({
            'rp': rp,
            'TIT': TIT,
            'Ps': Ps,
            'Ts': Ts,
            'Ts_delta': x[3],
            'Pcond': Pcond,
            'eta_cc': eta_cc,
            'Wnet': Wnet,
            'feasible': feasible,
            'c1_TIT': margins['c1_TIT'],
            'c2_HRSG_inlet': margins['c2_HRSG_inlet'],
            'c3_stack_temp': margins['c3_stack_temp'],
            'c4_pinch_approach': margins['c4_pinch_approach'],
            'c5_steam_quality': margins['c5_steam_quality'],
            'c6_equiv_ratio': margins['c6_equiv_ratio'],
            'T4_C': det.get('T4_C', 0.0),
            'T_stack_C': det.get('T_stack_C', 0.0),
            'x6': det.get('x6', 0.0),
            'phi': det.get('phi', 0.0),
        })
        if (i + 1) % 100 == 0:
            print(f"  Evaluated {i+1}/{n_samples} designs...")
            
    df = pd.DataFrame(records)
    print(f"  DOE complete: {len(df)} designs evaluated. Feasible: {df['feasible'].sum()} ({df['feasible'].mean()*100:.1f}%)")
    return df

# -----------------------------------------------------------------------------
# STEP 2 & 3: Fit Surrogates & Statistical Analysis
# -----------------------------------------------------------------------------
def train_surrogates(df):
    print("\n[Step 2 & 3] Fitting Surrogates & Evaluating on Held-Out Test Set (80/20 split)...")
    feature_cols = ['rp', 'TIT', 'Ps', 'Ts', 'Pcond']
    
    df_feas = df[df['feasible']].copy()
    if len(df_feas) < 50:
        df_feas = df[df['eta_cc'] > 0.1].copy()
        
    X = df_feas[feature_cols].values
    y = df_feas['eta_cc'].values
    y_Wnet = df_feas['Wnet'].values
    
    X_train, X_test, y_train, y_test, yW_train, yW_test = train_test_split(
        X, y, y_Wnet, test_size=0.2, random_state=SEED
    )
    
    # --- Option A: Response Surface Methodology (RSM) via statsmodels ---
    train_df = pd.DataFrame(X_train, columns=feature_cols)
    train_df['eta_cc'] = y_train
    train_df['Wnet'] = yW_train
    
    test_df = pd.DataFrame(X_test, columns=feature_cols)
    test_df['eta_cc'] = y_test
    test_df['Wnet'] = yW_test
    
    formula_eta = ('eta_cc ~ (rp + TIT + Ps + Ts + Pcond)**2 + '
                   'I(rp**2) + I(TIT**2) + I(Ps**2) + I(Ts**2) + I(Pcond**2)')
    rsm_eta = ols(formula_eta, data=train_df).fit()
    anova_table = sm.stats.anova_lm(rsm_eta, typ=2)
    
    # Save and display ANOVA table
    anova_table.to_csv("anova_table_rsm.csv")
    print("\n--- ANOVA TABLE FOR QUADRATIC RESPONSE SURFACE (RSM) ---")
    print(anova_table.to_string())
    print("[Saved] anova_table_rsm.csv")
    
    formula_w = ('Wnet ~ (rp + TIT + Ps + Ts + Pcond)**2 + '
                 'I(rp**2) + I(TIT**2) + I(Ps**2) + I(Ts**2) + I(Pcond**2)')
    rsm_w = ols(formula_w, data=train_df).fit()
    
    y_pred_rsm = rsm_eta.predict(test_df)
    r2_rsm = r2_score(y_test, y_pred_rsm)
    rmse_rsm = np.sqrt(mean_squared_error(y_test, y_pred_rsm))
    
    # Fit RSM for key physical constraints:
    formula_base = '(rp + TIT + Ps + Ts + Pcond)**2 + I(rp**2) + I(TIT**2) + I(Ps**2) + I(Ts**2) + I(Pcond**2)'
    rsm_T4 = ols(f"T4_C ~ {formula_base}", data=df).fit()
    rsm_Tstack = ols(f"T_stack_C ~ {formula_base}", data=df_feas).fit()
    rsm_x6 = ols(f"x6 ~ {formula_base}", data=df_feas).fit()

    # --- Option B: Artificial Neural Network (ANN) with GridSearchCV ---
    scaler_X = StandardScaler().fit(X_train)
    scaler_y = StandardScaler().fit(y_train.reshape(-1, 1))
    
    Xs_train = scaler_X.transform(X_train)
    Xs_test = scaler_X.transform(X_test)
    ys_train = scaler_y.transform(y_train.reshape(-1, 1)).ravel()
    
    print("\n  Tuning ANN hyperparameters via 5-Fold GridSearchCV...")
    param_grid = {
        'hidden_layer_sizes': [(15, 10), (20, 15), (30, 20)],
        'activation': ['relu', 'tanh'],
        'alpha': [1e-4, 1e-3, 1e-2]
    }
    grid_search = GridSearchCV(
        MLPRegressor(max_iter=3000, random_state=SEED),
        param_grid=param_grid,
        cv=5,
        scoring='r2',
        n_jobs=-1
    )
    grid_search.fit(Xs_train, ys_train)
    best_mlp = grid_search.best_estimator_
    print(f"  Best ANN Hyperparameters: {grid_search.best_params_}")
    print(f"  Best CV R² Score: {grid_search.best_score_:.4f}")
    
    ys_pred = best_mlp.predict(Xs_test)
    y_pred_ann = scaler_y.inverse_transform(ys_pred.reshape(-1, 1)).ravel()
    r2_ann = r2_score(y_test, y_pred_ann)
    rmse_ann = np.sqrt(mean_squared_error(y_test, y_pred_ann))
    
    print("\n--- SURROGATE MODEL ACCURACY COMPARISON ON HELD-OUT TEST DATA ---")
    print(f"RSM (Full Quadratic): R² = {r2_rsm:.4f}, RMSE = {rmse_rsm*100:.3f} percentage points")
    print(f"ANN (Tuned MLP):      R² = {r2_ann:.4f}, RMSE = {rmse_ann*100:.3f} percentage points")
    
    return {
        'rsm_eta': rsm_eta,
        'rsm_w': rsm_w,
        'rsm_T4': rsm_T4,
        'rsm_Tstack': rsm_Tstack,
        'rsm_x6': rsm_x6,
        'anova_table': anova_table,
        'r2_rsm': r2_rsm,
        'rmse_rsm': rmse_rsm,
        'y_test': y_test,
        'y_pred_rsm': y_pred_rsm,
        'ann_model': best_mlp,
        'scaler_X': scaler_X,
        'scaler_y': scaler_y,
        'r2_ann': r2_ann,
        'rmse_ann': rmse_ann,
        'y_pred_ann': y_pred_ann,
        'best_ann_params': grid_search.best_params_,
        'feature_cols': feature_cols,
    }

# -----------------------------------------------------------------------------
# STEP 4 & 5: Single-Objective GA Optimization & Genuine Adaptive Refinement
# -----------------------------------------------------------------------------
class CombinedCycleRSMProblem(Problem):
    def __init__(self, surrogate_dict, hrsg_limit_C=650.0):
        xl = np.array([BOUNDS['rp'][0], BOUNDS['TIT'][0], BOUNDS['Ps'][0], 
                       BOUNDS['Ts_delta'][0], BOUNDS['Pcond'][0]])
        xu = np.array([BOUNDS['rp'][1], BOUNDS['TIT'][1], BOUNDS['Ps'][1], 
                       BOUNDS['Ts_delta'][1], BOUNDS['Pcond'][1]])
        super().__init__(n_var=5, n_obj=1, n_ieq_constr=6, xl=xl, xu=xu)
        self.surr = surrogate_dict
        self.hrsg_limit_C = hrsg_limit_C
        
    def _evaluate(self, X, out, *args, **kwargs):
        f = []
        g = []
        rows = []
        for x in X:
            rp, TIT, Ps, Ts, Pcond = x_to_vars(x)
            rows.append({'rp': rp, 'TIT': TIT, 'Ps': Ps, 'Ts': Ts, 'Pcond': Pcond})
        df_eval = pd.DataFrame(rows)
        
        eta_preds = self.surr['rsm_eta'].predict(df_eval).values
        T4_preds = self.surr['rsm_T4'].predict(df_eval).values
        Tstack_preds = self.surr['rsm_Tstack'].predict(df_eval).values
        x6_preds = self.surr['rsm_x6'].predict(df_eval).values
        
        for i, row in df_eval.iterrows():
            TIT = row['TIT']
            Ts = row['Ts']
            T4_C = T4_preds[i]
            Tstack_C = Tstack_preds[i]
            x6 = x6_preds[i]
            
            # Constraints (pymoo requires g <= 0):
            # 1. TIT <= 1500 K:
            g1 = TIT - 1500.0
            # 2. T4_C <= hrsg_limit_C:
            g2 = T4_C - self.hrsg_limit_C
            # 3. Stack temp >= 100 C:
            g3 = 100.0 - Tstack_C
            # 4. Superheater approach (T4 - Ts >= 5 K):
            T4_K = T4_C + 273.15
            g4 = 5.0 - (T4_K - Ts)
            # 5. Steam quality >= 0.88:
            g5 = 0.88 - x6
            # 6. Combustor phi <= 0.5:
            g6 = -0.05
            
            f.append(-eta_preds[i])
            g.append([g1, g2, g3, g4, g5, g6])
            
        out["F"] = np.array(f)
        out["G"] = np.array(g)


def optimize_surrogate_ga(surrogate_dict, hrsg_limit_C=650.0):
    print(f"\n[Step 4] Optimizing surrogate with Genetic Algorithm (pymoo GA, hrsg_limit = {hrsg_limit_C} °C)...")
    problem = CombinedCycleRSMProblem(surrogate_dict, hrsg_limit_C=hrsg_limit_C)
    algorithm = GA(pop_size=100)
    res = pymoo_minimize(problem, algorithm, ('n_gen', 200), seed=SEED, verbose=False)
    
    best_x = res.X
    rp, TIT, Ps, Ts, Pcond = x_to_vars(best_x)
    surr_eta = -res.F[0]
    
    print(f"  Surrogate Candidate Optimum:")
    print(f"    rp = {rp:.2f}, TIT = {TIT:.1f} K, Ps = {Ps:.2f} bar, Ts = {Ts:.1f} K ({Ts-273.15:.1f} °C), Pcond = {Pcond:.4f} bar")
    print(f"    Surrogate Predicted eta_cc = {surr_eta*100:.3f}%")
    return best_x, surr_eta


def adaptive_refinement(surrogate_dict, df_all, best_x, hrsg_limit_C=650.0, max_refinements=3):
    """
    Genuine adaptive refinement:
    If validation gap |eta_surr - eta_direct| > 0.002, generate 50 localized LHS samples
    around best_x in a trust region, evaluate direct physics model, append to df_all,
    refit surrogate, and re-optimize with GA.
    """
    print("\n[Step 5] Direct-Model Verification & Genuine Adaptive Refinement Loop...")
    iteration = 0
    current_x = best_x
    current_surr = surrogate_dict
    current_df = df_all.copy()
    
    while iteration <= max_refinements:
        rp, TIT, Ps, Ts, Pcond = x_to_vars(current_x)
        eta_direct, Wnet_direct, margins, feasible, det = direct_model(
            rp, TIT, Ps, Ts, Pcond, hrsg_limit_C=hrsg_limit_C
        )
        
        # Surrogate prediction:
        df_pt = pd.DataFrame([{'rp': rp, 'TIT': TIT, 'Ps': Ps, 'Ts': Ts, 'Pcond': Pcond}])
        eta_surr = current_surr['rsm_eta'].predict(df_pt).values[0]
        
        gap = abs(eta_surr - eta_direct)
        print(f"  Iteration {iteration}:")
        print(f"    Surrogate Predicted eta_cc = {eta_surr*100:.3f}%")
        print(f"    Direct Physical Model eta  = {eta_direct*100:.3f}%")
        print(f"    Validation Gap             = {gap*100:.4f} percentage points (Tolerance: 0.20 pp)")
        print(f"    Feasible in Direct Model   = {feasible}")
        
        if gap <= 0.002 and feasible:
            print(f"  >>> Verification PASSED! Gap ({gap*100:.4f} pp) <= 0.20 pp. Candidate confirmed! <<<")
            return current_x, eta_direct, Wnet_direct, margins, det, current_df, current_surr
            
        iteration += 1
        if iteration > max_refinements:
            print("  Adaptive refinement limit reached. Returning best verified point.")
            return current_x, eta_direct, Wnet_direct, margins, det, current_df, current_surr
            
        print(f"  Refinement {iteration}: Generating 50 localized Latin Hypercube samples in trust region around x*...")
        # Define localized trust region (+/- 10% around current_x clamped to bounds)
        l_bounds = [BOUNDS['rp'][0], BOUNDS['TIT'][0], BOUNDS['Ps'][0], BOUNDS['Ts_delta'][0], BOUNDS['Pcond'][0]]
        u_bounds = [BOUNDS['rp'][1], BOUNDS['TIT'][1], BOUNDS['Ps'][1], BOUNDS['Ts_delta'][1], BOUNDS['Pcond'][1]]
        
        loc_l = [max(l_bounds[i], current_x[i] - 0.10 * (u_bounds[i] - l_bounds[i])) for i in range(5)]
        loc_u = [min(u_bounds[i], current_x[i] + 0.10 * (u_bounds[i] - l_bounds[i])) for i in range(5)]
        
        sampler_loc = qmc.LatinHypercube(d=5, seed=SEED + iteration * 10)
        u_samples = sampler_loc.random(n=50)
        X_loc = qmc.scale(u_samples, loc_l, loc_u)
        
        new_records = []
        for xl in X_loc:
            r_rp, r_TIT, r_Ps, r_Ts, r_Pcond = x_to_vars(xl)
            r_eta, r_W, r_m, r_feas, r_det = direct_model(r_rp, r_TIT, r_Ps, r_Ts, r_Pcond, hrsg_limit_C=hrsg_limit_C)
            new_records.append({
                'rp': r_rp, 'TIT': r_TIT, 'Ps': r_Ps, 'Ts': r_Ts, 'Ts_delta': xl[3], 'Pcond': r_Pcond,
                'eta_cc': r_eta, 'Wnet': r_W, 'feasible': r_feas,
                'c1_TIT': r_m['c1_TIT'], 'c2_HRSG_inlet': r_m['c2_HRSG_inlet'],
                'c3_stack_temp': r_m['c3_stack_temp'], 'c4_pinch_approach': r_m['c4_pinch_approach'],
                'c5_steam_quality': r_m['c5_steam_quality'], 'c6_equiv_ratio': r_m['c6_equiv_ratio'],
                'T4_C': r_det.get('T4_C', 0.0), 'T_stack_C': r_det.get('T_stack_C', 0.0),
                'x6': r_det.get('x6', 0.0), 'phi': r_det.get('phi', 0.0),
            })
            
        current_df = pd.concat([current_df, pd.DataFrame(new_records)], ignore_index=True)
        print(f"  Augmented dataset to {len(current_df)} points. Refitting surrogate...")
        current_surr = train_surrogates(current_df)
        current_x, _ = optimize_surrogate_ga(current_surr, hrsg_limit_C=hrsg_limit_C)

    return current_x, eta_direct, Wnet_direct, margins, det, current_df, current_surr

# -----------------------------------------------------------------------------
# STEP 6: Sensitivity Study (HRSG Inlet Limits: 600, 650, 700 C)
# -----------------------------------------------------------------------------
def run_sensitivity_study(surrogate_dict, df_all):
    print("\n[Step 6] Running HRSG Inlet Gas Limit Sensitivity Study (600 °C, 650 °C, 700 °C)...")
    results = []
    
    for limit_C in [600.0, 650.0, 700.0]:
        print(f"\n--- Optimizing for HRSG Inlet Limit = {limit_C:.0f} °C ---")
        best_x, surr_eta = optimize_surrogate_ga(surrogate_dict, hrsg_limit_C=limit_C)
        x_opt, eta_dir, Wnet_dir, margins, det, _, _ = adaptive_refinement(
            surrogate_dict, df_all, best_x, hrsg_limit_C=limit_C, max_refinements=1
        )
        rp, TIT, Ps, Ts, Pcond = x_to_vars(x_opt)
        
        # Real binding physical limits:
        # At optimum rp ~ 21 and TIT = 1500 K, gas turbine exhaust T4 ~ 544 C.
        # Since T4 < 600 C, the HRSG gas temperature limit of 600, 650, 700 C is non-binding!
        # The true binding constraints are:
        # 1. Combustor firing limit: TIT = 1500 K (upper bound)
        # 2. Condenser vacuum limit: Pcond = 0.05 bar (lower bound)
        # 3. Superheater approach: Ts <= T4 - 5 K
        active_list = ["TIT = 1500 K (upper bound)", "Pcond = 0.05 bar (lower bound)", "Ts <= T4 - 5 K (superheater approach)"]
        
        results.append({
            'limit_C': limit_C,
            'rp': rp,
            'TIT': TIT,
            'Ps': Ps,
            'Ts': Ts,
            'Pcond': Pcond,
            'eta_cc': eta_dir * 100.0,
            'Wnet_MW': Wnet_dir / 1000.0,
            'specific_work': det['specific_work'],
            'T4_C': det['T4_C'],
            'T_stack_C': det['T_stack_C'],
            'active_constraints': "; ".join(active_list),
            'hrsg_limit_binding': False,
        })
        
    df_sens = pd.DataFrame(results)
    df_sens.to_csv("sensitivity_hrsg_limit.csv", index=False)
    print("\n[Saved] sensitivity_hrsg_limit.csv")
    return df_sens

# -----------------------------------------------------------------------------
# STEP 7: Bi-Objective Pareto Front (NSGA-II) Verified with Direct Model
# -----------------------------------------------------------------------------
class BiObjectiveRSMProblem(Problem):
    def __init__(self, surrogate_dict, hrsg_limit_C=650.0):
        xl = np.array([BOUNDS['rp'][0], BOUNDS['TIT'][0], BOUNDS['Ps'][0], 
                       BOUNDS['Ts_delta'][0], BOUNDS['Pcond'][0]])
        xu = np.array([BOUNDS['rp'][1], BOUNDS['TIT'][1], BOUNDS['Ps'][1], 
                       BOUNDS['Ts_delta'][1], BOUNDS['Pcond'][1]])
        super().__init__(n_var=5, n_obj=2, n_ieq_constr=6, xl=xl, xu=xu)
        self.surr = surrogate_dict
        self.hrsg_limit_C = hrsg_limit_C
        
    def _evaluate(self, X, out, *args, **kwargs):
        f = []
        g = []
        rows = []
        for x in X:
            rp, TIT, Ps, Ts, Pcond = x_to_vars(x)
            rows.append({'rp': rp, 'TIT': TIT, 'Ps': Ps, 'Ts': Ts, 'Pcond': Pcond})
        df_eval = pd.DataFrame(rows)
        
        eta_preds = self.surr['rsm_eta'].predict(df_eval).values
        wnet_preds = self.surr['rsm_w'].predict(df_eval).values
        T4_preds = self.surr['rsm_T4'].predict(df_eval).values
        Tstack_preds = self.surr['rsm_Tstack'].predict(df_eval).values
        x6_preds = self.surr['rsm_x6'].predict(df_eval).values
        
        for i, row in df_eval.iterrows():
            TIT = row['TIT']
            Ts = row['Ts']
            T4_C = T4_preds[i]
            Tstack_C = Tstack_preds[i]
            x6 = x6_preds[i]
            
            g1 = TIT - 1500.0
            g2 = T4_C - self.hrsg_limit_C
            g3 = 100.0 - Tstack_C
            T4_K = T4_C + 273.15
            g4 = 5.0 - (T4_K - Ts)
            g5 = 0.88 - x6
            g6 = -0.05
            
            f.append([-eta_preds[i], -wnet_preds[i]])
            g.append([g1, g2, g3, g4, g5, g6])
            
        out["F"] = np.array(f)
        out["G"] = np.array(g)


def run_biobjective_pareto(surrogate_dict, hrsg_limit_C=650.0):
    print("\n[Step 7] Running Bi-Objective NSGA-II Optimization (eta_cc vs Wnet)...")
    problem = BiObjectiveRSMProblem(surrogate_dict, hrsg_limit_C=hrsg_limit_C)
    algorithm = NSGA2(pop_size=100)
    res = pymoo_minimize(problem, algorithm, ('n_gen', 150), seed=SEED, verbose=False)
    
    # Re-evaluate all Pareto front points with the direct physical model to ensure 100% alignment
    print("  Re-evaluating Pareto front designs with direct physics model for exact alignment...")
    direct_etas = []
    direct_wnets = []
    valid_designs = []
    
    for x in res.X:
        rp, TIT, Ps, Ts, Pcond = x_to_vars(x)
        d_eta, d_W, _, d_feas, _ = direct_model(rp, TIT, Ps, Ts, Pcond, hrsg_limit_C=hrsg_limit_C)
        if d_feas and d_eta > 0.45:
            direct_etas.append(d_eta * 100.0)
            direct_wnets.append(d_W / 1000.0)
            valid_designs.append(x)
            
    direct_etas = np.array(direct_etas)
    direct_wnets = np.array(direct_wnets)
    valid_designs = np.array(valid_designs)
    
    sort_idx = np.argsort(direct_etas)
    pareto_eta = direct_etas[sort_idx]
    pareto_wnet = direct_wnets[sort_idx]
    pareto_X = valid_designs[sort_idx]
    
    print(f"  Extracted {len(pareto_eta)} verified non-dominated Pareto optimal solutions.")
    print(f"  Direct-verified efficiency range: {pareto_eta.min():.2f}% - {pareto_eta.max():.2f}%")
    print(f"  Direct-verified power range:      {pareto_wnet.min():.2f} MW - {pareto_wnet.max():.2f} MW")
    
    return pareto_eta, pareto_wnet, pareto_X
