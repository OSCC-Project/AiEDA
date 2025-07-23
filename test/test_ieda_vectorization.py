#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : test_ieda_vectorization.py
@Author : yell
@Desc : test data vectorization for iEDA
'''
######################################################################################
# import aieda
from import_aieda import import_aieda
import_aieda()
######################################################################################

from aieda import (
    workspace_create,
    RunIEDA,
    DbFlow,
)

if __name__ == "__main__":  
    # step 1 : create workspace
    workspace_dir = "/data2/huangzengrong/test_aieda/workspace"
    workspace = workspace_create(directory=workspace_dir, design="gcd")
    
    # step 2 : init iEDA by workspace
    run_ieda = RunIEDA(workspace)
    
    # step 3 : generate vectors
    flow = DbFlow(eda_tool="iEDA", 
           step=DbFlow.FlowStep.vectorization, 
           input_def="/data2/huangzengrong/test_aieda/workspace/output/innovus/result/gcd_route.def")
    run_ieda.run_flow(flow)

    exit(0)

