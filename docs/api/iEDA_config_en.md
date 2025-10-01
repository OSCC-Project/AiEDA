# iEDA Tool Configuration Parameters Summary

This table summarizes the configuration parameters of commonly used tools in iEDA for user reference and usage.

## 1. Floorplan Tool Configuration

| Parameter Name | Data Type | Default Value | Description |
|---------------|----------|--------------|-------------|
| die_area | string | None | Die area size, format as "x1,y1,x2,y2" |
| core_area | string | None | Core area size, format as "x1,y1,x2,y2" |
| core_util | float | 0.7 | Core area utilization |
| core_site | string | None | Core area cell type |
| io_site | string | None | IO area cell type |
| corner_site | string | None | Corner cell type |
| x_margin | int | 0 | X-direction margin |
| y_margin | int | 0 | Y-direction margin |
| xy_ratio | float | 1.0 | Aspect ratio |
| cell_area | int | 0 | Cell area |

## 2. Placement Tool Configuration

| Parameter Name | Data Type | Default Value | Description |
|---------------|----------|--------------|-------------|
| global_place_enable | bool | true | Whether to enable global placement |
| detail_place_enable | bool | true | Whether to enable detailed placement |
| macro_place_enable | bool | true | Whether to enable macro placement |
| incremental_place_enable | bool | false | Whether to enable incremental placement |
| ai_place_enable | bool | false | Whether to enable AI placement |
| onnx_model_path | string | "" | ONNX model path (used in AI placement) |
| normalization_path | string | "" | Normalization file path (used in AI placement) |
| gp_iterations | int | 100 | Number of global placement iterations |
| lg_iterations | int | 50 | Number of detailed placement iterations |
| dp_iterations | int | 20 | Number of final optimization iterations |
| target_density | float | 0.7 | Target placement density |

## 3. Clock Tree Synthesis (CTS) Tool Configuration

| Parameter Name | Data Type | Default Value | Description |
|---------------|----------|--------------|-------------|
| cts_work_dir | string | None | Clock tree synthesis working directory |
| target_skew | float | 50.0 | Target clock skew (ps) |
| max_capacitance | float | 500.0 | Maximum capacitance (ff) |
| max_fanout | int | 32 | Maximum fanout |
| max_transition | float | 50.0 | Maximum transition time (ps) |
| buffer_cell | string | "" | Buffer cell type |
| inverter_cell | string | "" | Inverter cell type |
| clock_nets | array | [] | List of nets requiring clock tree synthesis |

## 4. Routing Tool Configuration

| Parameter Name | Data Type | Default Value | Description |
|---------------|----------|--------------|-------------|
| global_route_enable | bool | true | Whether to enable global routing |
| detail_route_enable | bool | true | Whether to enable detailed routing |
| timing_driven | bool | true | Whether to enable timing-driven routing |
| congestion_iterations | int | 5 | Number of congestion optimization iterations |
| layer_adjust_iterations | int | 3 | Number of layer adjustment iterations |
| min_route_layer | int | 1 | Minimum routing layer |
| max_route_layer | int | -1 | Maximum routing layer (-1 means using all layers) |
| via_cost | float | 10.0 | Via cost coefficient |
| wire_spacing | int | 1 | Wire spacing rule |

## 5. Static Timing Analysis (STA) Tool Configuration

| Parameter Name | Data Type | Default Value | Description |
|---------------|----------|--------------|-------------|
| design_workspace | string | None | Design workspace directory |
| lef_files | array | [] | List of LEF file paths |
| def_file | string | "" | DEF file path |
| liberty_files | array | [] | List of Liberty library file paths |
| netlist_file | string | "" | Netlist file path |
| sdc_file | string | "" | SDC constraint file path |
| spef_files | array | [] | List of SPEF file paths |
| analysis_mode | string | "setup" | Analysis mode (setup/hold) |
| derate | float | 1.0 | Timing analysis coefficient |
| digits | int | 3 | Number of decimal places in reports |

## 6. Design Rule Check (DRC) Tool Configuration

| Parameter Name | Data Type | Default Value | Description |
|---------------|----------|--------------|-------------|
| temp_directory_path | string | "" | Temporary directory path |
| thread_number | int | 128 | Number of threads |
| golden_directory_path | string | "" | Golden data directory path |
| report_path | string | "drc_report.txt" | DRC report path |
| rule_decks | array | [] | List of rule files |
| check_layers | array | [] | List of layers to check |
| severity_level | string | "ERROR" | Report severity level (ERROR/WARNING/INFO) |

## 7. Power Analysis Tool Configuration

| Parameter Name | Data Type | Default Value | Description |
|---------------|----------|--------------|-------------|
| vcd_file | string | "" | VCD file path |
| top_module | string | "" | Top module name |
| pg_spef_file | string | "" | Power ground SPEF file path |
| power_nets | array | [] | List of power nets |
| voltage | float | 1.8 | Operating voltage (V) |
| temperature | int | 25 | Operating temperature (°C) |
| output_report_path | string | "power_report.txt" | Power report path |

## 8. Power Delivery Network (PDN) Tool Configuration

| Parameter Name | Data Type | Default Value | Description |
|---------------|----------|--------------|-------------|
| power_net | string | "VDD" | Power net name |
| ground_net | string | "VSS" | Ground net name |
| grid_layers | array | [] | List of grid layers |
| stripe_layers | array | [] | List of stripe layers |
| grid_width | int | 10 | Grid width |
| grid_pitch | int | 100 | Grid pitch |
| stripe_width | int | 20 | Stripe width |
| stripe_pitch | int | 200 | Stripe pitch |
| via_width | int | 8 | Via width |
| via_height | int | 8 | Via height |

## 9. Timing Optimization Tool Configuration

| Parameter Name | Data Type | Default Value | Description |
|---------------|----------|--------------|-------------|
| optimization_type | string | "all" | Optimization type (all/setup/hold/drv) |
| buffer_cells | array | [] | List of available buffer cells |
| inverter_cells | array | [] | List of available inverter cells |
| max_buffer_insertion | int | 5 | Maximum number of buffer insertions |
| slack_threshold | float | 0.0 | Timing slack threshold |
| iteration_limit | int | 10 | Optimization iteration limit |
| area_constraint | float | 1.2 | Area constraint coefficient |

## 10. Vector Generation Tool Configuration

| Parameter Name | Data Type | Default Value | Description |
|---------------|----------|--------------|-------------|
| output_dir | string | "" | Output directory |
| patch_row_step | int | 9 | Row direction patch step |
| patch_col_step | int | 9 | Column direction patch step |
| batch_mode | bool | true | Whether to use batch mode |
| include_timing | bool | false | Whether to include timing information |
| include_power | bool | false | Whether to include power information |
| normalization | bool | true | Whether to perform normalization |

## 11. Evaluation Tool Configuration

| Parameter Name | Data Type | Default Value | Description |
|---------------|----------|--------------|-------------|
| bin_cnt_x | int | 256 | Number of grids in X direction |
| bin_cnt_y | int | 256 | Number of grids in Y direction |
| save_path | string | "" | Result save path |
| die_size_ratio | float | 0.1 | Die size ratio |
| plot_path | string | "" | Plot save path |
| hierarchy_level | int | 1 | Hierarchy level |
| forward_direction | bool | true | Whether to traverse hierarchy forwardly |

## 12. Feature Extraction Tool Configuration

| Parameter Name | Data Type | Default Value | Description |
|---------------|----------|--------------|-------------|
| output_path | string | "" | Feature output path |
| json_path | string | "" | JSON configuration file path |
| grid_size | int | 100 | Grid size |
| step_size | int | 10 | Step size |
| include_congestion | bool | true | Whether to include congestion features |
| include_timing | bool | true | Whether to include timing features |
| include_power | bool | false | Whether to include power features |