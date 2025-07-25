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
    InstanceStatus, 
    CongestionType, 
    WirelengthType, 
    RudyType, 
    Direction
)

class IEDAEvaluation(IEDAIO): 
    def __init__(self, workspace : Workspace, flow : DbFlow):
        super().__init__(workspace=workspace, flow=flow)
    
    def feature_eval_map(self, 
                         plot_dir : str, 
                         bin_cnt_x : int = 256, 
                         bin_cnt_y : int = 256):
        self.ieda.feature_summary_map(plot_dir, bin_cnt_x, bin_cnt_y)
        
    def init_wirelength_eval(self):
        self.ieda.init_wirelength_eval()
    
    def eval_total_wirelength(self, type : EvalWirelengthType):
        return self.ieda.eval_total_wirelength(wirelength_type = type.value)

    def init_cong_eval(self, 
                       bin_cnt_x : int = 256, 
                       bin_cnt_y : int = 256):
        self.ieda.init_cong_eval(bin_cnt_x, bin_cnt_y)

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

    def eval_inst_density(self, 
                          status : EvalInstanceStatus, 
                          flip_flop : int):
        self.ieda.eval_inst_density(inst_status = status.value, eval_flip_flop = flip_flop)

    def eval_pin_density(self, 
                         status : EvalInstanceStatus, 
                         eval_level : int):
        self.ieda.eval_pin_density(inst_status = status.value, level = eval_level)
    
    def eval_rudy_cong(self, 
                       type : EvalRudyType, 
                       eval_direction : EvalDirection ):
        self.ieda.eval_rudy_cong(rudy_type = type.value, direction = eval_direction.value)
    
    def eval_egr_cong(self):
        self.ieda.eval_egr_cong()
    
    def plot_bin_value(self, 
                       plot_path : str, 
                       file_name : str, 
                       value_type : CongestionType):
        self.ieda.plot_bin_value(plot_path, file_name, value_type.value)

    def plot_tile_value(self, 
                        plot_path : str, 
                        file_name : str):
        self.ieda.plot_tile_value(plot_path, file_name)
    
    def plot_flow_value(self, 
                        plot_path : str, 
                        file_name : str, 
                        step : str, 
                        value : str):
        self.ieda.plot_flow_value(plot_path, file_name, step, value)
        
    def get_timing_wire_graph(self, wire_graph_yaml_path: str):
        return self.ieda.get_timing_wire_graph(wire_graph_yaml_path)