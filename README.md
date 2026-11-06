# Evaluation of Trust Architecture in Multi-Robot Systems

This repository contains the simulation, logging, and evaluation framework developed for analyzing trust mechanisms in autonomous multi-robot platooning and delivery scenarios. The project evaluates how different local and global trust weights, along with governance layers, impact overall system safety, reliability, and resilience under various operational abnormalities.

## Key Features & Contributions
- **Trust Calculation Layer (`trust_ws/`)**: Implements dynamic local and global trust score updates based on robot actions, deviations, and governance modifiers.
- **Experimental Scenarios & Logs (`run/`)**: Contains experimental scenario configurations and output log files capturing robot behaviors across multiple test conditions:
  - **Scenario A**: Transient operational anomalies and emergency braking maneuvers.
  - **Scenario B**: Multi-cluster fleet setups featuring compromised or faulty nodes.
  - **Scenario C**: Network degradation, high latency, and communication loss fallback modes.
- **Analysis & Chart Generation (`analysis/`)**: Scripts and parsing tools that process log data to build interactive timeline visualizations, deviation metrics, and comparative trust score graphs.
- **Figures & Plots (`figures/`)**: Automatically stores exported visual analytics and performance figures used in the thesis.

## Repository Structure
```text
.
├── analysis/                 # Data parsing, statistical tests, and analytics modules
├── figures/                  # Generated plot outputs and charts (.png)
├── run/                      # Simulation run configurations and log files
├── trust_ws/                 # ROS 2 workspace containing custom trust packages
│   └── src/
│       └── trust_gov/        # Core trust calculation and governance logic
├── Dockerfile                # Container configuration for reproducible environment
├── generate_*.py             # Scripts for generating research scenario graphs
└── README.md                 # Project documentation