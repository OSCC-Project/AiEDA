#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : base.py
@Author : yhqiu
@Desc : abstract base class for analyzers
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from ..workspace import Workspace


class BaseAnalyzer(ABC):
    """
    Base class for all analyzers.

    This abstract base class defines the interface that all analyzer classes must implement.
    It enforces a consistent structure for data loading, analysis, and visualization across
    different analysis processes.
    """

    def __init__(self):
        """
        Initialize the base analyzer.

        Subclasses should call super().__init__() and initialize their own
        data structures for storing analysis results and tracking missing files.
        """
        self.dir_to_display_name = {}

    @abstractmethod
    def load(
        self,
        workspace_dirs: List[Workspace],
        dir_to_display_name: Optional[Dict[str, str]] = None,
        pattern: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Load data from multiple directories.

        This method should be implemented by subclasses to load and parse
        data from the specified directories. It should handle file discovery,
        data parsing, and error handling for missing or corrupted files.

        Args:
            workspace_dirs: List of base directories to process
            dir_to_display_name: Optional mapping from directory name to display name
            pattern: File pattern to search for

        Returns:
            Dictionary mapping design names to loaded data, or None if no specific
            return value is needed (data can be stored in instance variables)

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        self.dir_to_display_name = dir_to_display_name or {}

        # Subclasses should implement the logic to load data from the specified directories
        # and handle missing or corrupted files, storing the results in instance variables
        # and returning a dictionary mapping design names to loaded data, if appropriate.

        pass

    @abstractmethod
    def analyze(self) -> Optional[Any]:
        """
        Analyze the loaded data.

        This method should perform statistical analysis on the loaded data
        and provide insights such as summary statistics, distributions,
        and other relevant metrics.

        Returns:
            Analysis results (format depends on specific analyzer), or None
            if results are printed directly

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        # Subclasses should implement the logic to analyze the loaded data
        # and return the analysis results, if appropriate.

        pass

    @abstractmethod
    def visualize(self, save_path: Optional[str] = None) -> None:
        """
        Create visualizations for the analyzed data.

        This method should generate appropriate plots and charts to visualize
        the analysis results. Visualizations should be saved to files if
        save_path is provided.

        Args:
            save_path: Optional path where visualization files should be saved.
                      If None, visualizations may be displayed directly or
                      saved to a default location.

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        # Subclasses should implement the logic to generate visualizations
        # for the analyzed data and save them to the specified location, if provided.

        pass
