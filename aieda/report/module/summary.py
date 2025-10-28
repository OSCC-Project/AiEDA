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
from aieda.report.module.base import ReportBase

from ...data import DataVectors
from ...workspace import Workspace
from ...flows import DbFlow

from .flow import ReportFlow
from .foundry import ReportFoundry
from .vectors import ReportVectors


class ReportSummary:
    def __init__(self, workspace: Workspace, display_names_map=None):
        self.workspace = workspace
        self.display_names_map = display_names_map
        
    def generate_markdown(self, path : str):
        reportor = self.ReportMarkdown(self.workspace, self.display_names_map)
        content = reportor.summary_content()
            
        with open(path, 'w', encoding='utf-8') as f:
            f.write("\n".join(content))
            
    def get_markdown(self):
        reportor = self.ReportMarkdown(self.workspace, self.display_names_map)
        content = reportor.summary_content()
        
        return content
    
    def generate_html(self, path : str):   
        reportor = self.ReportHtml(self.workspace, self.display_names_map)
        content = reportor.summary_content()
        
        html_content = markdown2.markdown(content, extras=['tables', 'fenced-code-blocks'])
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"<!DOCTYPE html><html><body>{html_content}</body></html>")
    
    class ReportMarkdown:
        def __init__(self, workspace: Workspace, display_names_map=None):
            self.workspace = workspace
            self.content = []
            self.display_names_map = display_names_map
        
        def summary_content(self):
            self.content.append("# workspace summary - {} - {}".format(self.workspace.design, self.workspace.configs.workspace.process_node).strip())
            
            self.summary_foundry()
            self.summary_flows()
            self.summary_design()
            self.summary_vectors()
            
            return self.content
    
        def summary_flows(self):
            self.content.append("## flows".strip())
            
            self.content.append("### basic information".strip())
            flow=DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.place)
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
                
            return self.content
            
        def summary_foundry(self):
            self.content.append("## Technology information".strip())
            
            report = ReportFoundry(self.workspace)
            self.content.append("### foundry configs".strip())
            self.content.extend(report.content_path())
            
            return self.content
    
            
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
            
            return self.content
        
        def summary_flow(self, flow):
            report = ReportFlow(workspace=self.workspace, b_markdown=False)
            self.content.extend(report.content_flow(flow))   
            
            return self.content
            
    class ReportHtml(ReportBase.BaseHtml):
        def __init__(self, workspace: Workspace, display_names_map=None):
            self.workspace = workspace
            self.content = []
            self.display_names_map = display_names_map
        
        def summary_content(self):
            pass
    
        def summary_workspace(self):
            info_str = []
        
            info_str += self.make_title("Workspace information")
            
            info_str += self.make_parameters(("Design", self.workspace.design))
            info_str += self.make_parameters(("Directory", self.workspace.directory))
            info_str += self.make_parameters(("Process node", self.workspace.configs.workspace.process_node))
            info_str += self.make_parameters(("version", self.workspace.configs.workspace.version))
            
            info_str += self.make_seperator()
            
            info_str += self.make_title("Flows")
            
            flow_headers = ["Step", "EDA Tool", "State", "Runtime"]
            flow_values = []
            
            for flow in self.workspace.configs.flows:
                flow_values.append((flow.step.value, flow.eda_tool, flow.state.value, flow.runtime))
                 
            info_str += self.make_table(flow_headers, flow_values)
            
            return info_str
            
        def summary_net(self, vec_net):
            """处理网络选择事件，将网络详情添加到文本显示区域并滚动到底部"""
            info_str = []
            
            info_str += self.make_title(f"Net information : {vec_net.name}")
            info_str += self.make_line_space()
            
            headers = ["Feature", "Value"]
            values = []
    
            feature = vec_net.feature
            
            values.append(("llx", feature.llx))
            values.append(("lly", feature.lly))
            values.append(("urx", feature.urx))
            values.append(("ury", feature.ury))
            values.append(("width", feature.width))
            values.append(("height", feature.height))
            values.append(("area", feature.area))
            values.append(("aspect_ratio", feature.aspect_ratio))
            values.append(("wire_len", feature.wire_len))
            values.append(("via_num", feature.via_num))
            values.append(("drc_num", feature.drc_num))
            values.append(("R", feature.R))
            values.append(("C", feature.C))
            values.append(("power", feature.power))
            values.append(("delay", feature.delay))
            values.append(("slew", feature.slew))
            values.append(("volume", feature.volume))
            values.append(("l_ness", feature.l_ness))
            values.append(("layer_ratio", feature.layer_ratio))
            
            if feature.place_feature is not None:
                place_feature = feature.place_feature
                
                values.append(("placement_pin_num", place_feature.pin_num))
                values.append(("placement_aspect_ratio", place_feature.aspect_ratio))
                values.append(("placement_width", place_feature.width))
                values.append(("placement_height", place_feature.height))
                values.append(("placement_area", place_feature.area))
                values.append(("placement_l_ness", place_feature.l_ness))
                values.append(("placement_rsmt", place_feature.rsmt))
                values.append(("placement_hpwl", place_feature.hpwl))
            
            info_str += self.make_table(headers, values)
        
            return info_str
        
        def summary_flow(self, flow):
            report = ReportDesign(workspace=self.workspace, flow=flow, b_markdown=False)
            self.content.extend(report.common_report(flow))   
            
            return self.content
        
        def summary_patch(self, patch):
            report = ReportVectors(self.workspace)
            
            return report.patches.summary_patch(patch)