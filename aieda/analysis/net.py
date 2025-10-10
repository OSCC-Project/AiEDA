#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : net.py
@Author : yhqiu
@Desc : net level data ananlysis, including wirelength distribution and metrics correlation
"""

import os
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from ..data import DataVectors
from ..workspace import Workspace
from .base import BaseAnalyzer


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
        workspaces: List[Workspace],
        dir_to_display_name: Optional[Dict[str, str]] = None,
        pattern: Optional[str] = None,
    ) -> None:
        """
        Load net data from multiple directories.

        Args:
            workspaces: List of workspace containing net data
            dir_to_display_name: Optional mapping from directory names to display names
            pattern: File pattern to search for
        """
        self.dir_to_display_name = dir_to_display_name or {}
        self.workspaces = workspaces

        for workspace in workspaces:
            design_name = workspace.design

            vector_loader = DataVectors(workspace)

            net_db = vector_loader.load_nets(workspace.get_nets_path())

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

    def report(self) -> str:
        """Generate a text report summarizing wire distribution analysis."""
        if not self.net_data:
            return "No wire distribution data available for analysis."

        report_lines = []
        report_lines.append("**Wire Distribution Analysis Report**")
        
        # Overall statistics
        total_designs = len(self.net_data)
        total_nets = sum(len(data["df"]) for data in self.net_data)
        
        report_lines.append(f"- Analyzed {total_designs} design(s) with {total_nets:,} total nets")
        report_lines.append("")
        
        # Aggregate statistics across all designs
        all_hpwl = []
        all_rwl = []
        all_delay = []
        all_power = []
        
        for data in self.net_data:
            df = data["df"]
            all_hpwl.extend(df["hpwl"].tolist())
            all_rwl.extend(df["rwl"].tolist())
            all_delay.extend(df["delay"].tolist())
            all_power.extend(df["power"].tolist())
        
        # Wire length statistics
        report_lines.append("**Wire Length Statistics**")
        if all_hpwl:
            hpwl_array = np.array(all_hpwl)
            report_lines.append(f"- HPWL - Mean: {hpwl_array.mean():.1f}, Min: {hpwl_array.min():.1f}, Max: {hpwl_array.max():.1f}")
        
        if all_rwl:
            rwl_array = np.array(all_rwl)
            report_lines.append(f"- RWL - Mean: {rwl_array.mean():.1f}, Min: {rwl_array.min():.1f}, Max: {rwl_array.max():.1f}")
        
        report_lines.append("")
        
        # Performance metrics
        report_lines.append("**Performance Metrics**")
        if all_delay:
            delay_array = np.array(all_delay)
            report_lines.append(f"- Delay - Mean: {delay_array.mean():.3f}, Min: {delay_array.min():.3f}, Max: {delay_array.max():.3f}")
        
        if all_power:
            power_array = np.array(all_power)
            report_lines.append(f"- Power - Mean: {power_array.mean():.3e}, Min: {power_array.min():.3e}, Max: {power_array.max():.3e}")
        
        report_lines.append("")
        
        # Layer distribution summary
        report_lines.append("**Layer Distribution Summary**")
        total_layer_usage = np.zeros(20)
        for data in self.net_data:
            total_layer_usage += data["layer_proportions"]
        
        # Normalize and show top layers
        if np.sum(total_layer_usage) > 0:
            avg_layer_usage = total_layer_usage / total_designs
            top_layers = np.argsort(avg_layer_usage)[::-1][:5]
            
            for i, layer_idx in enumerate(top_layers):
                if avg_layer_usage[layer_idx] > 0.01:  # Only show layers with >1% usage
                    report_lines.append(f"- Layer {layer_idx}: {avg_layer_usage[layer_idx]:.1%} average usage")
        
        report_lines.append("")
        
        # Per-design summary
        report_lines.append("**Per-Design Summary**")
        for data in self.net_data:
            design_name = data["design_name"]
            display_name = self.dir_to_display_name.get(design_name, design_name)
            df = data["df"]
            net_count = len(df)
            avg_hpwl = df["hpwl"].mean() if not df["hpwl"].empty else 0
            avg_rwl = df["rwl"].mean() if not df["rwl"].empty else 0
            
            report_lines.append(f"- {display_name}: {net_count:,} nets, Avg HPWL: {avg_hpwl:.1f}, Avg RWL: {avg_rwl:.1f}")
        
        return report_lines

    def visualize(self, save_path: Optional[str] = None) -> None:
        """
        Visualize the net data.

        Args:
            save_path: Directory to save the visualizations
        """

        # Set up output directory
        if save_path is None:
            save_path = "."

        if len(self.workspaces) == 1:
            save_path = self.workspaces[0].paths_table.analysis_dir
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
        if len(self.workspaces) == 1:
            output_path = self.workspaces[0].paths_table.get_image_path("net_wire_length_distribution")
        else:
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
        workspaces: List[Workspace],
        dir_to_display_name: Optional[Dict[str, str]] = None,
        pattern: Optional[str] = None,
    ) -> None:
        """
        Load net feature data from multiple directories.

        Args:
            workspaces: List of workspace containing net data
            dir_to_display_name: Optional mapping from directory names to display names
            pattern: File pattern to search for
        """
        self.dir_to_display_name = dir_to_display_name or {}
        self.workspaces = workspaces

        for workspace in workspaces:
            design_name = workspace.design

            vector_loader = DataVectors(workspace)

            net_db = vector_loader.load_nets(workspace.get_nets_path())

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

    def report(self) -> str:
        """Generate a text report summarizing metrics correlation analysis."""
        if not self.net_data or not hasattr(self, 'combined_df'):
            return "No metrics correlation data available for analysis. Please run analyze() first."

        report_lines = []
        report_lines.append("**Metrics Correlation Analysis Report**")
        
        # Overall statistics
        total_designs = len(self.net_data)
        total_nets = len(self.combined_df)
        
        report_lines.append(f"- Analyzed {total_designs} design(s) with {total_nets:,} total nets")
        report_lines.append("")
        
        # Combined metrics statistics
        report_lines.append("**Overall Metrics Statistics**")
        metrics = ['hpwl', 'rwl', 'R', 'C', 'power', 'delay', 'slew']
        for metric in metrics:
            if metric in self.combined_df.columns:
                values = self.combined_df[metric]
                report_lines.append(f"- {metric.upper()}: Mean={values.mean():.3e}, Std={values.std():.3e}, Range=[{values.min():.3e}, {values.max():.3e}]")
        
        report_lines.append("")
        
        # Key correlations
        report_lines.append("**Key Correlations**")
        corr_matrix = self.combined_df[metrics].corr()
        
        # Find strongest correlations (excluding self-correlations)
        strong_corrs = []
        for i, metric1 in enumerate(metrics):
            for j, metric2 in enumerate(metrics):
                if i < j:  # Avoid duplicates and self-correlations
                    corr_val = corr_matrix.loc[metric1, metric2]
                    if abs(corr_val) > 0.5:  # Only show strong correlations
                        strong_corrs.append((metric1, metric2, corr_val))
        
        # Sort by absolute correlation strength
        strong_corrs.sort(key=lambda x: abs(x[2]), reverse=True)
        
        if strong_corrs:
            for metric1, metric2, corr_val in strong_corrs[:5]:  # Show top 5
                direction = "positive" if corr_val > 0 else "negative"
                report_lines.append(f"- {metric1.upper()} vs {metric2.upper()}: {corr_val:.3f} ({direction})")
        else:
            report_lines.append("- No strong correlations (>0.5) found between metrics")
        
        report_lines.append("")
        
        # Per-design summary
        report_lines.append("**Per-Design Summary**")
        for design_name, stats in self.design_stats.items():
            display_name = self.dir_to_display_name.get(design_name, design_name)
            net_count = stats['count']
            avg_hpwl = stats['mean_hpwl']
            avg_delay = stats['mean_delay']
            avg_power = stats['mean_power']
            
            report_lines.append(f"- {display_name}: {net_count:,} nets, Avg HPWL: {avg_hpwl:.1f}, Avg Delay: {avg_delay:.3e}, Avg Power: {avg_power:.3e}")
        
        report_lines.append("")
        
        # Layer usage summary
        report_lines.append("**Layer Usage Summary**")
        if self.design_stats:
            # Average layer proportions across all designs
            avg_layer_props = np.zeros(20)
            for stats in self.design_stats.values():
                avg_layer_props += np.array(stats['layer_proportions'])
            avg_layer_props /= len(self.design_stats)
            
            # Show top used layers
            top_layers = np.argsort(avg_layer_props)[::-1][:5]
            for layer_idx in top_layers:
                if avg_layer_props[layer_idx] > 0.01:  # Only show layers with >1% usage
                    report_lines.append(f"- Layer {layer_idx}: {avg_layer_props[layer_idx]:.1%} average usage")
        
        return report_lines

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
        if len(self.workspaces) == 1:
            save_path = self.workspaces[0].paths_table.analysis_dir
            print(f"Only one workspace, using save path: {save_path}")

        plt.figure(figsize=(5, 4))

        # Calculate correlation matrix
        features = ["rwl", "hpwl", "R", "C", "power", "delay", "slew"]
        corr_matrix = self.combined_df[features].corr()

        # Create heatmap
        sns.heatmap(corr_matrix, annot=True, cmap="YlGnBu", fmt=".2f", linewidths=0.5)
        plt.tight_layout()

        # Save plot
        if len(self.workspaces) == 1:
            output_path = self.workspaces[0].paths_table.get_image_path("net_correlation_matrix")
        else:
            output_path = os.path.join(save_path, "net_correlation_matrix.png")
        
        plt.savefig(output_path)
        plt.close()

        print(f"Correlation matrix plot saved to {output_path}")
