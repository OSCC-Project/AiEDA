# -*- encoding: utf-8 -*-
"""
@File : basic.py
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

class ZoomableGraphicsView(QGraphicsView):
    """Custom zoomable QGraphicsView with Ctrl+mouse wheel zoom support"""
    
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.parent_widget = parent
    
    def wheelEvent(self, event):
        """Handle mouse wheel events to implement Ctrl+mouse wheel zoom, centered at mouse cursor position in scene coordinates"""
        # Check if Ctrl key is pressed
        if event.modifiers() == Qt.ControlModifier:
            # Ignore default wheel event handling
            event.ignore()
            
            delta = event.angleDelta().y()
            
            # Get mouse wheel delta
            # if delta > 0:
            #     self.parent_widget.zoom_in()
            # else:
            #     self.parent_widget.zoom_out()
            
            # Store current transformation anchor setting
            # old_anchor = self.transformationAnchor()
            
            # Set transformation anchor to mouse position
            # self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
            
            # Calculate zoom factor based on wheel movement
            scale_factor = 1.2 if delta > 0 else 0.8  # Consistent zoom factor
            
            # Scale the view using the mouse position in scene coordinates as anchor
            self.scale(scale_factor, scale_factor)
            
            # Restore original transformation anchor setting after zoom
            # self.setTransformationAnchor(old_anchor)
        else:
            # Use default wheel event handling if Ctrl is not pressed
            super().wheelEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events to get and display mouse coordinates"""
        # Get mouse position in scene coordinates
        scene_pos = self.mapToScene(event.pos())
        x, y = scene_pos.x(), scene_pos.y()
        
        # # Get scene height and adjust y-axis direction to increase from bottom to top
        # scene_rect = self.sceneRect()
        # scene_height = scene_rect.height()
        # adjusted_y = scene_height - y  # Adjust y-axis direction
        
        # Format coordinate display (2 decimal places)
        coord_text = f"X: {x:.2f}, Y: {y:.2f}"
        
        # Update parent widget's coordinate status display
        if hasattr(self.parent_widget, 'update_coord_status'):
            self.parent_widget.update_coord_status(coord_text)
        
        # Call parent class's mouseMoveEvent for default behavior
        super().mouseMoveEvent(event)