#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : test_ieda_feature.py
@Author : yell
@Desc : test physical design features for iEDA
'''
######################################################################################
# import aieda
from import_aieda import import_aieda
import_aieda()
######################################################################################

from aieda import (
    workspace_create,
    DbFlow,
    DataFeature,
    DataGeneration
)


DESIGNS_T28 = [
        "/data2/project_share/dataset_baseline/s713/workspace",
        "/data2/project_share/dataset_baseline/s44/workspace",
        "/data2/project_share/dataset_baseline/apb4_rng/workspace",
        "/data2/project_share/dataset_baseline/gcd/workspace",
        "/data2/project_share/dataset_baseline/s1238/workspace",
        "/data2/project_share/dataset_baseline/s1488/workspace",
        "/data2/project_share/dataset_baseline/apb4_archinfo/workspace",
        "/data2/project_share/dataset_baseline/apb4_ps2/workspace",
        "/data2/project_share/dataset_baseline/s9234/workspace",
        "/data2/project_share/dataset_baseline/apb4_timer/workspace",
        "/data2/project_share/dataset_baseline/s13207/workspace",
        "/data2/project_share/dataset_baseline/apb4_i2c/workspace",
        "/data2/project_share/dataset_baseline/s5378/workspace",
        "/data2/project_share/dataset_baseline/apb4_pwm/workspace",
        "/data2/project_share/dataset_baseline/apb4_wdg/workspace",
        "/data2/project_share/dataset_baseline/apb4_clint/workspace",
        "/data2/project_share/dataset_baseline/ASIC/workspace",
        "/data2/project_share/dataset_baseline/s15850/workspace",
        "/data2/project_share/dataset_baseline/apb4_uart/workspace",
        "/data2/project_share/dataset_baseline/s38417/workspace",
        "/data2/project_share/dataset_baseline/s35932/workspace",
        "/data2/project_share/dataset_baseline/s38584/workspace",
        "/data2/project_share/dataset_baseline/BM64/workspace",
        "/data2/project_share/dataset_baseline/picorv32/workspace",
        "/data2/project_share/dataset_baseline/PPU/workspace",
        "/data2/project_share/dataset_baseline/blabla/workspace",
        "/data2/project_share/dataset_baseline/aes_core/workspace",
        "/data2/project_share/dataset_baseline/aes/workspace",
        "/data2/project_share/dataset_baseline/salsa20/workspace",
        "/data2/project_share/dataset_baseline/jpeg_encoder/workspace",
        "/data2/project_share/dataset_baseline/eth_top/workspace",
        # "/data2/project_share/dataset_baseline/yadan_riscv_sopc/workspace",
        # "/data2/project_share/dataset_baseline/beihai/workspace",
        # "/data2/project_share/dataset_baseline/shanghai_MS/workspace",
        # "/data2/project_share/dataset_baseline/nvdla/workspace",
        # "/data2/project_share/dataset_baseline/ZJU_asic_top/workspace",
        # "/data2/project_share/dataset_baseline/iEDA_2023/workspace",
        # "/data2/project_share/dataset_baseline/ysyx4_SoC2/workspace",
        # "/data2/project_share/dataset_baseline/BEIHAI_2.0/workspace",
        # "/data2/project_share/dataset_baseline/AIMP/workspace",
        # "/data2/project_share/dataset_baseline/AIMP_2.0/workspace",
        # "/data2/project_share/dataset_baseline/ysyx6/workspace",
        # "/data2/project_share/dataset_baseline/WUKONG/workspace",
        # "/data2/project_share/dataset_baseline/ysyx4_SoC1/workspace",
        # "/data2/project_share/dataset_baseline/ysyx4_2/workspace",
        # "/data2/project_share/dataset_baseline/T1/workspace",
        # "/data2/project_share/dataset_baseline/T1_machamp/workspace",
        # "/data2/project_share/dataset_baseline/nanhu-G/workspace",
        # "/data2/project_share/dataset_baseline/openC910/workspace",
        # "/data2/project_share/dataset_baseline/T1_sandslash/workspace",
    ]


def test_feature_generation(workspace):
    # step 1 : init data generation
    data_gen = DataGeneration(workspace)
    
    # step 2 : test generate feature summary json
    for step in ["fixFanout", 
                 "place",
                 "CTS",
                 "optDrv",
                 "optHold",
                 "legalization",
                 "route",
                 "filler"
                 ]:
        data_gen.generate_feature(step=DbFlow.FlowStep(step))
        print("generate feature summary data in step {}".format(step))
    
    # step 3 : test generate drc 
    data_gen.generate_drc()
    print("generate feature drc data in step drc")

def test_data_load(workspace):
    # step 1 : init data generation
    feature = DataFeature(workspace=workspace)
    
    # step 2 : test get feature summary db from iEDA flow
    for step in ["fixFanout", 
                 "place",
                 "CTS",
                 "optDrv",
                 "optHold",
                 "legalization",
                 "route",
                 "filler"
                 ]:
        feature_db = feature.load_feature_summary(flow=DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep(step)))
        print("get feature summary data in step {}".format(step))
        
    # # step 3 : test get feature tool db from iEDA flow
    for step in ["fixFanout", 
                 "place",
                 "CTS",
                 "optDrv",
                 "optHold",
                 "legalization",
                 "route",
                 "filler"
                 ]:
        feature_db = feature.load_feature_tool(flow=DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep(step)))
        print("get feature tool data in step {}".format(step))
        
    # # step 4 : test get feature map db from iEDA flow
    for step in ["fixFanout", 
                 "place",
                 "CTS",
                 "optDrv",
                 "optHold",
                 "legalization",
                 "route",
                 "filler"
                 ]:
        if step == "place" or step == "CTS":
            feature_db = feature.load_feature_map(flow=DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep(step)))
            print("get feature eval db in step {}".format(step))
            
    # step 5 : test get drc db 
    feature_db = feature.load_drc()
    print(1)

if __name__ == "__main__":  
    # # step 1 : create workspace
    # workspace_dir = "/data2/huangzengrong/test_aieda/sky130"
    # # workspace_dir = "/data/project_share/yhqiu/test_aieda/workspace_rerun"
    # workspace = workspace_create(directory=workspace_dir, design="gcd")
    
    # # not a must if flows has been run because feature would be generated by flow
    # # test_feature_generation(workspace)
    
    # test_data_load(workspace)

    # exit(0)
    
    for workspace_dir in DESIGNS_T28:
        print("process workspace : ", workspace_dir)
        
        design = workspace_dir.split("/")[-2]
        workspace = workspace_create(directory=workspace_dir, design=design)
        
        # not a must if flows has been run because feature would be generated by flow
        test_feature_generation(workspace)


