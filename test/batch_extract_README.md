# 批量特征提取工具使用说明

用于处理 skywater130 数据集中 SDC 文件和提取布局/布线特征的脚本工具。

## 工具简介

包含三个主要脚本：

1. **process_sdc_files.py** - 处理SDC文件，生成布局和布线版本
2. **batch_extract_place_features.py** - 提取布局特征
3. **batch_extract_route_features.py** - 提取布线特征

## 使用前提

- 已安装配置 aiEDA 框架
- 可访问 Sky130 PDK 文件
- 数据集目录包含设计子目录（含 `syn_netlist`、`place`、`route` 文件夹）

## 数据集目录结构

```
dataset_skywater130/
├── design1/
│   ├── syn_netlist/
│   │   └── design1.sdc
│   ├── place/
│   │   ├── design1.def
│   │   └── design1.sdc (由 process_sdc_files.py 生成)
│   └── route/
│       ├── design1.def
│       ├── design1.sdc (由 process_sdc_files.py 生成)
│       └── rpt/
│           └── design1.spef
├── design2/
│   └── ...
```

## 使用方法

### 1. 处理 SDC 文件

```bash
# 基本用法
python process_sdc_files.py /path/to/dataset_skywater130

# 指定数据集目录
python process_sdc_files.py --dataset-dir /path/to/dataset_skywater130
```

功能：
- 从 `syn_netlist` 目录读取 SDC 文件
- 生成布局版本（移除 `set_propagated_clock [all_clocks]`）
- 生成布线版本（确保包含 `set_propagated_clock [all_clocks]`）
- 分别保存到 `place` 和 `route` 目录

### 2. 提取布局特征

```bash
# 基本用法
python test/batch_extract_place_features.py /path/to/dataset_skywater130

# 自定义输出目录
python test/batch_extract_place_features.py --dataset-dir /path/to/dataset --output-dir /path/to/output

# 自定义patch大小
python test/batch_extract_place_features.py --dataset-dir /path/to/dataset --patch-row-step 18 --patch-col-step 18
```

### 3. 提取布线特征

```bash
# 基本用法
python test/batch_extract_route_features.py /path/to/dataset_skywater130

# 带自定义选项
python test/batch_extract_route_features.py --dataset-dir /path/to/dataset --output-dir /path/to/output --patch-row-step 24
```

## 主要参数

- `--dataset-dir`: 数据集目录路径
- `--output-dir`: 特征输出目录（默认自动生成）
- `--aieda-root`: aiEDA根目录路径（默认自动检测）
- `--patch-row-step`: 特征提取行步长（默认18）
- `--patch-col-step`: 特征提取列步长（默认18）

## 输出结果

- **process_sdc_files.py**: 在 place 和 route 目录生成 SDC 文件
- **batch_extract_place_features.py**: 在 `example/batch_place_features/` 生成特征向量
- **batch_extract_route_features.py**: 在 `example/batch_route_features/` 生成特征向量

## 完整流程示例

```bash
# 步骤1：处理SDC文件
python process_sdc_files.py /data/skywater130_dataset

# 步骤2：提取布局特征
python test/batch_extract_place_features.py /data/skywater130_dataset

# 步骤3：提取布线特征
python test/batch_extract_route_features.py /data/skywater130_dataset
```

## 注意事项

- 脚本会自动发现可用设计
- 缺失文件的设计会被跳过，不会导致整体失败
- 支持绝对路径和相对路径