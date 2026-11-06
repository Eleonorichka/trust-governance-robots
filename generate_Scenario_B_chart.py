import pandas as pd
import matplotlib.pyplot as plt

data = [
    {"weight": 0.50, "initial_trust": 1.0, "steps": 13},
    {"weight": 0.50, "initial_trust": 0.9, "steps": 17},
    {"weight": 0.50, "initial_trust": 0.8, "steps": 23},
    {"weight": 0.55, "initial_trust": 1.0, "steps": 12},
    {"weight": 0.55, "initial_trust": 0.9, "steps": 16},
    {"weight": 0.55, "initial_trust": 0.8, "steps": 22},
    {"weight": 0.60, "initial_trust": 1.0, "steps": 11},
    {"weight": 0.60, "initial_trust": 0.9, "steps": 15},
    {"weight": 0.60, "initial_trust": 0.8, "steps": 21},
    {"weight": 0.65, "initial_trust": 1.0, "steps": 10},
    {"weight": 0.65, "initial_trust": 0.9, "steps": 14},
    {"weight": 0.65, "initial_trust": 0.8, "steps": 20},
    {"weight": 0.70, "initial_trust": 1.0, "steps": 8},
    {"weight": 0.70, "initial_trust": 0.9, "steps": 13},
    {"weight": 0.70, "initial_trust": 0.8, "steps": 19},
    {"weight": 0.75, "initial_trust": 1.0, "steps": 6},
    {"weight": 0.75, "initial_trust": 0.9, "steps": 10},
    {"weight": 0.75, "initial_trust": 0.8, "steps": 16},
    {"weight": 0.80, "initial_trust": 1.0, "steps": 1},
    {"weight": 0.80, "initial_trust": 0.9, "steps": 7},
    {"weight": 0.80, "initial_trust": 0.8, "steps": 13}
]

df = pd.DataFrame(data)

plt.figure(figsize=(10, 5))
for trust in sorted(df["initial_trust"].unique()):
    sub = df[df["initial_trust"] == trust]
    plt.plot(sub["weight"], sub["steps"], marker="o", linewidth=2, label=f"Initial Trust {trust}")

plt.title("Convergence Steps vs Global Governance Weight")
plt.xlabel("Global Governance Weight")
plt.ylabel("Steps to Converge")
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()
plt.tight_layout()
plt.savefig("analysis/rq2/rq2_convergence_time_x_colors.png", dpi=300)
print("SUCCESS: Clean PNG created!")
