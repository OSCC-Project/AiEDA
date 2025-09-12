# iEDA Workspace路径和配置管理功能汇总

本文件汇总了iEDA Workspace模块中路径和配置管理相关的类和功能。

## 1. Workspace主类

| 功能类别 | 方法名 | 描述 | 参数 |
|---------|-------|------|-----|
| 工作空间创建 | `create_wrokspace` | 检查并创建工作空间目录结构，初始化配置文件 | `flow_list`：流程列表（可选） |
| 路径设置 | `set_tech_lef` | 设置工艺LEF文件路径并更新配置 | `tech_lef`：工艺LEF文件路径 |
| 路径设置 | `set_lefs` | 设置LEF文件列表并更新配置 | `lefs`：LEF文件路径列表 |
| 路径设置 | `set_libs` | 设置库文件列表并更新配置 | `libs`：库文件路径列表 |
| 路径设置 | `set_max_libs` | 设置最大库文件列表 | `libs`：最大库文件路径列表 |
| 路径设置 | `set_min_libs` | 设置最小库文件列表 | `libs`：最小库文件路径列表 |
| 路径设置 | `set_sdc` | 设置SDC文件路径并更新配置 | `sdc_path`：SDC文件路径 |
| 路径设置 | `set_spef` | 设置SPEF文件路径并更新配置 | `spef_path`：SPEF文件路径 |
| 路径设置 | `set_rcworst` | 设置RC worst文件路径 | `rcworst_path`：RC worst文件路径 |
| 路径设置 | `set_rcbest` | 设置RC best文件路径 | `rcbest_path`：RC best文件路径 |
| 路径设置 | `set_def_input` | 设置DEF输入文件路径并更新配置 | `def_input`：DEF文件路径 |
| 路径设置 | `set_verilog_input` | 设置Verilog输入文件路径并更新配置 | `verilog_input`：Verilog文件路径 |
| 工作空间配置 | `set_flows` | 设置流程配置并更新flow.json | `flows`：流程配置 |
| 工作空间配置 | `set_process_node` | 设置工艺节点 | `process_node`：工艺节点名称 |
| 工作空间配置 | `set_design` | 设置设计名称 | `design`：设计名称 |
| 工作空间配置 | `set_version` | 设置版本信息 | `version`：版本字符串 |
| 工作空间配置 | `set_project` | 设置项目名称 | `project`：项目名称 |
| 工作空间配置 | `set_task` | 设置任务名称 | `task`：任务名称 |
| iEDA工具配置 | `set_first_routing_layer` | 设置首个布线层 | `layer`：布线层名称 |
| iEDA工具配置 | `set_ieda_fixfanout_buffer` | 设置Fanout修复的buffer | `buffer`：buffer单元名称 |
| iEDA工具配置 | `set_ieda_cts_buffers` | 设置CTS的buffer列表 | `buffers`：buffer单元名称列表 |
| iEDA工具配置 | `set_ieda_cts_root_buffer` | 设置CTS的根buffer | `buffer`：buffer单元名称 |
| iEDA工具配置 | `set_ieda_placement_buffers` | 设置布局的buffer列表 | `buffers`：buffer单元名称列表 |
| iEDA工具配置 | `set_ieda_filler_cells_for_first_iteration` | 设置第一轮填充单元 | `cells`：填充单元名称列表 |
| iEDA工具配置 | `set_ieda_filler_cells_for_second_iteration` | 设置第二轮填充单元 | `cells`：填充单元名称列表 |
| iEDA工具配置 | `set_ieda_optdrv_buffers` | 设置驱动优化的buffer | `buffers`：buffer单元名称列表 |
| iEDA工具配置 | `set_ieda_opthold_buffers` | 设置保持时间优化的buffer | `buffers`：buffer单元名称列表 |
| iEDA工具配置 | `set_ieda_optsetup_buffers` | 设置建立时间优化的buffer | `buffers`：buffer单元名称列表 |
| iEDA工具配置 | `set_ieda_router_layer` | 设置布线层范围 | `bottom_layer`：底层名称，`top_layer`：顶层名称 |
| iEDA工具配置 | `set_ieda_router_timing` | 设置布线时是否启用时序优化 | `enable_timing`：布尔值 |
| 参数管理 | `update_parameters` | 更新参数配置并保存到JSON | `parameters`：EDAParameters对象 |
| 参数管理 | `load_parameters` | 从JSON文件加载参数配置 | `parameters_json`：参数JSON文件路径 |
| 参数管理 | `print_paramters` | 打印参数配置信息 | 无 |

## 2. PathsTable类（路径管理）

| 路径类别 | 属性/方法名 | 路径格式 | 描述 |
|---------|------------|---------|------|
| 工作空间顶层 | `workspace_top` | 列表包含以下目录：<br>- `{directory}/analyse`<br>- `{directory}/config`<br>- `{directory}/feature`<br>- `{directory}/output`<br>- `{directory}/script`<br>- `{directory}/report` | 工作空间主要目录结构 |
| 分析目录 | `analysis_dir` | `{directory}/analyse` | 分析结果目录 |
| 输出目录 | `output_dir` | `{directory}/output` | 输出文件目录 |
| 配置文件 | `flow` | `{directory}/config/flow.json` | 流程配置文件路径 |
| 配置文件 | `path` | `{directory}/config/path.json` | PDK和设计路径配置文件 |
| 配置文件 | `workspace` | `{directory}/config/workspace.json` | 工作空间设置文件 |
| 配置文件 | `parameters` | `{directory}/config/parameter.json` | 参数设置文件 |
| 日志 | `log_dir` | `{directory}/output/log` | 日志文件目录 |
| 日志 | `log` | `{log_dir}/{design}.log` | 日志文件路径 |
| 报告 | `report_dir` | `{directory}/report` | 报告文件目录 |
| 报告 | `report` | 包含summary_md和summary_html的字典 | 工作空间报告文件路径 |
| iEDA输出 | `ieda_output_dirs` | 列表包含iEDA各输出目录 | iEDA工具的输出目录结构 |
| iEDA配置 | `ieda_config` | 包含各种iEDA配置文件路径的字典 | iEDA工具各阶段的配置文件路径 |
| iEDA输出 | `ieda_output` | 包含各种iEDA输出路径的字典 | iEDA工具各阶段的输出文件路径 |
| iEDA报告 | `ieda_report` | 包含DRC报告路径的字典 | iEDA生成的报告文件路径 |
| iEDA特征 | `ieda_feature_json` | 包含各种特征JSON路径的字典 | 各阶段特征数据文件路径 |
| iEDA向量 | `ieda_vectors` | 包含各种向量数据路径的字典 | 向量数据文件和目录路径 |
| iEDA GUI | `ieda_gui` | 包含GUI相关路径的字典 | GUI相关文件路径 |
| 脚本 | `scripts` | 包含各种脚本路径的字典 | Tcl脚本文件路径 |
| 分析图像 | `analysis_images` | 包含各种分析图像路径的字典 | 分析可视化图像文件路径 |
| 辅助方法 | `get_image_path` | 动态生成图像路径 | 根据类型获取特定图像文件路径 |

## 3. Configs类（配置管理）

| 功能类别 | 方法名 | 描述 | 参数 |
|---------|-------|------|-----|
| 初始化 | `__init__` | 初始化配置管理器，加载各类配置 | `paths_table`：路径表，`logger`：日志记录器 |
| 更新 | `update` | 更新所有配置 | 无 |
| 内部初始化 | `_init_flow_json` | 初始化流程配置 | 无 |
| 内部初始化 | `_init_path_json` | 初始化路径配置 | 无 |
| 内部初始化 | `_init_workspace_json` | 初始化工作空间配置 | 无 |
| 内部初始化 | `_init_parameters` | 初始化参数配置 | 无 |
| 流程管理 | `reset_flow_states` | 重置流程状态 | 无 |
| 流程管理 | `save_flow_state` | 保存流程状态 | `db_flow`：流程数据库对象 |
| 输出文件 | `get_output_def` | 获取输出DEF文件路径 | `flow`：流程对象，`compressed`：是否压缩 |
| 输出文件 | `get_output_verilog` | 获取输出Verilog文件路径 | `flow`：流程对象，`compressed`：是否压缩 |

## 4. 工作空间初始化流程

Workspace类的`create_wrokspace`方法会按照以下步骤初始化工作空间：

1. 确保工作空间目录存在，如果不存在则创建
2. 创建工作空间顶层目录（analyse、config、feature、output、script、report）
3. 创建iEDA输出目录结构
4. 创建日志文件并初始化logger和configs
5. 创建flow.json配置文件
6. 创建path.json配置文件
7. 创建workspace.json配置文件
8. 创建parameter.json配置文件
9. 创建iEDA_config目录及其中的各类配置文件
10. 更新配置

## 5. iEDA配置文件结构

在iEDA_config目录下创建的配置文件包括：

- `flow_config.json`：iEDA流程配置
- `db_default_config.json`：数据库初始化配置
- `fp_default_config.json`：平面规划配置
- `pnp_default_config.json`：引脚排列配置
- `no_default_config_fixfanout.json`：扇出修复配置
- `pl_default_config.json`：布局配置
- `cts_default_config.json`：时钟树综合配置
- `to_default_config_drv.json`：驱动优化配置
- `to_default_config_hold.json`：保持时间优化配置
- `to_default_config_setup.json`：建立时间优化配置
- `rt_default_config.json`：布线配置
- `drc_default_config.json`：DRC检查配置

这些配置文件分别对应iEDA工具的不同设计阶段。