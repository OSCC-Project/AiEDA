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

import aieda
from aieda import (
    workspace_create,
    DbFlow,
    load_feature_summary,
    load_feature_tool
)

if __name__ == "__main__":  
    # step 1 : create workspace
    # workspace_dir = "{}/example/backend_flow".format(root)
    workspace_dir = "/data2/huangzengrong/test_aieda/workspace"
    workspace = workspace_create(directory=workspace_dir, design="gcd")
    
    # step 2 : test get feature summary db from iEDA flow
    for step in ["fixFanout", 
                 "place",
                 "CTS",
                 "optDrv",
                 "optHold",
                 "legalization",
                 "route",
                 "filler"
                 ]:
        feature_db = load_feature_summary(workspace=workspace, 
                                  flow=DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep(step))
                                  )
        print("feature summary db in step {}".format(step))
        
    # step 3 : test get feature tool db from iEDA flow
    for step in ["fixFanout", 
                 "place",
                 "CTS",
                 "optDrv",
                 "optHold",
                 "legalization",
                 "route",
                 "filler"
                 ]:
        feature_db = load_feature_tool(workspace=workspace, 
                                  flow=DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep(step))
                                  )
        print("feature tool db in step {}".format(step))

    exit(0)

