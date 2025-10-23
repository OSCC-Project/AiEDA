# Data Organization and Meaning

## Workspace Overview

### 1. Core Design Philosophy

`Workspace` is the core data management class in AiEDA, providing a unified working environment and data flow management mechanism. By encapsulating the workspace directory structure, configuration files, tool output paths, and data files, it achieves efficient integration of EDA multi-toolchains and unified data access.

### 2. Main Functions and Architecture

**Core Functional Modules:**
- Workspace creation and initialization
- Design information management
- Unified configuration file management
- Standardization of tool output paths
- Data file path acquisition interface
- Support for multi-tool engine integration

**Architectural Design:**
- The main `Workspace` class is responsible for high-level functional coordination.
- The `PathsTable` inner class handles all path management, defining the paths for various important files, including technology files, result files, analysis reports, vectorized data, etc.
- Various `Parser` implementations handle the reading, writing, and parsing of configuration files.

### 3. Directory Structure Organization

Using `sky130_gcd` as an example, the complete workspace directory structure is as follows:

```
sky130_gcd/
├── analyse/       # Analysis results directory, storing various visual analysis results for the current design.
├── config/        # Configuration file directory, storing config files for multi-tool engines and flow management.
│   ├── flow.json  # Flow configuration file.
│   ├── path.json  # Path configuration file.
│   ├── parameter.json  # Parameter configuration file.
│   ├── workspace.json  # Workspace configuration file.
│   └── iEDA_config/    # Directory for other third-party EDA tool configurations, using iEDA as an example.
├── output/        # Tool output directory, storing output files from multi-tool engines.
│   ├── DREAMPlace/  # DREAMPlace tool output.
│   ├── OpenROAD/    # OpenROAD tool output.
│   └── iEDA/        # iEDA tool output. The current open-source version only integrates iEDA, so it's used as an example.
│       ├── result/   # Raw data (.def/.v).
│       ├── data/     # Point tool output data (e.g., placement logs).
│       ├── feature/  # Stage-specific feature data (.json, .csv).
│       ├── rpt/      # Report data.
│       └── vectors/  # Vectorized base data (.json).
├── report/        # Report directory, for further organization and summarization of analysis results.
└── script/        # Script directory, storing commercial tool scripts.
```

### 4. Detailed Explanation of the `PathsTable` Inner Class

`PathsTable` is an inner class of `Workspace` that uses a property decorator pattern. It encapsulates path generation logic within methods, allowing users to obtain corresponding file paths for subsequent operations. Its main functions include:

- **Top-level Path Management**: Defines the paths for each subdirectory within the workspace directory.
- **Configuration Path Management**: Manages the paths for configuration files like `flow.json`, `path.json`, etc.
- **iEDA Configuration Management**: Manages the configuration file paths for various tools (e.g., floorplan, place, CTS, route).
- **Output Path Management**: Defines the output paths for tools at different stages.
- **Feature and Vector Path Management**: Manages file paths for feature extraction and vector data.

Note: When users need to integrate third-party tools, they can refer to the **iEDA Configuration Management** section to extend the path management.

### 5. Workflow

**Workspace Creation Workflow:**
1. Call the `create_workspace` method.
2. Create the directory structure.
3. Initialize logging.
4. Generate basic configuration files (`flow.json`, `path.json`, etc.).
5. Set design information and technology library paths.

**Data Access Workflow:**
1. Obtain paths through a `Workspace` instance.
2. Read from or write to files at the corresponding paths.
3. All tool engines use a unified interface to access data.

### 6. Key Implementation Mechanisms

**Path Management Mechanism:**
- Dynamically generates paths using property decorators.
- Employs templated path definitions to ensure consistency.
- Supports path isolation for different designs and tools.

**Configuration Management Mechanism:**
- Uses dedicated `Parser` classes to handle different configuration formats.
- Supports reading, writing, and dynamic updating of configurations.
- Implements associated management of configurations and paths.

## Config Overview

### 1. Configuration System Overview

The `config` directory in the Workspace is the core of AiEDA's configuration management. It adopts a hierarchical design, supporting the unified management of configurations for multiple tool engines. Users can configure the execution flow by directly modifying the configuration files or by dynamically changing configuration parameters through the programming interface of the `Workspace` class.

### 2. Top-Level Configuration File Structure

The `config` directory contains four core configuration files and a tool configuration subdirectory:

```
config/
├── flow.json        # Flow configuration file
├── parameter.json   # Parameter configuration file
├── path.json        # Path configuration file
├── workspace.json   # Workspace configuration file
└── iEDA_config/     # Configuration directory for other third-party EDA tools, using iEDA as an example.
```

### 3. Detailed Explanation of Core Configuration Files

#### 3.1 workspace.json - Basic Workspace Information

This file configures the workspace overview and defines its basic attributes:

```json
{
    "workspace": {
        "process_node": "sky130",  # Process node
        "version": "V1",           # Version number
        "project": "gcd",          # Project name
        "design": "gcd",           # Design name
        "task": "run_eda"          # Type of task to be executed
    }
}
```

**Main Function:** Defines the workspace's identification information, providing the basic context for subsequent tool execution.

#### 3.2 flow.json - Flow Configuration

Records and configures the execution sequence and status of the design flow:

```json
{
    "task": "run_eda",
    "flow": [
        {
            "eda_tool": "iEDA",      # EDA tool used
            "step": "floorplan",     # Execution stage
            "state": "success",      # Execution status
            "runtime": "0:0:5"       # Runtime
        },
        // More stages...
    ]
}
```

**Main Functions:** Defines the type of task to be executed, configures the sequence of flow execution stages, records the execution status and time for each stage, and supports the mixed execution of multi-toolchains.

#### 3.3 path.json - File Path Configuration

Configures and records the paths of all necessary files, which is fundamental for the execution of the design flow:

```json
{
    "def_input_path": "./gcd_floorplan.def",      # DEF file path
    "verilog_input_path": "./gcd_floorplan.v",    # Verilog file path (optional)
    "tech_lef_path": "./sky130_fd_sc_hs.tlef",    # Technology LEF file path
    "lef_paths": [...],                           # List of LEF file paths
    "lib_paths": [...],                           # List of library file paths
    "sdc_path": "./gcd.sdc",                      # Timing constraint file path
    "spef_path": "/gcd.spef",                     # SPEF file path
    // Other path configurations...
}
```

**Main Functions:** Centralizes the management of all input and output file paths, supports the configuration of multiple technology libraries and design files, and provides file access paths for tool execution.

#### 3.4 parameter.json - Tool Parameter Configuration

Configures key parameters for each tool stage using a unified naming standard:

```json
{
    "placement_target_density": 0.4,       # Placement target density
    "placement_max_phi_coef": 1.04,        # Parameter for the placement algorithm
    "cts_skew_bound": "0.1",               # CTS skew constraint
    "cts_max_buf_tran": "1.2",             # CTS buffer transition constraint
    // Other parameter configurations...
}
```

**Main Functions:** Provides a unified parameter naming standard across tools, centralizes the management of optimization parameters for each stage, and supports parameter tuning and exploration.

### 4. Third-Party Tool Engine Configuration

#### 4.1 iEDA Configuration File Structure

The iEDA tool engine configuration is stored in the `iEDA_config` subdirectory, which contains configuration files for multiple stages:

```
iEDA_config/
├── flow_config.json              # Flow configuration
├── db_default_config.json        # Database configuration
├── fp_default_config.json        # Floorplanning configuration
├── pnp_default_config.json       # PDN configuration
├── pl_default_config.json        # Placement configuration
├── cts_default_config.json       # CTS configuration
├── to_default_config_drv.json    # Timing optimization (DRV) configuration
├── to_default_config_hold.json   # Timing optimization (Hold) configuration
├── to_default_config_setup.json  # Timing optimization (Setup) configuration
├── rt_default_config.json        # Routing configuration
└── drc_default_config.json       # DRC configuration
```

<!-- TODO: #### 4.2 <Other Tools> Configuration File Structure -->

### 5. Configuration Management Mechanism

#### 5.1 Parser Architecture

AiEDA uses specialized `Parser` classes to handle different types of configuration files, including:

- `WorkspaceParser` - Workspace configuration parsing
- `FlowParser` - Flow configuration parsing
- `PathParser` - Path configuration parsing
- `ParametersParser` - Parameter configuration parsing
- `ConfigIEDADbParser` - iEDA database configuration parsing
- `ConfigIEDAFloorplanParser`, etc. - iEDA stage-specific configuration parsing

Note: When users need to integrate a third-party tool, they can extend the path management by following the example of `ConfigIEDADbParser` and others.

#### 5.2 Configuration Creation Process

In the `Workspace.create_workspace()` method, the configuration file creation process is as follows:
1. Create the directory structure.
2. Initialize configuration objects.
3. Create each configuration file in order:
   - `flow.json`
   - `path.json`
   - `workspace.json`
   - `parameter.json`
   - iEDA stage-specific configuration files

#### 5.3 Configuration Access and Modification Mechanism

Each `Parser` class provides the following core functions:
- `create_json()` - Creates the configuration file.
- `get_db()` - Reads the configuration into a data structure.
- `set_xxx()` - Sets a specific configuration item.
- Supports dynamic reading, writing, and updating.

### 6. Multi-Tool Support Mechanism

AiEDA is designed with a flexible configuration extension mechanism to support various tool engines:

- Unified configuration interface design.
- Isolated management of tool-specific configurations.
- Support for incremental extension of configurations.
- Reserved extension points for future integration of tools like DREAMPlace.

### 7. Configuration Best Practices

- Use the `Workspace` class API to modify configurations instead of editing files directly.
- Use the unified parameter names in `parameter.json` (e.g., placement density, CTS constraints) for cross-tool configuration.


## Output Overview

The `output` directory within the Workspace is AiEDA's centralized directory system for storing and managing all output data from EDA tool runs. This directory uses an organizational structure isolated by tool name, ensuring clear management and access to data in a multi-tool engine environment. The overall architecture and the contents of each subdirectory are detailed below.

### 1. File Structure

The output directory is designed with a hierarchical structure. The top level is organized by EDA tool names, and each tool's directory is further divided into functionally distinct data subdirectories. This design ensures that data generated by different tools are isolated from each other while also facilitating the sharing of necessary intermediate data between tools. AiEDA provides a standardized API through the `Workspace` class to achieve unified access to the data from various tools.

```
output/
├── DREAMPlace/     # Output from the DREAMPlace placement tool
├── OpenROAD/       # Output from the OpenROAD tool
└── iEDA/           # Output from the iEDA tool (detailed structure below)
    ├── data/       # Data from the execution process of point tools
    ├── feature/    # Stage-specific feature data
    ├── result/     # Result data
    ├── rpt/        # Report files
    └── vectors/    # Vectorized data
```

### 2. Detailed Explanation of the iEDA Tool Output Directory

Taking the iEDA tool as an example, its output directory contains five main subsystems:

#### 2.1 result Directory - Result Data

This directory stores the final result files from each stage of the EDA flow, primarily including netlist files (.v) and physical design exchange files (.def), which are compressed with gzip to save space.

- **File Naming Convention**: `{design_name}_{stage_name}.{ext}.gz`
  - `design_name`: The name of the design, e.g., "gcd"
  - `stage_name`: The flow stage, e.g., "floorplan", "place", "CTS", "route"
  - `ext`: The file extension, mainly "def" and "v"

- **List of Main Files**:
  ```
  result/
  ├── gcd_floorplan.def.gz     # Physical design file from the floorplan stage
  ├── gcd_floorplan.v.gz       # Netlist file from the floorplan stage
  ├── gcd_place.def.gz         # Physical design file from the placement stage
  ├── gcd_place.v.gz           # Netlist file from the placement stage
  ├── gcd_CTS.def.gz           # Physical design file from the clock tree synthesis stage
  ├── gcd_CTS.v.gz             # Netlist file from the clock tree synthesis stage
  ├── gcd_route.def.gz         # Physical design file from the routing stage
  └── gcd_route.v.gz           # Netlist file from the routing stage
  ```

#### 2.2 data Directory - Intermediate Processing Data

This directory stores detailed intermediate data generated by the EDA tool during various processing stages, further categorized by flow stage:

- **Main Subdirectories**:
  - `pl/`: Placement stage data
  - `cts/`: Clock Tree Synthesis stage data
  - `rt/`: Routing stage data
  - `drc/`: Design Rule Check data
  - `log/`: Run logs for the design flow

#### 2.3 feature Directory - Feature Data

This directory stores feature information extracted from the design, providing a basis for analysis and optimization. The feature data is divided into different types, reflecting various aspects of the design.

- **File Naming Convention**: `{design_name}_{stage_name}_{feature_type}.json`
  - `feature_type`: The type of feature, including:
    - `summary`: Macro-level design statistics (cell count, pin distribution, etc.)
    - `tool`: Detailed data reported by the tool's internal mechanisms
    - `map`: 2D mapping data (density maps, congestion maps, etc.), performance metric data
    - `drc`: Design Rule Check results

- **2D Feature Maps**:
  - `density_map/`: Density distribution map
  - `egr_congestion_map/`: Early global routing congestion map
  - `margin_map/`: Macro cell margin map
  - `RUDY_map/`: Routing demand distribution map

#### 2.4 vectors Directory - Vectorized Data

This directory is for breaking down complex chip designs into structured, computable data representations, which is the foundation for AI-driven optimization. We refer to this structured data as **Foundation Data**, also known as vectorized data. This structured data is presented in JSON format and saved in the `vectors` directory.

Specifically, AiEDA implements a "Design-to-Vector" methodology on the result files (.def), deconstructing the chip design into layers of logical netlist and geometric layout. The logical netlist can be further broken down into different levels of representation such as nets, paths, and graphs. The geometric layout can be deconstructed into information for individual patches. This deconstructed information is ultimately aggregated into finer-grained representations like wires and polygons. Additionally, AiEDA also performs vectorized representation of technology information, such as routing layers and vias (.lef), which is a "library-to-vector" process.

- **Main Vectorized Data Types**:
  - `tech/`: Technology information vectorization (`tech.json`, `cells.json`)
  - `instances/`: Cell instance information vectorization (`instances.json`)
  - `nets/`: Net information vectorization (`net_i.json`)
  - `patchs/`: Layout region partitioning vectorization (`patch_i.json`)
  - `wire_graph/`: Netlist graph structure vectorization (`timing_wire_graph.json`)
  - `wire_paths/`: Routing path vectorization (`wire_path_i.json`)
  - `instance_graph/`: Cell instance connection graph vectorization (`timing_instance_graph.json`)

**The specific meanings of this vectorized data will be detailed in a dedicated section later in this document.**

#### 2.5 rpt Directory - Report Files

This directory stores various report files generated by AiEDA's `report` module, used for analyzing and verifying design quality.

### 3. Data Flow Mechanism

Within the AiEDA framework, data flows between different tools and stages as follows:

1.  **Input Processing**: Initial data is read from design files (DEF, Verilog, etc.).
2.  **Stage Processing**: Data is processed by each EDA tool stage (floorplan, place, route, etc.).
3.  **Result Generation**: Final result files are generated in the `result` directory.
4.  **Feature Extraction**: Feature data is extracted and saved to the `feature` directory.
5.  **Vectorization Conversion**: The design is converted into vectorized data and stored in the `vectors` directory.
6.  **Analysis and Reporting**: Analysis reports are generated and saved to the `rpt` directory.

### 4. Output Management Best Practices

- **Data Sharing**: Access output data through the Workspace API to avoid direct file manipulation.
- **Performance Optimization**: For the purpose of intuitive data understanding, the vectorized data currently shown (for nets and patches) are in discrete files, meaning one file corresponds to one net or patch. For large-scale data operations, the data can be stored and processed in batches, for example, one file storing a batch of nets or patches (e.g., `net_0_678.json` could store 679 nets in one file). AiEDA supports both the generation and access of discrete files (e.g., `net_0.json`, `net_1.json`, ..., `net_678.json`) and aggregated files (`net_0_678.json`).


## Foundation Data: Net

- **Example File Path**: `example/sky130_gcd/output/iEDA/vectors/nets/net_0.json`
- **Data Generation Mechanism**:
  - The `Vectorization::buildFeature` function is called to invoke `buildLayoutData` and `buildGraphData` to construct the foundational data.
  - `generateFeature` is called to generate net features, including timing features, DRC features, and statistical features.
  - Finally, the data is saved via `_data_manager.saveData`, where Net data is saved to the `nets` directory using the `VecLayoutFileIO::saveJsonNets` method.
  - Batch processing mode is supported; depending on the `batch_mode` parameter, a single file can save one or multiple nets.

- **Data Structure Example**:
  ```json
  {
    "id": 0,
    "name": "Net Name",
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
        "i": "Cell Instance Name",
        "p": "Pin Name",
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
            }
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
            }
      ]
    }
  }
  ```

- **Field Descriptions**:

  | Field Name | Data Type | Description | Unit | Example Value |
  | :--- | :--- | :--- | :--- | :--- |
  | `id` | Integer | Unique identifier for the net | - | 0 |
  | `name` | String | Name of the net | - | "ctrl$a_mux_sel[0]" |
  | `feature` | Object | Collection of net features | - | - |
  | `feature.llx` | Integer | Lower-left x-coordinate of the net's bounding box, taking the leftmost polygon value | Database Unit | 79680 |
  | `feature.lly` | Integer | Lower-left y-coordinate of the net's bounding box, taking the bottommost polygon value | Database Unit | 68880 |
  | `feature.urx` | Integer | Upper-right x-coordinate of the net's bounding box, taking the rightmost polygon value | Database Unit | 82320 |
  | `feature.ury` | Integer | Upper-right y-coordinate of the net's bounding box, taking the topmost polygon value | Database Unit | 74880 |
  | `feature.wire_len` | Integer | Total length of the net's wire segments | Database Unit | 11040 |
  | `feature.via_num` | Integer | Number of vias | Count | 6 |
  | `feature.drc_num` | Integer | Number of DRC violations | Count | 0 |
  | `feature.drc_type` | Array | List of DRC violation types | - | [] |
  | `feature.R` | Float | Total resistance of the net | Ohms | 19.714 |
  | `feature.C` | Float | Total capacitance of the net | pF | 0.003467 |
  | `feature.power` | Float | Total power consumption of the net | Watts | 1.1747e-07 |
  | `feature.delay` | Float | Total delay of the net | ns | 0.02949 |
  | `feature.slew` | Float | Signal slew rate | ns | 0.009644 |
  | `feature.aspect_ratio` | Float | Aspect ratio of the bounding box | - | 2.0 |
  | `feature.width` | Integer | Width of the bounding box | Database Unit | 2640 |
  | `feature.height` | Integer | Height of the bounding box | Database Unit | 6000 |
  | `feature.area` | Integer | Area of the bounding box | Square DB Unit | 15840000 |
  | `feature.volume` | Integer | 3D volume of the bounding box | Cubic DB Unit | 31680000 |
  | `feature.layer_ratio` | Array | Wire length distribution ratio for each layer from bottom to top | - | [0.0, 0.0, 0.28, ...] |
  | `feature.place_feature` | Object | Features from the placement stage | - | - |
  | `feature.place_feature.pin_num` | Integer | Number of pins connected to the net | Count | 2 |
  | `feature.place_feature.aspect_ratio` | Float | Aspect ratio of the net's bounding box, calculated from pin center points | - | 2.0 |
  | `feature.place_feature.width` | Integer | Width of the pin placement bounding box, calculated from pin center points | Database Unit | 2195 |
  | `feature.place_feature.height` | Integer | Height of the pin placement bounding box, calculated from pin center points | Database Unit | 3507 |
  | `feature.place_feature.area` | Integer | Area of the pin placement bounding box, calculated from pin center points | Square DB Unit | 7697865 |
  | `feature.place_feature.l_ness` | Float | Pin distribution, from A.B. Kahang's paper "What the L" | - | 1.0 |
  | `feature.place_feature.hpwl` | Integer | Half-perimeter wire length, calculated from pin center points | Database Unit | 5702 |
  | `feature.place_feature.rsmt` | Integer | Rectilinear Steiner minimal tree length, calculated from pin center points | Database Unit | 5702 |
  | `pin_num` | Integer | Number of pins | Count | 2 |
  | `pins` | Array | List of pins | - | - |
  | `pins[].id` | Integer | Pin ID | - | 0 |
  | `pins[].i` | String | Name of the instance the pin belongs to | - | "ctrl/_34_" |
  | `pins[].p` | String | Pin name | - | "X" |
  | `pins[].driver` | Integer | Is it a driver pin? (1: Yes, 0: No) | - | 1 |
  | `wire_num` | Integer | Number of wire segments | Count | 11 |
  | `wires` | Array | List of wire segments | - | - |
  | `wires[].id` | Integer | Wire segment ID | - | 0 |
  | `wires[].feature` | Object | Wire segment features | - | - |
  | `wires[].feature.wire_width` | Integer | Wire segment width | Database Unit | 140 |
  | `wires[].feature.wire_len` | Integer | Wire segment length | Database Unit | 960 |
  | `wires[].feature.wire_density` | Float | Wire segment density | - | 0.1 |
  | `wires[].feature.drc_num` | Integer | Number of DRC violations on the segment | Count | 0 |
  | `wires[].feature.R` | Float | Resistance of the segment | Ohms | 0.8571 |
  | `wires[].feature.C` | Float | Capacitance of the segment | pF | 4.6356e-05 |
  | `wires[].feature.power` | Float | Power consumption of the segment | Watts | 8.7271e-07 |
  | `wires[].feature.delay` | Float | Delay of the segment | ns | 0.002208 |
  | `wires[].feature.slew` | Float | Slew rate of the segment | ns | 6.6217e-11 |
  | `wires[].feature.congestion` | Float | Congestion in the wire segment's area (demand-supply) | - | 4.5 |
  | `wires[].feature.drc_type` | Array | List of DRC violation types on the segment | - | [] |
  | `wires[].wire` | Object | Node info for the wire segment; connection is not necessarily Manhattan | - | - |
  | `wires[].wire.id1` | Integer | Start node ID | - | 742163 |
  | `wires[].wire.x1` | Integer | Start x-coordinate on the grid | Database Unit | 81360 |
  | `wires[].wire.y1` | Integer | Start y-coordinate on the grid | Database Unit | 74880 |
  | `wires[].wire.real_x1` | Integer | Actual start x-coordinate | Database Unit | 81360 |
  | `wires[].wire.real_y1` | Integer | Actual start y-coordinate | Database Unit | 75055 |
  | `wires[].wire.r1` | Integer | Row number of the start point | - | 312 |
  | `wires[].wire.c1` | Integer | Column number of the start point | - | 339 |
  | `wires[].wire.l1` | Integer | Metal layer of the start point | - | 2 |
  | `wires[].wire.p1` | Integer | Corresponding real pin number for the start point, -1 if not a real pin | - | -1 |
  | `wires[].wire.id2` | Integer | End node ID | - | 742167 |
  | `wires[].wire.x2` | Integer | End x-coordinate on the grid | Database Unit | 82320 |
  | `wires[].wire.y2` | Integer | End y-coordinate on the grid | Database Unit | 74880 |
  | `wires[].wire.real_x2` | Integer | Actual end x-coordinate | Database Unit | 82320 |
  | `wires[].wire.real_y2` | Integer | Actual end y-coordinate | Database Unit | 75055 |
  | `wires[].wire.r2` | Integer | Row number of the end point | - | 312 |
  | `wires[].wire.c2` | Integer | Column number of the end point | - | 343 |
  | `wires[].wire.l2` | Integer | Metal layer of the end point | - | 2 |
  | `wires[].wire.p2` | Integer | Corresponding real pin number for the end point, -1 if not a real pin | - | -1 |
  | `wires[].path_num` | Integer | Number of Manhattan paths the wire is decomposed into | Count | 1 |
  | `wires[].paths` | Array | Information on the Manhattan paths the wire is decomposed into | - | - |
  | `wires[].patch_num` | Integer | Number of patches passed through | Count | 2 |
  | `wires[].patchs` | Array | List of IDs of patches passed through | - | [528, 529] |
  | `routing_graph` | Object | Routing graph structure, representing the net's graph theory model | - | - |
  | `routing_graph.vertices`| Array | List of vertices in the graph, containing all nodes | - | - |
  | `routing_graph.vertices[].id` | Integer | Unique vertex identifier | - | 0 |
  | `routing_graph.vertices[].is_pin` | Integer | Is it a pin? (1: Yes, 0: No) | - | 0 |
  | `routing_graph.vertices[].is_driver_pin` | Integer | Is it a driver pin? (1: Yes, 0: No) | - | 0 |
  | `routing_graph.vertices[].x` | Integer | Vertex x-coordinate | Database Unit | 81360 |
  | `routing_graph.vertices[].y` | Integer | Vertex y-coordinate | Database Unit | 75055 |
  | `routing_graph.vertices[].layer_id` | Integer | Metal layer ID of the vertex | - | 2 |
  | `routing_graph.edges` | Array | List of edges, representing connections between vertices | - | - |
  | `routing_graph.edges[].source_id` | Integer | Source vertex ID of the edge | - | 0 |
  | `routing_graph.edges[].target_id` | Integer | Target vertex ID of the edge | - | 1 |
  | `routing_graph.edges[].path` | Array | List of path points on the edge, representing the actual route | - | - |
  | `routing_graph.edges[].path[].x` | Integer | Path point x-coordinate | Database Unit | 81360 |
  | `routing_graph.edges[].path[].y` | Integer | Path point y-coordinate | Database Unit | 75055 |
  | `routing_graph.edges[].path[].layer_id` | Integer | Metal layer ID of the path point | - | 2 |

- **Data Usage**:
  1. Provides the geometric and electrical characteristics of nets for physical design analysis.
  2. Supports timing analysis with key parameters like resistance, capacitance, delay, and slew.
  3. Used for DRC checks and violation analysis.
  4. Power estimation and optimization.
  5. Routing density and congestion analysis.
  6. Provides training data for machine learning models to predict net performance.

- **Data Characteristics**:
  1. Contains multi-level net information, from macroscopic bounding boxes to microscopic wire segment details.
  2. Integrates geometric, electrical, and timing characteristics.
  3. Supports feature analysis for both placement and routing stages.
  4. Stored in JSON format for easy parsing and processing.
  5. Provides a complete routing graph structure, facilitating graph-based analysis and algorithm optimization.


## Foundation Data: Path
- **Example File Path**: `"example/sky130_gcd/output/iEDA/vectors/wire_paths/wire_path_1.json"`

- **Data Generation Mechanism**:
  - First, foundational data is built using `buildLayoutData` and `buildGraphData`.
  - The `buildFeatureTiming` method of the `VecFeature` class is called for timing feature extraction.
  - `eval_tp->runVecSTA()` is executed to perform a detailed timing analysis.
  - Specifically, the `reportWirePaths()` function generates detailed path data by traversing paths in the timing graph.
  - Finally, the data is saved in JSON format to the `wire_paths` directory through file I/O operations.

- **Data Structure Example**:
Path data uses a JSON array format, organizing the nodes and delay arcs of a path in chronological order. Each element in the array is a JSON object representing an element in the path (a node or an arc).

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
          // more edges...
      }
    }
    // more nodes and arcs...
  ]
  ```

- **Field Descriptions**:

  | Field Type | Field Name | Data Type | Description | Unit | Example Value |
  | :--- | :----| :--- | :--- | :--- | :--- |
  | **Node Info** | `node_*` | Object | An instance pin or internal node on the path | - | - |
  | | `node_*.Point` | String | Node location info, format: "instance_name:pin_name (cell_type)" | - | "dpath/b_reg/_147_:CLK (sky130_fd_sc_hs__dfxtp_1)" |
  | | `node_*.Capacitance` | Float | Node capacitance value | pF | 0.003 |
  | | `node_*.slew` | Float | Node signal transition time (slew) | ns | 0.134413 |
  | | `node_*.trans_type` | String | Signal transition type | - | "rise" or "fall" |
  | **Instance Arc** | `inst_arc_*` | Object | Internal delay arc of an instance, representing cell-internal propagation delay | - | - |
  | | `inst_arc_*.Incr` | Float | Incremental delay within the instance | ns | 0.238 |
  | **Net Arc** | `net_arc_*` | Object | Net delay arc, representing signal propagation delay on the net | - | - |
  | | `net_arc_*.Incr` | Float | Total incremental delay of the net | ns | 0.000476 |
  | | `net_arc_*.edge_*` | Object | Specific wire segment information within the net | - | - |
  | | `net_arc_*.edge_*.wire_from_node` | String | Start node name of the wire segment | - | "dpath/b_reg/_147_:Q" |
  | | `net_arc_*.edge_*.wire_to_node` | String | End node name of the wire segment | - | "dpath/a_lt_b$in1[15]:847926" |
  | | `net_arc_*.edge_*.wire_R` | Float | Resistance value of the wire segment | Ω | 0.642857 |
  | | `net_arc_*.edge_*.wire_C` | Float | Capacitance value of the wire segment | pF | 3.618685e-05 |
  | | `net_arc_*.edge_*.from_slew` | Float | Slew at the start of the wire segment | ns | 0.134413 |
  | | `net_arc_*.edge_*.to_slew` | Float | Slew at the end of the wire segment | ns | 0.134413033744 |
  | | `net_arc_*.edge_*.wire_delay` | Float | Delay introduced by the wire segment | ns | 1.18515e-05 |

- **Data Usage**:
  1.  **Timing Analysis**: Provides detailed path delay information for analyzing and optimizing the design's timing performance.
  2.  **Signal Integrity Assessment**: Includes signal transition times and net RC parameters, supporting signal integrity analysis.
  3.  **Power Analysis**: Based on node capacitance and toggle rates, dynamic power can be calculated.
  4.  **Path Visualization**: The data structure facilitates the graphical representation and analysis of paths.
  5.  **Timing Closure Verification**: Used to verify that the design meets timing constraints.
  6.  **Machine Learning Model Training**: Provides training data for predicting path delays, signal integrity, and other issues.

- **Data Characteristics**:
  1.  **Temporal Order**: Elements in the array are strictly arranged in the chronological order of signal propagation.
  2.  **Alternating Structure**: Nodes (`node_*`) and arcs (`inst_arc_*`/`net_arc_*`) appear alternately, forming a complete path.
  3.  **Incremental IDs**: The IDs of nodes and arcs increase sequentially along the path, making it easy to trace the signal flow.
  4.  **Hierarchical Details**: Net arcs contain nested, detailed wire segment information (`edge_*`), providing fine-grained interconnect characteristics.


## Foundation Data: Graph

- **Example File Path**: `./example/sky130_gcd/output/iEDA/vectors/wire_graph/timing_wire_graph.json`

- **Data Generation Mechanism**:
  - **Data Preparation**: In the `Vectorization::buildFeature` method, `_data_manager.buildLayoutData()` is first called to build layout data, followed by `_data_manager.buildGraphData()` to construct the initial graph data structure.
  - **Feature Extraction**: The `generateFeature()` method is called to create a `VecFeature` object, and `feature.buildFeatureTiming()` generates timing-related features.
  - **Timing Analysis**: The `runVecSTA` method (called on an `InitSTA::getInst()` instance via `eval_tp->runVecSTA()`) performs a detailed timing analysis to calculate key parameters like arrival times and required times for nodes.
  - **Data Saving**: Finally, the `_data_manager.saveData()` method saves the generated Graph data as a JSON file.

- **Data Structure Example**: Graph data is organized in JSON format, using a standard graph data structure to represent the net connection relationships in the chip design.
  ```json
  {
      "nodes": [ // Array of nodes, representing pins, ports, and routing nodes
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
        // more nodes...
      ],  
      "edges": [ // Array of edges, representing connections between nodes
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
        // more edges...
      ]   
  }
  ```


- **Field Descriptions**:
  - **Nodes**: Each node represents a connection point in the chip design, which could be a cell pin, a port, or a routing node.
    | Field Name | Data Type | Description | Unit | Example Value |
    | :--- | :--- | :--- | :--- | :--- |
    | `id` | string | Unique identifier for the node | - | "node_4" |
    | `name` | string | Node name, usually containing instance and pin names | - | "clk_0_buf:X" |
    | `is_pin` | boolean | Whether it is a cell pin | - | true |
    | `is_port` | boolean | Whether it is a chip port | - | false |
    | `node_feature` | object | Collection of node feature attributes, including timing and power info | - | - |
  - **Node Features** (`node_feature`):
    | Field Name | Data Type | Description | Unit | Example Value |
    | :--- | :--- | :--- | :--- | :--- |
    | `is_input` | boolean | Whether it is an input node (relative to the cell) | - | false |
    | `fanout_num` | integer | Fanout count, indicating the number of loads driven by this node | - | 17 |
    | `is_endpoint` | boolean | Whether it is an endpoint of a timing path | - | false |
    | `cell_name` | string | Cell name, if the node is a cell pin | - | "sky130_fd_sc_hs__buf_1" |
    | `sizer_cells` | array[string] | List of replaceable cells for cell sizing optimization | - | ["sky130_fd_sc_hs__buf_16", ...] |
    | `node_coord` | array[float] | Node coordinates (x, y) | DB Unit | [57.842, 61.732] |
    | `node_slews` | array[float] | Node slew times, includes values for four process corners | ns | [0.0, 0.0, 0.0, 0.0] |
    | `node_capacitances` | array[float] | Node capacitance values, includes values for four process corners | pF | [0.0, 0.0, 0.0, 0.0] |
    | `node_arrive_times` | array[float] | Signal arrival times at the node, includes values for four process corners | ns | [1.1e+20, 1.1e+20, ...] |
    | `node_required_times` | array[float] | Required arrival times at the node, includes values for four process corners | ns | [1.1e+20, 1.1e+20, ...] |
    | `node_net_load_delays` | array[float] | Node net load delays, includes values for four process corners | ns | [0.0, 0.0, 0.0, 0.0] |
    | `node_toggle` | float | Node toggle rate, indicating signal transitions per unit time | - | 1.0 |
    | `node_sp` | float | Signal probability, the probability of the signal being high | - | 0.5 |
    | `node_internal_power` | float | Node internal power, mainly cell internal power | W | 0.0 |
    | `node_net_power` | float | Node net power, mainly dynamic power on the net | W | 0.00012901 |

  - **Edges**: Each edge represents a connection between two nodes, which can be an internal cell connection or a net connection.
    | Field Name | Data Type | Description | Unit | Example Value |
    | :--- | :--- | :--- | :--- | :--- |
    | `id` | string | Unique identifier for the edge | - | "edge_7960" |
    | `from_node` | integer | Start node ID (index in the `nodes` array) | - | 7586 |
    | `to_node` | integer | End node ID (index in the `nodes` array) | - | 7587 |
    | `is_net_edge` | boolean | Whether it is a net edge (true for net, false for internal cell connection) | - | true |
    | `edge_feature` | object | Collection of edge feature attributes, including delay and power info | - | - |

  - **Edge Features** (`edge_feature`):
    | Field Name | Data Type | Description | Unit | Example Value |
    | :--- | :--- | :--- | :--- | :--- |
    | `edge_delay` | array[float] | Edge delay values, includes values for four process corners | ns | [0.0, 0.0, 0.0, 0.0] |
    | `edge_resistance` | float | Edge resistance value, mainly for net edges | Ohms | 18.42857 |
    | `inst_arc_internal_power`| float | Instance arc internal power, mainly for internal cell edges | W | 0.0 |

- **Data Usage**:
  1.  **Timing Analysis**: Provides a complete timing graph structure, supporting Static Timing Analysis (STA).
  2.  **Power Optimization**: Contains detailed power-related parameters, supporting power analysis and optimization.
  3.  **Physical Design Verification**: Offers the connection relationship between physical implementation and logical design, supporting design verification.
  4.  **Machine Learning Feature Extraction**: Provides structured chip design feature data for ML models, supporting prediction and optimization tasks.
  5.  **Design Visualization**: Supports converting the chip design into a visual graph structure for better understanding and analysis.

- **Data Characteristics**:
  1.  **STA Support**: The Graph data includes complete timing-related information, supporting calculations and verifications related to Static Timing Analysis (STA).
  2.  **Process Corner Coverage**: Key parameters (like delay, slew, etc.) include values for four process corners, supporting full process corner analysis.
  3.  **Hierarchical Structure**: Data is organized by nodes and edges from graph theory, clearly expressing the connection relationships in the chip design.
  4.  **Multi-dimensional Features**: Each node and edge contains multi-dimensional features like timing, power, and geometric location, supporting comprehensive analysis and optimization.


## Foundation Data: Patch

- **Example File Path**: `./example/sky130_gcd/output/iEDA/vectors/patchs/patch_0.json`

- **Data Generation Mechanism**:
  1. The `Vectorization::buildFeature` function calls the `buildPatchData` method to construct the Patch data.
  2. The data generation process is managed by `VecDataManager` and specifically implemented by `VecPatchDataManager`.
  3. `VecPatchInit` is responsible for initializing the Patch grid and populating it with net and wire segment information.
  4. Finally, the data is saved as a JSON file via `VecLayoutFileIO::saveJsonPatchs`.

- **Data Structure Example**:
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
          // More sub-nets ...
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
                    // More wire segments...
                  ]
              } 
            ]
          },
          // More patch_layers...
      ]
  }
  ```


- **Field Descriptions**:
  - **Global Information**
    | Field Name | Data Type | Description | Unit | Example Value |
    | :--- | :--- | :--- | :--- | :--- |
    | `id` | Integer | Unique identifier for the patch, as an integer sequence number | - | 0 |
    | `patch_id_row` | Integer | Row index of the patch in the grid | - | 0 |
    | `patch_id_col` | Integer | Column index of the patch in the grid | - | 0 |
    | `llx` | Integer | Lower-left x-coordinate of the patch | Database Unit | 0 |
    | `lly` | Integer | Lower-left y-coordinate of the patch | Database Unit | 0 |
    | `urx` | Integer | Upper-right x-coordinate of the patch | Database Unit | 4320 |
    | `ury` | Integer | Upper-right y-coordinate of the patch | Database Unit | 4320 |
    | `row_min` | Integer | Minimum row number of nodes within the patch | - | 0 |
    | `row_max` | Integer | Maximum row number of nodes within the patch | - | 18 |
    | `col_min` | Integer | Minimum column number of nodes within the patch | - | 0 |
    | `col_max` | Integer | Maximum column number of nodes within the patch | - | 18 |
    | `cell_density` | Float | Cell density within the patch, value range [0, 1] | - | 0.898148 |
    | `pin_density` | Float | Pin density within the patch | Number of pins | 40 |
    | `net_density` | Float | Net density within the patch | - | 0.123714 |
    | `macro_margin` | Integer | Maximum margin distance to a macro cell within the patch | Database Unit | 255180 |
    | `RUDY_congestion` | Float | Congestion estimation value based on the RUDY model | - | 0.000292 |
    | `EGR_congestion` | Float | Congestion estimation value based on the EGR model | - | 3.0 |
    | `timing` | Float | Timing information | ns | 0.0 |
    | `power` | Float | Power information | W | 3.26907e-07 |
    | `IR_drop` | Float | IR drop information | V | 0.0 |
    | `sub_nets` | Array | Information about sub-nets contained within the patch | - | [Array of sub-net objects] |
    | `patch_layer` | Array | Detailed information for each layer of the patch | - | [Array of layer objects] |

  - **Sub-net Information (`sub_nets`)**: Each element in the `sub_nets` array is a sub-net, defining the overlapping area of a net with the patch, as follows:
    | Field Name | Data Type | Description | Unit | Example Value |
    | :--- | :--- | :--- | :--- | :--- |
    | `id` | Integer | Unique identifier for the sub-net | - | 626 |
    | `llx` | Integer | Lower-left x-coordinate of the sub-net | Database Unit | 1000 |
    | `lly` | Integer | Lower-left y-coordinate of the sub-net | Database Unit | 0 |
    | `urx` | Integer | Upper-right x-coordinate of the sub-net | Database Unit | 4320 |
    | `ury` | Integer | Upper-right y-coordinate of the sub-net | Database Unit | 4320 |

  - **Layer Information (`patch_layer`)**: Each element in the `patch_layer` array represents a layer within the patch, defined as follows:
    | Field Name | Data Type | Description | Unit | Example Value |
    | :--- | :--- | :--- | :--- | :--- |
    | `id` | Integer | Layer ID, corresponding to a metal layer in the physical design | - | 4 |
    | `feature` | Object | Layer feature information | - | See table below |
    | `net_num` | Integer | Number of nets contained in the layer | - | 1 |
    | `nets` | Array | List of nets in the layer | - | [Array of net objects] |

  - **Layer Features (`feature`)**
    | Field Name | Data Type | Description | Unit | Example Value |
    | :--- | :--- | :--- | :--- | :--- |
    | `wire_width` | Integer | Wire segment width | Database Unit | 140 |
    | `wire_len` | Integer | Total length of wire segments | Database Unit | 3120 |
    | `wire_density` | Float | Wire density | - | 0.023405 |
    | `congestion` | Float | Congestion level of this layer | - | 2.0 |

  - **Net Information (`nets`)**: Each element in the `nets` array represents a net, defined as follows:
    | Field Name | Data Type | Description | Unit | Example Value |
    | :--- | :--- | :--- | :--- | :--- |
    | `id` | Integer | Unique identifier for the net | - | 650 |
    | `wire_num` | Integer | Number of wires in the net | - | 2 |
    | `wires` | Array | List of wires | - | [Array of wire objects] |

  - **Wire Information (`wires`)**: Each element in the `wires` array represents a wire segment, defined as follows:
    | Field Name | Data Type | Description | Unit | Example Value |
    | :--- | :--- | :--- | :--- | :--- |
    | `id` | Integer | Unique identifier for the wire | - | 6600 |
    | `feature` | Object | Wire feature information | - | {"wire_len": 3120} |
    | `path_num` | Integer | Number of paths contained in the wire | - | 1 |
    | `paths` | Array | List of paths | - | [Array of path objects] |

  - **Path Information (`paths`)**: Each element in the `paths` array represents a segment of a wire's path, defined as follows:
    | Field Name | Data Type | Description | Unit | Example Value |
    | :--- | :--- | :--- | :--- | :--- |
    | `id1` | Integer | Unique identifier for the start point | - | 1151867 |
    | `x1`, `y1` | Integer | Grid coordinates of the start point | Database Unit | 720, 1200 |
    | `real_x1`, `real_y1` | Integer | Actual physical coordinates of the start point | Database Unit | 720, 1200 |
    | `r1`, `c1` | Integer | Row and column of the grid where the start point is located | - | 5, 3 |
    | `l1` | Integer | Layer ID where the start point is located | - | 4 |
    | `p1` | Integer | Pin index of the start point (-1 for non-real pins) | - | -1 |
    | `id2` | Integer | Unique identifier for the end point | - | 1158835 |
    | `x2`, `y2` | Integer | Grid coordinates of the end point | Database Unit | 720, 4320 |
    | `real_x2`, `real_y2` | Integer | Actual physical coordinates of the end point | Database Unit | 720, 4320 |
    | `r2`, `c2` | Integer | Row and column of the grid where the end point is located | - | 18, 3 |
    | `l2` | Integer | Layer ID where the end point is located | - | 4 |
    | `p2` | Integer | Pin index of the end point (-1 for non-real pins) | - | -1 |
    | `via` | Integer | Via ID (optional, exists only for cross-layer connections) | - | 10 (Via number) |

- **Data Usage**:
  1.  **Physical Layout Analysis**: Provides detailed physical characteristics of different regions in a chip design, supporting designers in macroscopic layout evaluation.
  2.  **Layout Visualization**: The data structure facilitates the graphical display and analysis of layout regions.
  3.  **Performance Optimization Guidance**: Based on path information and electrical characteristics, it provides detailed physical foundation data for timing performance optimization.
  4.  **AI Model Training Data**: Provides structured physical design feature data for deep learning models, supporting AI tasks like routing prediction and congestion analysis.

- **Data Characteristics**:
  1.  Patch data is divided into grid-like patch units based on physical design regions.
  2.  Each patch contains information for multiple layers, and each layer includes detailed geometric and electrical attributes of nets, wires, and paths.
  3.  The data is organized hierarchically from macro to micro: patch -> layer -> net -> wire -> path.
  4.  Path information precisely describes the connection points on a wire, including coordinates, layer, and grid position.


## Foundation Data: Instance

- **Example File Path**: `./example/sky130_gcd/output/iEDA/vectors/instances/instances.json`

- **Data Generation Mechanism**:
  1. The `Vectorization::buildFeature` function calls the `_data_manager.saveData` method to save all data.
  2. The `saveData` method internally calls the `VecLayoutFileIO::saveJson` function.
  3. The `saveJson` function calls the `saveJsonInstances` method specifically to generate Instance data.
  4. Finally, the data is saved in JSON format to the specified directory.

- **Data Structure Example**: The `instances.json` file uses the following structure:

  ```json
  {
    "instance_num": 1448, // Total number of instances
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
      // More instances...
    ]
  }
  ```

- **Field Descriptions**:

  The fields for each instance are described as follows:
  | Field Name | Data Type | Description | Unit | Example Value |
  | :--- | :--- | :--- | :--- | :--- |
  | `id` | Integer | Unique identifier for the instance | - | 1 |
  | `cell_id` | Integer | ID of the cell master to which the instance belongs | - | 1001 |
  | `name` | String | Instance name | - | "sky130_fd_sc_hs__and2_1_0" |
  | `cx` | Float | x-coordinate of the instance's center point | Database Unit | 1234.5 |
  | `cy` | Float | y-coordinate of the instance's center point | Database Unit | 5678.9 |
  | `width` | Float | Instance width | Database Unit | 420.0 |
  | `height` | Float | Instance height | Database Unit | 180.0 |
  | `llx` | Float | Lower-left x-coordinate of the instance | Database Unit | 1024.5 |
  | `lly` | Float | Lower-left y-coordinate of the instance | Database Unit | 5588.9 |
  | `urx` | Float | Upper-right x-coordinate of the instance | Database Unit | 1444.5 |
  | `ury` | Float | Upper-right y-coordinate of the instance | Database Unit | 5768.9 |

- **Data Usage**:
  1.  **Physical Layout Representation**: The instance data precisely describes the physical location and size of each standard cell in the design.
  2.  **Timing Analysis Support**: The location information of instances is fundamental for calculating wire lengths and interconnect delays.
  3.  **Routability Analysis**: The distribution of instances is used to evaluate layout quality and routing difficulty.
  4.  **AI Model Training**: Provides real physical design instance layout data for machine learning models.

- **Data Characteristics**:
  1.  **Comprehensiveness**: Contains information for all instances in the design, with no omissions.
  2.  **Precision**: Coordinate and size information is accurate to the database unit.
  3.  **Associativity**: Linked to cell library information via `cell_id`.
  4.  **Uniform Structure**: All instances use the same data structure, facilitating batch processing.
  5.  **Extensibility**: The JSON format supports the addition of extra instance attributes.

## Foundation Data: Instance Graph

- **Example File Path**: `./example/sky130_gcd/output/iEDA/vectors/instance_graph/timing_instance_graph.json`

- **Data Generation Mechanism**:
  1. The `Vectorization::buildFeature` function calls the `generateFeature` method.
  2. The `generateFeature` method internally calls the `VecFeature::buildFeatureTiming` function.
  3. The `buildFeatureTiming` function calls `eval_tp->getTimingInstanceGraph()` to obtain the instance graph data.
  4. Finally, the data is saved in JSON format to the specified directory via the `SaveTimingInstanceGraph` function.

- **Data Structure Example**:

  The `timing_instance_graph.json` file uses the following structure:

  ```json
  {
    "nodes": [        
      {
        "id": "node_0",
        "name": "ctrl/_34_",
        "leakage_power": 1.6979909062047418e-10
      },
      // More nodes...
    ],
    "edges": [
      {
        "id": "edge_0",
        "from_node": 0,
        "to_node": 1
      },
      // More edges...
    ]
  }
  ```

- **Field Descriptions**:

  - **Nodes**: Each node object represents an instance and contains the following fields:
    | Field Name | Data Type | Description | Unit | Example Value |
    | :--- | :--- | :--- | :--- | :--- |
    | `id` | String | Unique identifier for the node, format "node_number" | - | "node_0" |
    | `name` | String | Instance name | - | "ctrl/_34_" |
    | `leakage_power` | Float | Leakage power of the instance | W | 1.697e-10 |


  - **Edges**: Each edge represents the connection relationship between two instances and contains the following fields:
    | Field Name | Data Type | Description | Unit | Example Value |
    | :--- | :--- | :--- | :--- | :--- |
    | `id` | String | Unique identifier for the edge, format "edge_number" | - | "edge_1037" |
    | `from_node` | Integer | Index of the driving node (corresponds to the index in the `nodes` array) | - | 640 |
    | `to_node` | Integer | Index of the receiving node (corresponds to the index in the `nodes` array) | - | 188 |

- **Data Usage**:
  1.  **Timing Analysis**: The instance graph provides all instances and their connection relationships in the design, which can be used for timing path analysis and delay prediction.
  2.  **Power Estimation**: Contains leakage power information, which can be used for overall power estimation.
  3.  **Physical Constraint Study**: Reflects the connection density between instances, which helps in studying the impact of physical constraints on the design.
  4.  **AI Model Training**: Provides instance-level connection relationship and power data for machine learning models.

- **Data Characteristics**:
  1.  **Structured Representation**: Uses a graph data structure to clearly represent the connection relationships between instances.
  2.  **Lightweight Design**: Edges contain only basic connection information, facilitating fast processing and analysis.
  3.  **Includes Power Information**: Each node includes leakage power data, which is convenient for power analysis.
  4.  **Global View**: Provides a global view of the instance connections for the entire design.


## Foundation Data: Cell

- **Example File Path**: `./example/sky130_gcd/output/iEDA/vectors/tech/cells.json`

- **Data Generation Mechanism**:
  1. The `Vectorization::buildFeature` function calls `_data_manager.buildLayoutData` to construct the basic layout data.
  2. After data construction is complete, `_data_manager.saveData` is called to save the data.
  3. During the saving process, the `VecLayoutFileIO::saveJson` method calls the `saveJsonCells` method.
  4. The `saveJsonCells` method retrieves cell data from `_layout->get_cells().get_cell_map()` and saves it to the `cells.json` file.

- **Data Structure Example**:
  ```json
  {
    "cell_num": integer,      // Total number of cell_master units
    "cells": [            // Array of cells
      {
        "id": integer,       // Cell ID
        "name": "string", // Cell name
        "width": integer,    // Cell width
        "height": integer    // Cell height
      },
      // More cell masters...
    ]
  }
  ```

- **Field Descriptions**:
  | Field Name | Type | Description | Unit | Example Value |
  | :--- | :--- | :--- | :--- | :--- |
  | `cell_num` | integer | Total number of cells in the cell library | - | 416 |
  | `cells` | array | Array containing information for all cells | - | [{}, ...] |
  | `id` | integer | Unique identifier for the cell | - | 415 |
  | `name` | string | Cell name, including technology information and functional description | - | "sky130_sram_1rw1r_44x64_8" |
  | `width` | integer | Physical width of the cell | Database Unit (e.g., nm) | 445240 |
  | `height` | integer | Physical height of the cell | Database Unit (e.g., nm) | 237415 |

- **Data Usage**:
  1.  **Physical Design Reference**: Provides physical dimension information for standard cells and macro cells for placement and routing.
  2.  **Area Estimation**: Used for chip area calculation and density analysis.
  3.  **Power Analysis**: Serves as base data for power calculation.
  4.  **Timing Optimization**: Provides cell-level references for timing analysis.

- **Data Characteristics**:
  1.  **Completeness**: Contains information on all available standard cells and macro cells.
  2.  **Physical Accuracy**: Provides precise physical dimension parameters.
  3.  **Process-Related**: The data reflects cell characteristics under a specific technology node.
  4.  **Structured Storage**: Uses JSON format for easy parsing and processing by programs.
  5.  **Extensibility**: The data structure is simple and clear, making it easy to add new cell attributes.

## Foundation Data: Technology

- **Example File Path**: `./example/sky130_gcd/output/iEDA/vectors/tech/tech.json`

- **Data Generation Mechanism**:
  1. The `Vectorization::buildFeature` function calls `_data_manager.buildLayoutData` to construct the basic layout data.
  2. After data construction is complete, `_data_manager.saveData` is called to save the data.
  3. During the saving process, the `VecLayoutFileIO::saveJson` method calls the `saveJsonTech` method.
  4. The `saveJsonTech` method retrieves layer data from `_layout->get_layout_layers().get_layout_layer_map()` and via data from `_layout->get_via_name_map()`, saving them to the `tech.json` file.

- **Data Structure Example**:
  ```json
  {
    "layer_num": integer,  // Number of technology layers
    "layers": [        // Array of layer information
      {
        "id": integer,   // Layer number
        "name": "string" // Layer name
      },
      // More layers...
    ],
    "via_num": integer,   // Number of via types
    "vias": [          // Array of via information
      {
        "id": integer,   // Via number
        "name": "string", // Via name
        "bottom": {   // Bottom metal enclosure area coordinates
          "llx": integer,
          "lly": integer,
          "urx": integer,
          "ury": integer
        },
        "cut": {      // Via cut area coordinates
          "llx": integer,
          "lly": integer,
          "urx": integer,
          "ury": integer
        },
        "top": {      // Top metal enclosure area coordinates
          "llx": integer,
          "lly": integer,
          "urx": integer,
          "ury": integer
        },
        "row": integer,  // Number of via rows
        "col": integer,  // Number of via columns
        "bottom_direction": "string", // Offset direction of the cut relative to the bottom enclosure
        "top_direction": "string"     // Offset direction of the cut relative to the top enclosure
      },
      // More vias...
    ]
  }
  ```

- **Field Descriptions**:
  - **Layer Information Fields**
    | Field Name | Type | Description | Unit | Example Value |
    | :--- | :--- | :--- | :--- | :--- |
    | `layer_num` | integer | Total number of layers in the technology | - | 11 |
    | `layers` | array | Array of detailed information for all layers | - | [{}, ...] |
    | `id` | integer | Sequential number of the layer (from bottom to top) | - | 10 |
    | `name` | string | Layer name (metal layer, via layer, etc.) | - | "met5" |

  - **Via Information Fields**
    | Field Name | Type | Description | Unit | Example Value |
    | :--- | :--- | :--- | :--- | :--- |
    | `via_num` | integer | Total number of via types | - | 32 |
    | `vias` | array | Array of detailed information for all via types | - | [{}, ...] |
    | `id` | integer | Unique identifier for the via type | - | 0 |
    | `name` | string | Via type name | - | "L1M1_PR" |
    | `bottom` | object | Bounding box coordinates of the bottom metal enclosure area | Database Unit | {"llx": -85, "lly": -85, "urx": 85, "ury": 85} |
    | `cut` | object | Bounding box coordinates of the via cut area | Database Unit | {"llx": -85, "lly": -85, "urx": 85, "ury": 85} |
    | `top` | object | Bounding box coordinates of the top metal enclosure area | Database Unit | {"llx": -145, "lly": -115, "urx": 145, "ury": 115} |
    | `row` | integer | Number of rows of via cuts | - | 1 |
    | `col` | integer | Number of columns of via cuts | - | 1 |
    | `bottom_direction` | string | Connection direction for the bottom layer (C-Center, N-North, S-South, E-East, W-West) | - | "C" |
    | `top_direction` | string | Connection direction for the top layer (C-Center, N-North, S-South, E-East, W-West) | - | "C" |

- **Data Usage**:
  1.  **Physical Design Rule Checking**: Provides detailed parameters for layers and vias to verify if the design complies with technology rules.
  2.  **Routing Guidance**: Serves as technology constraint input for automatic routing tools.
  3.  **Design Visualization**: Provides accurate layer and via representations for design visualization.
  4.  **Timing Analysis**: Provides necessary technology parameters for signal integrity and timing analysis.

- **Data Characteristics**:
  1.  **Technology Accuracy**: Accurately reflects layer and via characteristics for a specific technology node.
  2.  **Completeness**: Includes all necessary physical layers and via types.
  3.  **Structured Representation**: Uses JSON format for easy parsing and processing by programs.
  4.  **Complete Spatial Information**: Provides precise geometric coordinates for different parts of each via.
  5.  **Directional Information**: Includes directional information for via connections, which helps in understanding routing topology.
