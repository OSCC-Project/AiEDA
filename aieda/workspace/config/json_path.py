#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : path_parser.py
@Author : yell
@Desc : path json parser 
'''
from dataclasses import dataclass
from dataclasses import field

from ..utility import JsonParser

@dataclass
class ConfigPath(object):
    """data structure"""
    def_input_path : str = ""
    verilog_input_path :str =""
    tech_lef_path: str = ""
    lef_paths : list = field(default_factory = list)
    lib_paths: list = field(default_factory = list)
    sdc_path: str = ""
    spef_path: str = ""
    mp_tcl:str = ""

class PathParser(JsonParser):
    """path parser"""
    def get_db(self):
        ''' get data '''
        db_path = ConfigPath()
        if self.read() is True:
            if( 'def_input_path' in self.json_data):      
                db_path.def_input_path = self.json_data['def_input_path']
                
            if( 'verilog_input_path' in self.json_data):      
                db_path.verilog_input_path = self.json_data['verilog_input_path']
                
            if( 'tech_lef_path' in self.json_data):      
                db_path.tech_lef_path = self.json_data['tech_lef_path']
     
            if( 'lef_paths' in self.json_data):    
                node_lef_dict = self.json_data['lef_paths']
                for lef in node_lef_dict:
                    db_path.lef_paths.append(lef)
                
            node_lib_dict = self.json_data['lib_paths']
            for lib in node_lib_dict:
                db_path.lib_paths.append(lib)
                
            db_path.sdc_path = self.json_data['sdc_path']
            db_path.spef_path = self.json_data['spef_path']
            db_path.mp_tcl = self.json_data['mp_tcl']
            
        return db_path
    
    def set_mp_tcl_path(self, mp_tcl_path :str):
        """save mp tcl path to json"""
        
        if self.read() is True:
            self.json_data['mp_tcl'] = mp_tcl_path
            
            return self.write()
            
        return False
    
    def reset_value(self, reset_value : dict):
        """save data to json"""
        
        if self.read() is True:
            self.json_data['def_input_path'] = reset_value['def_input_path']
            self.json_data['verilog_input_path'] = reset_value['verilog_input_path']
            self.json_data['sdc_path'] = reset_value['sdc_path']
            
            return self.write()
            
        return False
    
    def reset_libs(self, libs : list):
        """save data to json"""
        
        if self.read() is True:
            self.json_data['lib_paths'] = libs
            return self.write()
            
        return False

