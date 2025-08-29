#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : transformer_process.py
@Author : yhqiu
@Desc : Data process module for path delay prediction
"""
import os
import shutil
import random
import yaml
import torch
import hashlib
import json
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional, Union
from concurrent.futures import ProcessPoolExecutor
from torch.utils.data import Dataset, DataLoader, TensorDataset
from tqdm import tqdm

from transformer_config import DataConfig


class YMLDatasetHandler:
    """Handler for YML dataset collection and sampling"""

    def __init__(self, data_from: str, data_to: str):
        """
        Initialize dataset handler.

        Args:
            data_from: Source data path
            data_to: Target data path
        """
        self.data_from = data_from
        self.data_to = data_to
        # Ensure target directory exists
        os.makedirs(self.data_to, exist_ok=True)

    def collect_yml(self) -> Dict[str, int]:
        """
        Count .yml files in specified directory and print relative paths.
        Creates target directory if it doesn't exist.

        Returns:
            Dictionary with directory names and file counts
        """
        yml_file_counts = {}

        for root, dirs, files in os.walk(self.data_from):
            if (
                os.path.basename(root) == "wire_paths"
            ):  # Only process wire_paths directories
                for file in files:
                    if file.endswith(".yml"):  # Filter .yml files
                        relative_path = os.path.relpath(root, self.data_from)
                        yml_file_counts[relative_path] = (
                            yml_file_counts.get(relative_path, 0) + 1
                        )

        for dirname, count in yml_file_counts.items():
            print(f"{dirname}: {count} .yml files")

            # Create target directory
            dir_simply_name = dirname.split("/")[0]
            print(f"Processing: {dir_simply_name}")
            target_dir = os.path.join(self.data_to, dir_simply_name)
            os.makedirs(target_dir, exist_ok=True)

            # Copy files
            source_dir = os.path.join(self.data_from, dirname)
            for file in os.listdir(source_dir):
                if file.endswith(".yml"):
                    src_file = os.path.join(source_dir, file)
                    dst_file = os.path.join(target_dir, file)
                    shutil.copy(src_file, dst_file)

        return yml_file_counts

    def sample_dataset(self, sample_num: int, seed: int = 42) -> List[str]:
        """
        Randomly sample specified number of .yml files from dataset.

        Args:
            sample_num: Number of files to sample
            seed: Random seed for reproducibility

        Returns:
            List of sampled file paths
        """
        # Collect all .yml file paths
        file_paths = []
        for dirpath, dirnames, filenames in os.walk(self.data_to):
            file_paths.extend(
                [os.path.join(dirpath, f) for f in filenames if f.endswith(".yml")]
            )

        # Ensure sufficient files
        actual_sample_num = min(sample_num, len(file_paths))
        if len(file_paths) < sample_num:
            print(
                f"Warning: Insufficient files, only {len(file_paths)} available. Using all available files."
            )

        # Random sampling
        random.seed(seed)
        sampled_files = random.sample(file_paths, actual_sample_num)

        return sampled_files


class CircuitParser:
    """Parser for circuit data from YML files"""

    def __init__(self, file_path: str):
        """
        Initialize circuit parser.

        Args:
            file_path: Path to YML file
        """
        self.file_path = file_path
        self.data = None
        self.capacitance_list = []
        self.slew_list = []
        self.resistance_list = []
        self.incr_list = []
        self.point_list = []

    def load_data(self) -> None:
        """Load YAML data from file."""
        try:
            with open(self.file_path, "r") as f:
                self.data = yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading file {self.file_path}: {e}")
            raise

    def parse_data(self) -> None:
        """Parse nodes, net arcs, and instance arcs in order."""
        if self.data is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        for key, value in self.data.items():
            if key.startswith("node_"):
                # Parse node
                self.capacitance_list.append(value.get("Capacitance", 0))
                self.slew_list.append(value.get("slew", 0))
                self.resistance_list.append(0)  # Default R value for nodes
                point = value.get("Point", "")
                if point:
                    self.point_list.append(
                        point.split("(")[0].strip()
                    )  # Extract portion before '('

            elif key.startswith("net_arc_"):
                # Parse instance arc
                incr = value.get("Incr", 0)
                self.incr_list.append(value.get("Incr", 0))
                for edge_key, edge_value in value.items():
                    if edge_key.startswith("edge_"):
                        self.capacitance_list.append(edge_value.get("wire_C", 0))
                        self.slew_list.append(edge_value.get("to_slew", 0))
                        self.resistance_list.append(edge_value.get("wire_R", 0))
                        wire_from_node = edge_value.get("wire_from_node", "")
                        if wire_from_node:
                            self.point_list.append(
                                wire_from_node.replace(" ", "")
                            )  # Remove spaces

            elif key.startswith("inst_arc_"):
                # Parse instance arc
                incr = value.get("Incr", 0)
                self.incr_list.append(value.get("Incr", 0))

        self.point_list = list(dict.fromkeys(self.point_list))  # Remove duplicates

    def get_combined_tensor(self) -> torch.Tensor:
        """Combine all lists into a single 2D tensor with each list as a row."""
        combined_data = [self.capacitance_list, self.slew_list, self.resistance_list]
        tensor = torch.tensor(combined_data, dtype=torch.float32)
        return tensor

    def get_incr_tensor(self) -> Tuple[torch.Tensor, float]:
        """Get the tensor of Incr values and calculate the sum."""
        incr_tensor = torch.tensor(self.incr_list, dtype=torch.float32)
        incr_sum = incr_tensor.sum().item()
        return incr_tensor, incr_sum

    @staticmethod
    def pad_tensors(
        tensor_list: List[torch.Tensor], max_length: int
    ) -> List[torch.Tensor]:
        """Pad all tensors in the list to the max length."""
        padded_tensors = []
        for tensor in tensor_list:
            padded = torch.nn.functional.pad(
                tensor, (0, max_length - tensor.size(1)), "constant", 0
            )
            padded_tensors.append(padded)
        return padded_tensors

    def generate_hash(self) -> str:
        """Generate a hash for the concatenated unique strings."""
        concatenated = "".join(self.point_list)
        hash_object = hashlib.md5(concatenated.encode())
        return hash_object.hexdigest()


class DataProcessor:
    """Data processor for path delay prediction"""

    def __init__(self, config: DataConfig):
        """
        Initialize data processor.

        Args:
            config: Data configuration
        """
        self.config = config

    def process_file(self, file_path: str) -> Tuple[torch.Tensor, float]:
        """
        Process single file and return feature tensor and label.

        Args:
            file_path: Path to YML file

        Returns:
            Tuple of (feature tensor, label)
        """
        parser = CircuitParser(file_path)
        parser.load_data()
        parser.parse_data()
        combined_tensor = parser.get_combined_tensor()
        incr_tensor, incr_sum = parser.get_incr_tensor()
        return combined_tensor, incr_sum

    def process_dataset_dirs(
        self,
        dirs_list: List[str],
        dataset_directory: str,
        sample_num: int,
        normalize: bool,
        stats_file: str,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Process multiple dataset directories and merge results.

        Args:
            dirs_list: List of dataset directories
            stats_file: File to save normalization statistics

        Returns:
            Tuple of (features tensor, labels tensor)
        """
        all_tensors = []
        all_labels = []
        normalization_stats = {}

        for data_from in dirs_list:
            handler = YMLDatasetHandler(data_from, dataset_directory)
            handler.collect_yml()  # only run once to collect files
            sampled_files = handler.sample_dataset(sample_num, self.config.random_seed)
            print(f"Sampled {len(sampled_files)} files from {data_from}")

            # Use multiprocessing to process data
            with ProcessPoolExecutor() as executor:
                results = list(executor.map(self.process_file, sampled_files))

            if results:  # Ensure we have results
                tensors, labels = zip(*results)

                # Extract design name
                design_name = Path(data_from).name

                # Gaussian normalization for labels
                if normalize:
                    labels_array = np.array(labels)
                    mean = float(np.mean(labels_array))
                    std = float(np.std(labels_array))

                    # Prevent division by zero
                    if std < 1e-10:
                        std = 1.0
                        print(f"Warning: {design_name} std close to 0, set to 1.0")

                    # Record normalization statistics
                    normalization_stats[design_name] = {"mean": mean, "std": std}

                    # Normalize labels
                    normalized_labels = [(label - mean) / std for label in labels]
                    all_tensors.extend(tensors)
                    all_labels.extend(normalized_labels)
                else:
                    all_tensors.extend(tensors)
                    all_labels.extend(labels)

        if not all_tensors:  # Check if we have data
            raise ValueError("No valid data found")

        # Save normalization statistics to JSON file
        if normalize:
            with open(stats_file, "w") as f:
                json.dump(normalization_stats, f, indent=4)
            print(f"Normalization statistics saved to {stats_file}")

        # Find max path length and pad tensors
        max_length = max(tensor.shape[1] for tensor in all_tensors)
        padded_tensors = CircuitParser.pad_tensors(all_tensors, max_length)

        features_tensor = torch.stack(padded_tensors).permute(0, 2, 1)
        labels_tensor = torch.tensor(all_labels, dtype=torch.float32).unsqueeze(1)

        return features_tensor, labels_tensor

    def prepare_data(
        self,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Collect data and prepare feature and label tensors.

        Returns:
            Tuple of (train_features, train_labels, test_features, test_labels)
        """
        # Set random seed for reproducibility
        random.seed(self.config.random_seed)

        print(f"Number of training directories: {len(self.config.train_dirs)}")
        print(f"Number of test directories: {len(self.config.test_dirs)}")

        # Process training set
        print("Processing training set:")
        train_features, train_labels = self.process_dataset_dirs(
            self.config.train_dirs,
            self.config.dataset_directory,
            self.config.sample_num,
            self.config.normalize,
            self.config.train_stats_file,
        )

        # Process test set
        print("Processing test set:")
        test_features, test_labels = self.process_dataset_dirs(
            self.config.test_dirs,
            self.config.dataset_directory,
            self.config.sample_num,
            self.config.normalize,
            self.config.test_stats_file,
        )

        return train_features, train_labels, test_features, test_labels

    def create_dataloaders(
        self,
        train_features: torch.Tensor,
        train_labels: torch.Tensor,
        test_features: torch.Tensor,
        test_labels: torch.Tensor,
    ) -> Tuple[DataLoader, DataLoader]:
        """
        Create data loaders for training and test sets.

        Args:
            train_features: Training features
            train_labels: Training labels
            test_features: Test features
            test_labels: Test labels

        Returns:
            Tuple of (train_loader, test_loader)
        """
        train_dataset = TensorDataset(train_features, train_labels)
        test_dataset = TensorDataset(test_features, test_labels)

        train_loader = DataLoader(
            train_dataset,
            batch_size=self.config.batch_size,
            shuffle=True,
            num_workers=self.config.num_workers,
            pin_memory=self.config.pin_memory,
        )

        test_loader = DataLoader(
            test_dataset,
            batch_size=self.config.batch_size,
            shuffle=False,
            num_workers=self.config.num_workers,
            pin_memory=self.config.pin_memory,
        )

        return train_loader, test_loader

    def denormalize_predictions(
        self,
        predictions: Union[torch.Tensor, List[float]],
        design_name: str,
        stats_file: str,
    ) -> Union[torch.Tensor, List[float]]:
        """
        Convert normalized predictions back to real values.

        Args:
            predictions: Normalized predictions
            design_name: Design name
            stats_file: JSON file path with normalization statistics

        Returns:
            Denormalized predictions
        """
        # Load normalization statistics
        with open(stats_file, "r") as f:
            stats = json.load(f)

        if design_name not in stats:
            raise ValueError(
                f"Cannot find normalization statistics for design {design_name}"
            )

        mean = stats[design_name]["mean"]
        std = stats[design_name]["std"]

        # Convert back to real values
        if isinstance(predictions, torch.Tensor):
            denormalized = predictions * std + mean
        else:
            denormalized = [pred * std + mean for pred in predictions]

        return denormalized


# Usage example
if __name__ == "__main__":
    # Create configuration
    config = DataConfig(
        train_dirs=[
            "/data2/project_share/dataset_baseline/gcd",
            "/data2/project_share/dataset_baseline/BM64",
            "/data2/project_share/dataset_baseline/s1488",
            "/data2/project_share/dataset_baseline/salsa20",
            "/data2/project_share/dataset_baseline/s38417",
            "/data2/project_share/dataset_baseline/s9234",
            "/data2/project_share/dataset_baseline/s15850",
            "/data2/project_share/dataset_baseline/s38584",
            "/data2/project_share/dataset_baseline/s713",
            "/data2/project_share/dataset_baseline/apb4_uart",
            "/data2/project_share/dataset_baseline/s1238",
            "/data2/project_share/dataset_baseline/apb4_wdg",
            "/data2/project_share/dataset_baseline/apb4_ps2",
            "/data2/project_share/dataset_baseline/s5378",
            "/data2/project_share/dataset_baseline/PPU",
            "/data2/project_share/dataset_baseline/apb4_timer",
            "/data2/project_share/dataset_baseline/s13207",
            "/data2/project_share/dataset_baseline/apb4_i2c",
            "/data2/project_share/dataset_baseline/apb4_rng",
        ],
        test_dirs=[
            "/data2/project_share/dataset_baseline/apb4_clint",
            "/data2/project_share/dataset_baseline/s35932",
            "/data2/project_share/dataset_baseline/apb4_pwm",
            "/data2/project_share/dataset_baseline/ASIC",
            "/data2/project_share/dataset_baseline/s44",
            "/data2/project_share/dataset_baseline/apb4_archinfo",
        ],
        sample_num=3000,
        batch_size=32,
        random_seed=42,
        normalize=False,
        dataset_directory="dataset",
        train_stats_file="train_normalization_stats.json",
        test_stats_file="test_normalization_stats.json",
    )

    # Create data processor
    processor = DataProcessor(config)

    # Prepare data
    train_features, train_labels, test_features, test_labels = processor.prepare_data()
    print(f"Train Features Shape: {train_features.shape}")
    print(f"Train Labels Shape: {train_labels.shape}")
    print(f"Test Features Shape: {test_features.shape}")
    print(f"Test Labels Shape: {test_labels.shape}")

    # Create data loaders
    train_loader, test_loader = processor.create_dataloaders(
        train_features, train_labels, test_features, test_labels
    )
