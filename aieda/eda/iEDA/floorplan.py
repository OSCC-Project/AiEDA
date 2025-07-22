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
    
    def run_floorplan(self):
        pass
    
    def auto_place_pins(self, 
                        layer : str, 
                        width : int, 
                        height : int):
        self.ieda.auto_place_pins(layer=layer, 
                                  width = width, 
                                  height=height)
    
    def run_eval(self):
        self.read_def()
        
        ieda_feature_json = self.workspace.paths_table.ieda_feature_json
        
        self.ieda.feature_summary(ieda_feature_json['floorplan_summary'])
                
        
        
        