#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : test_ieda_flows.py
@Author : yell
@Desc : test physical design flows for iEDA
'''

######################################################################################
# import aieda
from import_aieda import import_aieda
import_aieda()
######################################################################################

from aieda import (
    workspace_create,
    RunIEDA
)

if __name__ == "__main__":  
    # step 1 : create workspace
    # workspace_dir = "/data2/huangzengrong/test_aieda/minirv"
    # workspace = workspace_create(directory=workspace_dir, design="minirv")
    workspace_dir = "/data2/huangzengrong/test_aieda/workspace1"
    workspace = workspace_create(directory=workspace_dir, design="gcd")
    
    # step 2 : init iEDA by workspace
    run_ieda = RunIEDA(workspace)
    
    # step 3 : run physical backend flows configured in workspace/config/flow.json
    run_ieda.run_flows()

    exit(0)

