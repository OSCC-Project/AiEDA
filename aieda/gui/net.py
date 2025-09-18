"""@File : net.py
@Author : yell
@Desc : Net Layout UI for AiEDA system
"""

import sys
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QGroupBox, QGridLayout, QScrollArea, QSplitter,
    QListWidget, QListWidgetItem
)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import Qt, QRectF
from aieda.data import DataVectors

class NetLayout(QWidget):
    """Net Layout UI component"""
    
    # 定义信号，当用户双击网络时发出
    net_selected = pyqtSignal(object)  # 传递选中的网络对象
    
    def __init__(self, vec_nets):
        self.nets = self.load_nets(vec_nets)
        self.net_list_widget = None
        self.net_details_text = None 
        super().__init__()
        
        self.init_ui()

        self.update_list()
    
    def init_ui(self):
        """Initialize UI components"""
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
        
        # Add list widget to layout
        main_layout.addWidget(self.net_list_widget)
        
        # Net information group
        info_group = QGroupBox("Net Details")
        info_layout = QGridLayout()
        
        # Create text edit for displaying net details
        from PyQt5.QtWidgets import QTextEdit
        self.net_details_text = QTextEdit()
        self.net_details_text.setReadOnly(True)
        self.net_details_text.setPlaceholderText("Double click a net to see details...")
        
        info_layout.addWidget(self.net_details_text, 0, 0)
        
        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)
        
        # Set main layout
        self.setLayout(main_layout)
    
    def load_nets(self, vec_nets):
        """Load nets data from workspace and convert to dictionary"""
        nets = {net.name: net for net in vec_nets} if vec_nets else {}
        return nets
    
    def update_list(self):
        """Update UI with nets data"""
        # Clear existing items
        self.net_list_widget.clear()
        
        # Add net names to the list
        if self.nets:
            # Get all net names from dictionary keys
            net_names = list(self.nets.keys())
            
            # Add each net name to the list widget
            for name in net_names:
                item = QListWidgetItem(name)
                self.net_list_widget.addItem(item)
            
            # Clear details text when updating list
            self.net_details_text.setPlainText("")
        else:
            # If no nets available
            # Add placeholder item
            placeholder = QListWidgetItem("No nets available")
            placeholder.setFlags(placeholder.flags() & ~Qt.ItemIsEnabled)
            self.net_list_widget.addItem(placeholder)
            
            # Show no nets message in details
            self.net_details_text.setPlainText("No nets available to display details.")
    
    def on_net_double_clicked(self, item):
        """Handle double click event on net list items using dictionary lookup"""
        net_name = item.text()
        
        # Directly get the net from the dictionary using name as key
        selected_net = self.nets.get(net_name)
        
        # If net found, process it
        if selected_net:
            # Example: Print net data to console
            print(f"Selected net: {selected_net.name}")
            
            # 获取net的详细数据并输出
            net_data = self.get_net_details(selected_net)
            print(f"Net details: {net_data}")
            
            # 这里可以添加显示详细信息的代码，例如弹出对话框或更新UI显示
            self.show_net_details(selected_net)
            
            # 发出信号，通知其他组件选中了这个网络
            self.net_selected.emit(selected_net)
    
    def get_net_details(self, net):
        """Get detailed feature data of the net, exclude None values"""
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
    
    def show_net_details(self, selected_net):
        """Display detailed information of the net on UI"""
        # Get detailed data of the net
        net_details = self.get_net_details(selected_net)
        
        # Format detailed information into readable text
        details_text = """
Network Feature
===============
"""
        
        # Add all detailed information
        for key, value in net_details.items():
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
            
            details_text += f"{readable_key}: {value_str}\n"
        
        # Add empty line at the end for better display
        details_text += "\n"
        
        # Update UI display
        self.net_details_text.setPlainText(details_text)