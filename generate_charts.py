#!/usr/bin/env python3
# generate_charts.py
# COMP3100/6105 Assignment 2

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import sys

if len(sys.argv) > 1:
    RESULTS_DIR = sys.argv[1]
else:
    RESULTS_DIR = os.path.join(os.getcwd(), 'results')

# RESULTS_DIR = os.path.join(os.getcwd(), 'results')
CHARTS_DIR = os.path.join(RESULTS_DIR, 'charts')

os.makedirs(CHARTS_DIR, exist_ok=True)

metrics_file = os.path.join(RESULTS_DIR, 'metrics.csv')

df = pd.read_csv(metrics_file)

def create_bar_chart(metric, ylabel, title, filename):
    plt.figure(figsize=(14, 8))
    
    configs = df['Config'].unique()
    algorithms = df['Algorithm'].unique()
    x = np.arange(len(configs))
    width = 0.8 / len(algorithms)
    
    for i, alg in enumerate(algorithms):
        values = [df[(df['Algorithm'] == alg) & (df['Config'] == config)][metric].values[0] for config in configs]
        plt.bar(x + i*width - 0.4 + width/2, values, width, label=alg.upper())
    
    plt.xlabel('Config')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(x, [c.replace('ds-sample-config', 'Config ').replace('.xml', '') for c in configs])
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    for i, alg in enumerate(algorithms):
        if alg == 'tos':
            for j, config in enumerate(configs):
                value = df[(df['Algorithm'] == alg) & (df['Config'] == config)][metric].values[0]
                plt.text(j + i*width - 0.4 + width/2, value, f"{value:.1f}", 
                         ha='center', va='bottom', fontweight='bold', color='red')
    
    plt.savefig(os.path.join(CHARTS_DIR, filename), dpi=300, bbox_inches='tight')

create_bar_chart('AvgTurnaroundTime', 'AvgTurnaroundTime', 'Comparison of Avg. Turnaround Time', 'turnaround_time.png')
create_bar_chart('AvgWaitingTime', 'AvgWaitingTime', 'Comparison of Avg. Waiting Time', 'waiting_time.png')
create_bar_chart('AvgUtilization', 'AvgUtilization(%)', 'Comparison of Avg. Utilization', 'utilization.png')
create_bar_chart('TotalCost', 'TotalCost($)', 'Comparison of Total Cost', 'cost.png')
create_bar_chart('TotalServers', 'TotalServers', 'Comparison of Total Servers', 'servers.png')



def create_summary_table():
    summary_df = pd.DataFrame(columns=['Config', 'Metric', 'My Method', 'The Best Baseline', 'Baseline Value', 'Improvement'])
    
    row = 0
    for config in df['Config'].unique():
        config_df = df[df['Config'] == config]
        tos_df = config_df[config_df['Algorithm'] == 'tos']
        baseline_df = config_df[config_df['Algorithm'] != 'tos']
        
        metrics = {
            'AvgTurnaroundTime': 'AvgTurnaroundTime',
            'AvgWaitingTime': 'AvgWaitingTime',
            'TotalCost': 'TotalCost',
            'AvgUtilization': 'AvgUtilization',
            'EffectiveUsage': 'EffectiveUsage',
        }
        
        for metric, metric_name in metrics.items():
            tos_value = tos_df[metric].values[0]
            
            if metric in ['AvgTurnaroundTime', 'AvgWaitingTime', 'TotalCost']:
                best_baseline = baseline_df.loc[baseline_df[metric].idxmin()]
                best_value = best_baseline[metric]
                improvement = (best_value - tos_value) / best_value * 100
            else:
                best_baseline = baseline_df.loc[baseline_df[metric].idxmax()]
                best_value = best_baseline[metric]
                improvement = (tos_value - best_value) / best_value * 100
            
            summary_df.loc[row] = [
                config.replace('ds-sample-config', 'Config ').replace('.xml', ''),
                metric_name,
                f"{tos_value:.2f}",
                best_baseline['Algorithm'].upper(),
                f"{best_value:.2f}",
                f"{improvement:.2f}%"
            ]
            row += 1
    summary_df.to_csv(os.path.join(RESULTS_DIR, 'summary.csv'), index=False)
    
create_summary_table()

