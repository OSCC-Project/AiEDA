#!/usr/bin/env python3

import os
import glob
import argparse
import sys

def find_design_directories(base_dir):
    """Find all design directories with required subdirectories."""
    if not os.path.exists(base_dir):
        print(f"Error: Dataset directory '{base_dir}' does not exist")
        return []

    if not os.path.isdir(base_dir):
        print(f"Error: '{base_dir}' is not a directory")
        return []

    design_dirs = []
    try:
        for item in os.listdir(base_dir):
            item_path = os.path.join(base_dir, item)
            if os.path.isdir(item_path):
                route_dir = os.path.join(item_path, "route")
                place_dir = os.path.join(item_path, "place")
                syn_netlist_dir = os.path.join(item_path, "syn_netlist")

                if os.path.exists(route_dir) and os.path.exists(place_dir) and os.path.exists(syn_netlist_dir):
                    design_dirs.append(item_path)
    except PermissionError:
        print(f"Error: Permission denied accessing '{base_dir}'")
        return []

    return design_dirs

def process_sdc_files(base_dir):
    """Process SDC files to create place and route versions."""
    design_dirs = find_design_directories(base_dir)

    if not design_dirs:
        print("No valid design directories found")
        return False

    print(f"Found {len(design_dirs)} design directories")

    success_count = 0
    for design_dir in design_dirs:
        design_name = os.path.basename(design_dir)
        syn_netlist_dir = os.path.join(design_dir, "syn_netlist")
        route_dir = os.path.join(design_dir, "route")
        place_dir = os.path.join(design_dir, "place")

        try:
            sdc_files = glob.glob(os.path.join(syn_netlist_dir, "*.sdc"))

            if not sdc_files:
                print(f"Warning: No SDC file found in {syn_netlist_dir}")
                continue

            for sdc_file in sdc_files:
                print(f"Processing {sdc_file}")

                try:
                    with open(sdc_file, 'r') as f:
                        content = f.read()
                except (IOError, PermissionError) as e:
                    print(f"  Error reading {sdc_file}: {e}")
                    continue

                # Generate place version (remove set_propagated_clock statements)
                lines = content.split('\n')
                place_lines = [line for line in lines if "set_propagated_clock [all_clocks]" not in line]
                place_content = '\n'.join(place_lines)

                # Generate route version (ensure set_propagated_clock statement is present)
                route_content = place_content.rstrip()
                if route_content and not route_content.endswith('\n'):
                    route_content += '\n'
                route_content += "set_propagated_clock [all_clocks]\n"

                # Save to place directory
                place_output = os.path.join(place_dir, os.path.basename(sdc_file))
                try:
                    with open(place_output, 'w') as f:
                        f.write(place_content)
                    print(f"  Saved place version to {place_output}")
                except (IOError, PermissionError) as e:
                    print(f"  Error writing {place_output}: {e}")
                    continue

                # Save to route directory
                route_output = os.path.join(route_dir, os.path.basename(sdc_file))
                try:
                    with open(route_output, 'w') as f:
                        f.write(route_content)
                    print(f"  Saved route version to {route_output}")
                except (IOError, PermissionError) as e:
                    print(f"  Error writing {route_output}: {e}")
                    continue

            success_count += 1

        except Exception as e:
            print(f"Error processing design {design_name}: {e}")
            continue

    print(f"Successfully processed {success_count}/{len(design_dirs)} designs")
    return success_count > 0

def main():
    parser = argparse.ArgumentParser(
        description="Process SDC files to create place and route versions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python process_sdc_files.py /path/to/dataset_skywater130
  python process_sdc_files.py --dataset-dir /path/to/dataset_skywater130
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

    args = parser.parse_args()

    # Determine dataset directory
    dataset_dir = args.dataset_dir or args.dataset_dir_alt

    if not dataset_dir:
        parser.print_help()
        print("\nError: Dataset directory must be specified")
        sys.exit(1)

    dataset_dir = os.path.abspath(dataset_dir)

    print(f"Processing SDC files in: {dataset_dir}")

    if process_sdc_files(dataset_dir):
        print("SDC file processing completed successfully!")
        sys.exit(0)
    else:
        print("SDC file processing failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()