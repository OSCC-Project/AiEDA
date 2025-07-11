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
        
    def run_legalization(self):
        self.read_def()
        
        self.ieda.run_incremental_flow(self.ieda_config)
        
        self.def_save()
        self.verilog_save(self.cell_names)
        
    def run_filler(self):
        self.read_def()
        
        self.ieda.run_filler(self.ieda_config)
        
        self.def_save()
        self.verilog_save(self.cell_names)
        
    def run_mp(self, config : str, tcl_path=""):
        self.ieda.runMP(config, tcl_path)
    
    def run_refinement(self, tcl_path=""):
        self.ieda.runRef(tcl_path)