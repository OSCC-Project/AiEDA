#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : patch.py
@Author : yhqiu
@Desc : Patch-level data analysis, including wire density and feature correlation for individual patches, and spatial mapping analysis for the entire chip layout
"""

import os
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import seaborn as sns
from mpl_toolkits.axes_grid1 import make_axes_locatable

from ..data import DataVectors
from ..workspace import Workspace
from .base import BaseAnalyzer


class WireDensityAnalyzer(BaseAnalyzer):
    """Analyzer for wire density and congestion analysis"""

    def __init__(self):
        super().__init__()
        self.patch_data = {}
        self.design_stats = {}
        self.valid_layers = [2, 4, 6, 8, 10, 12]  # Important layers for analysis

    def load(
        self,
        workspace_dirs: List[Workspace],
        dir_to_display_name: Optional[Dict[str, str]] = None,
        pattern: Optional[str] = None,
    ) -> None:
        """
        Load wire density data from multiple directories

        Args:
            workspace_dirs: List of base directories containing patch data
            dir_to_display_name: Optional mapping from directory names to display names
            pattern : Pattern to match patch files
            max_workers: Maximum number of worker processes (default: min(8, cpu_count()))
            verbose: Whether to show progress information
        """
        self.dir_to_display_name = dir_to_display_name or {}
        self.workspace_dirs = workspace_dirs
        for workspace in workspace_dirs:
            design_name = workspace.design

            vector_loader = DataVectors(workspace)

            patch_dir = workspace.directory + pattern

            patch_db = vector_loader.load_patchs(patch_dir)

            patch_list = []
            for vec_patch in patch_db:
                # Extract basic patch features
                patch_features = {
                    "CellDensity": vec_patch.cell_density,
                    "PinDensity": vec_patch.pin_density,
                    "NetDensity": vec_patch.net_density,
                    "RUDY": vec_patch.RUDY_congestion,
                    "Congestion": vec_patch.EGR_congestion,
                    "Timing": vec_patch.timing_map,
                    "Power": vec_patch.power_map,
                    "IRDrop": vec_patch.ir_drop_map,
                }

                # Extract per-layer congestion and wire density information
                layer_congestion = []
                layer_wire_density = []

                for layer in vec_patch.patch_layer:
                    if layer.congestion is not None and layer.wire_density is not None:
                        layer_congestion.append(layer.congestion)
                        layer_wire_density.append(layer.wire_density)
                    else:
                        layer_congestion.append(0.0)
                        layer_wire_density.append(0.0)

                # Ensure consistent list length (should have 20 layers)
                while len(layer_congestion) < 20:
                    layer_congestion.append(0.0)
                    layer_wire_density.append(0.0)

                # Keep only first 20 layers
                layer_congestion = layer_congestion[:20]
                layer_wire_density = layer_wire_density[:20]

                patch_list.append(
                    {
                        "features": patch_features,
                        "layer_congestion": layer_congestion,
                        "layer_wire_density": layer_wire_density,
                    }
                )

            # create features DataFrame
            features_df = pd.DataFrame([p["features"] for p in patch_list])

            # calculate average layer congestion and wire density
            avg_layer_congestion = np.mean(
                [p["layer_congestion"] for p in patch_list], axis=0
            )
            avg_layer_wire_density = np.mean(
                [p["layer_wire_density"] for p in patch_list], axis=0
            )

            self.patch_data[design_name] = {
                "design_name": design_name,
                "df": features_df,
                "avg_layer_congestion": avg_layer_congestion,
                "avg_layer_wire_density": avg_layer_wire_density,
                "file_count": len(patch_list),
                "raw_layer_data": {
                    "congestion": [p["layer_congestion"] for p in patch_list],
                    "wire_density": [p["layer_wire_density"] for p in patch_list],
                },
            }

        if not self.patch_data:
            raise ValueError("No valid results found from any directory.")

    def analyze(self) -> None:
        """
        Analyze loaded wire density data
        """
        if not self.patch_data:
            raise ValueError("No data loaded. Please call load() first.")

        # Calculate statistics for each design
        for design_name, data in self.patch_data.items():
            stats = {
                "design": design_name,
                "display_name": self.dir_to_display_name.get(design_name, design_name),
                "file_count": data["file_count"],
                "avg_layer_congestion": data["avg_layer_congestion"],
                "avg_layer_wire_density": data["avg_layer_wire_density"],
                "raw_layer_data": data["raw_layer_data"],
            }

            # Calculate layer-wise statistics
            for layer in self.valid_layers:
                if layer < len(data["avg_layer_congestion"]):
                    stats[f"layer_{layer}_congestion"] = data["avg_layer_congestion"][
                        layer
                    ]
                    stats[f"layer_{layer}_wire_density"] = data[
                        "avg_layer_wire_density"
                    ][layer]
                else:
                    stats[f"layer_{layer}_congestion"] = 0.0
                    stats[f"layer_{layer}_wire_density"] = 0.0

            self.design_stats[design_name] = stats

        print(f"Analysis completed for {len(self.design_stats)} designs.")

    def visualize(self, save_path: Optional[str] = None) -> None:
        """
        Visualize wire density analysis results

        Args:
            save_path: Directory to save visualization results
        """
        if not hasattr(self, "design_stats") or not self.design_stats:
            raise ValueError("No analysis results found. Please call analyze() first.")

        # Set output directory
        if save_path is None:
            save_path = "."
        if self.workspace_dirs.__len__() == 1:
            save_path = self.workspace_dirs[0].paths_table.analysis_path
            print(f"Only one workspace, using save path: {save_path}")

        # Generate visualizations
        self._create_wire_density_scatter(save_path)
        self._create_layer_comparison_plot(save_path)

    def _create_wire_density_scatter(self, save_path: str) -> None:
        """Create scatter plot of congestion vs wire density with regression lines"""

        fig, ax = plt.subplots(figsize=(5, 4))

        # Get default color cycle
        prop_cycle = plt.rcParams["axes.prop_cycle"]
        colors = prop_cycle.by_key()["color"]

        # Ensure enough colors
        if len(colors) < len(self.valid_layers):
            colors = colors * (len(self.valid_layers) // len(colors) + 1)

        # Create layer to color mapping
        layer_color_map = {
            layer: colors[i % len(colors)] for i, layer in enumerate(self.valid_layers)
        }

        for layer in self.valid_layers:
            x_values = []
            y_values = []

            for design_name, stats in self.design_stats.items():
                x = stats.get(f"layer_{layer}_wire_density", 0)
                y = stats.get(f"layer_{layer}_congestion", 0)
                if x != 0 and y != 0:  # Filter out invalid data
                    x_values.append(x)
                    y_values.append(y)

            if len(x_values) > 1:  # Ensure enough points for fitting
                color = layer_color_map[layer]

                # Scatter plot
                ax.scatter(
                    x_values,
                    y_values,
                    label=f"Layer {layer}",
                    alpha=0.7,
                    color=color,
                    s=50,
                )

                # Linear regression
                if len(x_values) > 1:
                    z = np.polyfit(x_values, y_values, 1)
                    p = np.poly1d(z)

                    # Calculate R² value
                    y_pred = p(x_values)

                    # Plot regression line
                    x_range = np.linspace(min(x_values), max(x_values), 100)
                    ax.plot(x_range, p(x_range), "--", color=color, linewidth=2)

        # Set labels and formatting
        ax.set_xlabel("Wire Density", fontsize=12)
        ax.set_ylabel("EGR Congestion", fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper right", ncol=1, fontsize=10)

        plt.tight_layout()

        output_path = os.path.join(
            save_path, "patch_congestion_wire_density_regression.png"
        )
        plt.savefig(output_path, bbox_inches="tight")
        plt.close()

        print(f"Wire density scatter plot saved to {output_path}")

    def _create_layer_comparison_plot(self, save_path: str) -> None:
        """Create comparison plot of different layers"""

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

        # Prepare data for plotting
        designs = list(self.design_stats.keys())
        display_names = [self.design_stats[d]["display_name"] for d in designs]

        # Plot 1: Average congestion by layer
        congestion_data = []
        for layer in self.valid_layers:
            layer_values = [
                self.design_stats[d].get(f"layer_{layer}_congestion", 0)
                for d in designs
            ]
            congestion_data.append(layer_values)

        positions = np.arange(len(designs))
        width = 0.12

        for i, layer in enumerate(self.valid_layers):
            offset = (i - len(self.valid_layers) / 2) * width
            ax1.bar(
                positions + offset,
                congestion_data[i],
                width,
                label=f"Layer {layer}",
                alpha=0.8,
            )

        ax1.set_xlabel("Design")
        ax1.set_ylabel("Average Congestion")
        ax1.set_title("Congestion by Layer")
        ax1.set_xticks(positions)
        ax1.set_xticklabels(display_names, rotation=45, ha="right")
        ax1.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        ax1.grid(axis="y", alpha=0.3)

        # Plot 2: Average wire density by layer
        wire_density_data = []
        for layer in self.valid_layers:
            layer_values = [
                self.design_stats[d].get(f"layer_{layer}_wire_density", 0)
                for d in designs
            ]
            wire_density_data.append(layer_values)

        for i, layer in enumerate(self.valid_layers):
            offset = (i - len(self.valid_layers) / 2) * width
            ax2.bar(
                positions + offset,
                wire_density_data[i],
                width,
                label=f"Layer {layer}",
                alpha=0.8,
            )

        ax2.set_xlabel("Design")
        ax2.set_ylabel("Average Wire Density")
        ax2.set_title("Wire Density by Layer")
        ax2.set_xticks(positions)
        ax2.set_xticklabels(display_names, rotation=45, ha="right")
        ax2.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        ax2.grid(axis="y", alpha=0.3)

        plt.tight_layout()

        output_path = os.path.join(save_path, "patch_layer_comparison.png")
        plt.savefig(output_path, bbox_inches="tight")
        plt.close()

        print(f"Layer comparison plot saved to {output_path}")


class FeatureCorrelationAnalyzer(BaseAnalyzer):
    """Analyzer for patch feature correlation analysis"""

    def __init__(self):
        super().__init__()
        self.patch_data = {}
        self.correlation_matrix = None
        self.feature_stats = {}
        self.correlation_features = [
            "CellDensity",
            "PinDensity",
            "NetDensity",
            "RUDY",
            "Congestion",
            "Timing",
            "Power",
            "IRDrop",
        ]

    def load(
        self,
        workspace_dirs: List[Workspace],
        dir_to_display_name: Optional[Dict[str, str]] = None,
        pattern: Optional[str] = None,
    ) -> None:
        """
        Load patch feature data from multiple directories

        Args:
            workspace_dirs: List of base directories containing patch data
            dir_to_display_name: Optional mapping from directory names to display names
            pattern : Pattern to match patch files
        """
        self.dir_to_display_name = dir_to_display_name or {}
        self.workspace_dirs = workspace_dirs
        for workspace in workspace_dirs:
            design_name = workspace.design

            vector_loader = DataVectors(workspace)

            patch_dir = workspace.directory + pattern

            patch_db = vector_loader.load_patchs(patch_dir)

            patch_list = []
            for vec_patch in patch_db:
                # Extract basic patch features
                patch_features = {
                    "CellDensity": vec_patch.cell_density,
                    "PinDensity": vec_patch.pin_density,
                    "NetDensity": vec_patch.net_density,
                    "RUDY": vec_patch.RUDY_congestion,
                    "Congestion": vec_patch.EGR_congestion,
                    "Timing": vec_patch.timing_map,
                    "Power": vec_patch.power_map,
                    "IRDrop": vec_patch.ir_drop_map,
                }

                # Extract per-layer congestion and wire density information
                layer_congestion = []
                layer_wire_density = []

                for layer in vec_patch.patch_layer:
                    if layer.congestion is not None and layer.wire_density is not None:
                        layer_congestion.append(layer.congestion)
                        layer_wire_density.append(layer.wire_density)
                    else:
                        layer_congestion.append(0.0)
                        layer_wire_density.append(0.0)

                # Ensure consistent list length (should have 20 layers)
                while len(layer_congestion) < 20:
                    layer_congestion.append(0.0)
                    layer_wire_density.append(0.0)

                # Keep only first 20 layers
                layer_congestion = layer_congestion[:20]
                layer_wire_density = layer_wire_density[:20]

                patch_list.append(
                    {
                        "features": patch_features,
                        "layer_congestion": layer_congestion,
                        "layer_wire_density": layer_wire_density,
                    }
                )

            # create features DataFrame
            features_df = pd.DataFrame([p["features"] for p in patch_list])

            # calculate average layer congestion and wire density
            avg_layer_congestion = np.mean(
                [p["layer_congestion"] for p in patch_list], axis=0
            )
            avg_layer_wire_density = np.mean(
                [p["layer_wire_density"] for p in patch_list], axis=0
            )

            self.patch_data[design_name] = {
                "design_name": design_name,
                "df": features_df,
                "avg_layer_congestion": avg_layer_congestion,
                "avg_layer_wire_density": avg_layer_wire_density,
                "file_count": len(patch_list),
                "raw_layer_data": {
                    "congestion": [p["layer_congestion"] for p in patch_list],
                    "wire_density": [p["layer_wire_density"] for p in patch_list],
                },
            }

        if not self.patch_data:
            raise ValueError("No valid results found from any directory.")

        print(f"Loaded feature data from {len(self.patch_data)} directories.")

    def analyze(self) -> None:
        """
        Analyze feature correlations
        """
        if not self.patch_data:
            raise ValueError("No data loaded. Please call load() first.")

        # Combine all design data
        all_dfs = []
        for design_name, data in self.patch_data.items():
            df = data["df"].copy()
            df["design_name"] = design_name
            all_dfs.append(df)

        combined_df = pd.concat(all_dfs, ignore_index=True)

        # Calculate correlation matrix
        self.correlation_matrix = combined_df[self.correlation_features].corr()

        # Calculate feature statistics for each design
        for design_name, data in self.patch_data.items():
            df = data["df"]

            stats = {
                "design": design_name,
                "display_name": self.dir_to_display_name.get(design_name, design_name),
                "file_count": data["file_count"],
            }

            # Calculate statistics for each feature
            for feature in self.correlation_features:
                if feature in df.columns:
                    stats[f"{feature}_mean"] = df[feature].mean()
                    stats[f"{feature}_std"] = df[feature].std()
                    stats[f"{feature}_median"] = df[feature].median()
                    stats[f"{feature}_min"] = df[feature].min()
                    stats[f"{feature}_max"] = df[feature].max()
                else:
                    for suffix in ["_mean", "_std", "_median", "_min", "_max"]:
                        stats[f"{feature}{suffix}"] = 0.0

            self.feature_stats[design_name] = stats

        print(f"Correlation analysis completed for {len(self.feature_stats)} designs.")

    def visualize(self, save_path: Optional[str] = None) -> None:
        """
        Visualize feature correlation analysis results

        Args:
            save_path: Directory to save visualization results
        """
        if not hasattr(self, "correlation_matrix") or self.correlation_matrix is None:
            raise ValueError("No analysis results found. Please call analyze() first.")

        # Set output directory
        if save_path is None:
            save_path = "."
        if self.workspace_dirs.__len__() == 1:
            save_path = self.workspace_dirs[0].paths_table.analysis_path
            print(f"Only one workspace, using save path: {save_path}")
        # Generate visualizations
        self._create_correlation_heatmap(save_path)
        self._create_feature_distribution_plot(save_path)

    def _create_correlation_heatmap(self, save_path: str) -> None:
        """Create feature correlation heatmap"""

        plt.figure(figsize=(5, 4))

        # Create heatmap with optimized font and layout
        heatmap = sns.heatmap(
            self.correlation_matrix,
            annot=True,  # Show values
            cmap="coolwarm",  # Use cool-warm color scheme
            fmt=".2f",  # Keep two decimal places
            linewidths=0.3,  # Grid line width
            annot_kws={"size": 10},  # Annotation font size
        )

        # Adjust axis labels font size and rotation
        plt.xticks(rotation=30, fontsize=10)
        plt.yticks(rotation=30, fontsize=10)

        # Adjust layout to avoid label truncation
        plt.tight_layout(pad=1.1)

        # Save plots
        output_path = os.path.join(save_path, "patch_feature_correlation.png")
        plt.savefig(output_path)
        plt.close()

        print(f"Feature correlation heatmap saved to {output_path}")

    def _create_feature_distribution_plot(self, save_path: str) -> None:
        """Create feature distribution comparison plot"""

        # Create subplots for different features
        fig, axes = plt.subplots(2, 4, figsize=(16, 8))
        axes = axes.flatten()

        for i, feature in enumerate(self.correlation_features):
            ax = axes[i]

            # Collect data for each design
            designs = list(self.feature_stats.keys())
            display_names = [self.feature_stats[d]["display_name"] for d in designs]
            feature_means = [
                self.feature_stats[d].get(f"{feature}_mean", 0) for d in designs
            ]
            feature_stds = [
                self.feature_stats[d].get(f"{feature}_std", 0) for d in designs
            ]

            # Create bar plot with error bars
            bars = ax.bar(
                display_names,
                feature_means,
                yerr=feature_stds,
                capsize=3,
                alpha=0.7,
                color=f"C{i}",
            )

            ax.set_title(f"{feature}")
            ax.set_ylabel("Value")
            ax.tick_params(axis="x", rotation=45)
            ax.grid(axis="y", alpha=0.3)

            # Format y-axis for better readability
            if max(feature_means) > 1000:
                ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))

        plt.tight_layout()

        output_path = os.path.join(save_path, "patch_feature_distributions.png")
        plt.savefig(output_path, bbox_inches="tight")
        plt.close()

        print(f"Feature distribution plot saved to {output_path}")


class MapAnalyzer(BaseAnalyzer):
    """
    Analyzer for visualizing chip layout spatial distribution of features.

    This analyzer creates 2D heatmaps showing the spatial distribution of
    various features across the chip layout, enabling analysis of spatial
    patterns and hotspots.
    """

    def __init__(self):
        super().__init__()
        self.analysis_results = {}
        self.features = [
            "Cell Density",
            "Pin Density",
            "Congestion",
            "Timing",
            "Power",
            "IR Drop",
            "net density",
            "RUDY",
        ]

    def load(
        self,
        workspace_dirs: List[Workspace],
        dir_to_display_name: Dict[str, str],
        pattern: Optional[str],
    ) -> None:
        """
        Load patch data with spatial position information from multiple directories.

        Args:
            workspace_dirs: List of base directory paths
            dir_to_display_name: Mapping from directory names to display names

        """
        print("Loading patch data with spatial positions...")

        if pattern is None:
            raise ValueError("Pattern must be specified to find patch files.")

        self.dir_to_display_name = dir_to_display_name or {}
        self.workspace_dirs = workspace_dirs

        for workspace in workspace_dirs:
            design_name = workspace.design

            vector_loader = DataVectors(workspace)

            patch_dir = workspace.directory + pattern

            patch_db = vector_loader.load_patchs(patch_dir)

            patch_list = []
            for vec_patch in patch_db:
                # Extract basic patch features
                patch_features = {
                    "design": design_name,
                    "row_id": vec_patch.patch_id_row,
                    "col_id": vec_patch.patch_id_col,
                    "Cell Density": vec_patch.cell_density,
                    "Pin Density": vec_patch.pin_density,
                    "Congestion": vec_patch.EGR_congestion,
                    "Timing": vec_patch.timing_map,
                    "Power": vec_patch.power_map,
                    "IR Drop": vec_patch.ir_drop_map,
                    "net density": vec_patch.net_density,
                    "RUDY": vec_patch.RUDY_congestion,
                }

                patch_list.extend([patch_features])

        # create features DataFrame
        self.data = pd.DataFrame(patch_list)
        print(f"Loaded {len(self.data)} patches from {len(workspace_dirs)} designs")

    def analyze(self) -> None:
        """
        Analyze the spatial distribution of features across designs.
        """
        print("Analyzing spatial feature distributions...")

        # Analyze each design separately
        for design in self.data["design"].unique():
            design_data = self.data[self.data["design"] == design]

            # Determine layout dimensions
            max_row = design_data["row_id"].max()
            max_col = design_data["col_id"].max()
            layout_dims = (max_row + 1, max_col + 1)

            print(f"Design {design}: {layout_dims[0]} rows x {layout_dims[1]} columns")

            # Create layout arrays for each feature
            design_layouts = {}
            for feature in self.features:
                layout = np.zeros(layout_dims)

                # Fill layout with feature values
                for _, patch in design_data.iterrows():
                    row = int(patch["row_id"])
                    col = int(patch["col_id"])
                    layout[row, col] = patch[feature]

                design_layouts[feature] = layout

            # Calculate spatial statistics
            spatial_stats = {}
            for feature in self.features:
                layout = design_layouts[feature]
                spatial_stats[feature] = {
                    "mean": np.mean(layout),
                    "std": np.std(layout),
                    "min": np.min(layout),
                    "max": np.max(layout),
                    "hotspot_ratio": np.sum(layout > np.percentile(layout, 90))
                    / layout.size,
                    "spatial_variance": np.var(layout),
                }

            self.analysis_results[design] = {
                "layouts": design_layouts,
                "dimensions": layout_dims,
                "spatial_stats": spatial_stats,
            }

        print("Spatial analysis completed")

    def visualize(self, save_path: Optional[str] = None) -> None:
        """
        Create comprehensive visualizations of spatial feature distributions.
        """
        print("Creating spatial distribution visualizations...")

        # Use consistent colormap
        unified_cmap = "viridis"

        if save_path is None:
            save_path = "."
        if self.workspace_dirs.__len__() == 1:
            save_path = self.workspace_dirs[0].paths_table.analysis_path
            print(f"Only one workspace, using save path: {save_path}")

        # 1. Create individual feature maps for each design
        self._create_individual_feature_maps(save_path, unified_cmap)

        # 2. Create combined feature comparison
        self._create_feature_comparison_grid(save_path, unified_cmap)

        print(f"Visualizations saved to {save_path}/")

    def _create_individual_feature_maps(self, save_path: str, cmap: str) -> None:
        """Create individual heatmaps for each feature and design."""
        for design, results in self.analysis_results.items():
            design_dir = os.path.join(save_path, f"patch_{design}_individual_maps")
            os.makedirs(design_dir, exist_ok=True)

            layouts = results["layouts"]

            for feature in self.features:
                plt.figure(figsize=(8, 6))
                layout_data = layouts[feature]

                # Create heatmap
                im = plt.imshow(
                    layout_data,
                    cmap=cmap,
                    aspect="equal",
                    interpolation="none",
                    origin="lower",
                )

                # Add colorbar with proper formatting
                divider = make_axes_locatable(plt.gca())
                cax = divider.append_axes("right", size="5%", pad=0.1)
                cbar = plt.colorbar(im, cax=cax)

                # Format colorbar for specific features
                if feature == "Power":
                    formatter = ticker.ScalarFormatter(useMathText=True)
                    formatter.set_scientific(True)
                    formatter.set_powerlimits((-4, 4))
                    cbar.ax.yaxis.set_major_formatter(formatter)
                elif feature == "RUDY":
                    formatter = ticker.ScalarFormatter(useMathText=True)
                    formatter.set_scientific(True)
                    formatter.set_powerlimits((0, 0))
                    cbar.ax.yaxis.set_major_formatter(formatter)

                cbar.ax.tick_params(labelsize=10)

                plt.title(f"{feature} Distribution", fontsize=14, pad=20)

                # Add grid for better readability
                plt.grid(True, alpha=0.3, linewidth=0.5)

                plt.tight_layout()
                plt.savefig(
                    os.path.join(
                        design_dir, f"patch_{feature.replace(' ', '_')}_layout.png"
                    )
                )
                plt.close()

    def _create_feature_comparison_grid(self, save_path: str, cmap: str) -> None:
        """Create a grid comparison of all features for each design."""
        for design, results in self.analysis_results.items():
            layouts = results["layouts"]

            # Create subplot grid
            fig, axes = plt.subplots(2, 4, figsize=(16, 8))
            fig.suptitle(
                f"{design} - Feature Distribution Overview", fontsize=16, y=0.95
            )

            axes = axes.flatten()

            for idx, feature in enumerate(self.features):
                ax = axes[idx]
                layout_data = layouts[feature]

                im = ax.imshow(
                    layout_data,
                    cmap=cmap,
                    aspect="equal",
                    interpolation="none",
                    origin="lower",
                )

                # Add colorbar
                divider = make_axes_locatable(ax)
                cax = divider.append_axes("right", size="5%", pad=0.05)
                cbar = plt.colorbar(im, cax=cax)
                cbar.ax.tick_params(labelsize=8)

                # Format specific features
                if feature == "Power":
                    formatter = ticker.ScalarFormatter(useMathText=True)
                    formatter.set_scientific(True)
                    formatter.set_powerlimits((-4, 4))
                    cbar.ax.yaxis.set_major_formatter(formatter)
                elif feature == "RUDY":
                    formatter = ticker.ScalarFormatter(useMathText=True)
                    formatter.set_scientific(True)
                    formatter.set_powerlimits((0, 0))
                    cbar.ax.yaxis.set_major_formatter(formatter)

                ax.set_title(feature, fontsize=12)
                ax.set_xticks([])
                ax.set_yticks([])

            plt.tight_layout()
            plt.savefig(os.path.join(save_path, f"patch_{design}_feature_grid.png"))
            plt.close()
