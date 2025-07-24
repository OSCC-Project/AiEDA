#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : vecorization.py
@Author : yell
@Desc : eda data vecorization api
'''
from multiprocessing import Process
from .io import IEDAIO
from ...workspace import Workspace
from ...flows import DbFlow
from ...data.database.enum import FeatureOption

class IEDAVectorization(IEDAIO):
    """eda data vecorization api"""
    def __init__(self, workspace : Workspace, flow : DbFlow, vectors_dir : str = None):
        self.vectors_dir = vectors_dir
        super().__init__(workspace=workspace, flow=flow)
        
    def build_config(self):
        if self.vectors_dir is None:
            self.vectors_dir = self.workspace.paths_table.ieda_output['vectors']
    
    def generate_vectors(self):
        def __generate_vectors__():
            self.read_def() 

            self.ieda.generate_vectors(dir=self.vectors_dir)
        
        if self.inited_flag:
            __generate_vectors__()
        else:
            p = Process(target=__generate_vectors__, args=())
            p.start()
            p.join()