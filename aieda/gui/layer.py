"""
@File : layer.py
@Author : yell
@Desc : Layer Layout UI for AiEDA system
"""

import sys
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QGroupBox, QGridLayout, QScrollArea, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QPushButton, QComboBox)
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import Qt, QRectF


class LayerLayout(QWidget):
    """Layer Layout UI component"""
    
    def __init__(self, vec_layers, color_list):
        self.vec_layers = self.load_layers(vec_layers)
        self.color_list = color_list
        
        super().__init__()
        
        self._init_ui()
        
        self.update_list()
        
    def _init_ui(self):
        """Initialize UI components"""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        
        # Title label
        title_label = QLabel("Layer View")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(title_label)
    
    def load_layers(self, vec_layers):
        layers = {layer.name: layer for layer in vec_layers.layers} if vec_layers else {}
        return layers
    
    def update_list(self):
        """Update UI with layers data"""
        # Clear existing widgets
        while self.main_layout.count() > 1:  # Keep the title label
            item = self.main_layout.takeAt(1)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Create table widget
        self.layer_table = QTableWidget(len(self.vec_layers), 2)
        self.layer_table.setHorizontalHeaderLabels(["Color", "Layer Name"])
        self.layer_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.layer_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        
        # Sort layers by their ID
        layer_list = sorted(self.vec_layers.values(), key=lambda x: x.id)
        
        # Populate table with layer names and colors
        for idx, layer in enumerate(layer_list):
            # Create color item
            color_widget = QWidget()
            color_layout = QHBoxLayout(color_widget)
            color_layout.setContentsMargins(5, 5, 5, 5)
            
            # Use layer.id to get color from color_list
            color_id = layer.id % len(self.color_list)
            color = self.color_list[color_id]
            
            color_label = QLabel()
            color_label.setFixedSize(20, 20)
            color_label.setStyleSheet(f"background-color: {color.name()}")
            color_layout.addWidget(color_label)
            
            # Add color widget to table using loop index
            self.layer_table.setCellWidget(idx, 0, color_widget)
            
            # Create layer name item
            name_item = QTableWidgetItem(layer.name)
            name_item.setTextAlignment(Qt.AlignCenter)
            self.layer_table.setItem(idx, 1, name_item)
        
        # Connect double-click signal
        self.layer_table.cellDoubleClicked.connect(self.on_layer_double_clicked)
        
        # Add table to layout
        self.main_layout.addWidget(self.layer_table)
        
    def on_layer_double_clicked(self, row, column):
        """Handle double-click on layer name"""
        if column == 1:  # Only handle double-clicks on layer name column
            layer_name = self.layer_table.item(row, column).text()
            layer_value = self.vec_layers.get(layer_name)
            # Here you can process the layer_value as needed
            print(f"Layer '{layer_name}' double-clicked, value: {layer_value}")