#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : vectors_io.py
@Author : yell
@Desc : parser for vectors
"""
import os
from tqdm import tqdm

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
                feature_data = net_metadata.get("feature", {})
                net_feature.llx = feature_data.get("llx")
                net_feature.lly = feature_data.get("lly")
                net_feature.urx = feature_data.get("urx")
                net_feature.ury = feature_data.get("ury")
                net_feature.wire_len = feature_data.get("wire_len")
                net_feature.via_num = feature_data.get("via_num")
                net_feature.drc_num = feature_data.get("drc_num")
                net_feature.R = feature_data.get("R")
                net_feature.C = feature_data.get("C")
                net_feature.power = feature_data.get("power")
                net_feature.delay = feature_data.get("delay")
                net_feature.slew = feature_data.get("slew")

                if "aspect_ratio" in feature_data:
                    net_feature.aspect_ratio = feature_data.get("aspect_ratio")
                    net_feature.width = feature_data.get("width")
                    net_feature.height = feature_data.get("height")
                    net_feature.area = feature_data.get("area")
                    net_feature.drc_type = feature_data.get("drc_type")
                    net_feature.volume = feature_data.get("volume")
                    net_feature.layer_ratio = feature_data.get("layer_ratio")

                # parse place_feature
                if "place_feature" in feature_data:
                    place_feature_data = feature_data.get("place_feature", {})
                    place_feature = VectorPlaceFeature()
                    place_feature.pin_num = place_feature_data.get("pin_num")
                    place_feature.aspect_ratio = place_feature_data.get("aspect_ratio")
                    place_feature.width = place_feature_data.get("width")
                    place_feature.height = place_feature_data.get("height")
                    place_feature.area = place_feature_data.get("area")
                    place_feature.l_ness = place_feature_data.get("l_ness")
                    place_feature.rsmt = place_feature_data.get("rsmt")
                    place_feature.hpwl = place_feature_data.get("hpwl")
                    net_feature.place_feature = place_feature

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
                    wire_feature.wire_density = wire_feature_data.get("wire_density")
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
                    
                    if "via" in wire_data:
                        wire_connections.via = wire_data.get("via")

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

                        if "via" in json_path:
                            wire_path.via = json_path.get("via")

                        vec_wire.paths.append(wire_path)

                    vec_net.wires.append(vec_wire)

                # routing graph
                routing_graph_data = net_metadata.get("routing_graph", {})
                vertices = []
                for v in routing_graph_data.get("vertices", []):
                    point = VectorNetRoutingPoint(
                        x=v["x"], y=v["y"], layer_id=v["layer_id"]
                    )
                    vertex = VectorNetRoutingVertex(
                        id=v["id"],
                        is_pin=v["is_pin"],
                        is_driver_pin=v["is_driver_pin"],
                        point=point,
                    )
                    vertices.append(vertex)

                edges = []
                for e in routing_graph_data.get("edges", []):
                    path = [VectorNetRoutingPoint(**p) for p in e["path"]]
                    edge = VectorNetRoutingEdge(
                        source_id=e["source_id"], target_id=e["target_id"], path=path
                    )
                    edges.append(edge)
                routing_graph = VectorNetRoutingGraph(vertices=vertices, edges=edges)
                vec_net.routing_graph = routing_graph

                vec_nets.append(vec_net)

        return vec_nets

    def get_patchs(self) -> list[VectorPatch]:
        vec_patchs = []
        if self.read():
            for json_patch in tqdm(
                self.json_data, total=len(self.json_data), desc="load patchs"
            ):

                vec_patch = VectorPatch()

                # patch
                vec_patch.id = json_patch.get("id")
                vec_patch.patch_id_row = json_patch.get("patch_id_row")
                vec_patch.patch_id_col = json_patch.get("patch_id_col")
                vec_patch.llx = json_patch.get("llx")
                vec_patch.lly = json_patch.get("lly")
                vec_patch.urx = json_patch.get("urx")
                vec_patch.ury = json_patch.get("ury")
                vec_patch.row_min = json_patch.get("row_min")
                vec_patch.row_max = json_patch.get("row_max")
                vec_patch.col_min = json_patch.get("col_min")
                vec_patch.col_max = json_patch.get("col_max")
                vec_patch.cell_density = json_patch.get("cell_density")
                vec_patch.pin_density = json_patch.get("pin_density")
                vec_patch.net_density = json_patch.get("net_density")
                vec_patch.macro_margin = json_patch.get("macro_margin")
                vec_patch.RUDY_congestion = json_patch.get("RUDY_congestion")
                vec_patch.EGR_congestion = json_patch.get("EGR_congestion")
                vec_patch.timing_map = json_patch.get("timing_map")
                vec_patch.power_map = json_patch.get("power_map")
                vec_patch.ir_drop_map = json_patch.get("IR_drop")

                # patch layer
                json_patch_layers = json_patch.get("patch_layer", [])
                for json_patch_layer in json_patch_layers:
                    patch_layer = VectorPatchLayer()
                    patch_layer.id = json_patch_layer.get("id")
                    patch_layer.net_num = json_patch_layer.get("net_num")
                    feature = json_patch_layer.get("feature", {})
                    patch_layer.wire_width = feature.get("wire_width")
                    patch_layer.wire_len = feature.get("wire_len")
                    patch_layer.wire_density = feature.get("wire_density")
                    patch_layer.congestion = feature.get("congestion")

                    json_nets = json_patch_layer.get("nets", [])
                    for json_net in json_nets:
                        # net
                        vec_net = VectorNet()
                        vec_net.id = json_net.get("id")
                        vec_net.name = json_net.get("name")

                        # wires
                        vec_net.wire_num = json_net.get("wire_num")
                        json_wires = json_net.get("wires", [])
                        for json_wire in json_wires:
                            vec_wire = VectorWire()
                            vec_wire.id = json_wire.get("id")

                            # wire feature
                            wire_feature = VectorWireFeature()
                            feature = json_wire.get("feature", {})
                            wire_feature.wire_len = feature.get("wire_len")

                            vec_wire.feature = wire_feature

                            # path
                            vec_wire.path_num = json_wire.get("path_num")
                            json_paths = json_wire.get("paths", [])
                            for json_path in json_paths:
                                wire_path = VectorPath()

                                vec_path_node1 = VectorNode()
                                vec_path_node1.id = json_path.get("id1")
                                vec_path_node1.x = json_path.get("x1")
                                vec_path_node1.y = json_path.get("y1")
                                vec_path_node1.row = json_path.get("r1")
                                vec_path_node1.col = json_path.get("c1")
                                vec_path_node1.layer = json_path.get("l1")
                                vec_path_node1.pin_id = json_path.get("p1")
                                wire_path.node1 = vec_path_node1

                                vec_path_node2 = VectorNode()
                                vec_path_node2.id = json_path.get("id2")
                                vec_path_node2.x = json_path.get("x2")
                                vec_path_node2.y = json_path.get("y2")
                                vec_path_node2.row = json_path.get("r2")
                                vec_path_node2.col = json_path.get("c2")
                                vec_path_node2.layer = json_path.get("l2")
                                vec_path_node2.pin_id = json_path.get("p2")
                                wire_path.node2 = vec_path_node2

                                if "via" in json_path:
                                    wire_path.via = json_path.get("via")

                                vec_wire.paths.append(wire_path)

                            vec_net.wires.append(vec_wire)

                        patch_layer.nets.append(vec_net)

                    vec_patch.patch_layer.append(patch_layer)

                vec_patchs.append(vec_patch)

        return vec_patchs

    def get_cells(self) -> VectorCells:
        vec_cells = VectorCells()

        if self.read() is True:
            vec_cells.cell_num = self.json_data.get("cell_num")
            json_cells = self.json_data.get("cells", [])
            for json_cell in json_cells:
                vec_cell = VectorCell()
                vec_cell.id = json_cell.get("id")
                vec_cell.name = json_cell.get("name")
                vec_cell.width = json_cell.get("width")
                vec_cell.height = json_cell.get("height")

                vec_cells.cells.append(vec_cell)

        return vec_cells

    def get_layers(self) -> VectorLayers:
        vec_layers = VectorLayers()

        if self.read() is True:
            vec_layers.layer_num = self.json_data.get("layer_num")
            json_layers = self.json_data.get("layers", [])
            for json_layer in json_layers:
                vec_layer = VectorLayer()
                vec_layer.id = json_layer.get("id")
                vec_layer.name = json_layer.get("name")

                vec_layers.layers.append(vec_layer)

        return vec_layers

    def get_vias(self) -> VectorVias:
        vec_vias = VectorVias()

        if self.read() is True:
            vec_vias.via_num = self.json_data.get("via_num")
            json_vias = self.json_data.get("vias", [])
            for json_via in json_vias:
                vec_via = VectorVia()
                vec_via.id = json_via.get("id")
                vec_via.name = json_via.get("name")
                
                bottom_data = json_via.get("bottom")
                vec_via.bottom = VectorViaRect()
                vec_via.bottom.llx = bottom_data.get("llx")
                vec_via.bottom.lly = bottom_data.get("lly")
                vec_via.bottom.urx = bottom_data.get("urx")
                vec_via.bottom.ury = bottom_data.get("ury")
                
                cut_data = json_via.get("cut")
                vec_via.cut = VectorViaRect()
                vec_via.cut.llx = cut_data.get("llx")
                vec_via.cut.lly = cut_data.get("lly")
                vec_via.cut.urx = cut_data.get("urx")
                vec_via.cut.ury = cut_data.get("ury")
                
                top_data = json_via.get("top")
                vec_via.top = VectorViaRect()
                vec_via.top.llx = top_data.get("llx")
                vec_via.top.lly = top_data.get("lly")
                vec_via.top.urx = top_data.get("urx")
                vec_via.top.ury = top_data.get("ury")
                
                vec_via.row = json_via.get("row")
                vec_via.col = json_via.get("col")
                vec_via.bottom_direction = json_via.get("bottom_direction")
                vec_via.top_direction = json_via.get("top_direction")

                vec_vias.vias.append(vec_via)

        return vec_vias

    def get_instances(self) -> VectorInstances:
        vec_insts = VectorInstances()

        if self.read() is True:
            vec_insts.instance_num = self.json_data.get("instance_num")
            json_insts = self.json_data.get("instances", [])
            for json_inst in json_insts:
                vec_inst = VectorInstance()
                vec_inst.id = json_inst.get("id")
                vec_inst.cell_id = json_inst.get("cell_id")
                vec_inst.name = json_inst.get("name")
                vec_inst.cx = json_inst.get("cx")
                vec_inst.cy = json_inst.get("cy")
                vec_inst.width = json_inst.get("width")
                vec_inst.height = json_inst.get("height")
                vec_inst.llx = json_inst.get("llx")
                vec_inst.lly = json_inst.get("lly")
                vec_inst.urx = json_inst.get("urx")
                vec_inst.ury = json_inst.get("ury")

                vec_insts.instances.append(vec_inst)

        return vec_insts

    def get_wire_graph(self) -> VectorTimingWireGraph:
        if self.read() is True:
            wire_nodes = []
            wire_edges = []

            json_nodes = self.json_data.get("nodes")
            for json_node in tqdm(json_nodes, total=len(json_nodes), desc="load nodes"):
                wire_node = VectorTimingWireGraphNode()

                # patch
                wire_node.id = json_node.get("id")
                wire_node.name = json_node.get("name")
                wire_node.is_pin = json_node.get("is_pin")
                wire_node.is_port = json_node.get("is_port")

                wire_nodes.append(wire_node)

            json_edges = self.json_data.get("edges")
            for json_edge in tqdm(json_edges, total=len(json_edges), desc="load edges"):
                wire_edge = VectorTimingWireGraphEdge()

                # patch
                wire_edge.id = json_edge.get("id")
                wire_edge.from_node = json_edge.get("from_node")
                wire_edge.to_node = json_edge.get("to_node")
                wire_edge.is_net_edge = json_edge.get("is_net_edge")

                wire_edges.append(wire_edge)

            wire_timing_graph = VectorTimingWireGraph(wire_nodes, wire_edges)

            self.logger.info("load wire graph end")
            self.logger.info("wire graph nodes num: %d", len(wire_nodes))
            self.logger.info("wire graph edges num: %d", len(wire_edges))
            return wire_timing_graph

        return None

    class TimingWirePathData:
        def __init__(self):
            self.capacitance_list = []
            self.slew_list = []
            self.resistance_list = []
            self.incr_list = []

            # record path nodes
            self.nodes = []

        def get_combined_tensor(self):
            """Combine all lists into a single 2D tensor with each list as a row."""
            import torch

            combined_data = [
                self.capacitance_list,
                self.slew_list,
                self.resistance_list,
            ]
            tensor = torch.tensor(combined_data, dtype=torch.float32)
            return tensor

        def get_incr_tensor(self):
            """Get the tensor of Incr values and calculate the sum."""
            import torch

            incr_tensor = torch.tensor(self.incr_list, dtype=torch.float32)
            incr_sum = incr_tensor.sum().item()
            return incr_tensor, incr_sum

        @staticmethod
        def pad_tensors(tensor_list, max_length):
            """Pad all tensors in the list to the max length."""
            import torch

            padded_tensors = []
            for tensor in tensor_list:
                padded = torch.nn.functional.pad(
                    tensor, (0, max_length - tensor.size(1)), "constant", 0
                )
                padded_tensors.append(padded)
            return padded_tensors

        def generate_hash(self):
            """Generate a hash for the concatenated unique strings."""
            import hashlib

            concatenated = "".join(self.nodes)
            hash_object = hashlib.md5(concatenated.encode())
            return hash_object.hexdigest()

    def get_timing_wire_paths(self):
        """return :
        path_hash : unique hash string
        wire_path_graph : VectorTimingWirePathGraph
        """

        def get_path_data_package() -> self.TimingWirePathData:
            remove_parentheses_content = lambda s: (
                s[: s.find("(")].strip() if s.find("(") != -1 else s
            )

            if self.read() is True:
                path_data = self.TimingWirePathData()

                for json_item in self.json_data:
                    for key, json_value in json_item.items():
                        if key.startswith("node_"):

                            node_name = json_value.get("Point")
                            node_name = remove_parentheses_content(node_name)
                            path_data.nodes.append(node_name)
                            path_data.capacitance_list.append(
                                json_value.get("Capacitance", 0)
                            )
                            path_data.slew_list.append(json_value.get("slew", 0))
                            path_data.resistance_list.append(
                                0
                            )  # Default R value for nodes

                        elif key.startswith("net_arc_"):
                            path_data.incr_list.append(json_value.get("Incr", 0))
                            for edge_key, edge_value in json_value.items():
                                if edge_key.startswith("edge_"):
                                    path_data.capacitance_list.append(
                                        edge_value.get("wire_C", 0)
                                    )
                                    path_data.slew_list.append(
                                        edge_value.get("to_slew", 0)
                                    )
                                    path_data.resistance_list.append(
                                        edge_value.get("wire_R", 0)
                                    )

                                    # record edge node
                                    path_data.nodes.append(
                                        edge_value.get("wire_to_node", "")
                                    )

                        elif key.startswith("inst_arc_"):
                            path_data.incr_list.append(json_value.get("Incr", 0))

            return path_data

        def construct_path_graph(nodes) -> VectorTimingWirePathGraph:
            """construct a path graph from yaml data."""
            wire_path_nodes = []
            wire_path_edges = []
            for index, node_name in enumerate(nodes):
                parts = node_name.split(":")
                is_port = True if len(parts) == 1 else False
                is_pin = True if len(parts) == 2 and not parts[1].isdigit() else False
                wire_path_node = VectorTimingWireGraphNode(node_name, is_pin, is_port)
                wire_path_nodes.append(wire_path_node)

                if index > 0:
                    wire_path_edge = VectorTimingWireGraphEdge(index - 1, index)
                    wire_path_edges.append(wire_path_edge)

            wire_path_graph = VectorTimingWirePathGraph(
                wire_path_nodes, wire_path_edges
            )
            return wire_path_graph

        path_data_package = get_path_data_package()
        wire_path_graph = construct_path_graph(path_data_package.nodes)
        path_hash = path_data_package.generate_hash()

        return path_hash, wire_path_graph

    def get_timing_paths_metrics(self) -> VectorPathMetrics:

        path_data = VectorPathMetrics()
        if self.read() is True:
            for json_item in self.json_data:
                for key, json_value in json_item.items():
                    if key.startswith("node_"):
                        break

                    elif key.startswith("net_arc_"):
                        path_data.net_delay.append(json_value.get("Incr", 0))
                        # Find the last net_arc_ key
                        net_arc_keys = [
                            key
                            for key in json_item.keys()
                            if key.startswith("net_arc_")
                        ]

                    elif key.startswith("inst_arc_"):
                        path_data.inst_delay.append(json_value.get("Incr", 0))

            if net_arc_keys:
                last_net_arc_key = max(
                    net_arc_keys, key=lambda x: int(x.split("_")[-1])
                )
                path_data.stage = (int(last_net_arc_key.split("_")[-1]) + 1) / 2
            else:
                path_data.stage = None

        return path_data

    def get_instance_graph(self):
        if self.read() is True:
            instance_nodes = []
            instance_edges = []

            json_nodes = self.json_data.get("nodes")
            for json_node in tqdm(json_nodes, total=len(json_nodes), desc="load nodes"):
                instance_node = VectorInstanceGraphNode()

                # patch
                instance_node.id = json_node.get("id")
                instance_node.name = json_node.get("name")

                instance_nodes.append(instance_node)

            json_edges = self.json_data.get("edges")
            for json_edge in tqdm(json_edges, total=len(json_edges), desc="load edges"):
                instance_edge = VectorInstanceGraphEdge()

                # patch
                instance_edge.id = json_edge.get("id")
                instance_edge.from_node = json_edge.get("from_node")
                instance_edge.to_node = json_edge.get("to_node")

                instance_edges.append(instance_edge)

            instance_graph = VectorInstanceGraph(instance_nodes, instance_edges)

            self.logger.info("load instance graph end")
            self.logger.info("instance graph nodes num: %d", len(instance_nodes))
            self.logger.info("instance graph edges num: %d", len(instance_edges))
            return instance_graph

        return None
