"""
Purpose: Generates convergence time visualizations for Research Question 2.
Input: .log files in analysis/rq2/ (e.g., C_2080_08.log).
Output: Time-series plots showing trust score convergence across scenarios.
"""
import re
import os
import plotly.graph_objects as go
import plotly.express as px

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Ordered to show increasing global weight, which should show a decrease in convergence steps
    # Maps global_weight_pct -> file code
    weights = {
        50: '5050',
        55: '4555',
        60: '4060',
        65: '3565',
        70: '3070',
        75: '2575',
        80: '2080'
    }
    
    initials = {
        '0.8': '08',
        '0.9': '09',
        '1.0': '10'
    }

    alpha = 0.05
    
    data = []
    
    for weight_label, weight_code in weights.items():
        for init_label, init_code in initials.items():
            filename = f"C_{weight_code}_{init_code}.log"
            filepath = os.path.join(base_dir, filename)
            
            if not os.path.exists(filepath):
                print(f"Warning: File {filepath} not found.")
                continue
                
            steps = 0
            counting = False
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
                            if final_val >= global_val - alpha:
                                data.append({
                                    'Weight': weight_label,
                                    'Initial Trust': init_label,
                                    'Steps to Converge': steps
                                })
                                break

    if not data:
        print("No data parsed.")
        return

    fig = go.Figure()

    ordered_weights = sorted(weights.keys())

    bar_colors = {
        '0.8': px.colors.qualitative.Pastel1[4], 
        '0.9': px.colors.qualitative.Pastel1[2],
        '1.0': px.colors.qualitative.Pastel1[1]
    }

    # --- Grouped bars, one series per initial trust baseline ---
    for init_label in initials.keys():
        x_vals, y_vals = [], []
        for w in ordered_weights:
            item = next((d for d in data if d['Weight'] == w and d['Initial Trust'] == init_label), None)
            if item:
                x_vals.append(w)
                y_vals.append(item['Steps to Converge'])

        fig.add_trace(go.Bar(
            x=x_vals,
            y=y_vals,
            name=f'Initial Trust: {init_label}',
            marker_color=bar_colors[init_label]
            # text=y_vals,
            # textposition='outside',
            # textfont=dict(size=11, color=bar_colors[init_label])
        ))

    # --- Average trend line across all initial-trust conditions ---
    avg_x, avg_y = [], []
    for w in ordered_weights:
        vals = [d['Steps to Converge'] for d in data if d['Weight'] == w]
        if vals:
            avg_x.append(w)
            avg_y.append(sum(vals) / len(vals))

    fig.add_trace(go.Scatter(
        x=avg_x,
        y=avg_y,
        mode='lines+markers+text',
        name='Average Convergence',
        text=[f'{v:.0f}' for v in avg_y],
        textposition='top center',
        textfont=dict(size=10, color='black'),
        line=dict(color='black', width=3, dash='solid'),
        marker=dict(color='black', size=10, symbol='diamond')
    ))

    max_steps = max(d['Steps to Converge'] for d in data)

    fig.update_layout(
        # title='Convergence Time of Final Trust Toward Ground-Truth (RQ2)',
        xaxis_title='Global Trust Weight',
        yaxis_title='Simulation Steps to Converge (Final Trust ≥ Global Trust - 0.05)',
        template='plotly_white',
        barmode='group',
        bargap=0.35,
        bargroupgap=0.05,
        xaxis=dict(
            tickmode='array',
            tickvals=ordered_weights,
            ticktext=[f'{w/100}' for w in ordered_weights],
            range=[45, 85],
        ),
        yaxis=dict(range=[0, max_steps + 4]),
        legend=dict(
            orientation='v',
            x=1.02,
            y=1,
            xanchor='left',
        ),
    )

    output_path = os.path.join(base_dir, 'rq2_convergence_time_x_colors.png')
    fig.write_html(output_path.replace(".png", ".html"))
    try:
        fig.write_image(output_path, width=1100, height=620, engine="kaleido")
    except:
        pass
    print(f"Plot saved to {output_path}")

if __name__ == '__main__':
    main()
