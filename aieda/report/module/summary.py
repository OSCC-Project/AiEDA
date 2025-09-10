#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : summary.py
@Author : yell
@Desc : summary reports for workspace
"""

import os
import markdown2

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np

from ...data import DataVectors
from ...workspace import Workspace
from ...flows import DbFlow

from .flow import ReportFlow
from .foundry import ReportFoundry


class ReportSummary:
    def __init__(self, workspace: Workspace):
        self.workspace = workspace
        self.content = []
        
    def generate_markdown(self, path : str):
        self.summary_content()
            
        with open(path, 'w', encoding='utf-8') as f:
            f.write("\n".join(self.content))
    
    def generate_html(self, path : str):   
        self.summary_content()
        
        html_content = markdown2.markdown(self.content, extras=['tables', 'fenced-code-blocks'])
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"<!DOCTYPE html><html><body>{html_content}</body></html>")
    
    def summary_content(self):
        self.content.append("# workspace summary - {} - {}".format(self.workspace.design, self.workspace.configs.workspace.process_node).strip())
        
        self.summary_foundry()
        self.summary_flow()

    def summary_flow(self):
        self.content.append("## flows".strip())
        
        self.content.append("### summary".strip())
        report = ReportFlow(self.workspace)
        self.content.extend(report.flow_summary())
        
        for flow in self.workspace.configs.flows:           
            self.content.append("### {}".format(flow.step.value).strip())
            self.content.extend(report.content_flow(flow))
        
    def summary_foundry(self):
        self.content.append("## Technology information".strip())
        
        report = ReportFoundry(self.workspace)
        self.content.append("### foundry configs".strip())
        self.content.extend(report.content_path())
        
        self.content.append("### Tech.".strip())
        self.content.extend(report.content_tech())
        
    def summary_design(self):
        self.content.append("## Technology information".strip())
        
        report = ReportFoundry(self.workspace)
        self.content.append("### foundry configs".strip())
        self.content.extend(report.content_path())
        
        self.content.append("### Tech.".strip())
        self.content.extend(report.content_tech())
        
