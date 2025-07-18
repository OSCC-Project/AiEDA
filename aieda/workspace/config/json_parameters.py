#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : json_parameters.py
@Author : yell
@Desc : parameters json parser 
'''
from ...utility.json_parser import JsonParser
from ...data.database.parameters import EDAParameters
       
class ParametersParser(JsonParser):
    """flow json parser"""
    def create_json(self, parameters:EDAParameters=None):
        # create json
        if self.read_create():
            if parameters is None:
                # default paramters
                parameters = EDAParameters()
                
            self.json_data['placement_target_density'] = parameters.placement_target_density
        
        return self.write()
        
    def get_db(self):
        """get data"""
        if self.read() is True:
            parameters = EDAParameters()
            
            return parameters
        
        return None