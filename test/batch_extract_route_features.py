#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Batch extract routing features from multiple designs in dataset_skywater130
"""

import os
import sys

os.environ["iEDA"] = "ON"
sys.path.append(os.getcwd())

from aieda.workspace import Workspace, workspace_create
from aieda.flows import DbFlow, DataGeneration

# 完整设计列表 (有完整的DEF, SPEF, SDC文件)
COMPLETE_DESIGNS = [
    "aes", "aes_core", "apb4_archinfo", "apb4_clint", "apb4_i2c", "apb4_ps2",
    "apb4_rng", "apb4_timer", "apb4_uart", "apb4_wdg", "blabla", "gcd",
    "picorv32", "PPU", "s1238", "s13207", "s1488", "s15850", "s35932",
    "s38417", "s38584", "s44", "s5378", "s713", "s9234", "salsa20"
]

def create_workspace_sky130_design(workspace_dir, design_name, dataset_dir):
    """为指定设计创建workspace"""
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
        DbFlow(eda_tool="iEDA", step=DbFlow.FlowStep.filler, state=DbFlow.FlowState.Unstart),
    ]

    workspace = workspace_create(
        directory=workspace_dir, design=design_name, flow_list=flow_db_list
    )

    current_dir = os.path.split(os.path.abspath(__file__))[0]
    root = current_dir.rsplit("/", 1)[0]
    foundry_dir = "{}/aieda/third_party/iEDA/scripts/foundry/sky130".format(root)

    # 设置verilog输入（从参考文件路径）
    sky130_verilog = "{}/aieda/third_party/iEDA/scripts/design/sky130_gcd/result/verilog/gcd.v".format(root)
    workspace.set_verilog_input(sky130_verilog)

    # 设置tech lef
    workspace.set_tech_lef("{}/lef/sky130_fd_sc_hd.tlef".format(foundry_dir))

    # 设置lefs
    lefs = [
        "{}/lef/sky130_fd_sc_hd_merged.lef".format(foundry_dir),
        "{}/lef/sky130_ef_io__com_bus_slice_10um.lef".format(foundry_dir),
        "{}/lef/sky130_ef_io__com_bus_slice_1um.lef".format(foundry_dir),
        "{}/lef/sky130_ef_io__com_bus_slice_20um.lef".format(foundry_dir),
        "{}/lef/sky130_ef_io__com_bus_slice_5um.lef".format(foundry_dir),
        "{}/lef/sky130_ef_io__connect_vcchib_vccd_and_vswitch_vddio_slice_20um.lef".format(foundry_dir),
        "{}/lef/sky130_ef_io__corner_pad.lef".format(foundry_dir),
        "{}/lef/sky130_ef_io__disconnect_vccd_slice_5um.lef".format(foundry_dir),
        "{}/lef/sky130_ef_io__disconnect_vdda_slice_5um.lef".format(foundry_dir),
        "{}/lef/sky130_ef_io__gpiov2_pad_wrapped.lef".format(foundry_dir),
        "{}/lef/sky130_ef_io__vccd_hvc_pad.lef".format(foundry_dir),
        "{}/lef/sky130_ef_io__vccd_lvc_pad.lef".format(foundry_dir),
        "{}/lef/sky130_ef_io__vdda_hvc_pad.lef".format(foundry_dir),
        "{}/lef/sky130_ef_io__vdda_lvc_pad.lef".format(foundry_dir),
        "{}/lef/sky130_ef_io__vddio_hvc_pad.lef".format(foundry_dir),
        "{}/lef/sky130_ef_io__vddio_lvc_pad.lef".format(foundry_dir),
        "{}/lef/sky130_ef_io__vssa_hvc_pad.lef".format(foundry_dir),
        "{}/lef/sky130_ef_io__vssa_lvc_pad.lef".format(foundry_dir),
        "{}/lef/sky130_ef_io__vssd_hvc_pad.lef".format(foundry_dir),
        "{}/lef/sky130_ef_io__vssd_lvc_pad.lef".format(foundry_dir),
        "{}/lef/sky130_ef_io__vssio_hvc_pad.lef".format(foundry_dir),
        "{}/lef/sky130_ef_io__vssio_lvc_pad.lef".format(foundry_dir),
        "{}/lef/sky130_fd_io__top_xres4v2.lef".format(foundry_dir),
        "{}/lef/sky130io_fill.lef".format(foundry_dir),
        "{}/lef/sky130_sram_1rw1r_128x256_8.lef".format(foundry_dir),
        "{}/lef/sky130_sram_1rw1r_44x64_8.lef".format(foundry_dir),
        "{}/lef/sky130_sram_1rw1r_64x256_8.lef".format(foundry_dir),
        "{}/lef/sky130_sram_1rw1r_80x64_8.lef".format(foundry_dir),
    ]
    workspace.set_lefs(lefs)

    # 设置libs
    libs = [
        "{}/lib/sky130_fd_sc_hd__tt_025C_1v80.lib".format(foundry_dir),
        "{}/lib/sky130_dummy_io.lib".format(foundry_dir),
        "{}/lib/sky130_sram_1rw1r_128x256_8_TT_1p8V_25C.lib".format(foundry_dir),
        "{}/lib/sky130_sram_1rw1r_44x64_8_TT_1p8V_25C.lib".format(foundry_dir),
        "{}/lib/sky130_sram_1rw1r_64x256_8_TT_1p8V_25C.lib".format(foundry_dir),
        "{}/lib/sky130_sram_1rw1r_80x64_8_TT_1p8V_25C.lib".format(foundry_dir),
    ]
    workspace.set_libs(libs)

    # 设置sdc, spef路径 (根据实际设计调整)
    design_dir = os.path.join(dataset_dir, design_name)

    # 自动查找SDC文件
    import glob
    sdc_files = glob.glob(os.path.join(design_dir, "syn_netlist", "*.sdc"))
    if sdc_files:
        workspace.set_sdc(sdc_files[0])
    else:
        raise FileNotFoundError(f"No SDC file found in {design_dir}/syn_netlist/")

    workspace.set_spef(os.path.join(design_dir, "route", "rpt", f"{design_name}.spef"))

    # 设置workspace信息
    workspace.set_process_node("sky130")
    workspace.set_project(design_name)
    workspace.set_design(design_name)
    workspace.set_version("V1")
    workspace.set_task("route_feature_extraction")

    workspace.set_first_routing_layer("li1")

    # config iEDA
    workspace.set_ieda_fixfanout_buffer("sky130_fd_sc_hs__buf_8")
    workspace.set_ieda_cts_buffers(["sky130_fd_sc_hs__buf_1"])
    workspace.set_ieda_cts_root_buffer("sky130_fd_sc_hs__buf_1")
    workspace.set_ieda_placement_buffers(["sky130_fd_sc_hs__buf_1"])
    workspace.set_ieda_filler_cells_for_first_iteration([
        "sky130_fd_sc_hs__fill_8", "sky130_fd_sc_hs__fill_4",
        "sky130_fd_sc_hs__fill_2", "sky130_fd_sc_hs__fill_1",
    ])
    workspace.set_ieda_filler_cells_for_second_iteration([
        "sky130_fd_sc_hs__fill_8", "sky130_fd_sc_hs__fill_4",
        "sky130_fd_sc_hs__fill_2", "sky130_fd_sc_hs__fill_1",
    ])
    workspace.set_ieda_optdrv_buffers(["sky130_fd_sc_hs__buf_8"])
    workspace.set_ieda_opthold_buffers(["sky130_fd_sc_hs__buf_8"])
    workspace.set_ieda_optsetup_buffers(["sky130_fd_sc_hs__buf_8"])
    workspace.set_ieda_router_layer(bottom_layer="met1", top_layer="met4")

    return workspace


def generate_vectors(workspace: Workspace, patch_row_step: int, patch_col_step: int,
                    input_def, batch_mode: bool = True, is_placement_mode: bool = False,
                    sta_mode: int = 0):
    """生成特征向量"""
    data_gen = DataGeneration(workspace)

    if is_placement_mode:
        vectors_dir = workspace.paths_table.ieda_output["pl_vectors"]
    else:
        vectors_dir = workspace.paths_table.ieda_output["rt_vectors"]

    data_gen.generate_vectors(
        input_def=input_def,
        vectors_dir=vectors_dir,
        patch_row_step=patch_row_step,
        patch_col_step=patch_col_step,
        batch_mode=batch_mode,
        is_placement_mode=is_placement_mode,
        sta_mode=sta_mode,
    )


def batch_extract_features(dataset_dir, output_base_dir, designs=None):
    """批量提取布线特征"""
    if designs is None:
        designs = COMPLETE_DESIGNS

    current_dir = os.path.split(os.path.abspath(__file__))[0]

    for design_name in designs:
        print(f"\n{'='*60}")
        print(f"Processing design: {design_name}")
        print(f"{'='*60}")

        try:
            # 检查文件是否存在
            design_dir = os.path.join(dataset_dir, design_name)
            def_file = os.path.join(design_dir, "route", f"{design_name}.def")
            spef_file = os.path.join(design_dir, "route", "rpt", f"{design_name}.spef")

            # 检查SDC文件(任意名称)
            import glob
            sdc_files = glob.glob(os.path.join(design_dir, "syn_netlist", "*.sdc"))

            if not os.path.exists(def_file):
                print(f"WARNING: Missing DEF file for {design_name}, skipping...")
                continue
            if not os.path.exists(spef_file):
                print(f"WARNING: Missing SPEF file for {design_name}, skipping...")
                continue
            if not sdc_files:
                print(f"WARNING: Missing SDC file for {design_name}, skipping...")
                continue

            print(f"Found files: DEF, SPEF, SDC({os.path.basename(sdc_files[0])})")

            # 创建workspace
            workspace_dir = os.path.join(output_base_dir, f"workspace_{design_name}")
            workspace = create_workspace_sky130_design(workspace_dir, design_name, dataset_dir)

            # 生成特征向量
            # sta_mode = 1: 使用spef进行STA
            generate_vectors(
                workspace=workspace,
                patch_row_step=18,
                patch_col_step=18,
                input_def=def_file,
                batch_mode=False,
                is_placement_mode=False,
                sta_mode=1
            )

            print(f"✓ Successfully processed {design_name}")

        except Exception as e:
            print(f"✗ Error processing {design_name}: {str(e)}")
            continue


if __name__ == "__main__":
    dataset_dir = "/data2/home/zyx/project_share/dataset_skywater130"
    current_dir = os.path.split(os.path.abspath(__file__))[0]
    root = current_dir.rsplit("/", 1)[0]
    output_base_dir = f"{root}/example/batch_route_features"

    print(f"Dataset directory: {dataset_dir}")
    print(f"Output directory: {output_base_dir}")
    print(f"Designs to process: {len(COMPLETE_DESIGNS)} (including apb4 series)")
    print(f"Design list: {', '.join(COMPLETE_DESIGNS)}")

    # 创建输出目录
    os.makedirs(output_base_dir, exist_ok=True)

    # 开始批量处理
    batch_extract_features(dataset_dir, output_base_dir)

    print(f"\n{'='*60}")
    print("Batch processing completed!")
    print(f"{'='*60}")