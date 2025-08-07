#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : evaluation.py
@Author : yhqiu
@Desc : metric evaluation api
'''

from .io import IEDAIO
from ...workspace import Workspace
from ...flows import DbFlow

from ...data import (
    WirelengthType, 
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
    # cell density (macro and standard cell)
    def cell_density(self, 
                     bin_cnt_x : int = 256, 
                     bin_cnt_y : int = 256, 
                     save_path : str = ""):
        self.read_output_def()
        max_density, avg_density = self.ieda.cell_density(bin_cnt_x, bin_cnt_y, save_path)
        return max_density, avg_density
    
    # pin density (pin count)
    def pin_density(self, 
                     bin_cnt_x : int = 256, 
                     bin_cnt_y : int = 256, 
                     save_path : str = ""):
        self.read_output_def()
        max_density, avg_density = self.ieda.pin_density(bin_cnt_x, bin_cnt_y, save_path)
        return max_density, avg_density
    
    # net density (net count)
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
    # RUDY congestion
    def rudy_congestion(self,
                        bin_cnt_x : int = 256,
                        bin_cnt_y : int = 256,
                        save_path : str = ""):
        self.read_output_def()
        max_congestion, total_congestion = self.ieda.rudy_congestion(bin_cnt_x, bin_cnt_y, save_path)
        return max_congestion, total_congestion
    
    # LUT-RUDY congesiton
    def lut_rudy_congestion(self,
                            bin_cnt_x : int = 256,
                            bin_cnt_y : int = 256,
                            save_path : str = ""):
        self.read_output_def()
        max_congestion, total_congestion = self.ieda.lut_rudy_congestion(bin_cnt_x, bin_cnt_y, save_path)
        return max_congestion, total_congestion
    
    # EGR congestion, calling iRT
    def egr_congestion(self,
                       save_path : str = ""):
        self.read_output_def()
        max_congestion, total_congestion = self.ieda.egr_congestion(save_path)
        return max_congestion, total_congestion


#######################################################################################
#                         timing and power evaluation                                 # 
#######################################################################################   
    # timing and power evaluation using HPWL wirelength model 
    def timing_power_hpwl(self):
        self.read_output_def()
        result_dict = self.ieda.timing_power_hpwl()
        return result_dict
    
    # timing and power evaluation using FULTE wirelength model 
    def timing_power_stwl(self):
        self.read_output_def()
        result_dict = self.ieda.timing_power_stwl()
        return result_dict
    
    # timing and power evaluation using EGR wirelength model 
    def timing_power_egr(self):
        self.read_output_def()
        result_dict = self.ieda.timing_power_egr()
        return result_dict
    
    # get timing wire graph (vectorization)
    def get_timing_wire_graph(self, wire_graph_yaml_path: str):
        return self.ieda.get_timing_wire_graph(wire_graph_yaml_path)
    

#######################################################################################
#                       other evaluation (TO BE DONE)                                 # 
#######################################################################################   
    
    def eval_macro_margin(self):
        self.ieda.eval_macro_margin()
    
    def eval_continuous_white_space(self):
        self.ieda.eval_continuous_white_space()

    def eval_macro_channel(self, die_size_ratio : float = 0.5):
        self.ieda.eval_macro_channel(die_size_ratio)
        
        
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
