#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File : eda.py
@Author : yell
@Desc : eda database
'''

from dataclasses import dataclass,field
from numpy import double, uint, uint64
from typing import Dict, List, Optional

##########################################################################################
##########################################################################################
""" data structure for feature of iEDA summary 

    begin
"""
##########################################################################################
@dataclass     
class SummaryInfo(object):
    """infomation structure"""
    eda_tool : str = ""
    eda_version : str = ""
    design_name = ""
    design_version : str = ""
    flow_stage : str = ""
    flow_runtime : str = ""
    flow_memory : str = ""

@dataclass     
class SummaryLayout(object):
    """layout structure"""
    design_dbu : int = 0
    die_area : double = 0.0
    die_usage : double = 0.0
    die_bounding_width : double = 0.0
    die_bounding_height : double = 0.0
    core_area : double = 0.0
    core_usage : double = 0.0
    core_bounding_width : double = 0.0
    core_bounding_height : double = 0.0
    
@dataclass     
class SummaryStatis(object):
    """chip statis"""
    num_layers : int = 0
    num_layers_routing : int = 0
    num_layers_cut : int = 0
    num_iopins : int = 0
    num_instances : int = 0
    num_nets : int = 0
    num_pdn :int = 0
    
@dataclass     
class SummaryInstance(object):
    num : uint64 = None
    num_ratio : double = None
    area : double = None
    area_ratio : double = None
    die_usage : double = None
    core_usage : double = None
    pin_num : uint64 = None
    pin_ratio : double = None

@dataclass     
class SummaryInstances(object):
    """instance structure"""
    total : SummaryInstance = None
    iopads : SummaryInstance = None
    macros : SummaryInstance = None
    logic : SummaryInstance = None
    clock : SummaryInstance = None
    
@dataclass     
class SummaryNets(object):
    """nets structure"""
    num_total : uint64 = None
    num_signal : uint64 = None
    num_clock : uint64 = None
    num_pins : uint64 = None
    num_segment : uint64 = None
    num_via : uint64 = None
    num_wire : uint64 = None
    num_patch : uint64 = None

    wire_len : double = None
    wire_len_signal : double = None
    ratio_signal : double = None
    wire_len_clock : double = None
    ratio_clock : double = None

@dataclass 
class SummaryLayerRouting(object):
    layer_name : str = None
    layer_order : uint = None
    wire_len : double = None
    wire_ratio : double = None
    wire_num : uint64 = None
    patch_num : uint64 = None

@dataclass 
class SummaryLayerCut(object):
    layer_name : str = None
    layer_order : uint = None
    via_num : uint64 = None
    via_ratio : double = None
    
@dataclass     
class SummaryLayers(object):
    """layer structure"""
    num_layers : int = 0
    num_layers_routing : int = 0
    num_layers_cut : int = 0
    routing_layers : list = field(default_factory=list)
    cut_layers : list = field(default_factory=list)

@dataclass     
class SummaryPins(object):
    """pins structure"""
    max_fanout : uint = None
    pin_distribution : list = field(default_factory=list)

@dataclass 
class SummaryPin(object):
    pin_num : uint64 = None
    net_num : uint64 = None
    net_ratio : double = None
    inst_num : uint64 = None
    inst_ratio : double = None

@dataclass     
class FeatureSummary(object):
     """basic feature package"""  
     flow = None
     info : SummaryInfo = None
     statis : SummaryStatis = None
     layout : SummaryLayout = None
     layers : SummaryLayers = None
     nets : SummaryNets = None
     instances : SummaryInstances = None
     pins : SummaryPins =None
##########################################################################################
""" data structure for feature of iEDA summary 

    end
"""
##########################################################################################
##########################################################################################


##########################################################################################
##########################################################################################
""" data structure for feature of iEDA tools 
    
    begin
""" 
##########################################################################################
@dataclass
class ClockTiming(object):
    clock_name: str = None
    setup_tns: float = None
    setup_wns: float = None
    hold_tns: float = None
    hold_wns: float = None
    suggest_freq: float = None


@dataclass
class CTSSummary(object):
    buffer_num: int = None
    buffer_area: float = None
    clock_path_min_buffer: int = None
    clock_path_max_buffer: int = None
    max_level_of_clock_tree: int = None
    max_clock_wirelength: int = None
    total_clock_wirelength: float = None
    clocks_timing: list = field(default_factory=list)
    static_power: float = None
    dynamic_power: float = None


@dataclass
class PLCommonSummary(object):
    place_density: float = None
    HPWL : int = None
    STWL : int = None


@dataclass
class LGSummary(object):
    pl_common_summary: PLCommonSummary = None
    lg_total_movement: int = None
    lg_max_movement: int = None


@dataclass
class PlaceSummary(object):
    bin_number: int = None
    bin_size_x: int = None
    bin_size_y: int = None
    fix_inst_cnt: int = None
    instance_cnt: int = None
    net_cnt: int = None
    overflow_number: int = None
    overflow: float = None
    total_pins: int = None

    dplace: PLCommonSummary = None
    gplace: PLCommonSummary = None
    lg_summary: LGSummary = None


@dataclass
class NOClockTimingCmp(object):
    clock_name: str = None
    origin: ClockTiming = None
    opt: ClockTiming = None
    delta: ClockTiming = None


@dataclass
class NetOptSummary(object):
    clock_timings: list = field(default_factory=list)


@dataclass
class TOClockTiming(object):
    tns: float = None
    wns: float = None
    suggest_freq: float = None


@dataclass
class TOClockTimingCmp(object):
    clock_name: str = None
    origin: TOClockTiming = None
    opt: TOClockTiming = None
    delta: TOClockTiming = None


@dataclass
class TimingOptSummary(object):
    HPWL: float = None
    STWL: float = None
    clock_timings: list = field(default_factory=list)


@dataclass
class PASummary(object):
    # std::map<int32_t, double> routing_wire_length_map
    routing_wire_length_map: Dict[int, float] = field(default_factory=dict)
    total_wire_length: float = 0.0
    # std::map<int32_t, int32_t> cut_via_num_map
    cut_via_num_map: Dict[int, int] = field(default_factory=dict)
    total_via_num: int = 0
    # std::map<int32_t, int32_t> routing_patch_num_map
    routing_patch_num_map: Dict[int, int] = field(default_factory=dict)
    total_patch_num: int = 0
    # std::map<int32_t, int32_t> routing_violation_num_map
    routing_violation_num_map: Dict[int, int] = field(default_factory=dict)
    total_violation_num: int = 0


@dataclass
class SASummary(object):
    # std::map<int32_t, int32_t> routing_supply_map
    routing_supply_map: Dict[int, int] = field(default_factory=dict)
    total_supply: int = 0


@dataclass
class TGSummary(object):
    total_demand: float = 0.0
    total_overflow: float = 0.0
    total_wire_length: float = 0.0
    # std::map<std::string, std::map<std::string, double>> clock_timing_map
    clock_timing_map: Dict[str, Dict[str, float]] = field(default_factory=dict)
    # std::map<std::string, double> type_power_map
    type_power_map: Dict[str, float] = field(default_factory=dict)

@dataclass
class LASummary(object):
    # std::map<int32_t, double> routing_demand_map
    routing_demand_map: Dict[int, float] = field(default_factory=dict)
    total_demand: float = 0.0
    # std::map<int32_t, double> routing_overflow_map
    routing_overflow_map: Dict[int, float] = field(default_factory=dict)
    total_overflow: float = 0.0
    # std::map<int32_t, double> routing_wire_length_map
    routing_wire_length_map: Dict[int, float] = field(default_factory=dict)
    total_wire_length: float = 0.0
    # std::map<int32_t, int32_t> cut_via_num_map
    cut_via_num_map: Dict[int, int] = field(default_factory=dict)
    total_via_num: int = 0
    # std::map<std::string, std::map<std::string, double>> clock_timing_map
    clock_timing_map: Dict[str, Dict[str, float]] = field(default_factory=dict)
    # std::map<std::string, double> type_power_map
    type_power_map: Dict[str, float] = field(default_factory=dict)

@dataclass
class SRSummary(object):
    # std::map<int32_t, double> routing_demand_map
    routing_demand_map: Dict[int, float] = field(default_factory=dict)
    total_demand: float = 0.0
    # std::map<int32_t, double> routing_overflow_map
    routing_overflow_map: Dict[int, float] = field(default_factory=dict)
    total_overflow: float = 0.0
    # std::map<int32_t, double> routing_wire_length_map
    routing_wire_length_map: Dict[int, float] = field(default_factory=dict)
    total_wire_length: float = 0.0
    # std::map<int32_t, int32_t> cut_via_num_map
    cut_via_num_map: Dict[int, int] = field(default_factory=dict)
    total_via_num: int = 0
    # std::map<std::string, std::map<std::string, double>> clock_timing_map
    clock_timing_map: Dict[str, Dict[str, float]] = field(default_factory=dict)
    # std::map<std::string, double> type_power_map
    type_power_map: Dict[str, float] = field(default_factory=dict)



@dataclass
class TASummary(object):
    # std::map<int32_t, double> routing_wire_length_map
    routing_wire_length_map: Dict[int, float] = field(default_factory=dict)
    total_wire_length: float = 0.0
    # std::map<int32_t, int32_t> routing_violation_num_map
    routing_violation_num_map: Dict[int, int] = field(default_factory=dict)
    total_violation_num: int = 0


@dataclass
class DRSummary(object):
    # std::map<int32_t, double> routing_wire_length_map
    routing_wire_length_map: Dict[int, float] = field(default_factory=dict)
    total_wire_length: float = 0.0
    # std::map<int32_t, int32_t> cut_via_num_map
    cut_via_num_map: Dict[int, int] = field(default_factory=dict)
    total_via_num: int = 0
    # std::map<int32_t, int32_t> routing_patch_num_map
    routing_patch_num_map: Dict[int, int] = field(default_factory=dict)
    total_patch_num: int = 0
    # std::map<int32_t, int32_t> routing_violation_num_map
    routing_violation_num_map: Dict[int, int] = field(default_factory=dict)
    total_violation_num: int = 0
    # std::map<std::string, std::map<std::string, double>> clock_timing_map
    clock_timing_map: Dict[str, Dict[str, float]] = field(default_factory=dict)
    # std::map<std::string, double> type_power_map
    type_power_map: Dict[str, float] = field(default_factory=dict)


@dataclass
class VRSummary(object):
    # std::map<int32_t, double> routing_wire_length_map
    routing_wire_length_map: Dict[int, float] = field(default_factory=dict)
    total_wire_length: float = 0.0
    # std::map<int32_t, int32_t> cut_via_num_map
    cut_via_num_map: Dict[int, int] = field(default_factory=dict)
    total_via_num: int = 0
    # std::map<int32_t, int32_t> routing_patch_num_map
    routing_patch_num_map: Dict[int, int] = field(default_factory=dict)
    total_patch_num: int = 0
    # std::map<int32_t, std::map<std::string, int32_t>> within_net_routing_violation_type_num_map
    within_net_routing_violation_type_num_map: Dict[int, Dict[str, int]] = field(default_factory=dict)
    # std::map<std::string, int32_t> within_net_violation_type_num_map
    within_net_violation_type_num_map: Dict[str, int] = field(default_factory=dict)
    # std::map<int32_t, int32_t> within_net_routing_violation_num_map
    within_net_routing_violation_num_map: Dict[int, int] = field(default_factory=dict)
    within_net_total_violation_num: int = 0
    # std::map<int32_t, std::map<std::string, int32_t>> among_net_routing_violation_type_num_map
    among_net_routing_violation_type_num_map: Dict[int, Dict[str, int]] = field(default_factory=dict)
    # std::map<std::string, int32_t> among_net_violation_type_num_map
    among_net_violation_type_num_map: Dict[str, int] = field(default_factory=dict)
    # std::map<int32_t, int32_t> among_net_routing_violation_num_map
    among_net_routing_violation_num_map: Dict[int, int] = field(default_factory=dict)
    among_net_total_violation_num: int = 0
    # std::map<std::string, std::map<std::string, double>> clock_timing_map
    clock_timing_map: Dict[str, Dict[str, float]] = field(default_factory=dict)
    # std::map<std::string, double> type_power_map
    type_power_map: Dict[str, float] = field(default_factory=dict)

@dataclass
class ERSummary(object):
    # std::map<int32_t, int32_t> routing_demand_map
    routing_demand_map: Dict[int, int] = field(default_factory=dict)
    total_demand: int = 0
    # std::map<int32_t, int32_t> routing_overflow_map
    routing_overflow_map: Dict[int, int] = field(default_factory=dict)
    total_overflow: int = 0
    # std::map<int32_t, double> routing_wire_length_map
    routing_wire_length_map: Dict[int, float] = field(default_factory=dict)
    total_wire_length: float = 0.0
    # std::map<int32_t, int32_t> cut_via_num_map
    cut_via_num_map: Dict[int, int] = field(default_factory=dict)
    total_via_num: int = 0
    # std::map<std::string, std::map<std::string, double>> clock_timing_map
    clock_timing_map: Dict[str, Dict[str, float]] = field(default_factory=dict)
    # std::map<std::string, double> type_power_map
    type_power_map: Dict[str, float] = field(default_factory=dict)



@dataclass
class RouteSummary(object):
    # std::map<int32_t, PASummary> iter_pa_summary_map
    iter_pa_summary_map: Dict[int, PASummary] = field(default_factory=dict)
    # SASummary sa_summary
    sa_summary: Optional[SASummary] = None
    # TGSummary tg_summary
    tg_summary: Optional[TGSummary] = None
    # LASummary la_summary
    la_summary: Optional[LASummary] = None
    # std::map<int32_t, SRSummary> iter_sr_summary_map
    iter_sr_summary_map: Dict[int, SRSummary] = field(default_factory=dict)
    # TASummary ta_summary
    ta_summary: Optional[TASummary] = None
    # std::map<int32_t, DRSummary> iter_dr_summary_map
    iter_dr_summary_map: Dict[int, DRSummary] = field(default_factory=dict)
    # VRSummary vr_summary
    vr_summary: Optional[VRSummary] = None
    # ERSummary er_summary
    er_summary: Optional[ERSummary] = None
    
@dataclass
class FeatureDrcShape(object):
    llx: float = None
    lly: float = None
    urx: float = None
    ury: float = None
    net_ids: list = field(default_factory=list)
    inst_ids: list = field(default_factory=list)

@dataclass
class FeatureDrcLayer(object):
    layer: str = None
    number: int = None
    shapes: List[FeatureDrcShape] = field(default_factory=list)

@dataclass
class FeatureDrcDistribution(object):
    type: str = None
    number: int = None
    layers: List[FeatureDrcLayer] = field(default_factory=list)

@dataclass
class FeatureDrcDistributions(object):
    number: int = None
    drc_list: List[FeatureDrcDistribution] = field(default_factory=list)


@dataclass
class FeatureTools(object):
    no_summary: NetOptSummary = None
    place_summary: PlaceSummary = None
    cts_summary: CTSSummary = None
    opt_drv_summary: TimingOptSummary = None
    opt_hold_summary: TimingOptSummary = None
    opt_setup_summary: TimingOptSummary = None
    legalization_summary: PlaceSummary = None
    routing_summary: RouteSummary = None
##########################################################################################
""" data structure for feature of iEDA tools 
    
    end
""" 
##########################################################################################
##########################################################################################



##########################################################################################
##########################################################################################
""" data structure for feature of iEDA evaluation 

    begin
"""
##########################################################################################
from enum import Enum
from typing import List
import numpy as np

# wirelength
@dataclass
class FeatureWirelength(object):
    FLUTE: float = None
    GRWL: float = None
    HPWL: float = None
    HTree: float = None
    VTree: float = None

# density
@dataclass
class FeatureDensityCell(object):
    # csv map path
    allcell_density: str = None
    macro_density: str = None
    stdcell_density: str = None
    # csv map value
    allcell_density_data: np.ndarray = None
    macro_density_data: np.ndarray = None
    stdcell_density_data: np.ndarray = None
    
@dataclass
class FeatureDensityMargin(object):
    # csv map path
    horizontal: str = None
    union: str = None
    vertical: str = None
    # csv map value
    horizontal_data: np.ndarray = None
    union_data: np.ndarray = None
    vertical_data: np.ndarray = None

@dataclass
class FeatureDensityNet(object):
    # csv map path
    allnet_density: str = None
    global_net_density: str = None
    local_net_density: str = None
    # csv map value
    allnet_density_data: np.ndarray = None
    global_net_density_data: np.ndarray = None
    local_net_density_data: np.ndarray = None

@dataclass
class FeatureDensityPin(object):
    # csv map path
    allcell_pin_density: str = None
    macro_pin_density: str = None
    stdcell_pin_density: str = None
    # csv map value
    allcell_pin_density_data: np.ndarray = None
    macro_pin_density_data: np.ndarray = None
    stdcell_pin_density_data: np.ndarray = None

@dataclass
class FeatureDensity(object):
    cell: FeatureDensityCell = None
    margin: FeatureDensityMargin = None
    net: FeatureDensityNet = None
    pin: FeatureDensityPin = None

# congestion
@dataclass
class FeatureCongestionMapBase(object):
    # csv map path
    horizontal: str = None
    union: str = None
    vertical: str = None
    # csv map value
    horizontal_data: np.ndarray = None
    union_data: np.ndarray = None
    vertical_data: np.ndarray = None

@dataclass
class FeatureCongestionMap(object):
    egr: FeatureCongestionMapBase = None
    lutrudy: FeatureCongestionMapBase = None
    rudy: FeatureCongestionMapBase = None

@dataclass
class FeatureCongestionOverflowBase(object):
    horizontal: float = None
    union: float = None
    vertical: float = None

@dataclass
class FeatureCongestionOverflow(object):
    max: FeatureCongestionOverflowBase = None
    top_average: FeatureCongestionOverflowBase = None
    total: FeatureCongestionOverflowBase = None

@dataclass
class FeatureCongestionUtilizationBase(object):
    horizontal: float = None
    union: float = None
    vertical: float = None
    
@dataclass
class FeatureCongestionUtilizationStats(object):
    max: FeatureCongestionUtilizationBase = None
    top_average: FeatureCongestionUtilizationBase = None  

@dataclass
class FeatureCongestionUtilization(object):
    lutrudy: FeatureCongestionUtilizationStats = None
    rudy: FeatureCongestionUtilizationStats = None

@dataclass
class FeatureCongestion(object):
    map: FeatureCongestionMap = None
    overflow: FeatureCongestionOverflow = None
    utilization: FeatureCongestionUtilization = None

# timing
@dataclass
class MethodTimingIEDA(object):
    clock_timings: List[ClockTiming] = None
    dynamic_power: float = None
    static_power: float = None

class FeatureTimingEnumIEDA(Enum):
    DR = 'DR'
    EGR = 'EGR'
    FLUTE = 'FLUTE'
    HPWL = 'HPWL'
    SALT = 'SALT'

@dataclass
class FeatureTimingIEDA(object):
    HPWL: MethodTimingIEDA = None
    FLUTE: MethodTimingIEDA = None
    SALT: MethodTimingIEDA = None
    EGR: MethodTimingIEDA = None
    DR: MethodTimingIEDA = None

@dataclass
class FeatureMetric(object):
    wirelength: FeatureWirelength = None
    density: FeatureDensity = None
    congestion: FeatureCongestion = None
    timing: FeatureTimingIEDA = None  # include timing and power
##########################################################################################
""" data structure for feature of iEDA tools 
    
    end
""" 
##########################################################################################
##########################################################################################