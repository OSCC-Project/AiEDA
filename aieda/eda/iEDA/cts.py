#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : cts.py
@Author : yell
@Desc : CTS api
'''
from .io import IEDAIO
from ...workspace import Workspace
from ...flows import DbFlow
from ...data.database.enum import FeatureOption

class IEDACts(IEDAIO):
    """CTS api"""
    def __init__(self, workspace : Workspace, flow : DbFlow):
        super().__init__(workspace=workspace, flow=flow)
        
    def build_config(self):
        self.ieda_config = self.workspace.paths_table.ieda_config['CTS']
        self.result_dir = self.workspace.paths_table.ieda_output['cts']
    
    def run_cts(self):
        self.read_def()
        
        self.ieda.run_cts(self.ieda_config, self.result_dir)
        self.ieda.cts_report(self.result_dir)
        
        self.ieda.run_incremental_flow(self.workspace.paths_table.ieda_config['place'])
        
        self.def_save()
        self.verilog_save(self.cell_names)
        
        self.run_feature()
    
    def run_feature(self):
        ieda_feature_json = self.workspace.paths_table.ieda_feature_json
        
        # generate feature summary data
        self.ieda.feature_summary(ieda_feature_json['CTS_summary'])
        
        # generate feature CTS data
        self.ieda.feature_tool(ieda_feature_json['CTS_tool'], DbFlow.FlowStep.cts.value)
        
        # generate eval metrics. The default map_grid_size is 1X row_height.
        map_grid_size = 1
        self.ieda.feature_cts_eval(ieda_feature_json['CTS_eval'], map_grid_size)