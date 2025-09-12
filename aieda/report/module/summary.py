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

from aieda.report.module.design import ReportDesign

from ...data import DataVectors
from ...workspace import Workspace
from ...flows import DbFlow

from .flow import ReportFlow
from .foundry import ReportFoundry
from .vectors import ReportVectors


class ReportSummary:
    def __init__(self, workspace: Workspace, display_names_map=None):
        self.workspace = workspace
        self.content = []
        self.display_names_map = display_names_map
        
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
        self.summary_design()
        self.summary_vectors()

    def summary_flow(self):
        self.content.append("## flows".strip())
        
        self.content.append("### basic information".strip())
        flow=DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.fixFanout)
        report = ReportDesign(workspace=self.workspace, flow=flow)
        self.content.extend(report.common_report())
        
        self.content.append("### flow status".strip())
        report = ReportFlow(self.workspace)
        self.content.extend(report.flow_summary())
        
        for flow in self.workspace.configs.flows:      
            if flow.step is DbFlow.FlowStep.optSetup or flow.step is DbFlow.FlowStep.vectorization:
                continue
              
            self.content.append("### {}".format(flow.step.value).strip())
            self.content.extend(report.content_flow(flow))
        
    def summary_foundry(self):
        self.content.append("## Technology information".strip())
        
        report = ReportFoundry(self.workspace)
        self.content.append("### foundry configs".strip())
        self.content.extend(report.content_path())

        
    def summary_design(self):
        self.content.append("## Design analysis".strip())
        
        self.content.append("### Design features".strip())
        
        report = ReportVectors(self.workspace) 
        self.content.append("#### design statis".strip())
        self.content.extend(report.nets.statis_report(self.display_names_map))
        
        flow=DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.route)
        report = ReportDesign(workspace=self.workspace, flow=flow)
        self.content.append("#### cell type".strip())
        self.content.extend(report.cell_type_report(self.display_names_map))
        
        self.content.append("#### core usage".strip())
        self.content.extend(report.usage_report())
        
        self.content.append("#### pin distribution".strip())
        self.content.extend(report.pin_distribution_report(self.display_names_map))
        
    def summary_vectors(self):
        self.content.append("## Vectors analysis".strip())
        
        report = ReportVectors(self.workspace)
        
        # nets
        self.content.append("### Nets analysis".strip())
        
        self.content.append("#### net wire distribution".strip())
        self.content.extend(report.nets.wire_distribution_report(self.display_names_map))
        
        self.content.append("#### net correlation".strip())
        self.content.extend(report.nets.metrics_correlation_report(self.display_names_map))
        
        # patches
        self.content.append("### Patches analysis".strip())
        
        self.content.append("#### patch wire density".strip())
        self.content.extend(report.patches.wire_density_report(self.display_names_map))
        
        self.content.append("#### patch feature correlation".strip())
        self.content.extend(report.patches.correlation_report(self.display_names_map))
        
        self.content.append("#### patch maps".strip())
        self.content.extend(report.patches.maps_report(self.display_names_map))
        
        # paths
        self.content.append("### Paths analysis".strip())
        
        self.content.append("#### path delay".strip())
        self.content.extend(report.nets.path_delay_report(self.display_names_map))
        
        self.content.append("#### path stage delay".strip())
        self.content.extend(report.nets.path_stage_report(self.display_names_map))