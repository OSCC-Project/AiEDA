#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : design.py
@Author : yhqiu
@Desc : design level data ananlysis, including cell type distribution, core usage, and pin distribution
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

from .base import BaseAnalyzer


class CellTypeAnalyzer(BaseAnalyzer):
    """Analyzer for cell type distribution across designs."""
    
    def __init__(self):
        super().__init__()
        self.inst_count = {}
    
    def load(self, 
            base_dirs: List[Union[str, Path]], 
            dir_to_display_name: Optional[Dict[str, str]] = None,
            verbose: bool = True):
        """
        Load data from multiple directories.
        
        Args:
            base_dirs: List of base directories to process
            dir_to_display_name: Optional mapping from directory name to display name
            verbose: Whether to print progress information
        """        
        for base_dir in base_dirs:
            design_name = os.path.basename(base_dir)
            display_name = dir_to_display_name.get(design_name, design_name) 
            
            pattern = "workspace/output/innovus/feature/*route_summary.json"
            json_path = os.path.join(base_dir, pattern)
            
            matching_files = glob.glob(json_path)
            
            if not matching_files:
                self.missing_files.append(display_name)
                continue
                
            json_file = matching_files[0]
            
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    
                if "Instances" in data:
                    counts = {}
                    for inst_type in ["clock", "logic", "macros", "iopads"]:
                        if inst_type in data["Instances"]:
                            counts[inst_type] = data["Instances"][inst_type]["num"]
                        else:
                            counts[inst_type] = 0
                    
                    counts["total"] = sum(counts.values())
                    self.inst_count[display_name] = counts
                else:
                    self.missing_files.append(f"{display_name} (No Instances field)")
                    
            except Exception as e:
                self.missing_files.append(f"{display_name} (Error: {str(e)})")
            
    def analyze(self):
        """Analyze cell type distribution across designs."""
        
        if not self.inst_count:
            print("No instance data found")
            return       
        
        df = pd.DataFrame.from_dict(self.inst_count, orient='index')
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
    
    def visualize(self, 
                  save_path: Optional[str] = None):
        """Create visualizations for cell type distribution."""
        if not self.inst_count:
            print("No instance data found")
            return       
        
        df = pd.DataFrame.from_dict(self.inst_count, orient='index')
        if "total" not in df.columns:
            df["total"] = df[["clock", "logic", "macros", "iopads"]].sum(axis=1)
            
        df_sorted = df.sort_values(by="total", ascending=False)
        
        # 1. Create heatmap for top 20 designs
        plt.figure(figsize=(5,4))
        
        top20_designs = df_sorted.index[:10]
        
        df_display = df_sorted.loc[top20_designs, ["clock", "logic", "macros", "iopads"]].copy()
        
        ax = sns.heatmap(df_display, 
                    annot=True, 
                    fmt='', 
                    cmap='YlGnBu', 
                    linewidths=0.5,
                    annot_kws={"size": 10},
                    cbar_kws={'label': 'Instance Count'})
        
        for i in range(len(df_display.index)):
            for j in range(len(df_display.columns)):
                text = ax.texts[i * len(df_display.columns) + j]
                text.set_text(self._custom_format(df_display.iloc[i, j]))
        
        plt.setp(ax.get_yticklabels(), style='italic')
        
        plt.xlabel('Instance Type', fontsize=12)
        plt.ylabel('Design', fontsize=12)
        plt.tight_layout()
        
        plt.savefig(save_path + 'instance_count_top20.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. create heatmap for bottom 20 designs
        plt.figure(figsize=(5,4))
        
        bottom20_designs = df_sorted.index[-10:]
        
        df_display = df_sorted.loc[bottom20_designs, ["clock", "logic", "macros", "iopads"]].copy()
        
        ax = sns.heatmap(df_display, 
                    annot=True, 
                    fmt='', 
                    cmap='YlGnBu', 
                    linewidths=0.5,
                    annot_kws={"size": 10},
                    cbar_kws={'label': 'Instance Count'})
        
        for i in range(len(df_display.index)):
            for j in range(len(df_display.columns)):
                text = ax.texts[i * len(df_display.columns) + j]
                text.set_text(self._custom_format(df_display.iloc[i, j]))
        
        plt.setp(ax.get_yticklabels(), style='italic')
        
        plt.xlabel('Instance Type', fontsize=12)
        plt.ylabel('Design', fontsize=12)
        plt.tight_layout()
        
        plt.savefig(save_path + 'instance_count_bottom20.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Saved instance count heatmaps:")
        print("- 'instance_count_top20.png' (Top 20 designs)")
        print("- 'instance_count_bottom20.png' (Bottom 20 designs)")
        
    def _custom_format(val):
        if val == 0:
            return '0'
        else:
            return '{:.1e}'.format(val)    
        
        
class CoreUsageAnalyzer(BaseAnalyzer):
    """Analyzer for core usage statistics."""
    
    def __init__(self):
        super().__init__()
        self.core_usage = {}
    
    def load(self, 
            base_dirs: List[Union[str, Path]], 
            verbose: bool = True):
        """
        Load data from multiple directories.
        
        Args:
            base_dirs: List of base directories to process
            verbose: Whether to print progress information
        """        
        for base_dir in base_dirs:
            design_name = os.path.basename(base_dir)
            
            pattern = "workspace/output/innovus/feature/*route_summary.json"
            json_path = os.path.join(base_dir, pattern)
            
            matching_files = glob.glob(json_path)
            
            if not matching_files:
                self.missing_files.append(display_name)
                continue
                
            json_file = matching_files[0]
            
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    
                # Extract core_usage value
                if "Design Layout" in data and "core_usage" in data["Design Layout"]:
                    core_usage = data["Design Layout"]["core_usage"]
                    self.core_usage[design_name] = core_usage
                else:
                    self.missing_files.append(f"{design_name} (No core_usage field)")
                    
            except Exception as e:
                self.missing_files.append(f"{design_name} (Error: {str(e)})")
            
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
        
        
    def visualize(self, 
                  save_path: Optional[str] = None):
        """Create visualizations for cell usage distribution."""
        if not self.core_usage:
            print("No core usage data found")
            return       
            
        usages = list(self.core_usage.values())
        
        from matplotlib.ticker import MultipleLocator
        
        plt.figure(figsize=(5, 4))
        plt.hist(usages, bins=10, color='lightgreen', edgecolor='black')
        plt.xlabel('core usage', fontsize=14)
        plt.ylabel('Number of Designs', fontsize=14)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.gca().xaxis.set_major_locator(MultipleLocator(0.1))  
        
        plt.tight_layout()
        plt.savefig(save_path + 'core_usage_hist.png', bbox_inches='tight') 
        plt.close()
        
        print("Charts saved as separate files:")
        print("- 'core_usage_hist.png' (Histogram)")


class PinDistributionAnalyzer(BaseAnalyzer):
    """Analyzer for pin distribution in designs."""
    
    def __init__(self):
        super().__init__()
        self.pin_dist = {}
    
    def load(self, 
            base_dirs: List[Union[str, Path]], 
            verbose: bool = True):
        """
        Load data from multiple directories.
        
        Args:
            base_dirs: List of base directories to process
            verbose: Whether to print progress information

        """        
        
        for base_dir in base_dirs:
            design_name = os.path.basename(base_dir)
            
            pattern = "workspace/output/innovus/feature/*route_summary.json"
            json_path = os.path.join(base_dir, pattern)
            
            matching_files = glob.glob(json_path)
            
            if not matching_files:
                self.missing_files.append(display_name)
                continue
                
            json_file = matching_files[0]
            
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    
                if "Pins" in data and "pin_distribution" in data["Pins"]:
                    pin_data = []
                    for item in data["Pins"]["pin_distribution"]:
                        if "pin_num" in item and "net_num" in item and "net_ratio" in item:
                            pin_num = self._parse_pin_num(item["pin_num"])
                            
                            try:
                                net_num = int(item["net_num"]) if isinstance(item["net_num"], (int, float, str)) else 0
                            except ValueError:
                                print(f"Warning: Could not parse net_num '{item['net_num']}', using 0 as default")
                                net_num = 0
                                
                            try:
                                net_ratio = float(item["net_ratio"]) if isinstance(item["net_ratio"], (int, float, str)) else 0.0
                            except ValueError:
                                print(f"Warning: Could not parse net_ratio '{item['net_ratio']}', using 0.0 as default")
                                net_ratio = 0.0
                            
                            pin_data.append({
                                "pin_num": pin_num,
                                "net_num": net_num,
                                "net_ratio": net_ratio,
                                "original_pin_num": item["pin_num"]  
                            })
                    
                    pin_data.sort(key=lambda x: x["pin_num"])
                    self.pin_dist[design_name] = pin_data
                else:
                    self.missing_files.append(f"{design_name} (No pin_distribution field)")
                    
            except Exception as e:
                self.missing_files.append(f"{design_name} (Error: {str(e)})")
            
    def analyze(self):
        """Analyze pin number distribution across designs."""
        
        if not self.pin_dist:
            print("No pin dist data found")
            return     
          
        all_data = []
        for design_name, pin_data in self.pin_dist.items():
            for item in pin_data:
                all_data.append({
                    "design": design_name,
                    "pin_num": item["pin_num"],
                    "net_num": item["net_num"],
                    "net_ratio": item["net_ratio"],
                    "original_pin_num": item.get("original_pin_num", str(item["pin_num"]))
                })
        
        df = pd.DataFrame(all_data)
        
        df_summary = df.groupby("pin_num").agg({
            "net_num": ["mean", "min", "max", "std"],
            "net_ratio": ["mean", "min", "max", "std"]
        }).reset_index()
        print("\nStatistical Summary by Pin Count:")
        print(df_summary.to_string())
        
    
    def visualize(self, 
                  save_path: Optional[str] = None):
        """Create visualizations for pin distribution."""
        if not self.pin_dist:
            print("No pin_dist data found")
            return       
        
        all_data = []
        for design_name, pin_data in self.pin_dist.items():
            for item in pin_data:
                all_data.append({
                    "design": design_name,
                    "pin_num": item["pin_num"],
                    "net_num": item["net_num"],
                    "net_ratio": item["net_ratio"],
                    "original_pin_num": item.get("original_pin_num", str(item["pin_num"]))
                })
        
        df = pd.DataFrame(all_data)
        
        df_summary = df.groupby("pin_num").agg({
            "net_num": ["mean", "min", "max", "std"],
            "net_ratio": ["mean", "min", "max", "std"]
        }).reset_index()
        
        
        plt.figure(figsize=(5, 4))
        plt.plot(df_summary["pin_num"], df_summary[("net_ratio", "mean")], 
                marker='o', markersize=5, linestyle='-', color='blue', linewidth=1.5, label="Mean")
        plt.fill_between(df_summary["pin_num"], 
                        df_summary[("net_ratio", "mean")] - df_summary[("net_ratio", "std")],
                        df_summary[("net_ratio", "mean")] + df_summary[("net_ratio", "std")],
                        alpha=0.2, color='blue', label="±1 Std Dev")
        plt.plot(df_summary["pin_num"], df_summary[("net_ratio", "min")], 
                marker='^', markersize=4, linestyle='--', color='green', linewidth=1.0, label="Min")
        plt.plot(df_summary["pin_num"], df_summary[("net_ratio", "max")], 
                marker='v', markersize=4, linestyle='--', color='red', linewidth=1.0, label="Max")
        
        plt.xlabel("Pin Count", fontsize=14)
        plt.ylabel("Net Ratio", fontsize=14)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(loc='upper right', frameon=True)
        
        plt.tick_params(axis='both', which='major', direction='out', length=4, width=1)
        
        plt.tight_layout()
        plt.savefig(save_path + 'pin_vs_net_ratio.png', bbox_inches='tight')
        print("Saved pin_vs_net_ratio.png")
        plt.close()  
        
    def _parse_pin_num(pin_num_str):
        if isinstance(pin_num_str, (int, float)):
            return int(pin_num_str)
        
        pin_num_str = str(pin_num_str).strip()
        
        if pin_num_str.startswith('>'):
            num_part = pin_num_str.replace('>', '').strip()
            try:
                return int(num_part) + 1
            except ValueError:
                print(f"Warning: Could not parse pin_num '{pin_num_str}', using 999 as default")
                return 999
        
        elif pin_num_str.startswith('<'):
            num_part = pin_num_str.replace('<', '').strip()
            try:
                return int(num_part) - 1
            except ValueError:
                print(f"Warning: Could not parse pin_num '{pin_num_str}', using 0 as default")
                return 0
        
        elif '-' in pin_num_str and not pin_num_str.startswith('-'):
            try:
                start, end = pin_num_str.split('-', 1)
                return (int(start.strip()) + int(end.strip())) // 2
            except ValueError:
                print(f"Warning: Could not parse pin_num range '{pin_num_str}', using 500 as default")
                return 500
        
        try:
            return int(pin_num_str)
        except ValueError:
            print(f"Error: Failed to parse pin_num '{pin_num_str}', using -1 as default")
            return -1
                
