#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : test_parameters.py
@Author : yell
@Desc : test all parameters in AiEDA
'''

######################################################################################
# import aieda
from import_aieda import import_aieda
import_aieda()
######################################################################################

from aieda import (
    workspace_create,
    EDAParameters
)

if __name__ == "__main__":  
    # step 1 : create workspace
    # workspace_dir = "/data2/huangzengrong/test_aieda/workspace1"
    workspace_dir = "/data2/huangzengrong/test_aieda/sky130"
    workspace = workspace_create(directory=workspace_dir, design="gcd")
    workspace.print_paramters()
    
    # step test parameters config
    parameters = EDAParameters()
    parameters.placement_target_density = 0.8
    
    workspace.update_parameters(parameters=parameters)
    
    workspace.print_paramters()

    exit(0)

