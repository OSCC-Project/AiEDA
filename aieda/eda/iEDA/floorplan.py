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
from numpy import double

class IEDAFloorplan(IEDAIO):
    """floorplan api"""
    def __init__(self, workspace : Workspace, flow : DbFlow):
        super().__init__(workspace=workspace, flow=flow)
        
    def __configs__(self):
        super().__configs__()
        
        self.ieda_config_floorplan = self.workspace.paths_table.ieda_config['floorplan']
        self.ieda_config_pnp = self.workspace.paths_table.ieda_config['pnp']
    
    def __run_flow__(self):
        pass
    
    def __generate_feature_summary__(self, json_path:str=None):
        if json_path is None:
            # use default feature path in workspace
            json_path = self.workspace.paths_table.ieda_feature_json['floorplan_summary']
            
        self.read_output_def()
        
        self.ieda.feature_summary(json_path)
    
     
    def init_floorplan(self, 
                       die_area : str, 
                       core_area : str,
                       core_site : str,
                       io_site : str,
                       corner_site : str,
                       core_util : double,
                       x_margin : double,
                       y_margin : double,
                       xy_ratio : double,
                       cell_area : double):
        """
        die_area :  "0.0    0.0   1100    1100"   
        core_area : "10.0   10.0  1090.0  1090.0"
        """
        return self.ieda.init_floorplan(die_area=die_area, 
                                        core_area=core_area,
                                        core_site=core_site,
                                        io_site=io_site,
                                        corner_site=corner_site,
                                        core_util=core_util,
                                        x_margin=x_margin,
                                        y_margin=y_margin,
                                        xy_ratio=xy_ratio,
                                        cell_area=cell_area)
    
    def init_floorplan_by_area(self, 
                       die_area : str, 
                       core_area : str,
                       core_site : str,
                       io_site : str,
                       corner_site : str):
        return self.init_floorplan(die_area=die_area, 
                                   core_area=core_area,
                                   core_site=core_site,
                                   io_site=io_site,
                                   corner_site=corner_site,
                                   core_util=0,
                                   x_margin=0,
                                   y_margin=0,
                                   xy_ratio=0,
                                   cell_area=0)
    
    def init_floorplan_by_core_utilization(self, 
                       core_site : str,
                       io_site : str,
                       corner_site : str,
                       core_util : double,
                       x_margin : double,
                       y_margin : double,
                       xy_ratio : double,
                       cell_area : double=0):
        return self.init_floorplan(die_area="", 
                                   core_area="",
                                   core_site=core_site,
                                   io_site=io_site,
                                   corner_site=corner_site,
                                   core_util=core_util,
                                   x_margin=x_margin,
                                   y_margin=y_margin,
                                   xy_ratio=xy_ratio,
                                   cell_area=cell_area)     
        
    def gern_track(self, 
                   layer : str,  
                   x_start : int, 
                   x_step : int, 
                   y_start : int,  
                   y_step : int):   
        return self.ieda.gern_track(layer=layer,
                            x_start=x_start,
                            x_step=x_step,
                            y_start=y_start,
                            y_step=y_step)
        
    def add_pdn_io(self, 
                   net_name : str, 
                   direction : str,
                   is_power : bool,
                   pin_name : str=None):
        if pin_name is None:
            pin_name = net_name
        return self.ieda.add_pdn_io(pin_name=pin_name,
                                    net_name=net_name,
                                    direction=direction,
                                    is_power=is_power)
        
    def global_net_connect(self,
                           net_name : str,
                           instance_pin_name : str,
                           is_power : bool):
        return self.ieda.global_net_connect(net_name=net_name,
                                    instance_pin_name=instance_pin_name,
                                    is_power=is_power)
        
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
        return self.ieda.auto_place_pins(layer=layer, 
                                  width = width, 
                                  height=height,
                                  sides=sides)
    
    def tapcell(self, tapcell : str, distance : double, endcap : str):
        return self.ieda.tapcell(tapcell=tapcell,
                                 distance=distance,
                                 endcap=endcap)   
        
    def pnp(self):
        self.ieda.run_pnp(self.ieda_config_pnp) 