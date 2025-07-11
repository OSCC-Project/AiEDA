#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : json_flow.py
@Author : yell
@Desc : flow json parser 
'''
from ..utility.json_parser import JsonParser
from ...flows import DbFlow
   
class FlowParser(JsonParser):
    """flow json parser"""
    
    def get_db(self):
        """get data"""
        if self.read() is True:
            flow_db_list = []
            
            node_flow_dict = self.json_data['flow']
            for flow_dict in node_flow_dict:
                flow = DbFlow(eda_tool=flow_dict['eda_tool'], 
                              step=DbFlow.FlowStep(flow_dict['step']), 
                              state=DbFlow.FlowState(flow_dict['state']))

                flow_db_list.append(flow)
            
            return flow_db_list
        
        return None
    
    def set_flow_state(self, flow : DbFlow):
        """set flow state to json"""
        if self.read() is True:
            node_flow_dict = self.json_data['flow']
            for flow_dict in node_flow_dict:
                if( flow.eda_tool == flow_dict['eda_tool'] and flow.step.value == flow_dict['step'] ):
                    #set state
                    flow_dict['state'] = flow.state.value
                    #save file
                    return self.write()
            
        return False

    def reset_flow_state(self):
        """get data"""
        if self.read() is True:
            node_flow_dict = self.json_data['flow']

            for flow_dict in node_flow_dict:
                flow_dict['state'] = 'unstart'
                    
            return self.write()
            
        return False