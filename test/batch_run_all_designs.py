#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
批量运行所有设计配置脚本
"""

import os
import glob
import sys
from pathlib import Path
import re

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from test_sky130_route_data import create_workspace_sky130, run_eda_flow


def find_design_files(design_dir):
    """
    在设计目录中查找.def文件和sdc文件
    """
    design_name = os.path.basename(design_dir)

    # 查找place文件夹中的所有.def.gz文件
    place_dir = os.path.join(design_dir, "place")
    def_files = glob.glob(os.path.join(place_dir, "*.def.gz"))
    
    # 尝试在place目录中查找sdc文件
    sdc_files = glob.glob(os.path.join(place_dir, "*.sdc"))
    
    # 如果在place目录中没有找到sdc，尝试在demo目录的对应设计中查找
    if not sdc_files:
        demo_dir = os.path.join("/data2/project_share/dataset_skywater130_demo", design_name)
        if os.path.exists(demo_dir):
            demo_place_dir = os.path.join(demo_dir, "place")
            demo_sdc_files = glob.glob(os.path.join(demo_place_dir, "*.sdc"))
            if demo_sdc_files:
                sdc_files = demo_sdc_files
            else:
                # 也可以尝试在route目录中查找
                demo_route_dir = os.path.join(demo_dir, "route")
                if os.path.exists(demo_route_dir):
                    demo_sdc_files = glob.glob(os.path.join(demo_route_dir, "*.sdc"))
                    if demo_sdc_files:
                        sdc_files = demo_sdc_files

    return {
        "design": design_name,
        "def_files": def_files,
        "sdc": sdc_files[0] if sdc_files else ""
    }


def run_eda_flow_with_def(workspace, def_file):
    """
    使用指定的def文件运行EDA流程
    直接传递def_file路径
    """
    from aieda.flows import RunIEDA
    
    run_ieda = RunIEDA(workspace)
    
    print(f"使用自定义DEF文件: {def_file}")
    
    # 复制def文件到workspace的预期路径，以便iEDA能够找到它
    import shutil
    import os
    
    # 创建输出目录
    output_dir = os.path.join(workspace.directory, "output", "iEDA", "result")
    # 如果输出目录已经存在，说明已经执行过了，这时候要跳过执行后续步骤
    if os.path.exists(output_dir):
        place_file = os.path.join(output_dir, f"{workspace.design}_place.def.gz")
        if os.path.exists(place_file):
            print(f"检测到输出目录已存在且包含完整结果: {output_dir}")
            print("跳过EDA流程执行")
            return
        else:
            print(f"输出目录存在但流程未完成，继续执行...")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 复制def文件到正确的位置和名称
    target_def = os.path.join(output_dir, f"{workspace.design}_place.def.gz")
    shutil.copy2(def_file, target_def)
    # print(f"已复制DEF文件到: {target_def}")
    
    run_ieda.run_legalization(
        input_def=target_def
    )    
    
    target_def = os.path.join(output_dir, f"{workspace.design}_legalization.def.gz")
    run_ieda.run_CTS(
        input_def=target_def
    )
    
    target_def = os.path.join(output_dir, f"{workspace.design}_CTS.def.gz")
    run_ieda.run_legalization(
        input_def=target_def
    )
    
    target_def = os.path.join(output_dir, f"{workspace.design}_legalization.def.gz")
    run_ieda.run_routing(
        input_def=target_def
    )
    

def run_design_variant(design, def_file, sdc, root):
    """
    运行单个设计
    """
    # 从def文件名提取变体信息
    def_name = os.path.basename(def_file).replace('.def.gz', '')
    variant_info = def_name[len(design)+1:]  # 去掉设计名前缀和下划线
    
    # 按照test_sky130_route_data.py的格式配置verilog和workspace_dir
    workspace_dir = "{}/test/output_test".format(root)
    
    # 尝试找到对应的verilog文件（与def文件同名但扩展名为.v.gz）
    verilog_file = def_file.replace('.def.gz', '.v.gz')
    if not os.path.exists(verilog_file):
        # 如果找不到对应的verilog，使用def文件所在目录中的第一个v.gz文件
        verilog_files = glob.glob(os.path.join(os.path.dirname(def_file), "*.v.gz"))
        verilog_file = verilog_files[0] if verilog_files else "/data2/project_share/dataset_skywater130/aes/place/aes_a_place_congestion_best.v.gz"

    print(f"开始处理设计变体: {design}_{variant_info}")
    print(f"  Workspace: {workspace_dir}")
    print(f"  DEF: {def_file}")
    print(f"  Verilog: {verilog_file}")
    print(f"  SDC: {sdc}")

    # 使用设计名+变体信息作为workspace的设计标识
    design_id = f"{design}_{variant_info}"
    workspace = create_workspace_sky130(workspace_dir, design_id, verilog_file, sdc, "")
    
    # 使用自定义的run_eda_flow_with_def函数，传入def_file
    run_eda_flow_with_def(workspace, def_file)
    
    print(f"设计变体 {design}_{variant_info} 完成")
    return True


def run_design(design_config, root):
    """
    运行单个设计的所有变体
    """
    design = design_config["design"]
    sdc = design_config["sdc"]
    def_files = design_config["def_files"]

    print(f"\n开始处理设计: {design}")
    print(f"找到 {len(def_files)} 个设计变体")
    
    success_count = 0
    total_variants = len(def_files)
    
    for def_file in def_files:
        if run_design_variant(design, def_file, sdc, root):
            success_count += 1
        print("-" * 50)
    
    print(f"设计 {design} 处理完成: {success_count}/{total_variants} 个变体成功")
    return success_count > 0


def main():
    # 配置路径 
    dataset_dir = "/data2/project_share/dataset_skywater130"
    current_dir = os.path.split(os.path.abspath(__file__))[0]
    root = current_dir.rsplit("/", 1)[0]

    # 获取所有设计目录
    design_dirs = [d for d in glob.glob(os.path.join(dataset_dir, "*"))
                   if os.path.isdir(d) and os.path.exists(os.path.join(d, "place"))]

    print(f"找到 {len(design_dirs)} 个设计:")
    for design_dir in design_dirs:
        print(f"  - {os.path.basename(design_dir)}")

    # 处理每个设计
    success_count = 0
    total_count = len(design_dirs)

    for design_dir in design_dirs:
        design_config = find_design_files(design_dir)

        if run_design(design_config, root):
            success_count += 1
        
        print("=" * 70)

    print(f"批量运行完成: {success_count}/{total_count} 个设计成功")


if __name__ == "__main__":
    main()