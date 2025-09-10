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

    def report(self) -> str:
        """Generate a text report summarizing wire density analysis."""
        if not self.design_stats:
            return "No wire density data available for analysis. Please run analyze() first."

        report_lines = []
        report_lines.append("Wire Density Analysis Report")
        report_lines.append("=" * 28)
        
        # Overall statistics
        total_designs = len(self.design_stats)
        total_patches = sum(stats['file_count'] for stats in self.design_stats.values())
        
        report_lines.append(f"Analyzed {total_designs} design(s) with {total_patches:,} total patches")
        report_lines.append("")
        
        # Layer-wise congestion summary
        report_lines.append("Layer-wise Congestion Summary:")
        for layer in self.valid_layers:
            layer_congestions = []
            for stats in self.design_stats.values():
                congestion = stats.get(f'layer_{layer}_congestion', 0.0)
                if congestion > 0:
                    layer_congestions.append(congestion)
            
            if layer_congestions:
                avg_congestion = np.mean(layer_congestions)
                max_congestion = np.max(layer_congestions)
                report_lines.append(f"  Layer {layer}: Avg={avg_congestion:.3f}, Max={max_congestion:.3f} ({len(layer_congestions)} designs)")
        
        report_lines.append("")
        
        # Layer-wise wire density summary
        report_lines.append("Layer-wise Wire Density Summary:")
        for layer in self.valid_layers:
            layer_densities = []
            for stats in self.design_stats.values():
                density = stats.get(f'layer_{layer}_wire_density', 0.0)
                if density > 0:
                    layer_densities.append(density)
            
            if layer_densities:
                avg_density = np.mean(layer_densities)
                max_density = np.max(layer_densities)
                report_lines.append(f"  Layer {layer}: Avg={avg_density:.3f}, Max={max_density:.3f} ({len(layer_densities)} designs)")
        
        report_lines.append("")
        
        # Per-design summary
        report_lines.append("Per-Design Summary:")
        for design_name, stats in self.design_stats.items():
            display_name = stats['display_name']
            patch_count = stats['file_count']
            
            # Calculate overall congestion and density averages
            avg_congestion = np.mean([stats.get(f'layer_{layer}_congestion', 0.0) for layer in self.valid_layers])
            avg_density = np.mean([stats.get(f'layer_{layer}_wire_density', 0.0) for layer in self.valid_layers])
            
            # Find most congested layer
            max_congestion_layer = None
            max_congestion_value = 0
            for layer in self.valid_layers:
                congestion = stats.get(f'layer_{layer}_congestion', 0.0)
                if congestion > max_congestion_value:
                    max_congestion_value = congestion
                    max_congestion_layer = layer
            
            congestion_info = f"Most congested: Layer {max_congestion_layer} ({max_congestion_value:.3f})" if max_congestion_layer else "No congestion data"
            
            report_lines.append(f"  {display_name}: {patch_count:,} patches, Avg Congestion: {avg_congestion:.3f}, Avg Density: {avg_density:.3f}")
            report_lines.append(f"    {congestion_info}")
        
        return "\n".join(report_lines)

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
        if len(self.workspace_dirs) == 1:
            save_path = self.workspace_dirs[0].paths_table.analysis_dir
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

        # Save plot
        if len(self.workspace_dirs) == 1:
            output_path = self.workspace_dirs[0].paths_table.get_image_path("patch_congestion_wire_density_regression")
        else:
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
        
        # Save Plots
        if len(self.workspace_dirs) == 1:
            output_path = self.workspace_dirs[0].paths_table.get_image_path("patch_layer_comparison")
        else:
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

    def report(self) -> str:
        """Generate a text report summarizing feature correlation analysis."""
        if not self.feature_stats or not hasattr(self, 'correlation_matrix'):
            return "No feature correlation data available for analysis. Please run analyze() first."

        report_lines = []
        report_lines.append("Feature Correlation Analysis Report")
        report_lines.append("=" * 35)
        
        # Overall statistics
        total_designs = len(self.feature_stats)
        total_patches = sum(stats['file_count'] for stats in self.feature_stats.values())
        
        report_lines.append(f"Analyzed {total_designs} design(s) with {total_patches:,} total patches")
        report_lines.append(f"Features analyzed: {', '.join(self.correlation_features)}")
        report_lines.append("")
        
        # Strong correlations
        report_lines.append("Strong Feature Correlations (|r| > 0.5):")
        strong_corrs = []
        for i, feature1 in enumerate(self.correlation_features):
            for j, feature2 in enumerate(self.correlation_features):
                if i < j:  # Avoid duplicates and self-correlations
                    corr_val = self.correlation_matrix.loc[feature1, feature2]
                    if abs(corr_val) > 0.5:
                        strong_corrs.append((feature1, feature2, corr_val))
        
        # Sort by absolute correlation strength
        strong_corrs.sort(key=lambda x: abs(x[2]), reverse=True)
        
        if strong_corrs:
            for feature1, feature2, corr_val in strong_corrs[:8]:  # Show top 8
                direction = "positive" if corr_val > 0 else "negative"
                report_lines.append(f"  {feature1} vs {feature2}: {corr_val:.3f} ({direction})")
        else:
            report_lines.append("  No strong correlations found between features")
        
        report_lines.append("")
        
        # Feature statistics summary
        report_lines.append("Feature Statistics Summary:")
        for feature in self.correlation_features:
            all_means = [stats.get(f'{feature}_mean', 0) for stats in self.feature_stats.values()]
            all_stds = [stats.get(f'{feature}_std', 0) for stats in self.feature_stats.values()]
            
            if any(mean > 0 for mean in all_means):
                avg_mean = np.mean([m for m in all_means if m > 0])
                avg_std = np.mean([s for s in all_stds if s > 0])
                min_val = min(stats.get(f'{feature}_min', 0) for stats in self.feature_stats.values())
                max_val = max(stats.get(f'{feature}_max', 0) for stats in self.feature_stats.values())
                
                report_lines.append(f"  {feature}: Avg={avg_mean:.3e}, Std={avg_std:.3e}, Range=[{min_val:.3e}, {max_val:.3e}]")
        
        report_lines.append("")
        
        # Per-design summary
        report_lines.append("Per-Design Summary:")
        for design_name, stats in self.feature_stats.items():
            display_name = stats['display_name']
            patch_count = stats['file_count']
            
            # Show key metrics for each design
            cell_density = stats.get('CellDensity_mean', 0)
            congestion = stats.get('Congestion_mean', 0)
            timing = stats.get('Timing_mean', 0)
            power = stats.get('Power_mean', 0)
            
            report_lines.append(f"  {display_name}: {patch_count:,} patches")
            report_lines.append(f"    Cell Density: {cell_density:.3f}, Congestion: {congestion:.3f}")
            report_lines.append(f"    Timing: {timing:.3e}, Power: {power:.3e}")
        
        return "\n".join(report_lines)

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
            save_path = self.workspace_dirs[0].paths_table.analysis_dir
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
        if len(self.workspace_dirs) == 1:
            output_path = self.workspace_dirs[0].paths_table.get_image_path("patch_feature_correlation")
        else:
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
        
        # Save Plots
        if len(self.workspace_dirs) == 1:
            output_path = self.workspace_dirs[0].paths_table.get_image_path("patch_feature_distributions")
        else:
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

    def report(self) -> str:
        """Generate a text report summarizing spatial feature distribution analysis."""
        if not self.analysis_results:
            return "No spatial analysis data available. Please run analyze() first."

        report_lines = []
        report_lines.append("Spatial Feature Distribution Analysis Report")
        report_lines.append("=" * 43)
        
        # Overall statistics
        total_designs = len(self.analysis_results)
        total_patches = sum(result['dimensions'][0] * result['dimensions'][1] for result in self.analysis_results.values())
        
        report_lines.append(f"Analyzed {total_designs} design(s) with {total_patches:,} total patches")
        report_lines.append(f"Features analyzed: {', '.join(self.features)}")
        report_lines.append("")
        
        # Design layout summary
        report_lines.append("Design Layout Summary:")
        for design, result in self.analysis_results.items():
            display_name = self.dir_to_display_name.get(design, design)
            dims = result['dimensions']
            patch_count = dims[0] * dims[1]
            report_lines.append(f"  {display_name}: {dims[0]} x {dims[1]} grid ({patch_count:,} patches)")
        
        report_lines.append("")
        
        # Feature statistics across all designs
        report_lines.append("Feature Statistics Across All Designs:")
        for feature in self.features:
            all_means = []
            all_maxes = []
            all_hotspot_ratios = []
            
            for result in self.analysis_results.values():
                if feature in result['spatial_stats']:
                    stats = result['spatial_stats'][feature]
                    all_means.append(stats['mean'])
                    all_maxes.append(stats['max'])
                    all_hotspot_ratios.append(stats['hotspot_ratio'])
            
            if all_means:
                avg_mean = np.mean(all_means)
                avg_max = np.mean(all_maxes)
                avg_hotspot_ratio = np.mean(all_hotspot_ratios)
                
                report_lines.append(f"  {feature}:")
                report_lines.append(f"    Avg Mean: {avg_mean:.3e}, Avg Max: {avg_max:.3e}")
                report_lines.append(f"    Avg Hotspot Ratio (>90th percentile): {avg_hotspot_ratio:.1%}")
        
        report_lines.append("")
        
        # Per-design detailed summary
        report_lines.append("Per-Design Detailed Summary:")
        for design, result in self.analysis_results.items():
            display_name = self.dir_to_display_name.get(design, design)
            dims = result['dimensions']
            spatial_stats = result['spatial_stats']
            
            report_lines.append(f"  {display_name} ({dims[0]}x{dims[1]}):")
            
            # Find most critical features
            max_congestion = spatial_stats.get('Congestion', {}).get('max', 0)
            max_timing = spatial_stats.get('Timing', {}).get('max', 0)
            max_power = spatial_stats.get('Power', {}).get('max', 0)
            
            # Find feature with highest spatial variance (most non-uniform)
            max_variance_feature = None
            max_variance_value = 0
            for feature in self.features:
                if feature in spatial_stats:
                    variance = spatial_stats[feature].get('spatial_variance', 0)
                    if variance > max_variance_value:
                        max_variance_value = variance
                        max_variance_feature = feature
            
            report_lines.append(f"    Max Congestion: {max_congestion:.3f}, Max Timing: {max_timing:.3e}, Max Power: {max_power:.3e}")
            if max_variance_feature:
                report_lines.append(f"    Most non-uniform feature: {max_variance_feature} (variance: {max_variance_value:.3e})")
            
            # Show hotspot information
            hotspot_features = []
            for feature in self.features:
                if feature in spatial_stats:
                    hotspot_ratio = spatial_stats[feature].get('hotspot_ratio', 0)
                    if hotspot_ratio > 0.1:  # More than 10% hotspots
                        hotspot_features.append(f"{feature} ({hotspot_ratio:.1%})")
            
            if hotspot_features:
                report_lines.append(f"    Features with significant hotspots: {', '.join(hotspot_features)}")
        
        return "\n".join(report_lines)

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
            save_path = self.workspace_dirs[0].paths_table.analysis_dir
            print(f"Only one workspace, using save path: {save_path}")

        # 1. Create individual feature maps for each design
        self._create_individual_feature_maps(save_path, unified_cmap)

        # 2. Create combined feature comparison
        self._create_feature_comparison_grid(save_path, unified_cmap)

        print(f"Visualizations saved to {save_path}/")

    def _create_individual_feature_maps(self, save_path: str, cmap: str) -> None:
        """Create individual heatmaps for each feature and design."""
        for design, results in self.analysis_results.items():
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
                
                if len(self.workspace_dirs) == 1:
                    output_path = self.workspace_dirs[0].paths_table.get_image_path(f"patch_map_{feature}", design)
                else:
                    output_path = os.path.join(save_path, f"patch_map_{design}_{feature.replace(' ', '_')}.png")
                
                plt.savefig(output_path)
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
            
            if len(self.workspace_dirs) == 1:
                output_path = self.workspace_dirs[0].paths_table.get_image_path("patch_map_union", design)
            else:
                output_path = os.path.join(save_path, f"patch_map_{design}_union.png")
            
            plt.savefig(output_path)
            plt.close()
