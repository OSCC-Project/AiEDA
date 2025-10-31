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
                pattern=self.workspace.get_nets_path(),
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
                pattern=self.workspace.get_nets_path(),
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
            
            analyzer = ResultStatisAnalyzer()
            
                
            analyzer.load(
                workspaces=workspace_list,
                pattern=self.workspace.get_vectors_path(),
                dir_to_display_name=display_names_map,
            )
            analyzer.analyze()
            analyzer.visualize()
            analyse_content = analyzer.report()
            
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
            
            analyzer = DelayAnalyzer()
            analyzer.load(
                workspaces=workspace_list,
                pattern=self.workspace.get_wire_paths_path(),
                dir_to_display_name=display_names_map
            )
            analyzer.analyze()
            analyzer.visualize()
            analyse_content = analyzer.report()
            
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
            
            analyzer = StageAnalyzer()
            analyzer.load(
                workspaces=workspace_list,
                pattern=self.workspace.get_wire_paths_path(),
                dir_to_display_name=display_names_map
            )
            analyzer.analyze()
            analyzer.visualize()
            analyse_content = analyzer.report()
            
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
                pattern=self.workspace.get_patchs_path(),
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
            
            analyzer = FeatureCorrelationAnalyzer()
            analyzer.load(
                workspaces=workspace_list,
                pattern=self.workspace.get_patchs_path(),
                dir_to_display_name=display_names_map,
            )
            analyzer.analyze()
            analyzer.visualize()
            analyse_content = analyzer.report()
            
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
            
            analyzer = MapAnalyzer()
            analyzer.load(
                workspaces=workspace_list,
                pattern=self.workspace.get_patchs_path(),
                dir_to_display_name=display_names_map,
            )
            analyzer.analyze()
            analyzer.visualize()
            analyse_content = analyzer.report()
            
            images = analyzer.image_paths
            
            image_gen = self.Images(images)
            iamge_content = image_gen.images_content(height="300", per_row=4)
            
            return analyse_content + iamge_content
        
        def summary_patch(self, selected_patch):
            if selected_patch is not None:
                info_str = []
                
                reportor = self.BaseHtml(self.workspace)
            
                # Add title
                info_str += reportor.make_title(f"Patch information : ID-{selected_patch.id}")
                info_str += reportor.make_line_space()
                
                # Prepare table data
                headers = ["Feature", "Value"]
                values = []
                
                # Add all VectorPatch attributes except patch_layer
                # Required attributes
                if hasattr(selected_patch, 'id'):
                    values.append(("ID", selected_patch.id))
                if hasattr(selected_patch, 'patch_id_row'):
                    values.append(("Row ID", selected_patch.patch_id_row))
                if hasattr(selected_patch, 'patch_id_col'):
                    values.append(("Column ID", selected_patch.patch_id_col))
                if hasattr(selected_patch, 'llx'):
                    values.append(("llx", selected_patch.llx))
                if hasattr(selected_patch, 'lly'):
                    values.append(("lly", selected_patch.lly))
                if hasattr(selected_patch, 'urx'):
                    values.append(("urx", selected_patch.urx))
                if hasattr(selected_patch, 'ury'):
                    values.append(("ury", selected_patch.ury))
                if hasattr(selected_patch, 'row_min'):
                    values.append(("Row min", selected_patch.row_min))
                if hasattr(selected_patch, 'row_max'):
                    values.append(("Row max", selected_patch.row_max))
                if hasattr(selected_patch, 'col_min'):
                    values.append(("Column min", selected_patch.col_min))
                if hasattr(selected_patch, 'col_max'):
                    values.append(("Column max", selected_patch.col_max))
                
                # Calculate width and height
                if all(hasattr(selected_patch, attr) for attr in ['llx', 'urx']):
                    width = selected_patch.urx - selected_patch.llx
                    values.append(("width", width))
                if all(hasattr(selected_patch, attr) for attr in ['lly', 'ury']):
                    height = selected_patch.ury - selected_patch.lly
                    values.append(("height", height))
                
                # Add patch_layer information
                if hasattr(selected_patch, 'patch_layer'):
                    values.append(("Layer count", len(selected_patch.patch_layer)))
                
                # Add all other VectorPatch attributes
                vector_patch_attrs = ['cell_density', 'pin_density', 'net_density', 'macro_margin', 
                                     'RUDY_congestion', 'EGR_congestion', 'timing_map', 'power_map', 'ir_drop_map']
                for attr_name in vector_patch_attrs:
                    if hasattr(selected_patch, attr_name):
                        attr_value = getattr(selected_patch, attr_name)
                        # Format with proper labels
                        label_map = {
                            'cell_density': 'Cell density',
                            'pin_density': 'Pin density',
                            'net_density': 'Net density',
                            'macro_margin': 'Macro margin',
                            'RUDY_congestion': 'RUDY congestion',
                            'EGR_congestion': 'EGR congestion',
                            'timing_map': 'Timing map',
                            'power_map': 'Power map',
                            'ir_drop_map': 'IR drop map'
                        }
                        display_label = label_map.get(attr_name, attr_name)
                        values.append((display_label, attr_value))
                
                # Create table and set HTML
                info_str += reportor.make_table(headers, values)
                
                return info_str
            
            return None