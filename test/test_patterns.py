#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : test_ieda_patterns.py
@Author : yell
@Desc : test pattern
'''
######################################################################################
# import aieda
from import_aieda import import_aieda
import_aieda()
######################################################################################

from aieda import (
    workspace_create,
    DataGeneration,
    DataPatterns
)

def test_pattern_generation(workspace):
    # step 1 : init by workspace
    data_gen = DataGeneration(workspace)
    
    # step 2 : generate vectors
    data_gen.generate_vectors(input_def="/data/project_share/dataset_baseline/eth_top/workspace/output/innovus/result/eth_top_route.def",
                               vectors_dir="/data/project_share/dataset_baseline/eth_top/workspace/output/innovus/vectors")

def test_patterns_load(workspace):
    data_load = DataPatterns(workspace)
    
    data = data_load.load_wire_sequences(sequences_json="/data/project_share/dataset_baseline/eth_top/workspace/output/innovus/vectors/patterns/wire_sequences.json")
    print(len(data))

if __name__ == "__main__":  
    # step 1 : create workspace
    workspace_dir = "/data/project_share/dataset_baseline/eth_top/workspace"
    workspace = workspace_create(directory=workspace_dir, design="eth_top")
    
    # test_pattern_generation(workspace)
    test_patterns_load(workspace)

    exit(0)

