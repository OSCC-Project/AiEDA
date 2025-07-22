#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : timing_opt.py
@Author : yell
@Desc : timing opt api
'''
from .io import IEDAIO
from ...workspace import Workspace
from ...flows import DbFlow

class IEDATimingOpt(IEDAIO):
    """timing opt api"""
    def __init__(self, workspace : Workspace, flow : DbFlow):
        super().__init__(workspace=workspace, flow=flow)
        
    def run_to_drv(self):
        self.ieda_config = self.workspace.paths_table.ieda_config['optDrv']
        
        self.read_def()
        
        self.ieda.run_to_drv(self.ieda_config)
        
        self.def_save()
        self.verilog_save(self.cell_names)
        
        self.run_opt_drv_feature()
    
    def run_opt_drv_feature(self):
        ieda_feature_json = self.workspace.paths_table.ieda_feature_json
        
        # generate feature summary data
        self.ieda.feature_summary(ieda_feature_json['optDrv_summary'])
        
        # generate feature CTS data
        self.ieda.feature_tool(ieda_feature_json['optDrv_tool'], DbFlow.FlowStep.optDrv.value)
        
    def run_to_hold(self):
        self.ieda_config = self.workspace.paths_table.ieda_config['optHold']
        
        self.read_def()
        
        self.ieda.run_to_hold(self.ieda_config)
        
        self.def_save()
        self.verilog_save(self.cell_names)
        
        self.run_opt_hold_feature()
    
    def run_opt_hold_feature(self):
        ieda_feature_json = self.workspace.paths_table.ieda_feature_json
        
        # generate feature summary data
        self.ieda.feature_summary(ieda_feature_json['optHold_summary'])
        
        # generate feature CTS data
        self.ieda.feature_tool(ieda_feature_json['optHold_tool'], DbFlow.FlowStep.optHold.value)
        
    def run_to_setup(self):
        self.ieda_config = self.workspace.paths_table.ieda_config['optSetup']
        
        self.read_def()
        
        self.ieda.run_to_setup(self.ieda_config)
        
        self.def_save()
        self.verilog_save(self.cell_names)
        
        self.run_opt_setup_feature()
    
    def run_opt_setup_feature(self):
        ieda_feature_json = self.workspace.paths_table.ieda_feature_json
        
        # generate feature summary data
        self.ieda.feature_summary(ieda_feature_json['optSetup_summary'])
        
        # generate feature CTS data
        self.ieda.feature_tool(ieda_feature_json['optSetup_tool'], DbFlow.FlowStep.optSetup.value)
        
    def run_drv_eval(self):
        self.read_def()
        
        ieda_feature_json = self.workspace.paths_table.ieda_feature_json
        
        # generate feature summary data
        self.ieda.feature_summary(ieda_feature_json['optDrv_summary'])
        
        # TODO: more eval metrics
        
    def run_hold_eval(self):
        self.read_def()
        
        ieda_feature_json = self.workspace.paths_table.ieda_feature_json
        
        # generate feature summary data
        self.ieda.feature_summary(ieda_feature_json['optHold_summary'])
        
        # TODO: more eval metrics
        
    def run_setup_eval(self):
        self.read_def()
        
        ieda_feature_json = self.workspace.paths_table.ieda_feature_json
        
        # generate feature summary data
        self.ieda.feature_summary(ieda_feature_json['optSetup_summary'])
        
        # TODO: more eval metrics
        