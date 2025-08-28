#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File : vectors.py
@Author : yell
@Desc : EDA vectors data structure for physical design
'''

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List

@dataclass
class VectorNode:
    id: Optional[int] = None
    x: Optional[int] = None
    y: Optional[int] = None
    row: Optional[int] = None
    col: Optional[int] = None
    layer: Optional[int] = None
    pin_id: Optional[int] = None

@dataclass
class VectorPath:
    node1: Optional[VectorNode] = None
    node2: Optional[VectorNode] = None

@dataclass
class VectorWireFeature:
    wire_width: Optional[int] = None
    wire_len: Optional[int] = None
    drc_num: Optional[int] = None
    R: Optional[float] = None
    C: Optional[float] = None
    power: Optional[float] = None
    delay: Optional[float] = None
    slew: Optional[float] = None
    congestion: Optional[float] = None
    wire_density: Optional[float] = None
    drc_type: List[str] = field(default_factory=list)

@dataclass
class VectorWire:
    id: Optional[int] = None
    feature: Optional[VectorWireFeature] = None
    wire: Optional[VectorPath] = None
    path_num: Optional[int] = None
    paths: List[VectorPath] = field(default_factory=list)

@dataclass
class VectorPin:
    id: Optional[int] = None
    pin_name: Optional[str] = None
    instance: Optional[str] = None
    is_driver: Optional[str] = None

@dataclass
class VectorNetFeature:
    llx: Optional[int] = None
    lly: Optional[int] = None
    urx: Optional[int] = None
    ury: Optional[int] = None
    wire_len: Optional[int] = None
    via_num: Optional[int] = None
    drc_num: Optional[int] = None
    R: Optional[float] = None
    C: Optional[float] = None
    power: Optional[float] = None
    delay: Optional[float] = None
    slew: Optional[float] = None
    fanout: Optional[int] = None
    aspect_ratio: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    area: Optional[int] = None
    l_ness: Optional[float] = None
    drc_type: List[str] = field(default_factory=list)
    volume: Optional[int] = None
    layer_ratio: List[float] = field(default_factory=list)
    rsmt: Optional[int] = None


@dataclass
class VectorNetRoutingPoint:
    x: int
    y: int
    layer_id: int

    def __str__(self):
        return f"({self.x}, {self.y}, {self.layer_id})"

    def __repr__(self):
        return f"Point({self.x}, {self.y}, {self.layer_id})"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.layer_id == other.layer_id

    def __hash__(self):
        return hash((self.x, self.y, self.layer_id))


@dataclass
class VectorNetRoutingVertex:
    id: int
    is_pin: bool
    is_driver_pin: bool
    point: VectorNetRoutingPoint


@dataclass
class VectorNetRoutingEdge:
    source_id: int
    target_id: int
    path: List[VectorNetRoutingPoint]
        
@dataclass
class VectorNetRoutingGraph:
    vertices: List[VectorNetRoutingVertex]
    edges: List[VectorNetRoutingEdge]
    
@dataclass
class VectorNet:
    id: Optional[int] = None
    name: Optional[str] = None
    feature: Optional[VectorNetFeature] = None
    pin_num: Optional[int] = None
    pins: List[VectorPin] = field(default_factory=list)
    wire_num: Optional[int] = None
    wires: List[VectorWire] = field(default_factory=list)
    routing_graph: Optional[VectorNetRoutingGraph] = None

@dataclass
class VectorPatchLayer:
    id: Optional[int] = None
    net_num: Optional[int] = None
    nets: List[VectorNet] = field(default_factory=list)
    wire_width: Optional[int] = None
    wire_len: Optional[int] = None
    wire_density: Optional[float] = None
    congestion: Optional[float] = None

@dataclass
class VectorPatch:
    id: Optional[int] = None
    patch_id_row: Optional[int] = None
    patch_id_col: Optional[int] = None
    llx: Optional[int] = None
    lly: Optional[int] = None
    urx: Optional[int] = None
    ury: Optional[int] = None
    row_min: Optional[int] = None
    row_max: Optional[int] = None
    col_min: Optional[int] = None
    col_max: Optional[int] = None
    patch_layer: List[VectorPatchLayer] = field(default_factory=list)
    area: Optional[int] = None
    cell_density: Optional[float] = None
    pin_density: Optional[int] = None
    net_density: Optional[float] = None
    macro_margin: Optional[int] = None
    RUDY_congestion: Optional[float] = None
    EGR_congestion: Optional[float] = None
    timing_map: Optional[float] = None
    power_map: Optional[float] = None
    ir_drop_map: Optional[float] = None

@dataclass
class VectorWirePatternPoint(object):
    x: int = None
    y: int = None
    z: int = None


@dataclass
class VectorWirePatternDirection(Enum):
    TOP = "TOP"
    BOTTOM = "BOTTOM"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    VIA = "VIA"

@dataclass
class VectorWirePatternUnit:
    direction: VectorWirePatternDirection = None
    length: int = None


@dataclass
class VectorWirePatternSeq:
    name: str = None
    units: List[VectorWirePatternUnit] = field(default_factory=list)


@dataclass
class VectorNetSeq:
    loc_seq: List[VectorWirePatternPoint] = field(default_factory=list)
    pattern_seq: List[VectorWirePatternSeq] = field(default_factory=list)

@dataclass
class VectorTimingWireGraphNode:
    id : str = None
    name: str = None
    is_pin: bool = False
    is_port: bool = False
    
@dataclass
class VectorTimingWireGraphEdge:
    id : str = None
    from_node: int = None
    to_node: int = None
    is_net_edge : bool = False
    
@dataclass
class VectorTimingWireGraph(object):
    nodes: List[VectorTimingWireGraphNode] = field(default_factory=list)
    edges: List[VectorTimingWireGraphEdge] = field(default_factory=list)
    
@dataclass
class VectorTimingWirePathGraph(object):
    nodes: List[VectorTimingWireGraphNode] = field(default_factory=list)
    edges: List[VectorTimingWireGraphEdge] = field(default_factory=list)

@dataclass
class VectorLayer:
    id : int = None
    name : str = None
    
@dataclass
class VectorLayers(object):
    layer_num : int = None
    layers: List[VectorLayer] = field(default_factory=list)
    
@dataclass
class VectorVia:
    id : int = None
    name : str = None
    
@dataclass
class VectorVias(object):
    via_num : int = None
    vias: List[VectorVia] = field(default_factory=list)
    
@dataclass
class VectorCell:
    id : int = None
    name : str = None
    width : int = None
    height : int = None
    
@dataclass
class VectorCells(object):
    cell_num : int = None
    cells: List[VectorCell] = field(default_factory=list)

@dataclass
class VectorInstance:
    id : int = None
    cell_id : int = None
    name : str = None
    x : int = None
    y : int = None
    width : int = None
    height : int = None
    llx : int = None
    lly : int = None
    urx : int = None
    ury : int = None
    orient : str = None
    status : str = None
    
@dataclass
class VectorInstances(object):
    instance_num : int = None
    instances: List[VectorInstance] = field(default_factory=list)
    
@dataclass
class VectorInstanceGraphNode:
    id : str = None
    name: str = None
    
@dataclass
class VectorInstanceGraphEdge:
    id : str = None
    from_node: int = None
    to_node: int = None
    
@dataclass
class VectorInstanceGraph(object):
    nodes: List[VectorInstanceGraphNode] = field(default_factory=list)
    edges: List[VectorInstanceGraphEdge] = field(default_factory=list)
    
@dataclass
class VectorPathMetrics:
    stage: Optional[int] = None
    inst_delay: List[float] = field(default_factory=list)
    net_delay: List[float] = field(default_factory=list)
