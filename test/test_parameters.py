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
    import os
    current_dir = os.path.split(os.path.abspath(__file__))[0]
    root = current_dir.rsplit('/', 1)[0]

    workspace_dir = "{}/example/sky130_test".format(root)
    
    workspace = workspace_create(directory=workspace_dir, design="gcd")
    workspace.print_paramters()
    
    # step 2 : test parameters config
    parameters = EDAParameters(workspace_dir=workspace_dir) 
    workspace.update_parameters(parameters=parameters)
    
    workspace.print_paramters()

    exit(0)

