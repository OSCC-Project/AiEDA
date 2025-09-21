#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
批量提取布局特征脚本
自动处理dataset_skywater130目录下已经产生place的设计
"""

import os
import sys
import glob
import shutil
import tempfile
from pathlib import Path

# 设置环境和路径
os.environ["iEDA"] = "ON"
sys.path.append(os.getcwd())

from aieda.workspace import Workspace, workspace_create
from aieda.flows import DbFlow, RunIEDA, DataGeneration
from aieda.data.database import EDAParameters


def find_designs_with_place(dataset_dir):
    """找到所有有place目录的设计"""
    designs = []
    for design_dir in Path(dataset_dir).iterdir():
        if design_dir.is_dir():
            place_dir = design_dir / "place"
            syn_netlist_dir = design_dir / "syn_netlist"
            if place_dir.exists() and syn_netlist_dir.exists():
                designs.append(design_dir.name)
    return sorted(designs)


def get_design_files(dataset_dir, design_name):
    """获取设计的def和sdc文件路径"""
    design_dir = Path(dataset_dir) / design_name

    # 查找def文件
    place_dir = design_dir / "place"
    def_files = list(place_dir.glob("*.def")) + list(place_dir.glob("*.def.gz"))
    if not def_files:
        return None, None
    def_file = def_files[0]

    # 查找sdc文件
    syn_netlist_dir = design_dir / "syn_netlist"
    sdc_files = list(syn_netlist_dir.glob("*.sdc"))
    if not sdc_files:
        return None, None
    sdc_file = sdc_files[0]

    return str(def_file), str(sdc_file)


def process_sdc_file(sdc_path):
    """处理sdc文件，临时删除set_propagated_clock [all_clocks]"""
    with open(sdc_path, 'r') as f:
        content = f.read()

    # 检查是否包含set_propagated_clock
    original_content = content
    modified = False

    lines = content.split('\n')
    filtered_lines = []
    for line in lines:
        if 'set_propagated_clock' in line and '[all_clocks]' in line:
            print(f"  临时移除: {line.strip()}")
            modified = True
        else:
            filtered_lines.append(line)

    if modified:
        # 创建临时文件
        temp_fd, temp_path = tempfile.mkstemp(suffix='.sdc')
        with os.fdopen(temp_fd, 'w') as f:
            f.write('\n'.join(filtered_lines))
        return temp_path, original_content, sdc_path
    else:
        return sdc_path, None, None


def restore_sdc_file(original_content, original_path):
    """恢复sdc文件原始内容"""
    if original_content is not None:
        with open(original_path, 'w') as f:
            f.write(original_content)


def create_workspace_for_design(workspace_dir, design_name, def_file, sdc_file):
    """为特定设计创建workspace"""
    flow_db_list = [
        DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.floorplan, state=DbFlow.FlowState.Unstart),
        DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.pdn, state=DbFlow.FlowState.Unstart),
        DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.fixFanout, state=DbFlow.FlowState.Unstart),
        DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.place, state=DbFlow.FlowState.Unstart),
        DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.cts, state=DbFlow.FlowState.Unstart),
        DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.optDrv, state=DbFlow.FlowState.Unstart),
        DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.optHold, state=DbFlow.FlowState.Unstart),
        DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.legalization, state=DbFlow.FlowState.Unstart),
        DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.route, state=DbFlow.FlowState.Unstart),
        DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.drc, state=DbFlow.FlowState.Unstart),
        DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.vectorization, state=DbFlow.FlowState.Unstart),
        DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.filler, state=DbFlow.FlowState.Unstart)
    ]

    workspace = workspace_create(directory=workspace_dir, design=design_name, flow_list=flow_db_list)

    # 设置基本路径
    current_dir = os.path.split(os.path.abspath(__file__))[0]
    root = current_dir.rsplit("/", 1)[0]
    foundry_dir = f"{root}/aieda/third_party/iEDA/scripts/foundry/sky130"

    # 设置verilog输入 - 统一使用gcd.v
    sky130_gcd_verilog = f"{root}/aieda/third_party/iEDA/scripts/design/sky130_gcd/result/verilog/gcd.v"
    workspace.set_verilog_input(sky130_gcd_verilog)

    # 设置tech lef
    workspace.set_tech_lef(f"{foundry_dir}/lef/sky130_fd_sc_hd.tlef")

    # 设置lefs
    lefs = [
        f"{foundry_dir}/lef/sky130_fd_sc_hd_merged.lef",
        f"{foundry_dir}/lef/sky130_ef_io__com_bus_slice_10um.lef",
        f"{foundry_dir}/lef/sky130_ef_io__com_bus_slice_1um.lef",
        f"{foundry_dir}/lef/sky130_ef_io__com_bus_slice_20um.lef",
        f"{foundry_dir}/lef/sky130_ef_io__com_bus_slice_5um.lef",
        f"{foundry_dir}/lef/sky130_ef_io__connect_vcchib_vccd_and_vswitch_vddio_slice_20um.lef",
        f"{foundry_dir}/lef/sky130_ef_io__corner_pad.lef",
        f"{foundry_dir}/lef/sky130_ef_io__disconnect_vccd_slice_5um.lef",
        f"{foundry_dir}/lef/sky130_ef_io__disconnect_vdda_slice_5um.lef",
        f"{foundry_dir}/lef/sky130_ef_io__gpiov2_pad_wrapped.lef",
        f"{foundry_dir}/lef/sky130_ef_io__vccd_hvc_pad.lef",
        f"{foundry_dir}/lef/sky130_ef_io__vccd_lvc_pad.lef",
        f"{foundry_dir}/lef/sky130_ef_io__vdda_hvc_pad.lef",
        f"{foundry_dir}/lef/sky130_ef_io__vdda_lvc_pad.lef",
        f"{foundry_dir}/lef/sky130_ef_io__vddio_hvc_pad.lef",
        f"{foundry_dir}/lef/sky130_ef_io__vddio_lvc_pad.lef",
        f"{foundry_dir}/lef/sky130_ef_io__vssa_hvc_pad.lef",
        f"{foundry_dir}/lef/sky130_ef_io__vssa_lvc_pad.lef",
        f"{foundry_dir}/lef/sky130_ef_io__vssd_hvc_pad.lef",
        f"{foundry_dir}/lef/sky130_ef_io__vssd_lvc_pad.lef",
        f"{foundry_dir}/lef/sky130_ef_io__vssio_hvc_pad.lef",
        f"{foundry_dir}/lef/sky130_ef_io__vssio_lvc_pad.lef",
        f"{foundry_dir}/lef/sky130_fd_io__top_xres4v2.lef",
        f"{foundry_dir}/lef/sky130io_fill.lef",
        f"{foundry_dir}/lef/sky130_sram_1rw1r_128x256_8.lef",
        f"{foundry_dir}/lef/sky130_sram_1rw1r_44x64_8.lef",
        f"{foundry_dir}/lef/sky130_sram_1rw1r_64x256_8.lef",
        f"{foundry_dir}/lef/sky130_sram_1rw1r_80x64_8.lef"
    ]
    workspace.set_lefs(lefs)

    # 设置libs
    libs = [
        f"{foundry_dir}/lib/sky130_fd_sc_hd__tt_025C_1v80.lib",
        f"{foundry_dir}/lib/sky130_dummy_io.lib",
        f"{foundry_dir}/lib/sky130_sram_1rw1r_128x256_8_TT_1p8V_25C.lib",
        f"{foundry_dir}/lib/sky130_sram_1rw1r_44x64_8_TT_1p8V_25C.lib",
        f"{foundry_dir}/lib/sky130_sram_1rw1r_64x256_8_TT_1p8V_25C.lib",
        f"{foundry_dir}/lib/sky130_sram_1rw1r_80x64_8_TT_1p8V_25C.lib"
    ]
    workspace.set_libs(libs)

    # 设置sdc
    workspace.set_sdc(sdc_file)

    # 设置spef
    workspace.set_spef("")

    # 设置workspace信息
    workspace.set_process_node("sky130")
    workspace.set_project(design_name)
    workspace.set_design(design_name)
    workspace.set_version("V1")
    workspace.set_task("run_eda")
    workspace.set_first_routing_layer("li1")

    # 配置iEDA
    workspace.set_ieda_fixfanout_buffer("sky130_fd_sc_hs__buf_8")
    workspace.set_ieda_cts_buffers(["sky130_fd_sc_hs__buf_1"])
    workspace.set_ieda_cts_root_buffer("sky130_fd_sc_hs__buf_1")
    workspace.set_ieda_placement_buffers(["sky130_fd_sc_hs__buf_1"])
    workspace.set_ieda_filler_cells_for_first_iteration([
        "sky130_fd_sc_hs__fill_8", "sky130_fd_sc_hs__fill_4",
        "sky130_fd_sc_hs__fill_2", "sky130_fd_sc_hs__fill_1"
    ])
    workspace.set_ieda_filler_cells_for_second_iteration([
        "sky130_fd_sc_hs__fill_8", "sky130_fd_sc_hs__fill_4",
        "sky130_fd_sc_hs__fill_2", "sky130_fd_sc_hs__fill_1"
    ])
    workspace.set_ieda_optdrv_buffers(["sky130_fd_sc_hs__buf_8"])
    workspace.set_ieda_opthold_buffers(["sky130_fd_sc_hs__buf_8"])
    workspace.set_ieda_optsetup_buffers(["sky130_fd_sc_hs__buf_8"])
    workspace.set_ieda_router_layer(bottom_layer="met1", top_layer="met4")

    return workspace


def generate_vectors_for_design(workspace, def_file):
    """为设计生成特征向量"""
    data_gen = DataGeneration(workspace)
    vectors_dir = workspace.paths_table.ieda_output["pl_vectors"]

    data_gen.generate_vectors(
        input_def=def_file,
        vectors_dir=vectors_dir,
        patch_row_step=18,
        patch_col_step=18,
        batch_mode=False,
        is_placement_mode=True,
        sta_mode=1
    )


def main():
    """主函数"""
    # 设置路径
    current_dir = os.path.split(os.path.abspath(__file__))[0]
    root = current_dir.rsplit("/", 1)[0]
    dataset_dir = f"{root}/example/dataset_skywater130"
    output_base_dir = f"{root}/example/batch_features"

    # 确保输出目录存在
    os.makedirs(output_base_dir, exist_ok=True)

    print("=== 批量布局特征提取 ===")
    print(f"数据集目录: {dataset_dir}")
    print(f"输出目录: {output_base_dir}")

    # 查找所有有place的设计
    designs = find_designs_with_place(dataset_dir)
    print(f"\n找到 {len(designs)} 个设计有place目录:")
    for design in designs:
        print(f"  - {design}")

    if not designs:
        print("没有找到任何有place目录的设计")
        return

    # 处理每个设计
    success_count = 0
    for i, design_name in enumerate(designs, 1):
        print(f"\n[{i}/{len(designs)}] 处理设计: {design_name}")

        try:
            # 获取设计文件
            def_file, sdc_file = get_design_files(dataset_dir, design_name)
            if not def_file or not sdc_file:
                print(f"  跳过: 缺少必要文件")
                continue

            print(f"  DEF文件: {def_file}")
            print(f"  SDC文件: {sdc_file}")

            # 处理sdc文件
            processed_sdc, original_content, original_path = process_sdc_file(sdc_file)

            # 创建workspace
            workspace_dir = f"{output_base_dir}/{design_name}"
            workspace = create_workspace_for_design(workspace_dir, design_name, def_file, processed_sdc)

            # 生成特征向量
            print(f"  开始生成特征向量...")
            generate_vectors_for_design(workspace, def_file)

            # 恢复sdc文件
            if original_content:
                restore_sdc_file(original_content, original_path)
                os.unlink(processed_sdc)  # 删除临时文件

            print(f"  完成: {design_name}")
            success_count += 1

        except Exception as e:
            print(f"  错误: {design_name} - {str(e)}")
            continue

    print(f"\n=== 批量处理完成 ===")
    print(f"成功处理: {success_count}/{len(designs)} 个设计")
    print(f"结果保存在: {output_base_dir}")


if __name__ == "__main__":
    main()