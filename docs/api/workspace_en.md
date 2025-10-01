# iEDA Workspace Path and Configuration Management Functions Summary

This document summarizes the classes and functions related to path and configuration management in the iEDA Workspace module.

## 1. Main Workspace Class

| Function Category | Method Name | Description | Parameters |
|-----------------|------------|------------|-----------|
| Workspace Creation | `create_workspace` | Check and create workspace directory structure, initialize configuration files | `flow_list` (optional): List of flows |
| Path Setting | `set_tech_lef` | Set technology LEF file path and update configuration | `tech_lef`: Technology LEF file path |
| Path Setting | `set_lefs` | Set LEF file list and update configuration | `lefs`: List of LEF file paths |
| Path Setting | `set_libs` | Set library file list and update configuration | `libs`: List of library file paths |
| Path Setting | `set_max_libs` | Set maximum library file list | `libs`: List of maximum library file paths |
| Path Setting | `set_min_libs` | Set minimum library file list | `libs`: List of minimum library file paths |
| Path Setting | `set_sdc` | Set SDC file path and update configuration | `sdc_path`: SDC file path |
| Path Setting | `set_spef` | Set SPEF file path and update configuration | `spef_path`: SPEF file path |
| Path Setting | `set_rcworst` | Set RC worst file path | `rcworst_path`: RC worst file path |
| Path Setting | `set_rcbest` | Set RC best file path | `rcbest_path`: RC best file path |
| Path Setting | `set_def_input` | Set DEF input file path and update configuration | `def_input`: DEF file path |
| Path Setting | `set_verilog_input` | Set Verilog input file path and update configuration | `verilog_input`: Verilog file path |
| Workspace Configuration | `set_flows` | Set flow configuration and update flow.json | `flows`: Flow configuration |
| Workspace Configuration | `set_process_node` | Set process node | `process_node`: Process node name |
| Workspace Configuration | `set_design` | Set design name | `design`: Design name |
| Workspace Configuration | `set_version` | Set version information | `version`: Version string |
| Workspace Configuration | `set_project` | Set project name | `project`: Project name |
| Workspace Configuration | `set_task` | Set task name | `task`: Task name |
| iEDA Tool Configuration | `set_first_routing_layer` | Set first routing layer | `layer`: Routing layer name |
| iEDA Tool Configuration | `set_ieda_fixfanout_buffer` | Set buffer for Fanout fixing | `buffer`: Buffer cell name |
| iEDA Tool Configuration | `set_ieda_cts_buffers` | Set buffer list for CTS | `buffers`: List of buffer cell names |
| iEDA Tool Configuration | `set_ieda_cts_root_buffer` | Set root buffer for CTS | `buffer`: Buffer cell name |
| iEDA Tool Configuration | `set_ieda_placement_buffers` | Set buffer list for placement | `buffers`: List of buffer cell names |
| iEDA Tool Configuration | `set_ieda_filler_cells_for_first_iteration` | Set filler cells for first iteration | `cells`: List of filler cell names |
| iEDA Tool Configuration | `set_ieda_filler_cells_for_second_iteration` | Set filler cells for second iteration | `cells`: List of filler cell names |
| iEDA Tool Configuration | `set_ieda_optdrv_buffers` | Set buffers for driver optimization | `buffers`: List of buffer cell names |
| iEDA Tool Configuration | `set_ieda_opthold_buffers` | Set buffers for hold time optimization | `buffers`: List of buffer cell names |
| iEDA Tool Configuration | `set_ieda_optsetup_buffers` | Set buffers for setup time optimization | `buffers`: List of buffer cell names |
| iEDA Tool Configuration | `set_ieda_router_layer` | Set routing layer range | `bottom_layer`: Bottom layer name, `top_layer`: Top layer name |
| iEDA Tool Configuration | `set_ieda_router_timing` | Set whether to enable timing optimization during routing | `enable_timing`: Boolean value |
| Parameter Management | `update_parameters` | Update parameter configuration and save to JSON | `parameters`: EDAParameters object |
| Parameter Management | `load_parameters` | Load parameter configuration from JSON file | `parameters_json`: Parameter JSON file path |
| Parameter Management | `print_paramters` | Print parameter configuration information | None |

## 2. PathsTable Class (Path Management)

| Path Category | Property/Method Name | Path Format | Description |
|--------------|---------------------|------------|------------|
| Workspace Top Level | `workspace_top` | List containing the following directories:<br>- `{directory}/analyse`<br>- `{directory}/config`<br>- `{directory}/feature`<br>- `{directory}/output`<br>- `{directory}/script`<br>- `{directory}/report` | Main workspace directory structure |
| Analysis Directory | `analysis_dir` | `{directory}/analyse` | Analysis results directory |
| Output Directory | `output_dir` | `{directory}/output` | Output files directory |
| Configuration Files | `flow` | `{directory}/config/flow.json` | Flow configuration file path |
| Configuration Files | `path` | `{directory}/config/path.json` | PDK and design path configuration file |
| Configuration Files | `workspace` | `{directory}/config/workspace.json` | Workspace settings file |
| Configuration Files | `parameters` | `{directory}/config/parameter.json` | Parameter settings file |
| Logs | `log_dir` | `{directory}/output/log` | Log files directory |
| Logs | `log` | `{log_dir}/{design}.log` | Log file path |
| Reports | `report_dir` | `{directory}/report` | Report files directory |
| Reports | `report` | Dictionary containing summary_md and summary_html | Workspace report file paths |
| iEDA Output | `ieda_output_dirs` | List containing various iEDA output directories | iEDA tool output directory structure |
| iEDA Configuration | `ieda_config` | Dictionary containing various iEDA configuration file paths | Configuration file paths for each iEDA tool stage |
| iEDA Output | `ieda_output` | Dictionary containing various iEDA output paths | Output file paths for each iEDA tool stage |
| iEDA Reports | `ieda_report` | Dictionary containing DRC report path | Report file paths generated by iEDA |
| iEDA Features | `ieda_feature_json` | Dictionary containing various feature JSON paths | Feature data file paths for each stage |
| iEDA Vectors | `ieda_vectors` | Dictionary containing various vector data paths | Vector data file and directory paths |
| iEDA GUI | `ieda_gui` | Dictionary containing GUI-related paths | GUI-related file paths |
| Scripts | `scripts` | Dictionary containing various script paths | Tcl script file paths |
| Analysis Images | `analysis_images` | Dictionary containing various analysis image paths | Analysis visualization image file paths |
| Helper Methods | `get_image_path` | Dynamically generate image paths | Get specific image file path based on type |

## 3. Configs Class (Configuration Management)

| Function Category | Method Name | Description | Parameters |
|-----------------|------------|------------|-----------|
| Initialization | `__init__` | Initialize configuration manager, load various configurations | `paths_table`: Path table, `logger`: Logger |
| Update | `update` | Update all configurations | None |
| Internal Initialization | `_init_flow_json` | Initialize flow configuration | None |
| Internal Initialization | `_init_path_json` | Initialize path configuration | None |
| Internal Initialization | `_init_workspace_json` | Initialize workspace configuration | None |
| Internal Initialization | `_init_parameters` | Initialize parameter configuration | None |
| Flow Management | `reset_flow_states` | Reset flow states | None |
| Flow Management | `save_flow_state` | Save flow state | `db_flow`: Flow database object |
| Output Files | `get_output_def` | Get output DEF file path | `flow`: Flow object, `compressed`: Whether to compress |
| Output Files | `get_output_verilog` | Get output Verilog file path | `flow`: Flow object, `compressed`: Whether to compress |

## 4. Workspace Initialization Process

The `create_workspace` method of the Workspace class initializes the workspace according to the following steps:

1. Ensure the workspace directory exists, create it if it doesn't
2. Create workspace top-level directories (analyse, config, feature, output, script, report)
3. Create iEDA output directory structure
4. Create log file and initialize logger and configs
5. Create flow.json configuration file
6. Create path.json configuration file
7. Create workspace.json configuration file
8. Create parameter.json configuration file
9. Create iEDA_config directory and various configuration files within it
10. Update configurations

## 5. iEDA Configuration File Structure

The configuration files created under the iEDA_config directory include:

- `flow_config.json`: iEDA flow configuration
- `db_default_config.json`: Database initialization configuration
- `fp_default_config.json`: Floorplan configuration
- `pnp_default_config.json`: Pin placement configuration
- `no_default_config_fixfanout.json`: Fanout fixing configuration
- `pl_default_config.json`: Placement configuration
- `cts_default_config.json`: Clock tree synthesis configuration
- `to_default_config_drv.json`: Driver optimization configuration
- `to_default_config_hold.json`: Hold time optimization configuration
- `to_default_config_setup.json`: Setup time optimization configuration
- `rt_default_config.json`: Routing configuration
- `drc_default_config.json`: DRC check configuration

These configuration files correspond to different design stages of the iEDA tool.