#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys
import os
from PyQt5.QtWidgets import (
    QWidget, QGraphicsScene, QGraphicsView, QHBoxLayout, QVBoxLayout, 
    QGraphicsRectItem, QGraphicsLineItem, QLabel, QGraphicsItem
)
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import Qt, QRectF, pyqtSignal

from .basic import ZoomableGraphicsView

class HighlightableRectItem(QGraphicsRectItem):
    """Highlightable rectangle item that supports mouse hover and double-click events
    
    This class extends QGraphicsRectItem to provide additional interactivity features,
    including highlighting on mouse hover and custom double-click event handling.
    
    Attributes:
        rect_id: Unique identifier for the rectangle
        original_pen: Original pen style to restore after highlighting
    """
    
    def __init__(self, rect_id, *args, **kwargs):
        """Initialize the HighlightableRectItem with a unique identifier
        
        Args:
            rect_id: Unique identifier for the rectangle
            *args: Additional positional arguments for QGraphicsRectItem
            **kwargs: Additional keyword arguments for QGraphicsRectItem
        """
        super().__init__(*args, **kwargs)
        self.rect_id = int(rect_id)  # Store rectangle ID
        self.original_pen = self.pen()  # Save original pen style
        self.setAcceptHoverEvents(True)  # Enable hover events
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)  # Enable selection
    
    def hoverEnterEvent(self, event):
        """Handle mouse hover enter event by highlighting the rectangle
        
        Args:
            event: QGraphicsSceneHoverEvent containing hover information
        """
        # Create highlight style pen
        highlight_pen = QPen(QColor(0, 255, 0), 50)  # Green thick border
        highlight_pen.setStyle(Qt.DashLine)
        self.setPen(highlight_pen)
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """Handle mouse hover leave event by restoring original style
        
        Args:
            event: QGraphicsSceneHoverEvent containing hover information
        """
        self.setPen(self.original_pen)
        super().hoverLeaveEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """Handle double-click event using traditional method since QGraphicsRectItem doesn't inherit QObject
        
        Args:
            event: QGraphicsSceneMouseEvent containing click information
        """
        if event.button() == Qt.LeftButton:
            # Find parent widget
            parent_widget = self.scene().views()[0].parent()
            if hasattr(parent_widget, 'on_rect_double_clicked'):
                parent_widget.on_rect_double_clicked(self.rect_id)
        super().mouseDoubleClickEvent(event)

class PatchesLayout(QWidget):
    """Patch Layout UI component for AiEDA system
    
    This widget provides a comprehensive interface for visualizing integrated circuit patches,
    including interactive features like zooming, panning, and highlighting of selected elements.
    
    Attributes:
        patches: Dictionary mapping patch IDs to patch objects
        color_list: List of colors used for rendering different elements
        rect_items: Dictionary mapping patch IDs to their graphical rectangle items
        overlapping_rects: Dictionary storing overlapping rectangle borders
        patch_layout: Reference to PatchLayout component set in WorkspaceUI
        selected_net_rect: Rectangle item highlighting the selected network
        scene: QGraphicsScene for rendering patches
        view: Custom ZoomableGraphicsView for displaying the scene
        status_bar: Status bar widget at the bottom of the window
        coord_label: Label displaying coordinate information
    """
    
    def __init__(self, vec_patches, color_list, patch_layout=None):
        """Initialize the PatchesLayout component
        
        Args:
            vec_patches: Vector of patch objects
            color_list: List of colors for rendering
            patch_layout: Optional reference to PatchLayout component
        """
        self.patches = self.load_patches(vec_patches)
        self.color_list = color_list
        self.rect_items = {}
        self.overlapping_rects = {}  # Store overlapping rectangle borders
        self.patch_layout = patch_layout  # Will be set in WorkspaceUI
        self.selected_net_rect = None
        super().__init__()
        
        self._init_ui()
        self.draw_layout(True)
    
    def load_patches(self, vec_patches):
        """Load patches data and convert to dictionary format
        
        Args:
            vec_patches: Vector of patch objects
            
        Returns:
            Dictionary mapping patch IDs to patch objects
        """
        patches = {patch.id: patch for patch in vec_patches} if vec_patches else {}
        return patches

    def _init_ui(self):
        """Initialize UI components and layout"""
        main_layout = QVBoxLayout(self)
        
        # Create QGraphicsScene and custom ZoomableGraphicsView
        self.scene = QGraphicsScene()
        self.view = ZoomableGraphicsView(self.scene, self)  # Pass self as parent
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
        self.setWindowTitle("Patches Display")
        self.resize(1000, 800)
        
    def zoom_in(self):
        """Zoom in on the view, centered at mouse position in scene coordinates"""
        # Scale the view
        self.view.scale(1.2, 1.2)
    
    def zoom_out(self):
        """Zoom out from the view, centered at mouse position in scene coordinates"""
        # Scale the view
        self.view.scale(0.8, 0.8)
    
    def fit_view(self):
        """Fit the view to the entire scene"""
        if not self.scene.items():
            return
        
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        
    def resizeEvent(self, event):
        """Handle resize event to maintain view fitting
        
        Args:
            event: QResizeEvent containing resize information
        """
        # Call the base class resize event
        super().resizeEvent(event)
        
        # Force view to fit scene
        self.fit_view()
        
    def draw_layout(self, fit_view=False):
        """Draw the patches layout in the scene
        
        Args:
            fit_view: Whether to fit the view to the entire scene after drawing
        """
        self.scene.clear()
        self.rect_items = {}  # Clear rectangle items list
        self.overlapping_rects = {}  # Clear overlapping rectangles dictionary
        
        for id, patch in self.patches.items():
            # Add patch rectangle
            # Use custom HighlightableRectItem instead of default QGraphicsRectItem
            rect_item = HighlightableRectItem(str(id), 
                                          patch.llx, 
                                          patch.lly, 
                                          patch.urx-patch.llx, 
                                          patch.ury-patch.lly)
                    
            # Set border to dashed line
            pen = QPen(QColor(0, 0, 0), 5.0)
            pen.setStyle(Qt.DashLine)
            rect_item.setPen(pen)
            self.scene.addItem(rect_item)
            self.rect_items[id] = rect_item # Store rectangle item
            
            for layer in patch.patch_layer:
                # Check if layer_visibility dictionary exists and if the layer is visible
                # Use layer.id as key to match layer_visibility dictionary
                if hasattr(layer, 'id'):
                    layer_id = layer.id
                    if hasattr(self, 'layer_visibility') and layer_id in self.layer_visibility:
                        # Skip drawing nets for this layer if it's hidden
                        if not self.layer_visibility[layer_id]:
                            continue
                # If no name attribute, use original way to try to get identifier
                
                for net in layer.nets:
                    for wire in net.wires:
                        for path in wire.paths:
                            if path.node1.layer == path.node2.layer or path.node1.layer > path.node2.layer:
                                color_id = path.node1.layer % len(self.color_list)
                                color = self.color_list[color_id]
                            else:
                                color_id = path.node2.layer % len(self.color_list)
                                color = self.color_list[color_id]
                                
                            wire_pen = QPen(color, 30) 
                    
                            line_item = QGraphicsLineItem(path.node1.x, 
                                                          path.node1.y, 
                                                          path.node2.x, 
                                                          path.node2.y)
                            line_item.setPen(wire_pen)
                            self.scene.addItem(line_item)
        if fit_view:    
            self.fit_view()
        
    def update_coord_status(self, coord_text):
        """Update the coordinate status display in the bottom status bar
        
        Args:
            coord_text: Text to display in the coordinate label
        """
        self.coord_label.setText(coord_text)
        
    def on_rect_double_clicked(self, rect_id):
        """Handle rectangle double-click event, display rectangle ID and pass selected patch to PatchLayout
        
        Args:
            rect_id: ID of the double-clicked rectangle
        """
        # Display rectangle ID in status bar
        current_text = self.coord_label.text()
        self.coord_label.setText(f"ID: {rect_id} | {current_text}")
        
        # Determine rect_id type and convert to number
        try:
            # If rect_id is string, try to convert to number
            if isinstance(rect_id, str):
                rect_id_key = int(rect_id)
            else:
                rect_id_key = rect_id
        except ValueError:
            # If conversion fails, use original rect_id
            rect_id_key = rect_id
        
        # Get selected patch
        selected_patch = self.patches.get(rect_id_key, None)
        
        # If patch_layout reference is set, pass the selected patch
        if self.patch_layout is not None and selected_patch is not None:
            self.patch_layout.update_patch(selected_patch)
        
    
    def on_net_selected(self, selected_net):
        """Handle network selection slot function, draw bounding rectangle and adjust view
        
        Args:
            selected_net: The network object that was selected
        """
        # Remove previous overlapping rectangle borders
        for id, rect in self.overlapping_rects.items():
            if rect in self.scene.items():
                self.scene.removeItem(rect)
        self.overlapping_rects = {}
        
        # Check if selected network has feature attribute
        if hasattr(selected_net, 'feature') and selected_net.feature:
            feature = selected_net.feature
            
            # Check if feature has llx, lly, width, height attributes
            if all(hasattr(feature, attr) for attr in ['llx', 'lly', 'width', 'height']):
                if self.selected_net_rect is not None:
                    self.selected_net_rect.setRect(feature.llx-100, feature.lly-100, feature.width+200, feature.height+200)
                else:
                    # Create rectangle with white border
                    pen = QPen(QColor(200, 0, 0), 40)
                    pen.setStyle(Qt.DashLine)
                    
                    # Create rectangle item
                    self.selected_net_rect = QGraphicsRectItem(
                        feature.llx-100, feature.lly-100, feature.width+200, feature.height+200
                    )
                    
                    # Set rectangle style
                    self.selected_net_rect.setPen(pen)
                    self.selected_net_rect.setBrush(QBrush(Qt.NoBrush))  # No border fill
                    
                    # Add rectangle to scene
                    self.scene.addItem(self.selected_net_rect)
                    
                    # Move rectangle to top layer to ensure visibility
                    self.selected_net_rect.setZValue(100)  # Set high z-value
                
                # Detect and display patch rectangles overlapping with selected network rectangle
                self._show_overlapping_rects()
                
                # Auto-fit view to show entire selected network rectangle
                self.view.fitInView(self.selected_net_rect, Qt.KeepAspectRatio)
                # Slightly zoom out to leave some space around the selected rectangle
                self.view.scale(0.6, 0.6)
                
    def _show_overlapping_rects(self):
        """Show patch rectangle borders that overlap with the selected network rectangle"""
        if not hasattr(self, 'selected_net_rect') or self.selected_net_rect is None:
            return
        
        # Get selected network rectangle bounds
        selected_rect = self.selected_net_rect.rect()
        
        # Iterate through all patch rectangles and check for overlap
        for id, rect_item in self.rect_items.items():
            # Get current rectangle bounds
            patch_rect = rect_item.rect()
            
            # Check if the two rectangles overlap
            if selected_rect.intersects(patch_rect):
                # Create white dashed border rectangle
                white_pen = QPen(QColor(200, 0, 0), 20)
                white_pen.setStyle(Qt.DashLine)
                
                # Create rectangle item
                overlapping_rect = QGraphicsRectItem(
                    patch_rect.x(), patch_rect.y(), patch_rect.width(), patch_rect.height()
                )
                
                # Set rectangle style
                overlapping_rect.setPen(white_pen)
                # Set transparent red background (R=255, G=0, B=0, Alpha=50)
                overlapping_rect.setBrush(QBrush(QColor(50, 50, 50, 50)))
                
                # Add rectangle to scene
                self.scene.addItem(overlapping_rect)
                
                # Move rectangle to top layer to ensure visibility
                overlapping_rect.setZValue(0)  # One less than selected network rectangle to avoid遮挡
                
                # Store overlapping rectangle for later removal
                self.overlapping_rects[id] = overlapping_rect
        
        