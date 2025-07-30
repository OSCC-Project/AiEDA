#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : pattern_io.py
@Author : yell
@Desc : pattern parser
'''

from ...utility.log import Logger
from ..database import *
from ...utility.json_parser import JsonParser
   
from typing import List, Dict, Tuple, Any
from collections import defaultdict
from math import gcd
from tqdm import tqdm
import networkx as nx
import pandas as pd

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

class VectorWirePatterns:
    def __init__(self, patterns_csv: str, logger : Logger, epsilon: int = 1):
        self.patterns_csv = patterns_csv
        self.logger = logger
        self.epsilon = epsilon
    
    def generate(self, vec_nets: List[VectorNet]):
        wire_patterns_gen = VectorWirePatternGen(epsilon=self.epsilon)

        for _, vec_net in tqdm(enumerate(vec_nets), total=len(vec_nets), desc="build vector net wires"):
            wires = vec_net.wires
            for wire in wires:
                wire_patterns_gen.add_wire(wire)

        wire_patterns_gen.generate(self.patterns_csv)
    

class VectorWireSequences(JsonParser):
    def __init__(self, json_path: str, logger : Logger, epsilon: int = 1):
        self.epsilon = epsilon
        super().__init__(json_path=json_path, logger=logger)

    def generate(self, vec_nets: List[VectorNet]):
        gen = VectorWirePatternGen(epsilon=self.epsilon)
        sequences = []
        
        def _convert(vec_net: VectorNet) -> nx.Graph:
            # edge with pattern
            graph = nx.Graph()
            wires = vec_net.wires
            for wire in wires:
                wire: VectorWire
                start = wire.wire.node1
                end = wire.wire.node2
    
                pattern = gen.add_wire(wire)
                pattern_name = pattern.name
                if start.id not in graph:
                    graph.add_node(start.id, pos=(start.x, start.y, start.layer))
                if end.id not in graph:
                    graph.add_node(end.id, pos=(end.x, end.y, end.layer))
                graph.add_edge(start.id, end.id, pattern=pattern_name)
    
            return graph
    
        def _convert_to_seq(net_graph: nx.Graph) -> List[VectorNetSeq]:
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
        
        if self.create():
            for _, vec_net in tqdm(enumerate(vec_nets), total=len(vec_nets), desc="transform vector nets"):
                graph = _convert(vec_net)
                seqs = _convert_to_seq(graph)
                sequences.extend(seqs)

            #save files
            return self.write(dict_value=sequences, is_db=True, indent=None)
        
        return False

    def load_sequences(self) -> List[VectorNetSeq]:
        sequences = []
        
        if self.read(is_db=True):
            sequences=self.json_data
            
        return sequences


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