#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : test_analysis_design.py
@Author : yhqiu
@Desc : test design_level data ananlysis
'''
import os
######################################################################################
# import aieda
from import_aieda import import_aieda
import_aieda()
######################################################################################

from aieda.analysis import CellTypeAnalyzer,CoreUsageAnalyzer,PinDistributionAnalyzer,ResultStatisAnalyzer
from aieda import (
    workspace_create,
    DbFlow
)

BASE_DIRS = [
    "/data2/project_share/dataset_baseline/s713",
    "/data2/project_share/dataset_baseline/s44",
    "/data2/project_share/dataset_baseline/apb4_rng",
    "/data2/project_share/dataset_baseline/gcd",
    "/data2/project_share/dataset_baseline/s1238",
    "/data2/project_share/dataset_baseline/s1488",
    "/data2/project_share/dataset_baseline/apb4_archinfo",
    "/data2/project_share/dataset_baseline/apb4_ps2",
    "/data2/project_share/dataset_baseline/s9234",
    "/data2/project_share/dataset_baseline/apb4_timer",
    "/data2/project_share/dataset_baseline/s13207",
    "/data2/project_share/dataset_baseline/apb4_i2c",
    "/data2/project_share/dataset_baseline/s5378",
    "/data2/project_share/dataset_baseline/apb4_pwm",
    "/data2/project_share/dataset_baseline/apb4_wdg",
    "/data2/project_share/dataset_baseline/apb4_clint",
    "/data2/project_share/dataset_baseline/ASIC",
    "/data2/project_share/dataset_baseline/s15850",
    "/data2/project_share/dataset_baseline/apb4_uart",
    "/data2/project_share/dataset_baseline/s38417",
    "/data2/project_share/dataset_baseline/s35932",
    "/data2/project_share/dataset_baseline/s38584",
    "/data2/project_share/dataset_baseline/BM64",
    "/data2/project_share/dataset_baseline/picorv32",
    "/data2/project_share/dataset_baseline/PPU",
    "/data2/project_share/dataset_baseline/blabla",
    "/data2/project_share/dataset_baseline/aes_core",
    "/data2/project_share/dataset_baseline/aes",
    "/data2/project_share/dataset_baseline/salsa20",
    "/data2/project_share/dataset_baseline/jpeg_encoder",
    "/data2/project_share/dataset_baseline/eth_top",
    # "/data2/project_share/dataset_baseline/yadan_riscv_sopc",
    # "/data2/project_share/dataset_baseline/beihai",
    # "/data2/project_share/dataset_baseline/shanghai_MS",
    # "/data2/project_share/dataset_baseline/nvdla",
    # "/data2/project_share/dataset_baseline/ZJU_asic_top",
    # "/data2/project_share/dataset_baseline/iEDA_2023",
    # "/data2/project_share/dataset_baseline/ysyx4_SoC2",
    # "/data2/project_share/dataset_baseline/BEIHAI_2.0",
    # "/data2/project_share/dataset_baseline/AIMP",
    # "/data2/project_share/dataset_baseline/AIMP_2.0",
    # "/data2/project_share/dataset_baseline/ysyx6",
    # "/data2/project_share/dataset_baseline/WUKONG",
    # "/data2/project_share/dataset_baseline/ysyx4_SoC1",
    # "/data2/project_share/dataset_baseline/ysyx4_2",
    # "/data2/project_share/dataset_baseline/T1",
    # "/data2/project_share/dataset_baseline/T1_machamp",
    # "/data2/project_share/dataset_baseline/nanhu-G",
    # "/data2/project_share/dataset_baseline/openC910",
    # "/data2/project_share/dataset_baseline/T1_sandslash"
]

DISPLAY_NAME = {
    "s713": "s713",
    "s44": "s44", 
    "apb4_rng": "apb4_rng",
    "gcd": "gcd",
    "s1238": "s1238",
    "s1488": "s1488",
    "apb4_archinfo": "apb4_arch",
    "apb4_ps2": "apb4_ps2",
    "s9234": "s9234",
    "apb4_timer": "apb4_timer",
    "s13207": "s13207",
    "apb4_i2c": "apb4_i2c",
    "s5378": "s5378",
    "apb4_pwm": "apb4_pwm",
    "apb4_wdg": "apb4_wdg",
    "apb4_clint": "apb4_clint",
    "ASIC": "ASIC",
    "s15850": "s15850",
    "apb4_uart": "apb4_uart",
    "s38417": "s38417",
    "s35932": "s35932",
    "s38584": "s38584",
    "BM64": "BM64",
    "picorv32": "picorv32",
    "PPU": "PPU",
    "blabla": "blabla",
    "aes_core": "aes_core",
    "aes": "aes",
    "salsa20": "salsa20",
    "jpeg_encoder": "jpeg",
    "eth_top": "eth_top",
    "yadan_riscv_sopc": "yadan",
    "beihai": "beihai",
    "shanghai_MS": "SHMS",
    "nvdla": "nvdla",
    "ZJU_asic_top": "ZJUC",
    "iEDA_2023": "iEDA23",
    "ysyx4_SoC2": "ysyx4S2",
    "BEIHAI_2.0": "beihai2",
    "AIMP": "AIMP",
    "AIMP_2.0": "AIMP2",
    "ysyx6": "ysyx6",
    "WUKONG": "wukong",
    "ysyx4_SoC1": "ysyx41",
    "ysyx4_2": "ysyx42",
    "T1": "T1",
    "T1_machamp": "T1_mach",
    "nanhu-G": "nanhu-G",
    "openC910": "openC910",
    "T1_sandslash": "T1_sand"
}


def main():
    # step 0: create workspace list
    workspace_list = []
    for base_dir in BASE_DIRS:
        workspace = workspace_create(directory=base_dir+"/workspace", design = os.path.basename(base_dir))
        workspace_list.append(workspace)
        
    # step 1: test cell type analysis
    cell_analyzer = CellTypeAnalyzer()
    cell_analyzer.load(
        workspace_dirs=workspace_list,
        flow = DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.route),
        dir_to_display_name=DISPLAY_NAME
        )
    cell_analyzer.analyze()
    cell_analyzer.visualize(save_path="./")
    
    
    # step 2: test core usage analysis
    core_analyzer = CoreUsageAnalyzer()
    core_analyzer.load(
        workspace_dirs=workspace_list,
        flow = DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.route)
    )
    core_analyzer.analyze()
    core_analyzer.visualize(save_path="./")
    
    
    # step 3: test pin distribution analysis
    pin_analyzer = PinDistributionAnalyzer()
    pin_analyzer.load(
        workspace_dirs=workspace_list,
        flow = DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.route)
    )
    pin_analyzer.analyze()
    pin_analyzer.visualize(save_path="./")
    
    
    # step 4: test result statistics
    result_analyzer = ResultStatisAnalyzer()
    result_analyzer.load(
        workspace_dirs=workspace_list, 
        pattern="/output/innovus/vectors",
        dir_to_display_name=DISPLAY_NAME,
        calc_wire_num=False,  # set to False to avoid calculating wire number
    )
    result_analyzer.analyze()
    result_analyzer.visualize(save_path="./")
    

if __name__ == "__main__":  
    main()



