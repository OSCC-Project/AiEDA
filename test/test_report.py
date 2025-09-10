#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : test_report.py
@Author : yell
@Desc : test report 
"""
######################################################################################
# # import aieda
# from import_aieda import import_aieda
# import_aieda()
######################################################################################

from aieda.workspace import workspace_create
from aieda.report import ReportGenerator

def workspace_report():
    import os

    current_dir = os.path.split(os.path.abspath(__file__))[0]
    root = current_dir.rsplit("/", 1)[0]

    workspace_dir = "{}/example/sky130_test".format(root)

    workspace = workspace_create(directory=workspace_dir, design="gcd")

    report = ReportGenerator(workspace)
    report.generate_report_workspace()
    
def workspace_list_report():
    pass

if __name__ == "__main__":
    workspace_report()

    exit(0)
