#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : test_analysis_design.py
@Author : yhqiu
@Desc : test design_level data ananlysis
'''

from aieda.analysis import CellTypeAnalyzer,CoreUsageAnalyzer,PinDistributionAnalyzer,ResultStatisAnalyzer
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
        
    # step 1: test cell type analysis
    cell_analyzer = CellTypeAnalyzer()
    cell_analyzer.load(
        workspace_dirs=workspace_list,
        flow = DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.route),
        dir_to_display_name=DISPLAY_NAME
        )
    cell_analyzer.analyze()
    cell_analyzer.visualize(save_path=workspace_dir)
    
    
    # step 2: test core usage analysis
    core_analyzer = CoreUsageAnalyzer()
    core_analyzer.load(
        workspace_dirs=workspace_list,
        flow = DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.route)
    )
    core_analyzer.analyze()
    core_analyzer.visualize(save_path=workspace_dir)
    
    
    # step 3: test pin distribution analysis
    pin_analyzer = PinDistributionAnalyzer()
    pin_analyzer.load(
        workspace_dirs=workspace_list,
        flow = DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.route)
    )
    pin_analyzer.analyze()
    pin_analyzer.visualize(save_path=workspace_dir)
    
    
    # step 4: test result statistics
    result_analyzer = ResultStatisAnalyzer()
    result_analyzer.load(
        workspace_dirs=workspace_list, 
        pattern="/output/iEDA/vectors",
        dir_to_display_name=DISPLAY_NAME,
        calc_wire_num=False,  # set to False to avoid calculating wire number
    )
    result_analyzer.analyze()
    result_analyzer.visualize(save_path=workspace_dir)
    

if __name__ == "__main__":  
    main()



