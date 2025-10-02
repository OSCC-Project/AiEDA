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

def report_summary(workspace):
    from aieda.report import ReportGenerator
    
    DISPLAY_NAME = {"gcd": "GCD"}
    
    report = ReportGenerator(workspace)
    report.generate_report_workspace(display_names_map=DISPLAY_NAME)
    
def workspace_list_report():
    pass

if __name__ == "__main__":
    import os
    current_dir = os.path.split(os.path.abspath(__file__))[0]
    root = current_dir.rsplit("/", 1)[0]

    workspace_dir = "{}/example/sky130_test".format(root)
    workspace = workspace_create(workspace_dir, "gcd")

    report_summary(workspace)

    exit(0)
