"""
Purpose: Calculates statistical metrics for Research Question 1x.
Input: .log files in analysis/rq1x/.
Output: Console output of mean, median, and variance for governance overhead.
"""
"""
Statistical Testing for RQ1
============================
RQ1: To what extent does the governance layer improve the reputation assigned to a
     system exhibiting justified misbehavior, compared to a system relying solely
     on its own direct experience represented by a local trust score?

Hypotheses:
  H01: The governance layer has no effect on trust accuracy (Final Trust ≈ Local Trust).
  H11: The governance layer improves trust accuracy (Final Trust > Local Trust).

Approach:
  - Parse the same log files used in plot_rq1x.py (C_1000.log, C_7525.log, ...).
  - Extract all emergency-action trust records (Local, Global, Final).
  - For each configuration compute the per-event "lift":  lift = Final - Local.
  - H01 says lift == 0; H11 says lift > 0 (one-tailed test).
  - Tests used:
      1. Wilcoxon signed-rank test (non-parametric, paired) per configuration with
         H0: median lift = 0, H1: median lift > 0.
      2. Kruskal-Wallis test across configurations to check whether the amount of
         lift differs by governance weight.
  - Effect size: rank-biserial correlation (r) for Wilcoxon.
  - A significance level of alpha = 0.05 is used throughout.
"""

import re
import os
import sys
from scipy import stats
import numpy as np

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
ALPHA = 0.05
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOGS = {
    '0%':   'C_1000.log',
    '25%':  'C_7525.log',
    '50%':  'C_5050.log',
    '75%':  'C_2575.log',
    '100%': 'C_0100.log',
}

PATTERN = re.compile(
    r"Action: (emergency_\w+)\.\s+Local: ([\d\.]+),\s+Global: ([\d\.]+),\s+Final: ([\d\.]+)"
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_log(filepath: str) -> list[dict]:
    """Return list of dicts with local/global/final values for every emergency event."""
    records = []
    if not os.path.exists(filepath):
        print(f"  [WARNING] File not found: {filepath}")
        return records
    with open(filepath) as f:
        for line in f:
            m = PATTERN.search(line)
            if m:
                records.append({
                    'action': m.group(1),
                    'local':  float(m.group(2)),
                    'global': float(m.group(3)),
                    'final':  float(m.group(4)),
                    'lift':   float(m.group(4)) - float(m.group(2)),  # Final - Local
                })
    return records


def rank_biserial_correlation(statistic, n):
    """Approximate rank-biserial r from Wilcoxon W statistic and sample size n."""
    # r = 1 - (4*W) / (n*(n+1))  — common approximation for one-sample Wilcoxon
    return 1.0 - (4.0 * statistic) / (n * (n + 1))


def interpret_effect(r: float) -> str:
    r = abs(r)
    if r < 0.1:
        return "negligible"
    if r < 0.3:
        return "small"
    if r < 0.5:
        return "medium"
    return "large"


def sep(char="=", width=72):
    print(char * width)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    sep()
    print("  RQ1 Statistical Analysis")
    print(f"  Significance level: α = {ALPHA}")
    sep()

    # ---- Parse data -------------------------------------------------------
    data = {}
    for label, filename in LOGS.items():
        fp = os.path.join(BASE_DIR, filename)
        records = parse_log(fp)
        data[label] = records
        print(f"\n[{label} governance weight]  →  {len(records)} emergency-event records parsed")
        for r in records:
            print(f"    {r['action']:30s}  local={r['local']:.4f}  global={r['global']:.4f}"
                  f"  final={r['final']:.4f}  lift={r['lift']:+.4f}")

    # ---- Extract lift arrays ----------------------------------------------
    lift = {k: np.array([r['lift'] for r in v]) for k, v in data.items()}
    final = {k: np.array([r['final'] for r in v]) for k, v in data.items()}
    local = {k: np.array([r['local'] for r in v]) for k, v in data.items()}

    # ---- Descriptive statistics -------------------------------------------
    sep()
    print("\nDESCRIPTIVE STATISTICS  (Final Trust scores at emergency events)\n")
    header = f"{'Config':>6}  {'n':>3}  {'Local mean':>10}  {'Final mean':>10}  "
    header += f"{'Lift mean':>9}  {'Lift median':>11}  {'Lift std':>8}"
    print(header)
    print("-" * len(header))
    for label in ['0%', '25%', '50%', '75%', '100%']:
        lc = local[label]
        fn = final[label]
        li = lift[label]
        n  = len(li)
        print(f"{label:>6}  {n:>3}  {lc.mean():>10.4f}  {fn.mean():>10.4f}  "
              f"{li.mean():>9.4f}  {np.median(li):>11.4f}  {li.std(ddof=1):>8.4f}")

    # ---- Test 1: Wilcoxon signed-rank (one-tailed) per configuration ------
    sep()
    print("\nTEST 1 — Wilcoxon Signed-Rank Test (one-tailed, H1: lift > 0)")
    print("         Tests whether the governance layer raises final trust above local trust.\n")

    wilcoxon_results = {}
    for label in ['0%', '25%', '50%', '75%', '100%']:
        li = lift[label]
        n  = len(li)
        if n < 2:
            print(f"  [{label}]  Not enough data (n={n}) — skipping.")
            continue

        # Check if all values are zero (no variation → can't run test)
        if np.all(li == 0):
            print(f"  [{label}]  All lifts are 0 — governance has NO effect by definition. Cannot reject H01.")
            wilcoxon_results[label] = {'rejected': False, 'p': 1.0, 'effect_r': 0.0}
            continue

        # scipy only gives two-tailed p; for "greater" alternative divide by 2 if W in correct direction
        try:
            stat, p_two = stats.wilcoxon(li, alternative='greater')
            p_val = p_two  # scipy ≥ 1.7 supports alternative='greater' directly
        except TypeError:
            # fallback for older scipy
            stat, p_two = stats.wilcoxon(li)
            p_val = p_two / 2 if np.sum(li > 0) > np.sum(li < 0) else 1 - p_two / 2

        effect_r = rank_biserial_correlation(stat, n)
        rejected = p_val < ALPHA

        wilcoxon_results[label] = {'rejected': rejected, 'p': p_val, 'stat': stat, 'effect_r': effect_r, 'n': n}

        decision = "REJECT H01" if rejected else "FAIL TO REJECT H01"
        print(f"  [{label}]  W={stat:.2f}, p={p_val:.4f}, r={effect_r:.3f} ({interpret_effect(effect_r)})")
        print(f"           → {decision}")

    # ---- Test 2: Kruskal-Wallis (do configs differ in lift?) --------------
    sep()
    print("\nTEST 2 — Kruskal-Wallis Test (do governance weights produce different lifts?)\n")

    groups = [lift[k] for k in ['0%', '25%', '50%', '75%', '100%'] if len(lift[k]) >= 2]
    if len(groups) >= 2:
        kw_stat, kw_p = stats.kruskal(*groups)
        kw_rejected = kw_p < ALPHA
        print(f"  H (Kruskal-Wallis) = {kw_stat:.4f},  p = {kw_p:.4f}")
        if kw_rejected:
            print("  → REJECT H0: significant difference in lift across governance configurations.")
        else:
            print("  → FAIL TO REJECT H0: no significant difference across governance configurations.")
    else:
        print("  Not enough valid groups for Kruskal-Wallis.")
        kw_rejected = None

    # ---- Final Verdict ----------------------------------------------------
    sep("=")
    print("\n  FINAL VERDICT\n")
    sep("-")

    any_wilcoxon_rejected = any(v.get('rejected', False) for v in wilcoxon_results.values())
    gov_better = wilcoxon_results.get('50%', {}).get('rejected', False) or \
                 wilcoxon_results.get('100%', {}).get('rejected', False)
    no_gov     = not wilcoxon_results.get('0%', {}).get('rejected', False)

    print(f"\n  α = {ALPHA}")
    print(f"\n  Test 1  (Wilcoxon, lift > 0):")
    for label in ['0%', '25%', '50%', '75%', '100%']:
        res = wilcoxon_results.get(label)
        if res:
            tag = "✓ REJECTED" if res['rejected'] else "✗ NOT rejected"
            print(f"    H01 [{label}]:  p={res['p']:.4f}  →  {tag}")

    print(f"\n  Test 2  (Kruskal-Wallis, difference across configs):")
    if kw_rejected is not None:
        tag = "✓ REJECTED" if kw_rejected else "✗ NOT rejected"
        print(f"    H0:  p={kw_p:.4f}  →  {tag}")

    print()
    sep("-")
    print()

    # Determine which governance configs rejected H01
    rejected_100 = wilcoxon_results.get('100%', {}).get('rejected', False)
    rejected_0   = wilcoxon_results.get('0%',   {}).get('rejected', False)


if __name__ == '__main__':
    main()
