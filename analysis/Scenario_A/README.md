# RQ1 Analysis — Governance Impact

## Research Question

To what extent does the governance layer improve the reputation assigned to a system exhibiting justified misbehavior, compared to a system relying solely on its own direct experience represented by a local trust score?

## Data Logs

The `.log` files in this directory (`C_*.log`) are **versioned simulation outputs used to produce the results in the paper**. They are the recorded logs of **Robot C** from simulation runs where the local/global trust weight ratio was varied:

| File | Local weight | Global weight |
|------|-------------|---------------|
| `C_1000.log` | 100% | 0% |
| `C_7525.log` | 75% | 25% |
| `C_5050.log` | 50% | 50% |
| `C_2575.log` | 25% | 75% |
| `C_0100.log` | 0% | 100% |

These logs are checked into the repository solely to allow reproduction of the paper's figures and statistics without re-running the full simulation suite.

## Reproducing with Fresh Simulation Data

To re-run the analysis with new simulation results:

1. Run the simulations: `make run`
2. Copy Robot C's log from the simulation results into this directory, renaming it to match the configuration being tested (e.g. `C_5050.log` for a 50/50 weight split).
3. The active weight ratio is controlled by the `calculate_final_ts` method in `trust_ws/src/trust_gov/trust_gov/trust_calculator.py` — uncomment the desired formula before running.
4. Run the analysis: `make analyze`

## Scripts

- `plot_rq1x.py` — generates `rq1x_color_governance_impact.png`
- `stats_rq1x.py` — runs Wilcoxon signed-rank and Kruskal-Wallis tests, prints results to stdout
