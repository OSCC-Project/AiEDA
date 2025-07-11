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