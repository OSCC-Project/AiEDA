#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : test_ieda_evaluation.py
@Author : yhqiu
@Desc : test ieda evaluation API
'''

######################################################################################
# import aieda
from import_aieda import import_aieda
import_aieda()
######################################################################################


from aieda import (
    workspace_create,
    DbFlow,
    IEDAEvaluation
)

if __name__ == "__main__":  
    # step 1 : create workspace
    workspace_dir = "/data/project_share/yhqiu/test_aieda/workspace_rerun"
    workspace = workspace_create(directory=workspace_dir, design="gcd")
    
    # step 2: init evaluation by workspace
    run_eval = IEDAEvaluation(workspace=workspace, 
                              flow=DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.place))
    
    # step 3: run iEDA wirelength evaluation
    hpwl = run_eval.total_wirelength_hpwl()
    print("Total HPWL: {}".format(hpwl))

    stwl = run_eval.total_wirelength_stwl()
    print("Total STWL: {}".format(stwl))

    grwl = run_eval.total_wirelength_grwl()
    print("Total GRWL: {}".format(grwl))
    
    # step 4: run iEDA density evaluation
    max_density, avg_density = run_eval.cell_density(bin_cnt_x=256, bin_cnt_y=256, save_path="./cell_density.csv")
    print("Max cell density: {}, Avg cell density: {}".format(max_density, avg_density))
    
    max_density, avg_density = run_eval.pin_density(bin_cnt_x=256, bin_cnt_y=256, save_path="./pin_density.csv")
    print("Max pin density: {}, Avg pin density: {}".format(max_density, avg_density))
    
    max_density, avg_density = run_eval.net_density(bin_cnt_x=256, bin_cnt_y=256, save_path="./net_density.csv")
    print("Max net density: {}, Avg net density: {}".format(max_density, avg_density))

    
    
    exit(0)