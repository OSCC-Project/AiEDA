#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Batch placement feature extraction script
Automatically processes designs with placement results in dataset directory
"""

import os
import sys
import glob
import shutil
import tempfile
import argparse
from pathlib import Path

# Set environment and paths
os.environ["iEDA"] = "ON"
sys.path.append(os.getcwd())

from aieda.workspace import Workspace, workspace_create
from aieda.flows import DbFlow, RunIEDA, DataGeneration
from aieda.data.database import EDAParameters


def find_designs_with_place(dataset_dir):
    """Find all designs with place directory and required files."""
    if not os.path.exists(dataset_dir):
        print(f"Error: Dataset directory '{dataset_dir}' does not exist")
        return []

    designs = []
    try:
        for design_dir in Path(dataset_dir).iterdir():
            if design_dir.is_dir():
                place_dir = design_dir / "place"
                if place_dir.exists():
                    # Check for def and sdc files in place directory
                    def_files = list(place_dir.glob("*.def")) + list(place_dir.glob("*.def.gz"))
                    sdc_files = list(place_dir.glob("*.sdc"))
                    if def_files and sdc_files:
                        designs.append(design_dir.name)
    except PermissionError:
        print(f"Error: Permission denied accessing '{dataset_dir}'")
        return []

    return sorted(designs)


def get_design_files(dataset_dir, design_name, design_type):
    """Get paths to def and sdc files for a design."""
    design_dir = Path(dataset_dir) / design_name

    # Find def file
    place_dir = design_dir / "place"
    def_files = list(place_dir.glob("*.def")) + list(place_dir.glob("*.def.gz"))
    if not def_files:
        return None, None
    
    def_file = None
    for one_def_file in def_files:
        if design_type in one_def_file.name:
            def_file = one_def_file
            break
        
    if def_file is None:
        raise ValueError(f"DEF file for design '{design_name}' with design type '{design_type}' not found")

    # Find sdc file - look in place directory
    sdc_files = list(place_dir.glob("*.sdc"))
    if not sdc_files:
        return None, None
    sdc_file = sdc_files[0]

    return str(def_file), str(sdc_file)


def process_sdc_file(sdc_path):
    """Process sdc file by temporarily removing set_propagated_clock [all_clocks]."""
    try:
        with open(sdc_path, 'r') as f:
            content = f.read()
    except (IOError, PermissionError) as e:
        print(f"  Error reading SDC file {sdc_path}: {e}")
        return sdc_path, None, None

    # Check if it contains set_propagated_clock
    original_content = content
    modified = False

    lines = content.split('\n')
    filtered_lines = []
    for line in lines:
        if 'set_propagated_clock' in line and '[all_clocks]' in line:
            print(f"  Temporarily removing: {line.strip()}")
            modified = True
        else:
            filtered_lines.append(line)

    if modified:
        # Create temporary file
        try:
            temp_fd, temp_path = tempfile.mkstemp(suffix='.sdc')
            with os.fdopen(temp_fd, 'w') as f:
                f.write('\n'.join(filtered_lines))
            return temp_path, original_content, sdc_path
        except (IOError, PermissionError) as e:
            print(f"  Error creating temporary SDC file: {e}")
            return sdc_path, None, None
    else:
        return sdc_path, None, None


def restore_sdc_file(original_content, original_path):
    """Restore original content of sdc file."""
    if original_content is not None:
        try:
            with open(original_path, 'w') as f:
                f.write(original_content)
        except (IOError, PermissionError) as e:
            print(f"  Error restoring SDC file {original_path}: {e}")


def create_workspace_for_design(workspace_dir, design_name, def_file, sdc_file, aieda_root=None):
    """Create workspace for specific design."""
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

    # Set basic paths
    if aieda_root is None:
        current_dir = os.path.split(os.path.abspath(__file__))[0]
        root = current_dir.rsplit("/", 1)[0]
    else:
        root = aieda_root

    foundry_dir = f"{root}/aieda/third_party/iEDA/scripts/foundry/sky130"

    # Set verilog input - use standard gcd.v
    sky130_gcd_verilog = f"{root}/aieda/third_party/iEDA/scripts/design/sky130_gcd/result/verilog/gcd.v"

    if not os.path.exists(sky130_gcd_verilog):
        print(f"Warning: Verilog file not found at {sky130_gcd_verilog}")

    workspace.set_verilog_input(sky130_gcd_verilog)

    # Set tech lef
    tech_lef_path = f"{foundry_dir}/lef/sky130_fd_sc_hd.tlef"
    if not os.path.exists(tech_lef_path):
        print(f"Warning: Tech LEF file not found at {tech_lef_path}")
    workspace.set_tech_lef(tech_lef_path)

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


def generate_vectors_for_design(workspace, def_file, patch_row_step=18, patch_col_step=18):
    """Generate feature vectors for design."""
    data_gen = DataGeneration(workspace)
    vectors_dir = workspace.paths_table.ieda_output["pl_vectors"]

    data_gen.generate_vectors(
        input_def=def_file,
        vectors_dir=vectors_dir,
        patch_row_step=patch_row_step,
        patch_col_step=patch_col_step,
        batch_mode=False,
        is_placement_mode=True,
        sta_mode=1
    )


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Batch placement feature extraction script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python batch_extract_place_features.py /path/to/dataset_skywater130 --design-type _a_place_congestion_best
  python batch_extract_place_features.py --dataset-dir /path/to/dataset --output-dir /path/to/output --design-type _a_place_congestion_best
  python batch_extract_place_features.py --dataset-dir /path/to/dataset --patch-step 24 --design-type _a_place_congestion_best
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
        help='Output directory for extracted features (default: ./example/batch_place_features)'
    )
    
    parser.add_argument(
        '--design-type',
        help='Design type of place def'
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
        output_base_dir = f"{root}/example/batch_place_features"
        
    if args.design_type:
        design_type = args.design_type
    else:
        design_type = None
        raise ValueError("Please specify design type")

    # Ensure output directory exists
    try:
        os.makedirs(output_base_dir, exist_ok=True)
    except PermissionError:
        print(f"Error: Permission denied creating output directory '{output_base_dir}'")
        sys.exit(1)

    print("=== Batch Placement Feature Extraction ===")
    print(f"Dataset directory: {dataset_dir}")
    print(f"Output directory: {output_base_dir}")
    print(f"Patch step size: {args.patch_row_step}x{args.patch_col_step}")

    # Find all designs with place directories
    designs = find_designs_with_place(dataset_dir)
    print(f"\nFound {len(designs)} designs with place directories:")
    for design in designs:
        print(f"  - {design}")

    if not designs:
        print("No designs with place directories found")
        return

    # Process each design
    success_count = 0
    for i, design_name in enumerate(designs, 1):
        print(f"\n[{i}/{len(designs)}] Processing design: {design_name}")

        try:
            # Get design files
            # design_type  = '_b_place_HPWL_best'
            def_file, sdc_file = get_design_files(dataset_dir, design_name, design_type)
            if not def_file or not sdc_file:
                print(f"  Skipping: Missing required files")
                continue

            print(f"  DEF file: {def_file}")
            print(f"  SDC file: {sdc_file}")

            # Process sdc file
            processed_sdc, original_content, original_path = process_sdc_file(sdc_file)

            # Create workspace
            workspace_dir = f"{output_base_dir}/{design_name}"
            workspace = create_workspace_for_design(
                workspace_dir, design_name, def_file, processed_sdc, args.aieda_root
            )

            # Generate feature vectors
            print(f"  Starting feature vector generation...")
            generate_vectors_for_design(
                workspace, def_file, args.patch_row_step, args.patch_col_step
            )

            # Restore sdc file
            if original_content:
                restore_sdc_file(original_content, original_path)
                os.unlink(processed_sdc)  # Delete temporary file

            print(f"  Completed: {design_name}")
            success_count += 1

        except Exception as e:
            print(f"  Error: {design_name} - {str(e)}")
            continue

    print(f"\n=== Batch Processing Complete ===")
    print(f"Successfully processed: {success_count}/{len(designs)} designs")
    print(f"Results saved to: {output_base_dir}")

    if success_count > 0:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()