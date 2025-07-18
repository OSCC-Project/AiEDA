#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : feature.py
@Author : yell
@Desc : data feature api
'''
from ..workspace.workspace import Workspace
from ..flows import DbFlow
def load_feature_summary(workspace : Workspace, flow : DbFlow):
    """workspace : Workspace data
       flow : DbFlow
    """
    from .io import FeatureParserJson
    summary_key = "{}_summary".format(flow.step.value)
    
    if flow.eda_tool == "iEDA":
        feature_path = workspace.paths_table.ieda_feature_json[summary_key]
        
        parser = FeatureParserJson(feature_path)
        return parser.get_summary()
    
def load_feature_tool(workspace : Workspace, flow : DbFlow):
    """workspace : Workspace data
       flow : DbFlow
    """
    from .io import FeatureParserJson   
    tool_key = "{}_tool".format(flow.step.value)
    
    if flow.eda_tool == "iEDA":
        feature_path = workspace.paths_table.ieda_feature_json[tool_key]
        
        parser = FeatureParserJson(feature_path)
        return parser.get_tools()