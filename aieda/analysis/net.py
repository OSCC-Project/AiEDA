#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : net.py
@Author : yhqiu
@Desc : net level data ananlysis, including wirelength distribution and metrics correlation
'''
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

# =====================================
# tool functions
# =====================================
def process_single_file(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Process a single net JSON file.
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        Dictionary containing extracted features or None if error
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        # Calculate HPWL
        llx = data['feature']['llx']
        lly = data['feature']['lly']
        urx = data['feature']['urx']
        ury = data['feature']['ury']
        hpwl = (urx - llx) + (ury - lly)
        
        # Get actual routed wirelength
        rwl = data['feature']['wire_len']
        
        # Get other features
        r_value = data['feature']['R']
        c_value = data['feature']['C']
        power = data['feature']['power']
        delay = data['feature']['delay']
        slew = data['feature']['slew']
        
        # Calculate wirelength per layer
        layer_lengths = [0] * 20  # Assume maximum 20 layers
        total_wire_length = 0
        
        for wire in data['wires']:
            if ('wire' in wire and 
                all(key in wire['wire'] for key in ['x1', 'y1', 'x2', 'y2', 'l1', 'l2'])):
                
                x1 = wire['wire']['x1']
                y1 = wire['wire']['y1']
                x2 = wire['wire']['x2']
                y2 = wire['wire']['y2']
                l1 = wire['wire']['l1']
                l2 = wire['wire']['l2']
                
                # Only consider wires on the same layer
                if l1 == l2 and l1 < 20:
                    wire_length = abs(x2 - x1) + abs(y2 - y1)
                    layer_lengths[l1] += wire_length
                    total_wire_length += wire_length
        
        # Calculate layer wire length ratios
        layer_ratios = [0] * 20
        if total_wire_length > 0:
            layer_ratios = [length / total_wire_length for length in layer_lengths]
        
        return {
            'hpwl': hpwl,
            'rwl': rwl,
            'R': r_value,
            'C': c_value,
            'power': power,
            'delay': delay,
            'slew': slew,
            'layer_lengths': layer_lengths,
            'layer_ratios': layer_ratios
        }
        
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return None
    
    
def process_single_directory(directory: str, pattern: str, verbose : bool) -> Optional[Dict[str, Any]]:
    """
    Process all net files in a single directory.
    
    Args:
        directory: Path to the directory containing net files
        pattern: File pattern to match net files
        verbose : Whether to show progress information
        
    Returns:
        Dictionary containing processed data for the directory
    """
    if pattern is None:
        raise ValueError("Pattern must be specified to find net files.")
    
    net_files_pattern = os.path.join(directory, pattern)
    net_files = glob.glob(net_files_pattern)
    
    if not net_files:
        print(f"No net files found in {directory}")
        return None
    
    print(f"Processing {len(net_files)} files in {os.path.basename(directory)}...")
    
    # Process files with progress bar
    results = []
    file_iterator = (tqdm(net_files, desc=f"Processing {os.path.basename(directory)}") 
                    if verbose else net_files)
    
    for filepath in file_iterator:
        result = process_single_file(filepath)
        if result:
            results.append(result)
    
    if not results:
        return None
    
    # Create DataFrame for this directory
    df = pd.DataFrame({
        'hpwl': [r['hpwl'] for r in results],
        'rwl': [r['rwl'] for r in results],
        'R': [r['R'] for r in results],
        'C': [r['C'] for r in results],
        'power': [r['power'] for r in results],
        'delay': [r['delay'] for r in results],
        'slew': [r['slew'] for r in results]
    })
        
    # Calculate total layer lengths and proportions
    total_layer_lengths = np.zeros(20)
    for r in results:
        total_layer_lengths += np.array(r['layer_lengths'])
    
    total_length = np.sum(total_layer_lengths)
    layer_proportions = (total_layer_lengths / total_length 
                        if total_length > 0 else np.zeros(20))
    
    return {
        'df': df,
        'design_name': os.path.basename(directory),
        'layer_lengths': total_layer_lengths,
        'layer_proportions': layer_proportions
    }
        

# =====================================
# analyzer classes
# =====================================
class WireDistributionAnalyzer(BaseAnalyzer):
    """Analyzer for wirelength distribution."""
    
    def __init__(self):
        super().__init__()
        self.net_data = []
    
    def load(self,
             base_dirs: List[str],
             dir_to_display_name: Optional[Dict[str, str]] = None,
             pattern: Optional[str] = None,
             max_workers: Optional[int] = None,
             verbose: bool = True) -> None:
        """
        Load net data from multiple directories.
        
        Args:
            base_dirs: List of base directories containing net data
            dir_to_display_name: Optional mapping from directory names to display names
            pattern: File pattern to search for
            max_workers: Maximum number of worker processes (default: min(8, cpu_count()))
            verbose: Whether to show progress information
        """        
        self.dir_to_display_name = dir_to_display_name or {}
        
        if max_workers is None:
            max_workers = min(8, cpu_count())
                
        # Process directories in parallel
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_single_directory, directory, pattern, verbose) 
                      for directory in base_dirs]
            
            future_iterator = (tqdm(futures, total=len(base_dirs), desc="Processing directories") 
                             if verbose else futures)
            
            for future in future_iterator:
                result = future.result()
                if result:
                    self.net_data.append(result)
        
        if not self.net_data:
            raise ValueError("No valid results found from any directory.")
        
        if verbose:
            print(f"Loaded data from {len(self.net_data)} directories.")
        
    def analyze(self, verbose: bool = True) -> None:
        """
        Analyze the loaded net data.
        
        Args:
            verbose: Whether to show analysis progress
        """
        if not self.net_data:
            raise ValueError("No data loaded. Please call load() first.")
                
        if verbose:
            print("Analyzing net features...")
        
                    
    def visualize(self, 
                  save_path: Optional[str] = None) -> None:
        """
        Visualize the net data.
        
        Args:
            save_path: Directory to save the visualizations
        """

        # Set up output directory
        if save_path is None:
            save_path = "."
        
        # Generate stacked bar chart for layer wire length proportions
        plt.figure(figsize=(5, 4))
        
        # Get design names with custom display names
        design_names = []
        for result in self.net_data:
            base_name = result['design_name']
            display_name = self.dir_to_display_name.get(base_name, base_name)
            design_names.append(display_name)
        
        layer_data = np.array([r['layer_proportions'] for r in self.net_data])
        
        # Show only even layers (actual chip layers)
        layers_to_show = [0, 2, 4, 6, 8, 10, 12]
        
        # Create stacked bar chart
        bottom = np.zeros(len(self.net_data))
        for i in layers_to_show:
            if i < 20:  # Ensure layer index is within range
                layer_props = layer_data[:, i]
                if np.sum(layer_props) > 0:  # Only plot layers with data
                    plt.bar(design_names, layer_props, bottom=bottom, label=f'Layer {i}')
                    bottom += layer_props
        
        plt.ylabel('Proportion of Wirelength')
        
        # Set x-axis labels to italic
        ax = plt.gca()
        for tick in ax.get_xticklabels():
            tick.set_style('italic')
        
        plt.legend(loc='upper right')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save plot
        output_path = os.path.join(save_path, 'wire_length_distribution.png')
        plt.savefig(output_path)
        plt.close()
        
        print(f"Layer distribution plot saved to {output_path}")
        


class MetricsCorrelationAnalyzer(BaseAnalyzer):
    """Analyzer for net features and statistics."""
    
    def __init__(self):
        super().__init__()
        self.net_data = []
        self.combined_df = None
    
    def load(self,
             base_dirs: List[str],
             dir_to_display_name: Optional[Dict[str, str]] = None,
             pattern: Optional[str] = None,
             max_workers: Optional[int] = None,
             verbose: bool = True) -> None:
        """
        Load net feature data from multiple directories.
        
        Args:
            base_dirs: List of base directories containing net data
            dir_to_display_name: Optional mapping from directory names to display names
            pattern: File pattern to search for
            max_workers: Maximum number of worker processes (default: min(8, cpu_count()))
            verbose: Whether to show progress information
        """      
        self.dir_to_display_name = dir_to_display_name or {}
  
        if max_workers is None:
            max_workers = min(8, cpu_count())
                
        # Process directories in parallel
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_single_directory, directory, pattern, verbose) 
                      for directory in base_dirs]
            
            future_iterator = (tqdm(futures, total=len(base_dirs), desc="Processing directories") 
                             if verbose else futures)
            
            for future in future_iterator:
                result = future.result()
                if result:
                    self.net_data.append(result)
        
        if not self.net_data:
            raise ValueError("No valid results found from any directory.")
        

        if verbose:
            print(f"Loaded data from {len(self.net_data)} directories.")
        
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
        self.combined_df = pd.concat([r['df'] for r in self.net_data], 
                                   ignore_index=True)
        
        # Calculate summary statistics for each design
        self.design_stats = {}
        for result in self.net_data:
            design_name = result['design_name']
            df = result['df']
            
            stats = {
                'count': len(df),
                'mean_hpwl': df['hpwl'].mean(),
                'mean_rwl': df['rwl'].mean(),
                'mean_R': df['R'].mean(),
                'mean_C': df['C'].mean(),
                'mean_power': df['power'].mean(),
                'mean_delay': df['delay'].mean(),
                'mean_slew': df['slew'].mean(),
                'layer_proportions': result['layer_proportions']
            }
            self.design_stats[design_name] = stats
        
        if verbose:
            print(f"Analysis completed for {len(self.design_stats)} designs.")
            print(f"Total nets analyzed: {len(self.combined_df)}")
                    
    def visualize(self, 
                  save_path: Optional[str] = None) -> None:
        """
        Visualize the net features and statistics.
        
        Args:
            save_path: Directory to save the visualizations
        """
        if not hasattr(self, 'combined_df') or self.combined_df is None:
            raise ValueError("No analysis results found. Please call analyze() first.")
        
        # Set up output directory
        if save_path is None:
            save_path = "."
            
        plt.figure(figsize=(5, 4))
        
        # Calculate correlation matrix
        features = ['rwl', 'hpwl', 'R', 'C', 'power', 'delay', 'slew']
        corr_matrix = self.combined_df[features].corr()
        
        # Create heatmap
        sns.heatmap(corr_matrix, annot=True, cmap='YlGnBu', fmt='.2f', linewidths=0.5)
        plt.tight_layout()
        
        # Save plot
        output_path = os.path.join(save_path, 'correlation_matrix.png')
        plt.savefig(output_path)
        plt.close()
        
        print(f"Correlation matrix plot saved to {output_path}")

