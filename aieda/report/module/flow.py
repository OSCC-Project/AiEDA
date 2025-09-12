#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : summary.py
@Author : yell
@Desc : summary reports for workspace
"""

import os

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np

from ...data import DataVectors
from ...workspace import Workspace
from ...data import DataFeature
from ...flows import DbFlow
from .base import ReportBase

class ReportFlow(ReportBase):
    def __init__(self, workspace: Workspace):
        super().__init__(workspace=workspace)
        
    def generate_markdown(self, path : str):
        pass
    
    def flow_summary(self):  
        table = self.TableMatrix(headers=["step", "eda tool", "state", "runtime"])
        
        # flow states
        for flow in self.workspace.configs.flows:
            if flow.step is DbFlow.FlowStep.optSetup:
                continue
            
            table.add_row([flow.step.value, 
                           flow.eda_tool, 
                           flow.state.value,
                           flow.runtime])
            
        return table.make_table() 
    
    def content_flow(self, flow : DbFlow):
        if flow.step is DbFlow.FlowStep.drc:
            return self.make_drc_content()
        
        table = self.TableParameters(max_num=5)   
        
        feature = DataFeature(workspace=self.workspace)
        
        # make summary
        def make_summary_content():
            feature_db = feature.load_feature_summary(flow)
            if feature_db is None:
                return ""
            table.add_class_members(feature_db.info)
            table.add_class_members(feature_db.statis)
            table.add_class_members(feature_db.layout)
        
        # make tools
        def make_tool_content():
            feature_db = feature.load_feature_tool(flow)
            if feature_db is None:
                if flow.step is DbFlow.FlowStep.drc:
                    pass
                else:
                    return ""
    
            match(flow.step):
                case DbFlow.FlowStep.fixFanout:
                    table.add_class_members(feature_db.no_summary)
                        
                case DbFlow.FlowStep.place:
                    table.add_class_members(feature_db.place_summary)
                
                case DbFlow.FlowStep.cts:
                    table.add_class_members(feature_db.cts_summary)
                    
                case DbFlow.FlowStep.optDrv:
                    table.add_class_members(feature_db.opt_drv_summary)
                    
                case DbFlow.FlowStep.optHold:
                    table.add_class_members(feature_db.opt_hold_summary)
                    
                case DbFlow.FlowStep.legalization:
                    table.add_class_members(feature_db.legalization_summary)
                    
                case DbFlow.FlowStep.route:
                    self.make_route_content()
        
        make_summary_content()
        make_tool_content()
        
        return table.make_table()
    
    def make_route_content(self):
        pass
    
    def make_drc_content(self):
        import copy

        
        
        # make layer
        feature = DataFeature(workspace=self.workspace)
        feature_db = feature.load_feature_summary(
            flow=DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.fixFanout)
        )
        
        headers = []
        layer_dict = {}
        
        headers.append("")
        for layer in feature_db.layers.routing_layers:
            layer_dict[layer.layer_name] = 0
            headers.append(layer.layer_name)
            
        for layer in feature_db.layers.cut_layers:
            layer_dict[layer.layer_name] = 0
            headers.append(layer.layer_name)
        
        headers.append("total")
        layer_dict["total"] = 0
        
        feature = DataFeature(workspace=self.workspace)
        feature_db = feature.load_drc()
        if feature_db is None:
            return ""
        
        # make drc type
        drc_dict = {}
        drc_total_dict= copy.deepcopy(layer_dict)
        
        for type_data in feature_db.drc_list:
            if type_data.type not in drc_dict:
                drc_dict[type_data.type] = copy.deepcopy(layer_dict)
            
            for layer_data in type_data.layers:
                drc_dict[type_data.type][layer_data.layer] = drc_dict[type_data.type][layer_data.layer] + layer_data.number
                
                drc_total_dict[layer_data.layer] = drc_total_dict[layer_data.layer] + layer_data.number
            
            drc_dict[type_data.type]["total"] = type_data.number
                
        
        drc_total_dict["total"] = feature_db.number
        drc_dict["total"] = drc_total_dict
        
        table = self.TableMatrix(headers=headers)
        
        # flow states
        for key, layer_dict in drc_dict.items():
            lines = []
            
            for header in headers:
                if header == "":
                    lines.append(key)
                else:
                    for layer_key, layer_value in layer_dict.items():
                        if header == layer_key:
                            lines.append(layer_value)
                
            table.add_row(lines)        
            
        return table.make_table() 
            
        