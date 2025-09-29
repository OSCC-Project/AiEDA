#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QGroupBox, QGridLayout, QScrollArea, QSplitter,
    QListWidget, QListWidgetItem, QToolTip
)
from PyQt5.QtCore import pyqtSignal, QPoint
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import Qt, QRectF
from aieda.data import DataVectors

class NetLayout(QWidget):
    """Net Layout UI component for AiEDA system
    
    This widget provides a list-based interface for browsing and selecting
    nets in a design. It emits a signal when a net is selected, allowing
    other components to respond to user interactions.
    
    Attributes:
        nets: Dictionary mapping net names to net objects
        net_list_widget: QListWidget for displaying net names
        selected_item_index: Index of the currently selected item in the list
    """
    
    # Signal emitted when a user double-clicks a net in the list
    net_selected = pyqtSignal(object)  # Passes the selected net object
    
    def __init__(self, vec_nets):
        """Initialize the NetLayout component
        
        Args:
            vec_nets: Vector of net data objects to be displayed
        """
        self.nets = self.load_nets(vec_nets)
        self.net_list_widget = None
        # Track the index of the currently selected net item
        self.selected_item_index = -1
        super().__init__()
        # Enable mouse tracking for tooltips
        self.setMouseTracking(True)
        
        self.init_ui()
        
        self.update_list()
    
    def init_ui(self):
        """Initialize UI components and layout"""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Title label
        # title_label = QLabel("Net View")
        # title_label.setFont(QFont("Arial", 14, QFont.Bold))
        # title_label.setAlignment(Qt.AlignCenter)
        # main_layout.addWidget(title_label)
        
        # Create net list widget
        self.net_list_widget = QListWidget()
        self.net_list_widget.setAlternatingRowColors(True)
        self.net_list_widget.itemDoubleClicked.connect(self.on_net_double_clicked)
        # Enable mouse tracking for tooltips
        self.net_list_widget.setMouseTracking(True)
        
        # Add list widget to layout
        main_layout.addWidget(self.net_list_widget)
        
        # Set main layout
        self.setLayout(main_layout)
    
    def load_nets(self, vec_nets):
        """Load nets data and convert to dictionary format
        
        Args:
            vec_nets: Vector of net objects to load
            
        Returns:
            Dictionary mapping net names to net objects
        """
        nets = {net.name: net for net in vec_nets} if vec_nets else {}
        return nets
    
    def update_list(self):
        """Update the net list UI with current nets data"""
        # Clear existing items
        self.net_list_widget.clear()
        
        # Add net names to the list
        if self.nets:
            # Get all net names from dictionary keys
            net_names = list(self.nets.keys())
            
            # Add each net name to the list widget with tooltip
            for name in net_names:
                item = QListWidgetItem(name)
                # Enable tooltip for the item
                item.setData(Qt.ToolTipRole, f"Net: {name}\nDouble click to view details")
                self.net_list_widget.addItem(item)
        else:
            # If no nets available
            # Add placeholder item
            placeholder = QListWidgetItem("No nets available")
            placeholder.setFlags(placeholder.flags() & ~Qt.ItemIsEnabled)
            self.net_list_widget.addItem(placeholder)
    
    def on_net_double_clicked(self, item):
        """Handle double click event on net list items
        
        Args:
            item: QListWidgetItem that was double-clicked
        """
        net_name = item.text()
        
        # Record the selected item index
        self.selected_item_index = self.net_list_widget.row(item)
        
        # Directly get the net from the dictionary using name as key
        selected_net = self.nets.get(net_name)
        
        # If net found, process it
        if selected_net:    
            # Emit signal to notify other components of the selected net
            self.net_selected.emit(selected_net)