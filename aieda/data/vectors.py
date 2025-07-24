#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : vectorization.py
@Author : yell
@Desc : data vectorization api
'''
from ..workspace.workspace import Workspace
from ..flows import DbFlow

class DataVectors:
    def __init__(self, workspace : Workspace):
        self.workspace = workspace