"""
Purpose: Statistical analysis of convergence thresholds for RQ2.
Input: .log files in analysis/rq2/.
Output: Summarized convergence rates and time-to-threshold metrics.
"""
"""
Statistical Testing for RQ2
===========================
RQ2: How do the global trust score weighting ratio and the initial trust score 
     at the time of a justified misbehavior event affect the time required for 
     a system's final trust score to converge to the ground-truth trustworthiness 
     of another system?

Hypotheses:
  H02: The global trust score weighting ratio has no significant effect on convergence time.
  H12: Increasing the global trust score weighting ratio decreases convergence time.

  H03: The initial trust score has no significant effect on convergence time.
  H13: Increasing the initial trust score decreases convergence time.

Approach:
  - Parse the log files used in plot_rq2.py.
  - Calculate "Steps to Converge" for each configuration.
  - Convergence is defined as Final Trust >= Global Trust - 0.05.
  - Use Spearman's Rank Correlation to test monotonic relationships (increases X -> decreases Y).
  - Use Kruskal-Wallis H-test to see if there are significant differences between groups.
"""

import re
import os
import sys
from scipy import stats
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
ALPHA = 0.05
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

WEIGHTS = {
    50: '5050',
    55: '4555',
    60: '4060',
    65: '3565',
    70: '3070',
    75: '2575',
    80: '2080'
}

INITIALS = {
    '1.0': '10',
    '0.9': '09',
    '0.8': '08'
}

CONVERGENCE_THRESHOLD = 0.05

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_data():
    data = []
    for weight_label, weight_code in WEIGHTS.items():
        for init_label, init_code in INITIALS.items():
            filename = f"C_{weight_code}_{init_code}.log"
            filepath = os.path.join(BASE_DIR, filename)
            
            if not os.path.exists(filepath):
                print(f"  [WARNING] File not found: {filename}")
                continue
                
            steps = 0
            counting = False
            found = False
            with open(filepath, 'r') as f:
                for line in f:
                    if "Trust Update: Predecessor B. Action: emergency_" in line:
                        counting = True
                        continue
                    if counting and "Trust Update: Predecessor B." in line:
                        steps += 1
                        global_match = re.search(r"Global: ([\d\.]+)", line)
                        match = re.search(r"Final: ([\d\.]+)", line)
                        if match:
                            global_val = float(global_match.group(1))
                            final_val = float(match.group(1))
                            if final_val >= global_val - CONVERGENCE_THRESHOLD:
                                data.append({
                                    'weight': weight_label / 100.0,
                                    'initial_trust': float(init_label),
                                    'steps': steps
                                })
                                found = True
                                break
            if not found:
                print(f"  [WARNING] No convergence found in {filename}")
    return pd.DataFrame(data)

def sep(char="=", width=72):
    print(char * width)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    sep()
    print("  RQ2 Statistical Analysis")
    print(f"  Significance level: α = {ALPHA}")
    sep()

    # ---- Parse data -------------------------------------------------------
    df = parse_data()
    if df.empty:
        print("  [ERROR] No data parsed. Exiting.")
        return

    print(f"\n  Parsed {len(df)} configurations.")
    print(df.to_string(index=False))

    # ---- Descriptive statistics -------------------------------------------
    sep()
    print("\nDESCRIPTIVE STATISTICS (Steps to Converge)\n")
    print("By Global Trust Weight:")
    print(df.groupby('weight')['steps'].agg(['count', 'mean', 'std', 'min', 'max']))
    print("\nBy Initial Trust Score:")
    print(df.groupby('initial_trust')['steps'].agg(['count', 'mean', 'std', 'min', 'max']))

    # ---- Test H12: Weight vs Steps (Spearman Rank Correlation) ------------
    sep()
    print("\nHYPOTHESIS H12: Increase Weight -> Decrease Steps")
    # alternative='less' for rho < 0 (negative correlation)
    rho_w, p_w = stats.spearmanr(df['weight'], df['steps'])
    
    # One-tailed test for negative correlation
    # scipy.stats.spearmanr returns two-tailed p-value.
    # For H12 (rho < 0), if rho < 0, p_one = p_two / 2. Else p_one = 1 - p_two / 2.
    p_w_one = p_w / 2 if rho_w < 0 else 1 - p_w / 2
    
    print(f"  Spearman's ρ: {rho_w:.4f}")
    print(f"  p-value (one-tailed): {p_w_one:.4e}")
    
    if p_w_one < ALPHA:
        print("  → REJECT H02: The global trust weight has a significant negative effect on convergence time.")
    else:
        print("  → FAIL TO REJECT H02.")

    # ---- Test H13: Initial Trust vs Steps (Spearman Rank Correlation) -----
    sep()
    print("\nHYPOTHESIS H13: Increase Initial Trust -> Decrease Steps")
    rho_i, p_i = stats.spearmanr(df['initial_trust'], df['steps'])
    
    # One-tailed test for negative correlation
    p_i_one = p_i / 2 if rho_i < 0 else 1 - p_i / 2
    
    print(f"  Spearman's ρ: {rho_i:.4f}")
    print(f"  p-value (one-tailed): {p_i_one:.4e}")
    
    if p_i_one < ALPHA:
        print("  → REJECT H03: The initial trust score has a significant negative effect on convergence time.")
    else:
        print("  → FAIL TO REJECT H03.")

    # ---- Kruskal-Wallis Tests (Differences between groups) ----------------
    sep()
    print("\nKRUSKAL-WALLIS H-TESTS (Do groups differ significantly?)\n")
    
    # Weight groups
    w_groups = [group['steps'].values for name, group in df.groupby('weight')]
    h_w, kw_p_w = stats.kruskal(*w_groups)
    print(f"  Weight groups: H={h_w:.4f}, p={kw_p_w:.4e}")
    
    # Initial Trust groups
    i_groups = [group['steps'].values for name, group in df.groupby('initial_trust')]
    h_i, kw_p_i = stats.kruskal(*i_groups)
    print(f"  Initial Trust groups: H={h_i:.4f}, p={kw_p_i:.4e}")


if __name__ == '__main__':
    main()
