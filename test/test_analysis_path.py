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
from aieda import (
    workspace_create,
    DbFlow
)

import os
current_dir = os.path.split(os.path.abspath(__file__))[0]
root = current_dir.rsplit('/', 1)[0]
workspace_dir = "{}/example/sky130_test".format(root)

# all workspace directory
WORKSPACES = {
    "gcd" : workspace_dir
}

# name map
DISPLAY_NAME = {
    "gcd" : "GCD"
}

def main():
    # step 0: create workspace list
    workspace_list = []
    for design, dir in WORKSPACES.items():
        workspace = workspace_create(directory=dir, design = design)
        workspace_list.append(workspace)
        
    # step 1: Path Delay Analysis
    delay_analyzer = DelayAnalyzer()
    delay_analyzer.load(
        workspace_dirs=workspace_list,
        pattern = "/output/iEDA/vectors/wire_paths",
        dir_to_display_name=DISPLAY_NAME
    )
    delay_analyzer.analyze()
    delay_analyzer.visualize(save_path=workspace_dir)
    
    # step 2: Path Stage Analysis
    stage_analyzer = StageAnalyzer()
    stage_analyzer.load(
        workspace_dirs=workspace_list,
        pattern = "/output/iEDA/vectors/wire_paths",
        dir_to_display_name=DISPLAY_NAME
    )
    stage_analyzer.analyze()
    stage_analyzer.visualize(save_path=workspace_dir)

if __name__ == "__main__":  
    main()
