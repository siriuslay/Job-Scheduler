#!/bin/bash
# run_experiments.sh
# COMP3100/6105 Assignment 2

CHOOSE='4'   # 1~4

# ouput colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

BASEDIR=$(pwd)
DS_SIM_DIR="$BASEDIR/ds-sim"
CONFIGS_DIR="$DS_SIM_DIR/configs"
RESULTS_DIR="$BASEDIR/results/$CHOOSE"
SERVER_PATH="$DS_SIM_DIR/src/pre-compiled/ds-server"
CLIENT_PATH="$DS_SIM_DIR/src/pre-compiled/ds-client"
# DPS_PATH="$BASEDIR/dps_scheduler.py"
# DPS_PATH="$BASEDIR/odps.py"
TOS_PATH="$BASEDIR/tos.py"

mkdir -p "$RESULTS_DIR"
chmod +x "$TOS_PATH"

BASELINE_ALGORITHMS=("ff" "bf" "atl" "fc" "fafc")

ALL_CONFIGS=(
    "ds-sample-config01.xml"
    "ds-sample-config02.xml"
    "ds-sample-config05.xml"
    "sample-config01.xml"
)

CONFIGS=("${ALL_CONFIGS[$((CHOOSE-1))]}")

extract_metrics() {
    local log_file=$1
    local algorithm=$2
    local config=$3
    
    echo "decoding the logfile: $log_file"
    
    total_servers="NULL"
    avg_util="NULL"
    ef_usage="NULL"
    total_cost="NULL"
    avg_waiting="NULL"
    avg_exec="NULL"
    avg_turnaround="NULL"
    
    grep -A2 "Summary" "$log_file" > "$RESULTS_DIR/temp_summary.txt"
    grep "avg waiting time" "$log_file" >> "$RESULTS_DIR/temp_summary.txt"
    
    # servers number
    if grep -q "total #servers used:" "$log_file"; then
        # total_servers=$(grep -A2 "Summary" "$log_file" | grep "total #servers used:" | awk '{print $4}' | tr -d ',')
        total_servers=$(grep -A2 "Summary" "$log_file" | grep -Eo "total #servers used: [0-9,]+" | grep -Eo "[0-9]+" )

    fi
    # avg usage
    if grep -q "avg util:" "$log_file"; then
        avg_util=$(grep -A2 "Summary" "$log_file" | grep "avg util:" | sed -n 's/.*avg util: \([0-9.]*\)%.*/\1/p')
    fi
    
    # ef. usage
    if grep -q "ef. usage:" "$log_file"; then
        ef_usage=$(grep -A2 "Summary" "$log_file" | grep "ef. usage:" | sed -n 's/.*ef. usage: \([0-9.]*\)%.*/\1/p')
    fi
    
    # total cost
    if grep -q "total cost:" "$log_file"; then
        total_cost=$(grep -A2 "Summary" "$log_file" | grep "total cost:" | sed -n 's/.*total cost: \$\([0-9.]*\).*/\1/p')
    fi
    
    # time
    time_line=$(grep "avg waiting time:" "$log_file")
    if [[ "$time_line" =~ avg\ waiting\ time:\ ([0-9]+) ]]; then
        avg_waiting="${BASH_REMATCH[1]}"
    fi
    
    if [[ "$time_line" =~ avg\ exec\ time:\ ([0-9]+) ]]; then
        avg_exec="${BASH_REMATCH[1]}"
    fi
    
    if [[ "$time_line" =~ avg\ turnaround\ time:\ ([0-9]+) ]]; then
        avg_turnaround="${BASH_REMATCH[1]}"
    fi
    
    echo "$algorithm,$config,$total_servers,$avg_util,$ef_usage,$total_cost,$avg_waiting,$avg_exec,$avg_turnaround" >> "$RESULTS_DIR/metrics.csv"
    
    echo -e "${BLUE}Algorithm: ${GREEN}$algorithm${NC}"
    echo -e "${BLUE}Config: ${GREEN}$config${NC}"
    echo -e "${BLUE}Total Servers: ${GREEN}$total_servers${NC}"
    echo -e "${BLUE}Avg. Usage: ${GREEN}$avg_util%${NC}"
    echo -e "${BLUE}Ef. Usage: ${GREEN}$ef_usage%${NC}"
    echo -e "${BLUE}Total Cost: ${GREEN}\$$total_cost${NC}"
    echo -e "${BLUE}Avg_waiting Time: ${GREEN}$avg_waiting${NC}"
    echo -e "${BLUE}Avg_executing Time: ${GREEN}$avg_exec${NC}"
    echo -e "${BLUE}Avg_turnaround Time: ${GREEN}$avg_turnaround${NC}"
    echo -e "${YELLOW}----------------------------------------------${NC}"
    
    cp "$log_file" "$RESULTS_DIR/raw_${algorithm}_${config%.xml}.log"
}

echo "Algorithm,Config,TotalServers,AvgUtilization,EffectiveUsage,TotalCost,AvgWaitingTime,AvgExecTime,AvgTurnaroundTime" > "$RESULTS_DIR/metrics.csv"

run_experiment() {
    local algorithm=$1
    local config_file=$2
    local config_path="$CONFIGS_DIR/sample-configs/$config_file"
    local log_file="$RESULTS_DIR/${algorithm}_${config_file%.xml}.log"
    
    echo -e "${YELLOW}Run $algorithm Algorithm, Config: $config_file${NC}"
    
    [ -f "$log_file" ] && rm "$log_file"
    
    # Start Server
    "$SERVER_PATH" -c "$config_path" -v all > "$log_file" &
    server_pid=$!
    sleep 2
    
    if [ "$algorithm" == "tos" ]; then
        python3 "$TOS_PATH" >> "$log_file" 2>&1   # run tos.py
    else
        "$CLIENT_PATH" -a "$algorithm" >> "$log_file" 2>&1
    fi

    # wait_time=0
    # max_wait=300
    # while kill -0 "$server_pid" 2>/dev/null; do
    #     sleep 1
    #     wait_time=$((wait_time + 1))
    #     if [ $wait_time -ge $max_wait ]; then
    #         echo "Out of time"
    #         kill -9 "$server_pid" 2>/dev/null
    #         break
    #     fi
    # done
    
    extract_metrics "$log_file" "$algorithm" "$config_file"
    sleep 5
}

# run baseline
for config in "${CONFIGS[@]}"; do
    for algorithm in "${BASELINE_ALGORITHMS[@]}"; do
        run_experiment "$algorithm" "$config"
    done
    
    # run tos
    run_experiment "tos" "$config"
done

if [ -f "$BASEDIR/generate_charts.py" ]; then
    # python3 "$BASEDIR/generate_charts.py"
    python3 "$BASEDIR/generate_charts.py" "$RESULTS_DIR"
fi
