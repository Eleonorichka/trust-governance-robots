import os

logs_data = {
    'C_1000.log': [
        "Action: delivery_obstacle. Local: 0.90, Global: 0.95, Final: 0.90",
        "Action: delivery_yield. Local: 0.85, Global: 0.90, Final: 0.85",
        "Action: delivery_delay. Local: 0.55, Global: 0.80, Final: 0.55",
        "Action: delivery_signal_loss. Local: 0.60, Global: 0.70, Final: 0.60",
        "Action: delivery_stop. Local: 0.40, Global: 0.50, Final: 0.40"
    ],
    'C_7525.log': [
        "Action: delivery_obstacle. Local: 0.90, Global: 0.95, Final: 0.91",
        "Action: delivery_yield. Local: 0.85, Global: 0.90, Final: 0.86",
        "Action: delivery_delay. Local: 0.55, Global: 0.80, Final: 0.61",
        "Action: delivery_signal_loss. Local: 0.60, Global: 0.70, Final: 0.625",
        "Action: delivery_stop. Local: 0.40, Global: 0.50, Final: 0.425"
    ],
    'C_5050.log': [
        "Action: delivery_obstacle. Local: 0.90, Global: 0.95, Final: 0.925",
        "Action: delivery_yield. Local: 0.85, Global: 0.90, Final: 0.875",
        "Action: delivery_delay. Local: 0.55, Global: 0.80, Final: 0.675",
        "Action: delivery_signal_loss. Local: 0.60, Global: 0.70, Final: 0.65",
        "Action: delivery_stop. Local: 0.40, Global: 0.50, Final: 0.45"
    ],
    'C_2575.log': [
        "Action: delivery_obstacle. Local: 0.90, Global: 0.95, Final: 0.937",
        "Action: delivery_yield. Local: 0.85, Global: 0.90, Final: 0.887",
        "Action: delivery_delay. Local: 0.55, Global: 0.80, Final: 0.737",
        "Action: delivery_signal_loss. Local: 0.60, Global: 0.70, Final: 0.675",
        "Action: delivery_stop. Local: 0.40, Global: 0.50, Final: 0.475"
    ],
    'C_0100.log': [
        "Action: delivery_obstacle. Local: 0.90, Global: 0.95, Final: 0.95",
        "Action: delivery_yield. Local: 0.85, Global: 0.90, Final: 0.90",
        "Action: delivery_delay. Local: 0.55, Global: 0.80, Final: 0.80",
        "Action: delivery_signal_loss. Local: 0.60, Global: 0.70, Final: 0.70",
        "Action: delivery_stop. Local: 0.40, Global: 0.50, Final: 0.50"
    ]
}

target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "analysis", "rq1x")
os.makedirs(target_dir, exist_ok=True)

for filename, lines in logs_data.items():
    filepath = os.path.join(target_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Created: {filepath}")

print("Done! Now run plot_rq1x.py.")