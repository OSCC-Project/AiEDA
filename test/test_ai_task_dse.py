#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_dse.py
@Time    :   2025-08-19 10:29:20
@Author  :   zhanghongda
@Version :   1.0
@Contact :   zhanghongda24@mails.ucas.ac.cn
@Desc    :   test placement for dse   
'''

######################################################################################
# import aieda
from import_aieda import import_aieda
import_aieda()
######################################################################################

from aieda.ai.design_parameter_optimization.dse_facade import DSEFacade
from aieda.data.database.enum import DSEMethod
from aieda.flows.base import DbFlow

if __name__ == "__main__":  
    #change the workspace_dir to the path of your workspace
    workspace_dir = "/home/zhanghongda/test_aieda/workspace_sky130_gcd"
    project_name = "gcd"
    step = DbFlow.FlowStep.place

    factory = DSEFacade(
        workspace_root=workspace_dir,
        project_name=project_name,
        step=step,
    )
    factory.start(optimize=DSEMethod.NNI)