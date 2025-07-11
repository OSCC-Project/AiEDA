#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : config_ieda.py
@Author : yell
@Desc : set iEDA config
'''

from ..utility.json_parser import JsonParser
    
class ConfigIEDA():
    def __init__(self):
        pass
    
    def reset_config(self, result_dir :str, flow_step):
        """reset iEDA json config"""      
        pass
        # if( flow_step.value == "route" ):
        #     if self.read() is True:
        #         old_dir = self.json_data['RT']['-temp_directory_path']
        #         if( result_dir in old_dir):
        #             print("no need to reset config path")   
        #         else:
        #             self.json_data['RT']['-temp_directory_path'] = result_dir + "iEDA/" + old_dir
        #             self.write()
    