#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : base.py
@Author : yell
@Desc : iEDA base framework
'''
import os
if os.environ.get('iEDA') == "on":
    from ...third_party.iEDA.bin import ieda_py as ieda
else:
    ieda = None

from ...workspace import Workspace
from ...flows import DbFlow

class IEDABase():
    """Manage flow"""  
    def __init__(self, workspace : Workspace, flow : DbFlow):
        if(ieda == None):
            workspace.logger.error("Error, iEDA library is not load.")
            exit(0)
        self.ieda = ieda #iEDA 
        self.workspace = workspace
        self.flow = flow

        self.build_config()
        
    def build_config(self):
        pass
        
    def get_ieda(self):
        return self.ieda
