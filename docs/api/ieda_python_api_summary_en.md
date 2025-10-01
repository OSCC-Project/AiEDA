# iEDA Python API Summary

<style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
        line-height: 1.6;
        color: #333;
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
        background-color: #f5f5f5;
    }
    h1, h2, h3 {
        color: #2c3e50;
        margin-top: 30px;
    }
    h1 {
        text-align: center;
        padding-bottom: 15px;
        border-bottom: 3px solid #3498db;
        margin-bottom: 30px;
    }
    h2 {
        padding-bottom: 10px;
        border-bottom: 2px solid #3498db;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        background-color: white;
    }
    th, td {
        padding: 12px 15px;
        text-align: left;
        border-bottom: 1px solid #ddd;
    }
    th {
        background-color: #3498db;
        color: white;
        font-weight: 600;
    }
    tr:nth-child(even) {
        background-color: #f2f2f2;
    }
    tr:hover {
        background-color: #e3f2fd;
    }
    .container {
        background-color: white;
        padding: 30px;
        border-radius: 8px;
        box-shadow: 0 2px 20px rgba(0,0,0,0.1);
    }
    .module-section {
        margin-bottom: 40px;
    }
    .intro {
        background-color: #e8f4f8;
        padding: 15px;
        border-left: 4px solid #3498db;
        margin-bottom: 25px;
    }
</style>

<div class="container">

This table summarizes all registered Python API interfaces and their parameter information in iEDA.

## <a name="config"></a>config Module
<div class="module-section">

| API Name | Parameter List | Description |
|---------|---------------|-------------|
| db_init | (config_path='', tech_lef_path='', lef_paths=[], def_path='', verilog_path='', output_path='', feature_path='', lib_paths=[], sdc_path='') | Initialize database |
| flow_init | (flow_config) | Initialize flow configuration |

</div>
## <a name="eval"></a>eval Module
<div class="module-section">

| API Name | Parameter List | Description |
|---------|---------------|-------------|
| cell_density | (bin_cnt_x=256, bin_cnt_y=256, save_path='') | Calculate cell density |
| egr_congestion | (save_path='') | Calculate EGR congestion |
| eval_cell_hierarchy | (plot_path, level, forward) | Evaluate cell hierarchy |
| eval_continuous_white_space | () | Evaluate continuous white space |
| eval_macro_channel | (die_size_ratio) | Evaluate macro channel |
| eval_macro_connection | (plot_path, level, forward) | Evaluate macro connection |
| eval_macro_hierarchy | (plot_path, level, forward) | Evaluate macro hierarchy |
| eval_macro_io_pin_connection | (plot_path, level, forward) | Evaluate macro IO pin connection |
| eval_macro_margin | () | Evaluate macro margin |
| eval_macro_pin_connection | (plot_path, level, forward) | Evaluate macro pin connection |
| eval_overflow | () | Evaluate overflow |
| lut_rudy_congestion | (bin_cnt_x=256, bin_cnt_y=256, save_path='') | Calculate LUT-RUDY congestion |
| net_density | (bin_cnt_x=256, bin_cnt_y=256, save_path='') | Calculate net density |
| pin_density | (bin_cnt_x=256, bin_cnt_y=256, save_path='') | Calculate pin density |
| rudy_congestion | (bin_cnt_x=256, bin_cnt_y=256, save_path='') | Calculate RUDY congestion |
| timing_power_egr | () | Evaluate timing and power for EGR |
| timing_power_hpwl | () | Evaluate timing and power for HPWL |
| timing_power_stwl | () | Evaluate timing and power for STWL |
| total_wirelength_dict | () | Calculate total wirelength |

</div>
## <a name="feature"></a>feature Module
<div class="module-section">

| API Name | Parameter List | Description |
|---------|---------------|-------------|
| feature_cong_map | (step, dir) | Generate congestion map features |
| feature_cts_eval | (json_path, grid_size) | Evaluate clock tree synthesis features |
| feature_eval_map | (path, bin_cnt_x, bin_cnt_y) | Generate evaluation feature map |
| feature_eval_summary | (path, grid_size) | Generate evaluation feature summary |
| feature_net_eval | (path) | Evaluate net features |
| feature_pl_eval | (json_path, grid_size) | Evaluate placement features |
| feature_route | (path) | Generate routing features |
| feature_route_read | (path) | Read routing features |
| feature_summary | (path) | Generate feature summary |
| feature_timing_eval_summary | (path) | Generate timing evaluation feature summary |
| feature_tool | (path, step) | Feature tool |

</div>
## <a name="flow"></a>flow Module
<div class="module-section">

| API Name | Parameter List | Description |
|---------|---------------|-------------|
| flow_exit | () | Exit flow |

</div>
## <a name="icts"></a>icts Module
<div class="module-section">

| API Name | Parameter List | Description |
|---------|---------------|-------------|
| cts_report | (path) | Generate clock tree synthesis report |
| run_cts | (cts_config, cts_work_dir) | Run clock tree synthesis |

</div>
## <a name="idb"></a>idb Module
<div class="module-section">

| API Name | Parameter List | Description |
|---------|---------------|-------------|
| clear_blockage | (type) | Clear blockage |
| create_inst | (inst_name, cell_master, coord_x=0, coord_y=0, orient='', type='', status='') | Create instance |
| create_net | (net_name, conn_type='') | Create net |
| def_init | (def_path) | Initialize DEF |
| def_save | (def_name) | Save DEF file |
| delete_inst | (inst_name) | Delete instance |
| delete_net | (net_name) | Delete net |
| gds_save | (gds_name) | Save GDS file |
| idb_get | (inst_name='', net_name='', file_name='') | Get IDB information |
| idb_init | () | Initialize IDB |
| lef_init | (lef_paths) | Initialize LEF |
| netlist_save | (netlist_path, exclude_cell_names={}, is_add_space_for_escape_name=False) | Save netlist |
| remove_except_pg_net | () | Remove nets except power and ground |
| set_net | (net_name, net_type) | Set net |
| tech_lef_init | () | Initialize technology LEF |
| verilog_init | (verilog_path, top_module) | Initialize Verilog |

</div>
## <a name="idrc"></a>idrc Module
<div class="module-section">

| API Name | Parameter List | Description |
|---------|---------------|-------------|
| init_drc | (temp_directory_path='', thread_number=128, golden_directory_path='') | Initialize DRC |
| run_drc | (config='', report='') | Run DRC check |
| save_drc | (path='') | Save DRC results |

</div>
## <a name="ifp"></a>ifp Module
<div class="module-section">

| API Name | Parameter List | Description |
|---------|---------------|-------------|
| add_placement_blockage | (box) | Add placement blockage |
| add_placement_halo | (inst_name, distance) | Add placement halo |
| add_routing_blockage | (layer, box, exceptpgnet) | Add routing blockage |
| add_routing_halo | (layer, distance, exceptpgnet=False, inst_name) | Add routing halo |
| auto_place_pins | (layer, width, height, sides) | Auto place pins |
| gern_track | (layer, x_start, x_step, y_start, y_step) | Generate track |
| init_floorplan | (die_area, core_area, core_site, io_site, corner_site, core_util, x_margin, y_margin, xy_ratio, cell_area) | Initialize floorplan |
| place_io_filler | (filler_types, prefix='IOFill') | Place IO filler |
| place_port | (pin_name, offset_x, offset_y, width, height, layer) | Place port |
| tapcell | (tapcell, distance, endcap) | Add Tap Cell |

</div>
## <a name="ino"></a>ino Module
<div class="module-section">

| API Name | Parameter List | Description |
|---------|---------------|-------------|
| run_no_fixfanout | (config) | Run fanout optimization |

</div>
## <a name="instance"></a>instance Module
<div class="module-section">

| API Name | Parameter List | Description |
|---------|---------------|-------------|
| place_instance | (inst_name, llx, lly, orient, cellmaster, source='') | Place instance |

</div>
## <a name="ipdn"></a>ipdn Module
<div class="module-section">

| API Name | Parameter List | Description |
|---------|---------------|-------------|
| add_pdn_io | (pin_name='', net_name, direction, is_power) | Add power/ground IO |
| add_segment_stripe | (net_name='', point_list=[], layer='', width=0, point_begin=[], layer_start='', point_end=[], layer_end='', via_width=0, via_height=0) | Add segment stripe |
| add_segment_via | (net_name, layer='', top_layer='', bottom_layer='', offset_x, offset_y, width, height) | Add segment via |
| connectIoPinToPower | (point_list, layer) | Connect IO pin to power |
| connectMacroPdn | (pin_layer, pdn_layer, power_pins, ground_pins, orient) | Connect macro PDN |
| connectPowerStripe | (point_list, net_name, layer, width=-1) | Connect power stripe |
| connect_two_layer | (layers) | Connect two layers |
| create_grid | (layer_name, net_name_power, net_name_ground, width, offset) | Create power grid |
| create_stripe | (layer_name, net_name_power, net_name_ground, width, pitch, offset) | Create power stripe |
| global_net_connect | (net_name, instance_pin_name, is_power) | Global net connect |
| place_pdn_port | (pin_name, io_cell_name, offset_x, offset_y, width, height, layer) | Place power/ground port |

</div>
## <a name="ipl"></a>ipl Module
<div class="module-section">

| API Name | Parameter List | Description |
|---------|---------------|-------------|
| destroy_pl | () | Destroy placement |
| init_pl | (config) | Initialize placement |
| placer_run_dp | () | Run detailed placement |
| placer_run_gp | () | Run global placement |
| placer_run_lg | () | Run legalization |
| placer_run_mp | () | Run macro placement |
| run_ai_placement | (config, onnx_path, normalization_path) | Run AI placement |
| run_filler | (config) | Run filler |
| run_incremental_flow | (config) | Run incremental flow |
| run_incremental_lg | () | Run incremental legalization |
| run_placer | (config) | Run placer |

</div>
## <a name="ipnp"></a>ipnp Module
<div class="module-section">

| API Name | Parameter List | Description |
|---------|---------------|-------------|
| run_pnp | (config) | Run pin placement |

</div>
## <a name="ipw"></a>ipw Module
<div class="module-section">

| API Name | Parameter List | Description |
|---------|---------------|-------------|
| build_connection_map | () | Build connection map |
| build_macro_connection_map | () | Build macro connection map |
| create_data_flow | () | Create data flow |
| get_wire_timing_power_data | () | Get wire timing power data |
| read_pg_spef | (pg_spef_file) | Read power/ground SPEF file |
| read_vcd_cpp | (file_name, top_name) | Read VCD file |
| report_ir_drop | (power_nets) | Report IR drop |
| report_power | () | Report power |
| report_power_cpp | () | Report power |

</div>
## <a name="irt"></a>irt Module
<div class="module-section">

| API Name | Parameter List | Description |
|---------|---------------|-------------|
| destroy_rt | () | Destroy router |
| init_rt | (config='', config_dict={}) | Initialize router |
| run_egr | () | Run global routing |
| run_rt | () | Run detailed routing |

</div>
## <a name="ista"></a>ista Module
<div class="module-section">

| API Name | Parameter List | Description |
|---------|---------------|-------------|
| get_net_name | (pin_port_name) | Get net name |
| get_segment_capacitance | (layer_id, segment_length, route_layer_id) | Get segment capacitance |
| get_segment_resistance | (layer_id, segment_length, route_layer_id) | Get segment resistance |
| get_used_libs | () | Get used libraries |
| get_wire_timing_data | () | Get wire timing data |
| init_log | (log_dir) | Initialize log |
| init_sta | (output) | Initialize static timing analysis |
| link_design | (cell_name) | Link design |
| make_rc_tree_edge | (net_name, node1, node2, res) | Create RC tree edge |
| make_rc_tree_inner_node | (net_name, id, cap) | Create RC tree inner node |
| make_rc_tree_obj_node | (pin_port_name, cap) | Create RC tree object node |
| read_lef_def | (lef_files, def_file) | Read LEF and DEF files |
| read_liberty | (file_name) | Read Liberty library |
| read_netlist | (file_name) | Read netlist |
| read_sdc | (file_name) | Read SDC file |
| read_spef | (file_name) | Read SPEF file |
| report_sta | (output) | Generate static timing analysis report |
| report_timing | (digits, delay_type, exclude_cell_names, derate) | Report timing |
| run_sta | (output) | Run static timing analysis |
| set_design_workspace | (design_workspace) | Set design workspace |
| update_rc_tree_info | (net_name) | Update RC tree information |
| update_timing | () | Update timing |

</div>
## <a name="ito"></a>ito Module
<div class="module-section">

| API Name | Parameter List | Description |
|---------|---------------|-------------|
| run_to | (config) | Run timing optimization |
| run_to_drv | (config) | Run driver optimization |
| run_to_hold | (config) | Run hold time optimization |
| run_to_setup | (config) | Run setup time optimization |

</div>
## <a name="report"></a>report Module
<div class="module-section">

| API Name | Parameter List | Description |
|---------|---------------|-------------|
| report_congestion | (path='') | Report congestion |
| report_dangling_net | (path='') | Report dangling net |
| report_db | (path='') | Report database summary |
| report_drc | (path) | Report DRC results |
| report_place_distribution | (prefixes=[]) | Report placement distribution |
| report_prefixed_instance | (prefix, level=1, num_threshold=1) | Report prefixed instance |
| report_route | (path='', net='', summary=True) | Report routing |
| report_wirelength | (path='') | Report wirelength |

</div>
## <a name="vec"></a>vec Module
<div class="module-section">

| API Name | Parameter List | Description |
|---------|---------------|-------------|
| generate_vectors | (dir, patch_row_step=9, patch_col_step=9, batch_mode=True) | Generate vectors |
| get_timing_instance_graph | () | Get timing instance graph |
| get_timing_wire_graph | () | Get timing wire graph |
| layout_graph | (path) | Generate layout graph |
| layout_patchs | (path) | Generate layout patches |
| read_vectors_nets | (dir) | Read net vectors |
| read_vectors_nets_patterns | (path) | Read net pattern vectors |

</div>
</div>