#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : patch.py
@Author : yhqiu
@Desc : Patch-level data analysis, including wire density and feature correlation for individual patches, and spatial mapping analysis for the entire chip layout
'''
import os
import json
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
import warnings
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import random
import time
from multiprocessing import Pool, cpu_count
from mpl_toolkits.axes_grid1 import make_axes_locatable  
import matplotlib.ticker as ticker 

from .base import BaseAnalyzer

# =====================================
# tool functions
# =====================================
def process_patch_file(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Process a single patch JSON file to extract features and layer information
    
    Args:
        filepath: Path to the patch JSON file
        
    Returns:
        Dictionary containing patch features and layer data, or None if error
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Extract basic patch features
        patch_features = {
            'CellDensity': data['cell_density'],
            'PinDensity': data['pin_density'],
            'NetDensity': data['net_density'],
            'RUDY': data['RUDY_congestion'],
            'Congestion': data['EGR_congestion'],
            'Timing': data['timing'],
            'Power': data['power'],
            'IRDrop': data['IR_drop']
        }
        
        # Extract per-layer congestion and wire density information
        layer_congestion = []
        layer_wire_density = []
        
        for layer in data['patch_layer']:
            if 'feature' in layer and 'congestion' in layer['feature']:
                layer_congestion.append(layer['feature']['congestion'])
                layer_wire_density.append(layer['feature']['wire_density'])
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
        
        return {
            'features': patch_features,
            'layer_congestion': layer_congestion,
            'layer_wire_density': layer_wire_density,
            'filename': os.path.basename(filepath)
        }
    
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return None
    
    
def process_patch_file_with_position(filepath: str) -> Optional[Dict]:
    """
    Process a single patch file and extract position information and features.
    
    Args:
        filepath: Path to the patch JSON file
        
    Returns:
        Dictionary containing patch data with position information
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Extract row and column information
        row_id = data.get('patch_id_row', 0)
        col_id = data.get('patch_id_col', 0)
        
        # Extract patch features
        patch_features = {
            'row_id': row_id,
            'col_id': col_id,
            'Cell Density': data['cell_density'],
            'Pin Density': data['pin_density'],
            'Congestion': data['EGR_congestion'],
            'Timing': data['timing'],
            'Power': data['power'],
            'IR Drop': data['IR_drop'],
            'net density': data['net_density'],
            'RUDY': data['RUDY_congestion']
        }
        
        return patch_features
    
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return None


def process_single_directory_for_patches(directory: str, pattern: str, verbose: bool = False) -> Optional[Dict[str, Any]]:
    """
    Process all patch files in a single directory
    
    Args:
        directory: Directory path containing patch files
        pattern : Pattern to match patch files
        verbose: Whether to show detailed progress
        
    Returns:
        Dictionary containing processed results, or None if error
    """
    if pattern is None:
        raise ValueError("Pattern must be specified to find patch files.")
    
    design_name = os.path.basename(directory)
    patch_files_pattern = os.path.join(directory, pattern)
    
    patch_files = glob.glob(patch_files_pattern)
    
    if not patch_files:
        if verbose:
            print(f"No patch files found in {directory}")
        return None
    
    # Limit number of files for faster analysis
    max_files = 200000
    if len(patch_files) > max_files:
        random.shuffle(patch_files)
        patch_files = patch_files[:max_files]
    
    if verbose:
        print(f"Processing {len(patch_files)} patch files in {design_name}...")
    
    # Process files with progress bar
    results = []
    file_iterator = (tqdm(patch_files, desc=f"Processing {design_name} patches") 
                    if verbose else patch_files)
    
    for filepath in file_iterator:
        result = process_patch_file(filepath)
        if result:
            results.append(result)
    
    if not results:
        return None
    
    # Create features DataFrame
    features_df = pd.DataFrame([r['features'] for r in results])
    
    # Calculate average layer congestion and wire density
    avg_layer_congestion = np.mean([r['layer_congestion'] for r in results], axis=0)
    avg_layer_wire_density = np.mean([r['layer_wire_density'] for r in results], axis=0)
    
    return {
        'design_name': design_name,
        'df': features_df,
        'avg_layer_congestion': avg_layer_congestion,
        'avg_layer_wire_density': avg_layer_wire_density,
        'file_count': len(results),
        'raw_layer_data': {
            'congestion': [r['layer_congestion'] for r in results],
            'wire_density': [r['layer_wire_density'] for r in results]
        }
    }

# =====================================
# analyzer classes
# =====================================    
class WireDensityAnalyzer(BaseAnalyzer):
    """Analyzer for wire density and congestion analysis"""
    
    def __init__(self):
        super().__init__()
        self.patch_data = {}
        self.design_stats = {}
        self.valid_layers = [2, 4, 6, 8, 10, 12]  # Important layers for analysis
    
    def load(self,
             base_dirs: List[str],
             dir_to_display_name: Optional[Dict[str, str]] = None,
             pattern: Optional[str] = None,
             max_workers: Optional[int] = None,
             verbose: bool = True) -> None:
        """
        Load wire density data from multiple directories
        
        Args:
            base_dirs: List of base directories containing patch data
            dir_to_display_name: Optional mapping from directory names to display names
            pattern : Pattern to match patch files
            max_workers: Maximum number of worker processes (default: min(8, cpu_count()))
            verbose: Whether to show progress information
        """
        self.dir_to_display_name = dir_to_display_name or {}
        
        if max_workers is None:
            max_workers = min(8, os.cpu_count() or 4)
        
        # Process directories in parallel
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_single_directory_for_patches, directory, pattern, verbose) 
                      for directory in base_dirs]
            
            future_iterator = (tqdm(futures, total=len(base_dirs), desc="Processing directories") 
                             if verbose else futures)
            
            for future in future_iterator:
                result = future.result()
                if result:
                    design_name = result['design_name']
                    self.patch_data[design_name] = result
        
        if not self.patch_data:
            raise ValueError("No valid results found from any directory.")
        
        if verbose:
            print(f"Loaded data from {len(self.patch_data)} directories.")
    
    def analyze(self, verbose: bool = True) -> None:
        """
        Analyze loaded wire density data
        
        Args:
            verbose: Whether to show analysis progress
        """
        if not self.patch_data:
            raise ValueError("No data loaded. Please call load() first.")
        
        if verbose:
            print("Analyzing wire density data...")
        
        # Calculate statistics for each design
        for design_name, data in self.patch_data.items():
            stats = {
                'design': design_name,
                'display_name': self.dir_to_display_name.get(design_name, design_name),
                'file_count': data['file_count'],
                'avg_layer_congestion': data['avg_layer_congestion'],
                'avg_layer_wire_density': data['avg_layer_wire_density'],
                'raw_layer_data': data['raw_layer_data']
            }
            
            # Calculate layer-wise statistics
            for layer in self.valid_layers:
                if layer < len(data['avg_layer_congestion']):
                    stats[f'layer_{layer}_congestion'] = data['avg_layer_congestion'][layer]
                    stats[f'layer_{layer}_wire_density'] = data['avg_layer_wire_density'][layer]
                else:
                    stats[f'layer_{layer}_congestion'] = 0.0
                    stats[f'layer_{layer}_wire_density'] = 0.0
            
            self.design_stats[design_name] = stats
        
        if verbose:
            print(f"Analysis completed for {len(self.design_stats)} designs.")
    
    def visualize(self, save_path: Optional[str] = None) -> None:
        """
        Visualize wire density analysis results
        
        Args:
            save_path: Directory to save visualization results
        """
        if not hasattr(self, 'design_stats') or not self.design_stats:
            raise ValueError("No analysis results found. Please call analyze() first.")
        
        # Set output directory
        if save_path is None:
            save_path = "."
        
        # Generate visualizations
        self._create_wire_density_scatter(save_path)
        self._create_layer_comparison_plot(save_path)
    
    def _create_wire_density_scatter(self, save_path: str) -> None:
        """Create scatter plot of congestion vs wire density with regression lines"""
        
        fig, ax = plt.subplots(figsize=(5, 4))
        
        # Get default color cycle
        prop_cycle = plt.rcParams['axes.prop_cycle']
        colors = prop_cycle.by_key()['color']
        
        # Ensure enough colors
        if len(colors) < len(self.valid_layers):
            colors = colors * (len(self.valid_layers) // len(colors) + 1)
        
        # Create layer to color mapping
        layer_color_map = {layer: colors[i % len(colors)] for i, layer in enumerate(self.valid_layers)}
        
        for layer in self.valid_layers:
            x_values = []
            y_values = []
            
            for design_name, stats in self.design_stats.items():
                x = stats.get(f'layer_{layer}_wire_density', 0)
                y = stats.get(f'layer_{layer}_congestion', 0)
                if x != 0 and y != 0:  # Filter out invalid data
                    x_values.append(x)
                    y_values.append(y)
            
            if len(x_values) > 1:  # Ensure enough points for fitting
                color = layer_color_map[layer]
                
                # Scatter plot
                ax.scatter(x_values, y_values, 
                          label=f'Layer {layer}', 
                          alpha=0.7, 
                          color=color,
                          s=50)
                
                # Linear regression
                if len(x_values) > 1:
                    z = np.polyfit(x_values, y_values, 1)
                    p = np.poly1d(z)
                    
                    # Calculate R² value
                    y_pred = p(x_values)
                    ss_total = np.sum((y_values - np.mean(y_values))**2)
                    ss_residual = np.sum((y_values - y_pred)**2)
                    r_squared = 1 - (ss_residual / ss_total) if ss_total != 0 else 0
                    
                    # Plot regression line
                    x_range = np.linspace(min(x_values), max(x_values), 100)
                    ax.plot(x_range, p(x_range), 
                           '--', 
                           color=color,
                           linewidth=2)
        
        # Set labels and formatting
        ax.set_xlabel('Wire Density', fontsize=12)
        ax.set_ylabel('EGR Congestion', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right', ncol=1, fontsize=10)
        
        plt.tight_layout()
        
        output_path = os.path.join(save_path, 'congestion_wire_density_regression.png')
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
        
        print(f"Wire density scatter plot saved to {output_path}")
    
    def _create_layer_comparison_plot(self, save_path: str) -> None:
        """Create comparison plot of different layers"""
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        
        # Prepare data for plotting
        designs = list(self.design_stats.keys())
        display_names = [self.design_stats[d]['display_name'] for d in designs]
        
        # Plot 1: Average congestion by layer
        congestion_data = []
        for layer in self.valid_layers:
            layer_values = [self.design_stats[d].get(f'layer_{layer}_congestion', 0) for d in designs]
            congestion_data.append(layer_values)
        
        positions = np.arange(len(designs))
        width = 0.12
        
        for i, layer in enumerate(self.valid_layers):
            offset = (i - len(self.valid_layers)/2) * width
            ax1.bar(positions + offset, congestion_data[i], width, 
                   label=f'Layer {layer}', alpha=0.8)
        
        ax1.set_xlabel('Design')
        ax1.set_ylabel('Average Congestion')
        ax1.set_title('Congestion by Layer')
        ax1.set_xticks(positions)
        ax1.set_xticklabels(display_names, rotation=45, ha='right')
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax1.grid(axis='y', alpha=0.3)
        
        # Plot 2: Average wire density by layer
        wire_density_data = []
        for layer in self.valid_layers:
            layer_values = [self.design_stats[d].get(f'layer_{layer}_wire_density', 0) for d in designs]
            wire_density_data.append(layer_values)
        
        for i, layer in enumerate(self.valid_layers):
            offset = (i - len(self.valid_layers)/2) * width
            ax2.bar(positions + offset, wire_density_data[i], width, 
                   label=f'Layer {layer}', alpha=0.8)
        
        ax2.set_xlabel('Design')
        ax2.set_ylabel('Average Wire Density')
        ax2.set_title('Wire Density by Layer')
        ax2.set_xticks(positions)
        ax2.set_xticklabels(display_names, rotation=45, ha='right')
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax2.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        output_path = os.path.join(save_path, 'layer_comparison.png')
        plt.savefig(output_path, bbox_inches='tight')
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
            'CellDensity', 'PinDensity', 'NetDensity', 'RUDY', 
            'Congestion', 'Timing', 'Power', 'IRDrop'
        ]
    
    def load(self,
             base_dirs: List[str],
             dir_to_display_name: Optional[Dict[str, str]] = None,
             pattern : Optional[str] = None,
             max_workers: Optional[int] = None,
             verbose: bool = True) -> None:
        """
        Load patch feature data from multiple directories
        
        Args:
            base_dirs: List of base directories containing patch data
            dir_to_display_name: Optional mapping from directory names to display names
            pattern : Pattern to match patch files
            max_workers: Maximum number of worker processes (default: min(8, cpu_count()))
            verbose: Whether to show progress information
        """
        self.dir_to_display_name = dir_to_display_name or {}
        
        if max_workers is None:
            max_workers = min(8, os.cpu_count() or 4)
        
        # Process directories in parallel
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_single_directory_for_patches, directory, pattern, verbose) 
                      for directory in base_dirs]
            
            future_iterator = (tqdm(futures, total=len(base_dirs), desc="Processing directories") 
                             if verbose else futures)
            
            for future in future_iterator:
                result = future.result()
                if result:
                    design_name = result['design_name']
                    self.patch_data[design_name] = result
        
        if not self.patch_data:
            raise ValueError("No valid results found from any directory.")
        
        if verbose:
            print(f"Loaded feature data from {len(self.patch_data)} directories.")
    
    def analyze(self, verbose: bool = True) -> None:
        """
        Analyze feature correlations
        
        Args:
            verbose: Whether to show analysis progress
        """
        if not self.patch_data:
            raise ValueError("No data loaded. Please call load() first.")
        
        if verbose:
            print("Analyzing feature correlations...")
        
        # Combine all design data
        all_dfs = []
        for design_name, data in self.patch_data.items():
            df = data['df'].copy()
            df['design_name'] = design_name
            all_dfs.append(df)
        
        combined_df = pd.concat(all_dfs, ignore_index=True)
        
        # Calculate correlation matrix
        self.correlation_matrix = combined_df[self.correlation_features].corr()
        
        # Calculate feature statistics for each design
        for design_name, data in self.patch_data.items():
            df = data['df']
            
            stats = {
                'design': design_name,
                'display_name': self.dir_to_display_name.get(design_name, design_name),
                'file_count': data['file_count']
            }
            
            # Calculate statistics for each feature
            for feature in self.correlation_features:
                if feature in df.columns:
                    stats[f'{feature}_mean'] = df[feature].mean()
                    stats[f'{feature}_std'] = df[feature].std()
                    stats[f'{feature}_median'] = df[feature].median()
                    stats[f'{feature}_min'] = df[feature].min()
                    stats[f'{feature}_max'] = df[feature].max()
                else:
                    for suffix in ['_mean', '_std', '_median', '_min', '_max']:
                        stats[f'{feature}{suffix}'] = 0.0
            
            self.feature_stats[design_name] = stats
        
        if verbose:
            print(f"Correlation analysis completed for {len(self.feature_stats)} designs.")
    
    def visualize(self, save_path: Optional[str] = None) -> None:
        """
        Visualize feature correlation analysis results
        
        Args:
            save_path: Directory to save visualization results
        """
        if not hasattr(self, 'correlation_matrix') or self.correlation_matrix is None:
            raise ValueError("No analysis results found. Please call analyze() first.")
        
        # Set output directory
        if save_path is None:
            save_path = "."
        
        # Generate visualizations
        self._create_correlation_heatmap(save_path)
        self._create_feature_distribution_plot(save_path)
    
    def _create_correlation_heatmap(self, save_path: str) -> None:
        """Create feature correlation heatmap"""
        
        plt.figure(figsize=(5, 4))
        
        # Create heatmap with optimized font and layout
        heatmap = sns.heatmap(
            self.correlation_matrix, 
            annot=True,                # Show values
            cmap='coolwarm',           # Use cool-warm color scheme
            fmt='.2f',                 # Keep two decimal places
            linewidths=0.3,            # Grid line width
            annot_kws={"size": 10},    # Annotation font size
        )
        
        # Adjust axis labels font size and rotation
        plt.xticks(rotation=30, fontsize=10)
        plt.yticks(rotation=30, fontsize=10)
        
        # Adjust layout to avoid label truncation
        plt.tight_layout(pad=1.1)
        
        # Save plots
        output_path = os.path.join(save_path, 'patch_feature_correlation.png')
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
            display_names = [self.feature_stats[d]['display_name'] for d in designs]
            feature_means = [self.feature_stats[d].get(f'{feature}_mean', 0) for d in designs]
            feature_stds = [self.feature_stats[d].get(f'{feature}_std', 0) for d in designs]
            
            # Create bar plot with error bars
            bars = ax.bar(display_names, feature_means, yerr=feature_stds, 
                         capsize=3, alpha=0.7, color=f'C{i}')
            
            ax.set_title(f'{feature}')
            ax.set_ylabel('Value')
            ax.tick_params(axis='x', rotation=45)
            ax.grid(axis='y', alpha=0.3)
            
            # Format y-axis for better readability
            if max(feature_means) > 1000:
                ax.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
        
        plt.tight_layout()
        
        output_path = os.path.join(save_path, 'feature_distributions.png')
        plt.savefig(output_path, bbox_inches='tight')
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
        self.features = ['Cell Density', 'Pin Density', 'Congestion', 
                        'Timing', 'Power', 'IR Drop', 'net density', 'RUDY']
    
    def load(self, base_dirs: List[str], dir_to_display_name: Dict[str, str], pattern : Optional[str]) -> None:
        """
        Load patch data with spatial position information from multiple directories.
        
        Args:
            base_dirs: List of base directory paths
            dir_to_display_name: Mapping from directory names to display names

        """
        print("Loading patch data with spatial positions...")
        
        if pattern is None:
            raise ValueError("Pattern must be specified to find patch files.")
        
        all_patches_data = []
        
        for base_dir in base_dirs:
            if not os.path.exists(base_dir):
                print(f"Warning: Directory {base_dir} does not exist, skipping...")
                continue
            
            # Find patch files in the directory
            patch_files_pattern = os.path.join(base_dir, pattern)
            patch_files = glob.glob(patch_files_pattern)
            
            if not patch_files:
                print(f"No patch files found in {base_dir}")
                continue
            
            print(f"Processing {len(patch_files)} patch files in {base_dir}...")
            
            # Process files in parallel
            with ProcessPoolExecutor(max_workers=min(8, cpu_count())) as executor:
                results = list(tqdm(executor.map(process_patch_file_with_position, patch_files), 
                                   total=len(patch_files), 
                                   desc=f"Loading {os.path.basename(base_dir)}"))
                valid_results = [r for r in results if r is not None]

                # Add design name to each patch
                design_name = dir_to_display_name.get(os.path.basename(base_dir), os.path.basename(base_dir))
                for patch in valid_results:
                    patch['design'] = design_name
                
                all_patches_data.extend(valid_results)
                        
        if not all_patches_data:
            raise ValueError("No valid patch data found in any directory")
        
        # Convert to DataFrame
        self.data = pd.DataFrame(all_patches_data)
        print(f"Loaded {len(self.data)} patches from {len(base_dirs)} designs")
        
    
    def analyze(self) -> None:
        """
        Analyze the spatial distribution of features across designs.
        """
        print("Analyzing spatial feature distributions...")
        
        
        # Analyze each design separately
        for design in self.data['design'].unique():
            design_data = self.data[self.data['design'] == design]
            
            # Determine layout dimensions
            max_row = design_data['row_id'].max()
            max_col = design_data['col_id'].max()
            layout_dims = (max_row + 1, max_col + 1)
            
            print(f"Design {design}: {layout_dims[0]} rows x {layout_dims[1]} columns")
            
            # Create layout arrays for each feature
            design_layouts = {}
            for feature in self.features:
                layout = np.zeros(layout_dims)
                
                # Fill layout with feature values
                for _, patch in design_data.iterrows():
                    row = int(patch['row_id'])
                    col = int(patch['col_id'])
                    layout[row, col] = patch[feature]
                
                design_layouts[feature] = layout
            
            # Calculate spatial statistics
            spatial_stats = {}
            for feature in self.features:
                layout = design_layouts[feature]
                spatial_stats[feature] = {
                    'mean': np.mean(layout),
                    'std': np.std(layout),
                    'min': np.min(layout),
                    'max': np.max(layout),
                    'hotspot_ratio': np.sum(layout > np.percentile(layout, 90)) / layout.size,
                    'spatial_variance': np.var(layout)
                }
            
            self.analysis_results[design] = {
                'layouts': design_layouts,
                'dimensions': layout_dims,
                'spatial_stats': spatial_stats
            }
        
        print("Spatial analysis completed")
    
    def visualize(self, save_path: Optional[str] = None) -> None:
        """
        Create comprehensive visualizations of spatial feature distributions.
        """
        print("Creating spatial distribution visualizations...")
                
        # Use consistent colormap
        unified_cmap = 'viridis'
        
        # 1. Create individual feature maps for each design
        self._create_individual_feature_maps(save_path, unified_cmap)
        
        # 2. Create combined feature comparison
        self._create_feature_comparison_grid(save_path, unified_cmap)
    
        print(f"Visualizations saved to {save_path}/")
    
    def _create_individual_feature_maps(self, save_path: str, cmap: str) -> None:
        """Create individual heatmaps for each feature and design."""
        for design, results in self.analysis_results.items():
            design_dir = os.path.join(save_path, f"{design}_individual_maps")
            os.makedirs(design_dir, exist_ok=True)
            
            layouts = results['layouts']
            
            for feature in self.features:
                plt.figure(figsize=(8, 6))
                layout_data = layouts[feature]
                
                # Create heatmap
                im = plt.imshow(layout_data, cmap=cmap, aspect='equal', 
                               interpolation='none', origin='lower')
                
                # Add colorbar with proper formatting
                divider = make_axes_locatable(plt.gca())
                cax = divider.append_axes("right", size="5%", pad=0.1)
                cbar = plt.colorbar(im, cax=cax)
                
                # Format colorbar for specific features
                if feature == 'Power':
                    formatter = ticker.ScalarFormatter(useMathText=True)
                    formatter.set_scientific(True)
                    formatter.set_powerlimits((-4, 4))
                    cbar.ax.yaxis.set_major_formatter(formatter)
                elif feature == 'RUDY':
                    formatter = ticker.ScalarFormatter(useMathText=True)
                    formatter.set_scientific(True)
                    formatter.set_powerlimits((0, 0))
                    cbar.ax.yaxis.set_major_formatter(formatter)
                
                cbar.ax.tick_params(labelsize=10)
                
                plt.title(f'{feature} Distribution', fontsize=14, pad=20)

           
                # Add grid for better readability
                plt.grid(True, alpha=0.3, linewidth=0.5)
                
                plt.tight_layout()
                plt.savefig(os.path.join(design_dir, f'{feature.replace(" ", "_")}_layout.png'))
                plt.close()
    
    def _create_feature_comparison_grid(self, save_path: str, cmap: str) -> None:
        """Create a grid comparison of all features for each design."""
        for design, results in self.analysis_results.items():
            layouts = results['layouts']
            
            # Create subplot grid
            fig, axes = plt.subplots(2, 4, figsize=(16, 8))
            fig.suptitle(f'{design} - Feature Distribution Overview', fontsize=16, y=0.95)
            
            axes = axes.flatten()
            
            for idx, feature in enumerate(self.features):
                ax = axes[idx]
                layout_data = layouts[feature]
                
                im = ax.imshow(layout_data, cmap=cmap, aspect='equal', 
                              interpolation='none', origin='lower')
                
                # Add colorbar
                divider = make_axes_locatable(ax)
                cax = divider.append_axes("right", size="5%", pad=0.05)
                cbar = plt.colorbar(im, cax=cax)
                cbar.ax.tick_params(labelsize=8)
                
                # Format specific features
                if feature == 'Power':
                    formatter = ticker.ScalarFormatter(useMathText=True)
                    formatter.set_scientific(True)
                    formatter.set_powerlimits((-4, 4))
                    cbar.ax.yaxis.set_major_formatter(formatter)
                elif feature == 'RUDY':
                    formatter = ticker.ScalarFormatter(useMathText=True)
                    formatter.set_scientific(True)
                    formatter.set_powerlimits((0, 0))
                    cbar.ax.yaxis.set_major_formatter(formatter)
                
                ax.set_title(feature, fontsize=12)
                ax.set_xticks([])
                ax.set_yticks([])
            
            plt.tight_layout()
            plt.savefig(os.path.join(save_path, f'{design}_feature_grid.png'))
            plt.close()
    
