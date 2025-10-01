#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys
import os
import numpy
import math
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QGroupBox, QGridLayout, QScrollArea, QTableWidget, 
    QTableWidgetItem, QHeaderView
)
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import Qt, QRectF

class PatchImageWidget(QWidget):
    """Custom widget for displaying combined image of all layers
    
    This widget renders an image composed of multiple superimposed layers,
    each represented by colored pixels. It automatically scales and centers
    the image within the available space while preserving aspect ratio.
    
    Attributes:
        image_dict: Dictionary mapping layer IDs to 2D arrays of color values
        row_num: Number of rows in the image grid
        col_num: Number of columns in the image grid
    """
    
    def __init__(self, parent=None):
        """Initialize the PatchImageWidget
        
        Args:
            parent: Parent widget for this component
        """
        super().__init__(parent)
        self.image_dict = None
        self.row_num = 0
        self.col_num = 0
        self.setMinimumSize(400, 400)
        # Set white background with gray border
        self.setStyleSheet("background-color: #FFFFFF; border: 2px solid #CCCCCC;")
        
    def set_image_data(self, image_dict, row_num, col_num):
        """Set the image data to be displayed
        
        Args:
            image_dict: Dictionary mapping layer IDs to 2D arrays of color values
            row_num: Number of rows in the image grid
            col_num: Number of columns in the image grid
        """
        self.image_dict = image_dict
        self.row_num = row_num
        self.col_num = col_num
        self.update()  # Trigger repaint
        
    def paintEvent(self, event):
        """Paint event handler to draw the superimposed layers image
        
        Args:
            event: QPaintEvent object containing painting information
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get widget dimensions
        width = self.width()
        height = self.height()
        
        # Draw white background
        painter.fillRect(0, 0, width, height, QBrush(QColor(255, 255, 255)))
        
        # Draw gray border
        pen = QPen(QColor(204, 204, 204))  # #CCCCCC gray
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(1, 1, width - 2, height - 2)  # Leave margin for border width
        
        if self.image_dict is None or len(self.image_dict) == 0:
            # Display empty prompt
            painter.drawText(self.rect(), Qt.AlignCenter, "No image data available")
            return
        
        if self.row_num == 0 or self.col_num == 0:
            return
            
        scale_x = width / self.col_num
        scale_y = height / self.row_num
        scale = min(scale_x, scale_y)  # Use proportional scaling
        
        # Calculate centered offset
        offset_x = (width - self.col_num * scale) / 2
        offset_y = (height - self.row_num * scale) / 2
        
        # Draw all layers data (superimposed display)
        for layer_id, layer_array in self.image_dict.items():
            for i in range(self.row_num):
                for j in range(self.col_num):
                    color_value = layer_array[i, j]
                    if color_value > 0:  # Only draw colored points
                        # Create QColor object
                        if isinstance(color_value, int):
                            color_id = color_value
                        else:
                            color_id = int(color_value) if color_value.is_integer() else color_value
                        
                        # Ensure color ID is valid
                        color_id = int(color_id) % 16777216  # 24-bit color value range
                        
                        # Convert color ID to RGB values
                        r = (color_id >> 16) & 0xFF
                        g = (color_id >> 8) & 0xFF
                        b = color_id & 0xFF
                        
                        painter.setBrush(QBrush(QColor(r, g, b)))
                        painter.setPen(Qt.NoPen)
                        
                        # Draw pixel (as rectangle)
                        rect = QRectF(
                            offset_x + j * scale,
                            offset_y + i * scale,
                            max(1, scale),  # Ensure at least 1 pixel width
                            max(1, scale)   # Ensure at least 1 pixel height
                        )
                        painter.drawRect(rect)
        
        if self.col_num > 0 and self.row_num > 0:
            rect = QRectF(
                offset_x,
                offset_y,
                self.col_num * scale,
                self.row_num * scale
            )
            pen = QPen(QColor(200, 0, 0)) 
            pen.setWidth(2)
            painter.setPen(pen)
            painter.setBrush(QBrush(Qt.NoBrush))
            painter.drawRect(rect)


class LayerImageWidget(QWidget):
    """Custom widget for displaying single layer image data with Ctrl+wheel zoom support
    
    This widget renders a single layer's image data with support for interactive
    zooming using Ctrl+mouse wheel, allowing users to examine details of individual layers.
    
    Attributes:
        layer_id: Identifier for the layer being displayed
        layer_array: 2D array of color values representing the layer
        row_num: Number of rows in the layer grid
        col_num: Number of columns in the layer grid
        zoom_factor: Current zoom level for the view
        min_zoom: Minimum allowed zoom level
        max_zoom: Maximum allowed zoom level
        zoom_step: Amount to change zoom level per wheel event
    """
    
    def __init__(self, layer_id, parent=None):
        """Initialize the LayerImageWidget
        
        Args:
            layer_id: Identifier for the layer to be displayed
            parent: Parent widget for this component
        """
        super().__init__(parent)
        self.layer_id = layer_id
        self.layer_array = None
        self.row_num = 0
        self.col_num = 0
        self.setMinimumSize(300, 300)
        # Set white background with gray border
        self.setStyleSheet("background-color: #FFFFFF; border: 2px solid #CCCCCC;")
        
        # Zoom-related variables
        self.zoom_factor = 1.0  # Initial zoom ratio
        self.min_zoom = 0.1     # Minimum zoom ratio
        self.max_zoom = 10.0    # Maximum zoom ratio
        self.zoom_step = 0.1    # Step size for each wheel zoom
        
    def set_layer_data(self, layer_array, row_num, col_num):
        """Set the layer data to be displayed
        
        Args:
            layer_array: 2D array of color values representing the layer
            row_num: Number of rows in the layer grid
            col_num: Number of columns in the layer grid
        """
        self.layer_array = layer_array
        self.row_num = row_num
        self.col_num = col_num
        self.update()  # Trigger repaint
        
    def wheelEvent(self, event):
        """Handle mouse wheel events to implement Ctrl+wheel zoom functionality
        
        Args:
            event: QWheelEvent object containing wheel movement information
        """
        # Check if Ctrl key is pressed
        if event.modifiers() == Qt.ControlModifier:
            # Get wheel direction
            delta = event.angleDelta().y()
            
            # Adjust zoom ratio based on wheel direction
            if delta > 0:  # Wheel up, zoom in
                self.zoom_factor = min(self.zoom_factor + self.zoom_step, self.max_zoom)
            else:  # Wheel down, zoom out
                self.zoom_factor = max(self.zoom_factor - self.zoom_step, self.min_zoom)
            
            # Trigger repaint to show zoomed image
            self.update()
        else:
            # If Ctrl key not pressed, call parent's event handler
            super().wheelEvent(event)
            
    def paintEvent(self, event):
        """Paint event handler to draw layer data with support for zooming
        
        Args:
            event: QPaintEvent object containing painting information
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get widget dimensions
        width = self.width()
        height = self.height()
        
        # Draw white background
        painter.fillRect(0, 0, width, height, QBrush(QColor(255, 255, 255)))
        
        # Draw gray border
        pen = QPen(QColor(204, 0, 0))  # #CCCCCC gray
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(1, 1, width - 2, height - 2)  # Leave margin for border width
        
        if self.layer_array is None:
            return
        
        if self.row_num == 0 or self.col_num == 0:
            return
            
        # Calculate base pixel size (maintaining square aspect ratio)
        # Use the same value for width and height to ensure square image
        base_pixel_size = min(width / self.col_num, height / self.row_num)
        
        # Apply zoom ratio
        pixel_size = base_pixel_size * self.zoom_factor
        
        # Calculate centered offset to keep square image in center
        total_width = self.col_num * pixel_size
        total_height = self.row_num * pixel_size
        offset_x = (width - total_width) / 2
        offset_y = (height - total_height) / 2
        
        # Draw layer data
        for i in range(self.row_num):
            for j in range(self.col_num):
                color_value = self.layer_array[i, j]
                if color_value > 0:  # Only draw colored points
                    # Create QColor object
                    if isinstance(color_value, int):
                        color_id = color_value
                    else:
                        color_id = int(color_value) if color_value.is_integer() else color_value
                    
                    # Ensure color ID is valid
                    color_id = int(color_id) % 16777216  # 24-bit color value range
                    
                    # Convert color ID to RGB values
                    r = (color_id >> 16) & 0xFF
                    g = (color_id >> 8) & 0xFF
                    b = color_id & 0xFF
                    
                    painter.setBrush(QBrush(QColor(r, g, b)))
                    painter.setPen(Qt.NoPen)
                    
                    # Draw pixel (as rectangle) with scaling and centering
                    rect = QRectF(
                        offset_x + j * pixel_size,
                        offset_y + i * pixel_size,
                        max(1, pixel_size),  # Ensure at least 1 pixel width
                        max(1, pixel_size)   # Ensure at least 1 pixel height
                    )
                    painter.drawRect(rect)
    
    def reset_zoom(self):
        """Reset zoom ratio to default value"""
        self.zoom_factor = 1.0
        self.update()

class PatchLayout(QWidget):
    """Patch Layout UI component with support for Ctrl+wheel zoom on scroll_content
    
    This widget provides a comprehensive interface for visualizing integrated circuit patches,
    displaying both combined and individual layer views with interactive capabilities.
    
    Attributes:
        vec_layers: Dictionary mapping layer IDs to layer objects
        color_list: List of colors used for rendering different layers
        patch: Current patch object being displayed
        scroll_zoom_factor: Zoom level for the scroll content area
        scroll_min_zoom: Minimum zoom level for scroll content
        scroll_max_zoom: Maximum zoom level for scroll content
        scroll_zoom_step: Step size for scroll content zoom
        original_item_size: Original size of layer items
        max_columns: Maximum number of columns in the layer grid
        combined_widget: Widget displaying the combined layer view
        layer_widgets: Dictionary mapping layer IDs to their display widgets
        image_dict: Dictionary of image data for each layer
        layer_containers: List of container widgets for layer displays
    """
    
    def __init__(self, vec_layers, color_list):
        """Initialize the PatchLayout component
        
        Args:
            vec_layers: Vector of layer objects
            color_list: List of colors for rendering layers
        """
        self.vec_layers = self.load_layers(vec_layers)
        self.color_list = color_list
        self.patch = None
        super().__init__()
        
        # Zoom-related variables
        self.scroll_zoom_factor = 1.0  # Initial zoom ratio for scroll_content
        self.scroll_min_zoom = 0.5     # Minimum zoom ratio for scroll_content
        self.scroll_max_zoom = 2.0     # Maximum zoom ratio for scroll_content
        self.scroll_zoom_step = 0.1    # Step size for each scroll_content zoom
        self.original_item_size = 200  # Original item size
        self.max_columns = 5

        self._init_ui()
        
    def load_layers(self, vec_layers):
        """Load layers data and convert to dictionary format
        
        Args:
            vec_layers: Vector of layer objects
            
        Returns:
            Dictionary mapping layer IDs to layer objects
        """
        layers = {layer.id: layer for layer in vec_layers.layers} if vec_layers else {}
        return layers
        
    def _init_ui(self):
        """Initialize UI components and layout"""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        
        # Title label
        # title_label = QLabel("Patch Images")
        # title_font = QFont()
        # title_font.setBold(True)
        # title_font.setPointSize(12)
        # title_label.setFont(title_font)
        # title_label.setAlignment(Qt.AlignCenter)
        
        # Add title to main layout
        # self.main_layout.addWidget(title_label)
        
        # Create horizontal layout for displaying components side by side
        content_layout = QHBoxLayout()
        
        # Left side: Combined image display component (PatchImageWidget), ratio 0.2
        combined_title = QLabel("Patch Image")
        combined_title.setAlignment(Qt.AlignCenter)
        combined_title.setStyleSheet("font-weight: bold;")
        
        self.combined_widget = PatchImageWidget()
        
        combined_layout = QVBoxLayout()
        combined_layout.addWidget(combined_title)
        combined_layout.addWidget(self.combined_widget, 1)
        
        combined_container = QWidget()
        combined_container.setLayout(combined_layout)
        
        # Add combined image to horizontal layout, ratio 0.2
        content_layout.addWidget(combined_container, 2)  # 2 represents stretch factor
        
        # Right side: Single layer display area (LayerImageWidget), ratio 0.8
        layers_title = QLabel("Patch Layer Images")
        layers_title.setAlignment(Qt.AlignCenter)
        layers_title.setStyleSheet("font-weight: bold;")
        
        # Create scroll area to support many layers
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Container widget inside scroll area
        self.scroll_content = QWidget()
        self.layers_layout = QGridLayout(self.scroll_content)  # Use grid layout for multiple rows
        self.layers_layout.setHorizontalSpacing(10)  # Set horizontal spacing
        self.layers_layout.setVerticalSpacing(10)    # Set vertical spacing
        self.scroll_area.setWidget(self.scroll_content)
        
        # Create right side vertical layout
        right_layout = QVBoxLayout()
        right_layout.addWidget(layers_title)
        right_layout.addWidget(self.scroll_area, 1)
        
        right_container = QWidget()
        right_container.setLayout(right_layout)
        
        # Add right layout to horizontal layout, ratio 0.8
        content_layout.addWidget(right_container, 8)  # 8 represents stretch factor
        
        # Add horizontal layout to main layout
        self.main_layout.addLayout(content_layout, 1)
        
        # Dictionary to store layer widgets
        self.layer_widgets = {}
        
        # Connect event filter for scroll area
        self.scroll_area.viewport().installEventFilter(self)
        self.image_dict = {}  # Store current image data dictionary
        self.layer_containers = []  # Store all layer container widgets
        
    def eventFilter(self, obj, event):
        """Event filter to capture wheel events for scroll_area
        
        Args:
            obj: Object that triggered the event
            event: Event object containing event information
            
        Returns:
            True if event was handled, False otherwise
        """
        # Check if this is a wheel event from the scroll area's viewport
        if obj == self.scroll_area.viewport() and event.type() == event.Wheel:
            # Check if Ctrl key is pressed
            if event.modifiers() == Qt.ControlModifier:
                # Get wheel direction
                delta = event.angleDelta().y()
                
                # Adjust zoom ratio based on wheel direction
                if delta > 0:  # Wheel up, zoom in
                    self.scroll_zoom_factor = min(self.scroll_zoom_factor + self.scroll_zoom_step, self.scroll_max_zoom)
                else:  # Wheel down, zoom out
                    self.scroll_zoom_factor = max(self.scroll_zoom_factor - self.scroll_zoom_step, self.scroll_min_zoom)
                
                # Apply zoom
                self.apply_scroll_zoom()
                
                # Prevent event from propagating further
                return True
        
        # For other events, call parent's event filter
        return super().eventFilter(obj, event)
        
    def apply_scroll_zoom(self):
        """Apply zoom ratio to all layer components in scroll_content"""
        # Calculate new item size
        new_item_size = int(self.original_item_size * self.scroll_zoom_factor)
        
        # Update each layer container's size
        for container in self.layer_containers:
            # Get layout inside container
            layout = container.layout()
            if layout and layout.count() > 1:
                # Get image widget
                image_widget = layout.itemAt(1).widget()
                if image_widget:
                    # Set new minimum size
                    image_widget.setMinimumSize(new_item_size, new_item_size)
                    
        # Update layout
        self.scroll_content.updateGeometry()
        self.scroll_area.update()
        
    def reset_scroll_zoom(self):
        """Reset scroll_content zoom ratio to default value"""
        self.scroll_zoom_factor = 1.0
        
        # Restore original size for each layer container
        for container in self.layer_containers:
            # Get layout inside container
            layout = container.layout()
            if layout and layout.count() > 1:
                # Get image widget
                image_widget = layout.itemAt(1).widget()
                if image_widget:
                    # Restore original minimum size
                    image_widget.setMinimumSize(self.original_item_size, self.original_item_size)
        
        self.scroll_content.updateGeometry()
        self.scroll_area.update()
        
    def update_patch(self, patch): 
        def align_data(row, col):
            return (row-patch.row_min, col-patch.col_min)
        
        # Initialize image dictionary
        image_dict = {}
        
        row_num, col_num = patch.row_max-patch.row_min, patch.col_max-patch.col_min

        for layer in patch.patch_layer:
            for net in layer.nets:
                for wire in net.wires:    
                    for path in wire.paths:
                        if path.node1.layer == path.node2.layer:
                            layer_id = path.node1.layer
                            
                            color = self.color_list[layer_id % len(self.color_list)]
                            # Convert QColor to RGB integer value
                            color_value = (color.red() << 16) | (color.green() << 8) | color.blue()
                            
                            row1, col1 = align_data(path.node1.row, path.node1.col)
                            row2, col2 = align_data(path.node2.row, path.node2.col)
                            
                            layer_array = image_dict.get(layer_id, None)
                            if layer_array is None:
                                layer_array = numpy.zeros((row_num, col_num))
                                image_dict[layer_id] = layer_array
                            layer_array[min(row1,row2) : max(row1,row2)+1, min(col1, col2) : max(col1, col2)+1] = color_value
                            
                        else:
                            # via data
                            row, col = (path.node1.col-patch.col_min, path.node1.row-patch.row_min)
                            
                            for layer_id in [path.node1.layer, (path.node1.layer+path.node2.layer)/2, path.node2.layer]:
                                color = self.color_list[layer_id % len(self.color_list)]
                                # Convert QColor to RGB integer value
                                color_value = (color.red() << 16) | (color.green() << 8) | color.blue()
                                
                                layer_array = image_dict.get(layer_id, None)
                                if layer_array is None:
                                    layer_array = numpy.zeros((row_num, col_num))
                                    image_dict[layer_id] = layer_array
                                
                                layer_array[row, col] = color_value
                                
        # Store current patch data and image data
        self.patch = patch
        self.image_dict = image_dict
        
        # Set data for combined image component
        if hasattr(self, 'combined_widget'):
            self.combined_widget.set_image_data(image_dict, row_num, col_num)
        
        # Clear existing layer widgets
        for widget in self.layer_widgets.values():
            widget.setParent(None)
        self.layer_widgets.clear()
        
        # Remove all items from layout
        while self.layers_layout.count() > 0:
            item = self.layers_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        # Create display components for each layer
        if image_dict:
            index = 0
            
            for layer_id, layer_array in image_dict.items():
                # Create layer image widget
                layer_widget = LayerImageWidget(layer_id)
                
                # Set LayerImageWidget to square size, multiple of row_num and col_num
                # Calculate appropriate square size (based on original item size and multiples of row/col count)
                base_size = self.original_item_size
                # Ensure size is a common multiple of row_num and col_num
                # Find least common multiple of row_num and col_num
                def lcm(a, b):
                    return a * b // math.gcd(a, b)
                
                if row_num > 0 and col_num > 0:
                    min_size = lcm(int(row_num), int(col_num))
                    # Ensure square size is at least base_size and a multiple of min_size
                    square_size = max(base_size, ((base_size + min_size - 1) // min_size) * min_size)
                else:
                    square_size = base_size
                
                # Create layer title
                layer_title = QLabel(self.vec_layers[layer_id].name)
                layer_title.setStyleSheet("font-weight: bold;")
                layer_title.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
                layer_title.setFixedWidth(square_size)  # Set same width as layer_widget for alignment
                
                # Set fixed square size
                layer_widget.setFixedSize(square_size, square_size)
                
                # Create vertical layout for title and image
                layer_layout = QVBoxLayout()
                # Set layout margins and spacing to ensure precise alignment of title and image
                layer_layout.setContentsMargins(0, 0, 0, 0)
                layer_layout.setSpacing(0)  # Set spacing between layout items to 0
                # Add title and image to layout, ensuring horizontal and vertical center alignment
                layer_layout.addWidget(layer_title, alignment=Qt.AlignHCenter | Qt.AlignVCenter | Qt.AlignBottom)
                layer_layout.addWidget(layer_widget, 1, alignment=Qt.AlignHCenter | Qt.AlignVCenter | Qt.AlignTop)  # Let image occupy remaining space and ensure vertical center
                
                # Create container widget for layout
                container = QWidget()
                container.setLayout(layer_layout)
                
                # Calculate grid position
                row = index // self.max_columns
                col = index % self.max_columns
                
                # Add to grid layout
                self.layers_layout.addWidget(container, row, col)
                
                # Store widget reference
                self.layer_widgets[layer_id] = layer_widget
                
                # Store container reference
                self.layer_containers.append(container)
                
                # Set layer data
                layer_widget.set_layer_data(layer_array, row_num, col_num)
                
                index += 1
        else:
            # If no layer data, display empty message
            empty_label = QLabel("No layer data available")
            empty_label.setAlignment(Qt.AlignCenter)
            # Add to center position of grid layout
            self.layers_layout.addWidget(empty_label, 0, 0)
            self.layers_layout.setAlignment(empty_label, Qt.AlignCenter)