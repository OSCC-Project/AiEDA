#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : path_parser.py
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
    verilog_input_path :str =""
    tech_lef_path: str = ""
    lef_paths : list = field(default_factory = list)
    lib_paths: list = field(default_factory = list)
    sdc_path: str = ""
    spef_path: str = ""

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
            self.json_data['sdc_path'] = paths.sdc_path
            self.json_data['spef_path'] = paths.spef_path
        
        return self.write()
    
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