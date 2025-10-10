#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : path.py
@Author : yhqiu
@Desc : Path-level data analysis, including delay and stage analysis.
"""

import os
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import ticker

from ..data import DataVectors
from ..workspace import Workspace
from .base import BaseAnalyzer


class DelayAnalyzer(BaseAnalyzer):
    """Analyzer for path delay."""

    def __init__(self):
        super().__init__()
        self.path_data = {}
        self.design_stats = {}

    def load(
        self,
        workspaces: List[Workspace],
        dir_to_display_name: Optional[Dict[str, str]] = None,
        pattern: Optional[str] = None,
    ) -> None:
        """
        Load path data from multiple directories.

        Args:
            workspaces: List of workspacecontaining net data
            dir_to_display_name: Optional mapping from directory names to display names
            pattern : File pattern to search for wire path files
        """
        self.dir_to_display_name = dir_to_display_name or {}
        self.workspaces = workspaces

        for workspace in workspaces:
            design_name = workspace.design

            vector_loader = DataVectors(workspace)

            path_db = vector_loader.load_timing_paths_metrics(workspace.get_wire_paths_path())

            path_list = []
            for path_metric in path_db:
                inst_delay = sum(path_metric.inst_delay)
                net_delay = sum(path_metric.net_delay)
                total_delay = inst_delay + net_delay
                stage = path_metric.stage

                path_list.append(
                    {
                        "inst_delay": inst_delay,
                        "net_delay": net_delay,
                        "total_delay": total_delay,
                        "stage": stage,
                    }
                )

            # transform results into DataFrame
            df = pd.DataFrame(path_list)

            self.path_data[design_name] = {
                "design_name": design_name,
                "df": df,
                "file_count": len(path_list),
            }

        if not self.path_data:
            raise ValueError("No valid results found from any directory.")

        print(f"Loaded data from {len(self.path_data)} directories.")

    def analyze(self) -> None:
        """
        Analyze the loaded path data.
        """
        if not self.path_data:
            raise ValueError("No data loaded. Please call load() first.")

        # merge all dataframes into a single DataFrame
        all_dfs = []
        for design_name, data in self.path_data.items():
            df = data["df"].copy()
            df["design_name"] = design_name
            all_dfs.append(df)

        # compute summary statistics for each design
        for design_name, data in self.path_data.items():
            df = data["df"]

            stats = {
                "design": design_name,
                "display_name": self.dir_to_display_name.get(design_name, design_name),
                "file_count": data["file_count"],
                "inst_delay_mean": df["inst_delay"].mean(),
                "inst_delay_median": df["inst_delay"].median(),
                "inst_delay_std": df["inst_delay"].std(),
                "net_delay_mean": df["net_delay"].mean(),
                "net_delay_median": df["net_delay"].median(),
                "net_delay_std": df["net_delay"].std(),
                "total_delay_mean": df["total_delay"].mean(),
                "total_delay_median": df["total_delay"].median(),
                "total_delay_std": df["total_delay"].std(),
                "raw_data": df[["inst_delay", "net_delay", "total_delay"]].values,
            }

            self.design_stats[design_name] = stats

        print(f"Analysis completed for {len(self.design_stats)} designs.")

    def report(self) -> str:
        """
        Generate a text report of the path delay analysis.
        
        Returns:
            str: Formatted report string
        """
        if not self.design_stats:
            return "No analysis results available. Please run analyze() first."
        
        report_lines = []
        report_lines.append("**PATH DELAY ANALYSIS REPORT**")
        report_lines.append(f"")
        
        # Overall statistics
        total_paths = sum(stats['file_count'] for stats in self.design_stats.values())
        report_lines.append(f"**OVERALL STATISTICS**")
        report_lines.append(f"- Total designs analyzed: {len(self.design_stats)}")
        report_lines.append(f"- Total paths analyzed: {total_paths}")
        
        # Delay statistics summary
        all_inst_delays = []
        all_net_delays = []
        all_total_delays = []
        
        for stats in self.design_stats.values():
            all_inst_delays.append(stats['inst_delay_mean'])
            all_net_delays.append(stats['net_delay_mean'])
            all_total_delays.append(stats['total_delay_mean'])
        
        report_lines.append(f"")
        report_lines.append(f"**DELAY STATISTICS SUMMARY**")
        report_lines.append(f"- Instance Delay - Mean: {np.mean(all_inst_delays):.3f}, Std: {np.std(all_inst_delays):.3f}")
        report_lines.append(f"- Net Delay - Mean: {np.mean(all_net_delays):.3f}, Std: {np.std(all_net_delays):.3f}")
        report_lines.append(f"- Total Delay - Mean: {np.mean(all_total_delays):.3f}, Std: {np.std(all_total_delays):.3f}")
        
        # Per-design summary
        report_lines.append(f"")
        report_lines.append(f"**PER-DESIGN SUMMARY**")
        for design_name, stats in self.design_stats.items():
            display_name = stats['display_name']
            report_lines.append(f"")
            report_lines.append(f"**Design: {display_name} ({design_name})**")
            report_lines.append(f"- Paths: {stats['file_count']}")
            report_lines.append(f"- Instance Delay: {stats['inst_delay_mean']:.3f} ± {stats['inst_delay_std']:.3f} (median: {stats['inst_delay_median']:.3f})")
            report_lines.append(f"- Net Delay: {stats['net_delay_mean']:.3f} ± {stats['net_delay_std']:.3f} (median: {stats['net_delay_median']:.3f})")
            report_lines.append(f"- Total Delay: {stats['total_delay_mean']:.3f} ± {stats['total_delay_std']:.3f} (median: {stats['total_delay_median']:.3f})")
        
        return report_lines

    def visualize(self, save_path: Optional[str] = None) -> None:
        """
        Visualize the delay data.

        Args:
            save_path: Directory to save the visualizations
        """

        if not hasattr(self, "design_stats") or not self.design_stats:
            raise ValueError("No analysis results found. Please call analyze() first.")

        # set default save path
        if save_path is None:
            save_path = "."
        if len(self.workspaces) == 1:
            save_path = self.workspaces[0].paths_table.analysis_dir
            print(f"Only one workspace, using save path: {save_path}")
        # create DataFrame for visualization
        df_summary = pd.DataFrame([stats for stats in self.design_stats.values()])

        # visulization
        self._create_delay_boxplot(df_summary, save_path)
        self._create_delay_scatter(df_summary, save_path)

    def _create_delay_boxplot(self, df_summary: pd.DataFrame, save_path: str) -> None:
        """create delay boxplot"""

        fig = plt.figure(figsize=(5, 4))

        # select top 10 designs by total delay mean
        top_designs = df_summary.sort_values("total_delay_mean", ascending=False).head(
            10
        )

        delay_data = []
        display_labels = []

        for _, row in top_designs.iterrows():
            design = row["design"]
            if design in self.design_stats:
                delay_data.append(
                    self.design_stats[design]["raw_data"][:, 2]
                )  # total delay
                display_labels.append(row["display_name"])

        bp = plt.boxplot(
            delay_data, labels=display_labels, showfliers=False, patch_artist=True
        )

        for box in bp["boxes"]:
            box.set(facecolor="lightblue", alpha=0.8)
        for median in bp["medians"]:
            median.set(color="navy", linewidth=1.5)
        for cap in bp["caps"]:
            cap.set(color="black", linewidth=1.0)

        plt.ylabel("Total Delay (ns)")

        # set x labels to italic
        ax = plt.gca()
        for tick in ax.get_xticklabels():
            tick.set_style("italic")

        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tick_params(axis="both", which="major", direction="out", length=4, width=1)

        plt.tight_layout()

        if len(self.workspaces) == 1:
            output_path = self.workspaces[0].paths_table.get_image_path("path_delay_boxplot")
        else:
            output_path = os.path.join(save_path, "path_delay_boxplot.png")
        plt.savefig(output_path, bbox_inches="tight")
        plt.close()

        print(f"Delay boxplot saved to {output_path}")

    def _create_delay_scatter(self, df_summary: pd.DataFrame, save_path: str) -> None:
        """create delay scatter plot"""

        fig = plt.figure(figsize=(5, 4))

        sc = plt.scatter(
            df_summary["inst_delay_mean"],
            df_summary["net_delay_mean"],
            alpha=0.8,
            c=df_summary["total_delay_mean"],
            cmap="YlGnBu",
            s=80,
            edgecolors="k",
            linewidths=0.5,
        )

        # add annotations for top 5 designs
        top_designs = (
            df_summary.sort_values("total_delay_mean", ascending=False)
            .head(5)
            .index.tolist()
        )
        for idx in top_designs:
            display_name = df_summary["display_name"].iloc[idx]
            x = df_summary["inst_delay_mean"].iloc[idx]
            y = df_summary["net_delay_mean"].iloc[idx]

            plt.annotate(
                f"$\\it{{{display_name}}}$",
                (x, y),
                fontsize=8,
                xytext=(5, 5),
                textcoords="offset points",
                bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.7),
            )

        plt.xlabel("Average Instance Delay (ns)")
        plt.ylabel("Average Net Delay (ns)")

        cbar = plt.colorbar(sc, label="Total Delay (ns)")
        cbar.ax.tick_params(labelsize=8)

        plt.grid(True, linestyle="--", alpha=0.7)
        plt.tick_params(axis="both", which="major", direction="out", length=4, width=1)

        # scientific notation for y-axis
        ax = plt.gca()
        ax.yaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
        ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        ax.yaxis.offsetText.set_visible(False)

        ax.text(
            0.01,
            0.98,
            r"$\times 10^{-3}$",
            transform=ax.transAxes,
            verticalalignment="top",
            horizontalalignment="left",
            fontsize=10,
        )

        plt.tight_layout()

        if len(self.workspaces) == 1:
            output_path = self.workspaces[0].paths_table.get_image_path("path_delay_scatter")
        else:
            output_path = os.path.join(save_path, "path_delay_scatter.png")
        plt.savefig(output_path, bbox_inches="tight")
        plt.close()

        print(f"Delay scatter plot saved to {output_path}")


class StageAnalyzer(BaseAnalyzer):
    """Analyzer for path stage."""

    def __init__(self):
        super().__init__()
        self.path_data = {}
        self.design_stats = {}

    def load(
        self,
        workspaces: List[Workspace],
        dir_to_display_name: Optional[Dict[str, str]] = None,
        pattern: Optional[str] = None,
    ) -> None:
        """
        load stage data from multiple directories

        Args:
            workspaces: List of workspacecontaining stage data
            dir_to_display_name: map directory names to display names
            pattern : File pattern to search for wire path files
        """
        self.dir_to_display_name = dir_to_display_name or {}
        self.workspaces = workspaces

        for workspace in workspaces:
            design_name = workspace.design

            vector_loader = DataVectors(workspace)

            path_db = vector_loader.load_timing_paths_metrics(workspace.get_wire_paths_path())

            path_list = []
            for path_metric in path_db:
                inst_delay = sum(path_metric.inst_delay)
                net_delay = sum(path_metric.net_delay)
                total_delay = inst_delay + net_delay
                stage = path_metric.stage

                path_list.append(
                    {
                        "inst_delay": inst_delay,
                        "net_delay": net_delay,
                        "total_delay": total_delay,
                        "stage": stage,
                    }
                )

            # transform results into DataFrame
            df = pd.DataFrame(path_list)

            # filter out rows without stage information
            df_with_stage = df.dropna(subset=["stage"])

            self.path_data[design_name] = {
                "design_name": design_name,
                "df": df_with_stage,
                "file_count": len(path_list),
            }

        if not self.path_data:
            raise ValueError("No valid results found from any directory.")

        print(f"Loaded stage data from {len(self.path_data)} directories.")

    def analyze(self) -> None:
        """
        analyze the loaded stage data
        """
        if not self.path_data:
            raise ValueError("No data loaded. Please call load() first.")

        # merge all dataframes into a single DataFrame
        all_dfs = []
        for design_name, data in self.path_data.items():
            df = data["df"].copy()
            df["design_name"] = design_name
            all_dfs.append(df)

        # compute summary statistics for each design
        for design_name, data in self.path_data.items():
            df = data["df"]

            # randomly select an example row
            example_idx = np.random.randint(0, len(df))

            stats = {
                "design": design_name,
                "display_name": self.dir_to_display_name.get(design_name, design_name),
                "file_count": data["file_count"],
                "stage_mean": df["stage"].mean(),
                "stage_median": df["stage"].median(),
                "stage_std": df["stage"].std(),
                "stage_min": df["stage"].min(),
                "stage_max": df["stage"].max(),
                "total_delay_mean": df["total_delay"].mean(),
            }

            self.design_stats[design_name] = stats

        print(f"Analysis completed for {len(self.design_stats)} designs.")

    def report(self) -> str:
        """
        Generate a text report of the stage analysis.
        
        Returns:
            str: Formatted report string
        """
        if not self.design_stats:
            return "No analysis results available. Please run analyze() first."
        
        report_lines = []
        report_lines.append("**STAGE ANALYSIS REPORT**")
        
        # Overall statistics
        total_paths = sum(stats['file_count'] for stats in self.design_stats.values())
        report_lines.append(f"")
        report_lines.append(f"**OVERALL STATISTICS**")
        report_lines.append(f"- Total designs analyzed: {len(self.design_stats)}")
        report_lines.append(f"- Total paths analyzed: {total_paths}")
        
        # Stage statistics summary
        all_stage_means = []
        all_stage_mins = []
        all_stage_maxs = []
        all_delay_means = []
        
        for stats in self.design_stats.values():
            all_stage_means.append(stats['stage_mean'])
            all_stage_mins.append(stats['stage_min'])
            all_stage_maxs.append(stats['stage_max'])
            all_delay_means.append(stats['total_delay_mean'])
        
        report_lines.append(f"")
        report_lines.append(f"**STAGE STATISTICS SUMMARY**")
        report_lines.append(f"- Average Stage Count - Mean: {np.mean(all_stage_means):.2f}, Std: {np.std(all_stage_means):.2f}")
        report_lines.append(f"- Stage Range - Min: {min(all_stage_mins)}, Max: {max(all_stage_maxs)}")
        report_lines.append(f"- Total Delay - Mean: {np.mean(all_delay_means):.3f}, Std: {np.std(all_delay_means):.3f}")
        
        # Per-design summary
        report_lines.append(f"")
        report_lines.append(f"**PER-DESIGN SUMMARY**")
        for design_name, stats in self.design_stats.items():
            display_name = stats['display_name']
            report_lines.append(f"**Design: {display_name} ({design_name})**")
            report_lines.append(f"- Paths: {stats['file_count']}")
            report_lines.append(f"- Stage Count: {stats['stage_mean']:.2f} ± {stats['stage_std']:.2f} (median: {stats['stage_median']:.2f})")
            report_lines.append(f"- Stage Range: {stats['stage_min']} - {stats['stage_max']}")
            report_lines.append(f"- Average Total Delay: {stats['total_delay_mean']:.3f}")
        
        return report_lines

    def visualize(self, save_path: Optional[str] = None) -> None:
        """
        visualize the stage data

        Args:
            save_path: directory to save the visualizations
        """
        if not hasattr(self, "design_stats") or not self.design_stats:
            raise ValueError("No analysis results found. Please call analyze() first.")

        # set default save path
        if save_path is None:
            save_path = "."
        if self.workspaces.__len__() == 1:
            save_path = self.workspaces[0].paths_table.analysis_dir
            print(f"Only one workspace, using save path: {save_path}")

        # create DataFrame for visualization
        df_summary = pd.DataFrame([stats for stats in self.design_stats.values()])

        # visualization
        self._create_stage_errorbar(df_summary, save_path)
        self._create_stage_scatter(df_summary, save_path)

    def _create_stage_errorbar(self, df_summary: pd.DataFrame, save_path: str) -> None:
        """create stage errorbar plot"""

        fig = plt.figure(figsize=(5, 4))

        # sort designs by stage mean and limit to top 15
        df_sorted = df_summary.sort_values("stage_mean", ascending=False)
        if len(df_sorted) > 15:
            df_sorted = df_sorted.head(15)

        display_names = df_sorted["display_name"].tolist()

        # create errorbar plot
        plt.errorbar(
            display_names,
            df_sorted["stage_mean"],
            yerr=[
                df_sorted["stage_mean"] - df_sorted["stage_min"],
                df_sorted["stage_max"] - df_sorted["stage_mean"],
            ],
            fmt="o",
            capsize=5,
            ecolor="darkred",
            markerfacecolor="blue",
            markersize=6,
            markeredgecolor="black",
            markeredgewidth=0.5,
        )

        plt.ylabel("Stage")

        # set x labels to italic
        ax = plt.gca()
        for tick in ax.get_xticklabels():
            tick.set_style("italic")

        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tick_params(axis="both", which="major", direction="out", length=4, width=1)

        plt.tight_layout()

        if len(self.workspaces) == 1:
            output_path = self.workspaces[0].paths_table.get_image_path("path_stage_errorbar")
        else:
            output_path = os.path.join(save_path, "path_stage_errorbar.png")
        plt.savefig(output_path, bbox_inches="tight")
        plt.close()

        print(f"Stage errorbar plot saved to {output_path}")

    def _create_stage_scatter(self, df_summary: pd.DataFrame, save_path: str) -> None:
        """create stage scatter plot"""

        fig = plt.figure(figsize=(5, 4))

        # create scatter plot
        sc = plt.scatter(
            df_summary["stage_mean"],
            df_summary["total_delay_mean"],
            alpha=0.8,
            s=80,
            c=df_summary["stage_std"],
            cmap="YlGnBu",
            edgecolors="k",
            linewidths=0.5,
        )

        # add labels and annotations
        for i, row in df_summary.iterrows():
            x = row["stage_mean"]
            y = row["total_delay_mean"]
            display_name = row["display_name"]

            plt.annotate(
                f"$\\it{{{display_name}}}$",
                (x, y),
                fontsize=8,
                xytext=(5, 5),
                textcoords="offset points",
                bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.7),
            )

        plt.xlabel("Average Stage")
        plt.ylabel("Average Total Delay (ns)")

        cbar = plt.colorbar(sc, label="Stage Standard Deviation")
        cbar.ax.tick_params(labelsize=8)

        plt.grid(True, linestyle="--", alpha=0.7)
        plt.tick_params(axis="both", which="major", direction="out", length=4, width=1)

        # add trend line if there are multiple points
        if len(df_summary) > 1:
            z = np.polyfit(df_summary["stage_mean"], df_summary["total_delay_mean"], 1)
            p = np.poly1d(z)
            x_trend = np.linspace(
                df_summary["stage_mean"].min(), df_summary["stage_mean"].max(), 100
            )
            plt.plot(
                x_trend,
                p(x_trend),
                "--",
                color="red",
                linewidth=1.5,
                label=f"Trend: y={z[0]:.3f}x+{z[1]:.3f}",
            )
            plt.legend(loc="upper left")

        plt.tight_layout()

        if len(self.workspaces) == 1:
            output_path = self.workspaces[0].paths_table.get_image_path("path_stage_delay_scatter")
        else:
            output_path = os.path.join(save_path, "path_stage_delay_scatter.png")
        plt.savefig(output_path, bbox_inches="tight")
        plt.close()

        print(f"Stage scatter plot saved to {output_path}")
