#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : test_ieda_flows.py
@Author : yell
@Desc : test physical design flows for iEDA
'''
import os
os.environ['iEDA'] = "ON"


from aieda import (
    workspace_create,
    RunIEDA
)

if __name__ == "__main__":  
    # step 1 : create workspace
    import os
    current_dir = os.path.split(os.path.abspath(__file__))[0]
    root = current_dir.rsplit('/', 1)[0]

    workspace_dir = "{}/example/sky130_test".format(root)
    
    workspace = workspace_create(directory=workspace_dir, design="gcd")
    
    # step 2 : init iEDA by workspace
    run_ieda = RunIEDA(workspace)
    
    # step 3 : run physical backend flows configured in workspace/config/flow.json
    run_ieda.run_flows()

    exit(0)

