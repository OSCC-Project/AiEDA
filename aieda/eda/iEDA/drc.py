#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : drc.py
@Author : yell
@Desc : DRC api
'''
from .io import IEDAIO
from ...workspace import Workspace
from ...flows import DbFlow

class IEDADrc(IEDAIO): 
    """DRC api"""
    def __init__(self, workspace : Workspace, flow : DbFlow):
        super().__init__(workspace=workspace, flow=flow)
        
    def __configs__(self):
        super().__configs__()
        
        self.ieda_config = self.workspace.paths_table.ieda_config['drc']
        self.report_path = self.workspace.paths_table.ieda_report['drc']
        self.feature_path = self.workspace.paths_table.ieda_feature_json['route_drc']
        
    def __run_flow__(self):
        self.read_def()
        
        self.ieda.init_drc(temp_directory_path = self.workspace.paths_table.ieda_output['drc'], 
                           thread_number = 128, 
                           golden_directory_path="")
        
        self.ieda.run_drc(config = self.ieda_config, report = self.report_path)
        
        self.ieda.save_drc(path = self.feature_path)