"""
@File : layer.py
@Author : yell
@Desc : Layer Layout UI for AiEDA system
"""

import sys
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QGroupBox, QGridLayout, QScrollArea, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QPushButton, QComboBox, QCheckBox)
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import Qt, QRectF


class LayerLayout(QWidget):
    """Layer Layout UI component"""
    
    def __init__(self, vec_layers, color_list, chip_layout=None, patches_layout=None):
        self.vec_layers = self.load_layers(vec_layers)
        self.color_list = color_list
        self.chip_layout = chip_layout  # 引用ChipLayout实例
        self.patches_layout = patches_layout  # 引用PatchesLayout实例
        self.layer_visibility = {}  # 存储每个图层的显示状态
        
        # Store a reference to self in chip_layout and patches_layout for reverse communication
        if self.chip_layout is not None:
            self.chip_layout.layer_layout = self
            self.chip_layout.layer_visibility = self.layer_visibility
        if self.patches_layout is not None:
            self.patches_layout.layer_layout = self
            self.patches_layout.layer_visibility = self.layer_visibility
        
        super().__init__()
        
        # 初始化所有图层的显示状态为True，使用layer.id作为key
        for layer in self.vec_layers.values():
            self.layer_visibility[layer.id] = True
        
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
        
        # Create table widget with merged Layer Name and Visibility column
        self.layer_table = QTableWidget(len(self.vec_layers), 2)
        self.layer_table.setHorizontalHeaderLabels(["Color", "Layers"])
        self.layer_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.layer_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        # Hide row numbers (vertical header)
        self.layer_table.verticalHeader().setVisible(False)
        
        # Sort layers by their ID
        layer_list = sorted(self.vec_layers.values(), key=lambda x: x.id)
        
        # Populate table with layer names, colors and visibility status
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
            
            # Create merged widget with layer name and visibility checkbox
            merged_widget = QWidget()
            merged_layout = QHBoxLayout(merged_widget)
            merged_layout.setContentsMargins(5, 5, 5, 5)
            
            # Layer name label (不可编辑)
            name_label = QLabel(layer.name)
            name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            name_label.setStyleSheet("background: transparent;")
            merged_layout.addWidget(name_label, 1)  # 1 for stretch factor
            
            # Visibility checkbox
            visibility_checkbox = QCheckBox()
            visibility_checkbox.setChecked(self.layer_visibility.get(layer.id, True))
            visibility_checkbox.setStyleSheet("margin-left: auto;")
            visibility_checkbox.setProperty("layer_id", layer.id)  # Store layer_id for double-click handling
            visibility_checkbox.stateChanged.connect(
                lambda state, layer_id=layer.id: self.on_visibility_changed(layer_id, state)
            )
            merged_layout.addWidget(visibility_checkbox)
            
            self.layer_table.setCellWidget(idx, 1, merged_widget)
        
        # Connect double-click signal
        self.layer_table.cellDoubleClicked.connect(self.on_layer_double_clicked)
        
        # Add table to layout
        self.main_layout.addWidget(self.layer_table)
        
    def on_layer_double_clicked(self, row, column):
        """Handle double-click on merged cell to toggle visibility checkbox"""
        if column == 1:  # Only handle double-clicks on merged Layer Name & Visibility column
            # Get the merged widget from the cell
            merged_widget = self.layer_table.cellWidget(row, 1)
            if merged_widget and hasattr(merged_widget, 'layout'):
                layout = merged_widget.layout()
                if layout and layout.count() > 0:
                    # Iterate through layout items to find the checkbox
                    for i in range(layout.count()):
                        item = layout.itemAt(i)
                        widget = item.widget()
                        if widget and isinstance(widget, QCheckBox):
                            # Get layer_id from checkbox property
                            layer_id = widget.property("layer_id")
                            if layer_id is not None:
                                # Toggle the visibility status of the layer
                                current_visibility = self.layer_visibility.get(layer_id, True)
                                new_visibility = not current_visibility
                                
                                # Update checkbox state
                                widget.setChecked(new_visibility)
                                
                                # Update visibility status
                                self.on_visibility_changed(layer_id, Qt.Checked if new_visibility else Qt.Unchecked)
                            break
    
    def on_visibility_changed(self, layer_id, state):
        """Handle visibility checkbox state change"""
        # Update the visibility status
        is_visible = (state == Qt.Checked)
        self.layer_visibility[layer_id] = is_visible
        
        # Find layer by id to get its name for display
        layer_name = None
        for layer in self.vec_layers.values():
            if layer.id == layer_id:
                layer_name = layer.name
                break
        
        # Update ChipLayout and PatchesLayout to show/hide nets for this layer
        if self.chip_layout is not None:
            print(f"Updating ChipLayout to {'show' if is_visible else 'hide'} nets for layer: {layer_name or layer_id}")
            self.chip_layout.draw_layout()  # 重新绘制布局以反映图层可见性变化
        
        if self.patches_layout is not None:
            print(f"Updating PatchesLayout to {'show' if is_visible else 'hide'} nets for layer: {layer_name or layer_id}")
            self.patches_layout.draw_layout()  # 重新绘制布局以反映图层可见性变化
        
        print(f"Layer '{layer_name or layer_id}' visibility toggled to {'Visible' if is_visible else 'Hidden'}")