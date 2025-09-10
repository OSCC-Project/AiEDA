#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : foundry.py
@Author : yell
@Desc : foundry info report
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


class ReportFoundry(ReportBase):
    def __init__(self, workspace: Workspace):
        super().__init__(workspace=workspace)
        
    def generate_markdown(self, path : str):
        pass
    
    def generate_pdf(self, path : str):
        pass
    
    def content_path(self):  
        table = self.TableMatrix(headers=["configs", "paths"])

        table.add_row(("tech lef", self.workspace.configs.paths.tech_lef_path))
        table.add_row(("lefs", self.workspace.configs.paths.lef_paths))
        table.add_row(("libs", self.workspace.configs.paths.lib_paths))
        table.add_row(("sdc", self.workspace.configs.paths.sdc_path))
        table.add_row(("spef", self.workspace.configs.paths.spef_path))
            
        return table.make_table()
    
    def content_tech(self):  
        table = self.TableParameters(max_num=4) 

        feature = DataFeature(workspace=self.workspace)
        feature_db = feature.load_feature_summary(
            flow=DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.fixFanout)
        )
        
        table.add_parameter("dbu", feature_db.layout.design_dbu)
        table.add_parameter("die area", feature_db.layout.die_area)
        table.add_parameter("core area", feature_db.layout.core_area)
        table.add_parameter("layer num", feature_db.statis.num_layers)
        table.add_parameter("routing layer", feature_db.statis.num_layers_routing)
        table.add_parameter("cut layer", feature_db.statis.num_layers_cut)
        table.add_parameter("io pin num", feature_db.statis.num_iopins)
            
        return table.make_table()
