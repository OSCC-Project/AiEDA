#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : test_analysis_patch.py
@Author : yhqiu
@Desc : test patch_level data ananlysis
'''

######################################################################################
# import aieda
from import_aieda import import_aieda
import_aieda()
######################################################################################

from aieda.analysis import WireDensityAnalyzer, FeatureCorrelationAnalyzer, MapAnalyzer
from aieda import (
    workspace_create,
    DbFlow
)
import os

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
    # step 0: create workspace list
    workspace_list = []
    for base_dir in BASE_DIRS:
        workspace = workspace_create(directory=base_dir+"/workspace", design = os.path.basename(base_dir))
        workspace_list.append(workspace)
        
    # step 1: Wire Density Analysis
    wire_analyzer = WireDensityAnalyzer()
    wire_analyzer.load(
        workspace_dirs=workspace_list,
        pattern = "/output/innovus/vectors/patchs",
        dir_to_display_name=DISPLAY_NAME
    )
    wire_analyzer.analyze()
    wire_analyzer.visualize(save_path = '.')
    
    # step 2: Feature Correlation Analysis
    feature_analyzer = FeatureCorrelationAnalyzer()
    feature_analyzer.load(
        workspace_dirs=workspace_list,
        pattern = "/output/innovus/vectors/patchs",
        dir_to_display_name=DISPLAY_NAME
        
    )
    feature_analyzer.analyze()
    feature_analyzer.visualize(save_path = '.')
    
    # step 3: Map Analysis
    workspace_dir = workspace_create(directory="/data2/project_share/dataset_baseline/aes/workspace", design="aes")
    map_analyzer = MapAnalyzer()
    map_analyzer.load(
        workspace_dirs=[workspace_dir],
        pattern = "/output/innovus/vectors/patchs",
        dir_to_display_name={"aes": "AES"}
    )
    map_analyzer.analyze()
    map_analyzer.visualize(save_path = '.')
    

if __name__ == "__main__":  
    main()
