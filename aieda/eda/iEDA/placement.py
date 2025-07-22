#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : placement.py
@Author : yell
@Desc : placement api
'''
from .io import IEDAIO
from ...workspace import Workspace
from ...flows import DbFlow

class IEDAPlacement(IEDAIO):
    """placement api"""
    def __init__(self, workspace : Workspace, flow : DbFlow):
        super().__init__(workspace=workspace, flow=flow)
        
    def build_config(self):
        self.ieda_config = self.workspace.paths_table.ieda_config['place']
        
    def run_placement(self):
        self.read_def()
        
        self.ieda.run_placer(self.ieda_config)
        
        self.def_save()
        self.verilog_save(self.cell_names)
        
        self.run_placement_feature()
    
    def run_placement_feature(self):
        ieda_feature_json = self.workspace.paths_table.ieda_feature_json
        
        # generate feature summary data
        self.ieda.feature_summary(ieda_feature_json['place_summary'])
        
        # generate feature CTS data
        self.ieda.feature_tool(ieda_feature_json['place_tool'], DbFlow.FlowStep.place.value)
        
        # generate eval metrics. The default map_grid_size is 1X row_height.
        map_grid_size = 1
        self.ieda.feature_pl_eval(ieda_feature_json['place_eval'], map_grid_size)
        
    def run_legalization(self):
        self.read_def()
        
        self.ieda.run_incremental_flow(self.ieda_config)
        
        self.def_save()
        self.verilog_save(self.cell_names)
        
        self.run_legalization_feature()
    
    def run_legalization_feature(self):
        ieda_feature_json = self.workspace.paths_table.ieda_feature_json
        
        # generate feature summary data
        self.ieda.feature_summary(ieda_feature_json['legalization_summary'])
        
        # generate feature CTS data
        self.ieda.feature_tool(ieda_feature_json['legalization_tool'], DbFlow.FlowStep.legalization.value)
        
    def run_filler(self):
        self.read_def()
        
        self.ieda.run_filler(self.ieda_config)
        
        self.def_save()
        self.verilog_save(self.cell_names)
        
        self.run_filler_feature()
    
    def run_filler_feature(self):
        ieda_feature_json = self.workspace.paths_table.ieda_feature_json
        
        # generate feature summary data
        self.ieda.feature_summary(ieda_feature_json['filler_summary'])
        
        # generate feature CTS data
        self.ieda.feature_tool(ieda_feature_json['filler_tool'], DbFlow.FlowStep.filler.value)
        
    def run_mp(self, config : str, tcl_path=""):
        self.ieda.runMP(config, tcl_path)
    
    def run_refinement(self, tcl_path=""):
        self.ieda.runRef(tcl_path)
        
    # build macro drc distribution
    def feature_macro_drc_distribution(self, path: str, drc_path: str):
        self.ieda.feature_macro_drc(path=path, drc_path=drc_path)
        
    def run_place_eval(self):
        self.read_def()
        
        ieda_feature_json = self.workspace.paths_table.ieda_feature_json
        
        self.ieda.feature_summary(ieda_feature_json['place_summary'])
        
        # TODO: mode eval metrics
        # generate eval metrics. The default map_grid_size is 1X row_height.
        map_grid_size = 1
        self.ieda.feature_pl_eval(ieda_feature_json['place_eval'], map_grid_size)
        
    def run_legalization_eval(self):
        self.read_def()
        
        ieda_feature_json = self.workspace.paths_table.ieda_feature_json
        
        self.ieda.feature_summary(ieda_feature_json['legalization_summary'])
        
        # TODO: mode eval metrics
        
    def run_filler_eval(self):
        self.read_def()
        
        ieda_feature_json = self.workspace.paths_table.ieda_feature_json
        
        self.ieda.feature_summary(ieda_feature_json['filler_summary'])
        
        # TODO: mode eval metrics
