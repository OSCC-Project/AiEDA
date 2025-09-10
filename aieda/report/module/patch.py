#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : patch.py
@Author : yell
@Desc : patch data analyse report
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


class ReportPatch(ReportBase):
    def __init__(self, workspace: Workspace):
        super().__init__(workspace=workspace)
        
    def generate_markdown(self, path : str):
        pass
    
    def generate_pdf(self, path : str):
        pass
    
    def patch_congestion_wire_density_regression(self):  
        table = self.Image(image_path=self.workspace.paths_table.get_image_path(
            image_type="patch_congestion_wire_density_regression",
            design_name=self.workspace.design
        ))