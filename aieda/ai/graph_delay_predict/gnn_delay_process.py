import os
import json
import logging
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional, Set
from dataclasses import dataclass
from pathlib import Path
import torch
from torch_geometric.data import Data
from torch_geometric.loader import DataLoader
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class RCNetworkDataConfig:
    """RC network data processing configuration"""
    # Data paths: raw data directories, model input file, visualization file storage directory
    raw_input_dirs: List[str]
    pattern: str = "/output/iEDA/vectors/timing_data"
    model_input_file: str = "./rc_network_dataset.pt"
    plot_dir: str = "./rc_network_analysis_plots"
    
    # Data features: node and edge feature dimensions
    node_feature_dim: int = 9  # Node feature dimension (capacitance nodes)
    edge_feature_dim: int = 8  # Edge feature dimension (resistance connections)
    
    # Data cleaning: delay thresholds, outlier detection, graph size constraints
    min_delay_threshold: float = 1e-12  # Minimum delay threshold (1ps)
    max_delay_threshold: float = 3   # Maximum delay threshold (1ns) 
    min_nodes_per_net: int = 5       # Minimum nodes per network
    min_edges_per_net: int = 4       # Minimum edges per network
    min_paths_per_net: int = 2       # Minimum paths per network
    
    # Critical path identification: delay ratio and maximum paths
    critical_path_delay_ratio: float = 0.8  # Critical path delay threshold ratio
    max_critical_paths: int = 3       # Maximum critical paths per net
    
    # Debug parameters: network construction and delay extraction debugging
    debug_net_construction: bool = True  # Whether to output network construction debug info
    debug_delay_extraction: bool = False  # Whether to output delay extraction debug info
    
    # Design-specific normalization configuration
    use_design_specific_normalization: bool = True  # Whether to use design-specific normalization
    save_normalization_params: bool = True  # Whether to save normalization parameters
    normalization_params_file: str = "./design_normalization_params.json"  # Normalization parameters file
    
    # Data splitting: train, validation, test set ratios
    train_ratio: float = 0.7
    val_ratio: float = 0.15
    test_ratio: float = 0.15
    
    # Data processing: PyTorch Geometric parameters
    batch_size: int = 16  # Reduced batch size due to larger networks
    num_workers: int = 4
    
    # Other parameters
    random_seed: int = 43

class RCNetworkDataProcessor:
    """RC network data processor - aggregates paths with same source node into net"""
    
    def __init__(self, config: RCNetworkDataConfig):
        """
        Initialize RC network data processor
        
        Args:
            config: Data processing configuration
        """
        self.config = config
        self.node_scaler = StandardScaler()
        self.edge_scaler = StandardScaler()
        self.delay_scaler = StandardScaler()
        
        # Design-specific normalization parameters
        self.design_normalization_params = {}  # Store normalization parameters for each design
        
        # Create output directories
        os.makedirs(os.path.dirname(self.config.model_input_file), exist_ok=True)
        os.makedirs(self.config.plot_dir, exist_ok=True)
        
        # Set random seed
        np.random.seed(self.config.random_seed)
    
    def extract_rc_networks(self) -> List[Dict[str, Any]]:
        """
        Extract RC network data from timing files (aggregate by source node)
        
        Returns:
            List[Dict]: RC network data list, each network contains multiple paths
        """
        logger.info("Starting RC network data extraction (aggregated by source node)")
        
        all_networks = []
        total_files = 0
        successful_files = 0
        
        for workspace_dir in self.config.raw_input_dirs:
            design_name = os.path.basename(os.path.dirname(workspace_dir))
            logger.info(f"Processing workspace: {workspace_dir} (design: {design_name})")
            
            # Find timing data files
            possible_patterns = [
                "/output/iEDA/vectors/wire_paths",
                "/output/iEDA/vectors/wire_graph", 
                "/output/iEDA/vectors/timing_data",
                "/output/iEDA/feature/large_model/timing_data",
                "/output/iEDA/timing_data",
                "/timing_data"
            ]
            
            selected_timing_dir = None
            for pattern in possible_patterns:
                test_dir = os.path.join(workspace_dir, pattern.lstrip('/'))
                if os.path.exists(test_dir):
                    selected_timing_dir = test_dir
                    logger.info(f"Selected data source: {test_dir}")
                    break
            
            if not selected_timing_dir:
                logger.warning(f"Design {design_name} found no available timing data directories")
                continue
            
            # Extract all paths for this design
            design_paths = self._extract_design_paths(selected_timing_dir, design_name)
            total_files += len(design_paths)
            
            if design_paths:
                # Aggregate paths by source node into networks
                networks = self._aggregate_paths_to_networks(design_paths, design_name)
                all_networks.extend(networks)
                successful_files += len(networks)
                logger.info(f"✓ Design {design_name}: Created {len(networks)} networks from {len(design_paths)} paths")
        
        logger.info(f"RC network extraction completed - Total paths: {total_files}, Successfully created networks: {len(all_networks)}")
        return all_networks
    
    def _extract_design_paths(self, timing_dir: str, design_name: str) -> List[Dict[str, Any]]:
        """
        Extract all path data for a design
        
        Args:
            timing_dir: Timing data directory
            design_name: Design name
            
        Returns:
            List[Dict]: Path data list
        """
        all_paths = []
        
        if "wire_paths" in timing_dir:
            # Process wire_paths directory
            wire_path_files = []
            for file in os.listdir(timing_dir):
                if file.startswith("wire_path_") and file.endswith(".json"):
                    wire_path_files.append(os.path.join(timing_dir, file))
            
            for wire_path_file in tqdm(wire_path_files, desc=f"Extract {design_name} paths", leave=False):
                try:
                    path_data = self._parse_wire_path_file_for_network(wire_path_file)
                    if path_data:
                        all_paths.append(path_data)
                except Exception as e:
                    logger.error(f"Error processing wire_path file {wire_path_file}: {e}")
                    continue
        
        elif "timing_data" in timing_dir:
            # Process traditional timing_data directory
            timing_files = []
            for root, dirs, files in os.walk(timing_dir):
                for file in files:
                    if file == "timing_paths_data.json":
                        timing_files.append(os.path.join(root, file))
            
            for timing_file in tqdm(timing_files, desc=f"Extract {design_name} paths", leave=False):
                try:
                    paths_from_file = self._parse_timing_file_for_network(timing_file)
                    all_paths.extend(paths_from_file)
                except Exception as e:
                    logger.error(f"Error processing timing file {timing_file}: {e}")
                    continue
        
        logger.info(f"Design {design_name} extracted {len(all_paths)} paths")
        return all_paths
    
    def _aggregate_paths_to_networks(self, paths: List[Dict[str, Any]], design_name: str) -> List[Dict[str, Any]]:
        """
        Aggregate paths by source node into networks (optimized version)
        
        Args:
            paths: Path data list
            design_name: Design name
            
        Returns:
            List[Dict]: Network data list
        """
        logger.info(f"Starting aggregation of design {design_name}'s {len(paths)} paths into RC networks")
        
        # Group paths by source node
        source_groups = defaultdict(list)
        
        for path in paths:
            source_node = path.get('source_node', '')
            if source_node:
                source_groups[source_node].append(path)
            else:
                logger.warning(f"Path missing source node information: {path.get('path_id', 'unknown')}")
        
        networks = []
        total_paths_processed = 0
        
        for source_node, grouped_paths in source_groups.items():
            if len(grouped_paths) >= self.config.min_paths_per_net:
                try:
                    # Validate path data completeness
                    valid_paths = []
                    for path in grouped_paths:
                        if (path.get('nodes') is not None and 
                            path.get('edges') is not None and 
                            path.get('node_delays') is not None and
                            len(path['nodes']) > 0):
                            valid_paths.append(path)
                    
                    if len(valid_paths) >= self.config.min_paths_per_net:
                        network = self._create_network_from_paths(valid_paths, source_node, design_name)
                        if network:
                            networks.append(network)
                            total_paths_processed += len(valid_paths)
                            if self.config.debug_net_construction:
                                logger.info(f"✓ Created RC network {source_node}: {network['num_nodes']} nodes, "
                                          f"{network['num_edges']} edges, {len(valid_paths)} paths")
                    else:
                        logger.debug(f"Source node {source_node} has insufficient valid paths ({len(valid_paths)} < {self.config.min_paths_per_net})")
                except Exception as e:
                    logger.error(f"Error creating RC network for source node {source_node}: {e}")
                    continue
            else:
                logger.debug(f"Source node {source_node} has insufficient paths ({len(grouped_paths)} < {self.config.min_paths_per_net})")
        
        logger.info(f"Design {design_name} created {len(networks)} RC networks, processed {total_paths_processed} paths")
        return networks
    
    def _create_network_from_paths(self, paths: List[Dict[str, Any]], source_node: str, design_name: str) -> Optional[Dict[str, Any]]:
        """
        Create RC network from multiple paths (optimized version)
        
        Args:
            paths: Path data list (same source node)
            source_node: Source node name
            design_name: Design name
            
        Returns:
            Optional[Dict]: Network data dictionary
        """
        # Use simpler node naming strategy to avoid complexity from path indexing
        global_nodes = {}  # node_name -> node_id
        global_node_features = {}  # node_id -> features
        global_node_delays = {}  # node_name -> delay
        global_edges = set()  # (from_id, to_id)
        global_edge_features = []  # edge features list
        
        # Path information
        path_node_sequences = []  # Node sequence for each path
        path_delays = []  # Total delay for each path
        
        # Process each path
        for path_idx, path in enumerate(paths):
            path_nodes = path['nodes']
            path_edges = path['edges']
            path_edge_features = path['edge_features']
            path_node_delays = path['node_delays']
            
            # Record path node sequence (for critical path identification)
            path_sequence = []
            
            # Add nodes in path - use simpler naming
            for i, node_feat in enumerate(path_nodes):
                # Use actual node information from path instead of renaming
                node_name = f"{source_node}_node_{i}"
                
                if node_name not in global_nodes:
                    node_id = len(global_nodes)
                    global_nodes[node_name] = node_id
                    global_node_features[node_id] = node_feat.copy()
                    # Ensure delay value is scalar
                    delay_val = path_node_delays[i] if i < len(path_node_delays) else 0.0
                    if isinstance(delay_val, np.ndarray):
                        delay_val = float(delay_val.item() if delay_val.size == 1 else delay_val.mean())
                    global_node_delays[node_name] = float(delay_val)
                else:
                    # Node already exists, update features and delay (take maximum)
                    node_id = global_nodes[node_name]
                    existing_delay = float(global_node_delays[node_name])
                    new_delay = path_node_delays[i] if i < len(path_node_delays) else 0.0
                    if isinstance(new_delay, np.ndarray):
                        new_delay = float(new_delay.item() if new_delay.size == 1 else new_delay.mean())
                    new_delay = float(new_delay)
                    if new_delay > existing_delay:
                        global_node_delays[node_name] = new_delay
                        global_node_features[node_id][4] = new_delay  # Update delay feature
                
                path_sequence.append(global_nodes[node_name])
            
            # Add edges in path
            for i, edge in enumerate(path_edges):
                from_node_name = f"{source_node}_node_{edge[0]}"
                to_node_name = f"{source_node}_node_{edge[1]}"
                
                if from_node_name in global_nodes and to_node_name in global_nodes:
                    from_id = global_nodes[from_node_name]
                    to_id = global_nodes[to_node_name]
                    edge_tuple = (from_id, to_id)
                    
                    if edge_tuple not in global_edges:
                        global_edges.add(edge_tuple)
                        edge_feat = path_edge_features[i] if i < len(path_edge_features) else [0.0] * self.config.edge_feature_dim
                        global_edge_features.append(edge_feat)
            
            # Record path information
            path_node_sequences.append(path_sequence)
            # Ensure delay value is scalar
            if path_node_delays is not None and len(path_node_delays) > 0:
                if isinstance(path_node_delays, np.ndarray):
                    total_delay = float(np.sum(path_node_delays))
                else:
                    total_delay = float(sum(path_node_delays))
            else:
                total_delay = 0.0
            path_delays.append(total_delay)
        
        # Validate network scale
        if (len(global_nodes) < self.config.min_nodes_per_net or 
            len(global_edges) < self.config.min_edges_per_net):
            return None
        
        # Identify critical paths
        critical_paths = self._identify_critical_paths(path_node_sequences, path_delays)
        
        # Create node feature matrix and delay targets
        node_features_matrix = []
        node_delay_targets = []
        critical_path_mask = []  # Mark which nodes are on critical paths
        
        for node_id in range(len(global_nodes)):
            node_features_matrix.append(global_node_features[node_id])
        
        for node_name in sorted(global_nodes.keys(), key=lambda x: global_nodes[x]):
            delay_val = global_node_delays[node_name]
            # Ensure delay value is scalar
            if isinstance(delay_val, np.ndarray):
                delay_val = float(delay_val.item() if delay_val.size == 1 else delay_val.mean())
            delay_val = float(delay_val)
            node_delay_targets.append(delay_val)
            
            # Check if node is on critical path
            node_id = global_nodes[node_name]
            is_critical = any(node_id in path for path in critical_paths)
            critical_path_mask.append(is_critical)
        
        # Create edge matrix
        edges_matrix = list(global_edges)
        
        # Calculate fanin/fanout and update node features
        fanin_count = [0] * len(global_nodes)
        fanout_count = [0] * len(global_nodes)
        
        for from_id, to_id in edges_matrix:
            fanout_count[from_id] += 1
            fanin_count[to_id] += 1
        
        for i, feat in enumerate(node_features_matrix):
            feat[7] = fanin_count[i]   # fanin
            feat[8] = fanout_count[i]  # fanout
        
        # Create network data
        network_data = {
            'nodes': np.array(node_features_matrix, dtype=np.float32),
            'edges': np.array(edges_matrix, dtype=np.int64),
            'edge_features': np.array(global_edge_features, dtype=np.float32),
            'node_delays': np.array(node_delay_targets, dtype=np.float32),
            'critical_path_mask': np.array(critical_path_mask, dtype=bool),  # Critical path mask
            'critical_paths': critical_paths,  # Critical path node sequences
            'path_sequences': path_node_sequences,  # All path node sequences
            'num_nodes': len(global_nodes),
            'num_edges': len(edges_matrix),
            'num_paths': len(paths),
            'num_critical_nodes': sum(critical_path_mask),
            'source_node': source_node,
            'design_name': design_name,
            'network_id': f"{design_name}_{source_node}_{len(paths)}_paths"
        }
        
        return network_data
    
    def _identify_critical_paths(self, path_sequences: List[List[int]], path_delays: List[float]) -> List[List[int]]:
        """
        Identify critical paths (paths with maximum delay)
        
        Args:
            path_sequences: Path node sequence list
            path_delays: Path delay list
            
        Returns:
            List[List[int]]: Critical path node sequence list
        """
        if not path_delays:
            return []
        
        # Ensure all delay values are scalars
        path_delays = [float(delay) if not isinstance(delay, (int, float)) else float(delay) for delay in path_delays]
        
        max_delay = max(path_delays)
        delay_threshold = max_delay * self.config.critical_path_delay_ratio
        
        critical_paths = []
        for i, delay in enumerate(path_delays):
            if float(delay) >= delay_threshold and len(critical_paths) < self.config.max_critical_paths:
                critical_paths.append(path_sequences[i])
        
        # If no critical paths found, at least select the path with maximum delay
        if not critical_paths:
            max_delay_idx = int(np.argmax(path_delays))
            critical_paths.append(path_sequences[max_delay_idx])
        
        return critical_paths
    
    def run_pipeline(self) -> Optional[Dict[str, Any]]:
        """
        Run complete data processing pipeline
        
        Returns:
            Optional[Dict]: Processing results including data loaders
        """
        logger.info("Starting complete data processing pipeline")
        
        try:
            # Extract RC networks
            networks = self.extract_rc_networks()
            if not networks:
                logger.error("No networks extracted")
                return None
            
            # Clean and normalize data
            cleaned_networks = self.clean_and_normalize_data(networks)
            if not cleaned_networks:
                logger.error("No networks after cleaning")
                return None
            
            # Convert to PyTorch Geometric format
            graph_data = self._convert_to_pyg_format(cleaned_networks)
            if not graph_data:
                logger.error("Failed to convert to PyTorch Geometric format")
                return None
            
            # Split data
            train_data, val_data, test_data = self._split_data(graph_data)
            
            # Create data loaders
            train_loader, val_loader, test_loader = self._create_data_loaders(
                train_data, val_data, test_data
            )
            
            # Save processed data
            self._save_processed_data(train_data, val_data, test_data)
            
            logger.info(f"Pipeline completed successfully - Total networks: {len(graph_data)}")
            
            return {
                'train_loader': train_loader,
                'val_loader': val_loader,
                'test_loader': test_loader,
                'train_data': train_data,
                'val_data': val_data,
                'test_data': test_data,
                'total_networks': len(graph_data)
            }
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            import traceback
            logger.error(f"Detailed error: {traceback.format_exc()}")
            return None
    
    def _convert_to_pyg_format(self, networks: List[Dict[str, Any]]) -> List[Data]:
        """Convert network data to PyTorch Geometric format"""
        graph_data = []
        
        for network in networks:
            try:
                # Create PyTorch Geometric Data object
                data = Data(
                    x=torch.tensor(network['nodes'], dtype=torch.float32),
                    edge_index=torch.tensor(network['edges'], dtype=torch.long).t().contiguous(),
                    edge_attr=torch.tensor(network['edge_features'], dtype=torch.float32),
                    y=torch.tensor(network['node_delays'], dtype=torch.float32),
                    valid_mask=torch.tensor(network.get('node_valid_mask', np.ones(len(network['node_delays']), dtype=bool)), dtype=torch.bool)
                )
                
                # Add additional attributes
                data.design_name = network.get('design_name', 'unknown')
                data.network_id = network.get('network_id', 'unknown')
                data.num_nodes = network['num_nodes']
                data.num_edges = network['num_edges']
                
                graph_data.append(data)
                
            except Exception as e:
                logger.error(f"Error converting network to PyG format: {e}")
                continue
        
        return graph_data
    
    def _split_data(self, graph_data: List[Data]) -> Tuple[List[Data], List[Data], List[Data]]:
        """Split data into train/validation/test sets"""
        from sklearn.model_selection import train_test_split
        
        # First split: train vs (val + test)
        train_data, temp_data = train_test_split(
            graph_data, 
            test_size=(1 - self.config.train_ratio),
            random_state=self.config.random_seed
        )
        
        # Second split: val vs test
        val_ratio = self.config.val_ratio / (self.config.val_ratio + self.config.test_ratio)
        val_data, test_data = train_test_split(
            temp_data,
            test_size=(1 - val_ratio),
            random_state=self.config.random_seed
        )
        
        logger.info(f"Data split - Train: {len(train_data)}, Val: {len(val_data)}, Test: {len(test_data)}")
        return train_data, val_data, test_data
    
    def _create_data_loaders(self, train_data: List[Data], val_data: List[Data], test_data: List[Data]) -> Tuple[DataLoader, DataLoader, DataLoader]:
        """Create PyTorch Geometric data loaders"""
        train_loader = DataLoader(
            train_data, 
            batch_size=self.config.batch_size, 
            shuffle=True,
            num_workers=self.config.num_workers,
            pin_memory=True
        )
        
        val_loader = DataLoader(
            val_data, 
            batch_size=self.config.batch_size, 
            shuffle=False,
            num_workers=self.config.num_workers,
            pin_memory=True
        )
        
        test_loader = DataLoader(
            test_data, 
            batch_size=self.config.batch_size, 
            shuffle=False,
            num_workers=self.config.num_workers,
            pin_memory=True
        )
        
        return train_loader, val_loader, test_loader
    
    def _save_processed_data(self, train_data: List[Data], val_data: List[Data], test_data: List[Data]):
        """Save processed data to file"""
        processed_data = {
            'train_data': train_data,
            'val_data': val_data,
            'test_data': test_data,
            'design_normalization_params': getattr(self, 'design_normalization_params', {})
        }
        
        torch.save(processed_data, self.config.model_input_file)
        logger.info(f"Processed data saved to: {self.config.model_input_file}")
    
    def create_data_loaders(self, train_data: List[Data], val_data: List[Data], test_data: List[Data]) -> Tuple[DataLoader, DataLoader, DataLoader]:
        """Create data loaders from existing data"""
        return self._create_data_loaders(train_data, val_data, test_data)
    
    def clean_and_normalize_data(self, graph_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean and normalize data
        
        Args:
            graph_data_list: Original graph data list
            
        Returns:
            List[Dict]: Cleaned graph data list
        """
        logger.info("Starting data cleaning and normalization")
        
        cleaned_data = []
        all_node_features = []
        all_edge_features = []
        all_node_delays = []
        
        # If design-specific normalization is enabled, first calculate normalization parameters
        if self.config.use_design_specific_normalization:
            logger.info("Starting design-specific normalization processing")
            
            # Calculate normalization parameters
            design_normalization_params = self.compute_design_specific_normalization(graph_data_list)
            self.design_normalization_params = design_normalization_params
            
            # Save normalization parameters
            self.save_normalization_parameters(design_normalization_params)
            
            # Apply design-specific normalization
            graph_data_list = self.apply_design_specific_normalization(graph_data_list, design_normalization_params)
        
        # First collect all data for standardization
        logger.info("Cleaning and validating graph data...")
        for graph_data in tqdm(graph_data_list, desc="Cleaning graph data", leave=False):
            node_delays = graph_data['node_delays']
            
            # Basic delay value validation (only check if valid numerical values)
            valid_delays = np.isfinite(node_delays) & (node_delays >= 0)
            
            # Check if there are enough valid delay values
            if (not np.any(valid_delays) or 
                len(graph_data['nodes']) < self.config.min_nodes_per_net or 
                np.sum(valid_delays) < len(node_delays) * 0.3):  # Lower requirement to 30%
                continue
            
            # Keep original delay values, no truncation
            # Only check basic statistical properties for information recording
            delay_mean = np.mean(node_delays[valid_delays])
            delay_std = np.std(node_delays[valid_delays])
            delay_min = np.min(node_delays[valid_delays])
            delay_max = np.max(node_delays[valid_delays])
            
            if self.config.debug_delay_extraction:
                logger.info(f"  Graph {len(cleaned_data)+1} delay statistics: mean={delay_mean:.2e}, std={delay_std:.2e}, range=[{delay_min:.2e}, {delay_max:.2e}]")
            
            # Use original delay values directly, no modifications
            # graph_data['node_delays'] remains unchanged
            
            all_node_features.append(graph_data['nodes'])
            all_edge_features.append(graph_data['edge_features'])
            all_node_delays.append(node_delays)  # Use original delay values
            cleaned_data.append(graph_data)
        
        if not cleaned_data:
            logger.error("No data remaining after cleaning")
            return []
        
        # Standardize features
        node_features_concat = np.vstack(all_node_features)
        edge_features_concat = np.vstack(all_edge_features)
        node_delays_concat = np.concatenate(all_node_delays)
        
        # Standardize node and edge features
        normalized_node_features = self.node_scaler.fit_transform(node_features_concat)
        normalized_edge_features = self.edge_scaler.fit_transform(edge_features_concat)
        
        # Apply moderate standardization to delay targets, maintain natural data distribution
        # Only use log transformation when delay values span multiple orders of magnitude
        delay_range = np.max(node_delays_concat) / (np.min(node_delays_concat[node_delays_concat > 0]) + 1e-15)
        
        if delay_range > 1000:  # Only use log transformation when range exceeds 1000x
            log_delays = np.log1p(node_delays_concat / 1e-15)  # Use smaller normalization factor
            normalized_delays = self.delay_scaler.fit_transform(log_delays.reshape(-1, 1)).flatten()
            logger.info(f"Using log transformation for delay data, dynamic range: {delay_range:.2f}")
        else:
            # Direct standardization, maintain original data distribution
            normalized_delays = self.delay_scaler.fit_transform(node_delays_concat.reshape(-1, 1)).flatten()
            logger.info(f"Using linear standardization for delay data, dynamic range: {delay_range:.2f}")
        
        # Update data
        node_start_idx = 0
        edge_start_idx = 0
        delay_start_idx = 0
        
        for graph_data in cleaned_data:
            num_nodes = graph_data['num_nodes']
            num_edges = graph_data['num_edges']
            
            graph_data['nodes'] = normalized_node_features[node_start_idx:node_start_idx + num_nodes]
            graph_data['edge_features'] = normalized_edge_features[edge_start_idx:edge_start_idx + num_edges]
            graph_data['normalized_node_delays'] = normalized_delays[delay_start_idx:delay_start_idx + num_nodes]
            
            node_start_idx += num_nodes
            edge_start_idx += num_edges
            delay_start_idx += num_nodes
        
        logger.info(f"Cleaning and normalization completed, remaining {len(cleaned_data)} graphs")
        return cleaned_data
    
    def compute_design_specific_normalization(self, graph_data_list: List[Dict[str, Any]]) -> Dict[str, Dict]:
        """
        Calculate normalization parameters for each design
        
        Args:
            graph_data_list: Original graph data list
            
        Returns:
            Dict: Normalization parameters for each design {design_name: {'mean': float, 'std': float}}
        """
        logger.info("Calculating design-specific normalization parameters")
        
        # Group delay data by design
        design_delays = {}
        for graph_data in graph_data_list:
            design_name = graph_data.get('design_name', 'unknown')
            if design_name not in design_delays:
                design_delays[design_name] = []
            
            delays = graph_data['node_delays']
            # Only use valid delay values (greater than threshold)
            valid_delays = delays[delays > self.config.min_delay_threshold]
            if len(valid_delays) > 0:
                design_delays[design_name].extend(valid_delays)
        
        # Calculate normalization parameters for each design
        normalization_params = {}
        for design_name, delays in design_delays.items():
            if len(delays) > 0:
                delays_array = np.array(delays)
                
                # Use log transformation for delay values with large span
                if np.max(delays_array) / np.min(delays_array) > 1000:
                    log_delays = np.log1p(delays_array / 1e-15)
                    mean = np.mean(log_delays)
                    std = np.std(log_delays)
                    use_log = True
                else:
                    mean = np.mean(delays_array)
                    std = np.std(delays_array)
                    use_log = False
                
                # Ensure standard deviation is not zero
                if std < 1e-15:
                    std = 1.0
                
                normalization_params[design_name] = {
                    'mean': float(mean),
                    'std': float(std),
                    'use_log': use_log,
                    'sample_count': len(delays),
                    'delay_range': [float(np.min(delays_array)), float(np.max(delays_array))]
                }
                
                logger.info(f"Design {design_name}: mean={mean:.2e}, std={std:.2e}, "
                           f"samples={len(delays)}, use_log={use_log}")
        
        return normalization_params
    
    def apply_design_specific_normalization(self, graph_data_list: List[Dict[str, Any]], 
                                          normalization_params: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """
        Apply design-specific normalization
        
        Args:
            graph_data_list: Original graph data list
            normalization_params: Normalization parameters
            
        Returns:
            List[Dict]: Normalized graph data list
        """
        logger.info("Applying design-specific normalization")
        
        normalized_data = []
        for graph_data in graph_data_list:
            design_name = graph_data.get('design_name', 'unknown')
            
            if design_name not in normalization_params:
                logger.warning(f"Design {design_name} has no normalization parameters, skipping")
                continue
            
            params = normalization_params[design_name]
            delays = graph_data['node_delays'].copy()
            
            # Apply normalization
            if params['use_log']:
                # Log transformation + standardization
                log_delays = np.log1p(delays / 1e-15)
                normalized_delays = (log_delays - params['mean']) / params['std']
            else:
                # Direct standardization
                normalized_delays = (delays - params['mean']) / params['std']
            
            # Create new graph data copy
            normalized_graph = graph_data.copy()
            normalized_graph['normalized_node_delays'] = normalized_delays.astype(np.float32)
            normalized_graph['original_node_delays'] = delays.astype(np.float32)  # Save original delays
            
            normalized_data.append(normalized_graph)
        
        logger.info(f"Design-specific normalization completed, processed {len(normalized_data)} graphs")
        return normalized_data
    
    def save_normalization_parameters(self, normalization_params: Dict[str, Dict]):
        """
        Save normalization parameters to file
        
        Args:
            normalization_params: Normalization parameters
        """
        if self.config.save_normalization_params:
            try:
                with open(self.config.normalization_params_file, 'w') as f:
                    json.dump(normalization_params, f, indent=2)
                logger.info(f"Normalization parameters saved to: {self.config.normalization_params_file}")
            except Exception as e:
                logger.error(f"Failed to save normalization parameters: {e}")
    
    def load_normalization_parameters(self) -> Optional[Dict[str, Dict]]:
        """
        Load normalization parameters from file
        
        Returns:
            Optional[Dict]: Normalization parameters, returns None if file doesn't exist
        """
        if os.path.exists(self.config.normalization_params_file):
            try:
                with open(self.config.normalization_params_file, 'r') as f:
                    params = json.load(f)
                logger.info(f"Loaded normalization parameters from file: {self.config.normalization_params_file}")
                return params
            except Exception as e:
                logger.error(f"Failed to load normalization parameters: {e}")
        return None
    
    def denormalize_delays(self, normalized_delays: np.ndarray, design_name: str, 
                          normalization_params: Dict[str, Dict]) -> np.ndarray:
        """
        Convert normalized delays back to original values
        
        Args:
            normalized_delays: Normalized delay values
            design_name: Design name
            normalization_params: Normalization parameters
            
        Returns:
            np.ndarray: Original delay values
        """
        if design_name not in normalization_params:
            logger.warning(f"Design {design_name} has no normalization parameters, returning original values")
            return normalized_delays
        
        params = normalization_params[design_name]
        
        # Denormalize
        if params['use_log']:
            # Denormalize + inverse log transformation
            log_delays = normalized_delays * params['std'] + params['mean']
            original_delays = (np.expm1(log_delays)) * 1e-15
        else:
            # Direct denormalization
            original_delays = normalized_delays * params['std'] + params['mean']
        
        return original_delays

    # Additional helper methods would be added here...
    # (The file is quite large, so I'm showing the key structure and main methods)
    
    def _parse_wire_path_file_for_network(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Parse wire_path file and extract path information for network construction"""
        # Implementation details would go here
        pass
    
    def _parse_timing_file_for_network(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse timing file and extract path information for network construction"""
        # Implementation details would go here
        pass

# Usage examples
if __name__ == "__main__":
    # Example usage
    config = RCNetworkDataConfig(
        raw_input_dirs=[
            "/data2/project_share/dataset_baseline/s713/workspace",
            "/data2/project_share/dataset_baseline/s44/workspace"
        ],
        pattern="/output/iEDA/vectors/timing_data",
        model_input_file="./rc_network_dataset.pt",
        plot_dir="./rc_network_analysis_plots"
    )
    
    processor = RCNetworkDataProcessor(config)
    result = processor.run_pipeline()
    
    if result:
        print(f"Processing completed successfully!")
        print(f"Train loader: {result['train_loader']}")
        print(f"Val loader: {result['val_loader']}")
        print(f"Test loader: {result['test_loader']}")
        print(f"Total networks: {result['total_networks']}")
    else:
        print("Processing failed!")