#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : json_workspace.py
@Author : yell
@Desc : workspace json parser 
'''
from dataclasses import dataclass
from dataclasses import field

from ...utility import JsonParser

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
    def create_json(self, workspace_config:ConfigWorkspace=None):
        # create json
        if self.read_create():
            if workspace_config is None:
                # create default flow of iEDA
                workspace_config = ConfigWorkspace()
            workspace_json = {}      
            workspace_json['process_node'] = workspace_config.process_node
            workspace_json['version'] = workspace_config.version
            workspace_json['project'] = workspace_config.project
            workspace_json['design'] = workspace_config.design
            workspace_json['task'] = workspace_config.task
            
            self.json_data['workspace'] = workspace_json
        return self.write()
     
    def get_db(self):
        ''' get data '''
        db_workspcae = ConfigWorkspace()
        if((self.read() is True) and  ('workspace' in self.json_data)):
            node_workspace = self.json_data['workspace']
            
            db_workspcae.process_node = node_workspace['process_node']
            db_workspcae.version = node_workspace['version']
            db_workspcae.project = node_workspace['project']
            db_workspcae.design = node_workspace['design']
            
        return db_workspcae
    
    def set_process_node(self, process_node : str):
        if self.read():
            self.json_data['workspace']['process_node'] = process_node

            #save file
            return self.write()
            
        return False
    
    def set_version(self, version : str):
        if self.read():
            self.json_data['workspace']['version'] = version

            #save file
            return self.write()
            
        return False
    
    def set_project(self, project : str):
        if self.read():
            self.json_data['workspace']['project'] = project

            #save file
            return self.write()
            
        return False
    
    def set_design(self, design : str):
        if self.read():
            self.json_data['workspace']['design'] = design

            #save file
            return self.write()
            
        return False
    
    def set_task(self, task : str):
        if self.read():
            self.json_data['workspace']['task'] = task

            #save file
            return self.write()
            
        return False

