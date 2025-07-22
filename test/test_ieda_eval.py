#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : test_ieda_eval.py
@Author : yhqiu
@Desc : specify the workspace and DEF name, directly output summary.json and eval metrics
'''

######################################################################################
# import aieda
from import_aieda import import_aieda
import_aieda()
######################################################################################

from aieda import (
    workspace_create,
    RunEval,
    DbFlow
)

if __name__ == "__main__":  
    # step 1 : create workspace
    # workspace_dir = "/data2/huangzengrong/test_aieda/workspace1"
    workspace_dir = "/data/project_share/yhqiu/test_aieda/workspace_rerun"
    workspace = workspace_create(directory=workspace_dir, design="gcd")
    # specify input DEF for evaluation
    workspace.set_def_input("{}/output/iEDA/result/gcd_place.def.gz".format(workspace_dir))

    # step 2 : init eval by workspace
    run_ieda = RunEval(workspace)
    
    # step 3 : eval stage
    run_ieda.run_placement_eval(input_def=workspace.configs.paths.def_input_path)
    
    # change the input DEF and run the coorresponding eval stage
    # run_ieda.run_floorplan_eval(input_def=workspace.configs.paths.def_input_path)
    # run_ieda.run_fixFanout_eval(input_def=workspace.configs.paths.def_input_path)
    # run_ieda.run_CTS_eval(input_def=workspace.configs.get_output_def(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.place)))
    # run_ieda.run_optimizing_drv_eval(input_def=workspace.configs.get_output_def(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.cts)))
    # run_ieda.run_optimizing_hold_eval(input_def=workspace.configs.get_output_def(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.optDrv)))
    # run_ieda.run_legalization_eval(input_def=workspace.configs.get_output_def(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.optHold)))
    # run_ieda.run_routing_eval(input_def=workspace.configs.get_output_def(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.legalization)))
    # run_ieda.run_filler_eval(input_def=workspace.configs.get_output_def(DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.route)))

    exit(0)

