#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : design.py
@Author : yell
@Desc : design feature analyse report
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


class ReportDesign(ReportBase):
    def __init__(self, workspace: Workspace, flow : DbFlow):
        super().__init__(workspace=workspace)
        self.flow = flow
        
    def generate_markdown(self, path : str):
        pass
    
    def common_report(self):  
        table = self.TableParameters(max_num=7) 

        feature = DataFeature(workspace=self.workspace)
        feature_db = feature.load_feature_summary(
            flow=DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.fixFanout)
        )
        
        table.add_parameter("dbu", feature_db.layout.design_dbu)
        table.add_parameter("die area", feature_db.layout.die_area)
        table.add_parameter("core area", feature_db.layout.core_area)
        table.add_parameter("layer num", feature_db.statis.num_layers)
        table.add_parameter("routing layer", feature_db.statis.num_layers_routing)
        table.add_parameter("cut layer", feature_db.statis.num_layers_cut)
        table.add_parameter("io pin num", feature_db.statis.num_iopins)
            
        return table.make_table()
    
            
    def cell_type_report(self, display_names_map):
        workspace_list = []
        workspace_list.append(self.workspace)
    
        # step 1: Wire Density Analysis
        from ...analysis import CellTypeAnalyzer
        
        analyzer = CellTypeAnalyzer()
        analyzer.load(
            workspaces=workspace_list,
            flow=self.flow,
            dir_to_display_name=display_names_map,
        )
        analyzer.analyze()
        analyzer.visualize()
        analyse_content = analyzer.report()
        
        images = [
            self.get_image_path(
            image_type="design_cell_type_top_10",
            design_name=self.workspace.design),
            self.get_image_path(
            image_type="design_cell_type_bottom_10",
            design_name=self.workspace.design)
        ]
        
        image_gen = self.Images(images)
        iamge_content = image_gen.images_content(per_row=2)

        return analyse_content + iamge_content
    
    def usage_report(self):
        workspace_list = []
        workspace_list.append(self.workspace)
    
        # step 1: Wire Density Analysis
        from ...analysis import CoreUsageAnalyzer
        
        analyzer = CoreUsageAnalyzer()
        analyzer.load(
            workspaces=workspace_list,
            flow=self.flow,
        )
        analyzer.analyze()
        analyzer.visualize()
        analyse_content = analyzer.report()
        
        images = [
            self.get_image_path(
            image_type="design_core_usage_hist",
            design_name=self.workspace.design)
        ]
        
        image_gen = self.Images(images)
        iamge_content = image_gen.images_content(per_row=1)

        return analyse_content + iamge_content
    
    def pin_distribution_report(self, display_names_map):
        workspace_list = []
        workspace_list.append(self.workspace)
    
        # step 1: Wire Density Analysis
        from ...analysis import PinDistributionAnalyzer
        
        analyzer = PinDistributionAnalyzer()
        analyzer.load(
            workspaces=workspace_list,
            flow=self.flow
        )
        analyzer.analyze()
        analyzer.visualize()
        analyse_content = analyzer.report()
        
        images = [
            self.get_image_path(
            image_type="design_pin_vs_net_ratio",
            design_name=self.workspace.design)
        ]
        
        image_gen = self.Images(images)
        iamge_content = image_gen.images_content(per_row=1)

        return analyse_content + iamge_content