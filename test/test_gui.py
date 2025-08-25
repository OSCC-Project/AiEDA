#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : test_gui.py
@Author : RuiWang
@Desc : test gui for data vectors
'''

######################################################################################
# import aieda
from import_aieda import import_aieda
import_aieda()
######################################################################################

from aieda import (
    workspace_create,
    DbFlow,
    GuiLayout
)
    
if __name__ == "__main__":  
    workspace_dir = "/data2/huangzengrong/test_aieda/sky130_5"
    workspace = workspace_create(directory=workspace_dir, design="gcd")
    
    gui = GuiLayout(workspace)
    gui.instance_graph(workspace.paths_table.ieda_gui['instance_graph'])

    exit(0)

