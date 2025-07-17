#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : test_ieda_feature.py
@Author : yell
@Desc : test physical design features for iEDA
'''
######################################################################################
# import aieda
from import_aieda import import_aieda
import_aieda()
######################################################################################

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

