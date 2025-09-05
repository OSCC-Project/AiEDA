#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : test_parameters.py
@Author : yell
@Desc : test all parameters in AiEDA
"""
######################################################################################
# # import aieda
# from import_aieda import import_aieda
# import_aieda()
######################################################################################

from aieda.workspace import workspace_create
from aieda.data.database import EDAParameters

if __name__ == "__main__":
    # step 1 : create workspace
    import os

    current_dir = os.path.split(os.path.abspath(__file__))[0]
    root = current_dir.rsplit("/", 1)[0]

    workspace_dir = "{}/example/sky130_test".format(root)

    workspace = workspace_create(directory=workspace_dir, design="gcd")
    workspace.print_paramters()

    # step 2 : test parameters config
    parameters = EDAParameters()
    parameters.placement_target_density = 0.4
    parameters.placement_max_phi_coef = 1.04
    parameters.placement_init_wirelength_coef = 0.15
    parameters.placement_min_wirelength_force_bar = -54.04
    parameters.cts_skew_bound = "0.1"
    parameters.cts_max_buf_tran = "1.2"
    parameters.cts_max_sink_tran = "1.1"    
    parameters.cts_max_cap = "0.2"
    parameters.cts_max_fanout = "32"
    parameters.cts_cluster_size = "32"
    workspace.update_parameters(parameters=parameters)

    workspace.print_paramters()

    exit(0)
