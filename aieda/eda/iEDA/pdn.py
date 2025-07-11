#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : pdn.py
@Author : yell
@Desc : pdn api
'''
from .io import IEDAIO
from ...workspace import Workspace
from ...flows import DbFlow

class IEDAPdn(IEDAIO):
    """pdn api"""
    def __init__(self, workspace : Workspace, flow : DbFlow):
        super().__init__(workspace=workspace, flow=flow)
        
    def build_config(self):
        pass
    
    def run_pdn(self):
        pass