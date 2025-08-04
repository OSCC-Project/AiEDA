#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : tabnet_process.py
@Author : yhqiu
@Desc : data process module for tabnet
'''
import os
import json
import csv
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import List, Union, Tuple, Dict, Any, Optional
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import logging
import time

from tabnet_config import DataConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DataProcessor:
    """Data processor class"""
    def __init__(self, config: DataConfig):
        self.config = config
        # Configure logger
        self.logger = logging.getLogger(__name__)

        # Initialize normalizers
        self.via_scaler = MinMaxScaler()
        self.wl_baseline_scaler = MinMaxScaler()
        self.wl_with_via_scaler = MinMaxScaler()

        # Save feature names
        self.via_feature_names = None
        self.wl_baseline_feature_names = None
        self.wl_with_via_feature_names = None

    def run_pipeline(self) -> str:
        """Execute complete data processing pipeline"""
        self.logger.info("Starting complete data processing pipeline")

        # step 1: Extract feature data
        combined_df = self._extract_and_combine_features()
        if combined_df is None or combined_df.empty:
            self.logger.error("Feature extraction failed, pipeline terminated")
            return None

        # step 2: Data cleaning
        combined_df = self._clean_data(combined_df)

        # step 3: Add engineered features
        combined_df = self._add_engineered_features(combined_df)

        # step 4: Analyze target distribution (optional)
        if hasattr(self.config, 'plot_dir') and self.config.plot_dir:
            self._analyze_target_distribution(combined_df)

        # step 5: Remove outliers
        combined_df = self._remove_outliers(combined_df)

        # step 6: Save final data
        final_file = self._save_final_data(combined_df)

        # Show final data information
        self._show_final_data_info(combined_df)

        self.logger.info(f"Data processing pipeline completed, final file: {final_file}")

    def _extract_and_combine_features(self) -> pd.DataFrame:
        """Extract features from JSON files and combine all data"""
        self.logger.info("Starting feature extraction and combination")
        all_dataframes = []

        for input_dir in self.config.raw_input_dirs:
            self.logger.info(f"Processing directory: {input_dir}")

            # Collect all data from single directory
            directory_data = []
            processed_count = 0
            error_count = 0

            # Get all JSON files
            json_files = [f for f in os.listdir(
                input_dir) if f.endswith('.json')]
            total_files = len(json_files)

            self.logger.info(f"Found {total_files} JSON files")

            for i, filename in enumerate(json_files):
                filepath = os.path.join(input_dir, filename)

                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                        # Extract feature data
                        row_data = {
                            'id': data.get('id', 'N/A'),
                            'wire_len': data.get('feature', {}).get('wire_len', 0),
                            'width': data.get('feature', {}).get('width', 0),
                            'height': data.get('feature', {}).get('height', 0),
                            'fanout': data.get('feature', {}).get('fanout', 0),
                            'aspect_ratio': data.get('feature', {}).get('aspect_ratio', 0),
                            'l_ness': data.get('feature', {}).get('l_ness', 0.0),
                            'rsmt': data.get('feature', {}).get('rsmt', 0.0),
                            'via_num': data.get('feature', {}).get('via_num', 0.0)
                        }

                        directory_data.append(row_data)
                        processed_count += 1

                except Exception as e:
                    error_count += 1
                    self.logger.error(f"Error processing file {filename}: {str(e)}")

                # Show progress
                if (i + 1) % 1000 == 0 or (i + 1) == total_files:
                    self.logger.info(
                        f"Progress: {i + 1}/{total_files} ({(i + 1)/total_files*100:.1f}%)")

            # Convert current directory data to DataFrame
            if directory_data:
                df = pd.DataFrame(directory_data)
                # Remove id column (if exists)
                if 'id' in df.columns:
                    df = df.drop('id', axis=1)
                # Ensure column order
                feature_cols = [
                    col for col in self.config.extracted_feature_columns if col != 'id']
                df = df[feature_cols]
                all_dataframes.append(df)

                self.logger.info(
                    f"Directory {input_dir} processing completed: {processed_count} files successful, {error_count} errors")
            else:
                self.logger.warning(f"No valid data found in directory {input_dir}")

        if not all_dataframes:
            self.logger.error("No valid data found")
            return None

        # Combine all data
        self.logger.info("Starting data combination")
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        self.logger.info(f"Combination completed, total {len(combined_df)} rows of data")

        return combined_df

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean data"""
        self.logger.info("Starting data cleaning")
        original_count = len(df)

        # Apply cleaning rules
        df_cleaned = df[df['fanout'] <= self.config.max_fanout]
        df_cleaned = df_cleaned[df_cleaned['aspect_ratio']
                                <= self.config.max_aspect_ratio]
        df_cleaned = df_cleaned[(df_cleaned['height'] > 0) &
                                (df_cleaned['width'] > 0)]

        cleaned_count = len(df_cleaned)
        removed_count = original_count - cleaned_count
        self.logger.info(
            f"Data cleaning completed: original {original_count} rows, after cleaning {cleaned_count} rows, removed {removed_count} rows")

        return df_cleaned

    def _add_engineered_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add engineered features
        """
        self.logger.info("Starting feature engineering")

        # Create copy to avoid modifying original data
        df_engineered = df.copy()

        # Add area feature
        df_engineered['area'] = df_engineered['width'] * \
            df_engineered['height']

        # Add routing ratio features
        df_engineered['route_ratio_x'] = df_engineered['width'] / \
            df_engineered['area']
        df_engineered['route_ratio_y'] = df_engineered['height'] / \
            df_engineered['area']

        # Rename columns
        df_engineered['fanout'] = df_engineered['fanout'] + 1
        df_engineered.rename(
            columns={'fanout': 'pin_num', 'wire_len': 'drwl'}, inplace=True)

        self.logger.info("Feature engineering completed")
        self.logger.info(f"Number of columns after adding new features: {len(df_engineered.columns)}")

        return df_engineered

    def _analyze_target_distribution(self, df: pd.DataFrame) -> None:
        """
        Analyze target value distribution
        """
        self.logger.info("Starting target distribution analysis")

        # Calculate target values
        target_series = df['drwl'] / df['rsmt']

        # Basic statistics
        stats_info = target_series.describe()
        self.logger.info(f"Target value basic statistics:\n{stats_info}")

        # Calculate quantiles
        percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
        quantiles = np.percentile(target_series, percentiles)
        self.logger.info("Quantile distribution:")
        for p, q in zip(percentiles, quantiles):
            self.logger.info(f"{p}% quantile: {q:.4f}")

        # Create chart directory
        os.makedirs(self.config.plot_dir, exist_ok=True)

        # Plot distribution charts
        self._plot_distribution_charts(target_series)

        self.logger.info(f"Analysis charts saved to {self.config.plot_dir} directory")

    def _plot_distribution_charts(self, target_series: pd.Series) -> None:
        """
        Plot target distribution charts
        """
        # Plot histogram and kernel density estimation
        plt.figure(figsize=(12, 6))
        sns.histplot(data=target_series, bins=100, kde=True)
        plt.title('drwl/rsmt Distribution')
        plt.xlabel('drwl/rsmt')
        plt.ylabel('Count')
        plt.savefig(os.path.join(self.config.plot_dir,
                    'target_distribution.png'))
        plt.close()

        # Plot boxplot
        plt.figure(figsize=(10, 6))
        sns.boxplot(x=target_series)
        plt.title('drwl/rsmt Boxplot')
        plt.xlabel('drwl/rsmt')
        plt.savefig(os.path.join(self.config.plot_dir, 'target_boxplot.png'))
        plt.close()

        # Plot Q-Q plot
        from scipy import stats
        plt.figure(figsize=(10, 6))
        stats.probplot(target_series, dist="norm", plot=plt)
        plt.title('Q-Q Plot of drwl/rsmt')
        plt.savefig(os.path.join(self.config.plot_dir, 'target_qq_plot.png'))
        plt.close()

        # Segment statistics plot
        self._plot_segment_statistics(target_series)

    def _plot_segment_statistics(self, target_series: pd.Series) -> None:
        """
        Plot segment statistics charts
        """
        # Segment statistics
        bins = [0, 0.8, 0.9, 1.0, 1.1, 1.2, float('inf')]
        labels = ['<0.8', '0.8-0.9', '0.9-1.0', '1.0-1.1', '1.1-1.2', '>1.2']

        # Create temporary DataFrame for segmentation
        temp_df = pd.DataFrame({'target': target_series})
        temp_df['range'] = pd.cut(temp_df['target'], bins=bins, labels=labels)
        segment_stats = temp_df.groupby(
            'range')['target'].agg(['count', 'mean', 'std'])
        segment_stats['percentage'] = segment_stats['count'] / \
            len(temp_df) * 100

        self.logger.info("Segment statistics:")
        self.logger.info(segment_stats)

        # Plot segment statistics bar chart
        plt.figure(figsize=(12, 6))
        segment_stats['percentage'].plot(kind='bar')
        plt.title('Distribution of drwl/rsmt Ranges')
        plt.xlabel('Range')
        plt.ylabel('Percentage (%)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(self.config.plot_dir, 'target_segments.png'))
        plt.close()

    def _remove_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove outliers
        """
        self.logger.info("Starting outlier removal")
        original_count = len(df)

        # Calculate target values
        target_series = df['drwl'] / df['rsmt']

        # Calculate outlier boundaries
        Q1 = target_series.quantile(0.25)
        Q3 = target_series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - self.config.outlier_multiplier * IQR
        upper_bound = Q3 + self.config.outlier_multiplier * IQR

        self.logger.info(f"Outlier boundaries: lower bound {lower_bound:.4f}, upper bound {upper_bound:.4f}")

        # Remove outliers
        outlier_mask = (target_series >= lower_bound) & (
            target_series <= upper_bound)
        df_cleaned = df[outlier_mask].copy()

        cleaned_count = len(df_cleaned)
        removed_count = original_count - cleaned_count
        self.logger.info(
            f"Outlier removal completed: original {original_count} rows, after cleaning {cleaned_count} rows, removed {removed_count} rows")

        return df_cleaned

    def _save_final_data(self, df: pd.DataFrame) -> str:
        """
        Save final data
        """
        self.logger.info("Saving final cleaned file")
        df.to_csv(self.config.model_input_file, index=False)

        self.logger.info(f"Final dataset contains {len(df)} rows, {len(df.columns)} columns")
        return self.config.model_input_file

    def _show_final_data_info(self, df: pd.DataFrame) -> None:
        """
        Show final dataset information
        """
        self.logger.info("=== Final Dataset Information ===")
        self.logger.info(f"Data shape: {df.shape}")
        self.logger.info(f"Column names: {list(df.columns)}")

        # Show basic statistics for each column
        self.logger.info("Column statistics:")
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                stats_info = df[col].describe()
                self.logger.info(f"{col}: min={stats_info['min']:.4f}, max={stats_info['max']:.4f}, "
                                 f"mean={stats_info['mean']:.4f}, std={stats_info['std']:.4f}")

        # Check missing values
        missing_values = df.isnull().sum()
        if missing_values.sum() > 0:
            self.logger.warning("Missing values found:")
            for col, count in missing_values.items():
                if count > 0:
                    self.logger.warning(f"{col}: {count} missing values")
        else:
            self.logger.info("No missing values found")

    def enhance_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Feature enhancement

        Args:
            X: Input feature DataFrame

        Returns:
            Enhanced feature DataFrame
        """
        self.logger.info("Performing feature enhancement...")
        X_enhanced = X.copy()

        # Feature interactions based on correlation analysis
        X_enhanced['pin_rsmt'] = X['pin_num'] * X['rsmt']
        X_enhanced['l_ness_route_y'] = X['l_ness'] * X['route_ratio_y']

        # Composite features for extreme value regions
        X_enhanced['shape_complexity'] = X['width'] * \
            X['height'] / (X['rsmt'] ** 2)
        X_enhanced['pin_density'] = X['pin_num'] / X['area']

        # Non-linear transformations
        X_enhanced['rsmt_sqrt'] = np.sqrt(X['rsmt'])

        # Geometric feature combinations
        X_enhanced['hpwl'] = X['width'] + X['height']
        X_enhanced['log_pin'] = np.log1p(X['pin_num'])
        X_enhanced['log_area'] = np.log1p(X['area'])
        X_enhanced['sqrt_rsmt'] = np.sqrt(X['rsmt'])

        self.logger.info(
            f"Feature enhancement completed: original features {X.shape[1]}, enhanced features {X_enhanced.shape[1]}")

        return X_enhanced


    def load_and_preprocess_data(self, data_path: str) -> Dict[str, Any]:
        """
        Load data and preprocess

        Args:
            data_path: Data file path

        Returns:
            Preprocessed data dictionary
        """
        self.logger.info(f"Starting data loading: {data_path}")
        start_time = time.time()

        # Read data
        df = pd.read_csv(data_path)

        # Calculate target values
        df['target'] = df['drwl'] / df['rsmt']

        # Create target value bins
        df['target_bin'] = pd.cut(df['target'],
                                  bins=self.config.target_bins,
                                  labels=self.config.target_labels)

        # Analyze sample counts for each interval
        bin_counts = df['target_bin'].value_counts()
        self.logger.info("Target value interval distribution:")
        for bin_name, count in bin_counts.items():
            self.logger.info(
                f"{bin_name}: {count} samples ({count/len(df)*100:.2f}%)")

        # Prepare datasets for different stages
        X_via = df[self.config.via_feature_columns]
        y_via = df['via_num']

        X_wl_baseline = df[self.config.wl_baseline_feature_columns]
        y_wl = df['target']

        X_wl_with_via = df[self.config.wl_with_via_feature_columns]

        # Enhance features
        X_via_enhanced = self.enhance_features(X_via)
        X_wl_baseline_enhanced = self.enhance_features(X_wl_baseline)
        X_wl_with_via_enhanced = self.enhance_features(X_wl_with_via)

        # Data splitting
        X_wl_baseline_train, X_wl_baseline_test, y_wl_train, y_wl_test, train_bins, test_bins = train_test_split(
            X_wl_baseline_enhanced, y_wl, df['target_bin'],
            test_size=self.config.test_size,
            random_state=self.config.random_state,
            stratify=df['target_bin']
        )

        # Split other data using the same indices
        train_indices = y_wl_train.index
        test_indices = y_wl_test.index

        X_wl_with_via_train = X_wl_with_via_enhanced.loc[train_indices]
        X_wl_with_via_test = X_wl_with_via_enhanced.loc[test_indices]

        X_via_train = X_via_enhanced.loc[train_indices]
        X_via_test = X_via_enhanced.loc[test_indices]
        y_via_train = y_via.loc[train_indices]
        y_via_test = y_via.loc[test_indices]

        self.logger.info(
            f"Dataset splitting completed: training set {X_via_train.shape[0]} samples, test set {X_via_test.shape[0]} samples")

        # Feature normalization
        self.logger.info("Starting feature normalization...")
        X_via_train_scaled = self.via_scaler.fit_transform(X_via_train)
        X_via_test_scaled = self.via_scaler.transform(X_via_test)

        X_wl_baseline_train_scaled = self.wl_baseline_scaler.fit_transform(
            X_wl_baseline_train)
        X_wl_baseline_test_scaled = self.wl_baseline_scaler.transform(
            X_wl_baseline_test)

        X_wl_with_via_train_scaled = self.wl_with_via_scaler.fit_transform(
            X_wl_with_via_train)
        X_wl_with_via_test_scaled = self.wl_with_via_scaler.transform(
            X_wl_with_via_test)

        # Save feature names
        self.via_feature_names = list(X_via_enhanced.columns)
        self.wl_baseline_feature_names = list(X_wl_baseline_enhanced.columns)
        self.wl_with_via_feature_names = list(X_wl_with_via_enhanced.columns)

        end_time = time.time()
        self.logger.info(f"Data preprocessing completed! Time elapsed: {end_time - start_time:.2f} seconds")

        return {
            'via_train': (X_via_train_scaled, y_via_train.values),
            'via_test': (X_via_test_scaled, y_via_test.values),
            'wl_baseline_train': (X_wl_baseline_train_scaled, y_wl_train.values),
            'wl_baseline_test': (X_wl_baseline_test_scaled, y_wl_test.values),
            'wl_with_real_via_train': (X_wl_with_via_train_scaled, y_wl_train.values),
            'wl_with_real_via_test': (X_wl_with_via_test_scaled, y_wl_test.values),
            'X_via_test_orig': X_via_test,
            'X_wl_baseline_test_orig': X_wl_baseline_test,
            'X_wl_with_via_test_orig': X_wl_with_via_test,
            'y_wl_test': y_wl_test.values,
            'train_bins': train_bins,
            'test_bins': test_bins,
            'via_feature_cols': self.config.via_feature_columns,
            'wl_baseline_feature_cols': self.config.wl_baseline_feature_columns,
            'wl_with_via_feature_cols': self.config.wl_with_via_feature_columns
        }


# Usage example
if __name__ == "__main__":
    INPUT_DIRECTORYS = [
        "/data/project_share/yhqiu/aes/workspace/output/innovus/feature/large_model/nets",
        "/data/project_share/yhqiu/aes_core/workspace/output/innovus/feature/large_model/nets",
        "/data/project_share/yhqiu/apb4_i2c/workspace/output/innovus/feature/large_model/nets",
        "/data/project_share/yhqiu/apb4_ps2/workspace/output/innovus/feature/large_model/nets",
        "/data/project_share/yhqiu/apb4_pwm/workspace/output/innovus/feature/large_model/nets",
        "/data/project_share/yhqiu/apb4_rng/workspace/output/innovus/feature/large_model/nets",
        "/data/project_share/yhqiu/apb4_timer/workspace/output/innovus/feature/large_model/nets",
        "/data/project_share/yhqiu/apb4_uart/workspace/output/innovus/feature/large_model/nets",
        "/data/project_share/yhqiu/apb4_wdg/workspace/output/innovus/feature/large_model/nets",
        "/data/project_share/yhqiu/blabla/workspace/output/innovus/feature/large_model/nets",
        "/data/project_share/yhqiu/BM64/workspace/output/innovus/feature/large_model/nets",
        "/data/project_share/yhqiu/gcd/workspace/output/innovus/feature/large_model/nets",
        "/data/project_share/yhqiu/jpeg_encoder/workspace/output/innovus/feature/large_model/nets",
        "/data/project_share/yhqiu/picorv32/workspace/output/innovus/feature/large_model/nets",
        "/data/project_share/yhqiu/PPU/workspace/output/innovus/feature/large_model/nets",
        "/data/project_share/yhqiu/s13207/workspace/output/innovus/feature/large_model/nets",
        "/data/project_share/yhqiu/apb4_archinfo/workspace/output/innovus/feature/large_model/nets",
        "/data/project_share/yhqiu/apb4_clint/workspace/output/innovus/feature/large_model/nets",
        "/data/project_share/yhqiu/s1238/workspace/output/innovus/feature/large_model/nets",
        "/data/project_share/yhqiu/s1488/workspace/output/innovus/feature/large_model/nets",
        "/data/project_share/yhqiu/s15850/workspace/output/innovus/feature/large_model/nets",
        "/data/project_share/yhqiu/s35932/workspace/output/innovus/feature/large_model/nets",
        "/data/project_share/yhqiu/s38417/workspace/output/innovus/feature/large_model/nets",
        "/data/project_share/yhqiu/s38584/workspace/output/innovus/feature/large_model/nets",
        "/data/project_share/yhqiu/s44/workspace/output/innovus/feature/large_model/nets",
        "/data/project_share/yhqiu/s5378/workspace/output/innovus/feature/large_model/nets",
        "/data/project_share/yhqiu/s713/workspace/output/innovus/feature/large_model/nets",
        "/data/project_share/yhqiu/s9234/workspace/output/innovus/feature/large_model/nets",
        "/data/project_share/yhqiu/salsa20/workspace/output/innovus/feature/large_model/nets",
        "/data/project_share/yhqiu/eth_top/workspace/output/innovus/feature/large_model/nets",
    ]
    data_config = DataConfig(
        raw_input_dirs=INPUT_DIRECTORYS,
        model_input_file="./iEDA_combined_nets_cleaned.csv",
        plot_dir="./analysis_plots",
        extracted_feature_columns=['id', 'wire_len', 'width', 'height',
                                'fanout', 'aspect_ratio', 'l_ness', 'rsmt',
                                'via_num'],
    )
    data_processor = DataProcessor(data_config)
    data_processor.run_pipeline()
