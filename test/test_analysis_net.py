#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : test_analysis_net.py
@Author : yhqiu
@Desc : test net_level data ananlysis
'''

import sys
import os

# when install as package, the following code must be commented
current_dir = os.path.split(os.path.abspath(__file__))[0]
root = current_dir.rsplit('/', 1)[0]
sys.path.append(root)

from aieda.analysis import WireDistributionAnalyzer, MetricsCorrelationAnalyzer

BASE_DIRS = [
    "/data/project_share/yhqiu/s713",
    "/data/project_share/yhqiu/s44",
    "/data/project_share/yhqiu/apb4_rng",
    "/data/project_share/yhqiu/gcd",
    "/data/project_share/yhqiu/s1238",
    "/data/project_share/yhqiu/s1488",
    "/data/project_share/yhqiu/apb4_archinfo",
    "/data/project_share/yhqiu/apb4_ps2",
    "/data/project_share/yhqiu/s9234",
    "/data/project_share/yhqiu/apb4_timer",
]

DISPLAY_NAME = {
    "s713": "D1",
    "s44": "D2", 
    "apb4_rng": "D3",
    "gcd": "D4",
    "s1238": "D5",
    "s1488": "D6",
    "apb4_archinfo": "D7",
    "apb4_ps2": "D8",
    "s9234": "D9",
    "apb4_timer": "D10",
}


def main():
    # 1. Wire Distribution Analysis
    wire_analyzer = WireDistributionAnalyzer()
    wire_analyzer.load(
        base_dirs=BASE_DIRS,
        dir_to_display_name=DISPLAY_NAME,
        verbose=True
    )
    wire_analyzer.analyze()
    wire_analyzer.visualize(save_path=".")
    
    # 2. Metrics Correlation Analysis
    metric_analyzer = MetricsCorrelationAnalyzer()
    metric_analyzer.load(
        base_dirs=BASE_DIRS,
        dir_to_display_name=DISPLAY_NAME,
        verbose=True
    )
    metric_analyzer.analyze()
    metric_analyzer.visualize(save_path=".")

if __name__ == "__main__":  
    main()
