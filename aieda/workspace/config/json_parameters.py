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
            self.json_data['placement_max_phi_coef'] = parameters.placement_max_phi_coef
            self.json_data['placement_init_wirelength_coef'] = parameters.placement_init_wirelength_coef
            self.json_data['placement_min_wirelength_force_bar'] = parameters.placement_min_wirelength_force_bar
            self.json_data['cts_skew_bound'] = parameters.cts_skew_bound
            self.json_data['cts_max_buf_tran'] = parameters.cts_max_buf_tran
            self.json_data['cts_max_sink_tran'] = parameters.cts_max_sink_tran
            self.json_data['cts_max_cap'] = parameters.cts_max_cap
            self.json_data['cts_max_fanout'] = parameters.cts_max_fanout
            self.json_data['cts_cluster_size'] = parameters.cts_cluster_size            
        
        return self.write()
        
    def get_db(self):
        """get data"""
        if self.read() is True:
            parameters = EDAParameters()
            
            return parameters
        
        return None