#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : vectors.py
@Author : yell
@Desc : vectors data analyse report
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


class ReportVectors:
    def __init__(self, workspace: Workspace):
        self.workspace = workspace
        
        self.patches = self.ReportPatches(self.workspace)
        self.nets = self.ReportNets(self.workspace)
        
    def generate_markdown(self, path : str):
        pass
    
    class ReportNets(ReportBase):
        def __init__(self, workspace: Workspace):
            super().__init__(workspace=workspace)
            
        def wire_distribution_report(self, display_names_map):
            workspace_list = []
            workspace_list.append(self.workspace)
        
            # step 1: Wire Density Analysis
            from ...analysis import WireDistributionAnalyzer
            
            analyzer = WireDistributionAnalyzer()
            analyzer.load(
                workspaces=workspace_list,
                pattern=self.workspace.paths_table.ieda_vectors["nets"],
                dir_to_display_name=display_names_map,
            )
            analyzer.analyze()
            analyzer.visualize()
            analyse_content = analyzer.report()
            
            images = [
                self.get_image_path(
                image_type="net_wire_length_distribution",
                design_name=self.workspace.design)
            ]
            
            image_gen = self.Images(images)
            iamge_content = image_gen.images_content(per_row=1)
    
            return analyse_content + iamge_content
        
        def metrics_correlation_report(self, display_names_map):
            workspace_list = []
            workspace_list.append(self.workspace)
        
            # step 1: Wire Density Analysis
            from ...analysis import MetricsCorrelationAnalyzer
            
            analyzer = MetricsCorrelationAnalyzer()
            analyzer.load(
                workspaces=workspace_list,
                pattern=self.workspace.paths_table.ieda_vectors["nets"],
                dir_to_display_name=display_names_map,
            )
            analyzer.analyze()
            analyzer.visualize()
            analyse_content = analyzer.report()
            
            images = [
                self.get_image_path(
                image_type="net_correlation_matrix",
                design_name=self.workspace.design)
            ]
            
            image_gen = self.Images(images)
            iamge_content = image_gen.images_content(per_row=1)
    
            return analyse_content + iamge_content
        
        def statis_report(self, display_names_map):
            workspace_list = []
            workspace_list.append(self.workspace)
        
            from ...analysis import ResultStatisAnalyzer
            
            wire_analyzer = ResultStatisAnalyzer()
            wire_analyzer.load(
                workspaces=workspace_list,
                pattern=self.workspace.paths_table.ieda_output["vectors"],
                dir_to_display_name=display_names_map,
                calc_wire_num=False
            )
            wire_analyzer.analyze()
            wire_analyzer.visualize()
            analyse_content = wire_analyzer.report()
            
            images = [
                self.get_image_path(
                image_type="design_result_stats_overview",
                design_name=self.workspace.design),
                self.get_image_path(
                image_type="design_result_stats_heatmap",
                design_name=self.workspace.design)
            ]
            
            image_gen = self.Images(images)
            iamge_content = image_gen.images_content(per_row=2)
            
            return analyse_content + iamge_content
        
        def path_delay_report(self, display_names_map):
            workspace_list = []
            workspace_list.append(self.workspace)
        
            from ...analysis import DelayAnalyzer
            
            wire_analyzer = DelayAnalyzer()
            wire_analyzer.load(
                workspaces=workspace_list,
                pattern=self.workspace.paths_table.ieda_vectors["wire_paths"],
                dir_to_display_name=display_names_map
            )
            wire_analyzer.analyze()
            wire_analyzer.visualize()
            analyse_content = wire_analyzer.report()
            
            images = [
                self.get_image_path(
                image_type="path_delay_boxplot",
                design_name=self.workspace.design),
                self.get_image_path(
                image_type="path_delay_scatter",
                design_name=self.workspace.design)
            ]
            
            image_gen = self.Images(images)
            iamge_content = image_gen.images_content(per_row=2)
            
            return analyse_content + iamge_content
        
        def path_stage_report(self, display_names_map):
            workspace_list = []
            workspace_list.append(self.workspace)
        
            from ...analysis import StageAnalyzer
            
            wire_analyzer = StageAnalyzer()
            wire_analyzer.load(
                workspaces=workspace_list,
                pattern=self.workspace.paths_table.ieda_vectors["wire_paths"],
                dir_to_display_name=display_names_map
            )
            wire_analyzer.analyze()
            wire_analyzer.visualize()
            analyse_content = wire_analyzer.report()
            
            images = [
                self.get_image_path(
                image_type="path_stage_errorbar",
                design_name=self.workspace.design),
                self.get_image_path(
                image_type="path_stage_delay_scatter",
                design_name=self.workspace.design)
            ]
            
            image_gen = self.Images(images)
            iamge_content = image_gen.images_content(per_row=2)
            
            return analyse_content + iamge_content
    
    class ReportPatches(ReportBase):
        def __init__(self, workspace: Workspace):
            super().__init__(workspace=workspace)
            
        def wire_density_report(self, display_names_map):
            workspace_list = []
            workspace_list.append(self.workspace)
        
            # step 1: Wire Density Analysis
            from ...analysis import WireDensityAnalyzer
            
            analyzer = WireDensityAnalyzer()
            analyzer.load(
                workspaces=workspace_list,
                pattern=self.workspace.paths_table.ieda_vectors["patchs"],
                dir_to_display_name=display_names_map,
            )
            analyzer.analyze()
            analyzer.visualize()
            analyse_content = analyzer.report()
            
            images = [
                self.get_image_path(
                image_type="patch_congestion_wire_density_regression",
                design_name=self.workspace.design),
                self.get_image_path(
                image_type="patch_layer_comparison",
                design_name=self.workspace.design)
            ]
            
            image_gen = self.Images(images)
            iamge_content = image_gen.images_content(per_row=2)
    
            return analyse_content + iamge_content
        
        def correlation_report(self, display_names_map):
            workspace_list = []
            workspace_list.append(self.workspace)
        
            from ...analysis import FeatureCorrelationAnalyzer
            
            wire_analyzer = FeatureCorrelationAnalyzer()
            wire_analyzer.load(
                workspaces=workspace_list,
                pattern=self.workspace.paths_table.ieda_vectors["patchs"],
                dir_to_display_name=display_names_map,
            )
            wire_analyzer.analyze()
            wire_analyzer.visualize()
            analyse_content = wire_analyzer.report()
            
            images = [
                self.get_image_path(
                image_type="patch_feature_correlation",
                design_name=self.workspace.design),
                self.get_image_path(
                image_type="patch_feature_distributions",
                design_name=self.workspace.design)
            ]
            
            image_gen = self.Images(images)
            iamge_content = image_gen.images_content(per_row=2)
            
            return analyse_content + iamge_content
        
        def maps_report(self, display_names_map):
            workspace_list = []
            workspace_list.append(self.workspace)
        
            from ...analysis import MapAnalyzer
            
            wire_analyzer = MapAnalyzer()
            wire_analyzer.load(
                workspaces=workspace_list,
                pattern=self.workspace.paths_table.ieda_vectors["patchs"],
                dir_to_display_name=display_names_map,
            )
            wire_analyzer.analyze()
            wire_analyzer.visualize()
            analyse_content = wire_analyzer.report()
            
            images = wire_analyzer.image_paths
            
            image_gen = self.Images(images)
            iamge_content = image_gen.images_content(height="300", per_row=4)
            
            return analyse_content + iamge_content