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
