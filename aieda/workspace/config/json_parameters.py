#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : json_parameters.py
@Author : yell
@Desc : parameters json parser 
'''
from dataclasses import dataclass

from ...utility.json_parser import JsonParser

@dataclass
class ConfigParameters(object):
    """data structure"""
    p1 = None
       
class ParametersParser(JsonParser):
    """flow json parser"""
    def create_json(self, parameters:ConfigParameters=None):
        # create json
        if self.read_create():
            if parameters is None:
                # default paramters
                parameters = ConfigParameters()
        
        return self.write()
        
    def get_db(self):
        """get data"""
        if self.read() is True:
            parameters = None
            
            return parameters
        
        return None