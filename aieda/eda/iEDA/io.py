#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : io.py
@Author : yell
@Desc : iEDA data io, including read/write config/lef/def/verilog/gds ext.
'''
from multiprocessing import Process
from .base import IEDABase
from ...workspace import Workspace
from ...flows import DbFlow

class IEDAIO(IEDABase):
    """iEDA data io, including read/write config/lef/def/verilog/gds ext."""
    def __init__(self, workspace : Workspace, flow : DbFlow):
        self.cell_names : set = set()
        
        super().__init__(workspace=workspace, flow=flow)
        self.inited_flag = False
        
    def set_exclude_cell_names(self, cell_names : set):
        self.cell_names = cell_names
        
    def run_flow(self):
        p = Process(target=self._run_flow, args=())
        p.start()
        p.join()
       
    def _run_flow(self):
        pass
        
    def generate_feature_summary(self, json_path:str=None):    
        if self.inited_flag:
            self._generate_feature_summary(json_path=json_path)
        else:
            p = Process(target=self._generate_feature_summary, args=(json_path,))
            p.start()
            p.join()
    
    def _generate_feature_summary(self, json_path:str=None):
        pass
    
    def generate_feature_tool(self):
        if self.inited_flag:
            self._generate_feature_tool()
        else:
            p = Process(target=self._generate_feature_tool, args=())
            p.start()
            p.join()
    
    def _generate_feature_tool(self):
        pass
    
    def generate_feature_map(self,map_grid_size=1):
        if self.inited_flag:
            self._generate_feature_map()
        else:
            p = Process(target=self._generate_feature_map, args=(map_grid_size,))
            p.start()
            p.join()
    
    def _generate_feature_map(self):
        pass
        
    def init_config(self):
        """init_config"""
        self.ieda.flow_init(flow_config=self.workspace.paths_table.ieda_config['initFlow'])
        
        self.ieda.db_init(config_path = self.workspace.paths_table.ieda_config['initDB'],
                          output_path=self.workspace.paths_table.ieda_output['data'],
                          feature_path=self.workspace.paths_table.ieda_output['feature']
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
        if self.inited_flag:
            self.workspace.logger.info("design has been init.")
        else:
            self.init_config()
            self.init_techlef()
            self.init_lef()
            
            if read_verilog:
                self.init_verilog()
            else:
                self.init_def(self.flow.input_def)
                
            self.inited_flag = True
    
    def read_output_def(self):
        if self.inited_flag:
            self.workspace.logger.info("design has been init.")
        else:
            self.init_config()
            self.init_techlef()
            self.init_lef()
            
            self.init_def(self.flow.output_def)
                
            self.inited_flag = True
        
    def read_verilog(self, top_module=""):
        if self.inited_flag:
            self.workspace.logger.info("design has been init.")
        else:
            self.init_config()
            self.init_techlef()
            self.init_lef()
            self.init_verilog(top_module)
            
            self.inited_flag = True
        
    def run_def_to_gds(self, gds_path : str):
        self.ieda.gds_save(gds_path)
        
    def read_liberty(self):
        lib_paths = self.workspace.configs.paths.lib_paths
        self.ieda.read_liberty(lib_paths)
        
    def read_sdc(self):
        sdc_path= self.workspace.configs.paths.sdc_path
        self.ieda.read_sdc(sdc_path)