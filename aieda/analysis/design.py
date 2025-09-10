#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : design.py
@Author : yhqiu
@Desc : design level data ananlysis, including cell type distribution, core usage, pin distribution and result statistics
"""

import glob
import multiprocessing
import os
import re
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from ..data import DataFeature
from ..flows import DbFlow
from ..workspace import Workspace
from .base import BaseAnalyzer


class CellTypeAnalyzer(BaseAnalyzer):
    """Analyzer for cell type distribution across designs."""

    def __init__(self):
        super().__init__()
        self.inst_count = {}
        self.workspace_dirs = []

    def load(
        self,
        workspace_dirs: List[Workspace],
        flow: Optional[DbFlow] = None,
        dir_to_display_name: Optional[Dict[str, str]] = None,
    ):
        """
        Load data from multiple workspaces.

        Args:
            workspace_dirs: List of workspace directories to process
            flow: DbFlow object representing the flow context
            dir_to_display_name: Optional mapping from directory name to display name
        """
        self.workspace_dirs = workspace_dirs
        for workspace in workspace_dirs:
            design_name = workspace.design
            display_name = dir_to_display_name.get(design_name, design_name)

            feature = DataFeature(workspace=workspace)
            feature_db = feature.load_feature_summary(flow)

            counts = {}
            counts["clock"] = feature_db.instances.clock.num
            counts["logic"] = feature_db.instances.logic.num
            counts["macros"] = feature_db.instances.macros.num
            counts["iopads"] = feature_db.instances.iopads.num

            counts["total"] = sum(counts.values())
            self.inst_count[display_name] = counts

    def analyze(self):
        """Analyze cell type distribution across designs."""

        if not self.inst_count:
            print("No instance data found")
            return

        df = pd.DataFrame.from_dict(self.inst_count, orient="index")
        if "total" not in df.columns:
            df["total"] = df[["clock", "logic", "macros", "iopads"]].sum(axis=1)

        df_sorted = df.sort_values(by="total", ascending=False)

        print("\nStatistical Summary of Instance Counts:")
        for inst_type in ["clock", "logic", "macros", "iopads"]:
            values = df_sorted[inst_type]
            print(f"\n{inst_type.upper()}:")
            print(f"  Mean: {values.mean():.2f}")
            print(f"  Median: {values.median():.2f}")
            print(f"  Min: {values.min():.2f}")
            print(f"  Max: {values.max():.2f}")
            print(f"  Std Dev: {values.std():.2f}")

        print("\nAverage Instance Type Proportions:")
        total = df[["clock", "logic", "macros", "iopads"]].sum().sum()
        for inst_type in ["clock", "logic", "macros", "iopads"]:
            type_sum = df[inst_type].sum()
            print(f"  {inst_type}: {type_sum / total:.2%}")

    def report(self) -> str:
        """Generate a text report summarizing cell type distribution."""
        if not self.inst_count:
            return "No instance data available for cell type analysis."

        df = pd.DataFrame.from_dict(self.inst_count, orient="index")
        if "total" not in df.columns:
            df["total"] = df[["clock", "logic", "macros", "iopads"]].sum(axis=1)

        df_sorted = df.sort_values(by="total", ascending=False)
        
        report_lines = []
        report_lines.append("Cell Type Distribution Analysis Report")
        report_lines.append("=" * 40)
        
        # Overall statistics
        total_designs = len(df)
        total_instances = df["total"].sum()
        report_lines.append(f"Analyzed {total_designs} design(s) with {total_instances:,} total instances")
        report_lines.append("")
        
        # Instance type statistics
        report_lines.append("Instance Type Statistics:")
        for inst_type in ["clock", "logic", "macros", "iopads"]:
            values = df_sorted[inst_type]
            type_sum = values.sum()
            proportion = type_sum / total_instances if total_instances > 0 else 0
            report_lines.append(f"  {inst_type.capitalize()}: {type_sum:,} ({proportion:.1%}) - Min: {values.min()}, Max: {values.max()}, Avg: {values.mean():.1f}")
        
        report_lines.append("")
        
        # Top designs by instance count
        report_lines.append("Top 3 Designs by Total Instance Count:")
        for i, (design, row) in enumerate(df_sorted.head(3).iterrows()):
            report_lines.append(f"  {i+1}. {design}: {row['total']:,} instances")
        
        return "\n".join(report_lines)

    def visualize(self, save_path: Optional[str] = None):
        """Create visualizations for cell type distribution."""
        if not self.inst_count:
            print("No instance data found")
            return

        if self.workspace_dirs.__len__() == 1:
            save_path = self.workspace_dirs[0].paths_table.analysis_path
            print(f"Only one workspace, using save path: {save_path}")

        df = pd.DataFrame.from_dict(self.inst_count, orient="index")
        if "total" not in df.columns:
            df["total"] = df[["clock", "logic", "macros", "iopads"]].sum(axis=1)

        df_sorted = df.sort_values(by="total", ascending=False)

        # 1. Create heatmap for top 10 designs
        plt.figure(figsize=(5, 4))

        top10_designs = df_sorted.index[:10]

        df_display = df_sorted.loc[
            top10_designs, ["clock", "logic", "macros", "iopads"]
        ].copy()

        ax = sns.heatmap(
            df_display,
            annot=True,
            fmt="",
            cmap="YlGnBu",
            linewidths=0.5,
            annot_kws={"size": 10},
            cbar_kws={"label": "Instance Count"},
        )

        for i in range(len(df_display.index)):
            for j in range(len(df_display.columns)):
                text = ax.texts[i * len(df_display.columns) + j]
                text.set_text(self._custom_format(df_display.iloc[i, j]))

        plt.setp(ax.get_yticklabels(), style="italic")

        plt.xlabel("Instance Type", fontsize=12)
        plt.ylabel("Design", fontsize=12)
        plt.tight_layout()

        # Save plot
        if len(self.workspace_dirs) == 1:
            output_path = self.workspace_dirs[0].paths_table.get_image_path("design_cell_type_top_10")
        else:
            output_path = save_path + "/design_cell_type_top_10.png"
        
        plt.savefig(
            output_path, dpi=300, bbox_inches="tight"
        )
        plt.close()

        # 2. create heatmap for bottom 20 designs
        plt.figure(figsize=(5, 4))

        bottom10_designs = df_sorted.index[-10:]

        df_display = df_sorted.loc[
            bottom10_designs, ["clock", "logic", "macros", "iopads"]
        ].copy()

        ax = sns.heatmap(
            df_display,
            annot=True,
            fmt="",
            cmap="YlGnBu",
            linewidths=0.5,
            annot_kws={"size": 10},
            cbar_kws={"label": "Instance Count"},
        )

        for i in range(len(df_display.index)):
            for j in range(len(df_display.columns)):
                text = ax.texts[i * len(df_display.columns) + j]
                text.set_text(self._custom_format(df_display.iloc[i, j]))

        plt.setp(ax.get_yticklabels(), style="italic")

        plt.xlabel("Instance Type", fontsize=12)
        plt.ylabel("Design", fontsize=12)
        plt.tight_layout()

        # Save plot
        if len(self.workspace_dirs) == 1:
            output_path = self.workspace_dirs[0].paths_table.get_image_path("design_cell_type_bottom_10")
        else:
            output_path = save_path + "/design_cell_type_bottom_10.png"
        
        plt.savefig(
            output_path, dpi=300, bbox_inches="tight"
        )
        plt.close()

        print("Saved instance count heatmaps:")
        print("- 'design_cell_type_top_10.png' (Top 10 designs)")
        print("- 'design_cell_type_bottom_10.png' (Bottom 10 designs)")

    def _custom_format(self, val):
        if val == 0:
            return "0"
        else:
            return "{:.1e}".format(val)


class CoreUsageAnalyzer(BaseAnalyzer):
    """Analyzer for core usage statistics."""

    def __init__(self):
        super().__init__()
        self.core_usage = {}
        self.workspace_dirs = []

    def load(
        self,
        workspace_dirs: List[Workspace],
        flow: Optional[DbFlow] = None,
        dir_to_display_name: Optional[Dict[str, str]] = None,
    ):
        """
        Load data from multiple directories.

        Args:
            workspace_dirs: List of base directories to process
            flow: DbFlow object representing the flow context
            dir_to_display_name: Optional mapping from directory name to display name
        """
        self.workspace_dirs = workspace_dirs
        for workspace in workspace_dirs:
            design_name = workspace.design

            feature = DataFeature(workspace=workspace)
            feature_db = feature.load_feature_summary(flow)

            self.core_usage[design_name] = feature_db.layout.core_usage

    def analyze(self):
        """Analyze core usage distribution across designs."""

        if not self.core_usage:
            print("No core usage data found")
            return

        designs = list(self.core_usage.keys())
        usages = list(self.core_usage.values())

        sorted_indices = np.argsort(usages)
        sorted_designs = [designs[i] for i in sorted_indices]
        sorted_usages = [usages[i] for i in sorted_indices]

        # Print all collected core_usage values
        print("\ncore_usage values for all designs:")
        for design, usage in sorted(self.core_usage.items(), key=lambda x: x[1]):
            print(f"{design}: {usage:.4f}")

        # Output additional statistical information
        print("\nStatistical Summary:")
        print(f"Minimum: {min(sorted_usages):.4f} ({sorted_designs[0]})")
        print(f"Maximum: {max(sorted_usages):.4f} ({sorted_designs[-1]})")
        print(f"Mean: {np.mean(sorted_usages):.4f}")
        print(f"Median: {np.median(sorted_usages):.4f}")
        print(f"Standard Deviation: {np.std(sorted_usages):.4f}")

        # Calculate percentiles
        percentiles = [25, 50, 75, 90, 95, 99]
        print("\nPercentiles:")
        for p in percentiles:
            value = np.percentile(sorted_usages, p)
            print(f"{p}%: {value:.4f}")

    def report(self) -> str:
        """Generate a text report summarizing core usage statistics."""
        if not self.core_usage:
            return "No core usage data available for analysis."

        usages = list(self.core_usage.values())
        designs = list(self.core_usage.keys())
        
        report_lines = []
        report_lines.append("Core Usage Analysis Report")
        report_lines.append("=" * 30)
        
        # Overall statistics
        total_designs = len(usages)
        avg_usage = np.mean(usages)
        min_usage = np.min(usages)
        max_usage = np.max(usages)
        std_usage = np.std(usages)
        
        report_lines.append(f"Analyzed {total_designs} design(s)")
        report_lines.append(f"Average core usage: {avg_usage:.2%}")
        report_lines.append(f"Usage range: {min_usage:.2%} - {max_usage:.2%}")
        report_lines.append(f"Standard deviation: {std_usage:.2%}")
        report_lines.append("")
        
        # Usage categories
        low_usage = [d for d, u in self.core_usage.items() if u < 0.5]
        medium_usage = [d for d, u in self.core_usage.items() if 0.5 <= u < 0.8]
        high_usage = [d for d, u in self.core_usage.items() if u >= 0.8]
        
        report_lines.append("Usage Distribution:")
        report_lines.append(f"  Low usage (<50%): {len(low_usage)} designs")
        report_lines.append(f"  Medium usage (50-80%): {len(medium_usage)} designs")
        report_lines.append(f"  High usage (≥80%): {len(high_usage)} designs")
        report_lines.append("")
        
        # Top and bottom designs
        sorted_designs = sorted(self.core_usage.items(), key=lambda x: x[1], reverse=True)
        
        report_lines.append("Top 3 Designs by Core Usage:")
        for i, (design, usage) in enumerate(sorted_designs[:3]):
            report_lines.append(f"  {i+1}. {design}: {usage:.2%}")
        
        if len(sorted_designs) > 3:
            report_lines.append("")
            report_lines.append("Bottom 3 Designs by Core Usage:")
            for i, (design, usage) in enumerate(sorted_designs[-3:]):
                report_lines.append(f"  {i+1}. {design}: {usage:.2%}")
        
        return "\n".join(report_lines)


    def visualize(self, save_path: Optional[str] = None):
        """Create visualizations for cell usage distribution."""
        if not self.core_usage:
            print("No core usage data found")
            return

        if self.workspace_dirs.__len__() == 1:
            save_path = self.workspace_dirs[0].paths_table.analysis_path
            print(f"Only one workspace, using save path: {save_path}")

        usages = list(self.core_usage.values())

        from matplotlib.ticker import MultipleLocator

        plt.figure(figsize=(5, 4))
        plt.hist(usages, bins=10, color="lightgreen", edgecolor="black")
        plt.xlabel("core usage", fontsize=14)
        plt.ylabel("Number of Designs", fontsize=14)
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.gca().xaxis.set_major_locator(MultipleLocator(0.1))

        plt.tight_layout()
        
        # Save plot
        if len(self.workspace_dirs) == 1:
            output_path = self.workspace_dirs[0].paths_table.get_image_path("design_core_usage_hist")
        else:
            output_path = save_path + "/design_core_usage_hist.png"
        
        plt.savefig(output_path, bbox_inches="tight")
        plt.close()

        print(f"Saved core usage chart to {output_path}:")
        print("- 'design_core_usage_hist.png' (Histogram)")


class PinDistributionAnalyzer(BaseAnalyzer):
    """Analyzer for pin distribution in designs."""

    def __init__(self):
        super().__init__()
        self.pin_dist = {}
        self.workspace_dirs = []

    def load(
        self,
        workspace_dirs: List[Workspace],
        flow: Optional[DbFlow] = None,
        dir_to_display_name: Optional[Dict[str, str]] = None,
    ):
        """
        Load data from multiple directories.

        Args:
            workspace_dirs: List of base directories to process
            flow: DbFlow object representing the flow context
            dir_to_display_name: Optional mapping from directory name to display name
        """
        self.workspace_dirs = workspace_dirs
        for workspace in workspace_dirs:
            design_name = workspace.design

            feature = DataFeature(workspace=workspace)
            feature_db = feature.load_feature_summary(flow)

            pin_data = []
            for iterm in feature_db.pins.pin_distribution:
                if (
                    hasattr(iterm, "pin_num")
                    and hasattr(iterm, "net_num")
                    and hasattr(iterm, "net_ratio")
                ):
                    pin_num = self._parse_pin_num(iterm.pin_num)

                    try:
                        net_num = (
                            int(iterm.net_num)
                            if isinstance(iterm.net_num, (int, float, str))
                            else 0
                        )
                    except ValueError:
                        print(
                            f"Warning: Could not parse net_num '{iterm.net_num}', using 0 as default"
                        )
                        net_num = 0

                    try:
                        net_ratio = (
                            float(iterm.net_ratio)
                            if isinstance(iterm.net_ratio, (int, float, str))
                            else 0.0
                        )
                    except ValueError:
                        print(
                            f"Warning: Could not parse net_ratio '{iterm.net_ratio}', using 0.0 as default"
                        )
                        net_ratio = 0.0

                    pin_data.append(
                        {
                            "pin_num": pin_num,
                            "net_num": net_num,
                            "net_ratio": net_ratio,
                            "original_pin_num": iterm.pin_num,
                        }
                    )
            pin_data.sort(key=lambda x: x["pin_num"])
            self.pin_dist[design_name] = pin_data

    def analyze(self):
        """Analyze pin number distribution across designs."""

        if not self.pin_dist:
            print("No pin dist data found")
            return

        all_data = []
        for design_name, pin_data in self.pin_dist.items():
            for item in pin_data:
                all_data.append(
                    {
                        "design": design_name,
                        "pin_num": item["pin_num"],
                        "net_num": item["net_num"],
                        "net_ratio": item["net_ratio"],
                        "original_pin_num": item.get(
                            "original_pin_num", str(item["pin_num"])
                        ),
                    }
                )

        df = pd.DataFrame(all_data)

        df_summary = (
            df.groupby("pin_num")
            .agg(
                {
                    "net_num": ["mean", "min", "max", "std"],
                    "net_ratio": ["mean", "min", "max", "std"],
                }
            )
            .reset_index()
        )
        print("\nStatistical Summary by Pin Count:")
        print(df_summary.to_string())

    def report(self) -> str:
        """Generate a text report summarizing pin distribution analysis."""
        if not self.pin_dist:
            return "No pin distribution data available for analysis."

        all_data = []
        for design_name, pin_data in self.pin_dist.items():
            for item in pin_data:
                all_data.append({
                    "design": design_name,
                    "pin_num": item["pin_num"],
                    "net_num": item["net_num"],
                    "net_ratio": item["net_ratio"]
                })

        if not all_data:
            return "No valid pin distribution data found."

        df = pd.DataFrame(all_data)
        
        report_lines = []
        report_lines.append("Pin Distribution Analysis Report")
        report_lines.append("=" * 35)
        
        # Overall statistics
        total_designs = len(self.pin_dist)
        unique_pin_counts = df['pin_num'].nunique()
        total_entries = len(df)
        
        report_lines.append(f"Analyzed {total_designs} design(s) with {total_entries} pin distribution entries")
        report_lines.append(f"Pin count range: {df['pin_num'].min()} - {df['pin_num'].max()} pins")
        report_lines.append(f"Unique pin counts: {unique_pin_counts}")
        report_lines.append("")
        
        # Net statistics
        report_lines.append("Net Statistics:")
        report_lines.append(f"  Average nets per pin group: {df['net_num'].mean():.1f}")
        report_lines.append(f"  Net count range: {df['net_num'].min()} - {df['net_num'].max()}")
        report_lines.append(f"  Average net ratio: {df['net_ratio'].mean():.3f}")
        report_lines.append(f"  Net ratio range: {df['net_ratio'].min():.3f} - {df['net_ratio'].max():.3f}")
        report_lines.append("")
        
        # Most common pin counts
        pin_count_freq = df['pin_num'].value_counts().head(5)
        report_lines.append("Top 5 Most Common Pin Counts:")
        for pin_count, freq in pin_count_freq.items():
            avg_nets = df[df['pin_num'] == pin_count]['net_num'].mean()
            report_lines.append(f"  {pin_count} pins: {freq} occurrences (avg {avg_nets:.1f} nets)")
        
        return "\n".join(report_lines)

    def visualize(self, save_path: Optional[str] = None):
        """Create visualizations for pin distribution."""
        if not self.pin_dist:
            print("No pin_dist data found")
            return

        if self.workspace_dirs.__len__() == 1:
            save_path = self.workspace_dirs[0].paths_table.analysis_path
            print(f"Only one workspace, using save path: {save_path}")

        all_data = []
        for design_name, pin_data in self.pin_dist.items():
            for item in pin_data:
                all_data.append(
                    {
                        "design": design_name,
                        "pin_num": item["pin_num"],
                        "net_num": item["net_num"],
                        "net_ratio": item["net_ratio"],
                        "original_pin_num": item.get(
                            "original_pin_num", str(item["pin_num"])
                        ),
                    }
                )

        df = pd.DataFrame(all_data)

        df_summary = (
            df.groupby("pin_num")
            .agg(
                {
                    "net_num": ["mean", "min", "max", "std"],
                    "net_ratio": ["mean", "min", "max", "std"],
                }
            )
            .reset_index()
        )

        plt.figure(figsize=(5, 4))
        plt.plot(
            df_summary["pin_num"],
            df_summary[("net_ratio", "mean")],
            marker="o",
            markersize=5,
            linestyle="-",
            color="blue",
            linewidth=1.5,
            label="Mean",
        )
        plt.fill_between(
            df_summary["pin_num"],
            df_summary[("net_ratio", "mean")] - df_summary[("net_ratio", "std")],
            df_summary[("net_ratio", "mean")] + df_summary[("net_ratio", "std")],
            alpha=0.2,
            color="blue",
            label="±1 Std Dev",
        )
        plt.plot(
            df_summary["pin_num"],
            df_summary[("net_ratio", "min")],
            marker="^",
            markersize=4,
            linestyle="--",
            color="green",
            linewidth=1.0,
            label="Min",
        )
        plt.plot(
            df_summary["pin_num"],
            df_summary[("net_ratio", "max")],
            marker="v",
            markersize=4,
            linestyle="--",
            color="red",
            linewidth=1.0,
            label="Max",
        )

        plt.xlabel("Pin Count", fontsize=14)
        plt.ylabel("Net Ratio", fontsize=14)
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.legend(loc="upper right", frameon=True)

        plt.tick_params(axis="both", which="major", direction="out", length=4, width=1)

        plt.tight_layout()
        
        # Save plot
        if len(self.workspace_dirs) == 1:
            output_path = self.workspace_dirs[0].paths_table.get_image_path("design_pin_vs_net_ratio")
        else:
            output_path = save_path + "/design_pin_vs_net_ratio.png"
        
        plt.savefig(output_path, bbox_inches="tight")
        print(f"Saved design_pin_vs_net_ratio.png to {output_path}")
        plt.close()

    def _parse_pin_num(self, pin_num_str):
        if isinstance(pin_num_str, (int, float)):
            return int(pin_num_str)

        pin_num_str = str(pin_num_str).strip()

        if pin_num_str.startswith(">"):
            num_part = pin_num_str.replace(">", "").strip()
            try:
                return int(num_part) + 1
            except ValueError:
                print(
                    f"Warning: Could not parse pin_num '{pin_num_str}', using 999 as default"
                )
                return 999

        elif pin_num_str.startswith("<"):
            num_part = pin_num_str.replace("<", "").strip()
            try:
                return int(num_part) - 1
            except ValueError:
                print(
                    f"Warning: Could not parse pin_num '{pin_num_str}', using 0 as default"
                )
                return 0

        elif "-" in pin_num_str and not pin_num_str.startswith("-"):
            try:
                start, end = pin_num_str.split("-", 1)
                return (int(start.strip()) + int(end.strip())) // 2
            except ValueError:
                print(
                    f"Warning: Could not parse pin_num range '{pin_num_str}', using 500 as default"
                )
                return 500

        try:
            return int(pin_num_str)
        except ValueError:
            print(
                f"Error: Failed to parse pin_num '{pin_num_str}', using -1 as default"
            )
            return -1


class ResultStatisAnalyzer(BaseAnalyzer):
    """Analyzer for result statistics including file counts, sizes, and wire numbers."""

    def __init__(self):
        super().__init__()
        self.stats_data = {}
        self.total_stats = {
            "nets_count": 0,
            "nets_size": 0,
            "patches_count": 0,
            "patches_size": 0,
            "paths_count": 0,
            "paths_size": 0,
            "wire_num_sum": 0,
            "accessible_designs": 0,
        }
        self.calc_wire_num = False

    def load(
        self,
        workspace_dirs: List[Workspace],
        dir_to_display_name: Optional[Dict[str, str]] = None,
        pattern: Optional[str] = None,
        calc_wire_num: bool = False,
    ):
        """
        Load data from multiple directories.

        Args:
            workspace_dirs: List of base directories to process
            dir_to_display_name: Optional mapping from directory name to display name
            pattern: Path pattern to append to workspace_dirs (required)
            calc_wire_num: Whether to calculate wire number sum (time-consuming)
        """
        if pattern is None:
            raise ValueError("Pattern must be specified for result statistics analysis")

        self.workspace_dirs = workspace_dirs
        self.calc_wire_num = calc_wire_num

        # Build complete design path list
        design_paths = []
        design_name_mapping = {}

        for workspace in workspace_dirs:
            # Build complete path
            full_path = workspace.directory + pattern
            design_paths.append(full_path)

            # Extract design name from workspace
            design_name = workspace.design

            # Establish mapping from path to design name
            design_name_mapping[full_path] = design_name

        # Use process pool to handle all designs in parallel
        process_design_with_params = partial(
            self._process_design, calc_wire_num=calc_wire_num
        )

        with ProcessPoolExecutor(
            max_workers=min(len(design_paths), multiprocessing.cpu_count())
        ) as executor:
            results = list(executor.map(process_design_with_params, design_paths))

        # Process results
        for result in results:
            if result:
                design_path = result["design_path"]
                design_name = design_name_mapping.get(
                    design_path, os.path.basename(design_path)
                )
                display_name = (
                    dir_to_display_name.get(design_name, design_name)
                    if dir_to_display_name
                    else design_name
                )

                # Store data
                self.stats_data[display_name] = {
                    "nets_count": result["nets"][0],
                    "nets_size": result["nets"][1],
                    "patches_count": result["patches"][0],
                    "patches_size": result["patches"][1],
                    "paths_count": result["paths"][0],
                    "paths_size": result["paths"][1],
                    "wire_num_sum": result["wire_num_sum"],
                }

                # Accumulate totals
                if (
                    result["nets"][0] > 0
                    or result["patches"][0] > 0
                    or result["paths"][0] > 0
                ):
                    self.total_stats["accessible_designs"] += 1
                    self.total_stats["nets_count"] += result["nets"][0]
                    self.total_stats["nets_size"] += result["nets"][1]
                    self.total_stats["patches_count"] += result["patches"][0]
                    self.total_stats["patches_size"] += result["patches"][1]
                    self.total_stats["paths_count"] += result["paths"][0]
                    self.total_stats["paths_size"] += result["paths"][1]
                    self.total_stats["wire_num_sum"] += result["wire_num_sum"]
                else:
                    print(f"Design {display_name} has no valid files, skipping")
            else:
                # If processing failed, extract design name from path
                print(f"Failed to process design at {design_path}, skipping")

        print(f"Loaded data for {len(self.stats_data)} designs")

    def analyze(self):
        """Analyze the loaded statistics data."""
        if not self.stats_data:
            print("No statistics data found")
            return

        df = pd.DataFrame.from_dict(self.stats_data, orient="index")

        # Print statistics in table format
        print(
            f"{'Designs':<16} | {'Nets Dir':<25} | {'Patches Dir':<25} | {'Paths Dir':<25} | {'Wire Num':<20}"
        )
        print(f"{'-' * 16} | {'-' * 25} | {'-' * 25} | {'-' * 25} | {'-' * 12}")

        for design, data in self.stats_data.items():
            nets_info = (
                f"{data['nets_count']} files, {self._format_size(data['nets_size'])}"
            )
            patches_info = f"{data['patches_count']} files, {self._format_size(data['patches_size'])}"
            paths_info = (
                f"{data['paths_count']} files, {self._format_size(data['paths_size'])}"
            )

            print(
                f"{design:<16} | {nets_info:<25} | {patches_info:<25} | {paths_info:<25} | {data['wire_num_sum']:<12}"
            )

        # Print totals
        print(f"{'-' * 16} | {'-' * 25} | {'-' * 25} | {'-' * 25} | {'-' * 12}")
        print(
            f"{'Total':<16} | {self.total_stats['nets_count']} files, {self._format_size(self.total_stats['nets_size']):<10} | "
            f"{self.total_stats['patches_count']} files, {self._format_size(self.total_stats['patches_size']):<10} | "
            f"{self.total_stats['paths_count']} files, {self._format_size(self.total_stats['paths_size']):<10} | "
            f"{self.total_stats['wire_num_sum']:<12}"
        )
        print(
            f"Accessible Designs: {self.total_stats['accessible_designs']}/{len(self.stats_data)}"
        )

        # Statistical analysis
        print("\n=== Statistical Analysis ===")

        # File count statistics
        print("\nFile Count Statistics:")
        for file_type in ["nets_count", "patches_count", "paths_count"]:
            values = df[file_type]
            print(f"\n{file_type.replace('_count', '').upper()}:")
            print(f"  Mean: {values.mean():.2f}")
            print(f"  Median: {values.median():.2f}")
            print(f"  Min: {values.min()}")
            print(f"  Max: {values.max()}")
            print(f"  Std Dev: {values.std():.2f}")

        # File size statistics
        print("\nFile Size Statistics:")
        for size_type in ["nets_size", "patches_size", "paths_size"]:
            values = df[size_type]
            print(f"\n{size_type.replace('_size', '').upper()}:")
            print(f"  Mean: {self._format_size(values.mean())}")
            print(f"  Median: {self._format_size(values.median())}")
            print(f"  Min: {self._format_size(values.min())}")
            print(f"  Max: {self._format_size(values.max())}")
            print(f"  Total: {self._format_size(values.sum())}")

        # Wire number statistics (if calculated)
        if self.calc_wire_num:
            print("\nWire Number Statistics:")
            wire_values = df["wire_num_sum"]
            print(f"  Mean: {wire_values.mean():.2f}")
            print(f"  Median: {wire_values.median():.2f}")
            print(f"  Min: {wire_values.min()}")
            print(f"  Max: {wire_values.max()}")
            print(f"  Total: {wire_values.sum()}")
            print(f"  Std Dev: {wire_values.std():.2f}")

    def report(self) -> str:
        """Generate a text report summarizing result statistics."""
        if not self.stats_data:
            return "No statistics data available for analysis."

        df = pd.DataFrame.from_dict(self.stats_data, orient="index")
        
        report_lines = []
        report_lines.append("Result Statistics Analysis Report")
        report_lines.append("=" * 37)
        
        # Overall summary
        total_designs = len(self.stats_data)
        accessible_designs = self.total_stats['accessible_designs']
        
        report_lines.append(f"Total designs analyzed: {total_designs}")
        report_lines.append(f"Accessible designs: {accessible_designs}/{total_designs} ({accessible_designs/total_designs:.1%})")
        report_lines.append("")
        
        # File statistics summary
        report_lines.append("File Statistics Summary:")
        report_lines.append(f"  Nets: {self.total_stats['nets_count']} files, {self._format_size(self.total_stats['nets_size'])}")
        report_lines.append(f"  Patches: {self.total_stats['patches_count']} files, {self._format_size(self.total_stats['patches_size'])}")
        report_lines.append(f"  Paths: {self.total_stats['paths_count']} files, {self._format_size(self.total_stats['paths_size'])}")
        
        if self.calc_wire_num:
            report_lines.append(f"  Total wire numbers: {self.total_stats['wire_num_sum']:,}")
        
        report_lines.append("")
        
        # Average statistics per design
        if accessible_designs > 0:
            report_lines.append("Average per Accessible Design:")
            report_lines.append(f"  Nets: {self.total_stats['nets_count']/accessible_designs:.1f} files, {self._format_size(self.total_stats['nets_size']/accessible_designs)}")
            report_lines.append(f"  Patches: {self.total_stats['patches_count']/accessible_designs:.1f} files, {self._format_size(self.total_stats['patches_size']/accessible_designs)}")
            report_lines.append(f"  Paths: {self.total_stats['paths_count']/accessible_designs:.1f} files, {self._format_size(self.total_stats['paths_size']/accessible_designs)}")
            
            if self.calc_wire_num:
                report_lines.append(f"  Wire numbers: {self.total_stats['wire_num_sum']/accessible_designs:.1f}")
        
        report_lines.append("")
        
        # Top designs by total file count
        df['total_files'] = df['nets_count'] + df['patches_count'] + df['paths_count']
        top_designs = df.nlargest(3, 'total_files')
        
        report_lines.append("Top 3 Designs by Total File Count:")
        for i, (design, row) in enumerate(top_designs.iterrows()):
            total_size = row['nets_size'] + row['patches_size'] + row['paths_size']
            report_lines.append(f"  {i+1}. {design}: {int(row['total_files'])} files, {self._format_size(total_size)}")
        
        return "\n".join(report_lines)

    def visualize(self, save_path: Optional[str] = None):
        """Create visualizations for the statistics data."""
        if not self.stats_data:
            print("No statistics data found")
            return

        if save_path is None:
            save_path = ""

        if self.workspace_dirs.__len__() == 1:
            save_path = self.workspace_dirs[0].paths_table.analysis_path
            print(f"Only one workspace, using save path: {save_path}")

        df = pd.DataFrame.from_dict(self.stats_data, orient="index")

        # 1. File count distribution charts
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))

        # File count bar charts
        file_counts = ["nets_count", "patches_count", "paths_count"]
        colors = ["skyblue", "lightgreen", "lightcoral"]

        for i, (count_type, color) in enumerate(zip(file_counts, colors)):
            ax = axes[0, 0] if i == 0 else (axes[0, 1] if i == 1 else axes[1, 0])
            values = df[count_type].sort_values(ascending=False)
            ax.bar(range(len(values)), values, color=color)
            ax.set_title(
                f"All Designs - {count_type.replace('_count', '').title()} File Count"
            )
            ax.set_xlabel("Design Rank")
            ax.set_ylabel("File Count")
            ax.grid(axis="y", alpha=0.3)

            # Set x-axis labels to design names
            ax.set_xticks(range(len(values)))
            ax.set_xticklabels(values.index, rotation=45, ha="right")

        # File size distribution histogram
        total_sizes = df["nets_size"] + df["patches_size"] + df["paths_size"]
        axes[1, 1].hist(
            total_sizes / (1024**3),
            bins=max(5, len(df) // 2),
            color="orange",
            alpha=0.7,
            edgecolor="black",
        )
        axes[1, 1].set_title("Total File Size Distribution")
        axes[1, 1].set_xlabel("Total Size (GB)")
        axes[1, 1].set_ylabel("Number of Designs")
        axes[1, 1].grid(axis="y", alpha=0.3)

        plt.tight_layout()
        
        # Save plot
        if len(self.workspace_dirs) == 1:
            output_path = self.workspace_dirs[0].paths_table.get_image_path("design_result_stats_overview")
        else:
            output_path = save_path + "/design_result_stats_overview.png"
        
        plt.savefig(
            output_path,
            dpi=300,
            bbox_inches="tight",
        )
        plt.close()

        # 2. Heatmap - file counts
        plt.figure(figsize=(10, max(6, len(df) * 0.4)))

        # Sort by total file count
        df["total_files"] = df["nets_count"] + df["patches_count"] + df["paths_count"]
        df_sorted = df.sort_values(
            "total_files", ascending=True
        )  # Sort ascending for better visualization

        heatmap_data = df_sorted[["nets_count", "patches_count", "paths_count"]]

        ax = sns.heatmap(
            heatmap_data,
            annot=True,
            fmt="d",
            cmap="YlOrRd",
            linewidths=0.5,
            cbar_kws={"label": "File Count"},
        )

        plt.title("File Count Heatmap (All Designs)", fontsize=16, fontweight="bold")
        plt.xlabel("Directory Type", fontsize=12)
        plt.ylabel("Design", fontsize=12)
        plt.setp(ax.get_yticklabels(), style="italic")
        plt.tight_layout()
        
        # Save plot
        if len(self.workspace_dirs) == 1:
            output_path = self.workspace_dirs[0].paths_table.get_image_path("design_result_stats_heatmap")
        else:
            output_path = save_path + "/design_result_stats_heatmap.png"
        
        plt.savefig(
            output_path, dpi=300, bbox_inches="tight"
        )
        plt.close()

        # 3. Wire number distribution charts (if calculated)
        if self.calc_wire_num and "wire_num_sum" in df.columns:
            plt.figure(figsize=(12, 5))

            # Subplot 1: Wire number bar chart
            plt.subplot(1, 2, 1)
            wire_values = df["wire_num_sum"].sort_values(ascending=False)
            plt.bar(range(len(wire_values)), wire_values, color="purple", alpha=0.7)
            plt.title("All Designs - Wire Number Sum")
            plt.xlabel("Design Rank")
            plt.ylabel("Wire Number Sum")
            plt.xticks(
                range(len(wire_values)), wire_values.index, rotation=45, ha="right"
            )
            plt.grid(axis="y", alpha=0.3)

            # Subplot 2: Wire number distribution histogram
            plt.subplot(1, 2, 2)
            plt.hist(
                df["wire_num_sum"],
                bins=max(5, len(df) // 2),
                color="purple",
                alpha=0.7,
                edgecolor="black",
            )
            plt.title("Wire Number Sum Distribution")
            plt.xlabel("Wire Number Sum")
            plt.ylabel("Number of Designs")
            plt.grid(axis="y", alpha=0.3)

            plt.tight_layout()
            plt.savefig(
                save_path + "design_wire_number_analysis.png",
                dpi=300,
                bbox_inches="tight",
            )
            plt.close()

            print("Saved wire number analysis:")
            print("- 'wire_number_analysis.png'")

        print("Saved result statistics visualizations:")
        print("- 'result_stats_overview.png' (Overview charts)")
        print("- 'result_stats_heatmap.png' (File count heatmap)")

    def _process_design(self, design_path, calc_wire_num=False):
        """Process a single design directory and return statistics."""
        # Build subdirectory paths
        nets_dir = os.path.join(design_path, "nets")
        patches_dir = os.path.join(design_path, "patchs")
        paths_dir = os.path.join(design_path, "wire_paths")

        try:
            with ProcessPoolExecutor(max_workers=3) as executor:
                dir_futures = {
                    executor.submit(self._fast_dir_scan, nets_dir): "nets",
                    executor.submit(self._fast_dir_scan, patches_dir): "patches",
                    executor.submit(self._fast_dir_scan, paths_dir): "paths",
                }

                results = {}
                for future in dir_futures:
                    dir_type = dir_futures[future]
                    try:
                        file_count, size = future.result()
                        results[dir_type] = (file_count, size)
                    except Exception:
                        results[dir_type] = (0, 0)

            # Calculate wire_num sum (potentially time-consuming, based on parameter)
            wire_num_sum = 0
            if calc_wire_num and results.get("nets", (0, 0))[0] > 0:
                wire_num_sum = self._get_wire_num_sum_parallel(nets_dir)

            return {
                "design_path": design_path,
                "nets": results.get("nets", (0, 0)),
                "patches": results.get("patches", (0, 0)),
                "paths": results.get("paths", (0, 0)),
                "wire_num_sum": wire_num_sum,
            }
        except Exception:
            return None

    def _fast_dir_scan(self, directory):
        """Quickly count files and calculate total size in directory."""
        if not os.path.exists(directory):
            return 0, 0

        total_size = 0
        file_count = 0

        try:
            for entry in os.scandir(directory):
                if entry.is_file(follow_symlinks=False):
                    file_count += 1
                    total_size += entry.stat().st_size
                elif entry.is_dir(follow_symlinks=False):
                    subdir_count, subdir_size = self._fast_dir_scan(entry.path)
                    file_count += subdir_count
                    total_size += subdir_size
        except Exception:
            pass

        return file_count, total_size

    def _process_net_file(self, file_path):
        """Process a single net file and return wire_num."""
        try:
            with open(file_path, "r") as f:
                for line in f:
                    if '"wire_num":' in line:
                        # Simple parsing to avoid loading entire JSON
                        match = re.search(r'"wire_num":\s*(\d+)', line)
                        if match:
                            return int(match.group(1))
                        break
        except Exception:
            pass
        return 0

    def _get_wire_num_sum_parallel(self, nets_dir, max_workers=None):
        """Calculate sum of wire_num from all net files in specified directory in parallel."""
        if not os.path.exists(nets_dir):
            return 0

        # Use glob pattern to match all net_*.json files
        net_files = list(glob.glob(os.path.join(nets_dir, "net_*.json")))

        if not net_files:
            return 0

        if max_workers is None:
            max_workers = multiprocessing.cpu_count()

        total_wire_num = 0
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            results = executor.map(self._process_net_file, net_files)
            total_wire_num = sum(results)

        return total_wire_num

    def _format_size(self, size_bytes):
        """Convert byte size to human-readable format (KB, MB, GB, etc.)."""
        if size_bytes == 0:
            return "0 B"

        size_units = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_units) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.2f} {size_units[i]}"
