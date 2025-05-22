# DS-Sim Scheduler Project

This project implements an advanced job scheduling algorithm for distributed systems simulation (DS-Sim). The Turnaround-Optimized Scheduler (TOS) focuses on optimizing average turnaround time while maintaining reasonable resource utilization and cost efficiency.

## Project Overview

The project consists of several components:
- **TOS Scheduler**: An intelligent job scheduling algorithm implemented in Python
- **Experiment Runner**: Bash scripts to automate running experiments and collecting results
- **Visualization Tool**: A Python script to generate comparison charts

This scheduling system outperforms baseline algorithms (FF, BF, WF, ATL, FC, FAFC) in average turnaround time while maintaining competitive performance in resource utilization and cost metrics.

## Features

The TOS Scheduler implements several advanced scheduling strategies:

- **Adaptive Job Packing**: Intelligently packs jobs to active servers with appropriate utilization levels (30%-80%)
- **Job and Server Classification**: Categorizes jobs and servers as small, medium, or large for optimal matching
- **Multi-dimensional Scoring System**: Considers wait time, queue length, and resource matching when making scheduling decisions
- **Resource Tracking and Dynamic Load Balancing**: Maintains accurate tracking of available resources on servers

## Project Structure

```
project/
│
├── tos.py                  # Main scheduler implementation
├── run_experiments.sh      # Script to run all experiments with various algorithms
├── generate_charts.py      # Script to generate performance comparison charts
├── ds-sim/                 # DS-Sim simulation environment
│   ├── src/                # Source code for DS-Sim
│   └── configs/            # Configuration files for experiments
│       └── sample-configs/ # Sample configuration files
└── results/                # Directory for storing experiment results
    └── charts/             # Generated comparison charts
```

## Installation & Setup

### dependencies

- Python 3.6+
- matplotlib
- pandas
- numpy

### install
```
chmod +x setup_server.sh 2>/dev/null || true
```
## Usage

### Running the Scheduler Directly (Not Recommend)

To run the TOS scheduler directly:

Open a terminal and run:

```
./ds-sim/src/pre-compiled/ds-server  -c ./ds-sim/configs/sample-configs/ds-sample-config01.xml -v brief
```

Open another terminal and run:
```
python tos.py
```

### Running Experiments

To run experiments with all baseline algorithms and the TOS scheduler:

```bash
./run_experiments.sh
```

This will:
- Run each baseline algorithm (FF, BF, WF, ATL, FC, FAFC) with specified configurations
- Run the TOS scheduler with the same configurations
- Collect performance metrics for each run
- Generate a CSV file with the results
- Create visualization charts comparing algorithm performance

### Generating Charts

Charts are automatically generated after running experiments. You can also generate them manually:

```bash
python3 generate_charts.py
```

This will create various charts comparing the performance of different algorithms in terms of:
- Average turnaround time
- Resource utilization
- Number of servers used
- Total cost

## Algorithm Details

The TOS scheduling algorithm uses a sophisticated scoring system to select the best server for each job:

```python
# Simplified scoring logic
score = wait_time + 
        (waiting_jobs * waiting_job_penalty) + 
        (running_jobs * running_job_penalty)

# Job packing logic (if enabled)
if server_load is between 30% and 80%:
    apply utilization bonus to score
```

Key parameters (can be adjusted in code):
- `max_server_load = 0.8` - Maximum server load for job packing
- `utilization_bonus = 50` - Bonus score for packing jobs on appropriate servers
- `waiting_job_penalty = 120` - Penalty for each waiting job
- `running_job_penalty = 30` - Penalty for each running job
- `boot_time_penalty = 60` - Penalty for server boot time

## Performance Metrics

The system tracks and reports several key performance metrics:

- **Total Servers Used**: Number of servers utilized during simulation
- **Average Utilization**: Percentage of server resources used on average
- **Effective Usage**: Efficiency of resource allocation
- **Total Cost**: Total cost of servers used during simulation
- **Average Waiting Time**: Average time jobs spend waiting to be processed
- **Average Execution Time**: Average time jobs spend executing
- **Average Turnaround Time**: Average total time from job submission to completion

## Optimization Focus

The TOS scheduler is specifically optimized to improve average turnaround time compared to baseline algorithms. It achieves this by:

1. Minimizing job waiting time through intelligent server selection
2. Reducing the need to start new servers by efficient job packing
3. Matching job size to appropriate server size
4. Avoiding overloading servers that would slow down job execution

## License

This project is distributed under the terms of the MIT license.

## Acknowledgments

- DS-Sim simulation environment provided by the COMP3100/6105 Distributed Systems course
- Baseline algorithms and sample configurations from DS-Sim repository
