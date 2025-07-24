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
    
    def __run_flow__(self): 
        match self.flow.step:
            case DbFlow.FlowStep.optDrv:
                self.__run_to_drv__()  
            case DbFlow.FlowStep.optHold:
                self.__run_to_hold__()   
            case DbFlow.FlowStep.optSetup:
                self.__run_to_setup__()
                    
    def __run_to_drv__(self):
        self.ieda_config = self.workspace.paths_table.ieda_config['optDrv']
        
        self.read_def()
        
        self.ieda.run_to_drv(self.ieda_config)
        
        self.def_save()
        self.verilog_save(self.cell_names)
        
        self.__generate_optdrv_feature_summary__()
        self.__generate_optdrv_feature_tool__()

    def __run_to_hold__(self):
        self.ieda_config = self.workspace.paths_table.ieda_config['optHold']
        
        self.read_def()
        
        self.ieda.run_to_hold(self.ieda_config)
        
        self.def_save()
        self.verilog_save(self.cell_names)
        
        self.__generate_opthold_feature_summary__()
        self.__generate_opthold_feature_tool__()
        
    def __run_to_setup__(self):
        self.ieda_config = self.workspace.paths_table.ieda_config['optSetup']
        
        self.read_def()
        
        self.ieda.run_to_setup(self.ieda_config)
        
        self.def_save()
        self.verilog_save(self.cell_names)
        
        self.__generate_optsetup_feature_summary__()
        self.__generate_optsetup_feature_tool__()
        
    def __generate_feature_summary__(self, json_path:str=None):
        match self.flow.step:
            case DbFlow.FlowStep.optDrv:
                self.__generate_optdrv_feature_summary__(json_path)  
            case DbFlow.FlowStep.optHold:
                self.__generate_opthold_feature_summary__(json_path)   
            case DbFlow.FlowStep.optSetup:
                self.__generate_optsetup_feature_summary__(json_path)
                
    def __generate_opthold_feature_summary__(self, json_path:str=None):
        if json_path is None:
            json_path = self.workspace.paths_table.ieda_feature_json['optHold_summary']
            
        self.read_output_def()    

        ieda_feature_json = self.workspace.paths_table.ieda_feature_json
        
        # generate feature summary data
        self.ieda.feature_summary(json_path)
    
    def __generate_optdrv_feature_summary__(self, json_path:str=None):
        if json_path is None:
            json_path = self.workspace.paths_table.ieda_feature_json['optDrv_summary']
            
        self.read_output_def()
        
        # generate feature summary data
        self.ieda.feature_summary(json_path)

    def __generate_optsetup_feature_summary__(self, json_path:str=None):
        if json_path is None:
            json_path = self.workspace.paths_table.ieda_feature_json['optSetup_summary']
            
        self.read_output_def()    
        
        # generate feature summary data
        self.ieda.feature_summary(json_path)
        
    def __generate_feature_tool__(self):
        match self.flow.step:
            case DbFlow.FlowStep.optDrv:
                self.__generate_optdrv_feature_tool__()  
            case DbFlow.FlowStep.optHold:
                self.__generate_opthold_feature_tool__()   
            case DbFlow.FlowStep.optSetup:
                self.__generate_optsetup_feature_tool__()
                
    def __generate_optdrv_feature_tool__(self):
        self.read_output_def()

        ieda_feature_json = self.workspace.paths_table.ieda_feature_json
        
        # generate feature tool data
        self.ieda.feature_tool(ieda_feature_json['optDrv_tool'], DbFlow.FlowStep.optDrv.value)
    
    def __generate_opthold_feature_tool__(self):
        self.read_output_def()    

        ieda_feature_json = self.workspace.paths_table.ieda_feature_json
        
        # generate feature tool data
        self.ieda.feature_tool(ieda_feature_json['optHold_tool'], DbFlow.FlowStep.optHold.value)

    def __generate_optsetup_feature_tool__(self):
        self.read_output_def()    

        ieda_feature_json = self.workspace.paths_table.ieda_feature_json

        # generate feature tool data
        self.ieda.feature_tool(ieda_feature_json['optSetup_tool'], DbFlow.FlowStep.optSetup.value)