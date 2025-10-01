# -*- encoding: utf-8 -*-

import sys
from typing import List, Dict, Optional, Tuple

from PyQt5.QtWidgets import (
    QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsLineItem,
    QGraphicsItemGroup, QGraphicsTextItem, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QComboBox, QPushButton
)
from PyQt5.QtGui import QPen, QBrush, QColor, QFont, QPainter
from PyQt5.QtCore import Qt, QRectF, QPointF

from ..data import DataVectors
from ..workspace import Workspace
from .basic import ZoomableGraphicsView


class ChipLayout(QWidget):
    """Qt-based chip layout display widget that shows instances, nets, and IO pins as rectangles
    
    This widget provides a visual representation of chip layout data including instances,
    nets, and IO pins. It supports zooming, panning, and toggling visibility of different
    layout elements.
    
    Attributes:
        vec_cells: Data vectors for cells
        instances: Instance data
        nets: Net data
        io_pins: IO pin data
        show_instances: Flag to show/hide instances
        show_nets: Flag to show/hide nets
        show_io_pins: Flag to show/hide IO pins
        net_opacity: Opacity level for net display
        scene: QGraphicsScene for drawing
        view: Custom ZoomableGraphicsView
        status_bar: Status bar widget for coordinate display
        coord_label: Label for displaying current coordinates
    """
    
    def __init__(self, vec_cells, vec_instances, vec_nets, color_list, parent: Optional[QWidget] = None):
        """Initialize the ChipLayout widget
        
        Args:
            vec_cells: Data vectors for cells
            vec_instances: Instance data
            vec_nets: Net data
            color_list: List of colors for different cell types
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self.vec_cells = vec_cells
        self.instances = vec_instances
        self.nets = vec_nets

        self.io_pins = []
        
        # Display options
        self.show_instances = True
        self.show_nets = True
        self.show_io_pins = True
        self.net_opacity = 0.5
        
        # Colors
        self.net_color = QColor(0, 250, 0)  # Blue with transparency
        self.io_pin_color = QColor(255, 0, 0, 200)  # Red for IO pins
        self.wire_node_color = {"wire_node": QColor(0, 200, 0), "pin_node": QColor(200, 0, 0)}
        self.text_color = QColor(0, 0, 0)
        self.color_list = color_list
        
        # Selected net rectangle
        self.selected_net_rect = None

        # Initialize UI
        self.init_ui()
        self.draw_layout(True)
    
    def init_ui(self):
        """Initialize the UI components including scene, view, and status bar
        
        Sets up the main layout, creates the QGraphicsScene and ZoomableGraphicsView,
        and adds a status bar for displaying coordinates.
        """
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Create QGraphicsScene and custom ZoomableGraphicsView
        self.scene = QGraphicsScene()
        self.view = ZoomableGraphicsView(self.scene, self)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        
        # Add view to main layout
        main_layout.addWidget(self.view)
        
        # Create status bar at the bottom
        self.status_bar = QWidget()
        status_layout = QHBoxLayout(self.status_bar)
        status_layout.setContentsMargins(5, 2, 5, 2)
        
        # Left empty space for future status messages
        status_layout.addStretch(1)
        
        # Right side coordinate display
        self.coord_label = QLabel("X: 0.00, Y: 0.00")
        self.coord_label.setStyleSheet("background-color: #f0f0f0; padding: 2px 5px;")
        self.coord_label.setMinimumWidth(150)
        self.coord_label.setAlignment(Qt.AlignRight)
        status_layout.addWidget(self.coord_label)
        
        # Add status bar to main layout
        main_layout.addWidget(self.status_bar)
        
        self.setLayout(main_layout)
        self.setWindowTitle("Chip Layout Display")
        self.resize(1000, 800)
  
    def draw_layout(self, fit_view=False):
        """Draw the chip layout elements
        
        Clears the scene and draws instances, nets, and IO pins based on current display settings.
        Optionally fits the view to the scene.
        
        Args:
            fit_view: Whether to fit the view to the entire scene after drawing
        """
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
        
        # Fit the view to the scene - ensure this is always called
        if fit_view:
            self.fit_view()
    
    def _draw_instances(self):
        """Draw instances as rectangles with colors based on cell type
        
        Creates QGraphicsRectItem for each instance and adds them to the scene.
        Adds instance names for larger instances to avoid cluttering.
        """
        for instance in self.instances.instances:
            # Check if instance has required attributes
            if not all(hasattr(instance, attr) for attr in ['llx', 'lly', 'width', 'height']):
                continue
            
            # Create rectangle item
            rect_item = QGraphicsRectItem(
                instance.llx, instance.lly, instance.width, instance.height
            )
            
            # Set color based on cell type
            cell_id = getattr(instance, 'cell_id', None)
            # color = self.color_list.get(cell_id, self.color_list[None])
            color = self.color_list[None]
            # 设置为Dense6Pattern填充样式
            rect_item.setBrush(QBrush(color, Qt.Dense6Pattern))
            rect_item.setPen(QPen(QColor(0, 0, 0), 10))  # Black border
            
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
        """Draw nets with simplified representation
        
        Draws wire nodes and paths between instances, using different colors for
        different layers and node types.
        """
        if len(self.nets) <= 0:
            return
        
        # Iterate through all nets
        for net in self.nets:  # Limit to first 500 nets for performance
            # Draw lines between consecutive points
            for wire in net.wires:
                #draw wire nodes
                wire_nodes = wire.wire
                if wire_nodes.node1.pin_id is not None and wire_nodes.node1.pin_id >= 0:
                    color = self.wire_node_color["pin_node"]
                else:
                    color = self.wire_node_color["wire_node"]
                    
                rect_item = QGraphicsRectItem(
                    wire_nodes.node1.real_x-25, 
                    wire_nodes.node1.real_y-25, 
                    50, 
                    50
                )
                    
                rect_item.setBrush(QBrush(color))
                rect_item.setPen(QPen(color, 1.0))  # Black border
                self.scene.addItem(rect_item)
                    
                if wire_nodes.node2.pin_id is not None and wire_nodes.node2.pin_id >= 0:
                    color = self.wire_node_color["pin_node"]
                else:
                    color = self.wire_node_color["wire_node"]
                rect_item = QGraphicsRectItem(
                    wire_nodes.node2.real_x-25, 
                    wire_nodes.node2.real_y-25, 
                    50, 
                    50
                )
                
                rect_item.setBrush(QBrush(color))
                rect_item.setPen(QPen(color, 1.0))  # Black border
                self.scene.addItem(rect_item)
                
                # draw path
                for path in wire.paths:
                    if path.node1.layer == path.node2.layer:
                        if hasattr(self, 'layer_visibility') and path.node1.layer in self.layer_visibility:
                            # Skip drawing if layer is hidden
                            if not self.layer_visibility[path.node1.layer]:
                                continue
                        
                        color_id = path.node1.layer % len(self.color_list)
                        color = self.color_list[color_id]
                        
                        wire_pen = QPen(color, 30)
                        line_item = QGraphicsLineItem(
                            path.node1.real_x, 
                            path.node1.real_y, 
                            path.node2.real_x, 
                            path.node2.real_y
                        )
                        line_item.setPen(wire_pen)
                        self.scene.addItem(line_item)
    
    def _draw_io_pins(self):
        """Draw IO pins as rectangles with red color
        
        Creates QGraphicsRectItem for each IO pin and adds them to the scene.
        Adds pin names with simplified formatting.
        """
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
            rect_item.setPen(QPen(QColor(0, 0, 0), 10))  # Black border
            
            # Add pin name if available
            if hasattr(pin, 'name'):
                pin_name = pin.name.split('/')[-1] if '/' in pin.name else pin.name
                text_item = QGraphicsTextItem(pin_name, rect_item)
                text_item.setPos(pin.llx + 5, pin.lly + 5)
                text_item.setScale(0.5)
                text_item.setDefaultTextColor(self.text_color)
            
            self.scene.addItem(rect_item)
    
    def toggle_instances(self, index):
        """Toggle display of instances
        
        Args:
            index: 0 to show instances, other values to hide
        """
        self.show_instances = (index == 0)
        self.draw_layout()
    
    def toggle_nets(self, index):
        """Toggle display of nets
        
        Args:
            index: 0 to show nets, other values to hide
        """
        self.show_nets = (index == 0)
        self.draw_layout()
    
    def toggle_io_pins(self, index):
        """Toggle display of IO pins
        
        Args:
            index: 0 to show IO pins, other values to hide
        """
        self.show_io_pins = (index == 0)
        self.draw_layout()
    
    def zoom_in(self):
        """Zoom in on the view, centered at mouse position in scene coordinates"""
        # Scale the view
        self.view.scale(1.2, 1.2)
    
    def zoom_out(self):
        """Zoom out from the view, centered at mouse position in scene coordinates"""
        self.view.scale(0.8, 0.8)
    
    def fit_view(self):
        """Fit the view to the entire scene"""
        if not self.scene.items():
            return
        
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        
    def update_coord_status(self, coord_text):
        """Update the coordinate status display in the bottom status bar
        
        Args:
            coord_text: Text to display in the coordinate label
        """
        self.coord_label.setText(coord_text)
        
    def on_net_selected(self, selected_net):
        """Slot function for handling selected nets, draws bounding rectangle
        
        Creates a red dashed rectangle around the selected net and adjusts the view
        to show the entire selected net with some padding.
        
        Args:
            selected_net: The net that was selected
        """
        # Check if selected net has feature attribute
        if hasattr(selected_net, 'feature') and selected_net.feature:
            feature = selected_net.feature
            
            # Check if feature has required geometric attributes
            if all(hasattr(feature, attr) for attr in ['llx', 'lly', 'width', 'height']):
                # Create white border rectangle
                pen = QPen(QColor(200, 0, 0), 40)
                pen.setStyle(Qt.DashLine)
                
                # Create rectangle item
                if self.selected_net_rect is not None:
                    self.selected_net_rect.setRect(
                        feature.llx-100, feature.lly-100, 
                        feature.width+200, feature.height+200
                    )
                else:
                    self.selected_net_rect = QGraphicsRectItem(
                        feature.llx-100, feature.lly-100, 
                        feature.width+200, feature.height+200
                    )
                
                    # Set rectangle style
                    self.selected_net_rect.setPen(pen)
                    self.selected_net_rect.setBrush(QBrush(Qt.NoBrush))  # No fill
                    
                    # Add rectangle to scene
                    self.scene.addItem(self.selected_net_rect)
                    
                    # Bring rectangle to top layer to ensure visibility
                    self.selected_net_rect.setZValue(100)  # Set high z-value
                
                # Auto adjust view to show entire selected net rectangle
                self.view.fitInView(self.selected_net_rect, Qt.KeepAspectRatio)
                # Slightly zoom out to leave some space around the selected rectangle
                self.view.scale(0.6, 0.6)

    def resizeEvent(self, event):
        """Handle resize event to maintain view fitting
        
        Ensures the view stays properly fitted to the scene when the widget is resized.
        
        Args:
            event: The resize event object
        """
        # Call the base class resize event
        super().resizeEvent(event)
        
        # Force view to fit scene
        self.fit_view()