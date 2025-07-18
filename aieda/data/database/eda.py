#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File : eda.py
@Author : yell
@Desc : eda database
'''

from dataclasses import dataclass
from dataclasses import field
from numpy import double, uint, uint64

##########################################################################################
##########################################################################################
""" data structure for feature of iEDA summary 

    begin
"""
##########################################################################################
from ...flows import DbFlow
    
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
     flow : DbFlow = None
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
    total_access_point_num: int = None
    routing_access_point_num_map: list = field(default_factory=list)
    type_access_point_num_map: list = field(default_factory=list)


@dataclass
class SASummary(object):
    total_supply: int = None
    routing_supply_map: list = field(default_factory=list)


@dataclass
class TGSummary(object):
    total_demand: int = None
    total_overflow: int = None
    total_wire_length: int = None
    clocks_timing: list = field(default_factory=list)
    static_power: float = None
    dynamic_power: float = None


@dataclass
class RoutingBasicSummary(object):
    total_demand: int = None
    routing_demand_map: list = field(default_factory=list)
    total_overflow: int = None
    routing_overflow_map: list = field(default_factory=list)
    total_wire_length: int = None
    routing_wire_length_map: list = field(default_factory=list)
    total_via_num: int = None
    cut_via_num_map: list = field(default_factory=list)
    clocks_timing: list = field(default_factory=list)
    static_power: float = None
    dynamic_power: float = None


@dataclass
class TASummary(object):
    total_wire_length: int = None
    routing_wire_length_map: list = field(default_factory=list)
    total_violation_num: int = None
    routing_violation_num_map: list = field(default_factory=list)


@dataclass
class DRBasicSummary(object):
    total_wire_length: int = None
    routing_wire_length_map: list = field(default_factory=list)
    total_via_num: int = None
    cut_via_num_map: list = field(default_factory=list)
    total_patch_num: int = None
    routing_patch_num_map: list = field(default_factory=list)
    total_violation_num: int = None
    routing_violation_num_map: list = field(default_factory=list)
    clocks_timing: list = field(default_factory=list)
    static_power: float = None
    dynamic_power: float = None


@dataclass
class GRSummary(object):
    summary: list = field(default_factory=list)


@dataclass
class DRSummary(object):
    summary: list = field(default_factory=list)


@dataclass
class RouteSummary(object):
    pa_summary: PASummary = None
    sa_summary: SASummary = None
    tg_summary: TGSummary = None
    la_summary: RoutingBasicSummary = None
    er_summary: RoutingBasicSummary = None
    gr_summary: GRSummary = None
    ta_summary: TASummary = None
    dr_summary: DRSummary = None


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

@dataclass
class FeatureWirelength(object):
    FLUTE: float = None
    GRWL: float = None
    HPWL: float = None
    HTree: float = None
    VTree: float = None

@dataclass
class FeatureDensityCell(object):
    allcell_density: str = None
    macro_density: str = None
    stdcell_density: str = None

@dataclass
class FeatureDensityMargin(object):
    horizontal: str = None
    union: str = None
    vertical: str = None

@dataclass
class FeatureDensityNet(object):
    allnet_density: str = None
    global_net_density: str = None
    local_net_density: str = None

@dataclass
class FeatureDensityPin(object):
    allcell_pin_density: str = None
    macro_pin_density: str = None
    stdcell_pin_density: str = None

@dataclass
class FeatureDensity(object):
    cell: FeatureDensityCell = None
    margin: FeatureDensityMargin = None
    net: FeatureDensityNet = None
    pin: FeatureDensityPin = None

@dataclass
class FeatureCongestionMapBase(object):
    horizontal: str = None
    union: str = None
    vertical: str = None

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
class FeatureCongestionUtilization(object):
    lutrudy: FeatureCongestionUtilizationBase = None
    rudy: FeatureCongestionUtilizationBase = None

@dataclass
class FeatureCongestion(object):
    map: FeatureCongestionMap = None
    overflow: FeatureCongestionOverflow = None
    utilization: FeatureCongestionUtilization = None

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
class FeatureEval(object):
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