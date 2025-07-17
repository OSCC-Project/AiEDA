#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : test_analysis_path.py
@Author : yhqiu
@Desc : test path_level data ananlysis
'''

######################################################################################
# import aieda
from import_aieda import import_aieda
import_aieda()
######################################################################################

from aieda.analysis import DelayAnalyzer, StageAnalyzer

BASE_DIRS = [
    "/data2/project_share/dataset_baseline/s713",
    "/data2/project_share/dataset_baseline/s44",
    "/data2/project_share/dataset_baseline/apb4_rng",
    "/data2/project_share/dataset_baseline/gcd",
    "/data2/project_share/dataset_baseline/s1238",
    "/data2/project_share/dataset_baseline/s1488",
    "/data2/project_share/dataset_baseline/apb4_archinfo",
    "/data2/project_share/dataset_baseline/apb4_ps2",
    "/data2/project_share/dataset_baseline/s9234",
    "/data2/project_share/dataset_baseline/apb4_timer",
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
    # 1. Path Delay Analysis
    delay_analyzer = DelayAnalyzer()
    delay_analyzer.load(
        base_dirs=BASE_DIRS,
        dir_to_display_name=DISPLAY_NAME,
        pattern = "workspace/output/innovus/feature/large_model/wire_paths/wire_path_*.yml"
    )
    delay_analyzer.analyze()
    delay_analyzer.visualize(save_path = '.')
    
    # 2. Path Stage Analysis
    stage_analyzer = StageAnalyzer()
    stage_analyzer.load(
        base_dirs=BASE_DIRS,
        dir_to_display_name=DISPLAY_NAME,
        pattern = "workspace/output/innovus/feature/large_model/wire_paths/wire_path_*.yml"
    )
    stage_analyzer.analyze()
    stage_analyzer.visualize(save_path = '.')

if __name__ == "__main__":  
    main()
