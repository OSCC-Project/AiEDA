#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : test_gui.py
@Author : RuiWang
@Desc : test gui for instance layout visualization
'''

######################################################################################
# import aieda
from import_aieda import import_aieda
import_aieda()
######################################################################################

from aieda import (
    workspace_create,
    DbFlow,
    DataGeneration,
    DataVectors
)

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import random
import os
from pathlib import Path


LIB_PATHS = [
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp30p140ssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp30p140hvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp30p140lvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp30p140mbssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp30p140mblvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp30p140oppssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp30p140opphvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp30p140opplvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp30p140oppuhvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp30p140oppulvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp30p140uhvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp35p140ssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp35p140hvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp35p140lvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp35p140mbssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp35p140mblvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp35p140oppssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp35p140opphvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp35p140opplvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp35p140oppuhvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp35p140oppulvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp35p140uhvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp40p140ssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp40p140hvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp40p140lvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp40p140mbssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp40p140mbhvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp40p140oppssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp40p140opphvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp40p140opplvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp40p140oppuhvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp40p140uhvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp35p140mbhvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp30p140ulvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tcbn28hpcplusbwp35p140ulvtssg0p81v125c_ccs.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta64x128m2f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta64x128m2fw_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta256x32m4fw_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta128x32m2f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta128x64m2f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta128x80m2f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta128x8m2f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta512x64m4f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta512x64m4fw_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta64x32m2f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta64x8m2f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta32x32m2f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta32x128m2f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta64x80m2f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta256x16m2f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts6n28hpcplvta512x2m8f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta8x144m2f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts6n28hpcplvta16x128m2f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta8x128m2f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta64x64m2f_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta1024x32m8fw_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta256x144m2fw_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/ts5n28hpcplvta128x144m2fw_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/tphn28hpcpgv18ssg0p81v1p62v125c.lib",
    "/data/project_share/process_node/dataset_baseline/lib/PLLTS28HPMLAINT_SS_0P81_125C.lib",
    "/data/project_share/process_node/T28_lib/ccslib/RocketTile_postroute_func_ssg0p81vm40c_cworst_T_setup.lib",
    "/data/project_share/process_node/T28_lib/ccslib/ts6n28hpcplvta2048x32m8sw_130a_ssg0p81vm40c.lib",
    "/data/project_share/process_node/T28_lib/ccslib/ts1n28hpcplvtb2048x48m8sw_180a_ssg0p81vm40c.lib",
    "/data/project_share/process_node/T28_lib/ccslib/ts1n28hpcplvtb8192x64m8sw_180a_ssg0p81vm40c.lib",
    "/data/project_share/process_node/T28_lib/mem/ts5n28hpcplvta256x64m2fw_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/T28_lib/mem/ts1n28hpcplvtb1024x64m4sw_180a_ssg0p81v125c.lib",
    "/data/project_share/process_node/T28_lib/mem/ts5n28hpcplvta256x128m2fw_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/beihai/lib/ts5n28hpcplvta64x88m2fw_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/beihai/lib/ts5n28hpcplvta512x64m4sw_130a_ssg0p81v125c.lib",
    "/data/project_share/process_node/beihai/lib/ts5n28hpcplvta64x84m2fw_130a_ssg0p81v125c.lib"
]

def test_instance_visualization(workspace_dir: str):
    """
    visualize instance layout using vectors_io functions
    
    Args:
        workspace_dir: workspace directory path
    """
    print(f"start instance layout visualization for workspace: {workspace_dir}")
    
    # extract design name from workspace path
    design = workspace_dir.split("/")[-2]
    print(f"design name: {design}")
    
    # construct file paths automatically
    vectors_dir = f"{workspace_dir}/output/iEDA/vectors"
    instance_graph_path = f"{vectors_dir}/instance_graph/timing_instance_graph.json"
    instances_path = f"{vectors_dir}/instances/instances.json"
    cells_path = f"{vectors_dir}/cells/cells.json"
    
    # output path will be saved in instance_graph directory
    output_path = f"{vectors_dir}/instance_graph/{design}_place_layout.png"
    
    print(f"instance graph file: {instance_graph_path}")
    print(f"instances file: {instances_path}")
    print(f"cells file: {cells_path}")
    print(f"output path: {output_path}")
    
    # check if required files exist
    if not os.path.exists(instance_graph_path):
        print(f"error: instance graph file not found: {instance_graph_path}")
        return
    if not os.path.exists(instances_path):
        print(f"error: instances file not found: {instances_path}")
        return
    if not os.path.exists(cells_path):
        print(f"warning: cells file not found: {cells_path}")
    
    from aieda.data.io.vectors_io import VectorsParserJson
    
    # read instance graph data using get_wire_graph
    try:
        graph_parser = VectorsParserJson(instance_graph_path)
        wire_graph = graph_parser.get_wire_graph()
        if wire_graph is None:
            print("failed to read wire graph data")
            return
        
        nodes = wire_graph.nodes
        edges = wire_graph.edges
        print(f"read wire graph data success: {len(nodes)} nodes, {len(edges)} edges")
    except Exception as e:
        print(f"read wire graph file failed: {e}")
        return
    
    # read instances data using get_instances
    try:
        instances_parser = VectorsParserJson(instances_path)
        instances_data = instances_parser.get_instances()
        if instances_data is None:
            print("failed to read instances data")
            return
        
        print(f"read instances data success: {instances_data.instance_num} instances")
    except Exception as e:
        print(f"read instances file failed: {e}")
        return
    
    # read cells data to map cell_id to cell name
    cell_id_to_name = {}
    try:
        cells_parser = VectorsParserJson(cells_path)
        cells_data = cells_parser.get_cells()
        if cells_data is not None:
            for cell in cells_data.cells:
                cell_id_to_name[cell.id] = cell.name
            print(f"read cells data success: {len(cells_data.cells)} cells")
        else:
            print("warning: failed to read cells data, will use cell_id in legend")
    except Exception as e:
        print(f"warning: read cells file failed: {e}, will use cell_id in legend")
    
    # create instance name to instance data mapping
    instance_name_to_data = {}
    for instance in instances_data.instances:
        instance_name_to_data[instance.name] = instance
    
    # get design name from path for title
    tool_name = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(instances_path))))
    
    # create image with larger size to accommodate legend
    fig, ax = plt.subplots(figsize=(20, 14))
    ax.set_title(f"{design}_{tool_name} - Instance Layout Visualization (Total: {len(instances_data.instances)} instances)", fontsize=16)
    
    # get all instances for image range
    instances = instances_data.instances
    if not instances:
        print("no instances data")
        return
    
    # calculate image range
    x_coords = [inst.x for inst in instances]
    y_coords = [inst.y for inst in instances]  
    widths = [inst.width for inst in instances]
    heights = [inst.height for inst in instances]
    
    min_x = min([x - w/2 for x, w in zip(x_coords, widths)])
    max_x = max([x + w/2 for x, w in zip(x_coords, widths)])
    min_y = min([y - h/2 for y, h in zip(y_coords, heights)])
    max_y = max([y + h/2 for y, h in zip(y_coords, heights)])
    
    # categorize instances by cell_id for better color coding
    cell_id_to_color = {}
    cell_id_count = {}
    
    # count instances per cell_id
    for instance in instances:
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
    
    for instance in instances:
        # calculate rectangle parameters
        x = instance.x - instance.width / 2
        y = instance.y - instance.height / 2
        width = instance.width
        height = instance.height
        
        # get color based on cell_id
        cell_id = instance.cell_id
        color = cell_id_to_color.get(cell_id, (0.8, 0.8, 0.8, 0.7))
        
        # draw rectangle
        rect = patches.Rectangle((x, y), width, height, 
                               linewidth=0.5, edgecolor='black', facecolor=color)
        ax.add_patch(rect)
        drawn_count += 1
        
        # add to legend if not already added
        if cell_id not in used_cell_ids:
            # get cell name from mapping, fallback to cell_id if not found
            cell_name = cell_id_to_name.get(cell_id, f"Cell_ID_{cell_id}")
            legend_handles.append(patches.Patch(color=color, label=f"{cell_name} ({cell_id_count[cell_id]} instances)"))
            legend_labels.append(f"{cell_name} ({cell_id_count[cell_id]} instances)")
            used_cell_ids.add(cell_id)
    
    print(f"draw {drawn_count} instances with {len(used_cell_ids)} different cell types")
    
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
            if from_name in instance_name_to_data and to_name in instance_name_to_data:
                valid_edges.append(edge)
    
    print(f"found {len(valid_edges)} valid edges connecting instances")
    
    # limit display edge number, avoid too many edges affecting visualization
    max_edges = 2000  # increased limit
    if len(valid_edges) > max_edges:
        # random select edges for display
        selected_edges = random.sample(valid_edges, max_edges)
        print(f"edge number too many({len(valid_edges)}), random select {max_edges} edges for display")
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
                ax.plot([from_instance.x, to_instance.x], 
                       [from_instance.y, to_instance.y], 
                       '-', linewidth=0.5, alpha=0.4, color='blue')
                edges_drawn += 1
    
    print(f"draw {edges_drawn} connection lines")
    
    # set axis range
    margin = max(max_x - min_x, max_y - min_y) * 0.05
    ax.set_xlim(min_x - margin, max_x + margin)
    ax.set_ylim(min_y - margin, max_y + margin)
    
    ax.set_xlabel('X', fontsize=12)
    ax.set_ylabel('Y', fontsize=12)
    ax.set_aspect('equal')
    
    # add legend outside the plot
    # sort legend by instance count (descending)
    legend_data = [(handle, label) for handle, label in zip(legend_handles, legend_labels)]
    legend_data.sort(key=lambda x: int(x[1].split('(')[1].split(' ')[0]), reverse=True)
    
    # limit legend items to top 20 to avoid overcrowding
    max_legend_items = 20
    if len(legend_data) > max_legend_items:
        legend_data = legend_data[:max_legend_items]
        legend_data.append((patches.Patch(color='gray', alpha=0.5), f"... and {len(legend_data) - max_legend_items} more types"))
    
    legend_handles = [item[0] for item in legend_data]
    legend_labels = [item[1] for item in legend_data]
    
    # place legend outside the plot
    ax.legend(handles=legend_handles, labels=legend_labels, 
             loc='center left', bbox_to_anchor=(1.02, 0.5), 
             fontsize=10, title="Instance Types", title_fontsize=12)
    
    # add info text above the legend
    info_text = (
        f"Instance Count: {len(instances)}\n"
        f"Cell Types: {len(used_cell_ids)}\n"
        f"Total Nodes: {len(nodes)}\n"
        f"Total Edges: {len(edges)}\n"
        f"Valid Edges: {len(valid_edges)}\n"
        f"Displayed Edges: {edges_drawn}\n"
        f"Layout Range: {max_x-min_x:.0f} x {max_y-min_y:.0f}"
    )
    # place info text above the legend
    fig.text(0.78, 0.95, info_text, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # save image with adjusted layout to accommodate legend
    plt.tight_layout()
    plt.subplots_adjust(right=0.75)  # make room for legend
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"visualization done, image saved to: {output_path}")
    
if __name__ == "__main__":  
    # step 1 : create workspace
    # workspace_dir = "/data/project_share/dataset_baseline/eth_top/workspace"
    # workspace_dir = "/data2/project_share/dataset_baseline/s713/workspace"
    # workspace_dir = "/data/wangrui/aieda/workspace"
    # workspace = workspace_create(directory=workspace_dir, design="apb4_i2c")
    
    # test with a specific workspace
    # workspace_dir = "/data2/project_share/dataset_baseline/apb4_i2c/workspace"
    
    test_instance_visualization("/data2/huangzengrong/test_aieda/sky130_1")
    
    # # define workspaces to process
    # DESIGNS_T28 = [
    #     "/data2/project_share/dataset_baseline/s713/workspace",
    #     "/data2/project_share/dataset_baseline/s44/workspace",
    #     "/data2/project_share/dataset_baseline/apb4_i2c/workspace",
    # ]
    
    # for workspace_dir in DESIGNS_T28:
    #     print(f"\nprocessing workspace: {workspace_dir}")
    #     try:
    #         test_instance_visualization(workspace_dir)
    #         print(f"✓ visualization completed for {workspace_dir}")
    #     except Exception as e:
    #         print(f"✗ visualization failed for {workspace_dir}: {e}")
    #         continue

    exit(0)

