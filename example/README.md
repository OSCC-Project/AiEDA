# 数据的组织与含义

## Workspace概述

### 1. 核心设计理念

`Workspace`是AiEDA中的核心数据管理类，提供了统一的工作环境和数据流管理机制。它通过封装工作区目录结构、配置文件、工具输出路径和数据文件，实现了EDA多工具链的高效集成和数据统一访问。

### 2. 主要功能与架构

**核心功能模块：**
- 工作区创建与初始化
- 设计信息管理
- 配置文件统一管理
- 工具输出路径标准化
- 数据文件路径获取接口
- 多工具引擎集成支持

**架构设计：**
- `Workspace`主类负责高层功能协调
- `PathsTable`内部类负责所有路径管理，定义了各类重要文件的路径，包括工艺文件、结果文件、分析报告、向量化数据等路径
- 各类Parser实现配置文件的读写与解析

### 3. 目录结构组织

以`sky130_gcd`为例，完整的workspace目录结构如下：

```
sky130_gcd/
├── analyse/       # 分析结果目录，存放当前设计的各类可视化分析结果
├── config/        # 配置文件目录，存放多工具引擎和当前流程管理的配置文件
│   ├── flow.json  # 流程配置文件
│   ├── path.json  # 路径配置文件
│   ├── parameter.json  # 参数配置文件
│   ├── workspace.json  # 工作区配置文件
│   └── iEDA_config/    # 其余第三方EDA工具配置目录，这里以iEDA工具配置目录为例
├── output/        # 工具输出目录，存放多工具引擎的输出文件
│   ├── DREAMPlace/  # DREAMPlace工具输出
│   ├── OpenROAD/    # OpenROAD工具输出
│   └── iEDA/        # iEDA工具输出。当前开源版本只接入iEDA，这里以iEDA工具输出为例
│       ├── result/   # 原始数据(.def/.v)
│       ├── data/     # 点工具输出数据(place log)
│       ├── feature/  # 阶段特征数据(.json,.csv)
│       ├── rpt/      # 报告数据
│       └── vectors/  # 向量化基础数据(.json)
├── report/        # 报告目录，对分析结果的进一步整理和汇总
└── script/        # 脚本目录，存放商业工具脚本
```

### 4. PathsTable内部类详解

`PathsTable`是`Workspace`的内部类，采用属性装饰器模式，将路径生成逻辑封装在方法中，用户可以基于PathsTable获取到对应文件路径以进行后续操作，主要功能包括：

- **顶层路径管理**：定义workspace目录下各子目录路径
- **配置路径管理**：管理flow.json、path.json等配置文件路径
- **iEDA配置管理**：管理各工具（floorplan、place、CTS、route等）的配置文件路径
- **输出路径管理**：定义各阶段工具输出路径
- **特征与向量路径**：管理特征提取和向量数据文件路径

注意，当用户需要接入第三方工具，可以参照**iEDA配置管理**以进行路径管理的扩充。

### 5. 工作流程

**工作区创建流程：**
1. 调用`create_workspace`方法
2. 创建目录结构
3. 初始化日志
4. 生成基础配置文件（flow.json、path.json等）
5. 设置设计信息和技术库路径

**数据访问流程：**
1. 通过`Workspace`实例获取路径
2. 读取或写入对应路径的文件
3. 各工具引擎使用统一接口访问数据

### 6. 关键实现机制

**路径管理机制：**
- 使用属性装饰器动态生成路径
- 采用模板化路径定义，确保一致性
- 支持不同设计和不同工具的路径隔离

**配置管理机制：**
- 使用专用Parser类处理不同格式配置
- 支持配置的读写和动态更新
- 实现配置与路径的关联管理


## Config概述

### 1. 配置系统概述

Workspace的config目录是AiEDA配置管理的核心，采用分层设计，支持多工具引擎配置的统一管理。用户既可以通过直接修改配置文件内容来配置运行流程，也可以基于Workspace类通过程序接口动态修改配置参数。

### 2. 顶层配置文件结构

config目录包含四个核心配置文件和一个工具配置子目录：

```
config/
├── flow.json        # 流程配置文件
├── parameter.json   # 参数配置文件
├── path.json        # 路径配置文件
├── workspace.json   # 工作区配置文件
└── iEDA_config/     # 其余第三方EDA工具配置目录，这里以iEDA工具配置目录为例
```

### 3. 核心配置文件详解

#### 3.1 workspace.json - 工作区基本信息

工作区概况配置，定义工作区的基础属性：

```json
{
    "workspace": {
        "process_node": "sky130",  # 工艺节点
        "version": "V1",           # 版本号
        "project": "gcd",          # 项目名称
        "design": "gcd",           # 设计名称
        "task": "run_eda"          # 执行任务类型
    }
}
```

主要功能：定义工作区标识信息，为后续工具执行提供基础上下文。

#### 3.2 flow.json - 流程配置

记录和配置设计流程的执行序列和状态：

```json
{
    "task": "run_eda",
    "flow": [
        {
            "eda_tool": "iEDA",      # 使用的EDA工具
            "step": "floorplan",     # 执行阶段
            "state": "success",      # 执行状态
            "runtime": "0:0:5"       # 运行时间
        },
        // 更多阶段...
    ]
}
```

主要功能：定义执行任务类型，配置流程执行阶段序列，记录各阶段执行状态和时间，支持多工具链的混合执行。

#### 3.3 path.json - 文件路径配置

配置和记录所有必要文件的路径，是设计流程执行的基础：

```json
{
    "def_input_path": "./gcd_floorplan.def",      # DEF文件路径
    "verilog_input_path": "./gcd_floorplan.v",    # Verilog文件路径 (可选)
    "tech_lef_path": "./sky130_fd_sc_hs.tlef",    # 工艺LEF文件路径
    "lef_paths": [...],                           # LEF文件路径列表
    "lib_paths": [...],                           # 库文件路径列表
    "sdc_path": "./gcd.sdc",                      # 时序约束文件路径
    "spef_path": "/gcd.spef",                     # SPEF文件路径
    // 其他路径配置...
}
```

主要功能：集中管理所有输入输出文件路径，支持多工艺库和设计文件配置，为工具执行提供文件访问路径。

#### 3.4 parameter.json - 工具参数配置

配置各工具阶段的关键参数，采用统一命名标准：

```json
{
    "placement_target_density": 0.4,       # 布局目标密度
    "placement_max_phi_coef": 1.04,        # 布局算法的参数
    "cts_skew_bound": "0.1",               # CTS时序约束
    "cts_max_buf_tran": "1.2",             # CTS缓冲器转换约束
    // 其他参数配置...
}
```

主要功能：提供跨工具的统一参数命名标，集中管理各阶段优化参数，支持参数调优和探索。

### 4. 第三方工具引擎配置

#### 4.1 iEDA配置文件结构

iEDA工具引擎配置存放在`iEDA_config`子目录下，包含多个阶段配置文件：

```
iEDA_config/
├── flow_config.json              # 流程配置
├── db_default_config.json        # 数据库配置
├── fp_default_config.json        # 布局规划配置
├── pnp_default_config.json       # PDN配置
├── pl_default_config.json        # 布局配置
├── cts_default_config.json       # CTS配置
├── to_default_config_drv.json    # 时序优化配置
├── to_default_config_hold.json   # 时序优化配置
├── to_default_config_setup.json  # 时序优化配置
├── rt_default_config.json        # 布线配置
└── drc_default_config.json       # DRC配置
```

<!-- TODO: #### 4.2 <其他工具>配置文件结构 -->

### 5. 配置管理机制

#### 5.1 Parser架构

AiEDA采用专门的Parser类处理不同类型的配置文件，主要包括：

- `WorkspaceParser` - 工作区配置解析
- `FlowParser` - 流程配置解析
- `PathParser` - 路径配置解析
- `ParametersParser` - 参数配置解析
- `ConfigIEDADbParser` - iEDA数据库配置解析
- `ConfigIEDAFloorplanParser`等 - iEDA各阶段配置解析

注意，当用户需要接入第三方工具，可以参照**ConfigIEDADbParser**等进行路径管理的扩充。

#### 5.2 配置创建流程

在`Workspace.create_workspace()`方法中，配置文件创建流程如下：
1. 创建目录结构
2. 初始化配置对象
3. 按顺序创建各配置文件：
   - flow.json
   - path.json
   - workspace.json
   - parameter.json
   - iEDA各阶段配置文件

#### 5.3 配置访问和修改机制

每个Parser类提供以下核心功能：
- `create_json()` - 创建配置文件
- `get_db()` - 读取配置到数据结构
- `set_xxx()` - 设置特定配置项
- 支持动态读写和更新

### 6. 多工具支持机制

AiEDA设计了灵活的配置扩展机制，支持多种工具引擎：

- 统一的配置接口设计
- 工具特定配置的隔离管理
- 支持配置的增量式扩充
- 为未来集成DREAMPlace等工具预留扩展点

### 7. 配置最佳实践

- 使用Workspace类API修改配置，避免直接编辑文件
- 使用parameter.json中的统一参数名（如布局密度、CTS约束）进行跨工具配置

## Output概述

Workspace的output目录是AiEDA集中存储和管理所有EDA工具运行输出数据的目录系统。该目录采用工具名隔离的组织结构，确保多工具引擎环境下数据的清晰管理和访问。下面详细介绍输出目录的整体架构和各子目录内容。

### 1. 文件结构

输出目录采用分层结构设计，顶层按EDA工具名称组织，每个工具目录内部进一步划分为功能明确的数据子目录。这种设计确保了不同工具生成的数据相互隔离，同时也便于在工具间共享必要的中间数据。AiEDA通过Workspace类提供标准化API，实现对各工具数据的统一访问。

```
output/
├── DREAMPlace/     # DREAMPlace布局工具输出
├── OpenROAD/       # OpenROAD工具输出
└── iEDA/           # iEDA工具输出（详细结构如下）
    ├── data/       # 点工具运行过程数据
    ├── feature/    # 阶段特征数据
    ├── result/     # 结果数据
    ├── rpt/        # 报告文件
    └── vectors/    # 向量化数据
```

### 2. iEDA工具输出目录详解

以iEDA工具为例，其输出目录包含五个主要子系统：

#### 2.1 result目录 - 结果数据

存储EDA流程各阶段的最终结果文件，主要包括网表文件（.v）和物理设计交换文件（.def），采用gzip压缩以节省空间。

- **文件命名规范**：`{design_name}_{stage_name}.{ext}.gz`
  - `design_name`：设计名称，如"gcd"
  - `stage_name`：流程阶段，如"floorplan"、"place"、"CTS"、"route"等
  - `ext`：文件扩展名，主要为"def"和"v"

- **主要文件列表**：
  ```
  result/
  ├── gcd_floorplan.def.gz     # floorplan阶段物理设计文件
  ├── gcd_floorplan.v.gz       # floorplan阶段网表文件
  ├── gcd_place.def.gz         # 布局阶段物理设计文件
  ├── gcd_place.v.gz           # 布局阶段网表文件
  ├── gcd_CTS.def.gz           # 时钟树综合阶段物理设计文件
  ├── gcd_CTS.v.gz             # 时钟树综合阶段网表文件
  ├── gcd_route.def.gz         # 布线阶段物理设计文件
  └── gcd_route.v.gz           # 布线阶段网表文件
  ```

#### 2.2 data目录 - 中间处理数据

存储EDA工具在各个处理阶段生成的详细中间数据，按流程阶段进一步分类：

- **主要子目录**：
  - `pl/`：布局阶段数据
  - `cts/`：时钟树综合阶段数据
  - `rt/`：布线阶段数据
  - `drc/`：设计规则检查数据
  - `log/`：设计流程的运行日志

#### 2.3 feature目录 - 特征数据

存储从设计中提取的特征信息，为分析和优化提供基础。特征数据分为不同类型，反映设计的不同方面。

- **文件命名规范**：`{design_name}_{stage_name}_{feature_type}.json`
  - `feature_type`：特征类型，主要包括：
    - `summary`：宏观设计统计信息（单元数量、引脚分布等）
    - `tool`：工具内部报告的详细数据
    - `map`：二维映射数据（密度图、拥塞图等）、性能指标数据
    - `drc`：设计规则检查结果

- **二维特征图**：
  - `density_map/`：密度分布映射
  - `egr_congestion_map/`：早期布线拥塞图
  - `margin_map/`：宏单元margin映射
  - `RUDY_map/`：布线需求分布映射

#### 2.4 vectors目录 - 向量化数据

将复杂的芯片设计拆解为结构化、可计算的数据表示，是AI驱动优化的基础。我们将这些结构化数据称为Foundation Data，也称为向量化数据。这些结构化数据以JSON形式呈现，保存在vectors目录下。

具体地，AiEDA对结果文件（.def）实现Design-to-Vector的方法学，将芯片设计（design）按照逻辑网表（netlist）和几何版图（layout）进行逐层拆解。逻辑网表又可以拆解为net、path、graph等不同层级的表示，几何版图又可以拆解为逐个patch的信息。这些拆解后的信息最终汇总到基于更细粒度的表示如wire、polygon。此外，AiEDA也对工艺信息如布线层、通孔（.lef）进行向量化表示（library-to-vector）。

- **主要向量化数据类型**：
  - `tech/`：工艺信息向量化（tech.json、cells.json）
  - `instances/`：单元实例信息向量化 （instances.json）
  - `nets/`：线网信息向量化 (net_i.json)
  - `patchs/`：版图区域划分向量化 (patch_i.json)
  - `wire_graph/`：网表图结构向量化 (timing_wire_graph.json)
  - `wire_paths/`：布线路径向量化 （wire_path_i.json）
  - `instance_graph/`：单元实例连接图向量化 （timing_instance_graph.json）

**这些向量化数据的具体含义，在下文中会有专门的小节进行详细介绍。**

#### 2.5 rpt目录 - 报告文件

存储AiEDA的report模块生成的各类报告文件，用于分析和验证设计质量。

### 3. 数据流转机制

在AiEDA框架中，数据在不同工具和阶段之间按照以下流程流转：

1. **输入处理**：从设计文件（DEF、Verilog等）读取初始数据
2. **阶段处理**：各EDA工具阶段（floorplan、place、route等）处理数据
3. **结果生成**：生成result目录中的最终结果文件
4. **特征提取**：提取特征数据到feature目录
5. **向量化转换**：将设计转换为向量化数据存储在vectors目录
6. **分析报告**：生成分析报告到rpt目录

### 4. 输出管理最佳实践

- **数据共享**：通过Workspace API访问输出数据，避免直接文件操作
- **性能优化**：出于直观理解数据的目的，目前展示的向量化数据（net和patch）都为分立文件，即一个文件对应一个net或者patch。对于大数据量操作，数据可以改用批量存储和批处理，例如一个文件存储批量的net或patch（例如net_0_678.json一个文件存储有679个net）。AiEDA同时支持分立文件（如net_0.json, net_1.json, ..., net_678.json）和聚合文件（net_0_678.json）的生成和访问。


## Foundation Data：Net
- 示例文件路径：`example/sky130_gcd/output/iEDA/vectors/nets/net_0.json`
- 数据生成机制：
  - 通过`Vectorization::buildFeature`函数调用`buildLayoutData`和`buildGraphData`构建基础数据
  - 调用`generateFeature`生成线网特征，包括时序特征、DRC特征和统计特征
  - 最后通过`_data_manager.saveData`保存数据，其中Net数据通过`VecLayoutFileIO::saveJsonNets`方法保存到nets目录
  - 支持批处理模式，可根据`batch_mode`参数决定一个文件保存单个或多个线网

- 数据结构示例：
  ```json
  {
    "id": 0,
    "name": "线网名称",
    "feature": {
      "llx": 79680,
      "lly": 68880,
      "urx": 82320,
      "ury": 74880,
      "wire_len": 11040,
      "via_num": 6,
      "drc_num": 0,
      "drc_type": [],
      "R": 19.71428571428571,
      "C": 0.0034665075873600007,
      "power": 1.1747088838172315e-07,
      "delay": 0.029491537147148576,
      "slew": 0.009644028041781348,
      "aspect_ratio": 2,
      "width": 2640,
      "height": 6000,
      "area": 15840000,
      "volume": 31680000,
      "layer_ratio": [0.0, 0.0, 0.2800000011920929, ...],
      "place_feature": {
        "pin_num": 2,
        "aspect_ratio": 2,
        "width": 2195,
        "height": 3507,
        "area": 7697865,
        "l_ness": 1.0,
        "hpwl": 5702,
        "rsmt": 5702
      }
    },
    "pin_num": 2,
    "pins": [
      {
        "id": 0,
        "i": "单元实例名称",
        "p": "引脚名称",
        "driver": 1
      }
    ],
    "wire_num": 11,
    "wires": [
      {
        "id": 0,
        "feature": {
                "wire_width": 140,
                "wire_len": 960,
                "wire_density": null,
                "drc_num": 0,
                "R": 0.8571428571428577,
                "C": 4.6356008480000124e-05,
                "power": 8.727133642824888e-07,
                "delay": 0.0022083051501257146,
                "slew": 6.621690001873404e-11,
                "congestion": 4.5,
                "drc_type": []
        },
        "wire": {
                "id1": 742163,
                "x1": 81360,
                "y1": 74880,
                "real_x1": 81360,
                "real_y1": 75055,
                "r1": 312,
                "c1": 339,
                "l1": 2,
                "p1": -1,
                "id2": 1316755,
                "x2": 81360,
                "y2": 74880,
                "real_x2": 81360,
                "real_y2": 75055,
                "r2": 312,
                "c2": 339,
                "l2": 4,
                "p2": -1,
                "via": 5
          },
        "path_num": 1,
        "paths": [
          {
                    "id1": 742163,
                    "x1": 81360,
                    "y1": 74880,
                    "real_x1": 81360,
                    "real_y1": 75055,
                    "r1": 312,
                    "c1": 339,
                    "l1": 2,
                    "p1": -1,
                    "id2": 1316755,
                    "x2": 81360,
                    "y2": 74880,
                    "real_x2": 81360,
                    "real_y2": 75055,
                    "r2": 312,
                    "c2": 339,
                    "l2": 4,
                    "p2": -1,
                    "via": 5
          }
        ],
        "patch_num": 2,
        "patchs": [528, 529]
      }
    ],
    "routing_graph": {
      "vertices": [
            {
                "id": 0,
                "is_pin": 0,
                "is_driver_pin": 0,
                "x": 81360,
                "y": 75055,
                "layer_id": 2
            },
      ],
      "edges": [
            {
                "source_id": 0,
                "target_id": 1,
                "path": [
                    {
                        "x": 81360,
                        "y": 75055,
                        "layer_id": 2
                    },
                    {
                        "x": 82320,
                        "y": 75055,
                        "layer_id": 2
                    }
                ]
            },
      ]
    }
  }
  ```

- 字段说明：

  | 字段名 | 数据类型 | 描述 | 单位 | 示例值 |
  | :---| :--- | :--- | :--- | :--- |
  | id | Integer | 线网唯一标识符 | - | 0 |
  | name | String | 线网名称 | - | "ctrl$a_mux_sel[0]" |
  | feature | Object | 线网特征集合 | - | - |
  | feature.llx | Integer | 线网包围盒左下角x坐标，取polygon最左值 | 数据库单位 | 79680 |
  | feature.lly | Integer | 线网包围盒左下角y坐标，取polygon最下值 | 数据库单位 | 68880 |
  | feature.urx | Integer | 线网包围盒右上角x坐标，取polygon最右值 | 数据库单位 | 82320 |
  | feature.ury | Integer | 线网包围盒右上角y坐标，取polygon最上值 | 数据库单位 | 74880 |
  | feature.wire_len | Integer | 线网总线段长度 | 数据库单位 | 11040 |
  | feature.via_num | Integer | 通孔数量 | 个 | 6 |
  | feature.drc_num | Integer | DRC违规数量 | 个 | 0 |
  | feature.drc_type | Array | DRC违规类型列表 | - | [] |
  | feature.R | Float | 线网总电阻 | 欧姆 | 19.714 |
  | feature.C | Float | 线网总电容 | 皮法 | 0.003467 |
  | feature.power | Float | 线网总功耗 | 瓦特 | 1.1747e-07 |
  | feature.delay | Float | 线网总时延 | 纳秒 | 0.02949 |
  | feature.slew | Float | 信号转换时间 | 纳秒 | 0.009644 |
  | feature.aspect_ratio | Float | 包围盒长宽比 | - | 2.0 |
  | feature.width | Integer | 包围盒宽度 | 数据库单位 | 2640 |
  | feature.height | Integer | 包围盒高度 | 数据库单位 | 6000 |
  | feature.area | Integer | 包围盒面积 | 平方数据库单位 | 15840000 |
  | feature.volume | Integer | 包围盒三维体积 | 立方数据库单位 | 31680000 |
  | feature.layer_ratio | Array | 自下而上各层线长分布比例 | - | [0.0, 0.0, 0.2800000011920929, ...] |
  | feature.place_feature | Object | 布局阶段特征 | - | - |
  | feature.place_feature.pin_num | Integer | 线网连接的引脚数量 | 个 | 2 |
  | feature.place_feature.aspect_ratio | Float | 线网包围盒的长宽比，取pin中心点计算 | - | 2.0 |
  | feature.place_feature.width | Integer | 引脚布局包围盒的宽度，取pin中心点计算 | 数据库单位 | 2195 |
  | feature.place_feature.height | Integer | 引脚布局包围盒的高度，取pin中心点计算 | 数据库单位 | 3507 |
  | feature.place_feature.area | Integer | 引脚布局包围盒的面积，取pin中心点计算 | 平方数据库单位 | 7697865 |
  | feature.place_feature.l_ness | Float | 引脚分布，源自A.B Kahang论文《Wot the L》 | - | 1.0 |
  | feature.place_feature.hpwl | Integer | 半周长线长，取pin中心点计算 | 数据库单位 | 5702 |
  | feature.place_feature.rsmt | Integer | 矩形斯坦纳最小树长度，取pin中心点计算 | 数据库单位 | 5702 |
  | pin_num | Integer | 引脚数量 | 个 | 2 |
  | pins | Array | 引脚列表 | - | - |
  | pins[].id | Integer | 引脚ID | - | 0 |
  | pins[].i | String | 引脚所属实例名称 | - | "ctrl/_34_" |
  | pins[].p | String | 引脚名称 | - | "X" |
  | pins[].driver | Integer | 是否为驱动引脚(1:是, 0:否) | - | 1 |
  | wire_num | Integer | 线段数量 | 个 | 11 |
  | wires | Array | 线段列表 | - | - |
  | wires[].id | Integer | 线段ID | - | 0 |
  | wires[].feature | Object | 线段特征 | - | - |
  | wires[].feature.wire_width | Integer | 线段宽度 | 数据库单位 | 140 |
  | wires[].feature.wire_len | Integer | 线段长度 | 数据库单位 | 960 |
  | wires[].feature.wire_density | Float | 线段密度 | - | 0.1 |
  | wires[].feature.drc_num | Integer | 线段DRC违规数量 | 个 | 0 |
  | wires[].feature.R | Float | 线段电阻 | 欧姆 | 0.8571 |
  | wires[].feature.C | Float | 线段电容 | 皮法 | 4.6356e-05 |
  | wires[].feature.power | Float | 线段功耗 | 瓦特 | 8.7271e-07 |
  | wires[].feature.delay | Float | 线段时延 | 纳秒 | 0.002208 |
  | wires[].feature.slew | Float | 线段信号转换时间 | 纳秒 | 6.6217e-11 |
  | wires[].feature.congestion | Float | 线段所在区域的拥塞度（demand-supply） | - | 4 |
  | wires[].feature.drc_type | Array | 线段DRC违规类型列表 | - | [] |
  | wires[].wire | Object | 线段节点信息，两点之间不一定为曼哈顿连线 | - | - |
  | wires[].wire.id1 | Integer | 起点节点ID | - | 742163 |
  | wires[].wire.x1 | Integer | 起点x网格化坐标 | 数据库单位 | 81360 |
  | wires[].wire.y1 | Integer | 起点y网格化坐标 | 数据库单位 | 74880 |
  | wires[].wire.real_x1 | Integer | 实际起点x坐标 | 数据库单位 | 81360 |
  | wires[].wire.real_y1 | Integer | 实际起点y坐标 | 数据库单位 | 75055 |
  | wires[].wire.r1 | Integer | 起点所在行号 | - | 312 |
  | wires[].wire.c1 | Integer | 起点所在列号 | - | 339 |
  | wires[].wire.l1 | Integer | 起点所在金属层 | - | 2 |
  | wires[].wire.p1 | Integer | 起点对应真实pin的编号，非真实pin则记为-1 | - | -1 |
  | wires[].wire.id2 | Integer | 终点节点ID | - | 742167 |
  | wires[].wire.x2 | Integer | 终点x网格化坐标 | 数据库单位 | 82320 |
  | wires[].wire.y2 | Integer | 终点y网格化坐标 | 数据库单位 | 74880 |
  | wires[].wire.real_x2 | Integer | 实际终点x坐标 | 数据库单位 | 82320 |
  | wires[].wire.real_y2 | Integer | 实际终点y坐标 | 数据库单位 | 75055 |
  | wires[].wire.r2 | Integer | 终点所在行号 | - | 312 |
  | wires[].wire.c2 | Integer | 终点所在列号 | - | 343 |
  | wires[].wire.l2 | Integer | 终点所在金属层 | - | 2 |
  | wires[].wire.p2 | Integer | 终点对应真实pin的编号，非真实pin则记为-1 | - | -1 |
  | wires[].path_num | Integer | Wire拆解为曼哈顿路径数量 | 个 | 1 |
  | wires[].paths | Array | Wire拆解为曼哈顿路径信息 | - | - |
  | wires[].patch_num | Integer | 经过的patch数量 | 个 | 2 |
  | wires[].patchs | Array | 经过的patch ID列表 | - | [528, 529] |
  | routing_graph | Object | 布线图结构，用于表示线网的图论模型 | - | - |
  | routing_graph.vertices | Array | 图顶点列表，包含布线图中的所有节点 | - | - |
  | routing_graph.vertices[].id | Integer | 顶点唯一标识符 | - | 0 |
  | routing_graph.vertices[].is_pin | Integer | 是否为引脚(1:是, 0:否) | - | 0 |
  | routing_graph.vertices[].is_driver_pin | Integer | 是否为驱动引脚(1:是, 0:否) | - | 0 |
  | routing_graph.vertices[].x | Integer | 顶点x坐标 | 数据库单位 | 81360 |
  | routing_graph.vertices[].y | Integer | 顶点y坐标 | 数据库单位 | 75055 |
  | routing_graph.vertices[].layer_id | Integer | 顶点所在金属层ID | - | 2 |
  | routing_graph.edges | Array | 图边列表，表示顶点间的连接关系 | - | - |
  | routing_graph.edges[].source_id | Integer | 边的起始顶点ID | - | 0 |
  | routing_graph.edges[].target_id | Integer | 边的目标顶点ID | - | 1 |
  | routing_graph.edges[].path | Array | 边上的路径点列表，表示实际布线路径 | - | - |
  | routing_graph.edges[].path[].x | Integer | 路径点x坐标 | 数据库单位 | 81360 |
  | routing_graph.edges[].path[].y | Integer | 路径点y坐标 | 数据库单位 | 75055 |
  | routing_graph.edges[].path[].layer_id | Integer | 路径点所在金属层ID | - | 2 |

- 数据用途：
  1. 提供线网的几何和电气特性，用于物理设计分析
  2. 支持时序分析，包含电阻、电容、延迟和转换时间等关键参数
  3. 用于DRC检查和违规分析
  4. 功耗估算和优化
  5. 布线密度和拥塞分析
  6. 为机器学习模型提供训练数据，用于预测线网性能

- 数据特点：
  1. 包含多层次的线网信息，从宏观包围盒到微观线段细节
  2. 融合了几何、电气和时序特性
  3. 支持布局和布线阶段的特征分析
  4. 以JSON格式存储，便于解析和处理
  5. 提供完整的布线图结构，便于图形分析和算法优化

## Foundation Data：Path
- 示例文件路径："example/sky130_gcd/output/iEDA/vectors/wire_paths/wire_path_1.json"

- 数据生成机制:
  - 首先通过`buildLayoutData`和`buildGraphData`构建基础数据
  - 调用`VecFeature`类的`buildFeatureTiming`方法进行时序特征提取
  - 调用`eval_tp->runVecSTA()`执行详细的时序分析
  - 具体由`reportWirePaths()`函数生成详细的路径数据，该函数遍历时序图中的路径
  - 最后通过文件I/O操作将数据保存为JSON格式到wire_paths目录

- 数据结构示例：
Path数据采用JSON数组格式，按时序顺序组织路径中的各个节点和延迟弧。数组中的每个元素都是一个JSON对象，代表路径中的一个元素（节点或弧）。

  ```json
  [
    {
      "node_0": {
        "Point": "dpath/b_reg/_147_:CLK (sky130_fd_sc_hs__dfxtp_1)",
        "Capacitance": 0.003,
        "slew": 0.0,
        "trans_type": "rise"
      }
    },
    {
      "inst_arc_0": {
        "Incr": 0.238
      }
    },
    {
      "node_1": {
          "Point": "dpath/b_reg/_147_:Q (sky130_fd_sc_hs__dfxtp_1)",
          "Capacitance": 0.018471882955040004,
          "slew": 0.134413,
          "trans_type": "rise"
      }
    },
    {
      "net_arc_1": {
          "Incr": 0.000476,
          "edge_0": {
              "wire_from_node": "dpath/b_reg/_147_:Q",
              "wire_to_node": "dpath/a_lt_b$in1[15]:847926",
              "wire_R": 0.0,
              "wire_C": 0.0,
              "from_slew": 0.134413,
              "to_slew": 0.134413,
              "wire_delay": 0.0
          },
          // 更多边...
    // 更多节点和弧...
  ]
  ```

- 字段说明:

  | 字段类型 | 字段名 | 数据类型 | 描述 | 单位 | 示例值 |
  | :--- | :----| :--- | :--- | :--- | :--- |
  | **节点信息** | node_* | Object | 路径上的实例引脚或内部节点 | - | - |
  | | node_*.Point | String | 节点位置信息，格式为"实例名:引脚名 (单元类型)" | - | "dpath/b_reg/_147_:CLK (sky130_fd_sc_hs__dfxtp_1)" |
  | | node_*.Capacitance | Float | 节点电容值 | pF | 0.003 |
  | | node_*.slew | Float | 节点信号转换时间 | ns | 0.134413 |
  | | node_*.trans_type | String | 信号转换类型 | - | "rise"或"fall" |
  | **实例延迟弧** | inst_arc_* | Object | 实例内部延迟弧，代表单元内部传播延迟 | - | - |
  | | inst_arc_*.Incr | Float | 实例内部延迟增量 | ns | 0.238 |
  | **线网延迟弧** | net_arc_* | Object | 线网延迟弧，代表线网上的信号传播延迟 | - | - |
  | | net_arc_\*.Incr | Float | 线网总延迟增量 | ns | 0.000476 |
  | | net_arc_\*.edge_\* | Object | 线网中的具体线段信息 | - | - |
  | | net_arc_\*.edge_\*.wire_from_node | String | 线段起始节点名称 | - | "dpath/b_reg/_147_:Q" |
  | | net_arc_\*.edge_\*.wire_to_node | String | 线段终止节点名称 | - | "dpath/a_lt_b$in1[15]:847926" |
  | | net_arc_\*.edge_\*.wire_R | Float | 线段电阻值 | Ω | 0.642857 |
  | | net_arc_\*.edge_\*.wire_C | Float | 线段电容值 | pF | 3.618685e-05 |
  | | net_arc_\*.edge_\*.from_slew | Float | 线段起始端信号转换时间 | ns | 0.134413 |
  | | net_arc_\*.edge_\*.to_slew | Float | 线段终止端信号转换时间 | ns | 0.134413033744 |
  | | net_arc_\*.edge_\*.wire_delay | Float | 线段带来的延迟 | ns | 1.18515e-05 |

- 数据用途:
  1. **时序分析**：提供详细的路径延迟信息，用于分析和优化设计的时序性能
  2. **信号完整性评估**：包含信号转换时间和线网RC参数，支持信号完整性分析
  3. **功耗分析**：基于节点电容和转换率，可计算动态功耗
  4. **路径可视化**：数据结构便于路径的图形化展示和分析
  5. **时序收敛验证**：用于验证设计是否满足时序约束
  6. **机器学习模型训练**：为预测路径延迟、信号完整性等问题提供训练数据

- 数据特点:
  1. **时序顺序**：数组中的元素严格按照信号传播的时间顺序排列
  2. **交替结构**：节点(node_\*)和弧(inst_arc_\*/net_arc_\*)交替出现，形成完整路径
  3. **递增ID**：节点和弧的ID按照路径顺序递增，便于追踪信号流
  4. **层级细节**：线网弧中嵌套详细的线段信息(edge_\*)，提供细粒度的互连特性


## Foundation Data：Graph

- 示例文件路径：`./example/sky130_gcd/output/iEDA/vectors/wire_graph/timing_wire_graph.json`

- 数据生成机制:
  - **数据准备**：在`Vectorization::buildFeature`方法中，首先调用`_data_manager.buildLayoutData()`构建版图数据，然后通过`_data_manager.buildGraphData()`构建初始图数据结构。
  - **特征提取**：调用`generateFeature()`方法创建`VecFeature`对象，并通过`feature.buildFeatureTiming()`生成时序相关特征。
  - **时序分析**：通过`runVecSTA`方法（在`InitSTA::getInst()`实例上调用`eval_tp->runVecSTA()`）执行详细的时序分析，计算节点的到达时间、要求时间等关键参数。
  - **数据保存**：最终通过`_data_manager.saveData()`方法将生成的Graph数据保存为JSON格式文件。

- 数据结构示例：Graph数据以JSON格式组织，采用标准图数据结构表示芯片设计中的线网连接关系。
  ```json
  {
      "nodes": [ // 节点数组，表示引脚、端口和布线节点
        {
            "id": "node_0",
            "name": "clk",
            "is_pin": false,
            "is_port": true,
            "node_feature": {
                "is_input": true,
                "fanout_num": 1,
                "is_endpoint": false,
                "cell_name": "NA",
                "sizer_cells": [],
                "node_coord": [
                    0.0,
                    0.0
                ],
                "node_slews": [
                    0.0,
                    0.0,
                    0.0,
                    0.0
                ],
                "node_capacitances": [
                    0.0,
                    0.0,
                    0.0,
                    0.0
                ],
                "node_arrive_times": [
                    1.1e+20,
                    1.1e+20,
                    1.1e+20,
                    1.1e+20
                ],
                "node_required_times": [
                    1.1e+20,
                    1.1e+20,
                    1.1e+20,
                    1.1e+20
                ],
                "node_net_load_delays": [
                    0.0,
                    0.0,
                    0.0,
                    0.0
                ],
                "node_toggle": 1.0,
                "node_sp": 0.5,
                "node_internal_power": 0.0,
                "node_net_power": 2.8232123814158402e-05
            }
        },
        //更多节点 ... 
      ],  
      "edges": [ // 边数组，表示节点间的连接关系
        {
            "id": "edge_0",
            "from_node": 510,
            "to_node": 746,
            "is_net_edge": false,
            "edge_feature": {
                "edge_delay": [
                    0.088476,
                    0.051862,
                    0.088476,
                    0.051862
                ],
                "edge_resistance": 0.0,
                "inst_arc_internal_power": 0.00011665750115296025
            }
        },
        // 更多边 ... 
      ]   
  }
  ```


- 字段说明：
  - 节点（nodes）：每个节点代表芯片设计中的一个连接点，可能是单元引脚、端口或布线节点。
    | 字段名 | 数据类型 | 描述 | 单位 | 示例值 |
    | :--- | :--- | :--- | :--- | :--- |
    | `id` | string | 节点唯一标识符 | - | "node_4" |
    | `name` | string | 节点名称，通常包含实例名和引脚名 | - | "clk_0_buf:X" |
    | `is_pin` | boolean | 是否为单元引脚 | - | true |
    | `is_port` | boolean | 是否为芯片端口 | - | false |
    | `node_feature` | object | 节点特征属性集合，包含时序和功耗信息 | - | - |
  - 节点特征（`node_feature`）：
    | 字段名 | 数据类型 | 描述 | 单位 | 示例值 |
    | :--- | :--- | :--- | :--- | :--- |
    | `is_input` | boolean | 是否为输入节点（相对于单元） | - | false |
    | `fanout_num` | integer | 扇出数量，表示该节点驱动的负载数量 | - | 17 |
    | `is_endpoint` | boolean | 是否为时序路径的端点 | - | false |
    | `cell_name` | string | 单元名称，如果节点属于单元引脚 | - | "sky130_fd_sc_hs__buf_1" |
    | `sizer_cells` | array[string] | 可替换单元列表，用于单元尺寸优化 | - | ["sky130_fd_sc_hs__buf_16", "sky130_fd_sc_hs__buf_4", "sky130_fd_sc_hs__buf_8"] |
    | `node_coord` | array[float] | 节点坐标(x, y) | 数据库单位 | [57.842, 61.732] |
    | `node_slews` | array[float] | 节点转换时间，包含四个工艺角的数值 | ns | [0.0, 0.0, 0.0, 0.0] |
    | `node_capacitances` | array[float] | 节点电容值，包含四个工艺角的数值 | pF | [0.0, 0.0, 0.0, 0.0] |
    | `node_arrive_times` | array[float] | 节点信号到达时间，包含四个工艺角的数值 | ns | [1.1e+20, 1.1e+20, 1.1e+20, 1.1e+20] |
    | `node_required_times` | array[float] | 节点要求到达时间，包含四个工艺角的数值 | ns | [1.1e+20, 1.1e+20, 1.1e+20, 1.1e+20] |
    | `node_net_load_delays` | array[float] | 节点线网负载延迟，包含四个工艺角的数值 | ns | [0.0, 0.0, 0.0, 0.0] |
    | `node_toggle` | float | 节点翻转率，表示信号在单位时间内的翻转次数 | - | 1.0 |
    | `node_sp` | float | 信号概率，表示信号为高电平的概率 | - | 0.5 |
    | `node_internal_power` | float | 节点内部功耗，主要是单元内部功耗 | W | 0.0 |
    | `node_net_power` | float | 节点线网功耗，主要是线网上的动态功耗 | W | 0.0001290105577302048 |

  - 边（edges）：每条边代表两个节点之间的连接关系，可能是单元内部连接或线网连接。
    | 字段名 | 数据类型 | 描述 | 单位 | 示例值 |
    | :--- | :--- | :--- | :--- | :--- |
    | `id` | string | 边唯一标识符 | - | "edge_7960" |
    | `from_node` | integer | 起始节点ID（对应nodes数组中的索引） | - | 7586 |
    | `to_node` | integer | 终止节点ID（对应nodes数组中的索引） | - | 7587 |
    | `is_net_edge` | boolean | 是否为线网边（true表示线网连接，false表示单元内部连接） | - | true |
    | `edge_feature` | object | 边特征属性集合，包含延迟和功耗信息 | - | - |

  - 边特征（`edge_feature`）：
    | 字段名 | 数据类型 | 描述 | 单位 | 示例值 |
    | :--- | :--- | :--- | :--- | :--- |
    | `edge_delay` | array[float] | 边延迟值，包含四个工艺角的数值 | ns | [0.0, 0.0, 0.0, 0.0] |
    | `edge_resistance` | float | 边电阻值，主要用于线网边 | 欧姆 | 18.428571428571427 |
    | `inst_arc_internal_power` | float | 实例弧内部功耗，主要用于单元内部边 | W | 0.0 |

- 数据用途：
  1. **时序分析**：提供完整的时序图结构，支持静态时序分析（STA）。
  2. **功耗优化**：包含详细的功耗相关参数，支持功耗分析和优化。
  3. **物理设计验证**：提供了物理实现与逻辑设计之间的连接关系，支持设计验证。
  4. **机器学习特征提取**：为机器学习模型提供结构化的芯片设计特征数据，支持预测和优化任务。
  5. **设计可视化**：支持将芯片设计转换为可视化的图结构，便于理解和分析。

- 数据特点：
  1. **时序分析支持**：Graph数据包含完整的时序相关信息，支持静态时序分析（STA）相关的计算和验证。
  2. **工艺角覆盖**：关键参数（如延迟、翻转率等）包含四个工艺角的数值，支持全工艺角分析。
  3. **层次化结构**：数据按照图论中的节点和边进行组织，清晰地表达了芯片设计中的连接关系。
  4. **多维度特征**：每个节点和边都包含时序、功耗、几何位置等多维度特征，支持综合分析和优化。

## Foundation Data：Patch

- 示例文件路径：`./example/sky130_gcd/output/iEDA/vectors/patchs/patch_0.json`

- 数据生成机制：
  1. `Vectorization::buildFeature`函数调用`buildPatchData`方法构建Patch数据
  2. 数据生成过程通过`VecDataManager`管理，由`VecPatchDataManager`具体实现
  3. `VecPatchInit`负责初始化Patch网格并填充线网和线段信息
  4. 最终通过`VecLayoutFileIO::saveJsonPatchs`将数据保存为JSON文件

- 数据结构示例：
  ```json
  {
      "id": 0,
      "patch_id_row": 0,
      "patch_id_col": 0,
      "llx": 0,
      "lly": 0,
      "urx": 4320,
      "ury": 4320,
      "row_min": 0,
      "row_max": 18,
      "col_min": 0,
      "col_max": 18,
      "cell_density": 0.8981481481481481,
      "pin_density": 40,
      "net_density": 0.12371399176954732,
      "macro_margin": 255180,
      "RUDY_congestion": 0.00029195559407049423,
      "EGR_congestion": 3.0,
      "timing": 0.0,
      "power": 3.2690654345212375e-07,
      "IR_drop": 0.0,
      "sub_nets": [
          {
              "id": 626,
              "llx": 1000,
              "lly": 0,
              "urx": 4320,
              "ury": 4320
          },
          // 更多子线网 ...
      ],
      "patch_layer": [
          {
            "id": 4,
            "feature": {
                "wire_width": 140,
                "wire_len": 3120,
                "wire_density": 0.023405349794238684,
                "congestion": 2.0
            },
            "net_num": 1,
            "nets": [
              {
                "id": 650,
                "wire_num": 2,
                "wires": [
                    {
                        "id": 6600,
                        "feature": {
                            "wire_len": 3120
                        },
                        "path_num": 1,
                        "paths": [
                            {
                                "id1": 1151867,
                                "x1": 720,
                                "y1": 1200,
                                "real_x1": 720,
                                "real_y1": 1200,
                                "r1": 5,
                                "c1": 3,
                                "l1": 4,
                                "p1": -1,
                                "id2": 1158835,
                                "x2": 720,
                                "y2": 4320,
                                "real_x2": -1,
                                "real_y2": -1,
                                "r2": 18,
                                "c2": 3,
                                "l2": 4,
                                "p2": -1
                            }
                        ]
                    },
                    // 更多线段...
                  ]
              } 
            ]
          },
          // 更多patch_layer...
      ]
  }
  ```


- 字段说明：
  - 全局信息
    | 字段名 | 数据类型 | 描述 | 单位 | 示例值 |
    | :--- | :--- | :--- | :--- | :--- |
    | `id` | 整型 | patch唯一标识符，格式为整数序号 | - | 0 |
    | `patch_id_row` | 整型 | patch在网格中的行索引 | - | 0 |
    | `patch_id_col` | 整型 | patch在网格中的列索引 | - | 0 |
    | `llx` | 整型 | patch左下角x坐标 | 数据库单位 | 0 |
    | `lly` | 整型 | patch左下角y坐标 | 数据库单位 | 0 |
    | `urx` | 整型 | patch右上角x坐标 | 数据库单位 | 4320 |
    | `ury` | 整型 | patch右上角y坐标 | 数据库单位 | 4320 |
    | `row_min` | 整型 | patch中节点的最小行号 | - | 0 |
    | `row_max` | 整型 | patch中节点的最大行号 | - | 18 |
    | `col_min` | 整型 | patch中节点的最小列号 | - | 0 |
    | `col_max` | 整型 | patch中节点的最大列号 | - | 18 |
    | `cell_density` | 浮点型 | patch中单元密度，取值范围[0,1] | - | 0.898148 |
    | `pin_density` | 浮点型 | patch中引脚密度 | 引脚数量 | 40 |
    | `net_density` | 浮点型 | patch中线网密度 | - | 0.123714 |
    | `macro_margin` | 整型 | patch中宏单元最大边缘距离 | 数据库单位 | 255180 |
    | `RUDY_congestion` | 浮点型 | 基于RUDY模型的拥塞评估值 | - | 0.000292 |
    | `EGR_congestion` | 浮点型 | 基于EGR模型的拥塞评估值 | - | 3.0 |
    | `timing` | 浮点型 | 时序信息 | ns | 0.0 |
    | `power` | 浮点型 | 功耗信息 | W | 3.26907e-07 |
    | `IR_drop` | 浮点型 | IR降信息 | V | 0.0 |
    | `sub_nets` | 数组 | patch中包含的子网信息 | - | [子网对象数组] |
    | `patch_layer` | 数组 | patch的各层详细信息 | - | [层对象数组] |

  - 子网信息（sub_nets）：`sub_nets` 数组中的每个元素是一个子网，定义了线网与patch的重叠区域，如下：
    | 字段名 | 数据类型 | 描述 | 单位 | 示例值 |
    | :--- | :--- | :--- | :--- | :--- |
    | `id` | 整型 | 子网唯一标识符 | - | 626 |
    | `llx` | 整型 | 子网左下角x坐标 | 数据库单位 | 1000 |
    | `lly` | 整型 | 子网左下角y坐标 | 数据库单位 | 0 |
    | `urx` | 整型 | 子网右上角x坐标 | 数据库单位 | 4320 |
    | `ury` | 整型 | 子网右上角y坐标 | 数据库单位 | 4320 |

  - 层信息（patch_layer）：`patch_layer` 数组中的每个元素表示patch中的每个层，定义如下：
    | 字段名 | 数据类型 | 描述 | 单位 | 示例值 |
    | :--- | :--- | :--- | :--- | :--- |
    | `id` | 整型 | 层ID，对应物理设计中的金属层 | - | 4 |
    | `feature` | 对象 | 层特征信息 | - | 见下表 |
    | `net_num` | 整型 | 层中包含的线网数量 | - | 1 |
    | `nets` | 数组 | 层中的线网列表 | - | [线网对象数组] |

  - 层特征（feature）
    | 字段名 | 数据类型 | 描述 | 单位 | 示例值 |
    | :--- | :--- | :--- | :--- | :--- |
    | `wire_width` | 整型 | 线段宽度 | 数据库单位 | 140 |
    | `wire_len` | 整型 | 线段总长度 | 数据库单位 | 3120 |
    | `wire_density` | 浮点型 | 线密度 | - | 0.023405 |
    | `congestion` | 浮点型 | 该层拥塞程度 | - | 2.0 |

  - 线网信息（nets）：`nets` 数组中的每个元素表示一个线网，定义如下：
    | 字段名 | 数据类型 | 描述 | 单位 | 示例值 |
    | :--- | :--- | :--- | :--- | :--- |
    | `id` | 整型 | 线网唯一标识符 | - | 650 |
    | `wire_num` | 整型 | 线网中的导线数量 | - | 2 |
    | `wires` | 数组 | 导线列表 | - | [导线对象数组] |

  - 线段信息（wires）：`wires` 数组中的每个元素表示一段导线，定义如下：
    | 字段名 | 数据类型 | 描述 | 单位 | 示例值 |
    | :--- | :--- | :--- | :--- | :--- |
    | `id` | 整型 | 导线唯一标识符 | - | 6600 |
    | `feature` | 对象 | 导线特征信息 | - | {"wire_len": 3120} |
    | `path_num` | 整型 | 导线包含的路径数量 | - | 1 |
    | `paths` | 数组 | 路径列表 | - | [路径对象数组] |

  - 路径信息（paths）：`paths` 数组中的每个元素表示导线的一段路径，定义如下：
    | 字段名 | 数据类型 | 描述 | 单位 | 示例值 |
    | :--- | :--- | :--- | :--- | :--- |
    | `id1` | 整型 | 起始点唯一标识符 | - | 1151867 |
    | `x1`, `y1` | 整型 | 起始点网格点坐标 | 数据库单位 | 720, 1200 |
    | `real_x1`, `real_y1` | 整型 | 起始点实际物理坐标 | 数据库单位 | 720, 1200 |
    | `r1`, `c1` | 整型 | 起始点所在网格行列 | - | 5, 3 |
    | `l1` | 整型 | 起始点所在层ID | - | 4 |
    | `p1` | 整型 | 起始点引脚索引（-1表示非真实引脚） | - | -1 |
    | `id2` | 整型 | 终止点唯一标识符 | - | 1158835 |
    | `x2`, `y2` | 整型 | 终止点网格点坐标 | 数据库单位 | 720, 4320 |
    | `real_x2`, `real_y2` | 整型 | 终止点实际物理坐标 | 数据库单位 | 720, 4320 |
    | `r2`, `c2` | 整型 | 终止点所在网格行列 | - | 18, 3 |
    | `l2` | 整型 | 终止点所在层ID | - | 4 |
    | `p2` | 整型 | 终止点引脚索引（-1表示非真实引脚） | - | -1 |
    | `via` | 整型 | 通孔ID（可选，仅在跨层连接时存在） | - | 10（通孔编号）

- 数据用途：
  1. **物理布局分析**：提供芯片设计中不同区域的详细物理特性，支持设计人员进行宏观布局评估
  2. **版图可视化**：数据结构便于版图区域的图形化展示和分析
  3. **性能优化指导**：基于路径信息和电气特性，为时序性能优化提供详细的物理基础数据
  4. **AI模型训练数据**：为深度学习模型提供结构化的物理设计特征数据，支持布线预测、拥塞分析等AI任务


- 数据特点：
  1. Patch数据按物理设计区域划分为网格状的patch单元
  2. 每个patch包含多个层的信息，每个层包含线网、导线和路径的详细几何和电气属性
  3. 数据组织结构从宏观到微观：patch -> layer -> net -> wire -> path
  4. 路径信息精确描述了导线上的连接点，包括坐标、所在层和网格位置

## Foundation Data：Instance

- 示例文件路径：`./example/sky130_gcd/output/iEDA/vectors/instances/instances.json`

- 数据生成机制：
  1. `Vectorization::buildFeature`函数调用`_data_manager.saveData`方法保存所有数据
  2. `saveData`方法内部调用`VecLayoutFileIO::saveJson`函数
  3. `saveJson`函数调用`saveJsonInstances`方法专门生成Instance数据
  4. 最终将数据保存为JSON格式到指定目录

- 数据结构示例：`instances.json`文件采用以下结构：

  ```json
  {
    "instance_num": 1448, // 总实例数目
    "instances": [
      {
        "id":0,
        "cell_id":236,
        "name":"ctrl/_17_",
        "cx":78480,
        "cy":61605,
        "width":1440,
        "height":3330,
        "llx":77760,
        "lly":59940,
        "urx":79200,
        "ury":63270
        },
      //更多instances...
    ]
  }
  ```

- 字段说明：

  每个instance字段说明如下
  | 字段名 | 数据类型 | 描述 | 单位 | 示例值 |
  | :--- | :--- | :--- | :--- | :--- |
  | `id` | 整型 | 实例唯一标识符 | - | 1 |
  | `cell_id` | 整型 | 实例所属cell master的ID | - | 1001 |
  | `name` | 字符串 | 实例名称 | - | "sky130_fd_sc_hs__and2_1_0"
  | `cx` | 浮点型 | 实例中心点x坐标 | 数据库单位 | 1234.5
  | `cy` | 浮点型 | 实例中心点y坐标 | 数据库单位 | 5678.9
  | `width` | 浮点型 | 实例宽度 | 数据库单位 | 420.0
  | `height` | 浮点型 | 实例高度 | 数据库单位 | 180.0
  | `llx` | 浮点型 | 实例左下角x坐标 | 数据库单位 | 1024.5
  | `lly` | 浮点型 | 实例左下角y坐标 | 数据库单位 | 5588.9
  | `urx` | 浮点型 | 实例右上角x坐标 | 数据库单位 | 1444.5
  | `ury` | 浮点型 | 实例右上角y坐标 | 数据库单位 | 5768.9

- 数据用途：
  1. **物理布局表示**：实例数据精确描述了设计中每个标准单元的物理位置和尺寸
  2. **时序分析支持**：实例的位置信息是计算线长和互连延迟的基础
  3. **可布性分析**：基于实例分布评估布局质量和布线难度
  4. **AI模型训练**：为机器学习模型提供真实的物理设计实例布局数据

- 数据特点：
  1. **全面性**：包含设计中所有实例的信息，无遗漏
  2. **精确性**：坐标和尺寸信息精确到数据库单位
  3. **关联性**：通过cell_id与单元库信息关联
  4. **结构统一**：所有实例采用相同的数据结构，便于批量处理
  5. **易于扩展**：JSON格式支持添加额外的实例属性

## Foundation Data：Instance Graph

- 示例文件路径：`./example/sky130_gcd/output/iEDA/vectors/instance_graph/timing_instance_graph.json`

- 数据生成机制：
  1. `Vectorization::buildFeature`函数调用`generateFeature`方法
  2. `generateFeature`方法内部调用`VecFeature::buildFeatureTiming`函数
  3. `buildFeatureTiming`函数调用`eval_tp->getTimingInstanceGraph()`获取实例图数据
  4. 最终通过`SaveTimingInstanceGraph`函数将数据保存为JSON格式到指定目录

- 数据结构示例：

  `timing_instance_graph.json`文件采用以下结构：

  ```json
  {
    "nodes": [        
      {
        "id": "node_0",
        "name": "ctrl/_34_",
        "leakage_power": 1.6979909062047418e-10
      },
      // 更多节点...
    ],
    "edges": [
      {
        "id": "edge_0",
        "from_node": 0,
        "to_node": 1
      },
      // 更多边...
    ]
  }
  ```

- 字段说明:

  - 节点：每个节点对象代表一个实例，包含以下字段：
    | 字段名 | 数据类型 | 描述 | 单位 | 示例值 |
    | :--- | :--- | :--- | :--- | :--- |
    | `id` | 字符串 | 节点唯一标识符，格式为"node_数字" | - | "node_0" |
    | `name` | 字符串 | 实例名称 | - | "ctrl/_34_" |
    | `leakage_power` | 浮点数 | 实例的泄漏功耗 | W | 1.697e-10 |


  - 边：每条边代表两个实例之间的连接关系，包含以下字段：
    | 字段名 | 数据类型 | 描述 | 单位 | 示例值 |
    | :--- | :--- | :--- | :--- | :--- |
    | `id` | 字符串 | 边唯一标识符，格式为"edge_数字" | - | "edge_1037" |
    | `from_node` | 整型 | 驱动端节点的索引值（对应nodes数组中的索引） | - | 640 |
    | `to_node` | 整型 | 接收端节点的索引值（对应nodes数组中的索引） | - | 188 |

- 数据用途：
  1. **时序分析**：实例图提供了设计中所有实例及其连接关系，可以用于时序路径分析和延迟预测
  2. **功耗评估**：包含泄漏功耗信息，可用于整体功耗评估
  3. **物理约束研究**：反映实例之间的连接密集程度，有助于研究物理约束对设计的影响
  4. **AI模型训练**：为机器学习模型提供实例级别的连接关系和功耗数据

- 数据特点：
  1. **结构化表示**：采用图数据结构清晰地表示实例之间的连接关系
  2. **轻量级设计**：边只包含基本的连接信息，便于快速处理和分析
  3. **包含功耗信息**：每个节点包含泄漏功耗数据，便于功耗分析
  4. **全局视图**：提供了整个设计的实例连接全局视图


## Foundation Data：Cell

- 示例文件路径：`./example/sky130_gcd/output/iEDA/vectors/tech/cells.json`

- 数据生成机制：
  1. `Vectorization::buildFeature`函数调用`_data_manager.buildLayoutData`构建基础版图数据
  2. 完成数据构建后，调用`_data_manager.saveData`保存数据
  3. 在保存过程中，`VecLayoutFileIO::saveJson`方法会调用`saveJsonCells`方法
  4. `saveJsonCells`方法从`_layout->get_cells().get_cell_map()`获取单元数据，并将其保存至`cells.json`文件

- 数据结构示例：
  ```json
  {
    "cell_num": 整数,      // cell_master单元总数
    "cells": [            // 单元数组
      {
        "id": 整数,       // 单元ID
        "name": "字符串", // 单元名称
        "width": 整数,    // 单元宽度
        "height": 整数    // 单元高度
      },
      // 更多cell masters...
    ]
  }
  ```

- 字段说明：
  | 字段名 | 类型 | 描述 | 单位 | 示例值 |
  | :--- | :--- | :--- | :--- | :--- |
  | cell_num | integer | 单元库中单元的总数量 | - | 416 |
  | cells | array | 包含所有单元信息的数组 | - | [{}, ...] |
  | id | integer | 单元唯一标识符 | - | 415 |
  | name | string | 单元名称，包含工艺信息和功能描述 | - | "sky130_sram_1rw1r_44x64_8" |
  | width | integer | 单元物理宽度 | 数据库单位（例如纳米） | 445240 |
  | height | integer | 单元物理高度 | 数据库单位（例如纳米） | 237415 |

- 数据用途：
  1. **物理设计参考**：为布局布线提供标准单元和宏单元的物理尺寸信息
  2. **面积评估**：用于芯片面积计算和密度分析
  3. **功耗分析**：作为功耗计算的基础数据
  4. **时序优化**：为时序分析提供单元级参考

- 数据特点：
  1. **完整性**：包含所有可用的标准单元和宏单元信息
  2. **物理准确性**：提供精确的物理尺寸参数
  3. **工艺相关性**：数据反映特定工艺节点下的单元特性
  4. **结构化存储**：采用JSON格式，便于程序解析和处理
  5. **易于扩展**：数据结构简单明确，便于添加新的单元属性

## Foundation Data：Technology

- 示例文件路径：`./example/sky130_gcd/output/iEDA/vectors/tech/tech.json`

- 数据生成机制：
  1. `Vectorization::buildFeature`函数调用`_data_manager.buildLayoutData`构建基础版图数据
  2. 完成数据构建后，调用`_data_manager.saveData`保存数据
  3. 在保存过程中，`VecLayoutFileIO::saveJson`方法会调用`saveJsonTech`方法
  4. `saveJsonTech`方法从`_layout->get_layout_layers().get_layout_layer_map()`获取层数据，从`_layout->get_via_name_map()`获取通孔数据，并将其保存至`tech.json`文件

- 数据结构示例：
  ```json
  {
    "layer_num": 整数,  // 工艺层数
    "layers": [        // 层信息数组
      {
        "id": 整数,   // 层编号
        "name": "字符串" // 层名称
      },
      // 更多layers...
    ],
    "via_num": 整数,   // 通孔类型数量
    "vias": [          // 通孔信息数组
      {
        "id": 整数,   // 通孔编号
        "name": "字符串", // 通孔名称
        "bottom": {   // 底层金属enclosure区域坐标
          "llx": 整数,
          "lly": 整数,
          "urx": 整数,
          "ury": 整数
        },
        "cut": {      // 通孔切割区域坐标
          "llx": 整数,
          "lly": 整数,
          "urx": 整数,
          "ury": 整数
        },
        "top": {      // 顶层金属enclosure区域坐标
          "llx": 整数,
          "lly": 整数,
          "urx": 整数,
          "ury": 整数
        },
        "row": 整数,  // 通孔行数
        "col": 整数,  // 通孔列数
        "bottom_direction": "字符串", // cut相对于底层enclosure的偏置方向
        "top_direction": "字符串"     // cut相对于顶层enclosure的偏置方向
      },
      // 更多vias...
    ]
  }
  ```

- 字段说明：
  - 层信息字段
    | 字段名 | 类型 | 描述 | 单位 | 示例值 |
    | :--- | :--- | :--- | :--- | :--- |
    | layer_num | integer | 工艺中包含的总层数 | - | 11 |
    | layers | array | 所有层的详细信息数组 | - | [{}, ...] |
    | id | integer | 层的顺序编号（从底层到顶层） | - | 10 |
    | name | string | 层名称（金属层、通孔层等） | - | "met5" |

  - 通孔信息字段
    | 字段名 | 类型 | 描述 | 单位 | 示例值 |
    | :--- | :--- | :--- | :--- | :--- |
    | via_num | integer | 通孔类型的总数量 | - | 32 |
    | vias | array | 所有通孔类型的详细信息数组 | - | [{}, ...] |
    | id | integer | 通孔类型的唯一标识符 | - | 0 |
    | name | string | 通孔类型名称 | - | "L1M1_PR" |
    | bottom | object | 底层金属enclosure区域的边界框坐标 | 数据库单位 | {"llx": -85, "lly": -85, "urx": 85, "ury": 85} |
    | cut | object | 通孔切割区域的边界框坐标 | 数据库单位 | {"llx": -85, "lly": -85, "urx": 85, "ury": 85} |
    | top | object | 顶层金属enclosure区域的边界框坐标 | 数据库单位 | {"llx": -145, "lly": -115, "urx": 145, "ury": 115} |
    | row | integer | 通孔切割的行数 | - | 1 |
    | col | integer | 通孔切割的列数 | - | 1 |
    | bottom_direction | string | 底层连接方向（C-居中、N-北、S-南、E-东、W-西） | - | "C" |
    | top_direction | string | 顶层连接方向（C-居中、N-北、S-南、E-东、W-西） | - | "C" |

- 数据用途：
  1. **物理设计规则检查**：提供层和通孔的详细参数，用于验证设计是否符合工艺规则
  2. **布线指导**：作为自动布线工具的工艺约束输入
  3. **设计可视化**：为设计可视化提供准确的层和通孔表示
  4. **时序分析**：为信号完整性和时序分析提供必要的工艺参数

- 数据特点：
  1. **工艺准确性**：精确反映特定工艺节点下的层和通孔特性
  2. **完整性**：包含所有必要的物理层和通孔类型
  3. **结构化表示**：采用JSON格式，便于程序解析和处理
  4. **空间信息完整**：提供每个通孔不同部分的精确几何坐标
  5. **方向性信息**：包含通孔连接的方向性信息，有助于理解布线拓扑

