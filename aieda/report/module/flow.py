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
    def __init__(self, workspace: Workspace, b_markdown=True):
        super().__init__(workspace=workspace)
        self.b_markdown = b_markdown
        
    def generate_markdown(self, path : str):
        pass
    
    def flow_summary(self):  
        table = self.TableMatrix(headers=["step", "eda tool", "state", "runtime"])
        
        # flow states
        instance_nums = []
        net_nums = []
        for flow in self.workspace.configs.flows:
            if flow.step is DbFlow.FlowStep.floorplan or flow.step is DbFlow.FlowStep.pdn \
                or flow.step is DbFlow.FlowStep.optSetup or flow.step is DbFlow.FlowStep.drc \
                    or flow.step is DbFlow.FlowStep.vectorization:
                continue
            
            table.add_row([flow.step.value, 
                           flow.eda_tool, 
                           flow.state.value,
                           flow.runtime])
            
            feature = DataFeature(workspace=self.workspace)
            feature_db = feature.load_feature_summary(flow)
            instance_nums.append(feature_db.statis.num_instances)
            net_nums.append(feature_db.statis.num_nets)
            
        return table.make_table() + self.flow_summary_image(instance_nums, net_nums)
            
    def flow_summary_image(self, instance_nums, net_nums):
        """
        Create a summary image showing instance and net counts across different steps.
        
        Args:
            instance_nums: List of instance counts for each step
            net_nums: List of net counts for each step
        
        Returns:
            None
        """
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Generate x-axis values (steps)
        steps = list(range(len(instance_nums)))
        
        # Find minimum value for y-axis start
        min_value = min(min(instance_nums), min(net_nums))
        
        # Plot instance counts
        ax.plot(steps, instance_nums, marker='o', linestyle='-', color='blue', label='Instances')
        
        # Plot net counts
        ax.plot(steps, net_nums, marker='s', linestyle='--', color='red', label='Nets')
        
        # Set y-axis to start from minimum value
        ax.set_ylim(bottom=min_value - (min_value * 0.1))  # Add 10% padding below minimum
        
        # Customize plot
        ax.set_xlabel('Step')
        ax.set_ylabel('Count')
        ax.set_title('Flow Summary: Instances and Nets')
        ax.set_xticks(steps)
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Ensure directory exists
        image_path = self.workspace.paths_table.analysis_images["flow_summary"]
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        
        # Save the figure
        plt.tight_layout()
        plt.savefig(image_path, dpi=300)
        plt.close(fig) 

        image_gen = self.Images([image_path])
        iamge_content = image_gen.images_content(per_row=1)

        return iamge_content
    
    def content_flow(self, flow : DbFlow):
        if flow.step is DbFlow.FlowStep.drc:
            return self.make_drc_content()
        
        table = self.TableParameters(max_num=2)   
        
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
            
        