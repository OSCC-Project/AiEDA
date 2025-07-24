#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : floorplan.py
@Author : yell
@Desc : floorplan api
'''
from .io import IEDAIO
from ...workspace import Workspace
from ...flows import DbFlow

class IEDAFloorplan(IEDAIO):
    """floorplan api"""
    def __init__(self, workspace : Workspace, flow : DbFlow):
        super().__init__(workspace=workspace, flow=flow)
        
    def build_config(self):
        self.ieda_config = self.workspace.paths_table.ieda_config['floorplan']
    
    def __run_flow__(self):
        pass
    
    def auto_place_pins(self, 
                        layer : str, 
                        width : int, 
                        height : int,
                        sides : list[str]=[]):
        """
        layer : layer place io pins
        witdh : io pin width, in dbu
        height : io pin height, in dbu
        sides : "left", "rigth", "top", "bottom", if empty, place io pins around die.
        """
        self.ieda.auto_place_pins(layer=layer, 
                                  width = width, 
                                  height=height,
                                  sides=sides)
    
    def __generate_feature_summary__(self, json_path:str=None):
        if json_path is None:
            # use default feature path in workspace
            json_path = self.workspace.paths_table.ieda_feature_json['floorplan_summary']
            
        self.read_output_def()
        
        self.ieda.feature_summary(json_path)
                
        
        
        