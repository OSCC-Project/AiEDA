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
        title_label = QLabel("Net View")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
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
            # Example: Print net data to console
            print(f"Selected net: {selected_net.name}")
            
            # Get detailed data about the net and output it
            net_data = self.get_net_details(selected_net)
            print(f"Net details: {net_data}")
            
            # Display detailed information about the net
            self.show_net_details(selected_net)
            
            # Emit signal to notify other components of the selected net
            self.net_selected.emit(selected_net)
            
            # 直接使用QToolTip.showText显示tooltip
            # 获取鼠标当前位置
            cursor_pos = self.mapFromGlobal(self.cursor().pos())
            # 获取列表项的视觉位置
            rect = self.net_list_widget.visualItemRect(item)
            # 计算tooltip显示位置
            pos = self.net_list_widget.mapToGlobal(rect.bottomLeft())
            # 直接获取并显示tooltip文本
            tooltip_text = item.toolTip()
            QToolTip.showText(pos, tooltip_text, self.net_list_widget, rect)

    def show_net_details(self, selected_net):
        """Display detailed information of the net using tooltips
        
        Args:
            selected_net: Net object to display details for
        """
        # Get detailed data of the net
        net_details = self.get_net_details(selected_net)
        
        # Format detailed information into tooltip text
        tooltip_text = f"Net: {net_details.get('name', 'Unknown')}\n\n" 
        
        # Add all detailed information
        for key, value in net_details.items():
            if key == 'name':
                continue  # Skip name as it's already in the title
                
            # Format key name to be more readable
            readable_key = key.replace('_', ' ').title()
            
            # Special handling for some value display formats
            if isinstance(value, list):
                # For list type, display as comma-separated string
                value_str = ', '.join(map(str, value))
            elif isinstance(value, float):
                # For float numbers, limit decimal places
                value_str = f"{value:.6f}"
            else:
                value_str = str(value)
            
            tooltip_text += f"{readable_key}: {value_str}\n"
        
        # Find the item in the list and set its tooltip using Qt.ToolTipRole
        for i in range(self.net_list_widget.count()):
            item = self.net_list_widget.item(i)
            if item.text() == selected_net.name:
                # 使用setToolTip方法设置tooltip
                item.setToolTip(tooltip_text)
                # 也使用Qt.ToolTipRole作为备用
                item.setData(Qt.ToolTipRole, tooltip_text)
                break
    
    def get_net_details(self, net):
        """Get detailed feature data of the net, excluding None values
        
        Args:
            net: Net object to retrieve details for
            
        Returns:
            Dictionary of net attributes with non-None values
        """
        details = {
            "name": net.name
        }
        
        # Check if net has feature attribute and it's not None
        if hasattr(net, 'feature') and net.feature:
            # Get all attributes of VectorNetFeature
            feature = net.feature
            feature_attrs = [
                'llx', 'lly', 'urx', 'ury', 'wire_len', 'via_num', 'drc_num',
                'R', 'C', 'power', 'delay', 'slew', 'aspect_ratio', 'width',
                'height', 'area', 'l_ness', 'volume', 'layer_ratio'
            ]
            
            # Add all non-None attributes to details
            for attr in feature_attrs:
                value = getattr(feature, attr, None)
                if value is not None:
                    details[attr] = value
            
            # Special handling for drc_type list
            if hasattr(feature, 'drc_type') and feature.drc_type:
                details['drc_type'] = ', '.join(feature.drc_type)
            
            # Process place_feature if it's not None
            if hasattr(feature, 'place_feature') and feature.place_feature:
                place_feature = feature.place_feature
                place_attrs = ['pin_num', 'aspect_ratio', 'width', 'height',
                              'area', 'l_ness', 'rsmt', 'hpwl']
                
                for attr in place_attrs:
                    value = getattr(place_feature, attr, None)
                    if value is not None:
                        details[f'place_{attr}'] = value
        
        return details