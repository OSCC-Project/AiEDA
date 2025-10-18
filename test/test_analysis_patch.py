#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : test_analysis_patch.py
@Author : yhqiu
@Desc : test patch_level data ananlysis
"""
######################################################################################
# # import aieda
# from import_aieda import import_aieda
# import_aieda()
######################################################################################

from aieda.analysis import WireDensityAnalyzer, FeatureCorrelationAnalyzer, MapAnalyzer
from aieda.workspace import workspace_create

import os

current_dir = os.path.split(os.path.abspath(__file__))[0]
root = current_dir.rsplit("/", 1)[0]
workspace_dir = "{}/example/sky130_test".format(root)

# all workspace directory
WORKSPACES = {"gcd": workspace_dir}

# name map
DISPLAY_NAME = {"gcd": "GCD"}


def main():
    # step 0: create workspace list
    workspace_list = []
    for design, dir in WORKSPACES.items():
        workspace = workspace_create(directory=dir, design=design)
        workspace_list.append(workspace)

    # step 1: Wire Density Analysis
    wire_analyzer = WireDensityAnalyzer()
    wire_analyzer.load(
        workspaces=workspace_list,
        pattern="/output/iEDA/vectors/patchs",
        dir_to_display_name=DISPLAY_NAME,
    )
    wire_analyzer.analyze()
    wire_analyzer.visualize()

    # step 2: Feature Correlation Analysis
    feature_analyzer = FeatureCorrelationAnalyzer()
    feature_analyzer.load(
        workspaces=workspace_list,
        pattern="/output/iEDA/vectors/patchs",
        dir_to_display_name=DISPLAY_NAME,
    )
    feature_analyzer.analyze()
    feature_analyzer.visualize()

    # step 3: Map Analysis
    workspace = workspace_create(directory=workspace_dir, design="gcd")

    map_analyzer = MapAnalyzer()
    map_analyzer.load(
        workspaces=[workspace],
        pattern="/output/iEDA/vectors/patchs",
        dir_to_display_name={"gcd": "GCD"},
    )
    map_analyzer.analyze()
    map_analyzer.visualize(save_path=workspace_dir)


if __name__ == "__main__":
    main()
