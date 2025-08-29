#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : json_path.py
@Author : yell
@Desc : path json parser 
'''
from dataclasses import dataclass
from dataclasses import field

from ...utility import JsonParser

@dataclass
class ConfigPath(object):
    """data structure"""
    def_input_path : str = ""
    verilog_input_path :str = ""
    tech_lef_path: str = ""
    lef_paths : list = field(default_factory = list)
    lib_paths: list = field(default_factory = list)
    max_lib_paths: list = field(default_factory = list)
    min_lib_paths: list = field(default_factory = list)
    sdc_path: str = ""
    spef_path: str = ""
    rcworst_path : str = ""
    rcbest_path : str = ""

class PathParser(JsonParser):
    """path parser"""
    def create_json(self, paths:ConfigPath=None):
        # create json
        if self.read_create():
            if paths is None:
                # create default flow of iEDA
                paths = ConfigPath()
                     
            self.json_data['def_input_path'] = paths.def_input_path
            self.json_data['verilog_input_path'] = paths.verilog_input_path
            self.json_data['tech_lef_path'] = paths.tech_lef_path
            self.json_data['lef_paths'] = paths.lef_paths
            self.json_data['lib_paths'] = paths.lib_paths
            self.json_data['max_lib_paths'] = paths.max_lib_paths
            self.json_data['min_lib_paths'] = paths.min_lib_paths
            self.json_data['sdc_path'] = paths.sdc_path
            self.json_data['spef_path'] = paths.spef_path
            self.json_data['rcworst_path'] = paths.rcworst_path
            self.json_data['rcbest_path'] = paths.rcbest_path
        
        return self.write()
    
    def get_db(self):
        ''' get data '''
        db_path = ConfigPath()
        if self.read() is True:
            db_path.def_input_path = self.json_data.get('def_input_path', "")              
            db_path.verilog_input_path = self.json_data.get('verilog_input_path', "")         
            db_path.tech_lef_path = self.json_data.get('tech_lef_path', "")
            db_path.lef_paths = self.json_data.get('lef_paths', [])
            db_path.lib_paths = self.json_data.get('lib_paths', [])
            db_path.max_lib_paths = self.json_data.get('max_lib_paths', [])
            db_path.min_lib_paths = self.json_data.get('min_lib_paths', [])
            db_path.sdc_path = self.json_data.get('sdc_path', "")
            db_path.spef_path = self.json_data.get('spef_path', "")
            db_path.rcworst_path = self.json_data.get('rcworst_path', "")
            db_path.rcbest_path = self.json_data.get('rcbest_path', "")
            
        return db_path
    
    def set_tech_lef(self, tech_lef : str):
        if self.read():
            self.json_data['tech_lef_path'] = tech_lef

            #save file
            return self.write()
            
        return False
    
    def set_lefs(self, lefs : list[str]):
        if self.read():
            self.json_data['lef_paths'] = lefs

            #save file
            return self.write()
            
        return False
    
    def set_def_input(self, def_input : str):
        if self.read():
            self.json_data['def_input_path'] = def_input

            #save file
            return self.write()
            
        return False
    
    def set_verilog_input(self, verilog_input : str):
        if self.read():
            self.json_data['verilog_input_path'] = verilog_input

            #save file
            return self.write()
            
        return False
    
    def set_libs(self, libs : list[str]):
        if self.read():
            self.json_data['lib_paths'] = libs

            #save file
            return self.write()
            
        return False
    
    def set_max_libs(self, libs : list[str]):
        if self.read():
            self.json_data['max_lib_paths'] = libs

            #save file
            return self.write()
            
        return False
    
    def set_min_libs(self, libs : list[str]):
        if self.read():
            self.json_data['min_lib_paths'] = libs

            #save file
            return self.write()
            
        return False
    
    def set_sdc(self, sdc_path : str):
        if self.read():
            self.json_data['sdc_path'] = sdc_path

            #save file
            return self.write()
            
        return False
    
    def set_spef(self, spef_path : str):
        if self.read():
            self.json_data['spef_path'] = spef_path

            #save file
            return self.write()
            
        return False
    
    def set_rcworst(self, rcworst_path : str):
        if self.read():
            self.json_data['rcworst_path'] = rcworst_path

            #save file
            return self.write()
            
        return False
    
    def set_rcbest(self, rcbest_path : str):
        if self.read():
            self.json_data['rcbest_path'] = rcbest_path

            #save file
            return self.write()
            
        return False