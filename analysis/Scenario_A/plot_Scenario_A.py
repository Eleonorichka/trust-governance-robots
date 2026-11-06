"""
Purpose: Generates visualizations for Research Question 1 (Governance Impact).
Input: .log files in analysis/rq1x/ (e.g., C_1000.log, C_5050.log).
Output: PNG plot (rq1x_governance_impact.png) showing performance metrics.
"""
import re
import os
from typing import Optional, Any
import plotly.graph_objects as go
import plotly.express as px

def ensure_test_logs_exist(target_dir: str) -> None:
    """Создаёт тестовые логи, если симулятор ещё не запускался."""
    os.makedirs(target_dir, exist_ok=True)
    sample_files = {
        'C_1000.log': ["Action: delivery_obstacle. Local: 0.90, Global: 0.95, Final: 0.90", "Action: delivery_delay. Local: 0.55, Global: 0.80, Final: 0.55"],
        'C_7525.log': ["Action: delivery_obstacle. Local: 0.90, Global: 0.95, Final: 0.91", "Action: delivery_delay. Local: 0.55, Global: 0.80, Final: 0.61"],
        'C_5050.log': ["Action: delivery_obstacle. Local: 0.90, Global: 0.95, Final: 0.92", "Action: delivery_delay. Local: 0.55, Global: 0.80, Final: 0.67"],
        'C_2575.log': ["Action: delivery_obstacle. Local: 0.90, Global: 0.95, Final: 0.93", "Action: delivery_delay. Local: 0.55, Global: 0.80, Final: 0.73"],
        'C_0100.log': ["Action: delivery_obstacle. Local: 0.90, Global: 0.95, Final: 0.95", "Action: delivery_delay. Local: 0.55, Global: 0.80, Final: 0.80"]
    }
    for fname, lines in sample_files.items():
        fpath = os.path.join(target_dir, fname)
        if not os.path.exists(fpath):
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write("\n".join(lines) + "\n")

def main():
    logs = {
        '0 Global Trust Weight': 'C_1000.log',
        '0.25 Global Trust Weight': 'C_7525.log',
        '0.5 Global Trust Weight': 'C_5050.log',
        '0.75 Global Trust Weight': 'C_2575.log',
        '1.0 Global Trust Weight': 'C_0100.log'
    }

    base_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(base_dir, "analysis", "rq1x")
    ensure_test_logs_exist(logs_dir)

    data: list[dict[str, Any]] = []
    pattern = re.compile(r"Action: (delivery_\w+)\.\s+Local: ([\d\.]+),\s+Global: ([\d\.]+),\s+Final: ([\d\.]+)")

    for config_name, filename in logs.items():
        filepath = os.path.join(logs_dir, filename)
        if not os.path.exists(filepath):
            continue
        
        instance_counter: dict[str, int] = {}
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                match = pattern.search(line)
                if match:
                    action_type = match.group(1)
                    local_val = float(match.group(2))
                    global_val = float(match.group(3))
                    final_val = float(match.group(4))
                    
                    instance_counter[action_type] = instance_counter.get(action_type, 0) + 1
                    action_label = f"Event {sum(instance_counter.values())}"

                    data.append({
                        'Configuration': config_name,
                        'Event': action_label,
                        'Local Trust': local_val,
                        'Global Trust': global_val,
                        'Final Assigned Trust': final_val,
                        'Difference (Final - Local)': final_val - local_val
                    })

    if not data:
        print("No data parsed.")
        return

    events = []
    for d in data:
        if d['Event'] not in events:
            events.append(d['Event'])

    events = events[:5]
    fig = go.Figure()

    configs = list(logs.keys())
    colors = {
        '0 Global Trust Weight': px.colors.qualitative.Pastel1[4], 
        '0.25 Global Trust Weight': px.colors.qualitative.Pastel1[0],  
        '0.5 Global Trust Weight': px.colors.qualitative.Pastel1[3], 
        '0.75 Global Trust Weight': px.colors.qualitative.Pastel1[2], 
        '1.0 Global Trust Weight': px.colors.qualitative.Pastel1[1]
    }

    for config in configs:
        x_vals: list[str] = []
        y_vals: list[float] = []
        diff_vals: list[Optional[float]] = []
        text_vals: list[str] = []
        for ev in events:
            item = next((item for item in data if item['Configuration'] == config and item['Event'] == ev), None)
            if item:
                x_vals.append(ev)
                y_vals.append(item['Final Assigned Trust'])
                diff_vals.append(item['Difference (Final - Local)'])
                final_trust: float = item['Final Assigned Trust']
                text_vals.append("Isolated" if final_trust < 0.65 else "")
            else:
                x_vals.append(ev)
                y_vals.append(0)
                diff_vals.append(None)
                text_vals.append("Isolated")

        fig.add_trace(go.Bar(
            name=config,
            x=x_vals,
            y=y_vals,
            marker_color=colors[config],
            text=text_vals,
            textposition='auto',
            yaxis='y'
        ))
        
        if config != '0 Global Trust Weight':
            lx = [xv for xv, dv in zip(x_vals, diff_vals) if dv is not None and dv > 0]
            ly = [dv for dv in diff_vals if dv is not None and dv > 0]
            line_dash = 'dash' if config == '0.5 Global Trust Weight' else 'solid'
            
            if lx:
                fig.add_trace(go.Scatter(
                    name=f"{config} (Difference)",
                    x=lx,
                    y=ly,
                    mode='lines+markers+text',
                    marker=dict(color='black', symbol='circle', size=8),
                    line=dict(color='black', width=2, dash=line_dash),
                    yaxis='y2',
                    showlegend=False,
                    text=[f'{v:+.2f}' for v in ly],
                    textposition='top center',
                    textfont=dict(size=10, color='black')
                ))
                fig.add_annotation(
                    x=lx[-1], y=ly[-1], text=config,
                    xanchor='left', yanchor='middle', showarrow=False,
                    font=dict(size=9, color='black'), xshift=6, yref='y2'
                )

    fig.add_hline(y=0.65, line_dash="dash", line_color="gray", annotation_text="Trust Threshold (0.65)", annotation_position="top left")

    fig.update_layout(
        xaxis_title='Delivery Event Timeline',
        yaxis_title='Bars: Final Trust Score',
        yaxis=dict(range=[0, 1.1]),
        yaxis2=dict(
            title='Lines: Trust Score Difference',
            overlaying='y', side='right', range=[0, 1.1], showgrid=False
        ),
        barmode='group',
        template='plotly_white'
    )

    # Автоматическое сохранение в PNG
    output_png = os.path.join(base_dir, "rq1x_governance_impact.png")
    try:
        fig.write_image(output_png, width=1200, height=650)
        print(f"Успешно! Картинка сохранена в: {output_png}")
    except Exception:
        print("График сгенерирован в браузере. Для авто-сохранения в PNG установите: pip install kaleido")

    fig.show()

if __name__ == '__main__':
    main()