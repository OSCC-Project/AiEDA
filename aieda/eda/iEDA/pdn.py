#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : pdn.py
@Author : yell
@Desc : pdn api
'''
from .io import IEDAIO
from ...workspace import Workspace
from ...flows import DbFlow

class IEDAPdn(IEDAIO):
    """pdn api"""
    def __init__(self, workspace : Workspace, flow : DbFlow):
        super().__init__(workspace=workspace, flow=flow)
        
    def _configs(self):
        super()._configs()
        
        self.ieda_config = self.workspace.paths_table.ieda_config['pnp']
    
    def _run_flow(self):     
        self.read_def()
        
        self.ieda.run_pnp(self.ieda_config)
        
        self.def_save()
        self.verilog_save(self.cell_names)
    
    def run_pnp(self):       
        self.ieda.run_pnp(self.ieda_config)    