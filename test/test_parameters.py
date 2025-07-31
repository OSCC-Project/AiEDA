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
    workspace_dir = "/data2/huangzengrong/test_aieda/workspace2"
    workspace = workspace_create(directory=workspace_dir, design="gcd")
    workspace.print_paramters()
    
    # step test parameters config
    parameters = EDAParameters()
    parameters.placement_target_density = 0.4
    parameters.placement_max_phi_coef = 1.04
    parameters.placement_init_wirelength_coef = 0.15
    parameters.placement_min_wirelength_force_bar = -54.04
    parameters.cts_skew_bound = 0.1
    parameters.cts_max_buf_tran = 1.2
    parameters.cts_max_sink_tran = 1.1
    parameters.cts_max_cap = 0.2
    parameters.cts_max_fanout = 32
    parameters.cts_cluster_size = 32
    
    workspace.update_parameters(parameters=parameters)
    
    workspace.print_paramters()

    exit(0)

