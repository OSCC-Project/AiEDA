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