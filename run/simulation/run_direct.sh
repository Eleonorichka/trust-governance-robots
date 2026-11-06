#!/bin/bash

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
RESULTS_DIR="$SCRIPT_DIR/results"
SRC_DIR="$SCRIPT_DIR/../../trust_ws/src/trust_gov"

export PYTHONPATH="$SRC_DIR:$PYTHONPATH"

SCENARIO_ARG=$1
if [ -z "$SCENARIO_ARG" ]; then
    echo "Usage: $0 <scenario.json | all>"
    exit 1
fi

if [ "$SCENARIO_ARG" == "all" ]; then
    SCENARIOS=("$SCRIPT_DIR/scenario1.json" "$SCRIPT_DIR/scenario2.json" "$SCRIPT_DIR/scenario3.json")
else
    SCENARIOS=("$SCENARIO_ARG")
fi

mkdir -p "$RESULTS_DIR"

# Clear logs
> "$RESULTS_DIR/A.log"
> "$RESULTS_DIR/B.log"
> "$RESULTS_DIR/C.log"
> "$RESULTS_DIR/gov.log"

cleanup() {
    pkill -9 -f "trust_gov" 2>/dev/null
    if command -v lsof >/dev/null 2>&1; then
        for PORT in 5000 5001 5002; do
            lsof -ti tcp:$PORT | xargs kill -9 2>/dev/null
        done
    fi
    sleep 1
}

trap cleanup SIGINT SIGTERM EXIT

launch_robot() {
    NS=$1
    PORT=$2
    LOG_FILE=$3
    python3 -m trust_gov.nodes.robot_node.robot_node >> "$LOG_FILE" 2>&1 &
    python3 -m trust_gov.nodes.ethics_manager.ethics_manager_node >> "$LOG_FILE" 2>&1 &
    python3 -m trust_gov.nodes.connector.connector_node --port "$PORT" >> "$LOG_FILE" 2>&1 &
}

for SCEN in "${SCENARIOS[@]}"; do
    cleanup
    
    echo "======================================"
    echo "Running simulation for: $(basename $SCEN)"
    python3 -c "import json; print('Description:', json.load(open('$SCEN'))['metadata']['description'])"
    echo "======================================"
    
    echo -e "\n=== Run: $(basename $SCEN) ===" >> "$RESULTS_DIR/A.log"
    echo -e "\n=== Run: $(basename $SCEN) ===" >> "$RESULTS_DIR/B.log"
    echo -e "\n=== Run: $(basename $SCEN) ===" >> "$RESULTS_DIR/C.log"

    echo "Starting Governance Node..."
    python3 -m trust_gov.nodes.governance_node.governance_node >> "$RESULTS_DIR/gov.log" 2>&1 &
    sleep 2

    echo "Starting 3 robots..."
    launch_robot "trust_robot_A" "5000" "$RESULTS_DIR/A.log"
    sleep 2
    launch_robot "trust_robot_B" "5001" "$RESULTS_DIR/B.log"
    sleep 2
    launch_robot "trust_robot_C" "5002" "$RESULTS_DIR/C.log"
    sleep 2

    export SCEN_FILE="$SCEN"
    python3 <<'PYEOF'
import json, os, time
scen_file = os.environ.get('SCEN_FILE')
scenario = json.load(open(scen_file))
platoon_order = scenario.get('metadata', {}).get('platoon_order', [])

def send_goal(port, bot_data):
    if not bot_data:
        return
    bot_data['platoon_order'] = platoon_order
    payload = json.dumps(bot_data).replace("'", "'\"'\"'")
    cmd = f"curl -s -X POST 'http://localhost:{port}/goal' -H 'Content-Type: application/json' -d '{payload}'"
    
    max_retries = 5
    for i in range(max_retries):
        exit_code = os.system(cmd)
        if exit_code == 0:
            return
        print(f"  [Wait] Port {port} not ready... retrying ({i+1}/{max_retries})")
        time.sleep(1)
    print(f"  [ERROR] Failed to send goal to port {port} after {max_retries} attempts.")

send_goal(5001, scenario.get('robot_B', {}))
send_goal(5002, scenario.get('robot_C', {}))
time.sleep(1)
bot_a_data = scenario.get('robot_A', {})
bot_a_data['init_global_ts'] = scenario.get('metadata', {}).get('init_global_ts', {})
send_goal(5000, bot_a_data)
PYEOF

    echo "Simulation running. Waiting 15s for completion..."
    sleep 15
    
    cleanup
    echo "Finished $(basename $SCEN)"
done

echo "All simulations completed."
