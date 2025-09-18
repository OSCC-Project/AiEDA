# -*- encoding: utf-8 -*-
"""
@File : qt_layout.py
@Author : yell
@Desc : Qt-based chip layout display
"""

import sys
from typing import List, Dict, Optional, Tuple

from PyQt5.QtWidgets import (QApplication, QGraphicsScene, QGraphicsView,
                             QGraphicsRectItem, QGraphicsLineItem, QGraphicsItemGroup,
                             QGraphicsTextItem, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QSlider, QComboBox, QPushButton)
from PyQt5.QtGui import QPen, QBrush, QColor, QFont, QPainter
from PyQt5.QtCore import Qt, QRectF, QPointF

from ..data import DataVectors
from ..workspace import Workspace


class ChipLayout(QWidget):
    """Qt-based chip layout display widget that shows instances, nets, and IO pins as rectangles"""
    
    def __init__(self, workspace: Workspace, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.workspace = workspace
        self.data_loader = DataVectors(workspace)
        
        # Data storage
        self.instances = []
        self.nets = []
        self.io_pins = []
        self.cell_id_to_name = {}
        
        # Display options
        self.show_instances = True
        self.show_nets = True
        self.show_io_pins = True
        self.instance_opacity = 0.8
        self.net_opacity = 0.5
        
        # Colors
        self.instance_colors = {}
        self.net_color = QColor(200, 200, 0, 200)  # Blue with transparency
        self.io_pin_color = QColor(255, 0, 0, 200)  # Red for IO pins
        self.text_color = QColor(0, 0, 0)
        
        # Initialize UI
        self.init_ui()
        self.load_data()
        self.draw_layout()
    
    def init_ui(self):
        """Initialize the UI components"""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Control panel layout
        control_layout = QHBoxLayout()
        
        # Checkboxes for display options
        self.instance_checkbox = QComboBox()
        self.instance_checkbox.addItems(["Show Instances", "Hide Instances"])
        self.instance_checkbox.currentIndexChanged.connect(self.toggle_instances)
        
        self.net_checkbox = QComboBox()
        self.net_checkbox.addItems(["Show Nets", "Hide Nets"])
        self.net_checkbox.currentIndexChanged.connect(self.toggle_nets)
        
        self.io_pin_checkbox = QComboBox()
        self.io_pin_checkbox.addItems(["Show IO Pins", "Hide IO Pins"])
        self.io_pin_checkbox.currentIndexChanged.connect(self.toggle_io_pins)
        
        # Opacity sliders
        control_layout.addWidget(QLabel("Instances:"))
        control_layout.addWidget(self.instance_checkbox)
        control_layout.addWidget(QLabel("Nets:"))
        control_layout.addWidget(self.net_checkbox)
        control_layout.addWidget(QLabel("IO Pins:"))
        control_layout.addWidget(self.io_pin_checkbox)
        
        # Zoom buttons
        zoom_in_btn = QPushButton("Zoom In")
        zoom_in_btn.clicked.connect(self.zoom_in)
        zoom_out_btn = QPushButton("Zoom Out")
        zoom_out_btn.clicked.connect(self.zoom_out)
        fit_btn = QPushButton("Fit View")
        fit_btn.clicked.connect(self.fit_view)
        
        control_layout.addWidget(zoom_in_btn)
        control_layout.addWidget(zoom_out_btn)
        control_layout.addWidget(fit_btn)
        
        # Add control panel to main layout
        main_layout.addLayout(control_layout)
        
        # Create QGraphicsScene and QGraphicsView
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        
        # Add view to main layout
        main_layout.addWidget(self.view)
        
        self.setLayout(main_layout)
        self.setWindowTitle("Chip Layout Display")
        self.resize(1000, 800)
    
    def load_data(self):
        """Load instances, nets, and IO pins data"""
        # Load instances
        try:
            vec_instances = self.data_loader.load_instances()
            if hasattr(vec_instances, 'instances'):
                self.instances = vec_instances.instances
            else:
                self.instances = []
                self.workspace.logger.warning("No instances found in data")
            
            # Load cells to map cell_id to cell name
            try:
                vec_cells = self.data_loader.load_cells()
                if hasattr(vec_cells, 'cells'):
                    for cell in vec_cells.cells:
                        self.cell_id_to_name[cell.id] = getattr(cell, 'name', f'cell_{cell.id}')
            except Exception as e:
                self.workspace.logger.warning(f"Failed to load cells: {e}")
            
            # Generate colors for different cell types
            self._generate_cell_colors()
            
            # Load nets
            try:
                self.nets = self.data_loader.load_nets()
                if not hasattr(self.nets, 'nets'):
                    self.workspace.logger.warning("Nets data format not as expected")
            except Exception as e:
                self.workspace.logger.warning(f"Failed to load nets: {e}")
                self.nets = type('obj', (object,), {'nets': []})()  # Create dummy object with empty nets list
            
            # For now, we'll consider boundary pins as IO pins
            # This is a simplification - in a real implementation, you'd need to identify actual IO pins
            self._identify_io_pins()
            
            net_count = len(self.nets) if hasattr(self.nets, 'nets') else 0
            self.workspace.logger.info(f"Loaded {len(self.instances)} instances, {net_count} nets, {len(self.io_pins)} IO pins")
        except Exception as e:
            self.workspace.logger.error(f"Failed to load data: {e}")
    
    def _generate_cell_colors(self):
        """Generate colors for different cell types"""
        # Count instances per cell type
        cell_counts = {}
        for instance in self.instances:
            if hasattr(instance, 'cell_id'):
                cell_id = instance.cell_id
                cell_counts[cell_id] = cell_counts.get(cell_id, 0) + 1
        
        # Generate colors
        unique_cell_ids = list(cell_counts.keys())
        for i, cell_id in enumerate(unique_cell_ids):
            # Generate a unique color based on cell_id
            hue = i / len(unique_cell_ids)
            color = QColor.fromHsvF(hue, 0.7, 0.9, self.instance_opacity)
            self.instance_colors[cell_id] = color
        
        # Add default color for unknown cell types
        self.instance_colors[None] = QColor(192, 192, 192, 200)  # Default gray
    
    def _identify_io_pins(self):
        """Identify IO pins from instances"""
        # This is a placeholder implementation
        # In a real scenario, you would need to identify IO pins based on cell type or location
        self.io_pins = []
        if not self.instances:
            return
        
        try:
            # Find layout boundaries
            min_x = min(getattr(inst, 'llx', 0) for inst in self.instances if hasattr(inst, 'llx'))
            max_x = max(getattr(inst, 'urx', 0) for inst in self.instances if hasattr(inst, 'urx'))
            min_y = min(getattr(inst, 'lly', 0) for inst in self.instances if hasattr(inst, 'lly'))
            max_y = max(getattr(inst, 'ury', 0) for inst in self.instances if hasattr(inst, 'ury'))
            
            # Define boundary threshold
            width = max_x - min_x if (max_x - min_x) > 0 else 10000
            height = max_y - min_y if (max_y - min_y) > 0 else 10000
            boundary_threshold = max(width, height) * 0.05
            
            # Identify IO pins
            for instance in self.instances:
                # Check if instance has required attributes
                if not all(hasattr(instance, attr) for attr in ['llx', 'lly', 'urx', 'ury', 'width', 'height']):
                    continue
                
                # Check if instance is near any boundary
                is_near_boundary = (
                    instance.llx < min_x + boundary_threshold or
                    instance.urx > max_x - boundary_threshold or
                    instance.lly < min_y + boundary_threshold or
                    instance.ury > max_y - boundary_threshold
                )
                
                # Simple heuristic: small instances near boundaries are likely IO pins
                if is_near_boundary and instance.width < 5000 and instance.height < 5000:
                    self.io_pins.append(instance)
        except Exception as e:
            self.workspace.logger.warning(f"Error identifying IO pins: {e}")
    
    def draw_layout(self):
        """Draw the chip layout"""
        self.scene.clear()
        
        # Draw instances
        if self.show_instances:
            self._draw_instances()
        
        # Draw nets (simplified as lines between instances)
        if self.show_nets:
            self._draw_nets()
        
        # Draw IO pins
        if self.show_io_pins:
            self._draw_io_pins()
        
        # Fit the view to the scene
        self.fit_view()
    
    def _draw_instances(self):
        """Draw instances as rectangles"""
        for instance in self.instances:
            # Check if instance has required attributes
            if not all(hasattr(instance, attr) for attr in ['llx', 'lly', 'width', 'height']):
                continue
            
            # Create rectangle item
            rect_item = QGraphicsRectItem(
                instance.llx, instance.lly, instance.width, instance.height
            )
            
            # Set color based on cell type
            cell_id = getattr(instance, 'cell_id', None)
            color = self.instance_colors.get(cell_id, self.instance_colors[None])
            rect_item.setBrush(QBrush(color))
            rect_item.setPen(QPen(QColor(0, 0, 0), 0.5))  # Black border
            
            # Optionally add instance name if available
            if hasattr(instance, 'name'):
                # Only add text for larger instances to avoid cluttering
                if instance.width > 1000 and instance.height > 1000:
                    text_item = QGraphicsTextItem(instance.name, rect_item)
                    text_item.setPos(instance.llx + 5, instance.lly + 5)
                    text_item.setScale(0.5)
                    text_item.setDefaultTextColor(self.text_color)
            
            self.scene.addItem(rect_item)
    
    def _draw_nets(self):
        """Draw nets (simplified representation)"""
        if len(self.nets) <= 0:
            return

        net_pen = QPen(self.net_color, 10)
        
        # Iterate through all nets
        for net_idx, net in enumerate(self.nets):  # Limit to first 500 nets for performance
            # Draw lines between consecutive points
            for wire in net.wires:
                for path in wire.paths:
                    line_item = QGraphicsLineItem(path.node1.real_x, 
                                                  path.node1.real_y, 
                                                  path.node2.real_x, 
                                                  path.node2.real_y)
                    line_item.setPen(net_pen)
                    self.scene.addItem(line_item)
    
    def _draw_io_pins(self):
        """Draw IO pins as rectangles"""
        for pin in self.io_pins:
            # Check if pin has required attributes
            if not all(hasattr(pin, attr) for attr in ['llx', 'lly', 'width', 'height']):
                continue
            
            # Create rectangle item
            rect_item = QGraphicsRectItem(
                pin.llx, pin.lly, pin.width, pin.height
            )
            
            # Set color for IO pins
            rect_item.setBrush(QBrush(self.io_pin_color))
            rect_item.setPen(QPen(QColor(0, 0, 0), 1.0))  # Black border
            
            # Add pin name if available
            if hasattr(pin, 'name'):
                pin_name = pin.name.split('/')[-1] if '/' in pin.name else pin.name
                text_item = QGraphicsTextItem(pin_name, rect_item)
                text_item.setPos(pin.llx + 5, pin.lly + 5)
                text_item.setScale(0.5)
                text_item.setDefaultTextColor(self.text_color)
            
            self.scene.addItem(rect_item)
    
    def toggle_instances(self, index):
        """Toggle display of instances"""
        self.show_instances = (index == 0)
        self.draw_layout()
    
    def toggle_nets(self, index):
        """Toggle display of nets"""
        self.show_nets = (index == 0)
        self.draw_layout()
    
    def toggle_io_pins(self, index):
        """Toggle display of IO pins"""
        self.show_io_pins = (index == 0)
        self.draw_layout()
    
    def zoom_in(self):
        """Zoom in on the view"""
        self.view.scale(1.2, 1.2)
    
    def zoom_out(self):
        """Zoom out from the view"""
        self.view.scale(0.8, 0.8)
    
    def fit_view(self):
        """Fit the view to the entire scene"""
        if not self.scene.items():
            return
        
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)