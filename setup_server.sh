#!/bin/bash
# setup_server_only.sh - Set up the environment using ds-server
# COMP3100/6105 Assignment 2

echo "=== Setting up COMP3100/6105 Assignment 2 Environment ==="

mkdir -p configs logs results

# Clone ds-sim
if [ ! -d "ds-sim" ]; then
    echo "Cloning ds-sim repository..."
    git clone https://github.com/distsys-MQ/ds-sim.git
    
    echo "ds-sim repository cloned successfully."
else
    echo "ds-sim repository already exists."
fi


chmod +x run_experiment.sh 2>/dev/null || true

pip install matplotlib pandas numpy