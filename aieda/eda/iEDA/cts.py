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

class IEDACts(IEDAIO):
    """CTS api"""
    def __init__(self, workspace : Workspace, flow : DbFlow):
        super().__init__(workspace=workspace, flow=flow)
        
    def __configs__(self):
        super().__configs__()
        
        self.ieda_config = self.workspace.paths_table.ieda_config['CTS']
        self.result_dir = self.workspace.paths_table.ieda_output['cts']
    
    def __run_flow__(self):     
        self.read_def()
        
        self.ieda.run_cts(self.ieda_config, self.result_dir)
        self.ieda.cts_report(self.result_dir)
        
        #legalization
        self.ieda.run_incremental_flow(self.workspace.paths_table.ieda_config['legalization'])
        
        self.def_save()
        self.verilog_save(self.cell_names)
        
        self.__generate_feature_summary__()
        self.__generate_feature_map__()
        self.__generate_feature_tool__()
        
    def __generate_feature_summary__(self, json_path:str=None):
        if json_path is None:
            # use default feature path in workspace
            json_path = self.workspace.paths_table.ieda_feature_json['CTS_summary']
            
        self.read_output_def()
        
        # generate feature summary data
        self.ieda.feature_summary(json_path)
        
    def __generate_feature_tool__(self):
        self.read_output_def()

        ieda_feature_json = self.workspace.paths_table.ieda_feature_json
        
        # generate feature CTS data
        self.ieda.feature_tool(ieda_feature_json['CTS_tool'], DbFlow.FlowStep.cts.value)
        
    def __generate_feature_map__(self, map_grid_size = 1):
        self.read_output_def()

        ieda_feature_json = self.workspace.paths_table.ieda_feature_json
        
        # generate eval metrics. The default map_grid_size is 1X row_height.
        self.ieda.feature_cts_eval(ieda_feature_json['CTS_map'], map_grid_size)