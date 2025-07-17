#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : test_ieda_steps.py
@Author : yell
@Desc : test physical design steps for iEDA
'''

######################################################################################
# import aieda
from import_aieda import import_aieda
import_aieda()
######################################################################################

from aieda import (
    workspace_create,
    RunIEDA,
    DbFlow
)

if __name__ == "__main__":  
    # step 1 : create workspace
    # workspace_dir = "{}/example/backend_flow".format(root)
    # workspace_dir = "/data2/huangzengrong/test_aieda/workspace1"
    workspace_dir = "/data2/huangzengrong/test_aieda/sky130"
    workspace = workspace_create(directory=workspace_dir, design="gcd")
    
    # step 2 : init iEDA by workspace
    run_ieda = RunIEDA(workspace)
    
    # step 3 : run each step of physical flow by iEDA 
    run_ieda.run_fixFanout(input_def=workspace.configs.paths.def_input_path)
    
    run_ieda.run_placement(input_def=workspace.configs.get_output_def(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.fixFanout)))
    
    run_ieda.run_CTS(input_def=workspace.configs.get_output_def(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.place)))
    
    run_ieda.run_optimizing_drv(input_def=workspace.configs.get_output_def(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.cts)))
    
    run_ieda.run_optimizing_hold(input_def=workspace.configs.get_output_def(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.optDrv)))
    
    run_ieda.run_legalization(input_def=workspace.configs.get_output_def(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.optHold)))
    
    run_ieda.run_routing(input_def=workspace.configs.get_output_def(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.legalization)))
    
    run_ieda.run_filler(input_def=workspace.configs.get_output_def(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.route)))

    exit(0)

