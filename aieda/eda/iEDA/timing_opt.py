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
        
    def run_to_hold(self):
        self.ieda_config = self.workspace.paths_table.ieda_config['optHold']
        
        self.read_def()
        
        self.ieda.run_to_hold(self.ieda_config)
        
        self.def_save()
        self.verilog_save(self.cell_names)
        
    def run_to_setup(self):
        self.ieda_config = self.workspace.paths_table.ieda_config['optSetup']
        
        self.read_def()
        
        self.ieda.run_to_setup(self.ieda_config)
        
        self.def_save()
        self.verilog_save(self.cell_names)