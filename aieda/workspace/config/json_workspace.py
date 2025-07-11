#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : json_workspace.py
@Author : yell
@Desc : workspace json parser 
'''
from dataclasses import dataclass
from dataclasses import field

from ..utility import JsonParser

@dataclass
class ConfigWorkspace(object):
    """data structure"""
    process_node : str = ""
    version : str = ""
    project : str = ""
    design : str = ""
    task : str = ""
    
class WorkspaceParser(JsonParser):
    """workspace parser"""
     
    def get_db(self):
        ''' get data '''
        db_workspcae = ConfigWorkspace()
        if((self.read() is True) and  ('workspace' in self.json_data)):
            node_workspace = self.json_data['workspace']
            
            db_workspcae.process_node = node_workspace['process_node']
            db_workspcae.version = node_workspace['version']
            db_workspcae.project = node_workspace['project']
            db_workspcae.design = node_workspace['design']
            db_workspcae.task = node_workspace['task']
            
        return db_workspcae
    
    def reset_value(self, reset_value : dict):
        """save data to json"""
        
        if self.read() is True:
            self.json_data['workspace']['project'] = reset_value['project']
            self.json_data['workspace']['design'] = reset_value['design']
            
            return self.write()
            
        return False

