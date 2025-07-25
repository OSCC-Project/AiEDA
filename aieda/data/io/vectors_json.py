#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : vectors_json.py
@Author : yell
@Desc : json parser for vectors
'''

from ...utility.json_parser import JsonParser
from ...utility.log import Logger
from ..database import *

class VectorsParserJson(JsonParser):
    def __init__(self, json_path: str, logger: Logger = None):
        super().__init__(json_path, logger)
    
    def get_nets(self) -> list[VectorNet]:
        vec_nets = []

        if self.read() is True:        
            for net_metadata in self.json_data:
                # net
                vec_net = VectorNet()
                vec_net.id = net_metadata.get("id")
                vec_net.name = net_metadata.get("name")
        
                # net feature
                net_feature = VectorNetFeature()
                feature_data = net_metadata.get('feature', {})
                net_feature.llx = feature_data.get('llx')
                net_feature.lly = feature_data.get('lly')
                net_feature.urx = feature_data.get('urx')
                net_feature.ury = feature_data.get('ury')
                net_feature.wire_len = feature_data.get('wire_len')
                net_feature.via_num = feature_data.get('via_num')
                net_feature.drc_num = feature_data.get('drc_num')
                net_feature.R = feature_data.get('R')
                net_feature.C = feature_data.get('C')
                net_feature.power = feature_data.get('power')
                net_feature.delay = feature_data.get('delay')
                net_feature.slew = feature_data.get('slew')
                net_feature.fanout = feature_data.get('fanout')
        
                if 'aspect_ratio' in feature_data:
                    net_feature.aspect_ratio = feature_data.get('aspect_ratio')
                    net_feature.width = feature_data.get('width')
                    net_feature.height = feature_data.get('height')
                    net_feature.area = feature_data.get('area')
                    net_feature.l_ness = feature_data.get('l_ness')
                    net_feature.drc_type = feature_data.get('drc_type')
                    net_feature.volume = feature_data.get('volume')
                    net_feature.layer_ratio = feature_data.get('layer_ratio')
                    net_feature.rsmt = feature_data.get('rsmt')
        
                vec_net.feature = net_feature
        
                # pins
                vec_net.pin_num = net_metadata.get("pin_num", 0)
                json_pins = net_metadata.get("pins", [])
                for json_pin in json_pins:
                    vec_pin = VectorPin()
                    vec_pin.id = json_pin.get("id")
                    vec_pin.instance = json_pin.get("i")
                    vec_pin.pin_name = json_pin.get("p")
                    vec_pin.is_driver = json_pin.get("driver")
        
                    vec_net.pins.append(vec_pin)
        
                # wires
                vec_net.wire_num = net_metadata.get("wire_num", 0)
                json_wires = net_metadata.get("wires", [])
                for json_wire in json_wires:
                    vec_wire = VectorWire()
                    vec_wire.id = json_wire.get("id")
        
                    # wire feature
                    wire_feature = VectorWireFeature()
                    wire_feature_data = json_wire.get("feature", {})
                    wire_feature.wire_width = wire_feature_data.get("wire_width")
                    wire_feature.wire_len = wire_feature_data.get("wire_len")
                    wire_feature.drc_num = wire_feature_data.get("drc_num")
                    wire_feature.R = wire_feature_data.get("R")
                    wire_feature.C = wire_feature_data.get("C")
                    wire_feature.power = wire_feature_data.get("power")
                    wire_feature.delay = wire_feature_data.get("delay")
                    wire_feature.slew = wire_feature_data.get("slew")
                    wire_feature.congestion = wire_feature_data.get("congestion")
                    wire_feature.wire_density = wire_feature_data.get(
                        "wire_density")
                    wire_feature.drc_type = wire_feature_data.get("drc_type")
        
                    vec_wire.feature = wire_feature
        
                    # wire connections
                    wire_data = json_wire.get("wire", {})
                    wire_connections = VectorPath()
        
                    vec_node1 = VectorNode()
                    vec_node1.id = wire_data.get("id1")
                    vec_node1.x = wire_data.get("x1")
                    vec_node1.y = wire_data.get("y1")
                    vec_node1.real_x = wire_data.get("real_x1")
                    vec_node1.real_y = wire_data.get("real_y1")
                    vec_node1.row = wire_data.get("r1")
                    vec_node1.col = wire_data.get("c1")
                    vec_node1.layer = wire_data.get("l1")
                    vec_node1.pin_id = wire_data.get("p1")
                    wire_connections.node1 = vec_node1
        
                    vec_node2 = VectorNode()
                    vec_node2.id = wire_data.get("id2")
                    vec_node2.x = wire_data.get("x2")
                    vec_node2.y = wire_data.get("y2")
                    vec_node2.real_x = wire_data.get("real_x2")
                    vec_node2.real_y = wire_data.get("real_y2")
                    vec_node2.row = wire_data.get("r2")
                    vec_node2.col = wire_data.get("c2")
                    vec_node2.layer = wire_data.get("l2")
                    vec_node2.pin_id = wire_data.get("p2")
                    wire_connections.node2 = vec_node2
        
                    vec_wire.wire = wire_connections
        
                    # path
                    vec_wire.path_num = json_wire.get("path_num", 0)
                    json_paths = json_wire.get("paths", [])
                    for json_path in json_paths:
                        wire_path = VectorPath()
        
                        vec_path_node1 = VectorNode()
                        vec_path_node1.id = json_path.get("id1")
                        vec_path_node1.x = json_path.get("x1")
                        vec_path_node1.y = json_path.get("y1")
                        vec_path_node1.real_x = json_path.get("real_x1")
                        vec_path_node1.real_y = json_path.get("real_y1")
                        vec_path_node1.row = json_path.get("r1")
                        vec_path_node1.col = json_path.get("c1")
                        vec_path_node1.layer = json_path.get("l1")
                        wire_path.node1 = vec_path_node1
        
                        vec_path_node2 = VectorNode()
                        vec_path_node2.id = json_path.get("id2")
                        vec_path_node2.x = json_path.get("x2")
                        vec_path_node2.y = json_path.get("y2")
                        vec_path_node2.real_x = json_path.get("real_x2")
                        vec_path_node2.real_y = json_path.get("real_y2")
                        vec_path_node2.row = json_path.get("r2")
                        vec_path_node2.col = json_path.get("c2")
                        vec_path_node2.layer = json_path.get("l2")
                        wire_path.node2 = vec_path_node2
        
                        vec_wire.paths.append(wire_path)
        
                    vec_net.wires.append(vec_wire)
        
                # routing graph
                routing_graph_data = net_metadata.get("routing_graph", {})
                vertices = []
                for v in routing_graph_data.get("vertices", []):
                    point = VectorNetRoutingPoint(
                        x=v["x"],
                        y=v["y"],
                        layer_id=v["layer_id"]
                    )
                    vertex = VectorNetRoutingVertex(
                        id=v["id"],
                        is_pin=v["is_pin"],
                        is_driver_pin=v["is_driver_pin"],
                        point=point
                    )
                    vertices.append(vertex)
        
                edges = []
                for e in routing_graph_data.get("edges", []):
                    path = [VectorNetRoutingPoint(**p) for p in e["path"]]
                    edge = VectorNetRoutingEdge(source_id=e["source_id"],
                                            target_id=e["target_id"], path=path)
                    edges.append(edge)
                routing_graph = VectorNetRoutingGraph(vertices=vertices, edges=edges)
                vec_net.routing_graph = routing_graph
                    
                vec_nets.append(vec_net)

        return vec_nets
    
    
    def get_patchs(self) -> list[VectorPatch]:
        vec_patchs = []
        if self.read():
            for json_patch in tqdm(self.json_data, total=len(self.json_data), desc="load patchs"):
            
                vec_patch = VectorPatch()
        
                # patch
                vec_patch.id = json_patch.get('id')
                vec_patch.patch_id_row = json_patch.get('patch_id_row')
                vec_patch.patch_id_col = json_patch.get('patch_id_col')
                vec_patch.llx = json_patch.get('llx')
                vec_patch.lly = json_patch.get('lly')
                vec_patch.urx = json_patch.get('urx')
                vec_patch.ury = json_patch.get('ury')
                vec_patch.row_min = json_patch.get('row_min')
                vec_patch.row_max = json_patch.get('row_max')
                vec_patch.col_min = json_patch.get('col_min')
                vec_patch.col_max = json_patch.get('col_max')
                vec_patch.area = json_patch.get('area')
                vec_patch.cell_density = json_patch.get('cell_density')
                vec_patch.pin_density = json_patch.get('pin_density')
                vec_patch.net_density = json_patch.get('net_density')
                vec_patch.macro_margin = json_patch.get('macro_margin')
                vec_patch.RUDY_congestion = json_patch.get('RUDY_congestion')
                vec_patch.EGR_congestion = json_patch.get('EGR_congestion')
                vec_patch.timing_map = json_patch.get('timing_map')
                vec_patch.power_map = json_patch.get('power_map')
                vec_patch.ir_drop_map = json_patch.get('ir_drop_map')   
        
                # patch layer
                json_patch_layers = json_patch.get('patch_layer', [])
                for json_patch_layer in json_patch_layers:
                    patch_layer = VectorPatchLayer()
                    patch_layer.id = json_patch_layer.get('id')
                    patch_layer.net_num = json_patch_layer.get('net_num')
                    feature = json_patch_layer.get('feature', {})
                    patch_layer.wire_width = feature.get('wire_width')
                    patch_layer.wire_len = feature.get('wire_len')
                    patch_layer.wire_density = feature.get('wire_density')
                    patch_layer.congestion = feature.get('congestion')
        
                    json_nets = json_patch_layer.get('nets', [])
                    for json_net in json_nets:
                        # net
                        vec_net = VectorNet()
                        vec_net.id = json_net.get('id')
                        vec_net.name = json_net.get('name')
        
                        # wires
                        vec_net.wire_num = json_net.get('wire_num')
                        json_wires = json_net.get('wires', [])
                        for json_wire in json_wires:
                            vec_wire = VectorWire()
                            vec_wire.id = json_wire.get('id')
        
                            # wire feature
                            wire_feature = VectorWireFeature()
                            feature = json_wire.get('feature', {})
                            wire_feature.wire_len = feature.get('wire_len')
        
                            vec_wire.feature = wire_feature
        
                            # path
                            vec_wire.path_num = json_wire.get('path_num')
                            json_paths = json_wire.get('paths', [])
                            for json_path in json_paths:
                                wire_path = VectorPath()
        
                                vec_path_node1 = VectorNode()
                                vec_path_node1.id = json_path.get('id1')
                                vec_path_node1.x = json_path.get('x1')
                                vec_path_node1.y = json_path.get('y1')
                                vec_path_node1.row = json_path.get('r1')
                                vec_path_node1.col = json_path.get('c1')
                                vec_path_node1.layer = json_path.get('l1')
                                vec_path_node1.pin_id = json_path.get('p1')
                                wire_path.node1 = vec_path_node1
        
                                vec_path_node2 = VectorNode()
                                vec_path_node2.id = json_path.get('id2')
                                vec_path_node2.x = json_path.get('x2')
                                vec_path_node2.y = json_path.get('y2')
                                vec_path_node2.row = json_path.get('r2')
                                vec_path_node2.col = json_path.get('c2')
                                vec_path_node2.layer = json_path.get('l2')
                                vec_path_node2.pin_id = json_path.get('p2')
                                wire_path.node2 = vec_path_node2
        
                                vec_wire.paths.append(wire_path)
        
                            vec_net.wires.append(vec_wire)
        
                        patch_layer.nets.append(vec_net)
        
                    vec_patch.patch_layer.append(patch_layer)
                
                vec_patchs.append(vec_patch)
    
        return vec_patchs
    
from typing import List, Dict, Tuple, Any
from collections import defaultdict
from math import gcd
from tqdm import tqdm
import networkx as nx
from dataclasses import asdict
import pandas as pd
import json
import os
class VectorWirePatternGen:
    def __init__(self, epsilon: int = 1):
        self._epsilon = epsilon
        self._patterns: Dict[str, VectorWirePatternSeq] = {}
        self._pattern_count: Dict[str, int] = defaultdict(int)

    def generate(self, csv_path: str = None) -> pd.DataFrame:
        df = pd.DataFrame(self._pattern_count.items(),
                          columns=["Pattern", "Count"])
        df.sort_values(by="Count", ascending=False,
                       inplace=True, ignore_index=True)
        if csv_path:
            df.to_csv(csv_path, index=False)
        return df

    def add_wire(self, wire: VectorWire) -> VectorWirePatternSeq:
        pattern = self.gen_pattern(wire)
        self.add_pattern(pattern)
        return pattern

    def add_pattern(self, pattern: VectorWirePatternSeq):
        if pattern.name in self._pattern_count:
            self._pattern_count[pattern.name] += 1
        else:
            self._patterns[pattern.name] = pattern
            self._pattern_count[pattern.name] = 1

    def gen_pattern(self, wire: VectorWire) -> VectorWirePatternSeq:
        point_list = self._get_point_list(wire)
        pattern = self._calc_pattern(point_list)
        return pattern

    def _get_point_list(self, wire: VectorWire) -> List[VectorWirePatternPoint]:
        paths = wire.paths
        points = [
            VectorWirePatternPoint(path.node1.x, path.node1.y, path.node1.layer)
            for path in paths
        ]
        end = VectorWirePatternPoint(
            paths[-1].node2.x, paths[-1].node2.y, paths[-1].node2.layer
        )
        points.append(end)
        return points

    def _calc_pattern(self, points: List[VectorWirePatternPoint]) -> VectorWirePatternSeq:
        sorted_points = points[:]
        if sorted_points[0].x > sorted_points[-1].x or (
            sorted_points[0].x == sorted_points[-1].x
            and sorted_points[0].y > sorted_points[-1].y
        ):
            sorted_points.reverse()

        pattern = VectorWirePatternSeq()
        for i in range(len(sorted_points) - 1):
            start = sorted_points[i]
            end = sorted_points[i + 1]
            x_same = start.x == end.x
            y_same = start.y == end.y
            z_same = start.z == end.z
            if x_same and y_same and z_same:
                continue

            if x_same and y_same:
                direction = VectorWirePatternDirection.VIA
                length = 1
            elif x_same:
                direction = (
                    VectorWirePatternDirection.TOP
                    if start.y < end.y
                    else VectorWirePatternDirection.BOTTOM
                )
                length = abs(start.y - end.y)
            else:
                direction = (
                    VectorWirePatternDirection.RIGHT
                    if start.x < end.x
                    else VectorWirePatternDirection.LEFT
                )
                length = abs(start.x - end.x)

            pattern.units.append(VectorWirePatternUnit(direction, length))

        if not pattern.units:
            return pattern

        max_common_factor = pattern.units[0].length
        for unit in pattern.units:
            max_common_factor = gcd(max_common_factor, unit.length)

        for unit in pattern.units:
            unit.length //= max_common_factor

        pattern_name = ""
        for unit in pattern.units:
            direction = unit.direction.name[0]
            normalized_length = unit.length // self._epsilon + 1
            pattern_name += f"{direction}{normalized_length}"

        pattern.name = pattern_name
        return pattern


class VectorNetSeqConverter:
    def __init__(self, epsilon: int = 1):
        self._gen = VectorWirePatternGen(epsilon=epsilon)
        self._seqs = []

    def build_seqs(self, vec_nets: List[VectorNet]) -> List[VectorNetSeq]:
        for vec_net in vec_nets:
            graph = self._convert(vec_net)
            seqs = self._convert_to_seq(graph)
            self._seqs.extend(seqs)
        return self._seqs

    def save_seqs(self, json_path: str):
        with open(json_path, "w") as f:
            json.dump(self._seqs, f, default=asdict)

    def load_seqs(self, json_path: str) -> List[VectorNetSeq]:
        with open(json_path, "r") as f:
            self._seqs = json.load(f)
        return self._seqs

    def _convert(self, vec_net: VectorNet) -> nx.Graph:
        # edge with pattern
        graph = nx.Graph()
        wires = vec_net.wires
        for wire in wires:
            wire: VectorWire
            start = wire.wire.node1
            end = wire.wire.node2

            pattern = self._gen.add_wire(wire)
            pattern_name = pattern.name
            if start.id not in graph:
                graph.add_node(start.id, pos=(start.x, start.y, start.layer))
            if end.id not in graph:
                graph.add_node(end.id, pos=(end.x, end.y, end.layer))
            graph.add_edge(start.id, end.id, pattern=pattern_name)

        return graph

    def _convert_to_seq(self, net_graph: nx.Graph) -> List[VectorNetSeq]:
        seqs = []
        source = 0
        for node in net_graph.nodes:
            if net_graph.degree(node) == 1:
                source = node
                break
        targets = []
        for node in net_graph.nodes:
            if net_graph.degree(node) == 1 and node != source:
                targets.append(node)
        for target in targets:
            loc_seq = []
            pattern_seq = []
            path = nx.shortest_path(net_graph, source, target)
            for vertex in path:
                pos = net_graph.nodes[vertex]["pos"]
                loc_seq.append(VectorWirePatternPoint(pos[0], pos[1], pos[2]))
            for i in range(1, len(path)):
                pattern = net_graph[path[i - 1]][path[i]]["pattern"]
                pattern_seq.append(pattern)
            seq = VectorNetSeq(loc_seq, pattern_seq)
            seqs.append(seq)
        return seqs


class VectorTimingGraphSeqConverter:
    def __init__(self, epsilon: int = 1):
        self._gen = VectorWirePatternGen(epsilon=epsilon)
        self._seqs = []

    def convert(self, timing_wire_graph : VectorTimingWireGraph, vec_nets: List[VectorNet]) -> nx.Graph:
        nodes = timing_wire_graph.nodes
        edges = timing_wire_graph.edges
        graph = nx.Graph()
        # build nodes
        for node in nodes:
            graph.add_node(node.name, is_pin=node.is_pin, is_port=node.is_port)
        # build edges
        wire_map = self._build_wire_map(vec_nets)
        for edge in edges:
            from_node = nodes[edge.from_node]
            to_node = nodes[edge.to_node]
            key = (
                (int)(from_node.name.split(":")[1]),
                (int)(to_node.name.split(":")[1]),
            )
            pattern = "" if key not in wire_map else self._gen.add_wire(
                wire_map[key])
            graph.add_edge(
                from_node.name,
                to_node.name,
                feature_R=edge.feature_R,
                feature_C=edge.feature_C,
                feature_from_slew=edge.feature_from_slew,
                feature_to_slew=edge.feature_to_slew,
                is_net_edge=edge.is_net_edge,
                pattern=pattern,
            )
        return graph

    def convert_to_seq(self, graph: nx.Graph) -> List[VectorNetSeq]:
        seqs = []
        pass

    def _build_wire_map(self, vec_nets: List[VectorNet]) -> Dict[Tuple[int, int], VectorWire]:
        wire_map = {}
        for vec_net in vec_nets:
            wires = vec_net.wires
            for wire in wires:
                wire: VectorWire
                start = wire.wire.node1.id
                end = wire.wire.node2.id
                wire_map[(start, end)] = wire
                wire_map[(end, start)] = wire
        return wire_map


class VectorTimingWireGraphParser:
    """The parser for vector wire timing graph."""
    def __init__(self, yaml_path : str, logger: Logger = None):
        self.yaml_path = yaml_path
        self.logger = logger

    def get_wire_graph(self) -> VectorTimingWireGraph:
        if not os.path.exists(self.yaml_path):
            return None

        with open(self.yaml_path, "r") as file:
            self.logger.info("load wire graph yaml %s", self.yaml_path)
            
            lines = file.readlines()
            
            wire_nodes = []
            wire_edges = []

            wire_node = None
            wire_edge = None
            edge_set = set()
            for _, line in tqdm(
                enumerate(lines), total=len(lines), desc="load wire graph"
            ):
                line = line.strip()
                if line.startswith("node_"):
                    if wire_node is not None:
                        wire_nodes.append(wire_node)
                        wire_node = None
                elif line.startswith("edge_"):
                    # add last node
                    if wire_node is not None:
                        wire_nodes.append(wire_node)
                        wire_node = None

                    if wire_edge is not None:
                        if not (wire_edge.from_node, wire_edge.to_node) in edge_set:
                            wire_edges.append(wire_edge)
                            edge_set.add(
                                (wire_edge.from_node, wire_edge.to_node))
                        wire_edge = None
                else:
                    # Split at the first colon only
                    key, value = line.split(":", 1)
                    if key == "name":
                        wire_node = VectorTimingWireGraphNode(
                            value.strip(), False, False)
                    elif key == "is_pin":
                        wire_node.is_pin = True if int(
                            value.strip()) == 1 else False
                    elif key == "is_port":
                        wire_node.is_port = True if int(
                            value.strip()) == 1 else False
                    elif key == "from_node":
                        wire_edge = VectorTimingWireGraphEdge(
                            int(value.strip()), None)
                    elif key == "to_node":
                        wire_edge.to_node = int(value.strip())
                    elif key == "is_net_edge":
                        wire_edge.is_net_edge = bool(value.strip())

            # add last edge
            wire_edges.append(wire_edge)
            wire_timing_graph = VectorTimingWireGraph(wire_nodes, wire_edges)

            self.logger.info("load wire graph yaml end")
            self.logger.info("wire graph nodes num: %d", len(wire_nodes))
            self.logger.info("wire graph edges num: %d", len(wire_edges))
            return wire_timing_graph

        return None