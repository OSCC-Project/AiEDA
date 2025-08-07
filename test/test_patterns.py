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
    # vectors_dir="/data/project_share/dataset_baseline/eth_top/workspace/output/innovus/vectors"
    # data_gen.generate_patterns(vectors_dir=vectors_dir)
    data_gen.generate_patterns()

def test_patterns_load(workspace):
    data_load = DataPatterns(workspace)
    
    # data = data_load.load_wire_sequences(sequences_json="/data/project_share/dataset_baseline/eth_top/workspace/output/innovus/vectors/patterns/wire_sequences.json")
    data = data_load.load_wire_sequences()
    print(len(data))

if __name__ == "__main__":  
    # step 1 : create workspace
    workspace_dir = "/data2/huangzengrong/test_aieda/sky130_1"
    workspace = workspace_create(directory=workspace_dir, design="gcd")
    
    # test_pattern_generation(workspace)
    test_patterns_load(workspace)

    exit(0)

