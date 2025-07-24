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
    
    def __run_flow__(self): 
        match self.flow.step:
            case DbFlow.FlowStep.place:
                self.__run_placement__()  
            case DbFlow.FlowStep.legalization:
                self.__run_legalization__()   
            case DbFlow.FlowStep.filler:
                self.__run_filler__()      
        
    def __run_placement__(self):
        self.read_def()
        
        self.ieda.run_placer(self.ieda_config)
        
        self.def_save()
        self.verilog_save(self.cell_names)
        
        self.__generate_placement_feature_summary__()
        self.__generate_placement_feature_tool__()
        self.__generate_feature_map__()
        
    def __run_legalization__(self):
        self.read_def()
        
        self.ieda.run_incremental_flow(self.ieda_config)
        
        self.def_save()
        self.verilog_save(self.cell_names)
        
        self.__generate_legalization_feature_summary__()
        self.__generate_legalization_feature_tool__()
        
    def __run_filler__(self):
        self.read_def()
        
        self.ieda.run_filler(self.ieda_config)
        
        self.def_save()
        self.verilog_save(self.cell_names)
        
        self.__generate_filler_feature_summary__()
        self.__generate_filler_feature_tool__()
    
    def __generate_feature_summary__(self, json_path:str=None):
        match self.flow.step:
            case DbFlow.FlowStep.place:
                self.__generate_placement_feature_summary__(json_path)  
            case DbFlow.FlowStep.legalization:
                self.__generate_legalization_feature_summary__(json_path)   
            case DbFlow.FlowStep.filler:
                self.__generate_filler_feature_summary__(json_path)
                
    def __generate_placement_feature_summary__(self, json_path:str=None):
        if json_path is None:
            # use default feature path in workspace
            json_path = self.workspace.paths_table.ieda_feature_json['place_summary']
            
        self.read_output_def()
        
        # generate feature summary data
        self.ieda.feature_summary(json_path)
        
    def __generate_legalization_feature_summary__(self, json_path:str=None):
        if json_path is None:
            # use default feature path in workspace
            json_path = self.workspace.paths_table.ieda_feature_json['legalization_summary']
            
        self.read_output_def()
        
        # generate feature summary data
        self.ieda.feature_summary(json_path)
        
    def __generate_filler_feature_summary__(self, json_path:str=None):
        if json_path is None:
            # use default feature path in workspace
            json_path = self.workspace.paths_table.ieda_feature_json['filler_summary']
            
        self.read_output_def()
        
        # generate feature summary data
        self.ieda.feature_summary(json_path)
        
    def __generate_feature_tool__(self):
        match self.flow.step:
            case DbFlow.FlowStep.place:
                self.__generate_placement_feature_tool__()  
            case DbFlow.FlowStep.legalization:
                self.__generate_legalization_feature_tool__()   
            case DbFlow.FlowStep.filler:
                self.__generate_filler_feature_tool__()
        
    def __generate_placement_feature_tool__(self):
        self.read_output_def()
            
        ieda_feature_json = self.workspace.paths_table.ieda_feature_json
        
        # generate feature tool data
        self.ieda.feature_tool(ieda_feature_json['place_tool'], DbFlow.FlowStep.place.value)
    
    def __generate_feature_map__(self, map_grid_size = 1):
        self.read_output_def()
            
        ieda_feature_json = self.workspace.paths_table.ieda_feature_json
        
        # generate eval metrics. The default map_grid_size is 1X row_height.
        self.ieda.feature_pl_eval(ieda_feature_json['place_map'], map_grid_size)
        
    def __generate_legalization_feature_tool__(self):
        self.read_output_def()
            
        ieda_feature_json = self.workspace.paths_table.ieda_feature_json
        
        # generate feature tool data
        self.ieda.feature_tool(ieda_feature_json['legalization_tool'], DbFlow.FlowStep.legalization.value)
        
    def __generate_filler_feature_tool__(self):
        self.read_output_def()
            
        ieda_feature_json = self.workspace.paths_table.ieda_feature_json
        
        # generate feature tool data
        self.ieda.feature_tool(ieda_feature_json['filler_tool'], DbFlow.FlowStep.filler.value)
        
    def run_mp(self, config : str, tcl_path=""):
        self.ieda.runMP(config, tcl_path)
    
    def run_refinement(self, tcl_path=""):
        self.ieda.runRef(tcl_path)
        
    # build macro drc distribution
    def feature_macro_drc_distribution(self, path: str, drc_path: str):
        self.ieda.feature_macro_drc(path=path, drc_path=drc_path)