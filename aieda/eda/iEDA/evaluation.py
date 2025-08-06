#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : ieda_engine.py
@Author : yell
@Desc : run iEDA
'''

from .io import IEDAIO
from ...workspace import Workspace
from ...flows import DbFlow

from ...data import (
    WirelengthType, 
    InstanceStatus, 
    CongestionType, 
    RudyType, 
    Direction
)

class IEDAEvaluation(IEDAIO): 
    def __init__(self, workspace : Workspace, flow : DbFlow):
        super().__init__(workspace=workspace, flow=flow)
        
        self.is_wirelength_eval = False
        self.wirelength_dict = {}
        

        
        
    def __configs__(self):
        super().__configs__()
#######################################################################################
#                      wirelength evaluation                                          # 
#######################################################################################
    # half-perimeter wirelength (HPWL)
    def total_wirelength_hpwl(self):
        if not self.is_wirelength_eval:
            self._total_wirelength()
            return self.wirelength_dict[str(WirelengthType.hpwl.value)]
        else:
            return self.wirelength_dict[str(WirelengthType.hpwl.value)]
        
    # Steiner tree wirelength (STWL)
    def total_wirelength_stwl(self):
        if not self.is_wirelength_eval:
            self._total_wirelength()
            return self.wirelength_dict[str(WirelengthType.flute.value)]
        else:
            return self.wirelength_dict[str(WirelengthType.flute.value)]
    
    # global routing wirelength (GRWL)
    def total_wirelength_grwl(self):
        if not self.is_wirelength_eval:
            self._total_wirelength()
            return self.wirelength_dict[str(WirelengthType.grwl.value)]
        else:
            return self.wirelength_dict[str(WirelengthType.grwl.value)]      
    
    # private function
    def _total_wirelength(self):
            self.read_output_def()
            self.wirelength_dict = self.ieda.total_wirelength_dict()
            self.is_wirelength_eval = True
#######################################################################################
#                         density evaluation                                          # 
#######################################################################################   
    def cell_density(self, 
                     bin_cnt_x : int = 256, 
                     bin_cnt_y : int = 256, 
                     save_path : str = ""):
        self.read_output_def()
        max_density, avg_density = self.ieda.cell_density(bin_cnt_x, bin_cnt_y, save_path)
        return max_density, avg_density
    
    def pin_density(self, 
                     bin_cnt_x : int = 256, 
                     bin_cnt_y : int = 256, 
                     save_path : str = ""):
        self.read_output_def()
        max_density, avg_density = self.ieda.pin_density(bin_cnt_x, bin_cnt_y, save_path)
        return max_density, avg_density
    
    def net_density(self, 
                     bin_cnt_x : int = 256, 
                     bin_cnt_y : int = 256, 
                     save_path : str = ""):
        self.read_output_def()
        max_density, avg_density = self.ieda.net_density(bin_cnt_x, bin_cnt_y, save_path)
        return max_density, avg_density
    
#######################################################################################
#                         congestion evaluation                                       # 
#######################################################################################   

    def eval_cell_hierarchy(self, 
                            plot_path : str, 
                            level : int = 1, 
                            forward : int = 1):
        self.ieda.eval_cell_hierarchy(plot_path, level, forward)

    def eval_macro_hierarchy(self, 
                             plot_path, 
                             level : int = 1, 
                             forward : int = 1):
        self.ieda.eval_macro_hierarchy(plot_path, level, forward)

    def eval_macro_connection(self, 
                              plot_path, 
                              level : int = 1, 
                              forward : int = 1):
        self.ieda.eval_macro_connection(plot_path, level, forward)
    
    def eval_macro_pin_connection(self, 
                                  plot_path, 
                                  level : int = 1, 
                                  forward : int = 1):
        self.ieda.eval_macro_pin_connection(plot_path, level, forward)

    def eval_macro_io_pin_connection(self, 
                                     plot_path, 
                                     level : int = 1, 
                                     forward : int = 1):
        self.ieda.eval_macro_io_pin_connection(plot_path, level, forward)


#######################################################################################
#                         timing evaluation                                           # 
#######################################################################################   

    def eval_inst_density(self, 
                          status : InstanceStatus, 
                          flip_flop : int):
        self.ieda.eval_inst_density(inst_status = status.value, eval_flip_flop = flip_flop)

    def eval_pin_density(self, 
                         status : InstanceStatus, 
                         eval_level : int):
        self.ieda.eval_pin_density(inst_status = status.value, level = eval_level)
    
    def eval_rudy_cong(self, 
                       type : RudyType, 
                       eval_direction : Direction ):
        self.ieda.eval_rudy_cong(rudy_type = type.value, direction = eval_direction.value)
    
    def eval_egr_cong(self):
        self.ieda.eval_egr_cong()


#######################################################################################
#                          power evaluation                                           # 
#######################################################################################   
    def plot_flow_value(self, 
                        plot_path : str, 
                        file_name : str, 
                        step : str, 
                        value : str):
        self.ieda.plot_flow_value(plot_path, file_name, step, value)
        
    def get_timing_wire_graph(self, wire_graph_yaml_path: str):
        return self.ieda.get_timing_wire_graph(wire_graph_yaml_path)
    
    def feature_eval_map(self, 
                         plot_dir : str, 
                         bin_cnt_x : int = 256, 
                         bin_cnt_y : int = 256):
        self.ieda.feature_summary_map(plot_dir, bin_cnt_x, bin_cnt_y)
        
    # density evaluation
    def eval_macro_density(self):
        self.ieda.eval_macro_density()

    def eval_macro_pin_density(self):
        self.ieda.eval_macro_pin_density()

    def eval_cell_pin_density(self):
        self.ieda.eval_cell_pin_density()

    def eval_macro_margin(self):
        self.ieda.eval_macro_margin()
    
    def eval_continuous_white_space(self):
        self.ieda.eval_continuous_white_space()

    def eval_macro_channel(self, die_size_ratio : float = 0.5):
        self.ieda.eval_macro_channel(die_size_ratio)