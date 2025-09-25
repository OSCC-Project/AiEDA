#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : test_gui.py
@Author : RuiWang
@Desc : test gui for data vectors
"""
######################################################################################
# # import aieda
# from import_aieda import import_aieda
# import_aieda()
######################################################################################

from aieda.workspace import workspace_create
from aieda.gui import GuiLayout

if __name__ == "__main__":
    import os

    current_dir = os.path.split(os.path.abspath(__file__))[0]
    root = current_dir.rsplit("/", 1)[0]

    workspace_dir = "{}/example/sky130_test".format(root)

    workspace = workspace_create(directory=workspace_dir, design="gcd")

    gui = GuiLayout(workspace)
    gui.instance_graph(workspace.paths_table.ieda_gui["instance_graph"])

    exit(0)
