#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   config_management.py
@Time    :   2024-10-22 20:29:20
@Author  :   SivanLaai
@Version :   1.0
@Contact :   lyhhap@163.com
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
from aieda.ai.DSE.parameter import iEDAParameter
import logging

class ConfigManagement:
    def __init__(self, args, eda_tool):
        self.args = args
        self.step = None
        root = self.args.root
        tech = self.args.tech
        design = self.args.project_name
        self.dir_workspace = f"{root}"
        self.workspace = Workspace(self.dir_workspace, design) 

        self.flow_list = list() 
        self.eda_tool = "iEDA" 
        self.initFlowStep()
        self.initConfigPathList()
        self.loadParameters()

    def initFlowList(self):
        if self.step == DbFlow.FlowStep.place:
            place_flow = DbFlow(
                eda_tool="iEDA", 
                step=DbFlow.FlowStep.place
            )
            self.flow_list = [place_flow]
            print(f"DEBUG: 创建了place_flow: {place_flow}")
        else:
            print(f"DEBUG: step不是place，是 {self.step}")

    def getFlowList(self):
        return self.flow_list
        
    def getFlowStepsByStepArg(self, step_list):
        flow_steps = list()
        for step in step_list:
            flow_steps.append(self.checkFlowStep(step))
        return flow_steps
    
    def checkFlowStep(self, step):
        if step == DbFlow.FlowStep.floorplan.value.lower():
            return DbFlow.FlowStep.floorplan
        
        if step == DbFlow.FlowStep.fixFanout.value.lower():
            return DbFlow.FlowStep.fixFanout
            
        if step == DbFlow.FlowStep.place.value.lower():
            return DbFlow.FlowStep.place
        
        if(step == DbFlow.FlowStep.cts.value.lower()):
            return DbFlow.FlowStep.cts
            
        if step == DbFlow.FlowStep.optDrv.value.lower():
            return DbFlow.FlowStep.optDrv
            
        if step == DbFlow.FlowStep.optHold.value.lower():
            return DbFlow.FlowStep.optHold
            
        if step == DbFlow.FlowStep.optSetup.value.lower():
            return DbFlow.FlowStep.optSetup
            
        if step == DbFlow.FlowStep.legalization.value.lower():
            return DbFlow.FlowStep.legalization
            
        if (step == DbFlow.FlowStep.route.value.lower()):
            return DbFlow.FlowStep.route
            
        if step == DbFlow.FlowStep.filler.value.lower():
            return DbFlow.FlowStep.filler
            
        if step == DbFlow.FlowStep.gds.value.lower():
            return DbFlow.FlowStep.gds
        
        if step == DbFlow.FlowStep.drc.value.lower():
            return DbFlow.FlowStep.drc

    def initFlowStep(self):
        # 直接设置为place，不需要判断
        self.step = DbFlow.FlowStep.place
        print(f"DEBUG: step设置为 {self.step}")
        self.initFlowList()
        print(f"DEBUG: flow_list长度 {len(self.flow_list)}")
    
    def getConfigPath(self, step):
        config_path = self.workspace.get_config(self.eda_tool.value+"_config").get(step.value, None)
        return config_path

    
    def initConfigPathList(self):
        self.config_paths = dict()
        self.best_config_paths = dict()
        for db_flow in self.flow_list:
            step = db_flow.step
            step_config_path = self.workspace.paths_table.ieda_config.get(step.value, None)
            best_step_config_path = self.workspace.paths_table.ieda_config.get(step.value, None).replace(".json", "_best.json")
            if step_config_path is not None:
                self.config_paths[step.value.lower()] = step_config_path
                self.best_config_paths[step.value.lower()] = best_step_config_path

        if not len(self.config_paths):
            logging.error("self.config_paths is empty, process exit")

    def getConfigPathList(self):
        return self.config_paths
    
    def getBestConfigPathList(self):
        return self.best_config_paths

    def getStep(self):
        return self.step

    def getWorkspacePath(self):
        return  self.dir_workspace

    def loadParameters(self):
        self.params = iEDAParameter(step=self.step)
        self.params.load_list(self.config_paths)
    
    def getParameters(self):
        return self.params