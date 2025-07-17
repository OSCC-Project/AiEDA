#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : io.py
@Author : yell
@Desc : iEDA data io, including read/write config/lef/def/verilog/gds ext.
'''

from .base import IEDABase
from ...workspace import Workspace
from ...flows import DbFlow

class IEDAIO(IEDABase):
    """iEDA data io, including read/write config/lef/def/verilog/gds ext."""
    def __init__(self, workspace : Workspace, flow : DbFlow):
        self.cell_names : set = set()
        
        super().__init__(workspace=workspace, flow=flow)
            
    def init_config(self):
        """init_config"""
        self.ieda.flow_init(flow_config=self.workspace.paths_table.ieda_config['initFlow'])
        
        self.ieda.db_init(config_path = self.workspace.paths_table.ieda_config['initDB'],
                          output_path=self.workspace.paths_table.ieda_output['data']
                          )
                        #   lib_paths = self.workspace.json_path.lib_paths, 
                        #   sdc_path = self.workspace.json_path.sdc_path)

    def init_techlef(self):
        """init_techlef"""
        path = self.workspace.configs.paths.tech_lef_path
        self.ieda.tech_lef_init(path)
    
    def init_lef(self):
        """init_lef"""
        paths = self.workspace.configs.paths.lef_paths
        self.ieda.lef_init(lef_paths=paths)
    
    def init_def(self, path : str = ""):
        """init_def"""
        self.ieda.def_init(def_path=path)
        
    def init_verilog(self, top_module : str = ""):
        """init_verilog"""
        if top_module == "":
            top_module = self.workspace.configs.workspace.design

        self.ieda.verilog_init(self.flow.input_verilog, top_module)
        
    def def_save(self):
        """def_save"""
        self.ieda.def_save(def_name=self.flow.output_def)
    
    def gds_save(self, output_path : str):
        """def_save"""
        self.ieda.gds_save(output_path)
        
    def tcl_save(self, output_path : str):
        """def_save"""
        self.ieda.tcl_save(output_path)
        
    def verilog_save(self, cell_names : set = set()):
        """verilog_save"""
        self.ieda.netlist_save(netlist_path=self.flow.output_verilog, exclude_cell_names=cell_names)

    def write_placement_back(self, dm_inst_ptr, node_x, node_y):
        self.ieda.write_placement_back(dm_inst_ptr, node_x, node_y)

    def exit(self):
        """exit"""
        self.ieda.flow_exit()
        
    def read_def(self, read_verilog=False):
        self.init_config()
        self.init_techlef()
        self.init_lef()
        
        if read_verilog:
            self.init_verilog()
        else:
            self.init_def(self.flow.input_def)
        
    def read_verilog(self, top_module=""):
        self.init_config()
        self.init_techlef()
        self.init_lef()
        self.init_verilog(top_module)
        
    def run_def_to_gds(self, gds_path : str):
        self.ieda.gds_save(gds_path)
        
    def read_liberty(self):
        lib_paths = self.workspace.configs.paths.lib_paths
        self.ieda.read_liberty(lib_paths)
        
    def read_sdc(self):
        sdc_path= self.workspace.configs.paths.sdc_path
        self.ieda.read_sdc(sdc_path)