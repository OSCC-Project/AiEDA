#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : ieda_engine.py
@Author : yell
@Desc : run iEDA
'''

from ..workspace import Workspace
from ..flows import DbFlow

def load_summary(workspace : Workspace, flow : DbFlow):
    from .io import FeatureParserJson
    
    summary_key = "{}_summary".format(flow.FlowStep.value)
    
    if flow.eda_tool.value == "iEDA":
        feature_path = workspace.paths_table.ieda_feature_json[summary_key]
        
        parser = FeatureParserJson(feature_path)
        return parser.get_summary()
    