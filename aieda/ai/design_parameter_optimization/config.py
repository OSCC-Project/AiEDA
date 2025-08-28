#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   config_management.py
@Time    :   2025-08-27 10:29:20
@Author  :   zhanghongda
@Version :   1.0
@Contact :   zhanghongda24@mails.ucas.ac.cn
@Desc    :   config management for iEDA
'''
import sys
import os
def setup_paths():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, '..', '..', '..')
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

setup_paths()
from aieda.flows.base import DbFlow
from aieda.workspace.workspace import Workspace
from aieda.ai.design_parameter_optimization.parameter import iEDAParameter
import logging

class ConfigManagement:
    def __init__(self, workspace, eda_tool, step=None):
        self.workspace = workspace     
        self.eda_tool = eda_tool      
        self.step = step              
        self.dir_workspace = workspace.directory 
        self.flow_list = list() 
        self.initFlowStep()
        self.initConfigPathList()
        self.loadParameters()
    
    def initFlowStep(self):

        if self.step is None:
            print(f"ERROR: step parameter cannot be None")
            raise ValueError("step parameter cannot be None")
        elif isinstance(self.step, str):
            try:
                self.step = getattr(DbFlow.FlowStep, self.step)
            except AttributeError:
                self.step = DbFlow.FlowStep.place
        self.initFlowList()

    def initFlowList(self):
        if self.step == DbFlow.FlowStep.place:
            place_flow = DbFlow(
                eda_tool=self.eda_tool,
                step=self.step
            )
            self.flow_list = [place_flow]
        else:
            pass
    
    def loadParameters(self):
        self.params = iEDAParameter(step=self.step)
        self.params.load_list(self.config_paths)

    def getFlowList(self):
        return self.flow_list

    def getConfigPath(self, step):
        print(f"DEBUG: self.eda_tool = {self.eda_tool}")
        print(f"DEBUG: self.eda_tool type = {type(self.eda_tool)}")
        print(f"DEBUG: self.eda_tool properties = {dir(self.eda_tool)}")
        config_path = self.workspace.get_config(self.eda_tool.value+"_config").get(step.value, None)
        return config_path
    
    def initConfigPathList(self):
        self.config_paths = {
            step: path 
            for step, path in self.workspace.paths_table.ieda_config.items()
            if path.endswith('.json') 
        }
        self.best_config_paths = {
            step: path.replace(".json", "_best.json") 
            for step, path in self.config_paths.items()
        }
        if not len(self.config_paths):
            logging.error("self.config_paths is empty, process exit")

    def getConfigPathList(self):
        return self.config_paths
    
    def getBestConfigPathList(self):
        return self.best_config_paths

    def getStep(self):
        return self.step

    def getWorkspacePath(self):
        return self.dir_workspace 
    def getParameters(self):
        return self.params