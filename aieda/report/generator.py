#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : generator.py
@Author : yell
@Desc : generate reports for workspace
"""

from ..workspace import Workspace
from .module import ReportSummary

class ReportGenerator:
    def __init__(self, workspace: Workspace):
        self.workspace = workspace
        
    def generate_report_workspace(self, display_names_map):
        report = ReportSummary(workspace=self.workspace, display_names_map=display_names_map)
        report.generate_markdown(self.workspace.paths_table.report["summary_md"])
        # report.generate_html(self.workspace.paths_table.report["summary_html"])
    
