#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : summary.py
@Author : yell
@Desc : summary reports for workspace
"""

import os

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np

from ...data import DataVectors
from ...workspace import Workspace
from ...data import DataFeature
from ...flows import DbFlow
from .base import ReportBase

class ReportFlow(ReportBase):
    def __init__(self, workspace: Workspace):
        super().__init__(workspace=workspace)
        
    def generate_markdown(self, path : str):
        pass
    
    def generate_pdf(self, path : str):
        pass
    
    def flow_summary(self):  
        table = self.TableMatrix(headers=["step", "eda tool", "state", "runtime"])
        
        # flow states
        for flow in self.workspace.configs.flows:
            table.add_row([flow.step.value, 
                           flow.eda_tool, 
                           flow.state.value,
                           flow.runtime])
            
        return table.make_table() 
    
    def content_flow(self, flow):
        table = self.TableParameters(max_num=4)   
        
        feature = DataFeature(workspace=self.workspace)
        feature_db = feature.load_feature_summary(flow)
        if feature_db is None:
            return ""
        
        table.add_parameter("die usage", feature_db.layout.die_usage)
        table.add_parameter("core usage", feature_db.layout.core_usage)
        table.add_parameter("instance num", feature_db.statis.num_instances)
        table.add_parameter("net num", feature_db.statis.num_nets)
        
        return table.make_table()