#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : enum.py
@Author : yell
@Desc : enum definition
"""

from enum import Enum


class TrackDirection(Enum):
    """track direction"""

    none = ""
    horizontal = "H"
    vertical = "V"


class LayerType(Enum):
    """layer type"""

    none = ""
    routing = "routing"
    cut = "cut"


class CellType(Enum):
    """cell type"""

    none = ""
    pad = "pad"
    core = "core"


class OrientType(Enum):
    """cell type"""

    none = ""
    N_R0 = "N"
    W_R90 = "W"
    S_R180 = "S"
    E_R270 = "E"
    FN_MY = "FN"
    FE_MY90 = "FE"
    FS_MX = "FS"
    FW_MX90 = "FW"


class PlaceStatus(Enum):
    """placement status"""

    none = ""
    fixed = "fixed"
    cover = "cover"
    placed = "placed"
    unplaced = "unplaced"


class NetType(Enum):
    """net type"""

    none = ""
    signal = "signal"
    clock = "clock"
    power = "power"
    ground = "ground"


class CongestionType(Enum):
    """congestion type in evaluation"""

    none = 0
    instance_density = 1
    pin_density = 2
    net_congestion = 3
    gr_congestion = 4
    macro_margin_h = 5
    macro_margin_v = 6
    continuous_white_space = 7
    macro_margin = 8
    macro_channel = 9


class RudyType(Enum):
    """RUDY type in evaluation"""

    none = 0
    rudy = 1
    pin_rudy = 2
    lut_rudy = 3


class WirelengthType(Enum):
    """wirelength type in evaluation"""

    none = 0
    hpwl = 1
    flute = 2
    htree = 3
    vtree = 4
    grwl = 5


class Direction(Enum):
    """direction type in evaluation"""

    none = 0
    h = 1
    v = 2


class FeatureOption(Enum):
    """feature options"""

    NoFeature = None
    summary = "summary"  # default
    tools = "tool"
    eval_map = "eval_map"
    drc = "drc"
    eval = "eval"
    timing_eval = "timing_eval"
    baseline_drc = "baseline_drc"
    baseline_sta = "baseline_sta"
    baseline_power = "baseline_power"


class DSEMethod(Enum):
    """different EDA DSE method."""

    WANDB = "wandb"
    OPTUNA = "optuna"
    NNI = "nni"
