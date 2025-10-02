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


class ZoomableGraphicsView(QGraphicsView):
    """Custom zoomable QGraphicsView with Ctrl+mouse wheel zoom support and coordinate tracking
    
    This class extends QGraphicsView to provide additional functionality for interactive
    zooming and mouse coordinate tracking in the scene. It handles Ctrl+mouse wheel events
    for smooth zooming centered at the mouse cursor position.
    
    Attributes:
        parent_widget: Reference to the parent widget for coordinate updates
    """
    
    def __init__(self, scene, parent=None):
        """Initialize the ZoomableGraphicsView
        
        Args:
            scene: QGraphicsScene to be displayed in the view
            parent: Parent widget (optional)
        """
        super().__init__(scene, parent)
        self.parent_widget = parent
    
    def wheelEvent(self, event):
        """Handle mouse wheel events to implement Ctrl+mouse wheel zoom, centered at mouse cursor position
        
        When Ctrl key is pressed, mouse wheel movements cause zooming in or out,
        with the zoom centered at the current mouse cursor position in the scene.
        If Ctrl key is not pressed, default wheel behavior is used.
        
        Args:
            event: QWheelEvent object containing mouse wheel movement information
        """
        # Check if Ctrl key is pressed
        if event.modifiers() == Qt.ControlModifier:
            # Ignore default wheel event handling
            event.ignore()
            
            delta = event.angleDelta().y()
            
            # Calculate zoom factor based on wheel movement
            scale_factor = 1.2 if delta > 0 else 0.8  # Consistent zoom factor
            
            # Scale the view using the mouse position in scene coordinates as anchor
            self.scale(scale_factor, scale_factor)
        else:
            # Use default wheel event handling if Ctrl is not pressed
            super().wheelEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events to get and display mouse coordinates
        
        Tracks mouse movements and converts screen coordinates to scene coordinates,
        then sends formatted coordinate text to the parent widget for display.
        
        Args:
            event: QMouseEvent object containing mouse position information
        """
        # Get mouse position in scene coordinates
        scene_pos = self.mapToScene(event.pos())
        x, y = scene_pos.x(), scene_pos.y()
        
        # Format coordinate display (2 decimal places)
        coord_text = f"X: {x:.2f}, Y: {y:.2f}"
        
        # Update parent widget's coordinate status display
        if hasattr(self.parent_widget, 'update_coord_status'):
            self.parent_widget.update_coord_status(coord_text)
        
        # Call parent class's mouseMoveEvent for default behavior
        super().mouseMoveEvent(event)