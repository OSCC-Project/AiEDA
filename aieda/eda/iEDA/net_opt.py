#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : net_opt.py
@Author : yell
@Desc : net opt api
'''
from .io import IEDAIO
from ...workspace import Workspace
from ...flows import DbFlow

class IEDANetOpt(IEDAIO):
    """net opt api"""
    def __init__(self, workspace : Workspace, flow : DbFlow):
        super().__init__(workspace=workspace, flow=flow)
        
    def build_config(self):
        self.ieda_config = self.workspace.paths_table.ieda_config['fixFanout']
    
    def run_fix_fanout(self):
        self.read_def()
        
        self.ieda.run_no_fixfanout(self.ieda_config)
        
        self.def_save()
        self.verilog_save(self.cell_names)
        
        self.run_feature()
    
    def run_feature(self):
        ieda_feature_json = self.workspace.paths_table.ieda_feature_json
        
        # generate feature summary data
        self.ieda.feature_summary(ieda_feature_json['fixFanout_summary'])
        
        # generate feature CTS data
        self.ieda.feature_tool(ieda_feature_json['fixFanout_tool'], DbFlow.FlowStep.fixFanout.value)
        
    def run_eval(self):
        self.read_def()

        ieda_feature_json = self.workspace.paths_table.ieda_feature_json
        
        # generate feature summary data
        self.ieda.feature_summary(ieda_feature_json['fixFanout_summary'])
        
        # TODO: more eval metrics