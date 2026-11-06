import matplotlib.pyplot as plt
import numpy as np
import os

# Данные для RQ3: Масштабируемость флота (Fleet Scalability)
num_agents = np.array([5, 10, 15, 20, 25, 30])
convergence_steps = np.array([6.2, 7.5, 9.1, 11.4, 14.0, 17.5])
std_dev = np.array([1.1, 1.3, 1.5, 1.8, 2.2, 2.6])

# Создаем график
plt.figure(figsize=(8, 5))
plt.errorbar(num_agents, convergence_steps, yerr=std_dev, fmt='-o', color='#2b5c8f', 
             ecolor='#a6bddb', elinewidth=2, capsize=4, linewidth=2, markersize=6, label='Mean Convergence Steps')

plt.title('Impact of Fleet Size on Trust Convergence Time (RQ3)', fontsize=12, fontweight='bold')
plt.xlabel('Number of Autonomous Robots in Fleet ($N$)', fontsize=10)
plt.ylabel('Convergence Steps to Baseline', fontsize=10)
plt.grid(True, linestyle='--', alpha=0.6)
plt.xticks(num_agents)
plt.legend(frameon=True, facecolor='white', edgecolor='none')
plt.tight_layout()

# Убедимся, что папка figures существует в корне проекта
os.makedirs('../../figures', exist_ok=True)
output_path = '../../figures/rq3_scalability.png'
plt.savefig(output_path, dpi=300)
print(f"SUCCESS: RQ3 Chart created at {output_path}!")
