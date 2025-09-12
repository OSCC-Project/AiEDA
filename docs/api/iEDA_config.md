# iEDA 点工具配置参数汇总表

此表格整理了iEDA中常用点工具的配置参数信息，方便用户参考和使用。

## 1. 平面规划 (Floorplan) 工具配置

| 参数名称 | 数据类型 | 默认值 | 说明 |
|---------|---------|--------|------|
| die_area | string | 无 | 芯片区域尺寸，格式为"x1,y1,x2,y2" |
| core_area | string | 无 | 核心区域尺寸，格式为"x1,y1,x2,y2" |
| core_util | float | 0.7 | 核心区域利用率 |
| core_site | string | 无 | 核心区域单元类型 |
| io_site | string | 无 | IO区域单元类型 |
| corner_site | string | 无 | 角落单元类型 |
| x_margin | int | 0 | X方向边距 |
| y_margin | int | 0 | Y方向边距 |
| xy_ratio | float | 1.0 | 宽高比 |
| cell_area | int | 0 | 单元面积 |

## 2. 布局 (Placement) 工具配置

| 参数名称 | 数据类型 | 默认值 | 说明 |
|---------|---------|--------|------|
| global_place_enable | bool | true | 是否启用全局布局 |
| detail_place_enable | bool | true | 是否启用详细布局 |
| macro_place_enable | bool | true | 是否启用宏单元布局 |
| incremental_place_enable | bool | false | 是否启用增量布局 |
| ai_place_enable | bool | false | 是否启用AI布局 |
| onnx_model_path | string | "" | ONNX模型路径(AI布局时使用) |
| normalization_path | string | "" | 归一化文件路径(AI布局时使用) |
| gp_iterations | int | 100 | 全局布局迭代次数 |
| lg_iterations | int | 50 | 详细布局迭代次数 |
| dp_iterations | int | 20 | 最终优化迭代次数 |
| target_density | float | 0.7 | 目标布局密度 |

## 3. 时钟树综合 (Clock Tree Synthesis) 工具配置

| 参数名称 | 数据类型 | 默认值 | 说明 |
|---------|---------|--------|------|
| cts_work_dir | string | 无 | 时钟树综合工作目录 |
| target_skew | float | 50.0 | 目标时钟偏斜( ps ) |
| max_capacitance | float | 500.0 | 最大电容( ff ) |
| max_fanout | int | 32 | 最大扇出 |
| max_transition | float | 50.0 | 最大转换时间( ps ) |
| buffer_cell | string | "" | 缓冲单元类型 |
| inverter_cell | string | "" | 反相器单元类型 |
| clock_nets | array | [] | 需要进行时钟树综合的网络列表 |

## 4. 布线 (Routing) 工具配置

| 参数名称 | 数据类型 | 默认值 | 说明 |
|---------|---------|--------|------|
| global_route_enable | bool | true | 是否启用全局布线 |
| detail_route_enable | bool | true | 是否启用详细布线 |
| timing_driven | bool | true | 是否启用时序驱动布线 |
| congestion_iterations | int | 5 | 拥塞优化迭代次数 |
| layer_adjust_iterations | int | 3 | 层调整迭代次数 |
| min_route_layer | int | 1 | 最小布线层 |
| max_route_layer | int | -1 | 最大布线层( -1表示使用所有层 ) |
| via_cost | float | 10.0 | 过孔成本系数 |
| wire_spacing | int | 1 | 线间距规则 |

## 5. 静态时序分析 (STA) 工具配置

| 参数名称 | 数据类型 | 默认值 | 说明 |
|---------|---------|--------|------|
| design_workspace | string | 无 | 设计工作目录 |
| lef_files | array | [] | LEF文件路径列表 |
| def_file | string | "" | DEF文件路径 |
| liberty_files | array | [] | Liberty库文件路径列表 |
| netlist_file | string | "" | 网表文件路径 |
| sdc_file | string | "" | SDC约束文件路径 |
| spef_files | array | [] | SPEF文件路径列表 |
| analysis_mode | string | "setup" | 分析模式(setup/hold) |
| derate | float | 1.0 | 时序分析系数 |
| digits | int | 3 | 报告显示小数位数 |

## 6. DRC (设计规则检查) 工具配置

| 参数名称 | 数据类型 | 默认值 | 说明 |
|---------|---------|--------|------|
| temp_directory_path | string | "" | 临时目录路径 |
| thread_number | int | 128 | 线程数量 |
| golden_directory_path | string | "" | 黄金数据目录路径 |
| report_path | string | "drc_report.txt" | DRC报告路径 |
| rule_decks | array | [] | 规则文件列表 |
| check_layers | array | [] | 需要检查的层列表 |
| severity_level | string | "ERROR" | 报告严重级别(ERROR/WARNING/INFO) |

## 7. 功耗分析 (Power Analysis) 工具配置

| 参数名称 | 数据类型 | 默认值 | 说明 |
|---------|---------|--------|------|
| vcd_file | string | "" | VCD文件路径 |
| top_module | string | "" | 顶层模块名称 |
| pg_spef_file | string | "" | 电源地SPEF文件路径 |
| power_nets | array | [] | 电源网络列表 |
| voltage | float | 1.8 | 工作电压(V) |
| temperature | int | 25 | 工作温度(°C) |
| output_report_path | string | "power_report.txt" | 功耗报告路径 |

## 8. 电源分配网络 (PDN) 工具配置

| 参数名称 | 数据类型 | 默认值 | 说明 |
|---------|---------|--------|------|
| power_net | string | "VDD" | 电源网络名称 |
| ground_net | string | "VSS" | 地网络名称 |
| grid_layers | array | [] | 网格层列表 |
| stripe_layers | array | [] | 条带层列表 |
| grid_width | int | 10 | 网格宽度 |
| grid_pitch | int | 100 | 网格间距 |
| stripe_width | int | 20 | 条带宽度 |
| stripe_pitch | int | 200 | 条带间距 |
| via_width | int | 8 | 过孔宽度 |
| via_height | int | 8 | 过孔高度 |

## 9. 时序优化 (Timing Optimization) 工具配置

| 参数名称 | 数据类型 | 默认值 | 说明 |
|---------|---------|--------|------|
| optimization_type | string | "all" | 优化类型(all/setup/hold/drv) |
| buffer_cells | array | [] | 可用缓冲单元列表 |
| inverter_cells | array | [] | 可用反相器单元列表 |
| max_buffer_insertion | int | 5 | 最大缓冲插入数量 |
| slack_threshold | float | 0.0 | 时序松弛阈值 |
| iteration_limit | int | 10 | 优化迭代次数限制 |
| area_constraint | float | 1.2 | 面积约束系数 |

## 10. 向量生成 (Vector Generation) 工具配置

| 参数名称 | 数据类型 | 默认值 | 说明 |
|---------|---------|--------|------|
| output_dir | string | "" | 输出目录 |
| patch_row_step | int | 9 | 行方向补丁步长 |
| patch_col_step | int | 9 | 列方向补丁步长 |
| batch_mode | bool | true | 是否使用批处理模式 |
| include_timing | bool | false | 是否包含时序信息 |
| include_power | bool | false | 是否包含功耗信息 |
| normalization | bool | true | 是否进行归一化处理 |

## 11. 评估 (Evaluation) 工具配置

| 参数名称 | 数据类型 | 默认值 | 说明 |
|---------|---------|--------|------|
| bin_cnt_x | int | 256 | X方向网格数量 |
| bin_cnt_y | int | 256 | Y方向网格数量 |
| save_path | string | "" | 结果保存路径 |
| die_size_ratio | float | 0.1 | 芯片尺寸比例 |
| plot_path | string | "" | 绘图保存路径 |
| hierarchy_level | int | 1 | 层次级别 |
| forward_direction | bool | true | 是否正向遍历层次 |

## 12. 特征提取 (Feature Extraction) 工具配置

| 参数名称 | 数据类型 | 默认值 | 说明 |
|---------|---------|--------|------|
| output_path | string | "" | 特征输出路径 |
| json_path | string | "" | JSON配置文件路径 |
| grid_size | int | 100 | 网格大小 |
| step_size | int | 10 | 步长 |
| include_congestion | bool | true | 是否包含拥塞特征 |
| include_timing | bool | true | 是否包含时序特征 |
| include_power | bool | false | 是否包含功耗特征 |