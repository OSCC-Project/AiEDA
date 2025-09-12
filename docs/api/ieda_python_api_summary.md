# iEDA Python API 汇总表

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

此表格整理了iEDA中所有注册的Python API接口及其参数信息。

## <a name="config"></a>config 模块
<div class="module-section">

| API名称 | 参数列表 | 说明 |
|---------|---------|------|
| db_init | (config_path='', tech_lef_path='', lef_paths=[], def_path='', verilog_path='', output_path='', feature_path='', lib_paths=[], sdc_path='') | 初始化数据库 |
| flow_init | (flow_config) | 初始化流程配置 |

</div>
## <a name="eval"></a>eval 模块
<div class="module-section">

| API名称 | 参数列表 | 说明 |
|---------|---------|------|
| cell_density | (bin_cnt_x=256, bin_cnt_y=256, save_path='') | 计算单元密度 |
| egr_congestion | (save_path='') | 计算EGR拥塞 |
| eval_cell_hierarchy | (plot_path, level, forward) | 评估单元层次结构 |
| eval_continuous_white_space | () | 评估连续空白区域 |
| eval_macro_channel | (die_size_ratio) | 评估宏单元通道 |
| eval_macro_connection | (plot_path, level, forward) | 评估宏单元连接 |
| eval_macro_hierarchy | (plot_path, level, forward) | 评估宏单元层次结构 |
| eval_macro_io_pin_connection | (plot_path, level, forward) | 评估宏单元IO引脚连接 |
| eval_macro_margin | () | 评估宏单元边界 |
| eval_macro_pin_connection | (plot_path, level, forward) | 评估宏单元引脚连接 |
| eval_overflow | () | 评估溢出 |
| lut_rudy_congestion | (bin_cnt_x=256, bin_cnt_y=256, save_path='') | 计算LUT-RUDY拥塞 |
| net_density | (bin_cnt_x=256, bin_cnt_y=256, save_path='') | 计算网络密度 |
| pin_density | (bin_cnt_x=256, bin_cnt_y=256, save_path='') | 计算引脚密度 |
| rudy_congestion | (bin_cnt_x=256, bin_cnt_y=256, save_path='') | 计算RUDY拥塞 |
| timing_power_egr | () | 评估EGR的时序和功耗 |
| timing_power_hpwl | () | 评估HPWL的时序和功耗 |
| timing_power_stwl | () | 评估STWL的时序和功耗 |
| total_wirelength_dict | () | 计算总绕线长度 |

</div>
## <a name="feature"></a>feature 模块
<div class="module-section">

| API名称 | 参数列表 | 说明 |
|---------|---------|------|
| feature_cong_map | (step, dir) | 生成拥塞图特征 |
| feature_cts_eval | (json_path, grid_size) | 评估时钟树综合特征 |
| feature_eval_map | (path, bin_cnt_x, bin_cnt_y) | 生成评估特征图 |
| feature_eval_summary | (path, grid_size) | 生成评估特征摘要 |
| feature_net_eval | (path) | 评估网络特征 |
| feature_pl_eval | (json_path, grid_size) | 评估布局特征 |
| feature_route | (path) | 生成布线特征 |
| feature_route_read | (path) | 读取布线特征 |
| feature_summary | (path) | 生成特征摘要 |
| feature_timing_eval_summary | (path) | 生成时序评估特征摘要 |
| feature_tool | (path, step) | 特征工具 |

</div>
## <a name="flow"></a>flow 模块
<div class="module-section">

| API名称 | 参数列表 | 说明 |
|---------|---------|------|
| flow_exit | () | 退出流程 |

</div>
## <a name="icts"></a>icts 模块
<div class="module-section">

| API名称 | 参数列表 | 说明 |
|---------|---------|------|
| cts_report | (path) | 生成时钟树综合报告 |
| run_cts | (cts_config, cts_work_dir) | 运行时钟树综合 |

</div>
## <a name="idb"></a>idb 模块
<div class="module-section">

| API名称 | 参数列表 | 说明 |
|---------|---------|------|
| clear_blockage | (type) | 清除阻塞 |
| create_inst | (inst_name, cell_master, coord_x=0, coord_y=0, orient='', type='', status='') | 创建实例 |
| create_net | (net_name, conn_type='') | 创建网络 |
| def_init | (def_path) | 初始化DEF |
| def_save | (def_name) | 保存DEF文件 |
| delete_inst | (inst_name) | 删除实例 |
| delete_net | (net_name) | 删除网络 |
| gds_save | (gds_name) | 保存GDS文件 |
| idb_get | (inst_name='', net_name='', file_name='') | 获取IDB信息 |
| idb_init | () | 初始化IDB |
| lef_init | (lef_paths) | 初始化LEF |
| netlist_save | (netlist_path, exclude_cell_names={}, is_add_space_for_escape_name=False) | 保存网表 |
| remove_except_pg_net | () | 移除除电源地以外的网络 |
| set_net | (net_name, net_type) | 设置网络 |
| tech_lef_init | () | 初始化技术LEF |
| verilog_init | (verilog_path, top_module) | 初始化Verilog |

</div>
## <a name="idrc"></a>idrc 模块
<div class="module-section">

| API名称 | 参数列表 | 说明 |
|---------|---------|------|
| init_drc | (temp_directory_path='', thread_number=128, golden_directory_path='') | 初始化DRC |
| run_drc | (config='', report='') | 运行DRC检查 |
| save_drc | (path='') | 保存DRC结果 |

</div>
## <a name="ifp"></a>ifp 模块
<div class="module-section">

| API名称 | 参数列表 | 说明 |
|---------|---------|------|
| add_placement_blockage | (box) | 添加布局阻塞 |
| add_placement_halo | (inst_name, distance) | 添加布局光晕 |
| add_routing_blockage | (layer, box, exceptpgnet) | 添加布线阻塞 |
| add_routing_halo | (layer, distance, exceptpgnet=False, inst_name) | 添加布线光晕 |
| auto_place_pins | (layer, width, height, sides) | 自动放置引脚 |
| gern_track | (layer, x_start, x_step, y_start, y_step) | 生成轨道 |
| init_floorplan | (die_area, core_area, core_site, io_site, corner_site, core_util, x_margin, y_margin, xy_ratio, cell_area) | 初始化平面规划 |
| place_io_filler | (filler_types, prefix='IOFill') | 放置IO填充 |
| place_port | (pin_name, offset_x, offset_y, width, height, layer) | 放置端口 |
| tapcell | (tapcell, distance, endcap) | 添加Tap Cell |

</div>
## <a name="ino"></a>ino 模块
<div class="module-section">

| API名称 | 参数列表 | 说明 |
|---------|---------|------|
| run_no_fixfanout | (config) | 运行扇出优化 |

</div>
## <a name="instance"></a>instance 模块
<div class="module-section">

| API名称 | 参数列表 | 说明 |
|---------|---------|------|
| place_instance | (inst_name, llx, lly, orient, cellmaster, source='') | 放置实例 |

</div>
## <a name="ipdn"></a>ipdn 模块
<div class="module-section">

| API名称 | 参数列表 | 说明 |
|---------|---------|------|
| add_pdn_io | (pin_name='', net_name, direction, is_power) | 添加电源地IO |
| add_segment_stripe | (net_name='', point_list=[], layer='', width=0, point_begin=[], layer_start='', point_end=[], layer_end='', via_width=0, via_height=0) | 添加分段条带 |
| add_segment_via | (net_name, layer='', top_layer='', bottom_layer='', offset_x, offset_y, width, height) | 添加分段过孔 |
| connectIoPinToPower | (point_list, layer) | 连接IO引脚到电源 |
| connectMacroPdn | (pin_layer, pdn_layer, power_pins, ground_pins, orient) | 连接宏单元电源 |
| connectPowerStripe | (point_list, net_name, layer, width=-1) | 连接电源条带 |
| connect_two_layer | (layers) | 连接两层 |
| create_grid | (layer_name, net_name_power, net_name_ground, width, offset) | 创建电源网格 |
| create_stripe | (layer_name, net_name_power, net_name_ground, width, pitch, offset) | 创建电源条带 |
| global_net_connect | (net_name, instance_pin_name, is_power) | 全局网络连接 |
| place_pdn_port | (pin_name, io_cell_name, offset_x, offset_y, width, height, layer) | 放置电源地端口 |

</div>
## <a name="ipl"></a>ipl 模块
<div class="module-section">

| API名称 | 参数列表 | 说明 |
|---------|---------|------|
| destroy_pl | () | 销毁布局 |
| init_pl | (config) | 初始化布局 |
| placer_run_dp | () | 运行详细摆放 |
| placer_run_gp | () | 运行全局布局 |
| placer_run_lg | () | 运行详细布局 |
| placer_run_mp | () | 运行宏单元布局 |
| run_ai_placement | (config, onnx_path, normalization_path) | 运行AI布局 |
| run_filler | (config) | 运行填充 |
| run_incremental_flow | (config) | 运行增量流程 |
| run_incremental_lg | () | 运行增量详细布局 |
| run_placer | (config) | 运行布局器 |

</div>
## <a name="ipnp"></a>ipnp 模块
<div class="module-section">

| API名称 | 参数列表 | 说明 |
|---------|---------|------|
| run_pnp | (config) | 运行引脚规划 |

</div>
## <a name="ipw"></a>ipw 模块
<div class="module-section">

| API名称 | 参数列表 | 说明 |
|---------|---------|------|
| build_connection_map | () | 构建连接图 |
| build_macro_connection_map | () | 构建宏单元连接图 |
| create_data_flow | () | 创建数据流 |
| get_wire_timing_power_data | () | 获取线网时序功耗数据 |
| read_pg_spef | (pg_spef_file) | 读取电源地SPEF文件 |
| read_vcd_cpp | (file_name, top_name) | 读取VCD文件 |
| report_ir_drop | (power_nets) | 报告IR压降 |
| report_power | () | 报告功耗 |
| report_power_cpp | () | 报告功耗 |

</div>
## <a name="irt"></a>irt 模块
<div class="module-section">

| API名称 | 参数列表 | 说明 |
|---------|---------|------|
| destroy_rt | () | 销毁布线工具 |
| init_rt | (config='', config_dict={}) | 初始化布线工具 |
| run_egr | () | 运行全局布线 |
| run_rt | () | 运行详细布线 |

</div>
## <a name="ista"></a>ista 模块
<div class="module-section">

| API名称 | 参数列表 | 说明 |
|---------|---------|------|
| get_net_name | (pin_port_name) | 获取网络名称 |
| get_segment_capacitance | (layer_id, segment_length, route_layer_id) | 获取段电容 |
| get_segment_resistance | (layer_id, segment_length, route_layer_id) | 获取段电阻 |
| get_used_libs | () | 获取使用的库 |
| get_wire_timing_data | () | 获取线网时序数据 |
| init_log | (log_dir) | 初始化日志 |
| init_sta | (output) | 初始化静态时序分析 |
| link_design | (cell_name) | 链接设计 |
| make_rc_tree_edge | (net_name, node1, node2, res) | 创建RC树边缘 |
| make_rc_tree_inner_node | (net_name, id, cap) | 创建RC树内部节点 |
| make_rc_tree_obj_node | (pin_port_name, cap) | 创建RC树对象节点 |
| read_lef_def | (lef_files, def_file) | 读取LEF和DEF文件 |
| read_liberty | (file_name) | 读取Liberty库 |
| read_netlist | (file_name) | 读取网表 |
| read_sdc | (file_name) | 读取SDC文件 |
| read_spef | (file_name) | 读取SPEF文件 |
| report_sta | (output) | 生成静态时序分析报告 |
| report_timing | (digits, delay_type, exclude_cell_names, derate) | 报告时序 |
| run_sta | (output) | 运行静态时序分析 |
| set_design_workspace | (design_workspace) | 设置设计工作区 |
| update_rc_tree_info | (net_name) | 更新RC树信息 |
| update_timing | () | 更新时序 |

</div>
## <a name="ito"></a>ito 模块
<div class="module-section">

| API名称 | 参数列表 | 说明 |
|---------|---------|------|
| run_to | (config) | 运行时序优化 |
| run_to_drv | (config) | 运行驱动优化 |
| run_to_hold | (config) | 运行保持时间优化 |
| run_to_setup | (config) | 运行建立时间优化 |

</div>
## <a name="report"></a>report 模块
<div class="module-section">

| API名称 | 参数列表 | 说明 |
|---------|---------|------|
| report_congestion | (path='') | 报告拥塞 |
| report_dangling_net | (path='') | 报告悬空网络 |
| report_db | (path='') | 报告数据库摘要 |
| report_drc | (path) | 报告DRC结果 |
| report_place_distribution | (prefixes=[]) | 报告布局分布 |
| report_prefixed_instance | (prefix, level=1, num_threshold=1) | 报告带前缀的实例 |
| report_route | (path='', net='', summary=True) | 报告布线 |
| report_wirelength | (path='') | 报告绕线长度 |

</div>
## <a name="vec"></a>vec 模块
<div class="module-section">

| API名称 | 参数列表 | 说明 |
|---------|---------|------|
| generate_vectors | (dir, patch_row_step=9, patch_col_step=9, batch_mode=True) | 生成向量 |
| get_timing_instance_graph | () | 获取时序实例图 |
| get_timing_wire_graph | () | 获取时序线网图 |
| layout_graph | (path) | 生成布局图 |
| layout_patchs | (path) | 生成布局补丁 |
| read_vectors_nets | (dir) | 读取网络向量 |
| read_vectors_nets_patterns | (path) | 读取网络模式向量 |

</div>
</div>

