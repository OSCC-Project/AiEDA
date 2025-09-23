#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Batch extract routing features from multiple designs in dataset directory
"""

import os
import sys
import glob
import argparse
from pathlib import Path

os.environ["iEDA"] = "ON"
sys.path.append(os.getcwd())

from aieda.workspace import Workspace, workspace_create
from aieda.flows import DbFlow, DataGeneration

def find_designs_with_route(dataset_dir):
    """Find all designs with complete route files."""
    if not os.path.exists(dataset_dir):
        print(f"Error: Dataset directory '{dataset_dir}' does not exist")
        return []

    designs = []
    try:
        for design_dir in Path(dataset_dir).iterdir():
            if design_dir.is_dir():
                route_dir = design_dir / "route"
                if route_dir.exists():
                    design_name = design_dir.name
                    # Check for def and sdc files in route directory
                    def_files = list(route_dir.glob(f"{design_name}.def")) + list(route_dir.glob("*.def"))
                    sdc_files = list(route_dir.glob(f"{design_name}.sdc")) + list(route_dir.glob("*.sdc"))

                    # Check for spef files in rpt directory
                    rpt_dir = route_dir / "rpt"
                    spef_files = []
                    if rpt_dir.exists():
                        spef_files = list(rpt_dir.glob(f"{design_name}.spef")) + list(rpt_dir.glob("*.spef"))

                    if def_files and sdc_files and spef_files:
                        designs.append(design_name)
    except PermissionError:
        print(f"Error: Permission denied accessing '{dataset_dir}'")
        return []

    return sorted(designs)

def create_workspace_sky130_design(workspace_dir, design_name, dataset_dir, aieda_root=None):
    """Create workspace for specified design."""
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

    # Set basic paths
    if aieda_root is None:
        current_dir = os.path.split(os.path.abspath(__file__))[0]
        root = current_dir.rsplit("/", 1)[0]
    else:
        root = aieda_root

    foundry_dir = "{}/aieda/third_party/iEDA/scripts/foundry/sky130".format(root)

    # Set verilog input (from reference file path)
    sky130_verilog = "{}/aieda/third_party/iEDA/scripts/design/sky130_gcd/result/verilog/gcd.v".format(root)

    if not os.path.exists(sky130_verilog):
        print(f"Warning: Verilog file not found at {sky130_verilog}")

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

    # 自动查找SDC文件 - 从route目录
    sdc_files = glob.glob(os.path.join(design_dir, "route", "*.sdc"))
    if sdc_files:
        workspace.set_sdc(sdc_files[0])
    else:
        raise FileNotFoundError(f"No SDC file found in {design_dir}/route/")

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
    """Generate feature vectors."""
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


def batch_extract_features(dataset_dir, output_base_dir, designs=None, aieda_root=None,
                          patch_row_step=18, patch_col_step=18):
    """Batch extract routing features."""
    if designs is None:
        designs = find_designs_with_route(dataset_dir)

    success_count = 0

    for design_name in designs:
        print(f"\n{'='*60}")
        print(f"Processing design: {design_name}")
        print(f"{'='*60}")

        try:
            # Check if files exist
            design_dir = os.path.join(dataset_dir, design_name)
            def_file = os.path.join(design_dir, "route", f"{design_name}.def")
            spef_file = os.path.join(design_dir, "route", "rpt", f"{design_name}.spef")

            # Check SDC files (from route directory)
            sdc_files = glob.glob(os.path.join(design_dir, "route", "*.sdc"))

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

            # Create workspace
            workspace_dir = os.path.join(output_base_dir, f"workspace_{design_name}")
            workspace = create_workspace_sky130_design(workspace_dir, design_name, dataset_dir, aieda_root)

            # Generate feature vectors
            # sta_mode = 1: use spef for STA
            generate_vectors(
                workspace=workspace,
                patch_row_step=patch_row_step,
                patch_col_step=patch_col_step,
                input_def=def_file,
                batch_mode=False,
                is_placement_mode=False,
                sta_mode=1
            )

            print(f"✓ Successfully processed {design_name}")
            success_count += 1

        except Exception as e:
            print(f"✗ Error processing {design_name}: {str(e)}")
            continue

    return success_count


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Batch routing feature extraction script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python batch_extract_route_features.py /path/to/dataset_skywater130
  python batch_extract_route_features.py --dataset-dir /path/to/dataset --output-dir /path/to/output
  python batch_extract_route_features.py --dataset-dir /path/to/dataset --patch-step 24
        """
    )

    parser.add_argument(
        'dataset_dir',
        nargs='?',
        help='Path to the dataset directory containing design subdirectories'
    )

    parser.add_argument(
        '--dataset-dir',
        dest='dataset_dir_alt',
        help='Alternative way to specify dataset directory path'
    )

    parser.add_argument(
        '--output-dir',
        help='Output directory for extracted features (default: ./example/batch_route_features)'
    )

    parser.add_argument(
        '--aieda-root',
        help='Path to aiEDA root directory (default: auto-detect)'
    )

    parser.add_argument(
        '--patch-row-step',
        type=int,
        default=18,
        help='Patch row step size for feature extraction (default: 18)'
    )

    parser.add_argument(
        '--patch-col-step',
        type=int,
        default=18,
        help='Patch column step size for feature extraction (default: 18)'
    )

    args = parser.parse_args()

    # Determine dataset directory
    dataset_dir = args.dataset_dir or args.dataset_dir_alt

    if not dataset_dir:
        parser.print_help()
        print("\nError: Dataset directory must be specified")
        sys.exit(1)

    dataset_dir = os.path.abspath(dataset_dir)

    # Set output directory
    if args.output_dir:
        output_base_dir = os.path.abspath(args.output_dir)
    else:
        current_dir = os.path.split(os.path.abspath(__file__))[0]
        root = current_dir.rsplit("/", 1)[0]
        output_base_dir = f"{root}/example/batch_route_features"

    # Dynamically discover designs with route files
    designs = find_designs_with_route(dataset_dir)

    print(f"Dataset directory: {dataset_dir}")
    print(f"Output directory: {output_base_dir}")
    print(f"Patch step size: {args.patch_row_step}x{args.patch_col_step}")
    print(f"Found {len(designs)} designs with route files:")
    for design in designs:
        print(f"  - {design}")

    if not designs:
        print("No designs with route files found")
        sys.exit(1)

    # Create output directory
    try:
        os.makedirs(output_base_dir, exist_ok=True)
    except PermissionError:
        print(f"Error: Permission denied creating output directory '{output_base_dir}'")
        sys.exit(1)

    # Start batch processing
    success_count = batch_extract_features(
        dataset_dir, output_base_dir, designs, args.aieda_root,
        args.patch_row_step, args.patch_col_step
    )

    print(f"\n{'='*60}")
    print("Batch processing completed!")
    print(f"Successfully processed: {success_count}/{len(designs)} designs")
    print(f"{'='*60}")

    if success_count > 0:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()