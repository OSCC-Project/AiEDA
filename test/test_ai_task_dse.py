#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   test_dse.py
@Time    :   2025-08-19 10:29:20
@Author  :   zhanghongda
@Version :   1.0
@Contact :   zhanghongda24@mails.ucas.ac.cn
@Desc    :   test placement for dse
"""
######################################################################################
# import aieda
# from import_aieda import import_aieda
# import_aieda()
######################################################################################

from aieda.ai.design_parameter_optimization.dse_facade import DSEFacade
from aieda.data.database.enum import DSEMethod
from aieda.flows.base import DbFlow
from aieda.workspace import Workspace, workspace_create

import os

os.environ["iEDA"] = "ON"

if __name__ == "__main__":
    # change the workspace_dir to the path of your workspace
    # step 1 : create workspace
    import os

    current_dir = os.path.split(os.path.abspath(__file__))[0]
    root = current_dir.rsplit("/", 1)[0]

    workspace_dir = "{}/example/sky130_test".format(root)
    workspace = workspace_create(directory=workspace_dir, design="gcd")

    factory = DSEFacade(
        workspace=workspace,
        step=DbFlow.FlowStep.place,
        run_count=100,
    )
    factory.start(optimize=DSEMethod.NNI)
