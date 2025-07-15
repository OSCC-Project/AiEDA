#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : test_ieda_backend.py
@Author : yell
@Desc : test physical design flow for iEDA
'''

######################################################################################
# import ai-eda as root

######################################################################################
import sys
import os
# set EDA tools working environment
# option : iEDA
os.environ['iEDA'] = "on"

current_dir = os.path.split(os.path.abspath(__file__))[0]
root = current_dir.rsplit('/', 1)[0]
sys.path.append(root)

from aieda.workspace import workspace_create
from aieda.flows import RunIEDA

if __name__ == "__main__":  
    # step 1 : create workspace
    # workspace_dir = "{}/example/backend_flow".format(root)
    workspace_dir = "/data2/huangzengrong/test_aieda/workspace"
    workspace = workspace_create(directory=workspace_dir, design="gcd")
    
    # step 2 : init iEDA by workspace
    run_ieda = RunIEDA(workspace)
    
    # step 3 : run physical backend flows that config in workspace/config/flow.json
    run_ieda.run_flows(reset=True)

    exit(0)

