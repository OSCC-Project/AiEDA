#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : layout.py
@Author : yell
@Desc : show layout
"""
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import random

from aieda import Workspace, DataVectors


class GuiLayout:
    def __init__(self, workspace: Workspace):
        self.workspace = workspace

    def instance_graph(self, fig_path: str):
        data_load = DataVectors(self.workspace)

        timing_graph = data_load.load_instance_graph()
        nodes = timing_graph.nodes
        edges = timing_graph.edges

        # read cells data to map cell_id to cell name
        cell_id_to_name = {}
        vec_cells = data_load.load_cells()
        for cell in vec_cells.cells:
            cell_id_to_name[cell.id] = cell.name

        # create instance name to instance data mapping
        vec_instances = data_load.load_instances()
        instance_name_to_data = {}
        for instance in vec_instances.instances:
            instance_name_to_data[instance.name] = instance

        # create image with larger size to accommodate legend
        fig, ax = plt.subplots(figsize=(20, 14))
        ax.set_title(f"{self.workspace.design} - Instance Graph", fontsize=16)

        # calculate image range
        x_coords = [inst.x for inst in vec_instances.instances]
        y_coords = [inst.y for inst in vec_instances.instances]
        widths = [inst.width for inst in vec_instances.instances]
        heights = [inst.height for inst in vec_instances.instances]

        min_x = min([x for x, w in zip(x_coords, widths)])
        max_x = max([x + w for x, w in zip(x_coords, widths)])
        min_y = min([y for y, h in zip(y_coords, heights)])
        max_y = max([y + h for y, h in zip(y_coords, heights)])

        # categorize instances by cell_id for better color coding
        cell_id_to_color = {}
        cell_id_count = {}

        # count instances per cell_id
        for instance in vec_instances.instances:
            cell_id = instance.cell_id
            cell_id_count[cell_id] = cell_id_count.get(cell_id, 0) + 1

        # generate colors for cell types
        unique_cell_ids = list(cell_id_count.keys())
        random.seed(42)
        colors = plt.cm.Set3(np.linspace(0, 1, len(unique_cell_ids)))

        for i, cell_id in enumerate(unique_cell_ids):
            cell_id_to_color[cell_id] = colors[i]

        # draw instance rectangles with categorized colors
        drawn_count = 0
        legend_handles = []
        legend_labels = []
        used_cell_ids = set()

        for instance in vec_instances.instances:
            # calculate rectangle parameters
            x = instance.x
            y = instance.y
            width = instance.width
            height = instance.height

            # get color based on cell_id
            cell_id = instance.cell_id
            color = cell_id_to_color.get(cell_id, (0.8, 0.8, 0.8, 0.7))

            # draw rectangle
            rect = patches.Rectangle(
                (x, y), width, height, linewidth=0.5, edgecolor="black", facecolor=color
            )
            ax.add_patch(rect)
            drawn_count += 1

            # add to legend if not already added
            if cell_id not in used_cell_ids:
                # get cell name from mapping, fallback to cell_id if not found
                cell_name = cell_id_to_name.get(cell_id, f"Cell_ID_{cell_id}")
                legend_handles.append(
                    patches.Patch(
                        color=color,
                        label=f"{cell_name} ({cell_id_count[cell_id]} instances)",
                    )
                )
                legend_labels.append(
                    f"{cell_name} ({cell_id_count[cell_id]} instances)"
                )
                used_cell_ids.add(cell_id)

        # draw node connection relations (improved edge drawing)
        edges_drawn = 0

        # create node id to node data mapping
        node_id_to_node = {node.id: node for node in nodes}

        # create node name to node data mapping for reverse lookup
        node_name_to_data = {node.name: node for node in nodes}

        # find edges that connect instances in our data
        valid_edges = []
        for edge in edges:
            from_node_id = edge.from_node
            to_node_id = edge.to_node

            # get node data - handle both string and integer node IDs
            from_node = None
            to_node = None

            # try to find by node ID (could be string or integer)
            if from_node_id in node_id_to_node:
                from_node = node_id_to_node[from_node_id]
            elif str(from_node_id) in node_id_to_node:
                from_node = node_id_to_node[str(from_node_id)]
            elif f"node_{from_node_id}" in node_id_to_node:
                from_node = node_id_to_node[f"node_{from_node_id}"]

            if to_node_id in node_id_to_node:
                to_node = node_id_to_node[to_node_id]
            elif str(to_node_id) in node_id_to_node:
                to_node = node_id_to_node[str(to_node_id)]
            elif f"node_{to_node_id}" in node_id_to_node:
                to_node = node_id_to_node[f"node_{to_node_id}"]

            if from_node and to_node:
                from_name = from_node.name
                to_name = to_node.name

                # check if both instances exist in our data
                if (
                    from_name in instance_name_to_data
                    and to_name in instance_name_to_data
                ):
                    valid_edges.append(edge)

        self.workspace.logger.info(
            "found {} valid edges connecting instances".format(len(valid_edges))
        )

        # limit display edge number, avoid too many edges affecting visualization
        max_edges = 2000  # increased limit
        if len(valid_edges) > max_edges:
            # random select edges for display
            selected_edges = random.sample(valid_edges, max_edges)
            self.workspace.logger.info(
                f"edge number too many({len(valid_edges)}), random select {max_edges} edges for display"
            )
        else:
            selected_edges = valid_edges

        # draw edges with better visibility
        for edge in selected_edges:
            from_node_id = edge.from_node
            to_node_id = edge.to_node

            # get node data - handle both string and integer node IDs
            from_node = None
            to_node = None

            # try to find by node ID (could be string or integer)
            if from_node_id in node_id_to_node:
                from_node = node_id_to_node[from_node_id]
            elif str(from_node_id) in node_id_to_node:
                from_node = node_id_to_node[str(from_node_id)]
            elif f"node_{from_node_id}" in node_id_to_node:
                from_node = node_id_to_node[f"node_{from_node_id}"]

            if to_node_id in node_id_to_node:
                to_node = node_id_to_node[to_node_id]
            elif str(to_node_id) in node_id_to_node:
                to_node = node_id_to_node[str(to_node_id)]
            elif f"node_{to_node_id}" in node_id_to_node:
                to_node = node_id_to_node[f"node_{to_node_id}"]

            if from_node and to_node:
                from_name = from_node.name
                to_name = to_node.name

                # get instance data
                from_instance = instance_name_to_data.get(from_name)
                to_instance = instance_name_to_data.get(to_name)

                if from_instance and to_instance:
                    # draw connection line with better visibility
                    ax.plot(
                        [
                            from_instance.x + from_instance.width / 2,
                            to_instance.x + to_instance.width / 2,
                        ],
                        [
                            from_instance.y + from_instance.height / 2,
                            to_instance.y + to_instance.height / 2,
                        ],
                        "-",
                        linewidth=0.5,
                        alpha=0.4,
                        color="blue",
                    )
                    edges_drawn += 1

        self.workspace.logger.info(f"draw {edges_drawn} connection lines")

        # set axis range
        margin = max(max_x - min_x, max_y - min_y) * 0.05
        ax.set_xlim(min_x - margin, max_x + margin)
        ax.set_ylim(min_y - margin, max_y + margin)

        ax.set_xlabel("X", fontsize=12)
        ax.set_ylabel("Y", fontsize=12)
        ax.set_aspect("equal")

        # add legend outside the plot
        # sort legend by instance count (descending)
        legend_data = [
            (handle, label) for handle, label in zip(legend_handles, legend_labels)
        ]
        legend_data.sort(
            key=lambda x: int(x[1].split("(")[1].split(" ")[0]), reverse=True
        )

        # limit legend items to top 20 to avoid overcrowding
        max_legend_items = 20
        if len(legend_data) > max_legend_items:
            legend_data = legend_data[:max_legend_items]
            legend_data.append(
                (
                    patches.Patch(color="gray", alpha=0.5),
                    f"... and {len(legend_data) - max_legend_items} more types",
                )
            )

        legend_handles = [item[0] for item in legend_data]
        legend_labels = [item[1] for item in legend_data]

        # place legend outside the plot
        ax.legend(
            handles=legend_handles,
            labels=legend_labels,
            loc="center left",
            bbox_to_anchor=(1.02, 0.5),
            fontsize=10,
            title="Cell Distribution",
            title_fontsize=12,
        )

        # add info text above the legend
        info_text = (
            f"Instance Count: {len(vec_instances.instances)}\n"
            f"Cell Types: {len(used_cell_ids)}\n"
            f"Total Nodes: {len(nodes)}\n"
            f"Total Edges: {len(edges)}\n"
            f"Valid Edges: {len(valid_edges)}\n"
            f"Displayed Edges: {edges_drawn}\n"
            f"Layout Range: {max_x-min_x:.0f} x {max_y-min_y:.0f}"
        )
        # place info text above the legend
        fig.text(
            0.78,
            0.95,
            info_text,
            fontsize=13,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
        )

        # save image with adjusted layout to accommodate legend
        plt.tight_layout()
        plt.subplots_adjust(right=0.75)  # make room for legend
        plt.savefig(fig_path, dpi=300, bbox_inches="tight")
        plt.close(fig)

        self.workspace.logger.info(f"instance graph image is saved to: {fig_path}")
