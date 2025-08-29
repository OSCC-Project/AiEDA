#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : net.py
@Author : yhqiu
@Desc : net level data ananlysis, including wirelength distribution and metrics correlation
"""
import os
import json
import glob
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from multiprocessing import Pool, cpu_count
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
import time
import matplotlib as mpl

from .base import BaseAnalyzer
from ..workspace import Workspace

from aieda import DbFlow, DataVectors


# =====================================
# analyzer classes
# =====================================
class WireDistributionAnalyzer(BaseAnalyzer):
    """Analyzer for wirelength distribution."""

    def __init__(self):
        super().__init__()
        self.net_data = []

    def load(
        self,
        workspace_dirs: List[Workspace],
        dir_to_display_name: Optional[Dict[str, str]] = None,
        pattern: Optional[str] = None,
    ) -> None:
        """
        Load net data from multiple directories.

        Args:
            workspace_dirs: List of base directories containing net data
            dir_to_display_name: Optional mapping from directory names to display names
            pattern: File pattern to search for
        """
        self.dir_to_display_name = dir_to_display_name or {}
        self.workspace_dirs = workspace_dirs

        for workspace in workspace_dirs:
            design_name = workspace.design

            vector_loader = DataVectors(workspace)

            net_dir = workspace.directory + pattern

            net_db = vector_loader.load_nets(net_dir)

            net_list = []
            for vec_net in net_db:
                # Calculate HPWL
                llx = vec_net.feature.llx
                lly = vec_net.feature.lly
                urx = vec_net.feature.urx
                ury = vec_net.feature.ury
                hpwl = (urx - llx) + (ury - lly)

                # Get actual routed wirelength
                rwl = vec_net.feature.wire_len

                # Get other features
                r_value = vec_net.feature.R
                c_value = vec_net.feature.C
                power = vec_net.feature.power
                delay = vec_net.feature.delay
                slew = vec_net.feature.slew

                # Calculate wirelength per layer
                layer_lengths = [0] * 20  # Assume maximum 20 layers
                total_wire_length = 0

                for wire in vec_net.wires:
                    x1 = wire.wire.node1.x
                    y1 = wire.wire.node1.y
                    x2 = wire.wire.node2.x
                    y2 = wire.wire.node2.y
                    l1 = wire.wire.node1.layer
                    l2 = wire.wire.node2.layer

                    # Only consider wires on the same layer
                    if l1 == l2 and l1 < 20:
                        wire_length = abs(x2 - x1) + abs(y2 - y1)
                        layer_lengths[l1] += wire_length
                        total_wire_length += wire_length

                # Calculate layer wire length ratios
                layer_ratios = [0] * 20
                if total_wire_length > 0:
                    layer_ratios = [
                        length / total_wire_length for length in layer_lengths
                    ]

                net_list.append(
                    {
                        "hpwl": hpwl,
                        "rwl": rwl,
                        "R": r_value,
                        "C": c_value,
                        "power": power,
                        "delay": delay,
                        "slew": slew,
                        "layer_lengths": layer_lengths,
                        "layer_ratios": layer_ratios,
                    }
                )

            # create DataFrame for the design
            df = pd.DataFrame(
                {
                    "hpwl": [net["hpwl"] for net in net_list],
                    "rwl": [net["rwl"] for net in net_list],
                    "R": [net["R"] for net in net_list],
                    "C": [net["C"] for net in net_list],
                    "power": [net["power"] for net in net_list],
                    "delay": [net["delay"] for net in net_list],
                    "slew": [net["slew"] for net in net_list],
                }
            )

            total_layer_lengths = np.zeros(20)
            for net in net_list:
                total_layer_lengths += np.array(net["layer_lengths"])

            total_length = np.sum(total_layer_lengths)
            layer_proportions = (
                total_layer_lengths / total_length if total_length > 0 else np.zeros(20)
            )

            self.net_data.append(
                {
                    "df": df,
                    "design_name": design_name,
                    "layer_lengths": total_layer_lengths,
                    "layer_proportions": layer_proportions,
                }
            )

        if not self.net_data:
            raise ValueError("No valid results found from any directory.")

        print(f"Loaded data from {len(self.net_data)} directories.")

    def analyze(self) -> None:
        """
        Analyze the loaded net data.

        Args:
            verbose: Whether to show analysis progress
        """
        if not self.net_data:
            raise ValueError("No data loaded. Please call load() first.")

    def visualize(self, save_path: Optional[str] = None) -> None:
        """
        Visualize the net data.

        Args:
            save_path: Directory to save the visualizations
        """

        # Set up output directory
        if save_path is None:
            save_path = "."

        if self.workspace_dirs.__len__() == 1:
            save_path = self.workspace_dirs[0].paths_table.analysis_path
            print(f"Only one workspace, using save path: {save_path}")
        # Generate stacked bar chart for layer wire length proportions
        plt.figure(figsize=(5, 4))

        # Get design names with custom display names
        design_names = []
        for result in self.net_data:
            base_name = result["design_name"]
            display_name = self.dir_to_display_name.get(base_name, base_name)
            design_names.append(display_name)

        layer_data = np.array([r["layer_proportions"] for r in self.net_data])

        # Show only even layers (actual chip layers)
        layers_to_show = [0, 2, 4, 6, 8, 10, 12]

        # Create stacked bar chart
        bottom = np.zeros(len(self.net_data))
        for i in layers_to_show:
            if i < 20:  # Ensure layer index is within range
                layer_props = layer_data[:, i]
                if np.sum(layer_props) > 0:  # Only plot layers with data
                    plt.bar(
                        design_names, layer_props, bottom=bottom, label=f"Layer {i}"
                    )
                    bottom += layer_props

        plt.ylabel("Proportion of Wirelength")

        # Set x-axis labels to italic
        ax = plt.gca()
        for tick in ax.get_xticklabels():
            tick.set_style("italic")

        plt.legend(loc="upper right")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        # Save plot
        output_path = os.path.join(save_path, "net_wire_length_distribution.png")
        plt.savefig(output_path)
        plt.close()

        print(f"Layer distribution plot saved to {output_path}")


class MetricsCorrelationAnalyzer(BaseAnalyzer):
    """Analyzer for net features and statistics."""

    def __init__(self):
        super().__init__()
        self.net_data = []
        self.combined_df = None

    def load(
        self,
        workspace_dirs: List[str],
        dir_to_display_name: Optional[Dict[str, str]] = None,
        pattern: Optional[str] = None,
    ) -> None:
        """
        Load net feature data from multiple directories.

        Args:
            workspace_dirs: List of base directories containing net data
            dir_to_display_name: Optional mapping from directory names to display names
            pattern: File pattern to search for
        """
        self.dir_to_display_name = dir_to_display_name or {}
        self.workspace_dirs = workspace_dirs

        for workspace in workspace_dirs:
            design_name = workspace.design

            vector_loader = DataVectors(workspace)

            net_dir = workspace.directory + pattern

            net_db = vector_loader.load_nets(net_dir)

            net_list = []
            for vec_net in net_db:
                # Calculate HPWL
                llx = vec_net.feature.llx
                lly = vec_net.feature.lly
                urx = vec_net.feature.urx
                ury = vec_net.feature.ury
                hpwl = (urx - llx) + (ury - lly)

                # Get actual routed wirelength
                rwl = vec_net.feature.wire_len

                # Get other features
                r_value = vec_net.feature.R
                c_value = vec_net.feature.C
                power = vec_net.feature.power
                delay = vec_net.feature.delay
                slew = vec_net.feature.slew

                # Calculate wirelength per layer
                layer_lengths = [0] * 20  # Assume maximum 20 layers
                total_wire_length = 0

                for wire in vec_net.wires:
                    x1 = wire.wire.node1.x
                    y1 = wire.wire.node1.y
                    x2 = wire.wire.node2.x
                    y2 = wire.wire.node2.y
                    l1 = wire.wire.node1.layer
                    l2 = wire.wire.node2.layer

                    # Only consider wires on the same layer
                    if l1 == l2 and l1 < 20:
                        wire_length = abs(x2 - x1) + abs(y2 - y1)
                        layer_lengths[l1] += wire_length
                        total_wire_length += wire_length

                # Calculate layer wire length ratios
                layer_ratios = [0] * 20
                if total_wire_length > 0:
                    layer_ratios = [
                        length / total_wire_length for length in layer_lengths
                    ]

                net_list.append(
                    {
                        "hpwl": hpwl,
                        "rwl": rwl,
                        "R": r_value,
                        "C": c_value,
                        "power": power,
                        "delay": delay,
                        "slew": slew,
                        "layer_lengths": layer_lengths,
                        "layer_ratios": layer_ratios,
                    }
                )

            # create DataFrame for the design
            df = pd.DataFrame(
                {
                    "hpwl": [net["hpwl"] for net in net_list],
                    "rwl": [net["rwl"] for net in net_list],
                    "R": [net["R"] for net in net_list],
                    "C": [net["C"] for net in net_list],
                    "power": [net["power"] for net in net_list],
                    "delay": [net["delay"] for net in net_list],
                    "slew": [net["slew"] for net in net_list],
                }
            )

            total_layer_lengths = np.zeros(20)
            for net in net_list:
                total_layer_lengths += np.array(net["layer_lengths"])

            total_length = np.sum(total_layer_lengths)
            layer_proportions = (
                total_layer_lengths / total_length if total_length > 0 else np.zeros(20)
            )

            self.net_data.append(
                {
                    "df": df,
                    "design_name": design_name,
                    "layer_lengths": total_layer_lengths,
                    "layer_proportions": layer_proportions,
                }
            )

        if not self.net_data:
            raise ValueError("No valid results found from any directory.")

    def analyze(self, verbose: bool = True) -> None:
        """
        Analyze the loaded net feature data.

        Args:
            verbose: Whether to show analysis progress
        """
        if not self.net_data:
            raise ValueError("No data loaded. Please call load() first.")

        if verbose:
            print("Analyzing net features...")

        # Combine all design DataFrames for correlation analysis
        self.combined_df = pd.concat(
            [r["df"] for r in self.net_data], ignore_index=True
        )

        # Calculate summary statistics for each design
        self.design_stats = {}
        for result in self.net_data:
            design_name = result["design_name"]
            df = result["df"]

            stats = {
                "count": len(df),
                "mean_hpwl": df["hpwl"].mean(),
                "mean_rwl": df["rwl"].mean(),
                "mean_R": df["R"].mean(),
                "mean_C": df["C"].mean(),
                "mean_power": df["power"].mean(),
                "mean_delay": df["delay"].mean(),
                "mean_slew": df["slew"].mean(),
                "layer_proportions": result["layer_proportions"],
            }
            self.design_stats[design_name] = stats

    def visualize(self, save_path: Optional[str] = None) -> None:
        """
        Visualize the net features and statistics.

        Args:
            save_path: Directory to save the visualizations
        """
        if not hasattr(self, "combined_df") or self.combined_df is None:
            raise ValueError("No analysis results found. Please call analyze() first.")

        # Set up output directory
        if save_path is None:
            save_path = "."
        if self.workspace_dirs.__len__() == 1:
            save_path = self.workspace_dirs[0].paths_table.analysis_path
            print(f"Only one workspace, using save path: {save_path}")

        plt.figure(figsize=(5, 4))

        # Calculate correlation matrix
        features = ["rwl", "hpwl", "R", "C", "power", "delay", "slew"]
        corr_matrix = self.combined_df[features].corr()

        # Create heatmap
        sns.heatmap(corr_matrix, annot=True, cmap="YlGnBu", fmt=".2f", linewidths=0.5)
        plt.tight_layout()

        # Save plot
        output_path = os.path.join(save_path, "net_correlation_matrix.png")
        plt.savefig(output_path)
        plt.close()

        print(f"Correlation matrix plot saved to {output_path}")
