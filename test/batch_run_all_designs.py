#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
批量运行所有设计配置脚本
"""

import os
import glob
import sys
from pathlib import Path

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from test_sky130_route_data import create_workspace_sky130, run_eda_flow


def find_design_files(design_dir):
    """
    在设计目录中查找sdc和spef文件
    """
    design_name = os.path.basename(design_dir)

    # 查找place文件夹中的sdc文件
    place_dir = os.path.join(design_dir, "place")
    sdc_files = glob.glob(os.path.join(place_dir, "*.sdc"))

    # 查找route文件夹中的spef文件
    route_dir = os.path.join(design_dir, "route")
    spef_files = []
    for root, dirs, files in os.walk(route_dir):
        spef_files.extend(glob.glob(os.path.join(root, "*.spef")))

    return {
        "design": design_name,
        "sdc": sdc_files[0] if sdc_files else "",
        "spef": spef_files[0] if spef_files else ""
    }


def run_design(design_config, root):
    """
    运行单个设计
    """
    design = design_config["design"]
    sdc = design_config["sdc"]
    spef = design_config["spef"]

    # 按照test_sky130_route_data.py的格式配置verilog和workspace_dir
    workspace_dir = "{}/test/output_test".format(root)
    verilog = "{}/test/output_test/{}/output_test/iEDA/result/{}_place.v.gz".format(root, design, design)

    print(f"开始处理设计: {design}")
    print(f"  Workspace: {workspace_dir}")
    print(f"  Verilog: {verilog}")
    print(f"  SDC: {sdc}")
    print(f"  SPEF: {spef}")

    if not sdc:
        print(f"警告: 设计 {design} 未找到sdc文件，跳过")
        return False

    try:
        workspace = create_workspace_sky130(workspace_dir, design, verilog, sdc, spef)
        run_eda_flow(workspace)
        print(f"设计 {design} 完成")
        return True
    except Exception as e:
        print(f"设计 {design} 运行失败: {str(e)}")
        return False


def main():
    # 配置路径
    dataset_dir = "/data2/home/zyx/project_share/dataset_skywater130_demo"
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

        print("-" * 50)

    print(f"批量运行完成: {success_count}/{total_count} 个设计成功")


if __name__ == "__main__":
    main()