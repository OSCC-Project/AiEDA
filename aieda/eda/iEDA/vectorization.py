#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : cts.py
@Author : yell
@Desc : CTS api
'''
from .io import IEDAIO
from ...workspace import Workspace
from ...flows import DbFlow
from ...data.database.enum import FeatureOption

class IEDAVectorization(IEDAIO):
    """CTS api"""
    def __init__(self, workspace : Workspace, flow : DbFlow):
        super().__init__(workspace=workspace, flow=flow)
        
    def build_config(self):
        self.result_dir = self.workspace.paths_table.ieda_output['vectors']
    
    def run_vectorization(self):
        self.read_def() 
        
        self.generate_vectors(dir=self.result_dir)